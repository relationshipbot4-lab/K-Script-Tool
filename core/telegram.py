"""Telegram client construction and connection helpers."""

from telethon.sync import TelegramClient

from config import API_HASH, API_ID, SESSIONS_DIR, validate_telegram_config


def create_telegram_client() -> TelegramClient:
    """Create a synchronous Telethon client for the CLI authentication flow."""
    valid, message = validate_telegram_config()
    if not valid:
        raise RuntimeError(message)

    session_path = SESSIONS_DIR / "k_script_tool"
    return TelegramClient(str(session_path), API_ID, API_HASH)
