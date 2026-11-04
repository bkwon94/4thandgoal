"""
Tests for the power rankings formula.
They run on the fixture history, and on small histories built for one rule each.
"""
import pytest
from cpc import cpc_client

from cornerstone.history import load_history
from cornerstone.models import History, PastWeek
from cornerstone.parse import parse_week
from cornerstone.power_rankings import power_rankings
from cornerstone.provider.sleeper import load_raw
from cornerstone.standings_table import standings
from cornerstone.tunables import POWER_WEIGHTS

CLIENT = cpc_client()

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
    table = standings(parse_week(load_raw(fixture_raw_dir)), h, client=CLIENT)
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


# Rosters 5 to 12 score these each week, so the median sits among them.
_FILLERS = dict(zip(range(5, 13), [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0]))


def test_median_wins_extend_the_form_streak():
    # Over the 3 weeks, both rosters go 4-2 with the median game and 22-11 in all-play.
    # Roster 1 loses both games in week 1, then wins four in a row: a form streak of 4.
    # Roster 3 wins the head-to-head game in weeks 2 and 3 but loses the median in week 2: a form streak of 2.
    h = _built([
        _FILLERS | {1: 95.0, 2: 96.0, 3: 110.0, 4: 111.0},
        _FILLERS | {1: 110.0, 2: 95.0, 3: 96.0, 4: 94.0},
        _FILLERS | {1: 111.0, 2: 95.0, 3: 110.0, 4: 94.0},
    ])
    rows = power_rankings(h, 3)[3]
    assert _row(rows, 1).values["form"] > _row(rows, 3).values["form"]
    assert _row(rows, 1).ranks["form"] < _row(rows, 3).ranks["form"]


def test_form_record_counts_the_median_game():
    # Both histories give roster 1 the same head-to-head wins, the same all-play record, and the same
    # form streak of -2 from week 3. Only the median games of weeks 1 and 2 differ: 2-0 against 1-1.
    week_three = _FILLERS | {1: 90.0, 2: 99.0, 3: 98.0, 4: 97.0}
    # All-play 6-5 in weeks 1 and 2: above the median both weeks.
    six_and_six = _built([
        _FILLERS | {1: 102.5, 2: 90.0, 3: 91.0, 4: 92.0},
        _FILLERS | {1: 102.5, 2: 90.0, 3: 91.0, 4: 92.0},
        week_three,
    ])
    # All-play 1-10 then 11-0: above the median in week 2 only.
    one_and_eleven = _built([
        _FILLERS | {1: 91.5, 2: 90.0, 3: 98.0, 4: 99.0},
        _FILLERS | {1: 120.0, 2: 90.0, 3: 91.0, 4: 92.0},
        week_three,
    ])
    assert (_row(power_rankings(six_and_six, 3)[3], 1).values["form"]
            > _row(power_rankings(one_and_eleven, 3)[3], 1).values["form"])


def test_form_streak_breaks_on_a_tie():
    # Roster 1 wins both games in weeks 1 and 3. In week 2 it ties roster 2, then wins the median game.
    # The median game is the newer game of its week, so the streak stops at the tie.
    # Newest back: median 1, head to head 2, median 1, then the tie. The streak is 4 of a cap of 9.
    # A streak that ran through the tie would be 7.
    win = _FILLERS | {1: 110.0, 2: 95.0, 3: 96.0, 4: 94.0}
    h = _built([win, win | {2: 110.0}, win])
    # The weighted record is 7-0 with the tie as neither: 2 + 1, 1, 2 + 1. All-play is 32-0.
    streak = (4 + 9) / 18
    assert _row(power_rankings(h, 3)[3], 1).values["form"] == pytest.approx((streak + 1 + 1) / 3)


