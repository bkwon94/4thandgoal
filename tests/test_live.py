"""
Tests for the live snapshot builder.
Every fetch is a fixture-backed callable, so no test calls the network or Claude.
"""
import csv
import os
import shutil
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from cornerstone.config import cornerstone_config
from cornerstone.history import save_week_to_history
from cornerstone.live import ProjectionsCache, fetch_current_week, live_rosters_snapshot, live_snapshot, refresh_sources
from cornerstone.nflverse import (
    DEPTH_CHARTS_URL, FFIDS_URL, FFOPPORTUNITY_URL, INJURIES_URL, SCHEDULES_URL, STATS_PLAYER_URL, cache_path,
)
from cornerstone.sleeper import load_raw
from cornerstone.snapshot import load_snapshot
from cornerstone.tunables import TEAMS_CACHE_SECONDS

ET = ZoneInfo("America/New_York")
# The league config the builds and fetches of these tests read.
CONFIG = cornerstone_config()
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
    after = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 8, 0, tzinfo=ET),
                          fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                          fetch_nflverse=_no_network, read_chart=chart, config=CONFIG)
    before = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 7, 59, tzinfo=ET),
                           fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                           fetch_nflverse=_no_network, read_chart=chart, config=CONFIG)
    assert [week for _, week in chart.weeks] == [7, 6]
    assert after.as_of.chart_week == chart_week6.week
    assert before.chart == chart_week6


def test_the_stamps_hold_the_stats_through_week_and_the_rosters_fetch_time(live_repo, sleeper, chart_week6):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                         fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=_no_network, read_chart=ChartRecorder(chart_week6), config=CONFIG)
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

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                         fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None), config=CONFIG)
    assert asked == [SCHEDULES_URL]
    assert time.time() - path.stat().st_mtime < DAY
    assert snap.stale == []
    assert "chart" in snap.missing


def test_a_failed_refresh_keeps_the_old_cache_and_notes_it(live_repo, sleeper):
    path = _age(live_repo, DEPTH_CHARTS_URL, 2 * DAY)
    before = path.read_bytes()

    def fetch(url):
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                         fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None), config=CONFIG)
    assert path.read_bytes() == before
    assert snap.stale == ["depth charts"]
    assert snap.depth_charts is not None


def test_a_source_with_no_cache_and_a_failed_fetch_is_missing_and_noted(live_repo, sleeper):
    cache_path(live_repo / "data" / "cache" / "nflverse", FFIDS_URL, 2026).unlink()

    def fetch(url):
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                         fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                         fetch_nflverse=fetch, read_chart=ChartRecorder(None), config=CONFIG)
    assert snap.stale == ["id map"]
    assert "id_map" in snap.missing


def test_a_season_that_is_not_in_progress_stops_the_build(live_repo, sleeper):
    with pytest.raises(ValueError, match="2025"):
        live_snapshot(live_repo, 2025, now=datetime(2026, 10, 19, tzinfo=ET),
                      fetch_sleeper=sleeper, fetch_history_week=_no_history_fetch,
                      fetch_nflverse=_no_network, read_chart=ChartRecorder(None), config=CONFIG)


def test_on_monday_night_the_raw_week_is_the_trade_week_and_its_known_games_stay_out_of_the_saved_history(
        live_repo, sleeper, chart_week6):
    # Monday 2026-10-19 is before the week 7 cutoff, so the chart week is 6. Sleeper shows week 6 too.
    chart = ChartRecorder(chart_week6)
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 21, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network, read_chart=chart,
                         config=CONFIG)
    assert [week for _, week in chart.weeks] == [6]
    assert snap.week == 6
    # The week 6 stat lines are the known games, so the player stats read them and the standings do not.
    assert snap.as_of.stats_through == 6
    assert snap.as_of.completed_through == 5
    assert snap.as_of.known_games is not None and snap.as_of.known_games.games == 14
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5, 6]
    assert sum(s.wins + s.losses for s in snap.standings) == 5 * 2 * 12
    assert not (live_repo / "data" / "2026" / "history" / "week-06").exists()
    assert snap.stale == []


def test_the_live_snapshot_and_the_saved_snapshot_give_the_same_position_ranks_for_the_same_raw(
        live_repo, fixture_raw_dir, fixture_history_root, chart_week6):
    # Before the first kickoff of week 6 Sleeper has no week 6 line, so both paths read the saved weeks 1 to 5.
    shutil.copy(fixture_history_root.parent / "returns.json", live_repo / "data" / "2026" / "returns.json")

    def before_kickoff(league_id, players_cache):
        raw = load_raw(fixture_raw_dir)
        raw["stats"] = []
        return raw, FETCHED

    live = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 15, 12, 0, tzinfo=ET), fetch_sleeper=before_kickoff,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    saved = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert (live.week, live.as_of.stats_through) == (saved.week, saved.as_of.stats_through) == (6, 5)
    pool = {pid for past in saved.stats.weeks.values() for pid in past.positions} | set(saved.players)
    live_ranks = {pid: live.position_rank(pid) for pid in pool}
    assert live_ranks == {pid: saved.position_rank(pid) for pid in pool}
    # Tuten is RB15 on both paths, as the hand count on the saved weeks gives.
    assert live_ranks["12490"] == 15


