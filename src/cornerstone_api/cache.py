"""
The result cache of the analyze route: one JSON file per proposed trade and the data it was graded on.
A repeat of the same trade on the same data reads the file and makes no Claude call.
"""
import hashlib
import json
from pathlib import Path

from cornerstone.rubric import ProposedTrade
from cornerstone.snapshot import Snapshot


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
