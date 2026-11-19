"""
Tests for the weekly odds of the season sim: the playoff odds, the bye odds, the status, the seed, and the swing.
They feed a small fixture league at the seam of season_sim and weekly_odds, as the weekly build reads them.
"""
from league.league_settings import LeagueSettings
from sim.season import season_sim, weekly_odds

SEASON = 2026
# The fixture league: 4 rosters, 2 weeks played, 2 weeks left, 2 playoff spots, 1 bye, 200 runs.
SPOTS, BYES, RUNS = 2, 1, 200
SCORES = {1: [120.0, 95.0], 2: [101.0, 110.0], 3: [88.0, 130.0], 4: [99.0, 85.0]}
RECORDS = {1: (3, 1, 215.0), 2: (2, 2, 211.0), 3: (2, 2, 218.0), 4: (1, 3, 184.0)}
REMAINING = {3: [(1, 2), (3, 4)], 4: [(1, 3), (2, 4)]}
EVEN = {rid: (2, 2, 200.0) for rid in (1, 2, 3, 4)}
FIXED_PAIRS = {3: [(1, 2), (3, 4)], 4: [(1, 2), (3, 4)]}


def _settings(spots: int = SPOTS, byes: int = BYES, last_regular_week: int = 4) -> LeagueSettings:
    return LeagueSettings(
        team_count=4, playoff_spots=spots, bye_count=byes, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=last_regular_week, reception_points=0.5, median_game=True,
    )


def _odds(scores=SCORES, records=RECORDS, remaining=REMAINING, week=2, runs=RUNS, settings=None, **kwargs):
    result = season_sim(scores, records, remaining, season=SEASON, week=week, settings=settings or _settings(),
                        runs=runs, **kwargs)
    return weekly_odds(result)


def _flat(scores: dict[int, float]) -> dict[int, list[float]]:
    """Two played weeks of one fixed score each, so every draw is that score."""
    return {rid: [s, s] for rid, s in scores.items()}


def test_same_random_seed_gives_the_same_odds_twice():
    assert _odds() == _odds()


def test_a_different_random_seed_gives_odds_within_a_few_points():
    # The random seed derives from the season and the week, so another week is another random seed.
    first, second = _odds(week=2, runs=1000), _odds(week=3, runs=1000)
    for rid in RECORDS:
        assert abs(first.teams[rid].playoff - second.teams[rid].playoff) <= 8


def test_the_weekly_odds_are_the_playoff_and_bye_odds_of_the_sim():
    result = season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(), runs=RUNS)
    odds = weekly_odds(result)
    assert {rid: (t.playoff, t.bye) for rid, t in odds.teams.items()} == {
        rid: (t.playoff, t.bye) for rid, t in result.teams.items()}


