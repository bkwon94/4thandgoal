"""
Tests for the points allowed per position per defense.
They read the weekly stats of the history fixture.
"""
import json
import shutil

from cornerstone.points_allowed import points_allowed


def test_points_allowed_ranks_a_defense_at_a_position(fixture_history_root):
    allowed = points_allowed(fixture_history_root, 5)
    # Worked by hand from the stat lines of weeks 1 to 5: SF gave up 90.1 half-PPR points to running backs.
    assert (allowed["SF"]["RB"].points, allowed["SF"]["RB"].rank) == (90.1, 15)
    assert (allowed["NO"]["RB"].points, allowed["NO"]["RB"].rank) == (139.1, 1)
    assert allowed["SF"]["QB"].rank == 31


def test_points_allowed_counts_only_the_weeks_through_the_given_one(fixture_history_root):
    assert points_allowed(fixture_history_root, 4)["NO"]["RB"].points < 139.1


def test_points_allowed_with_a_missing_week_is_none(fixture_history_root, tmp_path):
    shutil.copytree(fixture_history_root, tmp_path / "history")
    (tmp_path / "history" / "week-03" / "stats.json").unlink()
    assert points_allowed(tmp_path / "history", 5) is None


def test_points_allowed_with_an_outage_week_is_none(fixture_history_root, tmp_path):
    shutil.copytree(fixture_history_root, tmp_path / "history")
    (tmp_path / "history" / "week-03" / "stats.json").write_text(json.dumps([]))
    assert points_allowed(tmp_path / "history", 5) is None
