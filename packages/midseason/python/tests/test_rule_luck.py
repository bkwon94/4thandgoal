"""
The rules of Schedule luck and the Schedule swap, on small hand-built leagues: All-play wins, a tie as half a win, the
self-meet rule of the swap, the median game of the swap, points against, and the close-game record.
"""
from league.models import History, PastWeek
from midseason.luck import SwapCell, schedule_luck, swap_rankings, with_swap_callouts
from midseason.state import league_state


def _week(number: int, scores: dict[int, float], pairs: list[tuple[int, int]]) -> PastWeek:
    return PastWeek(week=number, scores=scores, pairs=pairs, points={}, projections={}, stats={}, moves=[])


# Four teams over two weeks. Week 1: 1 beats 2, and 3 ties 4. Week 2: 3 beats 1, and 2 beats 4.
HISTORY = History(week=2, weeks={
    # Median 85.
    1: _week(1, {1: 100.0, 2: 90.0, 3: 80.0, 4: 80.0}, [(1, 2), (3, 4)]),
    # Median 90.
    2: _week(2, {1: 70.0, 2: 120.0, 3: 110.0, 4: 60.0}, [(1, 3), (2, 4)]),
})
NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four"}


def _luck(history: History = HISTORY, through: int = 2, *, median_game: bool = True):
    state = league_state(history, through, NAMES, playoff_odds={}, median_game=median_game)
    return state, schedule_luck(history, through, state, median_game=median_game)


def _teams(**kwargs):
    return {team.roster_id: team for team in _luck(**kwargs)[1].teams}


def test_all_play_wins_sum_the_weekly_all_play_rates_and_a_tie_counts_half():
    teams = _teams()
    # Team 1 beats all 3 teams in week 1 and only team 4 in week 2.
    assert teams[1].all_play_wins == 1.33
    # Team 3 ties team 4 in week 1, then beats teams 1 and 4 in week 2: 0.5 / 3 + 2 / 3.
    assert teams[3].all_play_wins == 0.83


def test_schedule_luck_is_head_to_head_wins_minus_all_play_wins_and_a_tie_counts_half():
    teams = _teams()
    assert teams[3].head_to_head_wins == 1.5
    assert teams[3].schedule_luck == 0.67
    assert teams[1].schedule_luck == -0.33


def test_the_median_game_stays_out_of_schedule_luck():
    assert _teams(median_game=True)[3].schedule_luck == _teams(median_game=False)[3].schedule_luck


def test_the_table_ranks_every_team_by_schedule_luck_most_first():
    _, luck = _luck()
    values = [team.schedule_luck for team in luck.teams]
    assert len(values) == 4 and values == sorted(values, reverse=True)


def _cell(swap, row: int, schedule_of: int) -> SwapCell:
    return next(cell for cell in next(r for r in swap.rows if r.roster_id == row).cells if cell.schedule_of == schedule_of)


def test_in_the_week_that_the_other_team_played_the_row_team_the_row_team_plays_that_team():
    _, luck = _luck(median_game=False)
    # Team 1 with the schedule of team 3: team 4 in week 1, then team 3 itself in week 2, where it loses 70 to 110.
    assert _cell(luck.swap, 1, 3) == SwapCell(schedule_of=3, wins=1, losses=1, ties=0)


def test_a_tie_in_the_swap_counts_as_a_tie():
    _, luck = _luck(median_game=False)
    # Team 4 with the schedule of team 3: team 3 itself in week 1 at 80 to 80, then team 1 in week 2 at 60 to 70.
    assert _cell(luck.swap, 4, 3) == SwapCell(schedule_of=3, wins=0, losses=1, ties=1)


def test_a_swap_cell_keeps_the_row_team_s_own_median_results():
    _, luck = _luck(median_game=True)
    # Team 1 beats the median of week 1 and loses to the median of week 2.
    assert _cell(luck.swap, 1, 3) == SwapCell(schedule_of=3, wins=2, losses=2, ties=0)


