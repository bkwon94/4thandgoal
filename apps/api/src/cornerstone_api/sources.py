"""
The fetchers and the clock that the live snapshot reads, held on the app state so a test swaps each one.
Every route group that grades or lists the league builds its snapshot here, so all groups read the same data.
"""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from functools import partial

from facts.writer import parse_call
from league.chart import chart_values, claude_reader
from league.client import Client
from league.history import PastLegFetcher
from league.live import (
    ChartReader,
    RefreshResult,
    SleeperFetcher,
    fetch_current_week,
    fetch_live_week,
    live_rosters_snapshot,
    live_snapshot,
    refresh_sources,
)
from league.models import Week
from league.nflverse import CACHE_MAX_AGE_SECONDS, http_get
from league.provider.sleeper import fetch_past_week
from league.snapshot import Snapshot


@dataclass(frozen=True)
class Sources:
    """Each fetch of the live snapshot, with the real download as the default, and the clock of the request."""

    # The league the fetches read. The API entry builds it once.
    client: Client
    # The trade window week depends on the time of the request, so the clock is a source too.
    # It has no default, because the clock reads the league timezone. The API entry gives it with the client.
    clock: Callable[[], datetime]
    # The Sleeper adapter takes the cache dir of the run in its constructor, so the API entry gives the fetch.
    fetch_sleeper: SleeperFetcher
    fetch_nflverse: Callable[[str], bytes] = http_get
    fetch_history_week: PastLegFetcher = fetch_past_week
    # The download of the past season files. None skips it, so a test of another source makes no call.
    fetch_past: Callable[[str], bytes] | None = None
    # One shared partial is safe as the default, because it holds no state that a call changes.
    read_chart: ChartReader = partial(chart_values, read=claude_reader(parse_call))  # noqa: RUF009

    def snapshot(self, season: int) -> Snapshot:
        """The live snapshot of the league now. It raises ValueError when Sleeper is not in `season`."""
        return live_snapshot(
            season, client=self.client, now=self.clock(),
            fetch_sleeper=self.fetch_sleeper, fetch_nflverse=self.fetch_nflverse,
            fetch_history_week=self.fetch_history_week, read_chart=self.read_chart,
            fetch_past=self.fetch_past,
        )

    def rosters_snapshot(self, season: int) -> Snapshot:
        """The live snapshot for the rosters only, with no chart. It raises ValueError as snapshot does.

        It fetches only Sleeper and reads the slow sources from the disk as they are.
        """
        return live_rosters_snapshot(
            season, client=self.client, now=self.clock(), fetch_sleeper=self.fetch_sleeper)

    def refresh(self, season: int, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh the slow sources and the chart now, as the live snapshot does. It raises ValueError as snapshot does.

        Each nflverse file older than `max_age_seconds` is fetched again.
        The injuries file and the player weeks file are fetched again after at most 6 hours.
        """
        _, _, week = fetch_live_week(season, self.client, self.fetch_sleeper)
        return self._refresh_week(week, max_age_seconds)

    def refresh_current_season(self, *, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
        """Refresh as `refresh` does, for the season that Sleeper is in now.

        The start-up refresh calls it, because no request gives a season then. It fetches Sleeper once.
        """
        _, _, week = fetch_current_week(self.client, self.fetch_sleeper)
        return self._refresh_week(week, max_age_seconds)

    def _refresh_week(self, week: Week, max_age_seconds: int) -> RefreshResult:
        return refresh_sources(
            week.season, self.clock(), week, client=self.client,
            fetch_nflverse=self.fetch_nflverse, fetch_history_week=self.fetch_history_week,
            read_chart=self.read_chart, fetch_past=self.fetch_past, max_age_seconds=max_age_seconds,
        )
