"""
The caps of the front door: 25 Claude Answers per team per day, and $25 of Claude cost per league per month.
One SQLite file per client on the Fly volume holds the spend. A Claude call site asks `check` first and calls `record` after.
"""
import logging
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from pydantic_ai.usage import RunUsage

logger = logging.getLogger(__name__)

# The hard caps of the spec (decision 04). They are separate: a team at its cap leaves the other teams free.
TEAM_ANSWERS_PER_DAY = 25
LEAGUE_USD_PER_MONTH = 25.00
# At this share of the monthly cap, the API logs one alert. It sends no email, because the API has no mail sender.
ALERT_SHARE = 0.8

# The exact lines of the spec. Neither line names a manager.
TEAM_LINE = f"That's {TEAM_ANSWERS_PER_DAY} questions today. Ask again tomorrow."
LEAGUE_LINE = "The league's question budget is used up for this month. It resets on {date}."

# The prices of Claude Sonnet 5.5 in dollars per million tokens, from the pricing page of Anthropic: $2 input, $10
# output, $0.20 for a cache read, 1.25 times the input for a 5-minute cache write, and 2 times for a 1-hour write.
SONNET_INPUT = 2.00
SONNET_OUTPUT = 10.00
SONNET_CACHE_READ = 0.20
SONNET_CACHE_WRITE_5M = 2.50
SONNET_CACHE_WRITE_1H = 4.00

# The spend of the month before stays one month for the log, then a write removes it.
SCHEMA = """
CREATE TABLE IF NOT EXISTS spend (
    id INTEGER PRIMARY KEY,
    roster_id INTEGER,
    day TEXT NOT NULL,
    month TEXT NOT NULL,
    usd REAL NOT NULL,
    counts INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS alerts (
    month TEXT PRIMARY KEY
);
"""


def sonnet_cost(usage: RunUsage) -> float:
    """The dollars of the Sonnet 5.5 calls of one Pydantic AI run, from its tokens.

    Pydantic AI counts the cache reads and the cache writes inside `input_tokens`, so the full input price applies
    only to the rest.
    """
    write_1h = usage.cache_write_1h_tokens
    write_5m = usage.cache_write_tokens - write_1h
    plain = usage.input_tokens - usage.cache_read_tokens - usage.cache_write_tokens
    return (plain * SONNET_INPUT + usage.output_tokens * SONNET_OUTPUT + usage.cache_read_tokens * SONNET_CACHE_READ
            + write_5m * SONNET_CACHE_WRITE_5M + write_1h * SONNET_CACHE_WRITE_1H) / 1_000_000


@dataclass(frozen=True)
class CapHit:
    """A cap that stops a new Claude Answer: which cap, and its calm line."""

    cap: Literal["team", "league"]
    line: str


def _next_month(now: datetime) -> date:
    return date(now.year + 1, 1, 1) if now.month == 12 else date(now.year, now.month + 1, 1)


def _month(now: datetime) -> str:
    return now.strftime("%Y-%m")


class Caps:
    """The spend of one client in one SQLite file. Each call opens its own connection, so the threads of the API never
    share one. A lock makes the sum and the alert of `record` one step, so two answers at once log one alert."""

    def __init__(self, path: Path, slug: str) -> None:
        self.path = path
        self.slug = slug
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path)
        try:
            with db:
                yield db
        finally:
            db.close()

    def answers_today(self, roster_id: int, now: datetime) -> int:
        """The Claude Answers of the team today, in the timezone of `now`."""
        with self._connect() as db:
            row = db.execute("SELECT COUNT(*) FROM spend WHERE roster_id = ? AND day = ? AND counts = 1",
                             (roster_id, now.date().isoformat())).fetchone()
        return int(row[0])

    def month_usd(self, now: datetime) -> float:
        """The Claude cost of the league in the month of `now`."""
        with self._connect() as db:
            row = db.execute("SELECT COALESCE(SUM(usd), 0) FROM spend WHERE month = ?", (_month(now),)).fetchone()
        return float(row[0])

    def check(self, roster_id: int, now: datetime) -> CapHit | None:
        """The cap that stops a new Claude Answer of the team, or None. Ask it before each Claude call.

        The league cap comes first, because it lasts longer and its line says when it ends.
        """
        if self.month_usd(now) >= LEAGUE_USD_PER_MONTH:
            when = _next_month(now)
            return CapHit("league", LEAGUE_LINE.format(date=f"{when:%b} {when.day}"))
        if self.answers_today(roster_id, now) >= TEAM_ANSWERS_PER_DAY:
            return CapHit("team", TEAM_LINE)
        return None

    def record(self, roster_id: int | None, usd: float, now: datetime, *, counts: bool) -> None:
        """Add the Claude cost of one call site to the league month. With `counts`, it is one Answer of the team.

        A kept Answer makes no call and records nothing. An honest miss, a failed call, and the head start record their
        cost with `counts` False. The first record past ALERT_SHARE of the month logs the one alert of the month.
        """
        month = _month(now)
        with self._lock, self._connect() as db:
            previous = _month(datetime(now.year - 1, 12, 1) if now.month == 1 else datetime(now.year, now.month - 1, 1))
            db.execute("DELETE FROM spend WHERE month < ?", (previous,))
            db.execute("INSERT INTO spend (roster_id, day, month, usd, counts) VALUES (?, ?, ?, ?, ?)",
                       (roster_id, now.date().isoformat(), month, usd, int(counts)))
            total = float(db.execute("SELECT SUM(usd) FROM spend WHERE month = ?", (month,)).fetchone()[0])
            if total < ALERT_SHARE * LEAGUE_USD_PER_MONTH:
                return
            if db.execute("INSERT OR IGNORE INTO alerts (month) VALUES (?)", (month,)).rowcount == 1:
                logger.warning("The league %s used $%.2f of its $%.2f Claude budget for %s, past 80%%.",
                               self.slug, total, LEAGUE_USD_PER_MONTH, month)
