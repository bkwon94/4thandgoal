"""
Tests for the manager players module: the best adds and the top performers of a roster.
They build small past weeks in the test, so each case reads one rule.
"""
from cornerstone.manager_players import best_adds, top_performers
from cornerstone.models import History, Move, PastWeek


def _week(week, points, rosters, starters=None, moves=(), projections=None, positions=None):
    return PastWeek(
        week=week, scores={}, pairs=[], points=points, projections=projections or {}, stats={},
        moves=list(moves), positions=positions or {}, starters=starters or {}, rosters=rosters,
    )


def _add(pid, rid, week, kind="waiver"):
    return Move(player_id=pid, roster_id=rid, kind=kind, week=week, bid=None)


def _history(*weeks):
    return History(week=max(w.week for w in weeks), weeks={w.week: w for w in weeks})


PLAYERS = {"a": {"full_name": "Al Adds", "position": "WR"}, "b": {"full_name": "Bo Bench", "position": "RB"}}


def test_a_short_stint_add_still_ranks():
    # "a" plays one week for roster 1, then moves on. One big week is enough to rank.
    history = _history(
        _week(1, {"a": 30.0}, {1: ["a"]}, moves=[_add("a", 1, 1)], projections={"a": 12.0}),
        _week(2, {"a": 5.0}, {2: ["a"]}, projections={"a": 11.0}),
    )
    adds = best_adds(history, 1, PLAYERS)
    assert [a.model_dump() for a in adds] == [{
        "player_id": "a", "name": "Al Adds", "position": "WR", "week": 1, "points": 30.0, "projection": 12.0,
        "games": 1,
    }]


def test_a_dropped_and_re_added_player_counts_from_the_last_add():
    history = _history(
        _week(1, {"a": 10.0}, {1: ["a"]}, moves=[_add("a", 1, 1)], projections={"a": 8.0}),
        _week(2, {"a": 20.0}, {1: []}),
        _week(3, {"a": 7.0}, {1: ["a"]}, moves=[_add("a", 1, 3, kind="free_agent")]),
        _week(4, {"a": 4.0}, {1: ["a"]}, projections={"a": 6.0}),
    )
    (add,) = best_adds(history, 1, PLAYERS)
    # A week with no projection counts 0.
    assert (add.week, add.points, add.projection, add.games) == (3, 11.0, 6.0, 2)


def test_a_trade_is_not_an_add():
    history = _history(_week(1, {"a": 10.0}, {1: ["a"]}, moves=[_add("a", 1, 1, kind="trade")]))
    assert best_adds(history, 1, PLAYERS) == []


def test_a_roster_with_no_adds_has_no_best_adds():
    history = _history(_week(1, {"a": 10.0}, {1: ["a"], 2: []}, moves=[_add("a", 1, 1)]))
    assert best_adds(history, 2, PLAYERS) == []


def test_best_adds_keep_three_and_a_tie_goes_to_the_earlier_add():
    history = _history(
        _week(1, {"a": 10.0, "b": 0.0}, {1: ["a"]}, moves=[_add("a", 1, 1)]),
        _week(2, {"a": 0.0, "b": 10.0, "c": 3.0, "d": 2.0}, {1: ["a", "b", "c", "d"]},
              moves=[_add("b", 1, 2), _add("c", 1, 2), _add("d", 1, 2)]),
    )
    adds = best_adds(history, 1, PLAYERS)
    assert [a.player_id for a in adds] == ["a", "b", "c"]


def test_a_name_not_found_falls_back_to_the_id_and_the_saved_position():
    history = _history(_week(1, {"z": 9.0}, {1: ["z"]}, moves=[_add("z", 1, 1)], positions={"z": "TE"}))
    (add,) = best_adds(history, 1, {})
    assert (add.name, add.position) == ("z", "TE")
    history = _history(_week(1, {"z": 9.0}, {1: ["z"]}, moves=[_add("z", 1, 1)]))
    assert best_adds(history, 1, {})[0].position is None


def test_a_traded_away_player_keeps_his_starts():
    history = _history(
        _week(1, {"a": 20.0}, {1: ["a"]}, starters={1: ["a"]}),
        _week(2, {"a": 15.0}, {1: ["a"]}, starters={1: ["a"]}),
        # "a" goes to roster 2. His starts there count for roster 2 only.
        _week(3, {"a": 40.0}, {2: ["a"]}, starters={2: ["a"]}),
    )
    (one,) = top_performers(history, 1, PLAYERS)
    assert one.model_dump() == {
        "player_id": "a", "name": "Al Adds", "position": "WR", "points": 35.0, "games": 2, "per_game": 17.5,
    }
    (two,) = top_performers(history, 2, PLAYERS)
    assert (two.points, two.games) == (40.0, 1)


def test_bench_points_are_not_top_performer_points():
    history = _history(_week(1, {"a": 20.0, "b": 30.0}, {1: ["a", "b"]}, starters={1: ["a"]}))
    assert [p.player_id for p in top_performers(history, 1, PLAYERS)] == ["a"]


def test_top_performers_keep_five_in_points_order():
    pts = {"p1": 5.0, "p2": 30.0, "p3": 10.0, "p4": 25.0, "p5": 1.0, "p6": 12.0}
    history = _history(_week(1, pts, {1: list(pts)}, starters={1: list(pts)}))
    performers = top_performers(history, 1, PLAYERS)
    assert [p.player_id for p in performers] == ["p2", "p4", "p6", "p3", "p1"]
    # The per game number rounds to one decimal.
    history = _history(
        _week(1, {"a": 10.0}, {1: ["a"]}, starters={1: ["a"]}),
        _week(2, {"a": 10.0}, {1: ["a"]}, starters={1: ["a"]}),
        _week(3, {"a": 5.0}, {1: ["a"]}, starters={1: ["a"]}),
    )
    assert top_performers(history, 1, PLAYERS)[0].per_game == 8.3
