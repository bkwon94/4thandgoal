"""
The fair cache of the API process: the fair Noul answer of each Value offer in each side order (decision 19).
The fair question reads only the players of each side, so one answer serves a press of either team and the warm-up.
"""
import threading

from analyzer.trade import ProposedTrade
from league.snapshot import Snapshot

# The key of one fair answer: the client, the season, the chart week, and the player ids of each side in the side order.
FairKey = tuple[str, int, int | None, tuple[str, ...], tuple[str, ...]]


def fair_key(snapshot: Snapshot, trade: ProposedTrade, order: str) -> FairKey:
    """The key of the fair answer of the trade in the side order: "asker" names the first side of the trade first, and
    "partner" names the second side first.

    The process serves more than one client, and a team name of one league is not in another, so the key holds the
    client. A new chart week or a moved player gives a new key, so no answer of old values is read.
    """
    sides = list(trade.sides) if order == "asker" else list(reversed(trade.sides))
    first, second = (tuple(sorted(side.player_ids)) for side in sides)
    return snapshot.client.slug, snapshot.season, snapshot.as_of.chart_week, first, second


class FairCache:
    """The fair answers by key, in memory. A press and the warm-up read and write it from their own threads."""

    def __init__(self) -> None:
        self._answers: dict[FairKey, float] = {}
        self._lock = threading.Lock()

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
