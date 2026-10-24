"""
Builds the snapshot of the league as it is now, for the trade analyzer.
It fetches Sleeper at request time, refreshes the slow sources that are a day old, and writes no weekly raw file.
On the Tuesday after the cutoff, it saves the week before the trade week into the history.
"""
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import httpx

from cornerstone.chart import chart_values
from cornerstone.history import fetch_history, history_dir, history_root, returns_path, save_raw_to_history
from cornerstone.models import ChartValues, PlayerLine, Week, week_lines
from cornerstone.nflverse import (
    CACHE_MAX_AGE_SECONDS, DEPTH_CHARTS_URL, FFIDS_URL, INJURIES_URL, SCHEDULES_URL, cache_path, download, http_get,
    is_fresh,
)
from cornerstone.parse import parse_week
from cornerstone.pipeline import LEAGUE_ID, nflverse_cache_dir
from cornerstone.slow_sources import load_slow_sources
from cornerstone.sleeper import fetch_live_raw, fetch_past_week
from cornerstone.snapshot import Snapshot, build_snapshot, load_returns
from cornerstone.trades import default_cutoff

logger = logging.getLogger(__name__)

# The Sleeper fetch takes the league id and the players cache file. It gives the raw data and the fetch time.
SleeperFetcher = Callable[[str, Path], tuple[dict[str, object], datetime]]
# The chart read takes the repo, the season start, the chart week, and the player lines.
ChartReader = Callable[[Path, date, int, Iterable[PlayerLine]], ChartValues | None]

# The nflverse sources that the grade reads now, with the plain name the snapshot gives each one.
# The injuries file is here because on Fly no weekly build downloads it.
REFRESHED_SOURCES = (
    ("schedules", SCHEDULES_URL), ("depth charts", DEPTH_CHARTS_URL), ("id map", FFIDS_URL),
    ("injuries", INJURIES_URL),
)
# The last week of the NFL regular season. No trade window opens after its cutoff.
LAST_REGULAR_SEASON_WEEK = 18


def window_week(season_start: date, now: datetime) -> int:
    """The trade window week whose cutoff is the latest cutoff at or before `now`. Before week 1 it is week 1."""
    started = [week for week in range(1, LAST_REGULAR_SEASON_WEEK + 1) if default_cutoff(season_start, week) <= now]
    return max(started, default=1)


def _mtime(path: Path) -> float | None:
    return path.stat().st_mtime if path.exists() else None


def _refresh(
        cache_dir: Path, season: int, fetch: Callable[[str], bytes],
        max_age_seconds: int) -> tuple[list[str], list[str]]:
    """Refresh each source whose cache is older than `max_age_seconds`.

    Return the names refreshed and the names still older than a day.
    """
    refreshed, stale = [], []
    for name, url in REFRESHED_SOURCES:
        path = cache_path(cache_dir, url, season)
        # A changed time on the file shows a fetch that wrote it. A failed fetch leaves the time as it was.
        before = _mtime(path)
        # download keeps a fresh file, and on a failure it keeps the stale one, so the old cache stays in place.
        kept = download(url.format(season=season), path, max_age_seconds=max_age_seconds, fetch=fetch)
        # The age is of the file on disk, so it uses the clock of the disk and not the `now` of the request.
        # Stale always means older than a day, so a forced refresh that fails on a newer file is not stale.
        if kept is None or not is_fresh(path):
            stale.append(name)
        elif _mtime(path) != before:
            refreshed.append(name)
    return refreshed, stale


def _read_chart(
        read_chart: ChartReader, repo: Path, season_start: date, week: int,
        lines: Iterable[PlayerLine]) -> tuple[ChartValues | None, bool]:
    """The chart of `week`, and True when the read raised.

    The Anthropic client raises TypeError with no API key, so any error must not stop the service.
    The log names only the error type, so it never holds the key or the prompt.
    """
    try:
        return read_chart(repo, season_start, week, lines), False
    except Exception as error:
        logger.warning("Chart read for week %d failed (%s), so the week has no chart", week, type(error).__name__)
        return None, True


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


def fetch_current_week(repo: Path, fetch_sleeper: SleeperFetcher) -> tuple[dict[str, object], datetime, Week]:
    """The raw Sleeper data now, its fetch time, and its parsed week, in the season that Sleeper is in."""
    raw, fetched = fetch_sleeper(LEAGUE_ID, repo / "data" / "cache" / "players.json")
    return raw, fetched, parse_week(raw)


def fetch_live_week(
        repo: Path, season: int, fetch_sleeper: SleeperFetcher) -> tuple[dict[str, object], datetime, Week]:
    """The raw Sleeper data now, its fetch time, and its parsed week.

    Raises ValueError when Sleeper is not in `season`, because the cache and the history are per season.
    """
    raw, fetched, week = fetch_current_week(repo, fetch_sleeper)
    if week.season != season:
        raise ValueError(f"Sleeper is in season {week.season}, not {season}. Use --week to read a saved week.")
    return raw, fetched, week


