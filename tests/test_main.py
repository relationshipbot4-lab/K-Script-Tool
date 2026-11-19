"""Unit tests for terminal UI clearing and main-menu navigation."""

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

    def test_returning_from_account_setup_redraws(self):
        with patch.object(main, "clear_screen") as clear_mock, patch.object(
            main, "show_banner"
        ) as banner_mock, patch.object(main, "show_menu"), patch.object(
            main, "authenticate_telegram_account"
        ) as auth_mock, patch("builtins.input", side_effect=["1", "0"]):
            main.main()
        auth_mock.assert_called_once()
        self.assertEqual(clear_mock.call_count, 2)
        self.assertEqual(banner_mock.call_count, 2)

    def test_main_menu_routes_options_2_through_5(self):
        with patch.object(main, "clear_screen") as clear_mock, patch.object(
            main, "show_banner"
        ) as banner_mock, patch.object(main, "show_menu"), patch.object(
            main, "run_csv_menu"
        ) as csv_mock, patch.object(main, "run_scraper_menu") as scrape_mock, patch.object(
            main, "run_invite_menu"
        ) as invite_mock, patch.object(main, "run_report_menu") as report_mock, patch(
            "builtins.input", side_effect=["2", "3", "4", "5", "0"]
        ):
            main.main()
        csv_mock.assert_called_once()
        scrape_mock.assert_called_once()
        invite_mock.assert_called_once()
        report_mock.assert_called_once()
        self.assertEqual(clear_mock.call_count, 5)
        self.assertEqual(banner_mock.call_count, 5)

    def test_account_management_menu_routes_to_handler(self):
        with patch.object(main, "clear_screen"), patch.object(
            main, "show_banner"
        ), patch.object(main, "show_menu"), patch.object(
            main, "run_account_management_menu"
        ) as account_mock, patch("builtins.input", side_effect=["6", "0"]):
            main.main()
        account_mock.assert_called_once()

    def test_invalid_option_message(self):
        output = StringIO()
        with patch.object(main, "clear_screen"), patch.object(
            main, "show_banner"
        ), patch.object(main, "show_menu"), patch(
            "builtins.input", side_effect=["invalid", "0"]
        ), redirect_stdout(output):
            main.main()
        self.assertIn("Invalid option. Please choose 0-6.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
