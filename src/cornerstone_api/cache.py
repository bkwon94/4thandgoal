"""
The result cache of the analyze route: one JSON file per proposed trade and data as-of stamps.
A repeat of the same trade on the same data reads the file and makes no Claude call.
"""
import hashlib
import json
from pathlib import Path

from cornerstone.rubric import ProposedTrade
from cornerstone.snapshot import AsOf


def cache_key(trade: ProposedTrade, as_of: AsOf) -> str:
    """The hash of the trade and the stamps of the data it was graded on.

    The rosters fetch time changes on every request, so the key rounds it down to the hour.
    Without the rounding no repeat would ever hit. A roster change inside the hour is the cost of that.
    """
    fetched = as_of.rosters_fetched
    parts = {
        "season": trade.season,
        # The sides keep their order, because the document lists the sides in the order of the request.
        "sides": [[side.roster_id, sorted(side.gives)] for side in trade.sides],
        "asker": trade.asker,
        "chart_week": as_of.chart_week,
        "stats_through": as_of.stats_through,
        "rosters_hour": fetched.replace(minute=0, second=0, microsecond=0).isoformat() if fetched else None,
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
