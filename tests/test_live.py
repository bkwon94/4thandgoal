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

from cornerstone.history import save_week_to_history
from cornerstone.live import live_snapshot
from cornerstone.nflverse import DEPTH_CHARTS_URL, FFIDS_URL, INJURIES_URL, SCHEDULES_URL, cache_path
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


def _no_history_fetch(league_id, season, week, out_dir):
    raise AssertionError(f"network call for history week {week}")


def test_the_chart_week_is_the_window_week_of_the_latest_past_cutoff(live_repo, sleeper, chart_week6):
    chart = ChartRecorder(chart_week6)
    # The cutoff of week 7 is Tuesday 2026-10-20 08:00.
    after = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 8, 0, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                          fetch_nflverse=_no_network, read_chart=chart)
    before = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 7, 59, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                           fetch_nflverse=_no_network, read_chart=chart)
    assert [week for _, week in chart.weeks] == [7, 6]
    assert after.as_of.chart_week == chart_week6.week
    assert before.chart == chart_week6


def test_the_stamps_hold_the_stats_through_week_and_the_rosters_fetch_time(live_repo, sleeper, chart_week6):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=_no_network, read_chart=ChartRecorder(chart_week6))
    assert snap.as_of.chart_week == 6
    assert snap.as_of.rosters_fetched == FETCHED
    assert snap.season == 2026
    assert "7569" in snap.rosters[4]
    assert snap.schedules is not None and snap.depth_charts is not None and snap.points_allowed is not None
    assert snap.stale == []
    assert snap.injuries is not None


def test_a_source_older_than_a_day_refreshes_before_the_snapshot(live_repo, sleeper, fixture_nflverse_dir):
    path = _age(live_repo, SCHEDULES_URL, 2 * DAY)
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / path.name).read_bytes()

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
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

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None))
    assert path.read_bytes() == before
    assert snap.stale == ["depth charts"]
    assert snap.depth_charts is not None


def test_a_source_with_no_cache_and_a_failed_fetch_is_missing_and_noted(live_repo, sleeper):
    cache_path(live_repo / "data" / "cache" / "nflverse", FFIDS_URL, 2026).unlink()

    def fetch(url):
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None))
    assert snap.stale == ["id map"]
    assert "id_map" in snap.missing


def test_a_season_that_is_not_in_progress_stops_the_build(live_repo, sleeper):
    with pytest.raises(ValueError, match="2025"):
        live_snapshot(live_repo, 2025, now=datetime(2026, 10, 19, tzinfo=ET), fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                      fetch_nflverse=_no_network, read_chart=ChartRecorder(None))


def test_on_monday_night_the_raw_week_is_the_trade_week_and_stays_out_of_the_history(
        live_repo, sleeper, chart_week6):
    # Monday 2026-10-19 is before the week 7 cutoff, so the chart week is 6. Sleeper shows week 6 too.
    chart = ChartRecorder(chart_week6)
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 21, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network, read_chart=chart)
    assert [week for _, week in chart.weeks] == [6]
    assert snap.week == 6
    assert snap.as_of.stats_through == 5
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5]
    assert sum(s.wins + s.losses for s in snap.standings) == 5 * 2 * 12
    assert snap.stale == []


def test_on_the_tuesday_before_the_roll_the_raw_week_joins_the_history(live_repo, sleeper, chart_week6):
    # Tuesday 2026-10-20 09:00 is after the week 7 cutoff, so the chart week is 7. Sleeper still shows week 6.
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6))
    assert snap.week == 7
    assert snap.as_of.stats_through == 6
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5, 6]
    assert sum(s.wins + s.losses for s in snap.standings) == 6 * 2 * 12
    assert snap.stale == []


def test_a_failed_history_fetch_keeps_the_saved_weeks_and_notes_it(live_repo, sleeper, chart_week6):
    shutil.rmtree(live_repo / "data" / "2026" / "history" / "week-05")
    asked = []

    def fetch(league_id, season, week, out_dir):
        asked.append(week)
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 21, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=fetch, fetch_nflverse=_no_network, read_chart=ChartRecorder(chart_week6))
    assert asked == [5]
    assert snap.stale == ["history"]
    assert snap.as_of.stats_through == 4
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4]


def test_on_the_tuesday_before_the_roll_the_raw_week_is_saved_so_points_allowed_count_it(
        live_repo, sleeper, chart_week6):
    # The points allowed read weeks 1 to 6 from the history on disk, and only the raw data of this run holds week 6.
    saved = live_repo / "data" / "2026" / "history" / "week-06"
    assert not saved.exists()
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6))
    assert snap.points_allowed is not None
    assert "points_allowed" not in snap.missing
    assert (saved / "stats.json").exists()


def test_on_the_tuesday_an_empty_stats_raw_week_leaves_a_good_saved_week_untouched(
        live_repo, fixture_raw_dir, chart_week6):
    # A Sleeper outage gives an empty stats list. The saved copy of week 6 must stay as it is.
    saved = live_repo / "data" / "2026" / "history" / "week-06"
    save_week_to_history(fixture_raw_dir, saved)
    before = (saved / "stats.json").read_bytes()

    def outage(league_id, players_cache):
        raw = load_raw(fixture_raw_dir)
        raw["stats"] = []
        return raw, FETCHED

    live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=outage,
                  fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                  read_chart=ChartRecorder(chart_week6))
    assert (saved / "stats.json").read_bytes() == before


def test_on_the_tuesday_a_failed_history_write_marks_history_stale_and_the_snapshot_still_builds(
        live_repo, sleeper, chart_week6):
    # A file where the week 6 directory goes makes the write fail with an OSError.
    (live_repo / "data" / "2026" / "history" / "week-06").write_text("", encoding="utf-8")
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6))
    assert "history" in snap.stale
    assert snap.week == 7


def test_an_injuries_file_older_than_a_day_refreshes_before_the_snapshot(live_repo, sleeper, fixture_nflverse_dir):
    path = _age(live_repo, INJURIES_URL, 2 * DAY)
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / path.name).read_bytes()

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=fetch, read_chart=ChartRecorder(None))
    assert asked == [INJURIES_URL.format(season=2026)]
    assert time.time() - path.stat().st_mtime < DAY
    assert snap.stale == []


def test_the_live_path_keeps_a_file_one_hour_old(live_repo, sleeper, chart_week6):
    _age(live_repo, SCHEDULES_URL, 60 * 60)
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6))
    assert snap.stale == []


def test_no_chart_reader_skips_the_chart_and_notes_no_stale_chart(live_repo, sleeper):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network, read_chart=None)
    assert snap.chart is None
    assert "chart" not in snap.stale


def test_a_chart_read_that_raises_gives_no_chart_and_notes_it_stale(live_repo, sleeper):
    def read_chart(repo, season_start, week, lines):
        # The Anthropic client raises TypeError when the API key is absent.
        raise TypeError("no api key")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network, read_chart=read_chart)
    assert snap.chart is None
    assert "chart" in snap.stale


def test_the_live_snapshot_carries_the_expected_points_from_the_cache(live_repo, sleeper, chart_week6):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6))
    assert snap.expected is not None and snap.expected.players
    assert snap.expected.through_week == snap.week - 1


def test_the_live_snapshot_without_the_expected_points_file_still_builds(live_repo, sleeper, chart_week6):
    (live_repo / "data" / "cache" / "nflverse" / "ep_weekly_2026.csv").unlink()
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6))
    assert snap.expected is None and snap.stale == []
