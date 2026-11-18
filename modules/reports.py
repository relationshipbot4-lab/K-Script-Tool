"""Local activity reporting helpers."""


def summarize_results(results: list[dict]) -> dict[str, int]:
    """Count result records by their status field."""
    summary = {"success": 0, "failed": 0, "skipped": 0, "pending": 0}
    for result in results:
        status = str(result.get("status", "pending")).lower()
        if status in summary:
            summary[status] += 1
    summary["total"] = sum(summary.values())
    return summary
