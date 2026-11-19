"""Tests for authorized member scraping."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from telethon.errors import FloodWaitError

from modules.scraper import ScrapeRateLimitError, scrape_members


class FakeStore:
    def __init__(self):
        self.members = {}

    def save_member(self, member):
        self.members[member["user_id"]] = member

    def count(self):
        return len(self.members)


class ScraperTests(unittest.TestCase):
    def test_scrapes_accessible_users_and_skips_bots_and_deleted(self):
        entity = SimpleNamespace(id=99, title="Test Group")
        client = Mock()
        client.get_entity.return_value = entity
        client.iter_participants.return_value = iter([
            SimpleNamespace(id=1, username="one", first_name="One", last_name=None),
            SimpleNamespace(id=2, bot=True, deleted=False),
            SimpleNamespace(id=3, deleted=True, bot=False),
            SimpleNamespace(id=4, username=None, first_name="Four", last_name="User"),
        ])
        store = FakeStore()
        progress = []

        result = scrape_members(
            client, "testgroup", store=store, progress_callback=progress.append
        )

        self.assertEqual(result["scanned"], 4)
        self.assertEqual(result["saved"], 2)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(set(store.members), {1, 4})
        self.assertEqual(progress, [1, 2, 3, 4])
        client.get_entity.assert_called_once_with("testgroup")

    def test_stop_event_stops_before_processing_next_member(self):
        from threading import Event

        stop = Event()
        stop.set()
        client = Mock()
        client.get_entity.return_value = SimpleNamespace(id=5, title="Group")
        client.iter_participants.return_value = iter([
            SimpleNamespace(id=1, bot=False, deleted=False)
        ])
        store = FakeStore()

        result = scrape_members(client, 5, store=store, stop_event=stop)

        self.assertEqual(result["scanned"], 0)
        self.assertEqual(result["saved"], 0)
        self.assertEqual(store.members, {})

    def test_flood_wait_is_reported_without_retry(self):
        client = Mock()
        client.get_entity.return_value = SimpleNamespace(id=6, title="Group")

        def members(_entity, limit=None):
            raise FloodWaitError(None, 42)
            yield  # Make this a generator.

        client.iter_participants.side_effect = members
        with self.assertRaisesRegex(ScrapeRateLimitError, "42 seconds"):
            scrape_members(client, 6, store=FakeStore())
        client.iter_participants.assert_called_once_with(
            client.get_entity.return_value, limit=None
        )

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            scrape_members(Mock(), "group", store=FakeStore(), limit=0)


if __name__ == "__main__":
    unittest.main()
