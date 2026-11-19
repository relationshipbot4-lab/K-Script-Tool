"""Unit tests for terminal UI clearing and main-menu redraw."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import main


class MainMenuTests(unittest.TestCase):
    def test_clear_screen_uses_ansi_sequences(self):
        output = StringIO()
        with redirect_stdout(output):
            main.clear_screen()
        self.assertEqual(output.getvalue(), "\\033[2J\\033[H")

    def test_startup_clears_and_shows_banner(self):
        with patch.object(main, "clear_screen") as clear_mock, patch.object(
            main, "show_banner"
        ) as banner_mock, patch.object(main, "show_menu"), patch(
            "builtins.input", side_effect=["0"]
        ):
            main.main()
        clear_mock.assert_called_once()
        banner_mock.assert_called_once()

    def test_returning_from_submenu_clears_and_redraws_banner(self):
        with patch.object(main, "clear_screen") as clear_mock, patch.object(
            main, "show_banner"
        ) as banner_mock, patch.object(main, "show_menu"), patch.object(
            main, "authenticate_telegram_account"
        ) as auth_mock, patch("builtins.input", side_effect=["1", "0"]):
            main.main()
        auth_mock.assert_called_once()
        self.assertEqual(clear_mock.call_count, 2)
        self.assertEqual(banner_mock.call_count, 2)

    def test_invalid_option_does_not_clear_before_message_is_printed(self):
        output = StringIO()
        with patch.object(main, "clear_screen"), patch.object(
            main, "show_banner"
        ), patch.object(main, "show_menu"), patch(
            "builtins.input", side_effect=["invalid", "0"]
        ), redirect_stdout(output):
            main.main()
        self.assertIn("Invalid option. Please choose 0-5.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
