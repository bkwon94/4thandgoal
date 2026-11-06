"""
The rules of Position top 10, on small hand-built leagues: the points in the league's own scoring, the positions the
league starts, the manager now or the "Free agent" tag, and the points per game.
"""
from league.models import History, PastWeek
from midseason.players import PlayerCard
from midseason.top10 import FREE_AGENT, position_top10

SCORING = {"pass_yd": 0.04, "pass_int": -2.0, "rec": 0.5, "rec_yd": 0.1, "def_int": 2.0}
NAMES = {1: "One", 2: "Two"}


def _card(pid: str, position: str) -> PlayerCard:
    return PlayerCard(player_id=pid, name=f"Player {pid}", position=position, nfl_team="BUF")


PLAYERS = {pid: _card(pid, position) for pid, position in
           (("qb1", "QB"), ("qb2", "QB"), ("wr1", "WR"), ("k1", "K"), ("def1", "DEF"))}


def _week(number: int, stats: dict[str, dict[str, float]]) -> PastWeek:
    return PastWeek(week=number, scores={1: 100.0, 2: 90.0}, pairs=[(1, 2)], points={}, projections={}, stats=stats,
                    moves=[])


HISTORY = History(week=2, weeks={
    1: _week(1, {"qb1": {"pass_yd": 300.0, "pass_int": 1.0, "gp": 1.0}, "qb2": {"pass_yd": 250.0, "gp": 1.0},
                 "wr1": {"rec": 6.0, "rec_yd": 80.0, "gp": 1.0}, "k1": {"fgm": 3.0, "gp": 1.0},
                 "def1": {"def_int": 2.0, "gp": 1.0}}),
    # qb1 has a bye in week 2.
    2: _week(2, {"qb2": {"pass_yd": 200.0, "gp": 1.0}, "wr1": {"rec": 4.0, "rec_yd": 40.0, "gp": 1.0}}),
})


def _top(positions, owners=None, through=2):
    top = position_top10(HISTORY, through, PLAYERS, SCORING, positions, owners or {}, NAMES)
    return {board.position: board.players for board in top.positions}


def test_the_points_are_the_sum_of_each_week_in_the_league_scoring_and_the_points_per_game_skip_a_bye():
    qbs = _top(("QB",))["QB"]
    assert [(p.rank, p.player_id, p.points, p.games, p.points_per_game) for p in qbs] == [
        (1, "qb2", 18.0, 2, 9.0), (2, "qb1", 10.0, 1, 10.0)]


def test_the_boards_are_the_positions_the_league_starts_in_lineup_order():
    # A league with no DEF slot has no DEF board, and no league here starts a kicker.
    assert list(_top(("QB", "WR"))) == ["QB", "WR"]
    assert list(_top(("QB", "WR", "DEF"))) == ["QB", "WR", "DEF"]


def test_each_row_shows_the_manager_now_or_the_free_agent_tag():
    qbs = _top(("QB",), owners={"qb1": 2})["QB"]
    by_id = {p.player_id: p for p in qbs}
    assert (by_id["qb1"].roster_id, by_id["qb1"].manager, by_id["qb1"].tag) == (2, "Two", None)
    assert (by_id["qb2"].roster_id, by_id["qb2"].manager, by_id["qb2"].tag) == (None, None, FREE_AGENT)


def test_a_board_holds_at_most_10_players():
    many = {f"wr{i}": _card(f"wr{i}", "WR") for i in range(12)}
    history = History(week=1, weeks={1: _week(1, {pid: {"rec": float(i + 1), "gp": 1.0}
                                                  for i, pid in enumerate(many)})})
    top = position_top10(history, 1, many, SCORING, ("WR",), {}, NAMES)
    assert [p.player_id for p in top.positions[0].players] == [f"wr{i}" for i in range(11, 1, -1)]


def test_the_board_counts_only_the_weeks_through_the_week_of_the_report_and_a_tie_goes_by_name():
    qbs = _top(("QB",), through=1)["QB"]
    assert [(p.player_id, p.points) for p in qbs] == [("qb1", 10.0), ("qb2", 10.0)]
