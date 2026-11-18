"""Authentication unit tests for OTP, 2FA, and Telegram RPC failures."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from telethon.errors import (
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)

from core.auth import authenticate_telegram_account


class AuthenticationTests(unittest.TestCase):
    def make_logged_out_client(self):
        client = Mock()
        client.is_user_authorized.side_effect = [False, True]
        client.send_code_request.return_value = SimpleNamespace(
            phone_code_hash="test-phone-code-hash"
        )
        client.get_me.return_value = SimpleNamespace(id=12345)
        return client

    def test_existing_authorized_session(self):
        client = Mock()
        client.is_user_authorized.return_value = True
        client.get_me.return_value = SimpleNamespace(id=12345)
        output = []

        result = authenticate_telegram_account(client=client, output_fn=output.append)

        self.assertTrue(result)
        client.send_code_request.assert_not_called()
        client.disconnect.assert_called_once()
        self.assertIn("12345", output[0])

    def test_invalid_phone_is_rejected(self):
        client = Mock()
        client.is_user_authorized.return_value = False
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: "invalid",
            output_fn=output.append,
        )

        self.assertFalse(result)
        client.send_code_request.assert_not_called()
        client.disconnect.assert_called_once()
        self.assertTrue(any("international phone number" in line for line in output))

    def test_otp_login_success(self):
        client = self.make_logged_out_client()
        answers = iter(["+12345678901", "12345"])
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )

        self.assertTrue(result)
        client.send_code_request.assert_called_once_with("+12345678901")
        client.sign_in.assert_called_once_with(
            phone="+12345678901",
            code="12345",
            phone_code_hash="test-phone-code-hash",
        )
        client.disconnect.assert_called_once()
        self.assertTrue(any("Login successful" in line for line in output))

    def test_two_step_verification_success(self):
        client = self.make_logged_out_client()
        client.sign_in.side_effect = [
            SessionPasswordNeededError(None),
            None,
        ]
        answers = iter(["+12345678901", "12345"])
        secret_answers = []
        output = []

        def secret_input(prompt):
            secret_answers.append(prompt)
            return "correct-test-password"

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            secret_input_fn=secret_input,
            output_fn=output.append,
        )

        self.assertTrue(result)
        self.assertEqual(len(secret_answers), 1)
        self.assertEqual(
            client.sign_in.call_args_list[1].kwargs,
            {"password": "correct-test-password"},
        )
        client.disconnect.assert_called_once()
        self.assertTrue(any("Login successful" in line for line in output))

    def test_two_step_verification_invalid_password(self):
        client = self.make_logged_out_client()
        client.sign_in.side_effect = [
            SessionPasswordNeededError(None),
            PasswordHashInvalidError(None),
        ]
        answers = iter(["+12345678901", "12345"])
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            secret_input_fn=lambda _prompt: "wrong-test-password",
            output_fn=output.append,
        )

        self.assertFalse(result)
        client.disconnect.assert_called_once()
        self.assertTrue(any("2FA password is incorrect" in line for line in output))

    def test_invalid_otp_is_reported_and_disconnected(self):
        self.assert_rpc_error_is_handled(
            PhoneCodeInvalidError(None),
            "verification code is invalid",
        )

    def test_expired_otp_is_reported_and_disconnected(self):
        self.assert_rpc_error_is_handled(
            PhoneCodeExpiredError(None),
            "verification code expired",
        )

    def test_invalid_phone_rpc_error_is_reported_and_disconnected(self):
        self.assert_rpc_error_is_handled(
            PhoneNumberInvalidError(None),
            "rejected the phone number",
        )

    def test_flood_wait_is_reported_and_disconnected(self):
        client = Mock()
        client.is_user_authorized.return_value = False
        client.send_code_request.side_effect = FloodWaitError(None, 37)
        answers = iter(["+12345678901"])
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )

        self.assertFalse(result)
        client.disconnect.assert_called_once()
        self.assertTrue(any("37 seconds" in line for line in output))

    def test_empty_otp_cancels_and_disconnects(self):
        client = self.make_logged_out_client()
        answers = iter(["+12345678901", ""])
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )

        self.assertFalse(result)
        client.sign_in.assert_not_called()
        client.disconnect.assert_called_once()
        self.assertTrue(any("no verification code" in line for line in output))

    def test_disconnect_runs_after_unexpected_rpc_failure(self):
        client = Mock()
        client.is_user_authorized.return_value = False
        client.send_code_request.side_effect = RuntimeError("private diagnostic")
        answers = iter(["+12345678901"])
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )

        self.assertFalse(result)
        client.disconnect.assert_called_once()
        self.assertTrue(any("Telegram login failed" in line for line in output))
        self.assertFalse(any("private diagnostic" in line for line in output))

    def assert_rpc_error_is_handled(self, error, expected_message):
        client = Mock()
        client.is_user_authorized.return_value = False
        client.send_code_request.return_value = SimpleNamespace(
            phone_code_hash="test-phone-code-hash"
        )
        client.sign_in.side_effect = error
        answers = iter(["+12345678901", "12345"])
        output = []

        result = authenticate_telegram_account(
            client=client,
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )

        self.assertFalse(result)
        client.disconnect.assert_called_once()
        self.assertTrue(any(expected_message in line for line in output))


if __name__ == "__main__":
    unittest.main()
