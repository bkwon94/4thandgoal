"""
The fetchers and the clock that the live snapshot reads, held on the app state so a test swaps each one.
Every route group that grades or lists the league builds its snapshot here, so all groups read the same data.
"""
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from datetime import datetime
from pathlib import Path

from cornerstone.chart import chart_values, claude_reader
from cornerstone.config import LeagueConfig
from cornerstone.history import PastLegFetcher
from cornerstone.live import (
    ChartReader, RefreshResult, SleeperFetcher, fetch_current_week, fetch_live_week, live_rosters_snapshot,
    live_snapshot, refresh_sources,
)
from cornerstone.models import Week
from cornerstone.nflverse import CACHE_MAX_AGE_SECONDS, http_get
from cornerstone.provider.sleeper import SLEEPER
from cornerstone.snapshot import Snapshot
from cornerstone.writer import parse_call


@dataclass(frozen=True)
class Sources:
    """Each fetch of the live snapshot, with the real download as the default, and the clock of the request."""

    # The league the fetches read. The API entry builds it once.
    config: LeagueConfig
    # The trade window week depends on the time of the request, so the clock is a source too.
    # It has no default, because the clock reads the league timezone. The API entry gives it with the config.
    clock: Callable[[], datetime]
    fetch_sleeper: SleeperFetcher = SLEEPER.fetch_live
    fetch_nflverse: Callable[[str], bytes] = http_get
    fetch_history_week: PastLegFetcher = SLEEPER.fetch_past_leg
    read_chart: ChartReader = partial(chart_values, read=claude_reader(parse_call))

    def snapshot(self, repo: Path, season: int) -> Snapshot:
        """The live snapshot of the league now. It raises ValueError when Sleeper is not in `season`."""
        return live_snapshot(
            repo, season, config=self.config, now=self.clock(),
            fetch_sleeper=self.fetch_sleeper, fetch_nflverse=self.fetch_nflverse,
            fetch_history_week=self.fetch_history_week, read_chart=self.read_chart,
        )

    def rosters_snapshot(self, repo: Path, season: int) -> Snapshot:
        """The live snapshot for the rosters only, with no chart. It raises ValueError as snapshot does.

        It fetches only Sleeper and reads the slow sources from the disk as they are.
        """
        return live_rosters_snapshot(
            repo, season, config=self.config, now=self.clock(), fetch_sleeper=self.fetch_sleeper)

    def refresh(self, repo: Path, season: int, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh the slow sources and the chart now, as the live snapshot does. It raises ValueError as snapshot does.

        Each nflverse file older than `max_age_seconds` is fetched again.
        The injuries file and the player weeks file are fetched again after at most 6 hours.
        """
        _, _, week = fetch_live_week(repo, season, self.config, self.fetch_sleeper)
        return self._refresh_week(repo, week, max_age_seconds)

    def refresh_current_season(self, repo: Path, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh as `refresh` does, for the season that Sleeper is in now.

        The start-up refresh calls it, because no request gives a season then. It fetches Sleeper once.
        """
        _, _, week = fetch_current_week(repo, self.config, self.fetch_sleeper)
        return self._refresh_week(repo, week, max_age_seconds)

    def _refresh_week(self, repo: Path, week: Week, max_age_seconds: int) -> RefreshResult:
        return refresh_sources(
            repo, week.season, self.clock(), week, config=self.config,
            fetch_nflverse=self.fetch_nflverse, fetch_history_week=self.fetch_history_week,
            read_chart=self.read_chart, max_age_seconds=max_age_seconds,
        )
