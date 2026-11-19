"""Interactive account/session management for the configured Telegram session."""

from __future__ import annotations

from typing import Any, Callable

from core.telegram import connected_telegram_client


def _mask_phone(phone: str | None) -> str:
    """Mask a phone number, retaining only its final three digits."""
    if not phone:
        return "Not available"
    digits = "".join(char for char in phone if char.isdigit())
    if len(digits) <= 3:
        return "***"
    return f"***{digits[-3:]}"


def _display_profile(user: Any, output_fn: Callable[[str], None]) -> None:
    """Display non-sensitive account identity details."""
    output_fn("Account profile:")
    output_fn(f"  User ID: {getattr(user, 'id', 'Unavailable')}")
    output_fn(f"  Name: {' '.join(filter(None, [getattr(user, 'first_name', None), getattr(user, 'last_name', None)])) or 'Unavailable'}")
    username = getattr(user, "username", None)
    output_fn(f"  Username: @{username}" if username else "  Username: Not set")
    output_fn(f"  Phone: {_mask_phone(getattr(user, 'phone', None))}")


def run_account_management_menu(
    client: Any | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:
    """Show the configured session's status/profile and offer confirmed sign-out."""
    try:
        with connected_telegram_client(client) as telegram:
            if not telegram.is_user_authorized():
                output_fn("No authorized Telegram session is active.")
                return

            while True:
                output_fn("\n[1] View account profile")
                output_fn("[2] Log out this Telegram account")
                output_fn("[0] Back to main menu")
                choice = input_fn("Select an option: ").strip()

                if choice == "0":
                    return
                if choice == "1":
                    _display_profile(telegram.get_me(), output_fn)
                elif choice == "2":
                    confirm = input_fn("Log out and revoke this Telegram session? (y/N): ").strip().lower()
                    if confirm not in {"y", "yes"}:
                        output_fn("Logout cancelled.")
                        continue
                    if telegram.log_out():
                        output_fn("Logged out. This local session is no longer authorized.")
                    else:
                        output_fn("Telegram did not confirm logout. Session status may be unchanged.")
                    return
                else:
                    output_fn("Invalid option. Please choose 0-2.")
    except Exception:
        output_fn("Account management failed. Check your connection and local configuration.")