def test_a_known_game_of_week_n_moves_a_live_position_rank_and_weeks_1_to_n_minus_1_rank_as_the_saved_week(
        live_repo, sleeper, fixture_raw_dir, fixture_history_root, chart_week6):
    # On Monday night the week 6 stat lines are known games. The saved week 6 never counts its own games.
    shutil.copy(fixture_history_root.parent / "returns.json", live_repo / "data" / "2026" / "returns.json")
    live = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 21, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    saved = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert (live.as_of.stats_through, saved.as_of.stats_through) == (6, 5)
    assert all(live.stats.weeks[week] == saved.stats.weeks[week] for week in range(1, 6))
    # With the known games cut away, the live table is the saved table, so only week 6 moves a rank.
    cut = live.model_copy(update={
        "stats": live.stats.model_copy(update={"weeks": {w: past for w, past in live.stats.weeks.items() if w < 6}}),
        "as_of": live.as_of.model_copy(update={"stats_through": 5})})
    assert cut.rank_table() == saved.rank_table()
    # Tuten's week 6 game lifts him from RB15 to RB12.
    assert (saved.position_rank("12490"), live.position_rank("12490")) == (15, 12)


def test_the_live_snapshot_and_the_saved_snapshot_give_the_same_free_agents_for_the_same_raw(
        live_repo, free_agent_raw_dir, fixture_history_root, chart_week6):
    shutil.copy(fixture_history_root.parent / "returns.json", live_repo / "data" / "2026" / "returns.json")

    def before_kickoff(league_id, players_cache):
        raw = load_raw(free_agent_raw_dir)
        raw["stats"] = []
        return raw, FETCHED

    live = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 15, 12, 0, tzinfo=ET), fetch_sleeper=before_kickoff,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    saved = load_snapshot(free_agent_raw_dir, fixture_history_root, chart_week6)
    assert live.free_agents == saved.free_agents
    # Perine, the back with no stat line, and Bigsby, in player id order, as the saved test reads them.
    assert [p.player_id for p in live.free_agents["RB"]] == ["4147", "80001", "9225"]
    assert live.best_free_agent(["RB"]) == saved.best_free_agent(["RB"])


def _with_kickoff(repo, game_id, gametime):
    """Give the schedules cache a kickoff time column, with `gametime` for `game_id` and none for the rest."""
    path = cache_path(repo / "data" / "cache" / "nflverse", SCHEDULES_URL, 2026)
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["gametime"] = gametime if row["game_id"] == game_id else ""
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_on_monday_night_the_clock_of_the_request_puts_the_monday_game_in_progress(live_repo, sleeper, chart_week6):
    # The Commanders at the 49ers kick off at 8:15 pm Eastern on Monday 2026-10-19, so 9 pm is in the game.
    _with_kickoff(live_repo, "2026_06_WAS_SF", "20:15")
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 21, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert snap.as_of.known_games.games == 14
    assert snap.as_of.known_games.in_progress == 1
    assert snap.in_progress_teams == {"WAS", "SF"}


def test_on_the_tuesday_before_the_roll_the_raw_week_joins_the_history(live_repo, sleeper, chart_week6):
    # Tuesday 2026-10-20 09:00 is after the week 7 cutoff, so the chart week is 7. Sleeper still shows week 6.
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
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
                         fetch_history_week=fetch, fetch_nflverse=_no_network, read_chart=ChartRecorder(chart_week6),
                         config=CONFIG)
    assert asked == [5]
    assert snap.stale == ["history"]
    # A gap at week 5 keeps the week 6 games out too, so the known games never skip a week.
    assert snap.as_of.stats_through == 4
    assert snap.as_of.known_games is None
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4]


def test_on_the_tuesday_before_the_roll_the_raw_week_is_saved_so_points_allowed_count_it(
        live_repo, sleeper, chart_week6):
    # The points allowed read weeks 1 to 6 from the history on disk, and only the raw data of this run holds week 6.
    saved = live_repo / "data" / "2026" / "history" / "week-06"
    assert not saved.exists()
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
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
                  read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert (saved / "stats.json").read_bytes() == before


