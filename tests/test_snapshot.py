"""
Tests for the snapshot the trade analyzer grades from.
They build it from the recorded week 6 data and the week 6 chart values, with no network.
"""
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


def test_week_6_snapshot_holds_the_chart_week_and_stats_through_the_last_completed_week(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.chart == chart_week6
    assert snap.as_of.chart_week == 6
    assert snap.as_of.stats_through == 6
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5, 6]


def test_slow_sources_are_empty_and_named_as_missing(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.usage is None
    assert snap.injuries is None
    assert snap.schedules is None
    assert snap.depth_charts is None
    assert snap.points_allowed is None
    assert snap.missing == ["usage", "injuries", "schedules", "depth_charts", "points_allowed"]


def test_a_week_with_no_chart_has_no_chart_week(fixture_raw_dir, fixture_history_root):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, None)
    assert snap.chart is None
    assert snap.as_of.chart_week is None
    assert "chart" in snap.missing
