"""
The two caches of the API. The result cache of the analyze route keeps one JSON file per graded trade and data.
The teams cache keeps the teams answer per season in memory for a short window, so the trade form fills at once.
"""
import hashlib
import json
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from cornerstone.rubric import ProposedTrade
from cornerstone.snapshot import Snapshot


# The shape of the stored result document. A change of shape bumps it, so the key changes and a result stored on
# the volume in an old shape never serves again.
DOCUMENT_VERSION = 2


def cache_key(trade: ProposedTrade, snapshot: Snapshot) -> str:
    """The hash of the trade and the content of the snapshot that the grade reads.

    The key holds a hash of both rosters and of both records, not the fetch time. The fetch time changes on
    every request, so it would never hit. A roster change on Sleeper changes the hash, so a stale grade never serves.
    """
    as_of = snapshot.as_of
    roster_ids = [side.roster_id for side in trade.sides]
    standings = {standing.roster_id: standing for standing in snapshot.standings}
    content = {
        roster_id: {
            "players": sorted(snapshot.rosters[roster_id]),
            "record": standings[roster_id].model_dump(mode="json") if roster_id in standings else None,
        }
        for roster_id in roster_ids
    }
    parts = {
        "document_version": DOCUMENT_VERSION,
        "season": trade.season,
        # The sides keep their order, because the document lists the sides in the order of the request.
        "sides": [[side.roster_id, sorted(side.gives)] for side in trade.sides],
        "asker": trade.asker,
        "chart_week": as_of.chart_week,
        "stats_through": as_of.stats_through,
        "content": hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest(),
    }
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()


class ResultCache:
    """The result documents on disk, one file per key, under a directory on the data volume."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, document: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        # A write to a temporary file and a rename, so a crash never leaves half a document for a later hit.
        path = self._path(key)
        partial = path.with_suffix(".tmp")
        partial.write_text(json.dumps(document), encoding="utf-8")
        partial.replace(path)


class TeamsEntry(NamedTuple):
    """One teams answer and the monotonic time of its build."""

    built_at: float
    answer: dict


class TeamsCache:
    """The last teams answer per season, with the monotonic time of its build.

    One lock covers the check and the build, so two first requests make one build and not two.
    Only the teams route builds through it, so the refresh route and the analyze route never wait on a build.
    """

    def __init__(self, max_age_seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.max_age_seconds = max_age_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._entries: dict[int, TeamsEntry] = {}

    def get_or_build(self, season: int, build: Callable[[], dict]) -> dict:
        """The answer for `season` from memory within the window. Past it, `build` runs and the cache keeps its answer.

        A build that raises leaves the cache as it was, so the next request tries again.
        """
        with self._lock:
            entry = self._entries.get(season)
            if entry is not None and self.clock() - entry.built_at < self.max_age_seconds:
                return entry.answer
            answer = build()
            self._entries[season] = TeamsEntry(built_at=self.clock(), answer=answer)
            return answer

    def clear(self, season: int) -> None:
        """Drop the answer for `season`, so the next request builds again."""
        # A dict pop is atomic, so the analyze route clears with no wait on a build that holds the lock.
        self._entries.pop(season, None)