def test_on_the_tuesday_a_failed_history_write_marks_history_stale_and_the_snapshot_still_builds(
        live_repo, sleeper, chart_week6):
    # A file where the week 6 directory goes makes the write fail with an OSError.
    (live_repo / "data" / "2026" / "history" / "week-06").write_text("", encoding="utf-8")
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 20, 9, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert "history" in snap.stale
    assert snap.week == 7


def test_an_injuries_file_older_than_a_day_refreshes_before_the_snapshot(live_repo, sleeper, fixture_nflverse_dir):
    path = _age(live_repo, INJURIES_URL, 2 * DAY)
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / path.name).read_bytes()

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=fetch, read_chart=ChartRecorder(None),
                         config=CONFIG)
    assert asked == [INJURIES_URL.format(season=2026)]
    assert time.time() - path.stat().st_mtime < DAY
    assert snap.stale == []


def test_the_live_path_keeps_a_file_one_hour_old(live_repo, sleeper, chart_week6):
    _age(live_repo, SCHEDULES_URL, 60 * 60)
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert snap.stale == []


def _refresh_at_age(live_repo, sleeper, fixture_nflverse_dir, url, seconds, max_age_seconds=DAY, fail=False):
    """Age one source, run the refresh with no chart read, and give the result and the fetched urls."""
    path = _age(live_repo, url, seconds)
    asked = []

    def fetch(asked_url):
        asked.append(asked_url)
        if fail:
            raise httpx.ConnectError("down")
        return (fixture_nflverse_dir / path.name).read_bytes()

    _, _, week = fetch_current_week(live_repo, CONFIG, sleeper)
    result = refresh_sources(live_repo, 2026, datetime(2026, 10, 19, 12, 0, tzinfo=ET), week,
                             fetch_nflverse=fetch, fetch_history_week=_no_history_fetch, read_chart=None,
                             max_age_seconds=max_age_seconds, config=CONFIG)
    return result, asked


def test_an_injuries_file_seven_hours_old_refreshes_and_is_named(live_repo, sleeper, fixture_nflverse_dir):
    result, asked = _refresh_at_age(live_repo, sleeper, fixture_nflverse_dir, INJURIES_URL, 7 * 60 * 60)
    assert asked == [INJURIES_URL.format(season=2026)]
    assert result.refreshed == ["injuries"]


def test_a_player_weeks_file_seven_hours_old_refreshes(live_repo, sleeper, fixture_nflverse_dir):
    result, asked = _refresh_at_age(live_repo, sleeper, fixture_nflverse_dir, STATS_PLAYER_URL, 7 * 60 * 60)
    assert asked == [STATS_PLAYER_URL.format(season=2026)]
    assert result.refreshed == ["player weeks"]


def test_a_schedules_file_seven_hours_old_stays_and_one_25_hours_old_refreshes(
        live_repo, sleeper, fixture_nflverse_dir):
    result, asked = _refresh_at_age(live_repo, sleeper, fixture_nflverse_dir, SCHEDULES_URL, 7 * 60 * 60)
    assert asked == []
    assert result.refreshed == []
    result, asked = _refresh_at_age(live_repo, sleeper, fixture_nflverse_dir, SCHEDULES_URL, 25 * 60 * 60)
    assert asked == [SCHEDULES_URL.format(season=2026)]
    assert result.refreshed == ["schedules"]


def test_a_failed_six_hour_refresh_keeps_the_file_and_does_not_name_it_stale(
        live_repo, sleeper, fixture_nflverse_dir):
    path = cache_path(live_repo / "data" / "cache" / "nflverse", INJURIES_URL, 2026)
    before = path.read_bytes()
    result, asked = _refresh_at_age(
        live_repo, sleeper, fixture_nflverse_dir, INJURIES_URL, 7 * 60 * 60, fail=True)
    assert asked == [INJURIES_URL.format(season=2026)]
    assert path.read_bytes() == before
    assert result.stale == []
    assert result.refreshed == []


def test_a_forced_refresh_fetches_every_source(live_repo, sleeper, fixture_nflverse_dir):
    _, _, week = fetch_current_week(live_repo, CONFIG, sleeper)
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / url.rsplit("/", 1)[-1]).read_bytes()

    result = refresh_sources(live_repo, 2026, datetime(2026, 10, 19, 12, 0, tzinfo=ET), week,
                             fetch_nflverse=fetch, fetch_history_week=_no_history_fetch, read_chart=None,
                             max_age_seconds=0, config=CONFIG)
    assert set(asked) == {url.format(season=2026) for url in (
        SCHEDULES_URL, DEPTH_CHARTS_URL, FFIDS_URL, INJURIES_URL, FFOPPORTUNITY_URL, STATS_PLAYER_URL)}
    assert len(asked) == 6
    assert len(result.refreshed) == 6


