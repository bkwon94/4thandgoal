"""
Tests for the roster grade and the slot ranks of the managers file.
They feed the score known parts, and they read the grade of each entry on the fixture snapshot of week 6.
The grade reads the projections ahead, so some tests build projections that put a player above or below the line.
"""
import pytest

from cornerstone.history import load_history
from cornerstone.manager_grade import (
    GradeParts, depth_word, grade_letter, grade_score, position_ranks, projected_values, roster_grades,
)
from cornerstone.managers import managers
from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw
from cornerstone.snapshot import week_snapshot
from cornerstone.tunables import GRADE_WEIGHTS, LAST_REGULAR_WEEK


def _ahead(raw):
    return {entry["week"]: entry["projections"] for entry in raw["projections_ahead"]}


def _entries(raw_dir, root, with_snapshot=True):
    raw = load_raw(raw_dir)
    snapshot = week_snapshot(raw, root, 6) if with_snapshot else None
    return managers(load_history(root, raw, week=6), parse_week(raw).teams, snapshot=snapshot,
                    projections_ahead=_ahead(raw))


def _snapshot(raw_dir, root):
    return week_snapshot(load_raw(raw_dir), root, 6)


def _depth(grade, position):
    return next(slot.depth for slot in grade.slots if slot.position == position)


def _roster_ahead(snapshot, roster_id, points=10.0):
    """Projections ahead for the players of one roster only, so each of them ranks inside a small pool."""
    return {week: {pid: points for pid in snapshot.rosters[roster_id]} for week in (7, 8)}


@pytest.mark.parametrize("score, letter", [
    (100, "A+"), (90, "A+"), (89.99, "A"), (80, "A"), (79.99, "B"), (65, "B"), (64.99, "C"), (50, "C"),
    (49.99, "D"), (0, "D"),
])
def test_each_band_at_its_edge(score, letter):
    assert grade_letter(score) == letter


def test_the_score_is_the_weighted_sum_of_the_parts():
    assert grade_score(GradeParts(slots=1, holes=1, depth=1, lineup=1)) == 100
    assert grade_score(GradeParts(slots=0, holes=0, depth=0, lineup=0)) == 0
    assert grade_score(GradeParts(slots=1, holes=0, depth=0, lineup=0)) == GRADE_WEIGHTS["slots"]
    assert grade_score(GradeParts(slots=0, holes=0, depth=0, lineup=0.5)) == GRADE_WEIGHTS["lineup"] / 2


def test_a_score_at_a_band_edge_from_known_parts_reads_that_band():
    # Slots, holes, and depth in full give 75 of the 100. Lineup at 0.6 of its 25 gives 15 more, so the edge of A.
    parts = GradeParts(slots=1, holes=1, depth=1, lineup=0.6)
    assert grade_score(parts) == 90
    assert grade_letter(grade_score(parts)) == "A+"


@pytest.mark.parametrize("starters, above, hole, word", [
    (2, 3, False, "deep"),
    (2, 2, False, "fine"),
    (2, 2, True, "thin"),
    # A hole wins over depth: a slot no one above the line fills reads thin.
    (2, 4, True, "thin"),
])
def test_each_depth_word(starters, above, hole, word):
    assert depth_word(starters, above, hole) == word


def test_each_entry_carries_the_letter_and_the_slot_ranks_in_order(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root)
    for entry in entries:
        assert entry.grade.letter in {"A+", "A", "B", "C", "D"}
        assert [slot.position for slot in entry.grade.slots] == ["QB", "RB", "WR", "TE"]
        assert all(slot.depth in {"deep", "fine", "thin"} for slot in entry.grade.slots)


def test_the_slot_ranks_place_each_team_once_per_position(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root)
    for index, position in enumerate(["QB", "RB", "WR", "TE"]):
        ranks = sorted(entry.grade.slots[index].rank for entry in entries)
        assert ranks == list(range(1, 13)), position


def test_the_file_carries_the_letter_and_never_the_score(fixture_raw_dir, fixture_history_root):
    entry = _entries(fixture_raw_dir, fixture_history_root)[0]
    grade = entry.model_dump(mode="json")["grade"]
    assert set(grade) == {"letter", "slots"}
    assert set(grade["slots"][0]) == {"position", "rank", "depth"}


def test_the_grade_is_null_without_a_snapshot(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root, with_snapshot=False)
    assert all(entry.grade is None for entry in entries)
    assert entries[0].model_dump(mode="json")["grade"] is None


def test_the_value_is_the_mean_over_the_weeks_ahead_with_a_missing_week_as_0():
    values = projected_values({7: {"a": 10.0, "b": 4.0}, 8: {"a": 20.0}})
    assert values == {"a": 15.0, "b": 2.0}


def test_the_value_stops_at_the_last_regular_week():
    ahead = {LAST_REGULAR_WEEK - 1: {"a": 10.0}, LAST_REGULAR_WEEK: {"a": 20.0}, LAST_REGULAR_WEEK + 1: {"a": 90.0}}
    assert projected_values(ahead) == {"a": 15.0}


def test_a_player_with_a_cold_month_and_a_high_projection_ahead_ranks_high(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    rostered = [pid for roster in snapshot.rosters.values() for pid in roster if snapshot.players[pid].position == "WR"]
    # The coldest wide receiver on a roster by the analyzer's points per game over the last weeks.
    cold = min(rostered, key=lambda pid: (snapshot.lineup_value(pid), pid))
    ahead = _ahead(load_raw(fixture_raw_dir))
    ahead = {week: {**projections, cold: 99.0} for week, projections in ahead.items()}
    positions = {pid: player.position for pid, player in snapshot.players.items()}
    assert position_ranks(projected_values(ahead), positions)[cold] == 1


def test_a_player_with_no_projection_ahead_has_no_rank():
    ranks = position_ranks(projected_values({7: {"a": 10.0}}), {"a": "QB", "b": "QB"})
    assert ranks == {"a": 1}


def test_a_starter_out_with_a_projection_ahead_is_no_hole(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    # Roster 1 starts 10229 at WR with the status Out and no return week on file.
    assert snapshot.players["10229"].injury_status == "Out"
    grade = roster_grades(snapshot, _roster_ahead(snapshot, 1))[1]
    assert _depth(grade, "WR") != "thin"
    assert all(slot.depth != "thin" for slot in grade.slots)


def test_a_starter_with_no_projection_ahead_is_a_hole(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    ahead = _roster_ahead(snapshot, 1)
    # 8183 is the only QB of roster 1, so with no projection his slot is a hole.
    for projections in ahead.values():
        del projections["8183"]
    assert _depth(roster_grades(snapshot, ahead)[1], "QB") == "thin"


def test_the_grade_is_null_without_projections_ahead(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    entries = managers(load_history(fixture_history_root, raw, week=6), parse_week(raw).teams,
                       snapshot=week_snapshot(raw, fixture_history_root, 6))
    assert all(entry.grade is None for entry in entries)
