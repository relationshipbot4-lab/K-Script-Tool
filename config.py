"""Application configuration for K SCRIPT TOOL."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TOOL_NAME = os.getenv("TOOL_NAME", "K SCRIPT TOOL")
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "KEE")

API_ID_RAW = os.getenv("TELEGRAM_API_ID", "").strip()
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

try:
    API_ID = int(API_ID_RAW) if API_ID_RAW else None
except ValueError:
    API_ID = None

DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = BASE_DIR / "sessions"
LOGS_DIR = BASE_DIR / "logs"

for directory in (DATA_DIR, SESSIONS_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def validate_telegram_config() -> tuple[bool, str]:
    """Return whether Telegram API credentials are configured."""
    if API_ID is None or not API_HASH:
        return False, (
            "Telegram API credentials are missing or invalid. "
            "Set TELEGRAM_API_ID and TELEGRAM_API_HASH in your local .env file."
        )
    return True, "Telegram configuration is ready."
