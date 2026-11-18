"""Local SQLite persistence for scraped Telegram member records."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from config import DATA_DIR

DEFAULT_DB_PATH = DATA_DIR / "members.sqlite3"


class MemberStore:
    """Store the minimum member fields needed for later CSV workflows."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    source_id INTEGER,
                    source_title TEXT,
                    scraped_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_members_username ON members(username)"
            )

    def save_member(self, member: dict) -> bool:
        """Upsert one member; return True only when the ID was not already stored."""
        user_id = int(member["user_id"])
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM members WHERE user_id = ?", (user_id,)
            ).fetchone() is not None
            connection.execute(
                """
                INSERT INTO members
                    (user_id, username, first_name, last_name, source_id, source_title)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    source_id=excluded.source_id,
                    source_title=excluded.source_title,
                    scraped_at=CURRENT_TIMESTAMP
                """,
                (
                    user_id,
                    member.get("username"),
                    member.get("first_name"),
                    member.get("last_name"),
                    member.get("source_id"),
                    member.get("source_title"),
                ),
            )
            return not exists

    def save_members(self, members: Iterable[dict]) -> int:
        """Upsert a batch and return the number of supplied records."""
        records = [
            (
                int(item["user_id"]),
                item.get("username"),
                item.get("first_name"),
                item.get("last_name"),
                item.get("source_id"),
                item.get("source_title"),
            )
            for item in members
        ]
        if not records:
            return 0
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO members
                    (user_id, username, first_name, last_name, source_id, source_title)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    source_id=excluded.source_id,
                    source_title=excluded.source_title,
                    scraped_at=CURRENT_TIMESTAMP
                """,
                records,
            )
        return len(records)

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM members").fetchone()[0])

    def list_members(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT user_id, username, first_name, last_name, source_id, source_title
                FROM members ORDER BY user_id
                """
            ).fetchall()
        return [dict(row) for row in rows]
