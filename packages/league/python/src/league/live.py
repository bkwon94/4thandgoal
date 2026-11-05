"""
Builds the snapshot of the league as it is now, for the trade analyzer.
It fetches Sleeper at request time, refreshes the slow sources that are a day old, and writes no weekly raw file.
On the Tuesday after the cutoff, it saves the week before the trade week into the history.
"""
import logging
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

import httpx

from league.client import Client
from league.history import PastLegFetcher, fetch_history, save_raw_to_history
from league.models import ChartValues, PlayerLine, Week, week_lines
from league.nflverse import (
    CACHE_MAX_AGE_SECONDS,
    DEPTH_CHARTS_URL,
    FFIDS_URL,
    FFOPPORTUNITY_URL,
    INJURIES_URL,
    SCHEDULES_URL,
    STATS_PLAYER_URL,
    cache_path,
    download,
    http_get,
    is_fresh,
)
from league.parse import parse_week
from league.paths import history_root, history_week_dir, nflverse_cache_dir, returns_path
from league.provider.raw import RawAheadWeek, RawWeek
from league.provider.sleeper import fetch_past_week, fetch_projections_ahead
from league.slow_sources import load_slow_sources
from league.snapshot import Snapshot, build_snapshot, load_out_for_season, load_returns, saved_chart_before
from league.trades import default_cutoff
from league.tunables import FAST_SOURCES_MAX_AGE_SECONDS, TEAMS_CACHE_SECONDS

logger = logging.getLogger(__name__)

# The Sleeper fetch takes the league id. It gives the raw data and the fetch time. The adapter holds its cache dir.
# It has the shape of Provider.fetch_live. Each fetcher here stays a callable, so a test fakes one fetch, not five.
SleeperFetcher = Callable[[str], tuple[RawWeek, datetime]]
class ChartReader(Protocol):
    """The chart read: the NFL data folder, the season start, the chart week, the player lines, and the chart of the
    client, the package value `chart` of league."""

    def __call__(self, nfl: Path, season_start: date, week: int, lines: Iterable[PlayerLine], *,
                 chart: str) -> ChartValues | None: ...


# The projections fetch takes the season, the raw week, the last regular week, and the points key. It gives the
# projections ahead of that week. It has the shape of Provider.fetch_projections.
ProjectionsFetcher = Callable[[int, int, int, str], list[RawAheadWeek]]

# The nflverse sources that the grade reads now, with the plain name the snapshot gives each one.
# The injuries file, the expected points file, and the weekly player file are here because on Fly no weekly build
# downloads them.
REFRESHED_SOURCES = (
    ("schedules", SCHEDULES_URL), ("depth charts", DEPTH_CHARTS_URL), ("id map", FFIDS_URL),
    ("injuries", INJURIES_URL), ("expected points", FFOPPORTUNITY_URL), ("player weeks", STATS_PLAYER_URL),
)
# The fast sources change on game days, so they refresh sooner than the others.
FAST_SOURCES = ("injuries", "player weeks")
# The last week of the NFL regular season. No trade window opens after its cutoff.
LAST_REGULAR_SEASON_WEEK = 18


def window_week(season_start: date, now: datetime, tz: ZoneInfo) -> int:
    """The trade window week whose cutoff is the latest cutoff at or before `now`. Before week 1 it is week 1.

    The cutoffs fall in the league timezone `tz`.
    """
    started = [week for week in range(1, LAST_REGULAR_SEASON_WEEK + 1)
               if default_cutoff(season_start, week, tz) <= now]
    return max(started, default=1)


def _mtime(path: Path) -> float | None:
    return path.stat().st_mtime if path.exists() else None


def _refresh(
        cache_dir: Path, season: int, fetch: Callable[[str], bytes],
        max_age_seconds: int) -> tuple[list[str], list[str]]:
    """Refresh each source whose cache is older than its max age.

    A fast source uses the smaller of `max_age_seconds` and its own age, so a forced refresh of 0 fetches all.

    Return the names refreshed and the names still older than a day.
    """
    refreshed, stale = [], []
    for name, url in REFRESHED_SOURCES:
        path = cache_path(cache_dir, url, season)
        # A changed time on the file shows a fetch that wrote it. A failed fetch leaves the time as it was.
        before = _mtime(path)
        # download keeps a fresh file, and on a failure it keeps the stale one, so the old cache stays in place.
        source_max_age = max_age_seconds
        if name in FAST_SOURCES:
            source_max_age = min(max_age_seconds, FAST_SOURCES_MAX_AGE_SECONDS)
        kept = download(url.format(season=season), path, max_age_seconds=source_max_age, fetch=fetch)
        # The age is of the file on disk, so it uses the clock of the disk and not the `now` of the request.
        # Stale always means older than a day, so a forced refresh that fails on a newer file is not stale.
        if kept is None or not is_fresh(path):
            stale.append(name)
        elif _mtime(path) != before:
            refreshed.append(name)
    return refreshed, stale


