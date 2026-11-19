"""Tests for the configured Telethon client interface."""

import inspect
import unittest

from telethon.sync import TelegramClient as SyncTelegramClient

from core.telegram import TelegramClient as ConfiguredTelegramClient


class TelegramClientTests(unittest.TestCase):
    def test_shared_connection_helper_disconnects_after_success(self):
        client = Mock()
        with connected_telegram_client(client) as connected:
            self.assertIs(connected, client)
        client.connect.assert_called_once()
        client.disconnect.assert_called_once()

    def test_shared_connection_helper_disconnects_after_connect_error(self):
        client = Mock()
        client.connect.side_effect = RuntimeError("connection failed")
        with self.assertRaisesRegex(RuntimeError, "connection failed"):
            with connected_telegram_client(client):
                pass
        client.disconnect.assert_called_once()

    def test_factory_uses_synchronous_telethon_client(self):
        self.assertIs(ConfiguredTelegramClient, SyncTelegramClient)
        self.assertFalse(inspect.iscoroutinefunction(ConfiguredTelegramClient.connect))
        self.assertFalse(
            inspect.iscoroutinefunction(ConfiguredTelegramClient.is_user_authorized)
        )


if __name__ == "__main__":
    unittest.main()
