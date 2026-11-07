"""
The store of the egg hunt of one client: one SQLite file with the tables eggs and claims.
Each count, each letter of a manager, and each leader derives from the two tables, so the file holds no other state.
"""
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# A claim with no undo time holds its egg. The unique index covers only those claims, so the first claim of an egg
# wins a tie, and an undo sets the egg live again while the claims table keeps the row of the undone claim.
SCHEMA = """
CREATE TABLE IF NOT EXISTS eggs (
    id INTEGER PRIMARY KEY,
    week INTEGER NOT NULL,
    page TEXT NOT NULL,
    target TEXT NOT NULL,
    action TEXT NOT NULL,
    conditions TEXT NOT NULL,
    letter TEXT NOT NULL,
    dropped_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS claims (
    egg_id INTEGER NOT NULL REFERENCES eggs (id),
    roster_id INTEGER NOT NULL,
    word TEXT,
    claimed_at TEXT NOT NULL,
    browser TEXT,
    undone_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS claims_egg_id ON claims (egg_id) WHERE undone_at IS NULL;
"""


@dataclass(frozen=True)
class Egg:
    """One dropped egg: where it hides, the action and the conditions that find it, and its letter."""

    id: int
    week: int
    page: str
    target: str
    action: str
    conditions: dict[str, Any]
    letter: str
    dropped_at: str


@dataclass(frozen=True)
class Claim:
    """One claim of an egg that holds: the egg, its letter, the roster, and the egg word, or None for a block."""

    egg_id: int
    letter: str
    roster_id: int
    word: str | None
    claimed_at: str


class AlreadyClaimed(Exception):
    """Another manager holds the claim of the egg."""


class EggStore:
    """The eggs and the claims of one client in one SQLite file. Each call opens its own connection, so the threads
    of the API never share one."""

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

    def eggs(self, week: int | None = None) -> list[Egg]:
        """Each dropped egg in the order of the drop, or only the eggs of `week`."""
        with self._connect() as db:
            if week is None:
                rows = db.execute("SELECT * FROM eggs ORDER BY id").fetchall()
            else:
                rows = db.execute("SELECT * FROM eggs WHERE week = ? ORDER BY id", (week,)).fetchall()
        return [_egg(row) for row in rows]

    def drop(self, week: int, eggs: list[dict[str, Any]], now: datetime) -> list[Egg]:
        """Make the eggs of `week` live. A second drop of one week adds nothing, and returns the eggs already there."""
        with self._connect() as db:
            if db.execute("SELECT 1 FROM eggs WHERE week = ?", (week,)).fetchone() is None:
                db.executemany(
                    "INSERT INTO eggs (week, page, target, action, conditions, letter, dropped_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [(week, egg["page"], egg["target"], egg["action"], json.dumps(egg["conditions"], sort_keys=True),
                      egg["letter"], now.isoformat()) for egg in eggs])
        return self.eggs(week)

    def find(self, page: str, target: str, action: str) -> list[Egg]:
        """Each egg on `target` of `page` that `action` finds. The caller checks the conditions of each one."""
        with self._connect() as db:
            rows = db.execute("SELECT * FROM eggs WHERE page = ? AND target = ? AND action = ? ORDER BY id",
                              (page, target, action)).fetchall()
        return [_egg(row) for row in rows]

    def claim_of(self, egg_id: int) -> Claim | None:
        """The claim that holds the egg, or None when the egg is live."""
        return next((claim for claim in self.claims() if claim.egg_id == egg_id), None)

    def claim(self, egg_id: int, roster_id: int, word: str | None, browser: str | None, now: datetime) -> None:
        """Claim the egg for the roster. A second claim of one egg raises AlreadyClaimed, so the first write wins."""
        try:
            with self._connect() as db:
                db.execute("INSERT INTO claims (egg_id, roster_id, word, claimed_at, browser) VALUES (?, ?, ?, ?, ?)",
                           (egg_id, roster_id, word, now.isoformat(), browser))
        except sqlite3.IntegrityError:
            raise AlreadyClaimed() from None

    def undo(self, egg_id: int, now: datetime) -> bool:
        """Set the undo time of the claim that holds the egg, so the egg is live again. False when no claim holds it."""
        with self._connect() as db:
            cursor = db.execute("UPDATE claims SET undone_at = ? WHERE egg_id = ? AND undone_at IS NULL",
                                (now.isoformat(), egg_id))
        return cursor.rowcount > 0

    def claims(self) -> list[Claim]:
        """Each claim that holds its egg, newest first. An undone claim stays in the table and is not in the list."""
        with self._connect() as db:
            rows = db.execute(
                "SELECT claims.egg_id, eggs.letter, claims.roster_id, claims.word, claims.claimed_at FROM claims "
                "JOIN eggs ON eggs.id = claims.egg_id WHERE claims.undone_at IS NULL "
                "ORDER BY claims.claimed_at DESC, claims.rowid DESC").fetchall()
        return [Claim(egg_id=row["egg_id"], letter=row["letter"], roster_id=row["roster_id"], word=row["word"],
                      claimed_at=row["claimed_at"]) for row in rows]


def _egg(row: sqlite3.Row) -> Egg:
    return Egg(id=row["id"], week=row["week"], page=row["page"], target=row["target"], action=row["action"],
               conditions=json.loads(row["conditions"]), letter=row["letter"], dropped_at=row["dropped_at"])
