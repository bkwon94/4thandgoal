"""
The rules of the players to watch, on small hand-built leagues: Due to rise and Due to fall from the Expected gap over
the whole season with the 4-game floor, and Grab him now from the projections of the rest of the regular season.
"""
from league.models import ExpectedGame, History, PastWeek
from midseason.players import PlayerCard
from midseason.watch import players_to_watch

SCORING = {"rec": 1.0}
NAMES = {1: "One", 2: "Two"}


def _card(pid: str, position: str = "WR") -> PlayerCard:
    return PlayerCard(player_id=pid, name=f"Player {pid}", position=position, nfl_team="SEA")


def _week(number: int, stats: dict[str, dict[str, float]]) -> PastWeek:
    return PastWeek(week=number, scores={1: 100.0, 2: 90.0}, pairs=[(1, 2)], points={}, projections={}, stats=stats,
                    moves=[])


def _league(actual: dict[str, list[float]], expected: dict[str, list[float]]):
    """A history of 5 weeks: each player scores `actual` in weeks 1 on, and his expected points are `expected`."""
    weeks = {number: _week(number, {pid: {"rec": points[number - 1]} for pid, points in actual.items()
                                    if number <= len(points)}) for number in range(1, 6)}
    games = {pid: [ExpectedGame(week=i + 1, game_id=f"g{i + 1}", expected=e) for i, e in enumerate(points)]
             for pid, points in expected.items()}
    return History(week=5, weeks=weeks), games


def _watch(actual, expected, owners, players=None, ahead=None, through=5):
    history, games = _league(actual, expected)
    cards = players or {pid: _card(pid) for pid in {*actual, *(owners or {})}}
    return players_to_watch(history, through, cards, SCORING, games, owners, NAMES, ahead=ahead or {},
                            last_regular_week=8, positions=("QB", "RB", "WR", "TE"))


def test_due_to_rise_and_due_to_fall_take_the_furthest_gaps_under_and_over_zero():
    actual = {"up": [4.0] * 4, "down": [10.0] * 4, "flat": [5.0] * 4, "low": [3.0] * 4}
    expected = {"up": [8.0] * 4, "down": [5.0] * 4, "flat": [5.0] * 4, "low": [4.0] * 4}
    watch = _watch(actual, expected, {pid: 1 for pid in actual})
    assert [(p.player_id, p.gap, p.games) for p in watch.due_to_rise] == [("up", -4.0, 4), ("low", -1.0, 4)]
    assert [(p.player_id, p.gap) for p in watch.due_to_fall] == [("down", 5.0)]


def test_a_player_needs_4_games_or_more_for_due_to_rise_and_due_to_fall():
    # "three" has the largest gaps but only 3 games, so neither list names him.
    actual = {"three": [0.0] * 3, "four": [2.0] * 4, "hot3": [20.0] * 3, "hot4": [8.0] * 4}
    expected = {"three": [10.0] * 3, "four": [5.0] * 4, "hot3": [5.0] * 3, "hot4": [5.0] * 4}
    watch = _watch(actual, expected, {pid: 1 for pid in actual})
    assert [p.player_id for p in watch.due_to_rise] == ["four"]
    assert [p.player_id for p in watch.due_to_fall] == ["hot4"]


def test_a_game_with_no_stat_line_does_not_count_toward_the_floor():
    # The file lists 4 games, but the league has a stat line for 3 of them.
    actual = {"short": [0.0] * 3}
    expected = {"short": [10.0] * 4}
    watch = _watch(actual, expected, {"short": 1})
    assert watch.due_to_rise == []


def test_due_to_rise_and_due_to_fall_name_only_rostered_skill_players_with_their_manager():
    actual = {"mine": [1.0] * 4, "free": [0.0] * 4, "kick": [0.0] * 4}
    expected = {"mine": [5.0] * 4, "free": [9.0] * 4, "kick": [9.0] * 4}
    cards = {"mine": _card("mine"), "free": _card("free"), "kick": _card("kick", "K")}
    watch = _watch(actual, expected, {"mine": 2, "kick": 1}, players=cards)
    assert [(p.player_id, p.roster_id, p.manager) for p in watch.due_to_rise] == [("mine", 2, "Two")]


def test_each_list_holds_3_players_at_most():
    actual = {f"p{i}": [1.0] * 4 for i in range(5)}
    expected = {f"p{i}": [2.0 + i] * 4 for i in range(5)}
    watch = _watch(actual, expected, {pid: 1 for pid in actual})
    assert [p.player_id for p in watch.due_to_rise] == ["p4", "p3", "p2"]


def test_grab_him_now_is_the_free_agents_with_the_highest_projection_for_the_rest_of_the_regular_season():
    cards = {pid: _card(pid, position) for pid, position in
             (("a", "QB"), ("b", "WR"), ("c", "RB"), ("d", "TE"), ("e", "K"), ("owned", "QB"))}
    # Weeks 6 to 8 are the rest of the regular season. Week 9 is a playoff week, and week 5 is the report week.
    ahead = {5: {"d": 50.0}, 6: {"a": 10.0, "b": 12.0, "c": 5.0, "d": 1.0, "e": 30.0, "owned": 40.0},
             7: {"a": 10.0, "b": 2.0, "c": 5.0}, 8: {"c": 5.0}, 9: {"d": 99.0}}
    watch = _watch({}, {}, {"owned": 1}, players=cards, ahead=ahead)
    assert [(p.player_id, p.projection) for p in watch.grab_him_now] == [("a", 20.0), ("c", 15.0), ("b", 14.0)]
    assert all(p.roster_id is None for p in watch.grab_him_now)
