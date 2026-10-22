"""
Tests for the power rankings formula.
They run on the fixture history, and on small histories built for one rule each.
"""
import pytest

from cornerstone.facts_league import standings
from cornerstone.history import load_history
from cornerstone.models import History, PastWeek
from cornerstone.parse import parse_week
from cornerstone.power_rankings import power_rankings
from cornerstone.sleeper import load_raw
from cornerstone.tunables import POWER_WEIGHTS

PAIRS = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]


def _history(raw_dir, root):
    return load_history(root, load_raw(raw_dir), week=6)


def _built(weekly_scores: list[dict[int, float]]) -> History:
    """A history with the fixed pairs and the given scores of each week, from week 1."""
    weeks = {
        n: PastWeek(week=n, scores=scores, pairs=PAIRS, points={}, projections={}, stats={}, moves=[])
        for n, scores in enumerate(weekly_scores, start=1)
    }
    return History(week=len(weeks), weeks=weeks)


def _row(rows, roster_id):
    return next(r for r in rows if r.roster_id == roster_id)


def test_twelve_rows_every_week(fixture_raw_dir, fixture_history_root):
    ranked = power_rankings(_history(fixture_raw_dir, fixture_history_root), 6)
    assert sorted(ranked) == [1, 2, 3, 4, 5, 6]
    for rows in ranked.values():
        assert len(rows) == 12
        assert len({r.roster_id for r in rows}) == 12


def test_ranks_are_permutations(fixture_raw_dir, fixture_history_root):
    for rows in power_rankings(_history(fixture_raw_dir, fixture_history_root), 6).values():
        assert sorted(r.power_rank for r in rows) == list(range(1, 13))
        for component in ("standing", "form", "schedule_played", "scoring"):
            assert sorted(r.ranks[component] for r in rows) == list(range(1, 13))
            assert all(0 <= r.values[component] <= 1 for r in rows)


def test_week_one_has_no_movement_and_week_two_is_the_rank_change(fixture_raw_dir, fixture_history_root):
    ranked = power_rankings(_history(fixture_raw_dir, fixture_history_root), 6)
    assert all(r.movement is None for r in ranked[1])
    for row in ranked[2]:
        assert row.movement == _row(ranked[1], row.roster_id).power_rank - row.power_rank


def test_standing_rank_is_the_standings_order(fixture_raw_dir, fixture_history_root):
    h = _history(fixture_raw_dir, fixture_history_root)
    rows = power_rankings(h, 6)[6]
    table = standings(parse_week(load_raw(fixture_raw_dir)), h)
    assert [r.roster_id for r in sorted(rows, key=lambda r: r.ranks["standing"])] == [s.roster_id for s in table]


# Roster 1 scores 106.5 every week, so its all-play record is the same in both weeks below.
# Only roster 2, its head-to-head opponent, and roster 12 swap places around it.
_BASE = {rid: 100.0 + rid for rid in range(1, 13)} | {1: 106.5}
# Roster 1 beats roster 2 head to head.
_WIN = _BASE | {2: 102.0, 12: 112.0}
# Roster 1 loses to roster 2 head to head.
_LOSS = _BASE | {2: 112.0, 12: 102.0}


def test_three_win_streak_lifts_form():
    # The all-play rate of roster 1 is equal in both histories, so only the head-to-head half differs.
    streak = _built([_WIN] * 3)
    one_win = _built([_WIN, _LOSS, _LOSS])
    assert (_row(power_rankings(streak, 3)[3], 1).values["form"]
            > _row(power_rankings(one_win, 3)[3], 1).values["form"])


def test_form_counts_only_the_last_three_weeks():
    # The two histories differ only in week 1, which is outside the 3-week window at week 4.
    won_week_one = _built([_WIN, _LOSS, _LOSS, _LOSS])
    lost_week_one = _built([_LOSS, _LOSS, _LOSS, _LOSS])
    assert (_row(power_rankings(won_week_one, 4)[4], 1).values["form"]
            == _row(power_rankings(lost_week_one, 4)[4], 1).values["form"])


def test_all_play_record_splits_equal_points_for():
    # Rosters 1 and 3 both score 200 points for. Every other team scores 90 each week.
    # Roster 1 goes 11-0 then 0-11 in all-play. Roster 3 goes 10-1 then 11-0.
    others = {rid: 90.0 for rid in range(1, 13)}
    h = _built([others | {1: 200.0, 3: 100.0}, others | {1: 0.0, 3: 100.0}])
    rows = power_rankings(h, 2)[2]
    assert _row(rows, 3).values["scoring"] > _row(rows, 1).values["scoring"]


def _quality_week() -> History:
    """One week: rosters 1, 3, and 5 win and go 2-0. Roster 2 loses to 1 but is fourth by points."""
    return _built([{1: 150, 2: 140, 3: 130, 4: 120, 5: 125, 6: 115,
                    7: 100, 8: 90, 9: 95, 10: 85, 11: 92, 12: 80}])


def test_top_four_win_lifts_schedule():
    rows = power_rankings(_quality_week(), 1)[1]
    assert [r.roster_id for r in sorted(rows, key=lambda r: r.ranks["standing"])][:4] == [1, 3, 5, 2]
    # Rosters 1 and 3 are both 2-0, and both opponents are 0-1. Only roster 1 beat a top-4 team.
    assert _row(rows, 1).ranks["schedule_played"] < _row(rows, 3).ranks["schedule_played"]


def test_no_top_four_game_is_neutral():
    rows = power_rankings(_quality_week(), 1)[1]
    # Roster 3 played roster 4, who is 0-1, so the opponent half is 0 and the quality half is the neutral 0.5.
    assert _row(rows, 3).values["schedule_played"] == pytest.approx(0.5 / 2)


def test_weight_change_moves_the_result(fixture_raw_dir, fixture_history_root, monkeypatch):
    h = _history(fixture_raw_dir, fixture_history_root)
    equal = [r.roster_id for r in power_rankings(h, 6)[6]]
    for component in POWER_WEIGHTS:
        monkeypatch.setitem(POWER_WEIGHTS, component, 0.0)
    monkeypatch.setitem(POWER_WEIGHTS, "standing", 1.0)
    rows = power_rankings(h, 6)[6]
    assert [r.roster_id for r in rows] != equal
    assert all(r.power_rank == r.ranks["standing"] for r in rows)
