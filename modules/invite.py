"""Authorized Telegram invite-link creation."""

from __future__ import annotations

from typing import Any

from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import ExportChatInviteRequest


class InviteLinkError(RuntimeError):
    """Safe, user-facing invite link failure."""


def create_invite_link(client: Any, group: str | int) -> dict[str, str]:
    """Create a Telegram invite link for a group the account can administer."""
    try:
        entity = client.get_entity(group)
        exported = client(ExportChatInviteRequest(entity))
        link = getattr(exported, "link", None)
        if not link:
            raise InviteLinkError("Telegram did not return an invite link.")
        title = getattr(entity, "title", None) or getattr(entity, "username", None) or str(group)
        return {"title": str(title), "link": str(link)}
    except FloodWaitError as exc:
        raise InviteLinkError(
            f"Telegram requires waiting {exc.seconds} seconds before another request."
        ) from None
    except InviteLinkError:
        raise
    except Exception:
        raise InviteLinkError(
            "Could not create an invite link. Check group access and administrator permissions."
        ) from None


def run_invite_menu(input_fn=input, output_fn=print) -> bool:
    """Interactive menu for joining via link or creating an invite link."""
    from core.telegram import create_telegram_client
    from modules.join_manager import GroupJoinError, join_group

    output_fn("\n[1] Join group (public username or valid invite link)")
    output_fn("[2] Create invite link for a group you administer")
    output_fn("[0] Back")
    choice = input_fn("Select an option: ").strip()
    if choice == "0":
        return True
    if choice not in {"1", "2"}:
        output_fn("Invalid option.")
        return False
    target = input_fn("Group username, ID, or invite link: ").strip()
    if not target:
        output_fn("No group was provided.")
        return False

    client = create_telegram_client()
    connected = False
    try:
        client.connect()
        connected = True
        if not client.is_user_authorized():
            output_fn("Please choose [1] Telegram account setup first.")
            return False
        if choice == "1":
            result = join_group(client, target)
            if result["status"] == "already_joined":
                output_fn(f"Already joined: {result['title']}")
            else:
                output_fn(f"Joined successfully: {result['title']}")
            return True
        result = create_invite_link(client, target)
        output_fn(f"Group: {result['title']}")
        output_fn(f"Invite link: {result['link']}")
        output_fn("Share only with people who want to join.")
        return True
    except (InviteLinkError, GroupJoinError) as exc:
        output_fn(str(exc))
        return False
    except Exception:
        output_fn("Operation failed. Check group access and try again.")
        return False
    finally:
        if connected:
            try:
                client.disconnect()
            except Exception:
                pass