def test_the_diagonal_of_the_swap_is_the_full_record_of_the_standings():
    for median_game in (True, False):
        state, luck = _luck(median_game=median_game)
        for team in state.teams:
            assert _cell(luck.swap, team.roster_id, team.roster_id) == SwapCell(
                schedule_of=team.roster_id, wins=team.wins, losses=team.losses, ties=team.ties)


def test_the_rows_and_the_columns_of_the_swap_are_in_standings_order():
    state, luck = _luck()
    order = [team.roster_id for team in state.teams]
    assert [row.roster_id for row in luck.swap.rows] == order
    assert all([cell.schedule_of for cell in row.cells] == order for row in luck.swap.rows)


def test_each_team_gets_the_best_schedule_that_it_missed_and_a_tie_goes_to_the_higher_standings_place():
    _, luck = _luck(median_game=False)
    best = {callout.roster_id: (callout.schedule_of, callout.wins, callout.losses, callout.ties)
            for callout in luck.swap.best_missed}
    # The standings order is 2, 3, 1, 4. Team 2 met team 1 in week 1, so team 1 with the schedule of team 2 plays
    # team 2 and wins, then plays team 4 and wins.
    assert best[1] == (2, 2, 0, 0)
    # Team 2 is 2-0 with the schedule of team 3 and of team 4. Team 3 sits higher in the standings.
    assert best[2] == (3, 2, 0, 0)
    # Team 3 is 1-1 with the schedule of team 1 and of team 2. Team 2 sits higher in the standings.
    assert best[3] == (2, 1, 1, 0)
    assert best[4] == (3, 0, 1, 1)


def test_the_team_with_the_most_records_better_than_its_own_is_called_out():
    _, luck = _luck(median_game=False)
    # Team 2 is 1-1 for real and 2-0 with the schedule of team 3 and of team 4.
    assert luck.swap.most_better is not None
    assert (luck.swap.most_better.roster_id, luck.swap.most_better.count) == (2, 2)


def test_the_biggest_miss_is_the_team_with_the_most_wins_to_gain_from_its_best_schedule():
    _, luck = _luck(median_game=False)
    # Teams 2 and 1 are each 1-1 for real and 2-0 with their best schedule. Team 2 sits higher in the standings.
    # Team 3 gains nothing from its best schedule, so it is in no ranking of the biggest miss.
    most_better, biggest_miss = swap_rankings(luck.swap)
    assert biggest_miss == [2, 1]
    assert most_better[0] == 2
    assert luck.swap.biggest_miss is not None
    assert (luck.swap.biggest_miss.roster_id, luck.swap.biggest_miss.gain, luck.swap.biggest_miss.place) == (2, 1, 1)


def test_the_spread_rule_moves_a_swap_callout_to_the_next_team_with_its_place():
    _, luck = _luck(median_game=False)
    moved = with_swap_callouts(luck, most_better=(1, 2), biggest_miss=(1, 2))
    assert moved.swap.most_better is not None and moved.swap.biggest_miss is not None
    assert (moved.swap.most_better.roster_id, moved.swap.most_better.place) == (1, 2)
    assert (moved.swap.biggest_miss.roster_id, moved.swap.biggest_miss.schedule_of) == (1, 2)
    assert with_swap_callouts(luck, most_better=None, biggest_miss=None).swap.most_better is None


def test_each_team_has_points_against_with_its_rank_most_first():
    teams = _teams()
    # Team 1 faced 90 and 110, team 3 faced 80 and 70, team 4 faced 80 and 120, team 2 faced 100 and 60.
    assert (teams[1].points_against, teams[1].points_against_rank) == (200.0, 1)
    assert (teams[4].points_against, teams[4].points_against_rank) == (200.0, 1)
    assert (teams[3].points_against, teams[3].points_against_rank) == (150.0, 4)


