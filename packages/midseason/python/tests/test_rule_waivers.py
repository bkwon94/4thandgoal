"""
The rules of the waiver chapter, on a small hand-built league: the hits rank by Points over the line, a miss needs a
big bid and a game after it, a $0 add is never a miss, and a lost claim pairs with the won claim of the same run.
"""
from league.models import History, PastWeek
from league.provider.raw import RawTransaction
from midseason.moves import PlayerInfo
from midseason.waivers import waiver_facts

# The line is the 2nd RB, so a small pool of 3 RBs sets it each week.
LINES = {"RB": 2}
NAMES = {1: "One", 2: "Two"}
PLAYERS = {pid: PlayerInfo(name=f"Back {pid}", position="RB") for pid in ("10", "11", "12", "20", "21", "22")}


def _week(number: int, rosters: dict[int, list[str]], starters: dict[int, list[str]], points: dict[str, float],
          scores: dict[int, float]) -> PastWeek:
    return PastWeek(week=number, scores=scores, pairs=[(1, 2)], points=points, projections={}, stats={}, moves=[],
                    positions={pid: "RB" for pid in points}, starters=starters, rosters=rosters)


def _add(pid: str, roster_id: int, leg: int, *, bid: int | None, kind: str = "waiver", status: str = "complete",
         when: int = 0, note: str = "") -> RawTransaction:
    return RawTransaction.model_validate({
        "transaction_id": f"{kind}-{pid}-{roster_id}-{leg}-{status}", "type": kind, "status": status, "leg": leg,
        "created": when, "status_updated": when, "roster_ids": [roster_id], "adds": {pid: roster_id}, "drops": None,
        "settings": None if bid is None else {"waiver_bid": bid}, "metadata": {"notes": note}})


# Week 1: the line is 10. Week 2: the line is 10.
HISTORY = History(week=2, weeks={
    1: _week(1, {1: ["10", "11"], 2: ["20", "21"]}, {1: ["10"], 2: ["20"]},
             {"10": 30.0, "11": 5.0, "12": 10.0, "20": 8.0, "21": 0.0, "22": 1.0}, {1: 30.0, 2: 8.0}),
    2: _week(2, {1: ["10", "11"], 2: ["20", "21"]}, {1: ["10"], 2: ["20"]},
             {"10": 20.0, "11": 5.0, "12": 10.0, "20": 4.0, "21": 0.0, "22": 1.0}, {1: 20.0, 2: 4.0}),
})


def _facts(*rows: RawTransaction):
    by_week: dict[int, list[RawTransaction]] = {}
    for row in rows:
        by_week.setdefault(row.leg, []).append(row)
    return waiver_facts(HISTORY, 2, by_week, PLAYERS, NAMES, LINES, budget=100)


def test_a_hit_ranks_by_points_over_the_line_of_its_starts_and_counts_a_swung_win():
    facts = _facts(_add("10", 1, 1, bid=5), _add("20", 2, 1, bid=60))
    assert [(hit.player_id, hit.points_over_line, hit.starts) for hit in facts.hits] == [("10", 30.0, 2)]
    # Team One won week 1 by 22 and week 2 by 16, and Back 10 scored more than each margin.
    assert facts.hits[0].swung_wins == 2


def test_a_zero_dollar_add_is_never_a_miss():
    # Back 11 sat on the bench both weeks, so a paid claim on him is a miss, but a free add or a $0 claim is not.
    assert [miss.player_id for miss in _facts(_add("11", 1, 1, bid=30)).misses] == ["11"]
    assert _facts(_add("11", 1, 1, bid=None, kind="free_agent")).misses == []
    assert _facts(_add("11", 1, 1, bid=0)).misses == []


def test_a_claim_with_no_game_after_it_is_never_a_miss():
    # Back 12 was never on a roster in a week of the report, so the claim of week 2 came after the last game.
    facts = _facts(_add("12", 2, 2, bid=80))
    assert facts.misses == []


def test_a_bid_under_a_tenth_of_the_budget_is_never_a_miss():
    assert _facts(_add("11", 1, 1, bid=9)).misses == []


def test_a_miss_with_starts_needs_points_over_the_line_below_zero():
    # Back 20 started both weeks for Team Two, under the line each week.
    facts = _facts(_add("20", 2, 1, bid=60))
    assert [(miss.player_id, miss.starts, miss.points_over_line) for miss in facts.misses] == [("20", 2, -8.0)]


def test_a_lost_claim_pairs_with_the_won_claim_of_the_same_run_and_shows_the_margin():
    facts = _facts(_add("10", 1, 1, bid=40, when=1000),
                   _add("10", 2, 1, bid=36, status="failed", when=1000,
                        note="This player was claimed by another owner."),
                   _add("10", 2, 1, bid=50, status="failed", when=2000,
                        note="This player was claimed by another owner."))
    assert [(o.team, o.bid, o.winner, o.winner_bid, o.margin) for o in facts.outbid] == [("Two", 36, "One", 40, 4)]
