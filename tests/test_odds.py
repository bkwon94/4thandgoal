"""
Tests for the playoff odds engine.
They feed a small fixture league at the engine seam and read the odds, the status, the seed, and the swing.
"""
import time
from pathlib import Path

import pytest

from cornerstone.config import cornerstone_config
from cornerstone.odds import playoff_odds

CONFIG = cornerstone_config()

SEASON = 2026
# The fixture league: 4 rosters, 2 weeks played, 2 weeks left, 2 playoff spots, 1 bye, 200 runs.
SPOTS, BYES, RUNS = 2, 1, 200
# The fixture league is smaller than Cornerstone, so its config has its own playoff spots and byes.
SMALL = cornerstone_config().model_copy(update={"playoff_spots": SPOTS, "bye_count": BYES})
SCORES = {1: [120.0, 95.0], 2: [101.0, 110.0], 3: [88.0, 130.0], 4: [99.0, 85.0]}
RECORDS = {1: (3, 1, 215.0), 2: (2, 2, 211.0), 3: (2, 2, 218.0), 4: (1, 3, 184.0)}
REMAINING = {3: [(1, 2), (3, 4)], 4: [(1, 3), (2, 4)]}


def _odds(scores=SCORES, records=RECORDS, remaining=REMAINING, week=2, runs=RUNS, **kwargs):
    return playoff_odds(
        scores, records, remaining, season=SEASON, week=week,
        config=SMALL, runs=runs, **kwargs,
    )


def _flat(scores: dict[int, float]) -> dict[int, list[float]]:
    """Two played weeks of one fixed score each, so every draw is that score."""
    return {rid: [s, s] for rid, s in scores.items()}


EVEN = {rid: (2, 2, 200.0) for rid in (1, 2, 3, 4)}
FIXED_PAIRS = {3: [(1, 2), (3, 4)], 4: [(1, 2), (3, 4)]}


def test_same_random_seed_gives_the_same_odds_twice():
    assert _odds() == _odds()


def test_the_dict_order_of_the_inputs_does_not_change_the_odds():
    def backward(d):
        return dict(reversed(list(d.items())))

    assert _odds(backward(SCORES), backward(RECORDS), backward(REMAINING)) == _odds()


def test_a_different_random_seed_gives_odds_within_a_few_points():
    # The random seed derives from the season and the week, so another week is another random seed.
    first, second = _odds(week=2, runs=1000), _odds(week=3, runs=1000)
    for rid in RECORDS:
        assert abs(first.teams[rid].playoff - second.teams[rid].playoff) <= 8


