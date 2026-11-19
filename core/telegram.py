"""Telegram client construction and connection helpers."""

from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any

from telethon.sync import TelegramClient

from config import API_HASH, API_ID, SESSIONS_DIR, validate_telegram_config


def create_telegram_client() -> TelegramClient:
    """Create the synchronous Telegram client for the CLI."""
    valid, message = validate_telegram_config()
    if not valid:
        raise RuntimeError(message)

    session_path = SESSIONS_DIR / "k_script_tool"
    return TelegramClient(str(session_path), API_ID, API_HASH)


@contextmanager
def connected_telegram_client(client: Any | None = None) -> Iterator[Any]:
    """Connect a client and always attempt disconnect, even on connect failure."""
    telegram = client or create_telegram_client()
    try:
        telegram.connect()
        yield telegram
    finally:
        try:
            telegram.disconnect()
        except Exception:
            # Disconnect failures should not hide the original operation outcome.
            pass
