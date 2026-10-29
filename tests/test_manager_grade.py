"""
Tests for the roster grade and the slot ranks of the managers file.
They feed the score known parts, and they read the grade of each entry on the fixture snapshot of week 6.
"""
import pytest

from cornerstone.history import load_history
from cornerstone.manager_grade import GradeParts, depth_word, grade_letter, grade_score
from cornerstone.managers import managers
from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw
from cornerstone.snapshot import week_snapshot
from cornerstone.tunables import GRADE_WEIGHTS


def _entries(raw_dir, root, with_snapshot=True):
    raw = load_raw(raw_dir)
    snapshot = week_snapshot(raw, root, 6) if with_snapshot else None
    return managers(load_history(root, raw, week=6), parse_week(raw).teams, snapshot=snapshot)


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