def test_both_games_count():
    # The head-to-head results are the same in both fixtures: 1 beats 2 and 3 beats 4.
    # Only the median game differs: roster 2 is above the median in the first and below it in the second.
    above = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    below = _odds(scores=_flat({1: 100.0, 2: 50.0, 3: 80.0, 4: 40.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert above.teams[2].playoff != below.teams[2].playoff
    assert above.teams[2].playoff == 99
    assert below.teams[2].playoff == 1


def test_points_for_breaks_a_tie_on_wins():
    # Rosters 2 and 3 end with 6 wins each. Roster 2 draws more points, so it takes the last spot.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert result.teams[2].playoff == 99
    assert result.teams[3].playoff == 1


def test_roster_id_breaks_a_tie_on_wins_and_points_for():
    records = {1: (4, 0, 300.0), 2: (2, 2, 250.0), 3: (2, 2, 250.0), 4: (2, 2, 260.0)}
    result = _odds(records=records, remaining={})
    assert [result.teams[rid].seed for rid in (1, 4, 2)] == [1, 2, None]
    assert result.teams[3].status == "out"


def test_a_roster_that_wins_every_drawn_game_lands_at_the_1_seed():
    # The draws are normal around a level shrunk toward the league average, so the gap must be wide for every win.
    scores = {**SCORES, 4: [1000.0, 1010.0]}
    result = _odds(scores=scores, records=EVEN)
    assert result.teams[4].seed == 1
    # The roster is open, so its playoff odds clamp to 99, and the bye odds cap there.
    assert result.teams[4].bye == 99


def test_the_bye_goes_to_the_top_seeds():
    records = {1: (4, 0, 300.0), 2: (3, 1, 250.0), 3: (2, 2, 250.0), 4: (1, 3, 260.0)}
    result = playoff_odds(
        SCORES, records, {}, season=SEASON, week=4, config=SMALL.model_copy(update={"bye_count": 2}), runs=RUNS,
    )
    assert [result.teams[rid].bye for rid in (1, 2, 3, 4)] == [100, 100, 0, 0]


def test_the_bye_odds_never_read_above_the_playoff_odds():
    # Roster 1 takes the bye in every run, but it is open, so both numbers show 99.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert (result.teams[1].playoff, result.teams[1].bye) == (99, 99)
    assert all(t.bye <= t.playoff for t in _odds().teams.values())


def test_a_bye_of_0_needs_the_bye_to_be_gone():
    # With 1 week left roster 3 can reach 5 wins, short of the 7 of roster 1, so the bye is gone.
    # Its playoff spot is still open, since roster 2 holds the last spot at 5 wins.
    records = {1: (7, 1, 300.0), 2: (5, 3, 280.0), 3: (3, 5, 250.0), 4: (1, 7, 240.0)}
    result = _odds(records=records, remaining={5: [(1, 2), (3, 4)]}, week=4)
    assert result.teams[3].status == "open"
    assert result.teams[3].bye == 0
    assert all(t.bye >= 1 for rid, t in result.teams.items() if rid in (1, 2))


def test_a_roster_the_runs_never_give_a_bye_shows_1_while_it_can_catch_the_bye():
    # Roster 1 takes the bye in every run, but every roster can still reach its wins.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert [result.teams[rid].bye for rid in (2, 3, 4)] == [1, 1, 1]


def test_a_sure_bye_shows_100():
    # With 1 week left no roster can reach the 8 wins of roster 1.
    records = {1: (8, 0, 300.0), 2: (5, 3, 280.0), 3: (3, 5, 250.0), 4: (0, 8, 240.0)}
    result = _odds(records=records, remaining={5: [(1, 2), (3, 4)]}, week=4)
    assert result.teams[1].bye == 100


def test_a_roster_that_is_in_with_an_open_bye_shows_1_to_99():
    # Rosters 1 and 2 are in and play each other, so the runs give the bye to roster 1 every time.
    records = {1: (7, 1, 300.0), 2: (7, 1, 280.0), 3: (2, 6, 250.0), 4: (1, 7, 240.0)}
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=records,
                   remaining={5: [(1, 2), (3, 4)]}, week=4)
    assert (result.teams[1].status, result.teams[2].status) == ("in", "in")
    assert (result.teams[1].bye, result.teams[2].bye) == (99, 1)


def test_an_out_roster_shows_a_bye_of_0():
    records = {1: (6, 0, 300.0), 2: (5, 1, 280.0), 3: (0, 6, 250.0), 4: (2, 4, 240.0)}
    result = _odds(records=records)
    assert result.teams[3].status == "out"
    assert result.teams[3].bye == 0


def test_an_odd_count_of_rosters_fails_with_a_clear_message():
    records = {rid: RECORDS[rid] for rid in (1, 2, 3)}
    with pytest.raises(ValueError, match="even count of rosters"):
        _odds(scores={rid: SCORES[rid] for rid in (1, 2, 3)}, records=records, remaining={3: [(1, 2)]})


def test_a_4_win_lead_with_1_week_left_is_in():
    records = {1: (7, 1, 300.0), 2: (5, 3, 280.0), 3: (3, 5, 250.0), 4: (1, 7, 240.0)}
    result = _odds(records=records, remaining={5: [(1, 2), (3, 4)]}, week=4)
    assert result.teams[1].status == "in"
    assert result.teams[1].playoff == 100
    # Roster 2 leads roster 3 by 2 wins, and roster 3 can win 2 more, so roster 2 is not in yet.
    assert result.teams[2].status == "open"


def test_5_wins_back_with_2_weeks_left_is_out():
    records = {1: (6, 0, 300.0), 2: (5, 1, 280.0), 3: (0, 6, 250.0), 4: (2, 4, 240.0)}
    result = _odds(records=records)
    assert result.teams[3].status == "out"
    assert result.teams[3].playoff == 0
    assert result.teams[3].seed is None
    # Roster 4 is 3 wins back and can win 4 more, so it is open.
    assert result.teams[4].status == "open"


def test_open_odds_clamp_to_1_to_99():
    # Roster 1 makes it in every run and roster 4 in none, but the plain check leaves both open.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert result.teams[1].status == "open"
    assert result.teams[1].playoff == 99
    assert result.teams[4].status == "open"
    assert result.teams[4].playoff == 1


def test_the_seed_is_the_modal_seed_and_none_below_the_show_line():
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert result.teams[1].seed == 1
    assert result.teams[2].seed == 2
    assert result.teams[3].seed is None
    assert result.teams[4].seed is None


def test_the_swing_splits_the_runs_by_the_next_head_to_head_game():
    result = _odds()
    assert [(s.a, s.b) for s in result.swings] == [(1, 2), (3, 4)]
    # The game matters to roster 3, so its halves differ. A win never lowers a side's odds.
    assert result.swings[1].a_win > result.swings[1].a_loss
    for swing in result.swings:
        assert swing.a_win >= swing.a_loss
        assert swing.b_win >= swing.b_loss
        for odds in (swing.a_win, swing.a_loss, swing.b_win, swing.b_loss):
            assert 1 <= odds <= 99


def test_the_swing_ignores_the_median_game():
    # Roster 1 always beats roster 2 head to head, so no run falls in the other half.
    # The other half falls back to the full odds, and the median game does not split the runs.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    swing = result.swings[0]
    assert (swing.a_win, swing.a_loss) == (99, 99)
    assert (swing.b_win, swing.b_loss) == (99, 99)


def test_a_side_that_is_in_or_out_shows_100_or_0_in_both_halves():
    records = {1: (6, 0, 300.0), 2: (5, 1, 280.0), 3: (0, 6, 250.0), 4: (2, 4, 240.0)}
    result = _odds(records=records)
    by_pair = {(s.a, s.b): s for s in result.swings}
    assert (by_pair[(3, 4)].a_win, by_pair[(3, 4)].a_loss) == (0, 0)


def test_no_weeks_left_skips_the_runs_and_reads_the_final_table():
    records = {1: (6, 2, 300.0), 2: (5, 3, 250.0), 3: (5, 3, 240.0), 4: (0, 8, 260.0)}
    result = _odds(records=records, remaining={}, week=4)
    assert result.swings == []
    assert {rid: t.status for rid, t in result.teams.items()} == {1: "in", 2: "in", 3: "out", 4: "out"}
    assert [result.teams[rid].playoff for rid in (1, 2, 3, 4)] == [100, 100, 0, 0]
    assert [result.teams[rid].seed for rid in (1, 2, 3, 4)] == [1, 2, None, None]
    assert [result.teams[rid].bye for rid in (1, 2, 3, 4)] == [100, 0, 0, 0]


def test_the_odds_sum_to_the_spots_times_100_within_rounding():
    result = _odds()
    total = sum(t.playoff for t in result.teams.values())
    # Each roster rounds by at most half a point, and a clamp moves it by at most 1 more.
    assert abs(total - SPOTS * 100) <= len(RECORDS)


# A projected total per roster per remaining week, far from each season average, so any shift shows in the odds.
PROJECTED = {1: {3: 60.0, 4: 60.0}, 2: {3: 140.0, 4: 140.0}, 3: {3: 70.0, 4: 150.0}, 4: {3: 160.0, 4: 90.0}}


def test_the_odds_at_projection_weight_0_equal_the_odds_with_no_projections():
    plain = _odds()
    assert _odds(projected=PROJECTED, projection_weight=0) == plain
    # The odds of the 4-team fixture with no projections, at this seed.
    assert {rid: (t.playoff, t.bye, t.seed) for rid, t in plain.teams.items()} == {
        1: (76, 45, 1), 2: (57, 26, 2), 3: (55, 28, 1), 4: (13, 2, None)}
    assert [(s.a_win, s.a_loss, s.b_win, s.b_loss) for s in plain.swings] == [(95, 53, 82, 35), (73, 21, 34, 2)]


def test_the_projections_move_the_odds():
    assert _odds(projected=PROJECTED) != _odds()


def test_at_projection_weight_1_a_roster_draws_its_projection():
    # Roster 4 always scores 70 in the past, so at weight 1 every draw is its projection of 200.
    flat = _flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0})
    assert _odds(scores=flat, records=EVEN, remaining=FIXED_PAIRS).teams[4].playoff == 1
    result = _odds(scores=flat, records=EVEN, remaining=FIXED_PAIRS, projected={4: {3: 200.0, 4: 200.0}},
                   projection_weight=1)
    assert result.teams[4].playoff == 99
    assert result.teams[4].seed == 1


