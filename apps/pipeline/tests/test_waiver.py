"""
Tests for the waiver board engine.
They feed the week 6 raw with hand-set free agents at the engine seam and read the buckets and the budget table.
"""
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

from cpc import cpc_client

from cornerstone.provider.sleeper import load_raw
from cornerstone.waiver import waiver_board

CLIENT = cpc_client()

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))
# The weeks of the projections ahead file of week 6.
AHEAD = range(7, 18)


def _player(position: str, team: str | None = "KC", status: str | None = "Active", name: str = "Free Agent") -> dict:
    return {"position": position, "team": team, "status": status, "active": True, "full_name": name}


def _raw(fixture_raw_dir, players: dict[str, dict], per_week: dict[str, float]) -> dict:
    """The week 6 raw with `players` added to the players file and a flat projection per week for each ID in
    `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw.players = {**raw.players, **players}
    raw.projections_ahead = [{"week": w, "projections": dict(per_week)} for w in AHEAD]
    return raw


def _best_adds(raw) -> list[str]:
    return [p.player_id for p in waiver_board(raw, 6, BUILT, client=CLIENT).buckets["best_adds"]]


def test_the_pool_holds_active_free_agents_with_a_team_and_a_fantasy_position(fixture_raw_dir):
    rostered = load_raw(fixture_raw_dir).rosters[0].players[0]
    players = {
        "80001": _player("RB"),
        "80002": _player("WR"),
        "80003": _player("RB", team=None),
        "80004": _player("WR", status="Inactive"),
        "80005": _player("LB"),
        "80006": _player("TE", status="Injured Reserve"),
    }
    per_week = {pid: 10.0 for pid in players} | {rostered: 30.0}
    assert sorted(_best_adds(_raw(fixture_raw_dir, players, per_week))) == ["80001", "80002"]


def test_the_rest_of_season_projection_sums_weeks_7_to_17_with_the_bye_as_0(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("WR")}, {})
    # 11 weeks ahead of week 6. Week 9 is the bye, so it has no projection and counts 0.
    raw.projections_ahead = [
        {"week": w, "projections": {} if w == 9 else {"80001": 10.5 + w}} for w in AHEAD
    ]
    player = waiver_board(raw, 6, BUILT, client=CLIENT).buckets["best_adds"][0]
    assert player.week_projection == 17.5
    # Ten weeks at 10.5 give 105, and the week numbers 7 to 17 without 9 add 123.
    assert player.ros_projection == 228.0


def test_best_adds_holds_at_most_3_players_of_one_position_and_8_in_all(fixture_raw_dir):
    # Five RBs, five WRs, and five TEs. The RBs project the most, so the cap stops the 4th and the 5th RB.
    players, per_week = {}, {}
    for base, position, points in ((80000, "RB", 30.0), (80100, "WR", 20.0), (80200, "TE", 10.0)):
        for i in range(1, 6):
            players[str(base + i)] = _player(position)
            per_week[str(base + i)] = points - i
    best = waiver_board(_raw(fixture_raw_dir, players, per_week), 6, BUILT, client=CLIENT).buckets["best_adds"]
    assert len(best) == 8
    assert max(Counter(p.position for p in best).values()) == 3
    assert {"80004", "80005"}.isdisjoint(p.player_id for p in best)


def test_the_budget_table_holds_every_roster_with_its_budget_left_and_waiver_order(fixture_raw_dir):
    budgets = waiver_board(load_raw(fixture_raw_dir), 6, BUILT, client=CLIENT).budgets
    assert [row.roster_id for row in budgets] == list(range(1, 13))
    # The league budget is 100. Roster 1 used 31 and claims first; roster 8 used 91 and claims 10th.
    assert budgets[0].model_dump() == {"roster_id": 1, "budget_left": 69, "waiver_order": 1}
    assert budgets[7].model_dump() == {"roster_id": 8, "budget_left": 9, "waiver_order": 10}


def test_two_runs_on_the_same_raw_give_the_same_board(fixture_raw_dir):
    # Equal projections force a tie, so the order of the tie must not follow the dict order.
    players = {f"8000{i}": _player("WR") for i in range(1, 6)}
    raw = _raw(fixture_raw_dir, players, {pid: 8.0 for pid in players})
    backward = raw.model_copy(update={"players": dict(reversed(raw.players.items()))})
    first = waiver_board(raw, 6, BUILT, client=CLIENT).model_dump_json()
    assert waiver_board(raw, 6, BUILT, client=CLIENT).model_dump_json() == first
    assert waiver_board(backward, 6, BUILT, client=CLIENT).model_dump_json() == first


def test_a_top_kicker_and_a_top_defense_stay_out_of_best_adds(fixture_raw_dir):
    # The kicker and the defense project the most points of the pool, and they still never land in best adds.
    players = {"80001": _player("K"), "NYJ": _player("DEF", team="NYJ", status=None), "80002": _player("WR")}
    raw = _raw(fixture_raw_dir, players, {"80001": 30.0, "NYJ": 30.0, "80002": 5.0})
    assert _best_adds(raw) == ["80002"]
