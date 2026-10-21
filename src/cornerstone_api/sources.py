"""
The fetchers and the clock that the live snapshot reads, held on the app state so a test swaps each one.
Every route group that grades or lists the league builds its snapshot here, so all groups read the same data.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from cornerstone.chart import chart_values
from cornerstone.live import (
    ChartReader, RefreshResult, SleeperFetcher, fetch_live_week, live_snapshot, refresh_sources,
)
from cornerstone.nflverse import CACHE_MAX_AGE_SECONDS, http_get
from cornerstone.sleeper import fetch_live_raw, fetch_past_week
from cornerstone.snapshot import Snapshot
from cornerstone.trades import EASTERN


def _now() -> datetime:
    return datetime.now(EASTERN)


@dataclass(frozen=True)
class Sources:
    """Each fetch of the live snapshot, with the real download as the default, and the clock of the request."""

    fetch_sleeper: SleeperFetcher = fetch_live_raw
    fetch_nflverse: Callable[[str], bytes] = http_get
    fetch_history_week: Callable[[str, int, int, Path], None] = fetch_past_week
    read_chart: ChartReader = chart_values
    # The trade window week depends on the time of the request, so the clock is a source too.
    clock: Callable[[], datetime] = field(default=_now)

    def snapshot(self, repo: Path, season: int, *, with_chart: bool = True) -> Snapshot:
        """The live snapshot of the league now. It raises ValueError when Sleeper is not in `season`.

        With `with_chart` False, the snapshot skips the chart read and has no chart.
        """
        return live_snapshot(
            repo, season, now=self.clock(),
            fetch_sleeper=self.fetch_sleeper, fetch_nflverse=self.fetch_nflverse,
            fetch_history_week=self.fetch_history_week, read_chart=self.read_chart if with_chart else None,
        )

    def refresh(self, repo: Path, season: int, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh the slow sources and the chart now, as the live snapshot does. It raises ValueError as snapshot does.

        Each nflverse file older than `max_age_seconds` is fetched again.
        """
        _, _, week = fetch_live_week(repo, season, self.fetch_sleeper)
        return refresh_sources(
            repo, season, self.clock(), week,
            fetch_nflverse=self.fetch_nflverse, fetch_history_week=self.fetch_history_week,
            read_chart=self.read_chart, max_age_seconds=max_age_seconds,
        )