def test_no_projections_for_a_roster_or_a_week_gives_no_shift():
    assert _odds(projected={}) == _odds()
    flat = _flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0})
    # Roster 4 has a projection for week 3 only. A week 4 projection equal to its average of 70 is no shift too.
    def odds(projected):
        return _odds(scores=flat, records=EVEN, remaining=FIXED_PAIRS, projected=projected, projection_weight=1)

    assert odds({4: {3: 200.0}}) == odds({4: {3: 200.0, 4: 70.0}})
    assert odds({4: {3: 200.0}}) != odds({4: {3: 200.0, 4: 200.0}})


def test_the_full_league_runs_in_under_10_seconds(fixture_raw_dir, fixture_history_root):
    from cornerstone.history import load_history
    from cornerstone.provider.sleeper import load_raw
    from cornerstone.standings_table import season_records

    history = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    records = season_records(history, 6)
    scores = {rid: [history.weeks[n].scores[rid] for n in range(1, 7)] for rid in records}
    # Weeks 7 to 14 replay the pairs of weeks 1 to 6, then weeks 1 and 2, so the case has 8 full weeks.
    remaining = {7 + i: history.weeks[i % 6 + 1].pairs for i in range(8)}
    start = time.perf_counter()
    result = playoff_odds(scores, records, remaining, season=SEASON, week=6, config=CONFIG)
    assert time.perf_counter() - start < 10
    total = sum(t.playoff for t in result.teams.values())
    assert abs(total - CONFIG.playoff_spots * 100) <= len(records)


