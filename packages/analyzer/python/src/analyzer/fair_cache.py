"""
The fair cache of the API process: the fair Noul answer of each Value offer in each side order (decision 19).
The fair question reads only the players of each side, so one answer serves a press of either team and the warm-up.
"""
import json
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Literal

from analyzer.trade import ProposedTrade, TradeSide
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# The key of one fair answer: the client, the season, the chart week, and the player ids of each side in the side order.
FairKey = tuple[str, int, int | None, tuple[str, ...], tuple[str, ...]]
# The side order of a fair question: "asker" names the first side of the trade first, and "partner" the second side.
SideOrder = Literal["asker", "partner"]


def ordered_sides(trade: ProposedTrade, order: SideOrder) -> list[TradeSide]:
    """The sides of the trade in the side order: the first side of the trade first, or the second side first."""
    return list(trade.sides) if order == "asker" else list(reversed(trade.sides))


def fair_key(snapshot: Snapshot, trade: ProposedTrade, order: SideOrder) -> FairKey:
    """The key of the fair answer of the trade in the side order: "asker" names the first side of the trade first, and
    "partner" names the second side first.

    The process serves more than one client, and a team name of one league is not in another, so the key holds the
    client. A new chart week or a moved player gives a new key, so no answer of old values is read.
    """
    first, second = (tuple(sorted(side.player_ids)) for side in ordered_sides(trade, order))
    return snapshot.client.slug, snapshot.season, snapshot.as_of.chart_week, first, second


class FairCache:
    """The fair answers by key, in memory. A press and the warm-up read and write it from their own threads.

    With a `folder`, each client keeps its answers in `<folder>/<slug>.json`. The cache loads each file at start, so an
    API start does not pay Jev again for answers it already got. On Fly the folder sits on the volume.
    """

    def __init__(self, folder: Path | None = None) -> None:
        self._answers: dict[FairKey, float] = {}
        self._lock = threading.Lock()
        self._folder = folder
        # The count of answers that each client's file held at start, for the warm-up log.
        self._loaded: dict[str, int] = {}
        # One save at a time per cache, so two saves never share a temp file name or race the rename.
        self._save_lock = threading.Lock()
        if folder is not None and folder.is_dir():
            for path in sorted(folder.glob("*.json")):
                self._load(path)

    def _load(self, path: Path) -> None:
        """Read one client file. A broken file is no error: log one line and keep the cache empty for that client."""
        slug = path.stem
        try:
            rows = json.loads(path.read_text())
            answers = {(slug, season, week, tuple(first), tuple(second)): float(answer)
                       for season, week, first, second, answer in rows}
        except (OSError, ValueError, TypeError):
            log.warning("The fair cache file of %s is missing, empty, or broken, so it starts empty", slug)
            return
        with self._lock:
            self._answers.update(answers)
        self._loaded[slug] = len(answers)
        log.info("The fair cache loaded %d answers of %s from its file", len(answers), slug)

    def loaded(self, slug: str) -> int:
        """The count of answers of the client that its file held at start."""
        return self._loaded.get(slug, 0)

    def save(self, slug: str) -> None:
        """Write the answers of the client to its file. A temp file in the same folder takes the write and a rename puts
        it in place, so a crash never leaves half a file. The cache lock covers only the copy of the answers, never the
        disk work, so a press never waits on the disk. A failed write logs one line and the old file stays."""
        if self._folder is None:
            return
        with self._lock:
            rows = [[*key[1:3], list(key[3]), list(key[4]), answer] for key, answer in self._answers.items()
                    if key[0] == slug]
        with self._save_lock:
            temp = None
            try:
                self._folder.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile("w", dir=self._folder, prefix=f".{slug}.", suffix=".tmp",
                                                 delete=False) as handle:
                    temp = Path(handle.name)
                    json.dump(rows, handle)
                os.replace(temp, self._folder / f"{slug}.json")
            except OSError as error:
                log.warning("The fair cache file of %s did not save (%s)", slug, type(error).__name__)
                if temp is not None:
                    temp.unlink(missing_ok=True)

    def get(self, key: FairKey) -> float | None:
        with self._lock:
            return self._answers.get(key)

    def put(self, key: FairKey, answer: float) -> None:
        with self._lock:
            self._answers[key] = answer

    def __contains__(self, key: FairKey) -> bool:
        with self._lock:
            return key in self._answers

    def __len__(self) -> int:
        with self._lock:
            return len(self._answers)

    def keep_week(self, slug: str, season: int, chart_week: int | None) -> None:
        """Drop each answer of the client from another season or chart week. No press reads an old week again."""
        with self._lock:
            self._answers = {key: p for key, p in self._answers.items()
                             if key[0] != slug or key[1:3] == (season, chart_week)}
