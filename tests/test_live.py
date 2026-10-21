"""
Tests for the live snapshot builder.
Every fetch is a fixture-backed callable, so no test calls the network or Claude.
"""
import os
import shutil
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from cornerstone.live import live_snapshot
from cornerstone.nflverse import DEPTH_CHARTS_URL, FFIDS_URL, SCHEDULES_URL, cache_path
from cornerstone.sleeper import load_raw

ET = ZoneInfo("America/New_York")
FETCHED = datetime(2026, 10, 21, 9, 30, tzinfo=ET)
DAY = 24 * 60 * 60


@pytest.fixture
def live_repo(tmp_path, fixture_history_root, fixture_nflverse_dir):
    """A repo with the week 6 history and a fresh nflverse cache."""
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    # A copy keeps the fixture time, so the cache is made fresh here.
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached)
    return tmp_path


@pytest.fixture
def sleeper(fixture_raw_dir):
    def fetch(league_id, players_cache):
        return load_raw(fixture_raw_dir), FETCHED
    return fetch


class ChartRecorder:
    def __init__(self, chart):
        self.chart = chart
        self.weeks = []

    def __call__(self, repo, season_start, week, lines):
        self.weeks.append((season_start, week))
        return self.chart


def _age(repo, url, seconds):
    path = cache_path(repo / "data" / "cache" / "nflverse", url, 2026)
    old = time.time() - seconds
    os.utime(path, (old, old))
    return path


def _no_network(url):
    raise AssertionError(f"network call to {url}")


def test_the_chart_week_is_the_window_week_of_the_latest_past_cutoff(live_repo, sleeper, chart_week6):
    chart = ChartRecorder(chart_week6)
    # The cutoff of week 7 is Tuesday 2026-10-20 08:00.
    after = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 8, 0, tzinfo=ET), fetch_sleeper=sleeper,
                          fetch_nflverse=_no_network, read_chart=chart)
    before = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 7, 59, tzinfo=ET), fetch_sleeper=sleeper,
                           fetch_nflverse=_no_network, read_chart=chart)
    assert [week for _, week in chart.weeks] == [7, 6]
    assert after.as_of.chart_week == chart_week6.week
    assert before.chart == chart_week6


def test_the_stamps_hold_the_stats_through_week_and_the_rosters_fetch_time(live_repo, sleeper, chart_week6):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_nflverse=_no_network, read_chart=ChartRecorder(chart_week6))
    assert snap.as_of.chart_week == 6
    assert snap.as_of.stats_through == 6
    assert snap.as_of.rosters_fetched == FETCHED
    assert snap.season == 2026
    assert "7569" in snap.rosters[4]
    assert snap.schedules is not None and snap.depth_charts is not None and snap.points_allowed is not None
    assert snap.stale == []
    assert snap.usage is None and snap.injuries is None


def test_a_source_older_than_a_day_refreshes_before_the_snapshot(live_repo, sleeper, fixture_nflverse_dir):
    path = _age(live_repo, SCHEDULES_URL, 2 * DAY)
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / path.name).read_bytes()

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None))
    assert asked == [SCHEDULES_URL]
    assert time.time() - path.stat().st_mtime < DAY
    assert snap.stale == []
    assert "chart" in snap.missing


def test_a_failed_refresh_keeps_the_old_cache_and_notes_it(live_repo, sleeper):
    path = _age(live_repo, DEPTH_CHARTS_URL, 2 * DAY)
    before = path.read_bytes()

    def fetch(url):
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None))
    assert path.read_bytes() == before
    assert snap.stale == ["depth charts"]
    assert snap.depth_charts is not None


def test_a_source_with_no_cache_and_a_failed_fetch_is_missing_and_noted(live_repo, sleeper):
    cache_path(live_repo / "data" / "cache" / "nflverse", FFIDS_URL, 2026).unlink()

    def fetch(url):
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None))
    assert snap.stale == ["id map"]
    assert "id_map" in snap.missing


def test_a_season_that_is_not_in_progress_stops_the_build(live_repo, sleeper):
    with pytest.raises(ValueError, match="2025"):
        live_snapshot(live_repo, 2025, now=datetime(2026, 10, 19, tzinfo=ET), fetch_sleeper=sleeper,
                      fetch_nflverse=_no_network, read_chart=ChartRecorder(None))