def test_a_wide_spread_of_past_scores_gives_no_better_odds_than_a_narrow_spread():
    # Roster 2 averages 105.5 in both leagues. Only the spread of its two past scores differs.
    wide = _odds(scores={**SCORES, 2: [75.5, 135.5]}, runs=2000).teams[2].playoff
    narrow = _odds(scores={**SCORES, 2: [104.5, 106.5]}, runs=2000).teams[2].playoff
    assert abs(wide - narrow) <= 5


def test_the_shrink_pulls_a_roster_far_above_the_league_average_down():
    # Roster 4 trails on wins but scores far above the league, so its odds rest on its level.
    scores = {**SCORES, 4: [150.0, 160.0]}
    shrunk = _odds(scores=scores, runs=2000).teams[4].playoff
    raw = _odds(scores=scores, runs=2000, shrink_weeks=0).teams[4].playoff
    assert shrunk < raw


# The week 7 Level column of ticket 01 of odds-level: the playoff odds of the prototype on the saved data.
WEEK_7_LEVEL = {
    "Lil Fridge": 94, "Bo Girds": 94, "London Cooking": 94, "All You Need Is Love": 71,
    "Maye d'force B with U": 61, "Brock 'N' Roll": 57, "Return of T Mac": 34, "Amon-Ra Dawg Your Team": 53,
    "Unsolicited Dak Picks": 25, "behold the lamb": 16,
}
WEEK_7_RAW = Path(__file__).parent.parent / "data" / "2026" / "week-07" / "raw"


@pytest.mark.skipif(not WEEK_7_RAW.is_dir(), reason="no saved week 7 data")
def test_the_week_7_odds_match_the_prototype_within_3_points():
    from cornerstone.history import load_history
    from cornerstone.parse import parse_week
    from cornerstone.provider.sleeper import load_raw
    from cornerstone.sheet.base import odds_inputs, projected_totals, week_odds

    raw = load_raw(WEEK_7_RAW)
    week = parse_week(raw)
    history = load_history(WEEK_7_RAW.parent.parent / "history", raw, week=7)
    result = week_odds(week, history, odds_inputs(week, history, CONFIG), projected_totals(week, CONFIG), CONFIG)
    assert result is not None
    # The names on Sleeper use curly quotes, and the ticket table uses straight quotes.
    names = {rid: t.name.replace("‘", "'").replace("’", "'") for rid, t in week.teams.items()}
    odds = {names[rid]: t.playoff for rid, t in result.teams.items()}
    for name, level in WEEK_7_LEVEL.items():
        assert abs(odds[name] - level) <= 3, name
