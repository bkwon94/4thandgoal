"""
The rules of the look ahead, on a small hand-built league: each team's games left with the opponents' records, the
win rate of the opponents, and the softest and the hardest schedule.
"""
from league.models import History, PastWeek
from midseason.look_ahead import look_ahead, look_ahead_facts
from midseason.state import league_state


def _week(number: int, scores: dict[int, float], pairs: list[tuple[int, int]]) -> PastWeek:
    return PastWeek(week=number, scores=scores, pairs=pairs, points={}, projections={}, stats={}, moves=[])


# Four teams over two weeks, with no median game. Team 1 is 2-0, team 2 is 1-1, team 3 is 1-1, and team 4 is 0-2.
HISTORY = History(week=2, weeks={
    1: _week(1, {1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}, [(1, 2), (3, 4)]),
    2: _week(2, {1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}, [(1, 3), (2, 4)]),
})
NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four"}
# The weeks left: team 4 meets team 1 twice, and team 1 meets team 4 twice.
SCHEDULE = {3: [(1, 4), (2, 3)], 4: [(4, 1), (3, 2)]}


def _look(schedule=SCHEDULE):
    state = league_state(HISTORY, 2, NAMES, playoff_odds={}, median_game=False)
    return look_ahead(state, schedule)


def test_each_team_has_its_games_left_with_the_opponent_and_the_opponent_s_record():
    teams = {team.roster_id: team for team in _look().teams}
    games = [(game.week, game.opponent, game.wins, game.losses) for game in teams[4].games]
    assert games == [(3, 1, 2, 0), (4, 1, 2, 0)]


def test_the_opponents_win_rate_is_the_sum_of_their_wins_over_the_sum_of_their_games():
    teams = {team.roster_id: team for team in _look().teams}
    assert teams[4].opponents_rate == 1.0
    assert teams[1].opponents_rate == 0.0
    assert teams[2].opponents_rate == 0.5


def test_the_softest_and_the_hardest_schedule_are_called_out():
    look = _look()
    assert (look.softest, look.hardest) == (1, 4)


def test_the_table_orders_the_teams_softest_schedule_first():
    rates = [team.opponents_rate or 0.0 for team in _look().teams]
    assert rates == sorted(rates)


def test_a_league_with_no_weeks_left_has_no_softest_or_hardest_schedule():
    look = _look({})
    assert (look.softest, look.hardest) == (None, None)
    assert all(team.games == [] and team.opponents_rate is None for team in look.teams)


def test_the_facts_name_the_rate_of_each_team_and_the_softest_and_the_hardest_schedule():
    facts = {f.id: f for f in look_ahead_facts(_look())}
    assert facts["LA.1.rate"].text == "One faces opponents with a 0 win rate in weeks 3 to 4, the softest schedule."
    assert facts["LA.4.rate"].text == "Four faces opponents with a 1 win rate in weeks 3 to 4, the hardest schedule."
    assert "2nd softest" in facts["LA.2.rate"].text or "2nd softest" in facts["LA.3.rate"].text
