"""Tests for local member storage."""

import tempfile
import unittest
from pathlib import Path

from modules.storage import MemberStore


class MemberStoreTests(unittest.TestCase):
    def test_upsert_deduplicates_by_user_id(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MemberStore(Path(directory) / "members.sqlite3")
            self.assertTrue(store.save_member({"user_id": 7, "username": "first"}))
            self.assertFalse(store.save_member({"user_id": 7, "username": "updated"}))
            members = store.list_members()
            self.assertEqual(len(members), 1)
            self.assertEqual(members[0]["username"], "updated")
            self.assertEqual(store.count(), 1)

    def test_empty_batch_is_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MemberStore(Path(directory) / "members.sqlite3")
            self.assertEqual(store.save_members([]), 0)
            self.assertEqual(store.count(), 0)


if __name__ == "__main__":
    unittest.main()