def test_both_games_count():
    # The head-to-head results are the same in both fixtures: 1 beats 2 and 3 beats 4.
    # Only the median game differs: roster 2 is above the median in the first and below it in the second.
    above = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    below = _odds(scores=_flat({1: 100.0, 2: 50.0, 3: 80.0, 4: 40.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert above.teams[2].playoff == 99
    assert below.teams[2].playoff == 1


def test_points_for_breaks_a_tie_on_wins():
    # Rosters 2 and 3 end with 6 wins each. Roster 2 draws more points, so it takes the last spot.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert result.teams[2].playoff == 99
    assert result.teams[3].playoff == 1


def test_roster_id_breaks_a_tie_on_wins_and_points_for():
    records = {1: (4, 0, 300.0), 2: (2, 2, 250.0), 3: (2, 2, 250.0), 4: (2, 2, 260.0)}
    result = _odds(records=records, remaining={}, week=4)
    assert [result.teams[rid].seed for rid in (1, 4, 2)] == [1, 2, None]
    assert result.teams[3].status == "out"


def test_a_roster_that_wins_every_drawn_game_lands_at_the_1_seed():
    # The draws are normal around a level shrunk toward the league average, so the gap must be wide for every win.
    scores = {**SCORES, 4: [1000.0, 1010.0]}
    result = _odds(scores=scores, records=EVEN)
    assert result.teams[4].seed == 1
    # The roster is open, so its playoff odds clamp to 99, and the bye odds cap there.
    assert result.teams[4].bye == 99


def test_the_bye_odds_never_read_above_the_playoff_odds():
    # Roster 1 takes the bye in every run, but it is open, so both numbers show 99.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert (result.teams[1].playoff, result.teams[1].bye) == (99, 99)
    assert all(t.bye <= t.playoff for t in _odds().teams.values())


def test_a_bye_of_0_needs_the_bye_to_be_gone():
    # With 1 week left roster 3 can reach 5 wins, short of the 7 of roster 1, so the bye is gone.
    # Its playoff spot is still open, since roster 2 holds the last spot at 5 wins.
    records = {1: (7, 1, 300.0), 2: (5, 3, 280.0), 3: (3, 5, 250.0), 4: (1, 7, 240.0)}
    result = _odds(records=records, remaining={5: [(1, 2), (3, 4)]}, week=4, settings=_settings(last_regular_week=5))
    assert result.teams[3].status == "open"
    assert result.teams[3].bye == 0
    assert all(t.bye >= 1 for rid, t in result.teams.items() if rid in (1, 2))


def test_a_sure_bye_shows_100():
    # With 1 week left no roster can reach the 8 wins of roster 1.
    records = {1: (8, 0, 300.0), 2: (5, 3, 280.0), 3: (3, 5, 250.0), 4: (0, 8, 240.0)}
    result = _odds(records=records, remaining={5: [(1, 2), (3, 4)]}, week=4, settings=_settings(last_regular_week=5))
    assert result.teams[1].bye == 100


def test_an_out_roster_shows_a_bye_of_0_and_no_seed():
    records = {1: (6, 0, 300.0), 2: (5, 1, 280.0), 3: (0, 6, 250.0), 4: (2, 4, 240.0)}
    result = _odds(records=records)
    assert result.teams[3].status == "out"
    assert (result.teams[3].playoff, result.teams[3].bye, result.teams[3].seed) == (0, 0, None)
    # Roster 4 is 3 wins back and can win 4 more, so it is open.
    assert result.teams[4].status == "open"


def test_a_4_win_lead_with_1_week_left_is_in():
    records = {1: (7, 1, 300.0), 2: (5, 3, 280.0), 3: (3, 5, 250.0), 4: (1, 7, 240.0)}
    result = _odds(records=records, remaining={5: [(1, 2), (3, 4)]}, week=4, settings=_settings(last_regular_week=5))
    assert (result.teams[1].status, result.teams[1].playoff) == ("in", 100)
    # Roster 2 leads roster 3 by 2 wins, and roster 3 can win 2 more, so roster 2 is not in yet.
    assert result.teams[2].status == "open"


def test_open_odds_clamp_to_1_to_99():
    # Roster 1 makes it in every run and roster 4 in none, but the plain check leaves both open.
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert (result.teams[1].status, result.teams[1].playoff) == ("open", 99)
    assert (result.teams[4].status, result.teams[4].playoff) == ("open", 1)


def test_the_seed_is_the_modal_seed_and_none_below_the_show_line():
    result = _odds(scores=_flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}), records=EVEN, remaining=FIXED_PAIRS)
    assert [result.teams[rid].seed for rid in (1, 2, 3, 4)] == [1, 2, None, None]


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
    by_pair = {(s.a, s.b): s for s in _odds(records=records).swings}
    assert (by_pair[(3, 4)].a_win, by_pair[(3, 4)].a_loss) == (0, 0)


def test_no_weeks_left_reads_the_final_table_with_no_swing():
    records = {1: (6, 2, 300.0), 2: (5, 3, 250.0), 3: (5, 3, 240.0), 4: (0, 8, 260.0)}
    result = _odds(records=records, remaining={}, week=4)
    assert result.swings == []
    assert {rid: t.status for rid, t in result.teams.items()} == {1: "in", 2: "in", 3: "out", 4: "out"}
    assert [result.teams[rid].playoff for rid in (1, 2, 3, 4)] == [100, 100, 0, 0]
    assert [result.teams[rid].seed for rid in (1, 2, 3, 4)] == [1, 2, None, None]
    assert [result.teams[rid].bye for rid in (1, 2, 3, 4)] == [100, 0, 0, 0]


def test_the_odds_sum_to_the_spots_times_100_within_rounding():
    total = sum(t.playoff for t in _odds().teams.values())
    # Each roster rounds by at most half a point, and a clamp moves it by at most 1 more.
    assert abs(total - SPOTS * 100) <= len(RECORDS)


# A projected total per roster per remaining week, far from each season average, so any shift shows in the odds.
PROJECTED = {1: {3: 60.0, 4: 60.0}, 2: {3: 140.0, 4: 140.0}, 3: {3: 70.0, 4: 150.0}, 4: {3: 160.0, 4: 90.0}}


def test_the_projections_move_the_odds():
    assert _odds(projected=PROJECTED) != _odds()


def test_no_projections_for_a_roster_or_a_week_gives_no_shift():
    assert _odds(projected={}) == _odds()
    flat = _flat({1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0})

    def odds(projected):
        return _odds(scores=flat, records=EVEN, remaining=FIXED_PAIRS, projected=projected)

    # A week 4 projection equal to the average of 70 is no shift, as no projection is.
    assert odds({4: {3: 400.0}}) == odds({4: {3: 400.0, 4: 70.0}})
    assert odds({4: {3: 400.0}}) != odds({4: {3: 400.0, 4: 400.0}})