def test_a_losing_form_streak_scores_below_an_even_record():
    # Roster 1 wins both games in week 1. In week 2 it wins head to head but loses the median game.
    # In week 3 it loses both games. Newest back: median -1, head to head -2, median -1, then the win.
    # The form streak is -4 of a cap of 9. A streak clamped at 0 would score 0.5.
    win = _FILLERS | {1: 110.0, 2: 95.0, 3: 96.0, 4: 94.0}
    h = _built([win, win | {1: 99.0}, win | {1: 90.0}])
    # The weighted record: wins 2 + 1 + 2 = 5, losses 1 + 2 + 1 = 4. All-play: 11-0, then 3-8, then 0-11.
    streak = (-4 + 9) / 18
    assert streak < 0.5
    assert _row(power_rankings(h, 3)[3], 1).values["form"] == pytest.approx((streak + 5 / 9 + 14 / 33) / 3)


def test_form_weighs_the_head_to_head_game_double_the_median_game():
    # Roster 1 scores 99 and beats roster 2 at 90. The median is 101.5, the mean of 101 and 102, so it loses there.
    # Newest back: median -1, then the head-to-head win. The streak is -1 of a cap of 9.
    # The weighted record is 2-1. All-play: it beats 90, 91, and 92, so 3-8.
    h = _built([_FILLERS | {1: 99.0, 2: 90.0, 3: 91.0, 4: 92.0}])
    streak = (-1 + 9) / 18
    assert _row(power_rankings(h, 1)[1], 1).values["form"] == pytest.approx((streak + 2 / 3 + 3 / 11) / 3)


def test_form_streak_is_zero_when_the_newest_game_is_a_tie():
    # Roster 1 wins both games in weeks 1 and 2. In week 3 it wins head to head, then ties the median:
    # rosters 1 and 4 are the 6th and 7th scores. The streak is 0. A streak that skipped the tie would be 4.
    win = _FILLERS | {1: 110.0, 2: 95.0, 3: 96.0, 4: 94.0}
    h = _built([win, win, win | {1: 102.5, 4: 102.5}])
    # The record is 5-0 with the tie as neither. All-play: 11-0, 11-0, then 5-5 with one tie.
    assert _row(power_rankings(h, 3)[3], 1).values["form"] == pytest.approx((0.5 + 1 + 27 / 32) / 3)


def test_margin_splits_equal_points_for_and_all_play():
    # Rosters 1 and 3 score the same, so points for and all-play are equal. Roster 1 wins by 40, roster 3 by 1.
    h = _built([_FILLERS | {1: 120.0, 2: 80.0, 3: 120.0, 4: 119.0}])
    rows = power_rankings(h, 1)[1]
    assert _row(rows, 1).values["scoring"] > _row(rows, 3).values["scoring"]


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


def test_power_score_weighs_form_most_and_scoring_second(fixture_raw_dir, fixture_history_root):
    # The league rule: standing 0.10, form 0.60, schedule played 0.10, scoring 0.20.
    for row in power_rankings(_history(fixture_raw_dir, fixture_history_root), 6)[6]:
        v = row.values
        expected = 0.10 * v["standing"] + 0.60 * v["form"] + 0.10 * v["schedule_played"] + 0.20 * v["scoring"]
        assert row.power_score == pytest.approx(expected)


def test_a_row_holds_the_head_to_head_and_the_median_record_of_the_form_window():
    # Week 1: roster 1 wins both games. Weeks 2 to 4: it wins head to head but loses the median game.
    # Week 5: it loses both. At week 5 the window is weeks 3 to 5: head to head 2-1, median 0-3.
    win = _FILLERS | {1: 110.0, 2: 95.0, 3: 96.0, 4: 94.0}
    split = win | {1: 99.0}
    h = _built([win, split, split, split, win | {1: 90.0}])
    row = _row(power_rankings(h, 5)[5], 1)
    assert (row.head_to_head, row.median, row.form_weeks) == ((2, 1), (0, 3), 3)


def test_the_form_window_is_short_in_the_first_weeks():
    win = _FILLERS | {1: 110.0, 2: 95.0, 3: 96.0, 4: 94.0}
    row = _row(power_rankings(_built([win]), 1)[1], 1)
    assert (row.head_to_head, row.median, row.form_weeks) == ((1, 0), (1, 0), 1)
