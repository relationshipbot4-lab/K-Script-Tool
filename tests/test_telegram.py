"""Tests for the configured Telethon client interface."""

import inspect
import unittest

from telethon.sync import TelegramClient as SyncTelegramClient

from core.telegram import TelegramClient as ConfiguredTelegramClient


class TelegramClientTests(unittest.TestCase):
    def test_factory_uses_synchronous_telethon_client(self):
        self.assertIs(ConfiguredTelegramClient, SyncTelegramClient)
        self.assertFalse(inspect.iscoroutinefunction(ConfiguredTelegramClient.connect))
        self.assertFalse(
            inspect.iscoroutinefunction(ConfiguredTelegramClient.is_user_authorized)
        )


if __name__ == "__main__":
    unittest.main()