def _read_chart(
        read_chart: ChartReader, nfl: Path, season_start: date, week: int,
        lines: Iterable[PlayerLine], chart: str) -> tuple[ChartValues | None, bool]:
    """The chart of `week`, and True when the read raised.

    The Anthropic client raises TypeError with no API key, so any error must not stop the service.
    The log names only the error type, so it never holds the key or the prompt.
    """
    try:
        return read_chart(nfl, season_start, week, lines, chart=chart), False
    except Exception as error:  # noqa: BLE001 - the docstring says why: no error may stop the service
        logger.warning("Chart read for week %d failed (%s), so the week has no chart", week, type(error).__name__)
        return None, True


class ProjectionsCache:
    """The projections ahead per season and raw week, with the monotonic time of the fetch.

    The fetch is one Sleeper call per week ahead and takes seconds, so a repeat grade in the window pays nothing.
    One lock covers the check and the fetch, so two first requests make one fetch and not two.
    """

    def __init__(self, max_age_seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.max_age_seconds = max_age_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._entries: dict[tuple[int, int], tuple[float, list[RawAheadWeek]]] = {}

    def get_or_fetch(
            self, season: int, week: int, last_regular_week: int, points_key: str,
            fetch: ProjectionsFetcher) -> list[RawAheadWeek]:
        """The projections ahead of `week` through `last_regular_week`, at `points_key`, from memory within the window.

        Past it, `fetch` runs and the cache keeps its answer. One process serves one league, so the key needs no
        last week.
        """
        with self._lock:
            entry = self._entries.get((season, week))
            if entry is not None and self.clock() - entry[0] < self.max_age_seconds:
                return entry[1]
            ahead = fetch(season, week, last_regular_week, points_key)
            self._entries[(season, week)] = (self.clock(), ahead)
            return ahead


# The projections change at most a few times a day, so the window of the teams answer is short enough.
PROJECTIONS_CACHE = ProjectionsCache(TEAMS_CACHE_SECONDS)


@dataclass(frozen=True)
class RefreshResult:
    """What one refresh of the slow sources did, and the chart of the trade window that it read."""

    # The sources that the run fetched again, and the history weeks that it saved.
    refreshed: list[str]
    # The sources that are still older than a day, the history when its fetch failed, or the chart when its read raised.
    stale: list[str]
    trade_week: int
    # None when the trade window week has no good chart, or when the run skipped the chart.
    chart: ChartValues | None


def fetch_current_week(
        client: Client, fetch_sleeper: SleeperFetcher) -> tuple[RawWeek, datetime, Week]:
    """The raw Sleeper data now, its fetch time in the league timezone, and its parsed week.

    The data is of the season that Sleeper is in.
    """
    raw, fetched = fetch_sleeper(client.current_league_id)
    return raw, fetched.astimezone(client.tz), parse_week(raw, team_count=client.settings.team_count,
                                                          points_key=client.settings.points_key)


def fetch_live_week(
        season: int, client: Client,
        fetch_sleeper: SleeperFetcher) -> tuple[RawWeek, datetime, Week]:
    """The raw Sleeper data now, its fetch time, and its parsed week.

    Raises ValueError when Sleeper is not in `season`, because the cache and the history are per season.
    """
    raw, fetched, week = fetch_current_week(client, fetch_sleeper)
    if week.season != season:
        raise ValueError(f"Sleeper is in season {week.season}, not {season}. Use --week to read a saved week.")
    return raw, fetched, week


def refresh_sources(
        season: int, now: datetime, week: Week, *,
        client: Client,
        fetch_nflverse: Callable[[str], bytes] = http_get,
        fetch_history_week: PastLegFetcher = fetch_past_week,
        read_chart: ChartReader | None,
        max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
    """Refresh the nflverse sources older than their max age, the history weeks not yet saved, and the trade chart.

    The live snapshot and the refresh route both call it, so the daily job and a request refresh the same way.
    A failed fetch logs and leaves the old cache in place.
    The refresh route sets `max_age_seconds` to 0, because a late cron must still fetch a file 23 hours old.
    `read_chart` has no default, because the Claude read sits above this layer. With `read_chart` None, the run
    skips the chart. A client with no chart skips it too: the default of league is no chart, so each chart value is 0.
    """
    # The trade week is the chart week of the trade window, not Sleeper's display_week.
    # On a Monday night they match. On the Tuesday after the cutoff, Sleeper still shows the week before.
    trade_week = window_week(week.season_start, now, client.tz)
    refreshed, stale = _refresh(nflverse_cache_dir(client.nfl_dir), season, fetch_nflverse, max_age_seconds)
    # Past weeks never change, so the fetch gets only a week that is not saved.
    # A failure leaves a gap that the facts skip.
    # The inputs end at the week before the trade week. The raw data of this run gives its own week, so no fetch does.
    try:
        saved = fetch_history(client.league_id(season), season, min(trade_week, week.week) - 1,
                              history_root(client.folder, season), fetch=fetch_history_week)
        refreshed.extend(f"history week {saved_week}" for saved_week in saved)
    except httpx.HTTPError as error:
        logger.warning("History refresh failed (%s), so the saved weeks stand", error)
        stale.append("history")
    # The chart is the one of the trade window, which can be a week ahead of the last scored week.
    # The chart read caches its result per week, so a refresh before the first request saves that request the read.
    chart = None
    if read_chart is not None and client.chart is not None:
        chart, failed = _read_chart(read_chart, client.nfl_dir, week.season_start, trade_week, week_lines(week),
                                    client.chart)
        if failed:
            stale.append("chart")
    return RefreshResult(refreshed=refreshed, stale=stale, trade_week=trade_week, chart=chart)


def _build_live(
        season: int, raw: RawWeek, fetched: datetime, trade_week: int,
        chart: ChartValues | None, stale: list[str], now: datetime, client: Client) -> Snapshot:
    """The snapshot of the raw Sleeper data, with the slow sources and the returns read from the disk.

    `now` is the clock of the request, so the snapshot can tell the known games in progress.
    With no chart of the trade week, the superstar check reads the newest saved chart read of the weeks before.
    """
    root = history_root(client.folder, season)
    slow = load_slow_sources(nflverse_cache_dir(client.nfl_dir), season, trade_week, root, raw.league.scoring_settings,
                             client.settings.points_key)
    returns = load_returns(returns_path(client.nfl_dir, season))
    out_for_season = load_out_for_season(returns_path(client.nfl_dir, season))
    before = saved_chart_before(client, trade_week, raw, chart)
    return build_snapshot(raw, root, chart, slow, fetched, stale, trade_week=trade_week, returns=returns, now=now,
                          out_for_season=out_for_season, client=client, chart_before=before)


def live_snapshot(
        season: int, *, client: Client, now: datetime,
        fetch_sleeper: SleeperFetcher,
        fetch_nflverse: Callable[[str], bytes] = http_get,
        fetch_history_week: PastLegFetcher = fetch_past_week,
        read_chart: ChartReader | None,
        fetch_projections: ProjectionsFetcher = fetch_projections_ahead,
        projections: ProjectionsCache = PROJECTIONS_CACHE) -> Snapshot:
    """The snapshot of the league now. Every fetch is a callable, with the real download as the default.

    `fetch_sleeper` has no default, because the Sleeper adapter takes the cache dir of the run in its constructor.

    `read_chart` has no default, because the Claude read sits above this layer. The CLI and the API pass it.
    With `read_chart` None, the snapshot has no chart, and the chart is not noted as stale.
    The projections ahead come through `projections`, so a repeat grade in its window fetches none.

    Raises ValueError when Sleeper is not in `season`, because the cache and the history are per season.
    """
    raw, fetched, week = fetch_live_week(season, client, fetch_sleeper)
    result = refresh_sources(season, now, week, client=client, fetch_nflverse=fetch_nflverse,
                              fetch_history_week=fetch_history_week, read_chart=read_chart)
    trade_week = result.trade_week
    stale = list(result.stale)
    root = history_root(client.folder, season)
    # On the Tuesday after the cutoff, Sleeper still shows week N-1, and only this raw data holds it.
    # The points allowed read the history on disk, so week N-1 goes there before the slow sources load.
    # The weekly build saves the same week later and overwrites these files with the same data.
    # A Sleeper outage gives empty stats, so an empty week is not saved over a good saved copy.
    # A failed write must not stop the request, so the snapshot builds and notes the history as stale.
    if week.week == trade_week - 1 and raw.stats:
        try:
            save_raw_to_history(raw, history_week_dir(root, week.week))
        except OSError as error:
            logger.warning("Week %d not saved to history (%s), so the saved weeks stand", week.week, error)
            if "history" not in stale:
                stale.append("history")
    # Only the grade reads the projections ahead, so this route fetches them and the rosters route does not.
    # A fetcher that gives them already, as a saved week's raw data does, needs no fetch here.
    if raw.projections_ahead is None:
        ahead = projections.get_or_fetch(season, week.week, client.settings.last_regular_week,
                                         client.settings.points_key, fetch_projections)
        raw = raw.model_copy(update={"projections_ahead": ahead})
    return _build_live(season, raw, fetched, trade_week, result.chart, stale, now, client)


def live_rosters_snapshot(
        season: int, *, client: Client, now: datetime,
        fetch_sleeper: SleeperFetcher) -> Snapshot:
    """The snapshot of the league now for the rosters only. The teams route reads it.

    It fetches only Sleeper. It reads the slow sources and the history from the disk as they are. It refreshes
    no source, saves no history week, and reads no chart, so it never waits on a download.

    Raises ValueError when Sleeper is not in `season`, as live_snapshot does.
    """
    raw, fetched, week = fetch_live_week(season, client, fetch_sleeper)
    # No refresh ran, so no source goes in the stale list here. The build still notes a gap in the saved history.
    return _build_live(season, raw, fetched, window_week(week.season_start, now, client.tz), None, [],
                       now, client)