def refresh_sources(
        repo: Path, season: int, now: datetime, week: Week, *,
        fetch_nflverse: Callable[[str], bytes] = http_get,
        fetch_history_week: Callable[[str, int, int, Path], None] = fetch_past_week,
        read_chart: ChartReader | None = chart_values,
        max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> RefreshResult:
    """Refresh the day-old nflverse sources, the history weeks not yet saved, and the chart of the trade window.

    The live snapshot and the refresh route both call it, so the daily job and a request refresh the same way.
    A failed fetch logs and leaves the old cache in place.
    The refresh route sets `max_age_seconds` to 0, because a late cron must still fetch a file 23 hours old.
    With `read_chart` None, the run skips the chart.
    """
    # The trade week is the chart week of the trade window, not Sleeper's display_week.
    # On a Monday night they match. On the Tuesday after the cutoff, Sleeper still shows the week before.
    trade_week = window_week(week.season_start, now)
    refreshed, stale = _refresh(nflverse_cache_dir(repo), season, fetch_nflverse, max_age_seconds)
    # Past weeks never change, so the fetch gets only a week that is not saved. A failure leaves a gap that the facts skip.
    # The inputs end at the week before the trade week. The raw data of this run gives its own week, so no fetch does.
    try:
        saved = fetch_history(LEAGUE_ID, season, min(trade_week, week.week) - 1, history_root(repo, season),
                              fetch=fetch_history_week)
        refreshed.extend(f"history week {saved_week}" for saved_week in saved)
    except httpx.HTTPError as error:
        logger.warning("History refresh failed (%s), so the saved weeks stand", error)
        stale.append("history")
    # The chart is the one of the trade window, which can be a week ahead of the last scored week.
    # The chart read caches its result per week, so a refresh before the first request saves that request the read.
    chart = None
    if read_chart is not None:
        chart, failed = _read_chart(read_chart, repo, week.season_start, trade_week, week_lines(week))
        if failed:
            stale.append("chart")
    return RefreshResult(refreshed=refreshed, stale=stale, trade_week=trade_week, chart=chart)


def _build_live(
        repo: Path, season: int, raw: dict[str, object], fetched: datetime, trade_week: int,
        chart: ChartValues | None, stale: list[str]) -> Snapshot:
    """The snapshot of the raw Sleeper data, with the slow sources and the returns read from the disk."""
    root = history_root(repo, season)
    slow = load_slow_sources(nflverse_cache_dir(repo), season, trade_week, root, raw["league"]["scoring_settings"])
    returns = load_returns(returns_path(repo, season))
    return build_snapshot(raw, root, chart, slow, fetched, stale, trade_week=trade_week, returns=returns)


def live_snapshot(
        repo: Path, season: int, *, now: datetime,
        fetch_sleeper: SleeperFetcher = fetch_live_raw,
        fetch_nflverse: Callable[[str], bytes] = http_get,
        fetch_history_week: Callable[[str, int, int, Path], None] = fetch_past_week,
        read_chart: ChartReader | None = chart_values) -> Snapshot:
    """The snapshot of the league now. Every fetch is a callable, with the real download as the default.

    With `read_chart` None, the snapshot has no chart, and the chart is not noted as stale.

    Raises ValueError when Sleeper is not in `season`, because the cache and the history are per season.
    """
    raw, fetched, week = fetch_live_week(repo, season, fetch_sleeper)
    result = refresh_sources(repo, season, now, week, fetch_nflverse=fetch_nflverse,
                              fetch_history_week=fetch_history_week, read_chart=read_chart)
    trade_week = result.trade_week
    stale = list(result.stale)
    root = history_root(repo, season)
    # On the Tuesday after the cutoff, Sleeper still shows week N-1, and only this raw data holds it.
    # The points allowed read the history on disk, so week N-1 goes there before the slow sources load.
    # The weekly build saves the same week later and overwrites these files with the same data.
    # A Sleeper outage gives empty stats, so an empty week is not saved over a good saved copy.
    # A failed write must not stop the request, so the snapshot builds and notes the history as stale.
    if week.week == trade_week - 1 and raw["stats"]:
        try:
            save_raw_to_history(raw, history_dir(root, week.week))
        except OSError as error:
            logger.warning("Week %d not saved to history (%s), so the saved weeks stand", week.week, error)
            if "history" not in stale:
                stale.append("history")
    return _build_live(repo, season, raw, fetched, trade_week, result.chart, stale)


def live_rosters_snapshot(
        repo: Path, season: int, *, now: datetime, fetch_sleeper: SleeperFetcher = fetch_live_raw) -> Snapshot:
    """The snapshot of the league now for the rosters only. The teams route reads it.

    It fetches only Sleeper. It reads the slow sources and the history from the disk as they are. It refreshes
    no source, saves no history week, and reads no chart, so it never waits on a download.

    Raises ValueError when Sleeper is not in `season`, as live_snapshot does.
    """
    raw, fetched, week = fetch_live_week(repo, season, fetch_sleeper)
    # No refresh ran, so no source goes in the stale list here. The build still notes a gap in the saved history.
    return _build_live(repo, season, raw, fetched, window_week(week.season_start, now), None, [])
