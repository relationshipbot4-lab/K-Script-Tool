"""Tests for sanitized local activity reports."""
import json
import tempfile
import unittest
from pathlib import Path

from modules.reporter import record_operation, read_reports, summarize_reports


class ReporterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "reports.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_record_and_summary(self):
        self.assertTrue(record_operation("member_scrape", "success", details={"saved": 9, "processed": 12}, path=self.path))
        self.assertTrue(record_operation("csv_import_export", "failure", path=self.path))
        summary = summarize_reports(path=self.path)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["success"], 1)
        self.assertEqual(summary["failure"], 1)
        self.assertEqual(summary["by_operation"]["member_scrape"]["success"], 1)

    def test_only_safe_metadata_is_saved(self):
        record_operation("member_scrape", "success", details={"saved": 3, "user_id": 999, "username": "secret"}, path=self.path)
        event = json.loads(self.path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["details"], {"saved": 3})
        self.assertNotIn("secret", self.path.read_text(encoding="utf-8"))

    def test_invalid_events_rejected(self):
        self.assertFalse(record_operation("unknown", "success", path=self.path))
        self.assertFalse(record_operation("member_scrape", "unexpected", path=self.path))
        self.assertFalse(self.path.exists())

    def test_corrupt_lines_skipped(self):
        self.path.write_text("{broken json}\n", encoding="utf-8")
        record_operation("csv_import_export", "success", path=self.path)
        self.assertEqual(len(read_reports(path=self.path)), 1)

    def test_invalid_and_terminal_control_timestamps_are_skipped(self):
        event = {
            "timestamp": "2026-11-19T00:00:00+00:00\u001b[2J",
            "operation": "member_scrape",
            "outcome": "success",
            "details": {},
        }
        self.path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        self.assertEqual(read_reports(path=self.path), [])

    def test_timestamp_is_normalized_to_utc(self):
        event = {
            "timestamp": "2026-11-19T05:30:00+05:30",
            "operation": "member_scrape",
            "outcome": "success",
            "details": {},
        }
        self.path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        reports = read_reports(path=self.path)
        self.assertEqual(reports[0]["timestamp"], "2026-11-19T00:00:00+00:00")

    def test_summary_streams_large_history(self):
        for i in range(1500):
            record_operation("member_scrape", "success" if i % 2 == 0 else "failure", path=self.path)
        summary = summarize_reports(path=self.path)
        self.assertEqual(summary["total"], 1500)
        self.assertEqual(summary["success"], 750)
        self.assertEqual(summary["failure"], 750)
        self.assertEqual(len(read_reports(limit=15, path=self.path)), 15)

    def test_bool_values_are_not_saved_as_counts(self):
        record_operation("member_scrape", "success", details={"saved": True, "total": 4}, path=self.path)
        event = json.loads(self.path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["details"], {"total": 4})

    def test_read_limit_validation(self):
        with self.assertRaises(ValueError):
            read_reports(limit=0, path=self.path)


if __name__ == "__main__":
    unittest.main()
