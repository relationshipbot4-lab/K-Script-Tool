"""Authentication unit tests."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from core.auth import authenticate_telegram_account


class AuthenticationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
