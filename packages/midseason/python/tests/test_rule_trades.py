"""
The rules of the trade report card, on a small hand-built league: the result lines, Too soon under 2 weeks, the net of
each side, the stint of a flipped player, and the gap from the best side to the worst side of a 3-team trade.
"""
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from league.models import History, PastWeek
from league.provider.raw import RawTransaction
from midseason.players import PlayerCard
from midseason.trades import trade_facts, trade_result, trade_week

ET = ZoneInfo("America/New_York")
# The cutoff of week 2 is 6 days after the start: the Tuesday 2026-09-15 at 08:00 Eastern.
SEASON_START = date(2026, 9, 9)
# The line is the 4th RB, Back 99, who scores 0 each week.
LINES = {"RB": 4}
NAMES = {1: "One", 2: "Two", 3: "Three"}
PLAYERS = {pid: PlayerCard(player_id=pid, name=f"Back {pid}", position="RB") for pid in ("10", "20", "30", "99")}


@pytest.mark.parametrize(("gap", "weeks", "label"), [
    (90, 2, "Robbery"), (89.99, 5, "Clear win"), (60, 2, "Clear win"), (10, 3, "Slight edge"),
    (9.99, 3, "Even"), (200, 1, "Too soon")])
def test_the_result_lines_and_too_soon_under_two_weeks(gap, weeks, label):
    assert trade_result(gap, weeks) == label


def test_a_trade_belongs_to_the_week_of_its_trade_window():
    assert trade_week(datetime(2026, 9, 15, 11, 59, tzinfo=UTC), SEASON_START, ET, 3) == 1
    assert trade_week(datetime(2026, 9, 15, 12, 1, tzinfo=UTC), SEASON_START, ET, 3) == 2


def _week(number: int, rosters: dict[int, list[str]], points: dict[str, float]) -> PastWeek:
    # Each roster starts each of its players. Back 99 sits on no roster and sets the line at 0.
    return PastWeek(week=number, scores={1: 0.0, 2: 0.0, 3: 0.0}, pairs=[(1, 2)], points=points, projections={},
                    stats={}, moves=[], positions={pid: "RB" for pid in points}, starters=rosters, rosters=rosters)


def _trade(adds: dict[str, int], drops: dict[str, int], when: datetime) -> RawTransaction:
    return RawTransaction.model_validate({
        "transaction_id": f"t-{when.timestamp()}", "type": "trade", "status": "complete", "leg": 1,
        "created": int(when.timestamp() * 1000), "roster_ids": sorted(set(adds.values())), "adds": adds,
        "drops": drops})


# The trade of week 1 sends Back 10 to Two and Back 20 to One. Two flips Back 10 to Three for week 3.
HISTORY = History(week=3, weeks={
    1: _week(1, {1: ["20"], 2: ["10"], 3: ["30"]}, {"10": 50.0, "20": 10.0, "30": 5.0, "99": 0.0}),
    2: _week(2, {1: ["20"], 2: ["10"], 3: ["30"]}, {"10": 60.0, "20": 10.0, "30": 5.0, "99": 0.0}),
    3: _week(3, {1: ["20"], 2: ["30"], 3: ["10"]}, {"10": 70.0, "20": 10.0, "30": 5.0, "99": 0.0}),
})


def _cards(*rows: RawTransaction, history: History = HISTORY):
    return trade_facts(history, history.week, {1: list(rows)}, PLAYERS, NAMES, LINES, season_start=SEASON_START,
                       tz=ET, median_game=False).trades


def test_each_side_nets_what_it_started_minus_what_the_other_side_started_and_a_flip_ends_the_stint():
    [card] = _cards(_trade({"10": 2, "20": 1}, {"10": 1, "20": 2}, datetime(2026, 9, 12, tzinfo=UTC)))
    nets = {side.team: side.net for side in card.sides}
    # Two counts Back 10 for weeks 1 and 2 only, before the flip: 50 + 60 over a line of 0, less Back 20's 30.
    assert nets == {"One": -80.0, "Two": 80.0}
    assert (card.gap, card.result, card.winner, card.weeks_since) == (160.0, "Robbery", "Two", 3)


def test_a_three_team_trade_takes_its_gap_from_the_best_side_to_the_worst_side():
    history = History(week=2, weeks={
        number: _week(number, {1: ["30"], 2: ["10"], 3: ["20"]}, {"10": 50.0, "20": 10.0, "30": 5.0, "99": 0.0})
        for number in (1, 2)})
    [card] = _cards(_trade({"10": 2, "20": 3, "30": 1}, {"10": 1, "20": 2, "30": 3},
                           datetime(2026, 9, 12, tzinfo=UTC)), history=history)
    # One got 10 and gave 100. Two got 100 and gave 20. Three got 20 and gave 10.
    assert {side.team: side.net for side in card.sides} == {"One": -90.0, "Two": 80.0, "Three": 10.0}
    assert (card.gap, card.result, card.winner) == (170.0, "Robbery", "Two")


def test_a_trade_in_the_last_week_of_the_report_is_too_soon():
    [card] = _cards(_trade({"10": 2, "20": 1}, {"10": 1, "20": 2}, datetime(2026, 9, 29, tzinfo=UTC)))
    assert (card.week, card.weeks_since, card.result, card.winner) == (3, 1, "Too soon", None)
