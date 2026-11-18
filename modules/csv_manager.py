"""CSV import/export for locally stored Telegram member records."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import Any

from modules.storage import DEFAULT_DB_PATH, MemberStore

CSV_FIELDS = (
    "user_id",
    "username",
    "first_name",
    "last_name",
    "source_id",
    "source_title",
)
REQUIRED_FIELDS = {"user_id"}
OPTIONAL_TEXT_FIELDS = {"username", "first_name", "last_name", "source_title"}


class CSVImportError(ValueError):
    """Raised when a CSV file cannot be read or has an invalid header."""


def export_members(
    path: str | Path,
    *,
    store: MemberStore | None = None,
) -> int:
    """Write all stored members to a UTF-8-with-BOM CSV file.

    The destination is replaced atomically after a complete successful write.
    """
    destination = Path(path).expanduser()
    if destination.exists() and destination.is_dir():
        raise IsADirectoryError("CSV destination must be a file.")
    if not destination.parent.exists():
        raise FileNotFoundError("CSV destination directory does not exist.")

    records = (store or MemberStore(DEFAULT_DB_PATH)).list_members()
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            newline="",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temp_name = temporary.name
            writer = csv.DictWriter(
                temporary,
                fieldnames=CSV_FIELDS,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(records)
        os.replace(temp_name, destination)
    except (OSError, csv.Error):
        if temp_name:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
        raise
    return len(records)


def _optional_integer(value: Any, field: str, line_number: int) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except (TypeError, ValueError):
        raise ValueError(f"line {line_number}: {field} must be an integer.") from None


def import_members(
    path: str | Path,
    *,
    store: MemberStore | None = None,
) -> dict[str, Any]:
    """Validate a CSV fully, then upsert its valid unique member records.

    UTF-8 and UTF-8-BOM files are supported. The last valid occurrence of a
    repeated user_id wins. Invalid rows are skipped and reported by line.
    No database writes occur if the CSV itself is unreadable or malformed.
    """
    source = Path(path).expanduser()
    if not source.is_file():
        raise FileNotFoundError("CSV source file does not exist.")

    members_by_id: dict[int, dict[str, Any]] = {}
    duplicate_rows = 0
    invalid_rows = 0
    row_errors: list[str] = []

    try:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or ())
            missing = REQUIRED_FIELDS - headers
            if missing:
                raise CSVImportError(
                    "CSV is missing required column(s): "
                    + ", ".join(sorted(missing))
                )

            for line_number, row in enumerate(reader, start=2):
                try:
                    raw_user_id = str(row.get("user_id") or "").strip()
                    user_id = int(raw_user_id)
                    if user_id <= 0:
                        raise ValueError(
                            f"line {line_number}: user_id must be a positive integer."
                        )

                    member: dict[str, Any] = {"user_id": user_id}
                    for field in OPTIONAL_TEXT_FIELDS:
                        value = str(row.get(field) or "").strip()
                        member[field] = value or None
                    member["source_id"] = _optional_integer(
                        row.get("source_id"), "source_id", line_number
                    )

                    if user_id in members_by_id:
                        duplicate_rows += 1
                    members_by_id[user_id] = member
                except (TypeError, ValueError) as exc:
                    invalid_rows += 1
                    row_errors.append(str(exc))
    except UnicodeDecodeError:
        raise CSVImportError("CSV must use UTF-8 or UTF-8 with BOM encoding.") from None
    except csv.Error:
        raise CSVImportError("CSV contains malformed data and could not be imported.") from None

    imported = (store or MemberStore(DEFAULT_DB_PATH)).save_members(
        members_by_id.values()
    )
    return {
        "imported": imported,
        "duplicate_rows": duplicate_rows,
        "invalid_rows": invalid_rows,
        "errors": row_errors,
    }


def run_csv_menu(
    input_fn=input,
    output_fn=print,
) -> bool:
    """Interactive CSV import/export menu using the local member database."""
    default_path = Path("data") / "members_export.csv"
    output_fn("\n[1] Export stored members to CSV")
    output_fn("[2] Import members from CSV")
    output_fn("[0] Back")
    choice = input_fn("Select an option: ").strip()

    if choice == "0":
        return True
    if choice == "1":
        raw_path = input_fn(
            f"Export file path (Enter for {default_path}): "
        ).strip()
        destination = Path(raw_path).expanduser() if raw_path else default_path
        if destination.suffix.lower() != ".csv":
            destination = destination.with_suffix(".csv")
        try:
            count = export_members(destination)
            output_fn(f"Export complete: {count} member(s) written to {destination}.")
            return True
        except (OSError, csv.Error):
            output_fn("Export failed. Check the destination path and permissions.")
            return False

    if choice == "2":
        raw_path = input_fn("CSV file path to import: ").strip()
        if not raw_path:
            output_fn("No CSV file was provided.")
            return False
        source = Path(raw_path).expanduser()
        if input_fn(f"Import records from {source}? [y/N]: ").strip().lower() != "y":
            output_fn("Import cancelled.")
            return False
        try:
            result = import_members(source)
            output_fn(
                f"Import complete: {result['imported']} unique member(s) processed, "
                f"{result['duplicate_rows']} duplicate row(s), "
                f"{result['invalid_rows']} invalid row(s)."
            )
            for error in result["errors"][:10]:
                output_fn(error)
            if len(result["errors"]) > 10:
                output_fn(f"...and {len(result['errors']) - 10} more invalid row(s).")
            return True
        except (OSError, CSVImportError):
            output_fn("Import failed. Check the CSV file, encoding, and required user_id column.")
            return False

    output_fn("Invalid option.")
    return False
