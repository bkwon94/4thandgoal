"""
The rules of the state of the league, on small hand-built leagues: the full record, points for and against, the
streak, the order, and the playoff odds of each team.
"""
from league.models import History, PastWeek
from midseason.state import Streak, league_state


def _week(number: int, scores: dict[int, float], pairs: list[tuple[int, int]]) -> PastWeek:
    return PastWeek(week=number, scores=scores, pairs=pairs, points={}, projections={}, stats={}, moves=[])


# Four teams over three weeks. The median of each week is the mean of the 2nd and 3rd scores.
HISTORY = History(week=3, weeks={
    # Median 95: 1 beats 2 and the median, 3 ties 4 and both lose to the median.
    1: _week(1, {1: 120.25, 2: 100.5, 3: 89.5, 4: 89.5}, [(1, 2), (3, 4)]),
    # Median 100: 1 beats 3, 2 beats 4.
    2: _week(2, {1: 110.0, 2: 105.0, 3: 95.0, 4: 80.0}, [(1, 3), (2, 4)]),
    # Median 100: 4 beats 1, 2 beats 3.
    3: _week(3, {1: 90.0, 2: 130.0, 3: 70.0, 4: 110.0}, [(1, 4), (2, 3)]),
})
NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four"}


def _rows(**kwargs):
    return {row.roster_id: row for row in league_state(HISTORY, 3, NAMES, **kwargs).teams}


def test_the_full_record_counts_the_median_game_and_a_tie():
    rows = _rows(playoff_odds={}, median_game=True)
    assert (rows[1].wins, rows[1].losses, rows[1].ties) == (4, 2, 0)
    assert (rows[3].wins, rows[3].losses, rows[3].ties) == (0, 5, 1)
    assert (rows[4].wins, rows[4].losses, rows[4].ties) == (2, 3, 1)


def test_a_league_with_no_median_game_counts_one_game_a_week():
    rows = _rows(playoff_odds={}, median_game=False)
    assert (rows[1].wins, rows[1].losses, rows[1].ties) == (2, 1, 0)
    assert (rows[3].wins, rows[3].losses, rows[3].ties) == (0, 2, 1)


def test_points_for_is_the_sum_of_the_weekly_scores_and_points_against_is_head_to_head_only():
    rows = _rows(playoff_odds={}, median_game=True)
    assert rows[1].points_for == 320.25
    assert rows[1].points_against == 100.5 + 95.0 + 110.0
    assert rows[3].points_against == 89.5 + 110.0 + 130.0


def test_the_streak_is_head_to_head_only_newest_week_back_and_a_tie_ends_it():
    rows = _rows(playoff_odds={}, median_game=True)
    assert rows[2].streak == Streak(kind="W", length=2)
    assert rows[1].streak == Streak(kind="L", length=1)
    assert rows[3].streak == Streak(kind="L", length=2)
    # Team 4 won week 3, lost week 2, and tied week 1, so its streak is one win.
    assert rows[4].streak == Streak(kind="W", length=1)


def test_the_streak_of_a_team_whose_last_game_was_a_tie_is_none():
    history = History(week=1, weeks={1: HISTORY.weeks[1]})
    rows = {row.roster_id: row for row in league_state(history, 1, NAMES, playoff_odds={}).teams}
    assert rows[3].streak is None


def test_the_rows_are_in_standings_order_most_wins_then_most_points_for():
    state = league_state(HISTORY, 3, NAMES, playoff_odds={})
    assert [(row.rank, row.roster_id) for row in state.teams] == [(1, 2), (2, 1), (3, 4), (4, 3)]


def test_each_row_takes_the_playoff_odds_that_the_app_hands_in():
    rows = _rows(playoff_odds={1: 88, 2: 97, 3: 2})
    assert (rows[1].playoff_odds, rows[2].playoff_odds, rows[3].playoff_odds) == (88, 97, 2)
    # A team with no odds in hand has none, not a 0.
    assert rows[4].playoff_odds is None


def test_the_state_counts_only_the_weeks_through_the_week_of_the_report():
    rows = {row.roster_id: row for row in league_state(HISTORY, 2, NAMES, playoff_odds={}).teams}
    assert rows[1].points_for == 230.25
    assert (rows[4].wins, rows[4].losses, rows[4].ties) == (0, 3, 1)