def test_a_close_game_is_a_head_to_head_margin_under_5_points():
    history = History(week=1, weeks={1: _week(1, {1: 100.0, 2: 95.1, 3: 80.0, 4: 75.0}, [(1, 2), (3, 4)])})
    state = league_state(history, 1, NAMES, playoff_odds={})
    teams = {team.roster_id: team for team in schedule_luck(history, 1, state).teams}
    assert (teams[1].close_wins, teams[1].close_losses, teams[1].close_ties) == (1, 0, 0)
    assert (teams[2].close_wins, teams[2].close_losses, teams[2].close_ties) == (0, 1, 0)
    # A margin of exactly 5 is not close.
    assert (teams[3].close_wins, teams[3].close_losses) == (0, 0)
    # A tie is the closest game.
    tied = {team.roster_id: team for team in _luck()[1].teams}
    assert tied[3].close_ties == 1


def test_a_week_with_no_score_for_a_team_does_not_count():
    history = History(week=2, weeks={
        1: HISTORY.weeks[1],
        2: _week(2, {1: 70.0, 3: 110.0}, [(1, 3)]),
    })
    teams = _teams(history=history, median_game=False)
    # Team 2 has no score in week 2, so its All-play wins hold week 1 only: it beats teams 3 and 4.
    assert teams[2].all_play_wins == 0.67
    # Team 1 meets only team 3 in week 2, so that week is one all-play game.
    assert teams[1].all_play_wins == 1.0


def _ends(swap, roster_id: int):
    row = next(row for row in swap.best_and_worst if row.roster_id == roster_id)
    return row.best, row.worst


def test_each_team_gets_its_best_and_worst_schedule_and_a_tie_keeps_every_schedule_in_standings_order():
    _, luck = _luck(median_game=False)
    # The standings order is 2, 3, 1, 4. Team 2 is 1-1 for real, 2-0 with the schedules of teams 3 and 4, and 1-1
    # with the schedule of team 1.
    best, worst = _ends(luck.swap, 2)
    assert (best.schedules, best.wins, best.losses, best.ties) == ([3, 4], 2, 0, 0)
    assert (worst.schedules, worst.wins, worst.losses, worst.ties) == ([1], 1, 1, 0)
    # Team 3 is 1-1 with the schedule of team 1 and of team 2. With the schedule of team 4, it ties team 4 in week 1
    # and loses to team 2 in week 2.
    best, worst = _ends(luck.swap, 3)
    assert (best.schedules, best.wins, best.losses) == ([2, 1], 1, 1)
    assert (worst.schedules, worst.wins, worst.losses, worst.ties) == ([4], 0, 1, 1)


def test_the_rows_of_best_and_worst_sort_by_the_spread_most_first_and_a_tie_keeps_the_standings_order():
    _, luck = _luck(median_game=False)
    # Teams 2 and 1 each have a spread of 1 win, and teams 3 and 4 a spread of half a win. The standings order is
    # 2, 3, 1, 4.
    assert [row.roster_id for row in luck.swap.best_and_worst] == [2, 1, 3, 4]


def test_the_worked_example_is_the_luckiest_team_in_its_week_with_the_most_teams_outscored():
    _, luck = _luck()
    example = luck.example
    assert example is not None
    # Team 3 has the most Schedule luck. It ties team 4 in week 1, then outscores teams 1 and 4 in week 2.
    assert (example.roster_id, example.name, example.week, example.score) == (3, "Three", 2, 110.0)
    assert (example.outscored, example.others, example.week_wins) == (2, 3, 0.67)
    # Over the 2 weeks, a tie counts half: 0.5 + 2 of 6.
    assert (example.season_outscored, example.season_games) == (2.5, 6)
    assert (example.all_play_wins, example.head_to_head_wins, example.schedule_luck) == (0.83, 1.5, 0.67)


def test_a_tie_of_weeks_in_the_worked_example_goes_to_the_first_week():
    history = History(week=2, weeks={
        1: _week(1, {1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}, [(1, 2), (3, 4)]),
        2: _week(2, {1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0}, [(1, 3), (2, 4)]),
    })
    _, luck = _luck(history=history)
    assert luck.example is not None and luck.example.week == 1


def test_schedule_luck_counts_the_weeks_of_its_head_to_head_games():
    # The page says the count of games of each table in plain words.
    assert _luck()[1].weeks == 2
