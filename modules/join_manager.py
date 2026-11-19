"""Authorized group joining through public usernames or valid invite links."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

_INVITE_RE = re.compile(r"(?:https?://)?(?:www\.)?t\.me/(?:joinchat/|\+)([A-Za-z0-9_-]+)")


class GroupJoinError(RuntimeError):
    """Safe, user-facing group join failure."""


def _invite_hash(value: str) -> str | None:
    match = _INVITE_RE.search(value.strip())
    return match.group(1) if match else None


def join_group(client: Any, target: str | int) -> dict[str, str]:
    """Join a public group/channel or import a valid private invite.

    Already-joined targets are treated as success. Telegram FloodWait is
    surfaced with its required delay; it is never retried or bypassed here.
    """
    text = str(target).strip()
    if not text:
        raise ValueError("A group username, ID, or invite link is required.")

    invite_hash = _invite_hash(text)
    try:
        if invite_hash:
            result = client(ImportChatInviteRequest(invite_hash))
            chats = getattr(result, "chats", []) or []
            title = getattr(chats[0], "title", "Private invite") if chats else "Private invite"
            return {"status": "joined", "title": str(title)}

        parsed = urlparse(text if "://" in text else f"https://{text}")
        if parsed.netloc.lower() in {"t.me", "telegram.me"}:
            path = parsed.path.strip("/")
            if path.startswith("@"):
                path = path[1:]
            if not path or path.startswith(("c/", "joinchat/")):
                raise ValueError("Unsupported group link. Provide a public username or valid invite link.")
            target = path.split("/")[0]
        entity = client.get_entity(target)
        client(JoinChannelRequest(entity))
        title = getattr(entity, "title", None) or getattr(entity, "username", None) or str(target)
        return {"status": "joined", "title": str(title)}
    except UserAlreadyParticipantError:
        return {"status": "already_joined", "title": text}
    except FloodWaitError as exc:
        raise GroupJoinError(
            f"Telegram requires waiting {exc.seconds} seconds before another request."
        ) from None
    except GroupJoinError:
        raise
    except Exception:
        raise GroupJoinError(
            "Join failed. Verify the group link, access, and account eligibility."
        ) from None
