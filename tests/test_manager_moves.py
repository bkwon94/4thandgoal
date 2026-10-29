"""
Tests for the moves of a managers entry: the adds, the drops, and the trades per week, and the totals.
They run on small histories built in the test, and on the saved transactions of the fixture history.
"""
import json
from datetime import datetime, timezone

from cornerstone.managers import managers
from cornerstone.models import Drop, History, Move, PastWeek, Team, Trade
from cornerstone.parse import parse_drops

PLAYERS = {
    "100": {"full_name": "Wide Out", "position": "WR"},
    "200": {"full_name": "Run Back", "position": "RB"},
    "300": {"full_name": "Tight End", "position": "TE"},
    "400": {"full_name": "Quarter Back", "position": "QB"},
}
TEAMS = {
    rid: Team(roster_id=rid, name=f"Team {rid}", owner=f"owner{rid}", avatar_url=None, wins=0, losses=0,
              points_for=0.0, is_brian=False)
    for rid in range(1, 13)
}
# The record of an entry needs a full week of twelve rosters in six pairs.
SCORES = {rid: 100.0 + rid for rid in range(1, 13)}
PAIRS = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]


def _week(n: int, moves=(), drops=(), trades=()) -> PastWeek:
    return PastWeek(week=n, scores=SCORES, pairs=PAIRS, points={}, projections={}, stats={},
                    moves=list(moves), drops=list(drops), trades=list(trades))


def _moves(weeks: list[PastWeek], roster_id: int = 1, players=PLAYERS) -> dict:
    history = History(week=len(weeks), weeks={w.week: w for w in weeks})
    entry = next(e for e in managers(history, TEAMS, players=players) if e.roster_id == roster_id)
    return entry.model_dump(mode="json")["moves"]


def _trade(week: int) -> Trade:
    # Roster 1 gives the TE and gets the QB and the RB from roster 2.
    return Trade(transaction_id=f"t{week}", created=datetime(2026, 9, 20, tzinfo=timezone.utc), roster_ids=[1, 2],
                 adds={"400": 1, "200": 1, "300": 2}, drops={"400": 2, "200": 2, "300": 1}, draft_picks=[])


def test_a_roster_with_no_moves_has_empty_weeks_and_zero_totals():
    moves = _moves([_week(1), _week(2)])
    assert (moves["adds"], moves["drops"], moves["trades"]) == (0, 0, 0)
    assert moves["weeks"] == [
        {"week": 2, "adds": [], "drops": [], "trades": []},
        {"week": 1, "adds": [], "drops": [], "trades": []},
    ]


def test_a_free_agent_add_has_no_bid():
    add = Move(player_id="100", roster_id=1, kind="free_agent", week=1, bid=None)
    moves = _moves([_week(1, moves=[add]), _week(2)])
    assert moves["adds"] == 1
    assert moves["weeks"][1]["adds"] == [
        {"player_id": "100", "name": "Wide Out", "position": "WR", "kind": "free_agent", "bid": None},
    ]


def test_a_waiver_add_carries_its_bid():
    add = Move(player_id="100", roster_id=1, kind="waiver", week=2, bid=12)
    moves = _moves([_week(1), _week(2, moves=[add])])
    assert moves["weeks"][0]["adds"] == [
        {"player_id": "100", "name": "Wide Out", "position": "WR", "kind": "waiver", "bid": 12},
    ]


def test_a_drop_names_the_player():
    drop = Drop(player_id="200", roster_id=1, week=1)
    moves = _moves([_week(1, drops=[drop]), _week(2)])
    assert moves["drops"] == 1
    assert moves["weeks"][1]["drops"] == [{"player_id": "200", "name": "Run Back", "position": "RB"}]


def test_the_moves_of_another_roster_stay_out():
    add = Move(player_id="100", roster_id=2, kind="waiver", week=1, bid=3)
    drop = Drop(player_id="200", roster_id=2, week=1)
    moves = _moves([_week(1, moves=[add], drops=[drop]), _week(2)])
    assert (moves["adds"], moves["drops"]) == (0, 0)


def test_a_trade_shows_both_sides_and_its_adds_are_not_adds():
    trade_adds = [Move(player_id=p, roster_id=r, kind="trade", week=2, bid=None)
                  for p, r in (("400", 1), ("200", 1), ("300", 2))]
    weeks = [_week(1), _week(2, moves=trade_adds, trades=[_trade(2)])]
    mine = _moves(weeks, roster_id=1)
    assert (mine["adds"], mine["drops"], mine["trades"]) == (0, 0, 1)
    assert mine["weeks"][0]["trades"] == [{
        "with": [2],
        "gave": [{"player_id": "300", "name": "Tight End", "position": "TE"}],
        "got": [
            {"player_id": "200", "name": "Run Back", "position": "RB"},
            {"player_id": "400", "name": "Quarter Back", "position": "QB"},
        ],
    }]
    theirs = _moves(weeks, roster_id=2)
    assert theirs["weeks"][0]["trades"][0]["with"] == [1]
    assert [p["player_id"] for p in theirs["weeks"][0]["trades"][0]["gave"]] == ["200", "400"]


def test_the_weeks_run_newest_first_through_the_history_week():
    weeks = [_week(n, moves=[Move(player_id="100", roster_id=1, kind="waiver", week=n, bid=n)]) for n in (1, 2, 3)]
    moves = _moves(weeks)
    assert [w["week"] for w in moves["weeks"]] == [3, 2, 1]
    assert [w["adds"][0]["bid"] for w in moves["weeks"]] == [3, 2, 1]
    assert moves["adds"] == 3


def test_a_player_not_in_the_players_file_falls_back_to_the_id():
    add = Move(player_id="999", roster_id=1, kind="free_agent", week=1, bid=None)
    moves = _moves([_week(1, moves=[add]), _week(2)], players={})
    assert moves["weeks"][1]["adds"][0] == {
        "player_id": "999", "name": "999", "position": None, "kind": "free_agent", "bid": None,
    }


def test_the_drops_come_from_the_saved_transactions(fixture_history_root):
    transactions = json.loads((fixture_history_root / "week-02" / "transactions.json").read_text(encoding="utf-8"))
    expected = {
        (pid, rid)
        for t in transactions
        if t["status"] == "complete" and t["type"] in ("waiver", "free_agent")
        for pid, rid in (t["drops"] or {}).items()
    }
    drops = parse_drops(transactions)
    assert expected
    assert {(d.player_id, d.roster_id) for d in drops} == expected
    # A trade drop is a side of the trade, so the drops leave it out.
    assert {d.week for d in drops} == {2}
