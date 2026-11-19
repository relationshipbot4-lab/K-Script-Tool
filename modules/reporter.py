"""Privacy-conscious local operation reports for K SCRIPT TOOL.

Reports contain only operation labels, outcomes and UTC timestamps. No group
names, user IDs, usernames, invite links, credentials, or raw exceptions are
stored.
"""
from __future__ import annotations

import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from config import DATA_DIR

REPORT_FILE = DATA_DIR / "operation_reports.jsonl"
_ALLOWED_OPERATIONS = {
    "csv_import_export",
    "member_scrape",
    "group_join_or_invite",
}
_ALLOWED_OUTCOMES = {"success", "failure", "cancelled"}
_ALLOWED_DETAIL_KEYS = {"processed", "saved", "skipped", "invalid", "duplicates", "total"}


def record_operation(
    operation: str,
    outcome: str,
    *,
    details: dict[str, int] | None = None,
    path: str | Path = REPORT_FILE,
) -> bool:
    """Append a small sanitized event. Never let reporting break core actions."""
    if operation not in _ALLOWED_OPERATIONS or outcome not in _ALLOWED_OUTCOMES:
        return False
    safe_details: dict[str, int] = {}
    for key, value in (details or {}).items():
        if key in _ALLOWED_DETAIL_KEYS and isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            safe_details[key] = value
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "operation": operation,
        "outcome": outcome,
        "details": safe_details,
    }
    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return True
    except (OSError, TypeError, ValueError):
        return False


def _iter_valid_events(path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield well-shaped events line-by-line; malformed records are ignored."""
    target = Path(path)
    try:
        with target.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (
                    isinstance(event, dict)
                    and event.get("operation") in _ALLOWED_OPERATIONS
                    and event.get("outcome") in _ALLOWED_OUTCOMES
                    and isinstance(event.get("timestamp"), str)
                ):
                    yield event
    except (OSError, UnicodeDecodeError):
        return


def read_reports(*, limit: int = 100, path: str | Path = REPORT_FILE) -> list[dict[str, Any]]:
    """Read at most limit valid events into memory and return newest first."""
    if limit < 1:
        raise ValueError("limit must be positive.")
    recent: deque[dict[str, Any]] = deque(maxlen=limit)
    for event in _iter_valid_events(path):
        recent.append(event)
    return list(reversed(recent))


def summarize_reports(*, path: str | Path = REPORT_FILE) -> dict[str, Any]:
    """Summarize all events using constant memory regardless of file size."""
    counts: dict[str, Any] = {
        "total": 0,
        "success": 0,
        "failure": 0,
        "cancelled": 0,
        "by_operation": {
            operation: {"total": 0, "success": 0, "failure": 0, "cancelled": 0}
            for operation in sorted(_ALLOWED_OPERATIONS)
        },
    }
    for event in _iter_valid_events(path):
        operation = event["operation"]
        outcome = event["outcome"]
        counts["total"] += 1
        counts[outcome] += 1
        counts["by_operation"][operation]["total"] += 1
        counts["by_operation"][operation][outcome] += 1
    return counts


def run_report_menu(output_fn=print) -> None:
    """Display a compact aggregate and the most recent activity entries."""
    summary = summarize_reports()
    output_fn("\n=== Activity Report ===")
    output_fn(
        f"Total: {summary['total']} | Success: {summary['success']} | "
        f"Failed: {summary['failure']} | Cancelled: {summary['cancelled']}"
    )
    output_fn("\nBy operation:")
    labels = {
        "csv_import_export": "CSV import/export",
        "member_scrape": "Member scrape",
        "group_join_or_invite": "Group join/invite",
    }
    for operation, result in summary["by_operation"].items():
        output_fn(
            f"- {labels[operation]}: {result['total']} total, "
            f"{result['success']} success, {result['failure']} failed, "
            f"{result['cancelled']} cancelled"
        )
    recent = read_reports(limit=10)
    output_fn("\nRecent activity (latest 10):")
    if not recent:
        output_fn("No operation history yet.")
    for event in recent:
        output_fn(
            f"- {event['timestamp']} | {labels[event['operation']]} | "
            f"{event['outcome'].upper()}"
        )
    output_fn("\nReport file: data/operation_reports.jsonl")
