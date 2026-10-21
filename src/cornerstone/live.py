"""
Builds the snapshot of the league as it is now, for the trade analyzer.
It fetches Sleeper at request time, refreshes the slow sources that are a day old, and writes no weekly raw file.
"""
import logging
import time
from collections.abc import Callable, Iterable
from datetime import date, datetime
from pathlib import Path

import httpx

from cornerstone.chart import chart_values
from cornerstone.history import fetch_history, history_root
from cornerstone.models import ChartValues, PlayerLine, week_lines
from cornerstone.nflverse import (
    CACHE_MAX_AGE_SECONDS, DEPTH_CHARTS_URL, FFIDS_URL, SCHEDULES_URL, cache_path, download, http_get,
)
from cornerstone.parse import parse_week
from cornerstone.pipeline import LEAGUE_ID, nflverse_cache_dir
from cornerstone.slow_sources import load_slow_sources
from cornerstone.sleeper import fetch_live_raw, fetch_past_week
from cornerstone.snapshot import Snapshot, build_snapshot
from cornerstone.trades import default_cutoff

logger = logging.getLogger(__name__)

# The Sleeper fetch takes the league id and the players cache file. It gives the raw data and the fetch time.
SleeperFetcher = Callable[[str, Path], tuple[dict[str, object], datetime]]
# The chart read takes the repo, the season start, the chart week, and the player lines.
ChartReader = Callable[[Path, date, int, Iterable[PlayerLine]], ChartValues | None]

# The nflverse sources that the grade reads now, with the plain name the snapshot gives each one.
REFRESHED_SOURCES = (
    ("schedules", SCHEDULES_URL), ("depth charts", DEPTH_CHARTS_URL), ("id map", FFIDS_URL),
)
LAST_WEEK = 18


def window_week(season_start: date, now: datetime) -> int:
    """The trade window week whose cutoff is the latest cutoff at or before `now`. Before week 1 it is week 1."""
    started = [week for week in range(1, LAST_WEEK + 1) if default_cutoff(season_start, week) <= now]
    return max(started, default=1)


def _refresh(
        cache_dir: Path, season: int, fetch: Callable[[str], bytes]) -> list[str]:
    """Refresh each source whose cache is older than a day. The names of those still not fresh are returned."""
    stale = []
    for name, url in REFRESHED_SOURCES:
        path = cache_path(cache_dir, url, season)
        # download keeps a fresh file, and on a failure it keeps the stale one, so the old cache stays in place.
        # The age is of the file on disk, so it uses the clock of the disk and not the `now` of the request.
        kept = download(url.format(season=season), path, fetch=fetch)
        if kept is None or time.time() - path.stat().st_mtime >= CACHE_MAX_AGE_SECONDS:
            stale.append(name)
    return stale


def live_snapshot(
        repo: Path, season: int, *, now: datetime,
        fetch_sleeper: SleeperFetcher = fetch_live_raw,
        fetch_nflverse: Callable[[str], bytes] = http_get,
        fetch_history_week: Callable[[str, int, int, Path], None] = fetch_past_week,
        read_chart: ChartReader = chart_values) -> Snapshot:
    """The snapshot of the league now. Every fetch is a callable, with the real download as the default.

    Raises ValueError when Sleeper is not in `season`, because the cache and the history are per season.
    """
    raw, fetched = fetch_sleeper(LEAGUE_ID, repo / "data" / "cache" / "players.json")
    state = raw["state"]
    if int(state["season"]) != season:
        raise ValueError(f"Sleeper is in season {state['season']}, not {season}. Use --week to read a saved week.")
    week = parse_week(raw)
    stale = _refresh(nflverse_cache_dir(repo), season, fetch_nflverse)
    root = history_root(repo, season)
    # Past weeks never change, so only a week that is not saved is fetched. A failure leaves a gap that the facts skip.
    try:
        fetch_history(LEAGUE_ID, season, week.week - 1, root, fetch=fetch_history_week)
    except httpx.HTTPError as error:
        logger.warning("History refresh failed (%s), so the saved weeks stand", error)
        stale.append("history")
    # The chart is the one of the trade window, which can be a week ahead of the last scored week.
    chart = read_chart(repo, week.season_start, window_week(week.season_start, now), week_lines(week))
    slow = load_slow_sources(nflverse_cache_dir(repo), season, week.week, root)
    return build_snapshot(raw, root, chart, slow, fetched, stale)
