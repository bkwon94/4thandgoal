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
    ChartReader, RefreshResult, SleeperFetcher, fetch_current_week, fetch_live_week, live_rosters_snapshot,
    live_snapshot, refresh_sources,
)
from cornerstone.models import Week
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

    def snapshot(self, repo: Path, season: int) -> Snapshot:
        """The live snapshot of the league now. It raises ValueError when Sleeper is not in `season`."""
        return live_snapshot(
            repo, season, now=self.clock(),
            fetch_sleeper=self.fetch_sleeper, fetch_nflverse=self.fetch_nflverse,
            fetch_history_week=self.fetch_history_week, read_chart=self.read_chart,
        )

    def rosters_snapshot(self, repo: Path, season: int) -> Snapshot:
        """The live snapshot for the rosters only, with no chart. It raises ValueError as snapshot does.

        It fetches only Sleeper and reads the slow sources from the disk as they are.
        """
        return live_rosters_snapshot(repo, season, now=self.clock(), fetch_sleeper=self.fetch_sleeper)

    def refresh(self, repo: Path, season: int, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh the slow sources and the chart now, as the live snapshot does. It raises ValueError as snapshot does.

        Each nflverse file older than `max_age_seconds` is fetched again.
        """
        _, _, week = fetch_live_week(repo, season, self.fetch_sleeper)
        return self._refresh_week(repo, week, max_age_seconds)

    def refresh_current_season(self, repo: Path, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh as `refresh` does, for the season that Sleeper is in now.

        The start-up refresh calls it, because no request gives a season then. It fetches Sleeper once.
        """
        _, _, week = fetch_current_week(repo, self.fetch_sleeper)
        return self._refresh_week(repo, week, max_age_seconds)

    def _refresh_week(self, repo: Path, week: Week, max_age_seconds: int) -> RefreshResult:
        return refresh_sources(
            repo, week.season, self.clock(), week,
            fetch_nflverse=self.fetch_nflverse, fetch_history_week=self.fetch_history_week,
            read_chart=self.read_chart, max_age_seconds=max_age_seconds,
        )