def test_no_chart_reader_skips_the_chart_and_notes_no_stale_chart(live_repo, sleeper):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network, read_chart=None,
                         config=CONFIG)
    assert snap.chart is None
    assert "chart" not in snap.stale


def test_a_chart_read_that_raises_gives_no_chart_and_notes_it_stale(live_repo, sleeper):
    def read_chart(repo, season_start, week, lines):
        # The Anthropic client raises TypeError when the API key is absent.
        raise TypeError("no api key")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network, read_chart=read_chart,
                         config=CONFIG)
    assert snap.chart is None
    assert "chart" in snap.stale


def test_the_live_snapshot_carries_the_expected_points_from_the_cache(live_repo, sleeper, chart_week6):
    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=_no_network,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert snap.expected is not None and snap.expected.players
    assert snap.expected.through_week == snap.week - 1


def test_the_refresh_downloads_a_missing_expected_points_file_and_the_snapshot_carries_it(
        live_repo, sleeper, chart_week6, fixture_nflverse_dir):
    # On Fly no weekly build fills the cache, so the seed cache has no expected points file.
    path = cache_path(live_repo / "data" / "cache" / "nflverse", FFOPPORTUNITY_URL, 2026)
    path.unlink()
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / path.name).read_bytes()

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=fetch,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert asked == [FFOPPORTUNITY_URL.format(season=2026)]
    assert path.exists()
    assert snap.expected is not None and snap.expected.players
    assert snap.stale == []


def test_the_live_snapshot_without_the_expected_points_file_and_a_failed_fetch_still_builds(
        live_repo, sleeper, chart_week6):
    cache_path(live_repo / "data" / "cache" / "nflverse", FFOPPORTUNITY_URL, 2026).unlink()

    def fetch(url):
        raise httpx.ConnectError("down")

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=fetch,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert snap.expected is None and snap.stale == ["expected points"]


def test_the_refresh_downloads_a_missing_weekly_player_file_and_the_snapshot_carries_the_wopr(
        live_repo, sleeper, chart_week6, fixture_nflverse_dir):
    # On Fly no weekly build fills the cache, so the seed cache has no weekly player file.
    path = cache_path(live_repo / "data" / "cache" / "nflverse", STATS_PLAYER_URL, 2026)
    path.unlink()
    asked = []

    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / path.name).read_bytes()

    snap = live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper,
                         fetch_history_week=_no_history_fetch, fetch_nflverse=fetch,
                         read_chart=ChartRecorder(chart_week6), config=CONFIG)
    assert asked == [STATS_PLAYER_URL.format(season=2026)]
    assert path.exists()
    # The file has rows of the trade week, so the known games read them.
    assert snap.wopr and all(week <= snap.week for weeks in snap.wopr.values() for week in weeks)
    assert any(snap.week in weeks for weeks in snap.wopr.values())
    assert snap.stale == []


@pytest.fixture
def sleeper_now(fixture_raw_dir):
    """The Sleeper fetch as fetch_live_raw gives it: the raw data with no projections ahead."""
    def fetch(league_id, players_cache):
        raw = load_raw(fixture_raw_dir)
        raw.pop("projections_ahead")
        return raw, FETCHED
    return fetch


class ProjectionsRecorder:
    def __init__(self):
        self.calls = []

    def __call__(self, season, week):
        self.calls.append((season, week))
        return [{"week": 7, "projections": {"5850": 18.0}}]


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_the_live_snapshot_fetches_the_projections_ahead_once_in_the_cache_window(live_repo, sleeper_now):
    fetch, clock = ProjectionsRecorder(), Clock()
    cache = ProjectionsCache(TEAMS_CACHE_SECONDS, clock=clock)

    def snapshot():
        return live_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET), fetch_sleeper=sleeper_now,
                             fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch, read_chart=None,
                             fetch_projections=fetch, projections=cache, config=CONFIG)

    assert snapshot().projections_ahead["5850"][7] == 18.0
    clock.now += TEAMS_CACHE_SECONDS - 1
    snapshot()
    assert fetch.calls == [(2026, 6)]
    clock.now += 1
    snapshot()
    assert fetch.calls == [(2026, 6), (2026, 6)]


def test_the_rosters_snapshot_fetches_no_projections_ahead(live_repo, sleeper_now):
    # The teams route never grades, so it never waits on the projections.
    snap = live_rosters_snapshot(live_repo, 2026, now=datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                                 fetch_sleeper=sleeper_now, config=CONFIG)
    assert snap.projections_ahead is None
