"""Authorized Telegram group member scraping."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Any

from telethon.errors import FloodWaitError

from core.telegram import create_telegram_client
from modules.storage import DEFAULT_DB_PATH, MemberStore
from modules.reporter import record_operation


class ScrapeRateLimitError(RuntimeError):
    """A Telegram FloodWait that must be observed before retrying."""


def scrape_members(
    client: Any,
    source: str | int,
    *,
    store: MemberStore | None = None,
    limit: int | None = None,
    stop_event: Event | None = None,
    progress_callback: Callable[[int], None] | None = None,
) -> dict[str, int | str]:
    """Scrape members visible to the signed-in account and persist them.

    The account must already have access to the source. Telegram's access,
    privacy and rate-limit rules are respected; no restriction is bypassed.
    """
    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer or None.")

    member_store = store or MemberStore(DEFAULT_DB_PATH)
    entity = client.get_entity(source)
    source_id = getattr(entity, "id", None)
    source_title = (
        getattr(entity, "title", None)
        or getattr(entity, "username", None)
        or str(source)
    )

    scanned = saved = skipped = 0
    try:
        for user in client.iter_participants(entity, limit=limit):
            if stop_event is not None and stop_event.is_set():
                break
            scanned += 1
            if progress_callback is not None:
                progress_callback(scanned)
            if getattr(user, "deleted", False) or getattr(user, "bot", False):
                skipped += 1
                continue
            user_id = getattr(user, "id", None)
            if user_id is None:
                skipped += 1
                continue
            member_store.save_member(
                {
                    "user_id": user_id,
                    "username": getattr(user, "username", None),
                    "first_name": getattr(user, "first_name", None),
                    "last_name": getattr(user, "last_name", None),
                    "source_id": source_id,
                    "source_title": source_title,
                }
            )
            saved += 1
    except FloodWaitError as exc:
        raise ScrapeRateLimitError(
            f"Telegram rate limit: wait {exc.seconds} seconds before retrying."
        ) from None

    return {
        "source_title": source_title,
        "scanned": scanned,
        "saved": saved,
        "skipped": skipped,
        "total_stored": member_store.count(),
    }


def run_scraper_menu(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> bool:
    """Run one interactive scrape using an already-authorized local session."""
    client = create_telegram_client()
    connected = False
    try:
        client.connect()
        connected = True
        if not client.is_user_authorized():
            output_fn("Please choose [1] Telegram account setup before scraping.")
            return False

        source = input_fn("Source group username or ID: ").strip()
        if not source:
            output_fn("No source was provided.")
            return False
        if source.lstrip("-").isdigit():
            source = int(source)

        limit_text = input_fn("Maximum members (Enter for all accessible members): ").strip()
        try:
            limit = int(limit_text) if limit_text else None
            if limit is not None and limit < 1:
                raise ValueError
        except ValueError:
            output_fn("Member limit must be a positive whole number.")
            return False

        output_fn("Scraping started. Press Ctrl+C to stop safely.")
        result = scrape_members(
            client,
            source,
            limit=limit,
            progress_callback=lambda count: (
                output_fn(f"Processed: {count}") if count % 25 == 0 else None
            ),
        )
        record_operation("member_scrape", "success", details={"processed": result["scanned"], "saved": result["saved"], "skipped": result["skipped"]})
        output_fn(
            "Scrape complete: "
            f"{result['saved']} saved, {result['skipped']} skipped; "
            f"{result['total_stored']} unique records stored locally."
        )
        return True
    except KeyboardInterrupt:
        record_operation("member_scrape", "cancelled")
        output_fn("Scraping interrupted. Records saved so far are kept.")
        return False
    except ScrapeRateLimitError as exc:
        record_operation("member_scrape", "failure")
        output_fn(str(exc))
    except Exception:
        # Do not expose raw Telegram RPC errors or account metadata.
        record_operation("member_scrape", "failure")
        output_fn("Could not scrape this source. Check access and try again.")
        return False
    finally:
        if connected:
            try:
                client.disconnect()
            except Exception:
                pass
