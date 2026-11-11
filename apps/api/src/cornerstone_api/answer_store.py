"""
The kept Answers of the personal Topics and the kept free answers of one client: one SQLite file with one table, on the
Fly volume and never in the repo. Each key comes from the data the Answer read, so the same data gives it back free.
"""
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS answers (
    key TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    roster_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    kept_at TEXT NOT NULL
);
"""


class AnswerStore:
    """The kept Answers of one client in one SQLite file. Each call opens its own connection, so the threads of the API
    never share one."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def get(self, key: str) -> dict | None:
        """The kept Answer of `key`, or None when no Answer has that key."""
        with self._connect() as db:
            row = db.execute("SELECT answer FROM answers WHERE key = ?", (key,)).fetchone()
        return None if row is None else json.loads(row["answer"])

    def put(self, key: str, topic: str, roster_id: int, answer: dict, now: datetime) -> None:
        """Keep the checked Answer of `key`. A second Answer of the same key replaces the first."""
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO answers (key, topic, roster_id, answer, kept_at) VALUES (?, ?, ?, ?, ?)",
                       (key, topic, roster_id, json.dumps(answer), now.isoformat()))

    def kept_at(self, key: str) -> str | None:
        """The ISO time when the store kept the Answer of `key`, or None when no Answer has that key."""
        with self._connect() as db:
            row = db.execute("SELECT kept_at FROM answers WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row["kept_at"])
