"""
The miss log of the ask box of one client: one SQLite file with one table, on the Fly volume and never in the repo.
Each entry holds the question, the team, the time, and the 3 closest Topics. A write removes each entry past 90 days.
"""
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# ADR 0031: a typed question can name a person, so the log keeps each entry for 90 days only.
KEEP = timedelta(days=90)

SCHEMA = """
CREATE TABLE IF NOT EXISTS misses (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    roster_id INTEGER NOT NULL,
    team TEXT NOT NULL,
    asked_at TEXT NOT NULL,
    closest TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class Miss:
    """One honest miss: the question as typed, Your team, the time, and the closest Topics in order."""

    question: str
    roster_id: int
    team: str
    asked_at: str
    closest: list[str]


class MissLog:
    """The misses of one client in one SQLite file. Each call opens its own connection, so the threads of the API never
    share one."""

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

    def write(self, question: str, roster_id: int, team: str, closest: list[str], now: datetime) -> None:
        """Add one miss, and remove each miss older than KEEP in the same step."""
        with self._connect() as db:
            # Every time is in the timezone of the client, so the text of two times sorts as the times do, to the hour of
            # a change of daylight time.
            db.execute("DELETE FROM misses WHERE asked_at < ?", ((now - KEEP).isoformat(),))
            db.execute("INSERT INTO misses (question, roster_id, team, asked_at, closest) VALUES (?, ?, ?, ?, ?)",
                       (question, roster_id, team, now.isoformat(), json.dumps(closest)))

    def misses(self) -> list[Miss]:
        """Each kept miss, oldest first."""
        with self._connect() as db:
            rows = db.execute("SELECT * FROM misses ORDER BY id").fetchall()
        return [Miss(question=row["question"], roster_id=row["roster_id"], team=row["team"],
                     asked_at=row["asked_at"], closest=json.loads(row["closest"])) for row in rows]
