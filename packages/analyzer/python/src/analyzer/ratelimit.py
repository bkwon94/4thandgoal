"""
The rate limits of the API by request address: a one-minute window in memory, and a per-day grade count in a file.
The file lives on the volume, so a restart keeps the day counts. The minute windows start empty on each restart.
"""
import json
import logging
import math
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import Request

from league.files import write_bytes_atomic

logger = logging.getLogger(__name__)

WINDOW_SECONDS = 60
# The most addresses the map holds before it drops the expired windows, so a flood of new addresses cannot fill memory.
MAX_TRACKED_ADDRESSES = 10_000


class RateLimiter:
    """Count the requests of each address in its current window."""

    def __init__(self, limit: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.limit = limit
        self.clock = clock
        # The start of the current window and the count in it, by address.
        self.windows: dict[str, tuple[float, int]] = {}

    def hit(self, address: str) -> int | None:
        """Count one request. Return None when it is within the limit, else the seconds until the window ends."""
        now = self.clock()
        start, count = self.windows.get(address, (now, 0))
        if now - start >= WINDOW_SECONDS:
            start, count = now, 0
        if count >= self.limit:
            return max(1, math.ceil(start + WINDOW_SECONDS - now))
        self.windows[address] = (start, count + 1)
        # Old windows go when the map grows, so a stream of new addresses cannot fill the memory.
        if len(self.windows) > MAX_TRACKED_ADDRESSES:
            self.windows = {a: w for a, w in self.windows.items() if now - w[0] < WINDOW_SECONDS}
        return None


def request_address(request: Request) -> str:
    """The address that sent the request. On Fly every request comes from the proxy, so the proxy sets Fly-Client-IP.

    The name says request and not client, because a Client is a league (GLOSSARY.md).
    """
    forwarded = request.headers.get("Fly-Client-IP")
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def seconds_to_midnight(now: datetime) -> int:
    """The seconds from `now` to the next midnight in the timezone of `now`, rounded up, never less than one."""
    midnight = datetime(now.year, now.month, now.day, tzinfo=now.tzinfo) + timedelta(days=1)
    # The timestamps hold the offset, so a day when the clocks change counts its real seconds and not wall time.
    return max(1, math.ceil(midnight.timestamp() - now.timestamp()))


@dataclass(frozen=True)
class GradeLimited:
    """A grade past a limit: which window is full, "minute" or "day", and the seconds until it ends."""

    window: Literal["minute", "day"]
    retry_after: int


class GradeLimiter:
    """Count the grades of each address in a one-minute window and in a calendar day in the league timezone.

    The minute window lives in memory. The day counts live in a JSON file, so a restart or a deploy keeps them.
    The file holds only today: {"day": "2026-10-19", "counts": {"<address>": <grades>}}.
    """

    def __init__(self, per_minute: int, per_day: int, path: Path, tz: ZoneInfo,
                 clock: Callable[[], datetime] | None = None) -> None:
        self.per_day = per_day
        self.path = path
        self.tz = tz
        # An aware datetime, so the day is the calendar day in the league timezone wherever the host runs.
        self.clock = clock or (lambda: datetime.now(tz))
        self.minute = RateLimiter(per_minute, clock=lambda: self.clock().timestamp())
        # FastAPI runs the sync route in a thread pool. Without the lock, two grades at once both read N and both
        # write N+1, so one grade goes uncounted. The lock covers the minute check too, for the same reason.
        self.lock = threading.Lock()
        # The counts of today in this process. When a write fails, these keep the count until the process ends.
        self.day = ""
        self.counts: dict[str, int] = {}

    def hit(self, address: str) -> GradeLimited | None:
        """Count one grade. Return None when it is within both limits, else the full window and its retry-after."""
        with self.lock:
            now = self.clock().astimezone(self.tz)
            today = now.date().isoformat()
            counts = self._read(today)
            if self.day == today:
                # A failed write leaves the file behind the memory, so the larger count of the two stands.
                counts = {a: max(counts.get(a, 0), self.counts.get(a, 0)) for a in counts.keys() | self.counts.keys()}
            # The day comes first, so a full day says "tomorrow" and not "next minute".
            if counts.get(address, 0) >= self.per_day:
                return GradeLimited("day", seconds_to_midnight(now))
            retry_after = self.minute.hit(address)
            if retry_after is not None:
                return GradeLimited("minute", retry_after)
            counts[address] = counts.get(address, 0) + 1
            self.day, self.counts = today, counts
            try:
                self._write(today, counts)
            except OSError as error:
                # A full or read-only volume must not stop the grade. The count stays in memory for this process.
                logger.warning("The grade count file %s is not writable, so the count stays in memory: %s",
                               self.path, error)
            return None

    def _read(self, today: str) -> dict[str, int]:
        """The counts of today from the file. A missing, malformed, or older file starts at zero."""
        try:
            data = json.loads(self.path.read_text())
            if data.get("day") != today:
                return {}
            return {str(a): int(n) for a, n in data["counts"].items()}
        except FileNotFoundError:
            return {}
        except (OSError, ValueError, TypeError, AttributeError, KeyError):
            logger.warning("The grade count file %s is not readable, so the counts start at zero", self.path)
            return {}

    def _write(self, today: str, counts: dict[str, int]) -> None:
        """Write only today, so the file never grows past one day of addresses."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        body = json.dumps({"day": today, "counts": counts}, sort_keys=True).encode("utf-8")
        write_bytes_atomic(self.path, body)
