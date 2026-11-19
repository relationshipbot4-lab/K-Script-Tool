"""Interactive Telegram account authentication.

OTP and two-step verification passwords are requested only at runtime and are
never written to application logs or configuration files.
"""

from __future__ import annotations

import getpass
import re
from collections.abc import Callable
from typing import Any

from telethon.errors import (
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)

from core.telegram import connected_telegram_client


def _normalize_phone(value: str) -> str:
    """Normalize a phone number to a conservative international format."""
    phone = re.sub(r"[\s()-]", "", value)
    if not re.fullmatch(r"\+[1-9]\d{7,14}", phone):
        raise ValueError("Enter a valid international phone number, e.g. +1234567890.")
    return phone


def authenticate_telegram_account(
    client: Any | None = None,
    input_fn: Callable[[str], str] = input,
    secret_input_fn: Callable[[str], str] = getpass.getpass,
    output_fn: Callable[[str], None] = print,
) -> bool:
    """Log in interactively, supporting Telegram OTP and optional 2FA.

    The Telethon session is persisted locally by the configured session backend.
    Returns True only when the account is authorized.
    """
    try:
        with connected_telegram_client(client) as telegram:
            if telegram.is_user_authorized():
                user = telegram.get_me()
                output_fn(f"Already logged in as {user.id}.")
                return True

            try:
                phone = _normalize_phone(input_fn("Phone number (international format): ").strip())
            except ValueError as exc:
                output_fn(str(exc))
                return False

            sent_code = telegram.send_code_request(phone)
            code = input_fn("Telegram login code: ").strip()
            if not code:
                output_fn("Login cancelled: no verification code was entered.")
                return False

            try:
                telegram.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=sent_code.phone_code_hash,
                )
            except SessionPasswordNeededError:
                password = secret_input_fn("Two-step verification password: ")
                if not password:
                    output_fn("Login cancelled: no 2FA password was entered.")
                    return False
                telegram.sign_in(password=password)

            if not telegram.is_user_authorized():
                output_fn("Login could not be confirmed. Please try again.")
                return False

            user = telegram.get_me()
            output_fn(f"Login successful. Account ID: {user.id}")
            return True

    except FloodWaitError as exc:
        output_fn(
            f"Telegram rate limit reached. Please wait {exc.seconds} seconds "
            "before trying again."
        )
    except PhoneNumberInvalidError:
        output_fn("Telegram rejected the phone number. Check the international format.")
    except PhoneCodeInvalidError:
        output_fn("The verification code is invalid. Please start login again.")
    except PhoneCodeExpiredError:
        output_fn("The verification code expired. Please start login again.")
    except PasswordHashInvalidError:
        output_fn("The 2FA password is incorrect. Please start login again.")
    except Exception:
        # Avoid printing exception details that may contain account/session metadata.
        output_fn("Telegram login failed. Check your connection and local configuration.")

    return False
