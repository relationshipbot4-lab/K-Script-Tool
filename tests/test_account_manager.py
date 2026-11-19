"""Tests for Telegram account management actions."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from core.account_manager import _mask_phone, _display_profile, run_account_management_menu


class AccountManagerTests(unittest.TestCase):
    def test_phone_masking(self):
        self.assertEqual(_mask_phone("+12345678901"), "***901")
        self.assertEqual(_mask_phone(None), "Not available")
        self.assertEqual(_mask_phone("123"), "***")

    def test_profile_displays_masked_phone_and_profile_fields(self):
        user = SimpleNamespace(id=54321, first_name="Test", last_name="User", username="tester", phone="+12345678901")
        out = []
        _display_profile(user, out.append)
        self.assertIn("User ID: 54321", "\n".join(out))
        self.assertIn("Name: Test User", "\n".join(out))
        self.assertIn("Username: @tester", "\n".join(out))
        self.assertIn("Phone: ***901", "\n".join(out))
        self.assertNotIn("+12345678901", "\n".join(out))

    def test_unauthorized_session_reports_no_active_login(self):
        client = Mock()
        client.is_user_authorized.return_value = False
        out = []
        run_account_management_menu(client=client, output_fn=out.append)
        self.assertTrue(any("No authorized Telegram session" in line for line in out))
        client.disconnect.assert_called_once()

    def test_logout_cancelled_does_not_call_log_out(self):
        client = Mock()
        client.is_user_authorized.return_value = True
        out = []
        answers = iter(["2", "n"])
        run_account_management_menu(client=client, input_fn=lambda _p: next(answers), output_fn=out.append)
        client.log_out.assert_not_called()
        self.assertTrue(any("Logout cancelled" in line for line in out))
        client.disconnect.assert_called_once()

    def test_confirmed_logout_invokes_telethon_logout(self):
        client = Mock()
        client.is_user_authorized.return_value = True
        client.log_out.return_value = True
        out = []
        answers = iter(["2", "yes"])
        run_account_management_menu(client=client, input_fn=lambda _p: next(answers), output_fn=out.append)
        client.log_out.assert_called_once()
        self.assertTrue(any("Logged out" in line for line in out))
        client.disconnect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
