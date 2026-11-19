"""Tests for member CSV import and export."""

import csv
import tempfile
import unittest
from pathlib import Path

from modules.csv_manager import CSVImportError, export_members, import_members
from modules.storage import MemberStore


class CSVManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.store = MemberStore(self.directory / "members.sqlite3")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_and_import_round_trip_with_unicode(self):
        self.store.save_members([
            {
                "user_id": 101,
                "username": "kee",
                "first_name": "မြန်မာ",
                "last_name": "User",
                "source_id": -100123,
                "source_title": "测试群",
            },
            {"user_id": 102, "first_name": "Second"},
        ])
        path = self.directory / "members.csv"

        self.assertEqual(export_members(path, store=self.store), 2)
        self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))

        target = MemberStore(self.directory / "imported.sqlite3")
        result = import_members(path, store=target)
        self.assertEqual(result["imported"], 2)
        self.assertEqual(result["invalid_rows"], 0)
        self.assertEqual(target.list_members()[0]["first_name"], "မြန်မာ")
        self.assertEqual(target.list_members()[0]["source_id"], -100123)

    def test_import_accepts_utf8_bom_and_last_duplicate_wins(self):
        path = self.directory / "duplicates.csv"
        path.write_text(
            "user_id,username,first_name\n7,first,First\n7,last,Last\n",
            encoding="utf-8-sig",
        )

        result = import_members(path, store=self.store)
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["duplicate_rows"], 1)
        self.assertEqual(self.store.list_members()[0]["username"], "last")

    def test_invalid_rows_are_skipped_without_blocking_valid_rows(self):
        path = self.directory / "mixed.csv"
        path.write_text(
            "user_id,username,source_id\n"
            "1,valid,123\n"
            "not-a-number,bad,123\n"
            "-2,negative,123\n"
            "3,valid-three,not-int\n",
            encoding="utf-8",
        )

        result = import_members(path, store=self.store)
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["invalid_rows"], 3)
        self.assertEqual(self.store.count(), 1)

    def test_sqlite_integer_overflow_is_reported_as_invalid_row(self):
        path = self.directory / "overflow.csv"
        path.write_text(
            "user_id,source_id\n"
            "9223372036854775808,123\n"
            "5,999999999999999999999999999999999999\n",
            encoding="utf-8",
        )
        result = import_members(path, store=self.store)
        self.assertEqual(result["imported"], 0)
        self.assertEqual(result["invalid_rows"], 2)
        self.assertEqual(self.store.count(), 0)

    def test_missing_required_header_is_rejected_without_writes(self):
        path = self.directory / "missing-header.csv"
        path.write_text("username,first_name\nuser,Name\n", encoding="utf-8")

        with self.assertRaises(CSVImportError):
            import_members(path, store=self.store)
        self.assertEqual(self.store.count(), 0)

    def test_missing_file_is_rejected(self):
        with self.assertRaises(FileNotFoundError):
            import_members(self.directory / "absent.csv", store=self.store)

    def test_export_rejects_missing_parent_directory(self):
        destination = self.directory / "missing" / "out.csv"
        with self.assertRaises(FileNotFoundError):
            export_members(destination, store=self.store)
        self.assertFalse(destination.parent.exists())

    def test_export_empty_database_writes_header(self):
        path = self.directory / "empty.csv"
        self.assertEqual(export_members(path, store=self.store), 0)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(rows[0][0], "user_id")
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
