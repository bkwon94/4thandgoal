"""
Tests for the playoff odds engine.
They feed a small fixture league at the engine seam and read the odds, the status, the seed, and the swing.
"""
import time

from cornerstone.odds import playoff_odds

SEASON = 2026
# The fixture league: 4 rosters, 2 weeks played, 2 weeks left, 2 playoff spots, 1 bye, 200 runs.
SPOTS, BYES, RUNS = 2, 1, 200
SCORES = {1: [120.0, 95.0], 2: [101.0, 110.0], 3: [88.0, 130.0], 4: [99.0, 85.0]}
RECORDS = {1: (3, 1, 215.0), 2: (2, 2, 211.0), 3: (2, 2, 218.0), 4: (1, 3, 184.0)}
REMAINING = {3: [(1, 2), (3, 4)], 4: [(1, 3), (2, 4)]}


def _odds(scores=SCORES, records=RECORDS, remaining=REMAINING, week=2, **kwargs):
    return playoff_odds(
        scores, records, remaining, season=SEASON, week=week,
        playoff_spots=SPOTS, bye_count=BYES, runs=RUNS, **kwargs,
    )


def _flat(scores: dict[int, float]) -> dict[int, list[float]]:
    """Two played weeks of one fixed score each, so every draw is that score."""
    return {rid: [s, s] for rid, s in scores.items()}


EVEN = {rid: (2, 2, 200.0) for rid in (1, 2, 3, 4)}
FIXED_PAIRS = {3: [(1, 2), (3, 4)], 4: [(1, 2), (3, 4)]}


def test_same_seed_gives_the_same_odds_twice():
    assert _odds() == _odds()


def test_a_different_seed_gives_odds_within_a_few_points():
    # The seed derives from the season and the week, so another week is another seed.
    first, second = _odds(week=2), _odds(week=3)
    for rid in RECORDS:
        assert abs(first.teams[rid].playoff - second.teams[rid].playoff) <= 15


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
    scores = {**SCORES, 4: [200.0, 210.0]}
    result = _odds(scores=scores, records=EVEN)
    assert result.teams[4].seed == 1
    assert result.teams[4].bye == 100


def test_the_bye_goes_to_the_top_seeds():
    records = {1: (4, 0, 300.0), 2: (3, 1, 250.0), 3: (2, 2, 250.0), 4: (1, 3, 260.0)}
    result = playoff_odds(
        SCORES, records, {}, season=SEASON, week=4, playoff_spots=SPOTS, bye_count=2, runs=RUNS,
    )
    assert [result.teams[rid].bye for rid in (1, 2, 3, 4)] == [100, 100, 0, 0]


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


def test_the_full_league_runs_in_under_10_seconds(fixture_raw_dir, fixture_history_root):
    from cornerstone.facts_league import season_records
    from cornerstone.history import load_history
    from cornerstone.sleeper import load_raw

    history = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    records = season_records(history, 6)
    scores = {rid: [history.weeks[n].scores[rid] for n in range(1, 7)] for rid in records}
    # Weeks 7 to 14 replay the pairs of weeks 1 to 6, then weeks 1 and 2, so the case has 8 full weeks.
    remaining = {7 + i: history.weeks[i % 6 + 1].pairs for i in range(8)}
    start = time.perf_counter()
    result = playoff_odds(scores, records, remaining, season=SEASON, week=6, playoff_spots=6, bye_count=2)
    assert time.perf_counter() - start < 10
    total = sum(t.playoff for t in result.teams.values())
    assert abs(total - 6 * 100) <= len(records)
