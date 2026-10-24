"""
Tests for the snapshot the trade analyzer grades from.
They build it from the recorded week 6 data and the week 6 trade values, with no network.
"""
import shutil

from cornerstone.slow_sources import SlowSources, load_slow_sources
from cornerstone.snapshot import load_snapshot


def test_week_6_snapshot_holds_rosters_teams_standings_and_slots(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.season == 2026
    assert sorted(snap.rosters) == list(range(1, 13))
    assert "7569" in snap.rosters[4]
    assert "4034" in snap.rosters[3]
    assert snap.players["7569"].name == "Nico Collins"
    assert snap.players["7569"].position == "WR"
    assert len(snap.teams) == 12
    assert [s.rank for s in snap.standings] == list(range(1, 13))
    assert snap.roster_positions[:3] == ["QB", "RB", "RB"]


def test_week_6_snapshot_is_the_trade_week_and_its_inputs_end_at_week_5(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.week == 6
    assert snap.chart == chart_week6
    assert snap.as_of.chart_week == 6
    assert snap.as_of.stats_through == 5
    # The raw week 6 is the trade week, so its games stay out of the history.
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5]
    assert snap.stale == []


def test_week_6_standings_count_the_games_of_weeks_1_to_5(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Each week is two games for each of the 12 rosters: the head-to-head game and the median game.
    games = sum(s.wins + s.losses for s in snap.standings)
    assert games == 5 * 2 * 12


def test_a_history_without_week_5_stamps_the_last_week_it_holds_and_notes_it(
        fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    root = tmp_path / "history"
    shutil.copytree(fixture_history_root, root)
    shutil.rmtree(root / "week-05")
    snap = load_snapshot(fixture_raw_dir, root, chart_week6)
    assert snap.week == 6
    assert snap.as_of.stats_through == 4
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4]
    assert snap.stale == ["history"]


def test_slow_sources_are_empty_and_named_as_missing(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.injuries is None
    assert snap.schedules is None
    assert snap.depth_charts is None
    assert snap.points_allowed is None
    assert snap.id_map is None
    assert snap.expected is None and snap.wopr is None
    assert snap.missing == ["schedules", "depth_charts", "id_map", "points_allowed", "injuries", "expected_points",
                            "player_weeks"]


def test_slow_sources_fill_the_snapshot_and_only_the_files_not_in_the_cache_stay_missing(
        fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    cache.mkdir()
    for name in ("games.csv", "depth_charts_2026.csv.gz", "db_playerids.csv", "injuries_2026.csv.gz"):
        shutil.copy(fixture_nflverse_dir / name, cache / name)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow)
    assert snap.schedules == slow.schedules and snap.schedules
    assert snap.depth_charts == slow.depth_charts and snap.depth_charts
    assert snap.id_map == slow.id_map and snap.id_map
    assert snap.points_allowed == slow.points_allowed and snap.points_allowed
    assert snap.injuries == slow.injuries and snap.injuries
    # The cache holds neither the expected points file nor the weekly player file, so only those two are missing.
    assert snap.missing == ["expected_points", "player_weeks"]


def test_a_week_with_no_chart_has_no_chart_week(fixture_raw_dir, fixture_history_root):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, None)
    assert snap.chart is None
    assert snap.as_of.chart_week is None
    assert "chart" in snap.missing


def test_the_returns_file_gives_the_return_week_and_sleeper_gives_the_injury_status(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Brian keeps the returns file by hand. Josh Jacobs, suspended in week 6, is back in week 7.
    assert snap.returns == {"5850": 7}
    assert snap.players["5850"].injury_status == "NA"
    assert snap.players["7569"].injury_status is None
    assert "returns" not in snap.missing


def test_a_season_with_no_returns_file_has_no_return_weeks_and_names_it_as_missing(
        fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    # The returns file sits beside the history, so a history root with no sibling file has none.
    history_root = tmp_path / "2026" / "history"
    shutil.copytree(fixture_history_root, history_root)
    snap = load_snapshot(fixture_raw_dir, history_root, chart_week6)
    assert snap.returns == {}
    assert snap.missing[-1] == "returns"


def test_the_snapshot_carries_the_wopr_by_player_and_week(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, SlowSources(wopr={"12501": {5: 58}}))
    assert snap.wopr == {"12501": {5: 58}}
    assert load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6).wopr is None


def test_the_snapshot_carries_the_projections_ahead_by_player_and_week(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Josh Jacobs has his bye in week 11, so that week has no row.
    assert snap.projections_ahead["5850"] == {7: 10.81, 8: 14.19, 9: 12.41, 10: 11.0, 12: 11.39, 13: 13.25, 14: 12.4}


def test_the_projections_ahead_start_at_the_raw_week(fixture_raw_dir, fixture_history_root, chart_week6):
    # A player due back in the raw week counts for that week too, so its half-PPR projection joins the weeks ahead.
    # Nico Collins has his bye in week 8, so that week has no row.
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.projections_ahead["7569"] == {
        6: 15.52, 7: 15.29, 9: 15.25, 10: 14.48, 11: 15.16, 12: 14.88, 13: 15.43, 14: 16.6}


def test_a_week_with_no_projections_ahead_file_has_none(fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    raw_dir = tmp_path / "raw"
    shutil.copytree(fixture_raw_dir, raw_dir)
    (raw_dir / "projections_ahead.json").unlink()
    snap = load_snapshot(raw_dir, fixture_history_root, chart_week6)
    assert snap.projections_ahead is None
    # The missing list stays as it is. The fit reason says the projections are not available when a player is due back.
    assert "projections_ahead" not in snap.missing and "projections" not in snap.missing
