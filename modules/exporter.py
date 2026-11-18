"""Member-list import and export helpers."""

import csv
from pathlib import Path
from typing import Iterable, Mapping

from config import DATA_DIR

DEFAULT_EXPORT = DATA_DIR / "members.csv"


def export_members(
    members: Iterable[Mapping[str, object]],
    destination: Path = DEFAULT_EXPORT,
) -> int:
    """Write member records to CSV and return the number of exported rows."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=("user_id", "username", "display_name"),
            extrasaction="ignore",
        )
        writer.writeheader()
        for member in members:
            writer.writerow(member)
            count += 1
    return count
