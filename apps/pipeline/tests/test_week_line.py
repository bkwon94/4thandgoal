"""
Tests for the Week line of each side: the count of the players who play in the trade week and the next week, the
opponent of each player the side gets, each bye, and each player who is out. They grade real trades at the document seam.
"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from cpc import cpc_client

from analyzer.analysis import AnalysisOut, _inner_word_failures, check_response, code_only
from analyzer.routes import result_document
from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.trade_facts import trade_fact_sheet
from league.numbers import ordinal as _ordinal
from league.paths import returns_path
from league.provider.sleeper import load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import build_snapshot, load_out_for_season, load_returns

CLIENT = cpc_client()
SAVED = CLIENT.folder / "data" / "2026"
ET = ZoneInfo("America/New_York")
# The nflverse fixture holds the real 2026 schedule, so the saved week 8 data reads the real games of weeks 9 and 10.
NFLVERSE = Path(__file__).parent / "fixtures" / "nflverse"
# A Thursday and a Tuesday of the week 9 trade window, in US Eastern time.
THURSDAY = datetime(2026, 11, 5, 12, 0, tzinfo=ET)
TUESDAY = datetime(2026, 11, 3, 12, 0, tzinfo=ET)

# Trade A: roster 10 gives Omar Cooper Jr. (NYJ) to roster 6 for Parker Washington (JAX). Roster 10 asks.
COOPER, WASHINGTON = "13276", "9487"


def _snapshot(now: datetime):
    returns_file = returns_path(CLIENT.nfl_dir, 2026)
    slow = load_slow_sources(NFLVERSE, 2026, 9, SAVED / "history")
    return build_snapshot(load_raw(SAVED / "week-08" / "raw"), SAVED / "history", None, slow, trade_week=9,
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          now=now, client=CLIENT)


@pytest.fixture(scope="module")
def thursday():
    return _snapshot(THURSDAY)


def _trade(first: int, first_gives: list[str], second: int, second_gives: list[str]) -> ProposedTrade:
    return ProposedTrade(season=2026, asker=first, sides=(
        TradeSide(roster_id=first, gives=[{"player_id": pid, "to": second} for pid in first_gives]),
        TradeSide(roster_id=second, gives=[{"player_id": pid, "to": first} for pid in second_gives])))


TRADE_A = _trade(10, [COOPER], 6, [WASHINGTON])


def _lines(trade: ProposedTrade, snapshot, roster_id: int) -> list[dict]:
    document = result_document(trade, snapshot, code_only(trade, snapshot))
    return next(side for side in document["sides"] if side["roster_id"] == roster_id)["week_lines"]


def test_each_side_has_a_week_line_for_the_trade_week_and_the_next_week_only(thursday):
    for roster_id in (10, 6):
        assert [line["week"] for line in _lines(TRADE_A, thursday, roster_id)] == [9, 10]


def _texts(trade: ProposedTrade, snapshot, roster_id: int) -> list[str]:
    return [line["text"] for line in _lines(trade, snapshot, roster_id)]


def test_trade_a_gives_the_count_the_opponent_the_byes_and_the_outs_of_each_week(thursday):
    # Worked from the saved week 8 data and the 2026 schedule. Roster 10 has Nacua (WR2) and Cooper (WR27) in the top
    # 36 by the grade's Position rank, and gets Washington (WR20) for Cooper. Egbuka (TB) and Samuel (SF) are listed
    # Out. PIT, the team of Bernard, has its bye in week 9, and TB has its bye in week 10. JAX plays at BAL, 9th in
    # points allowed to WRs, then at TEN, 1st. Out counts in week 9 only, so Egbuka names only his bye in week 10.
    assert _texts(TRADE_A, thursday, 10) == [
        ("Week 9: WRs in the top 36 who play stay at 2. Washington plays at BAL, 9th most points to WRs. "
         "Bernard has a bye. Egbuka and Samuel are listed Out."),
        ("Week 10: WRs in the top 36 who play stay at 2. Washington plays at TEN, 1st most points to WRs. "
         "Egbuka has a bye."),
    ]


def test_trade_a_names_the_home_game_of_the_player_the_other_side_gets(thursday):
    # Roster 6 has Flowers (WR9), Golden (WR12), and Washington (WR20) in the top 36, and gets Cooper (WR27). No WR of
    # roster 6 has a bye or is out in week 9 or 10. NYJ plays at KC, then BUF at home.
    texts = _texts(TRADE_A, thursday, 6)
    assert texts[0].startswith("Week 9: WRs in the top 36 who play stay at 3. Cooper plays at KC, ")
    assert texts[1].startswith("Week 10: WRs in the top 36 who play stay at 3. Cooper plays BUF at home, ")
    allowed = thursday.points_allowed
    assert texts[0].endswith(f"{_ordinal(allowed['KC']['WR'].rank)} most points to WRs.")
    assert texts[1].endswith(f"{_ordinal(allowed['BUF']['WR'].rank)} most points to WRs.")


def test_a_grade_on_a_tuesday_says_listed_out_last_week():
    texts = _texts(TRADE_A, _snapshot(TUESDAY), 10)
    assert texts[0].endswith("Egbuka and Samuel were listed Out last week.")
    assert "Out" not in texts[1]


NACUA = "9493"


def _nacua(snapshot, status: str | None = None, back: int | None = None, season: bool = False):
    """The snapshot with Puka Nacua of roster 10 given a status, a return week on file, or out for the season."""
    player = snapshot.players[NACUA].model_copy(update={"injury_status": status})
    returns = {**snapshot.returns, NACUA: back} if back is not None else snapshot.returns
    out = snapshot.out_for_season | {NACUA} if season else snapshot.out_for_season
    return snapshot.model_copy(update={"players": {**snapshot.players, NACUA: player}, "returns": returns,
                                       "out_for_season": out})


@pytest.mark.parametrize("change, week_9, week_10", [
    # IR, PUP, NA, and Sus count in both weeks. Nacua and Cooper are in the top 36 before, and Nacua and Washington
    # after, so with Nacua out the count stays at 1.
    ({"status": "IR"}, "Nacua is on IR.", "Nacua is on IR."),
    ({"status": "PUP"}, "Nacua is on the PUP list.", "Nacua is on the PUP list."),
    ({"status": "NA"}, "Nacua is not active.", "Nacua is not active."),
    ({"status": "Sus"}, "Nacua is suspended.", "Nacua is suspended."),
    # Out for the season and a return week after the next week count in both weeks.
    ({"season": True}, "Nacua is out for the season.", "Nacua is out for the season."),
    ({"status": "Out", "back": 11}, "Nacua is out until week 11.", "Nacua is out until week 11."),
])
def test_a_long_absence_counts_in_both_weeks(thursday, change, week_9, week_10):
    texts = _texts(TRADE_A, _nacua(thursday, **change), 10)
    assert "WRs in the top 36 who play stay at 1." in texts[0] and week_9 in texts[0]
    assert "WRs in the top 36 who play stay at 1." in texts[1] and week_10 in texts[1]


def test_out_and_a_return_in_the_next_week_count_in_the_trade_week_only(thursday):
    for snapshot, words in ((_nacua(thursday, "Out"), "Egbuka, Samuel and Nacua are listed Out."),
                            (_nacua(thursday, back=10), "Nacua is out until week 10.")):
        texts = _texts(TRADE_A, snapshot, 10)
        assert "stay at 1." in texts[0] and words in texts[0]
        assert "stay at 2." in texts[1] and "Nacua" not in texts[1]


@pytest.mark.parametrize("status", ["Questionable", "Doubtful"])
def test_questionable_and_doubtful_never_count(thursday, status):
    texts = _texts(TRADE_A, _nacua(thursday, status), 10)
    assert all("stay at 2." in text and "Nacua" not in text for text in texts)


def test_a_three_side_trade_gives_week_lines_for_every_side(thursday):
    # AT-5: roster 4 gives Rome Odunze to roster 12, roster 12 gives Garrett Wilson to roster 7, and roster 7 gives
    # Ryan Flournoy to roster 4.
    trade = ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": "11620", "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": "8146", "to": 7}]),
        TradeSide(roster_id=7, gives=[{"player_id": "11783", "to": 4}])))
    document = result_document(trade, thursday, code_only(trade, thursday))
    assert [side["roster_id"] for side in document["sides"]] == [4, 12, 7]
    for side in document["sides"]:
        assert [line["week"] for line in side["week_lines"]] == [9, 10]
        assert side["week_lines"][0]["text"].startswith("Week 9: WRs in the top 36 who play ")


def test_the_week_line_is_never_a_factor_and_moves_no_letter(thursday):
    with_lines = code_only(TRADE_A, thursday)
    # On a Tuesday the Week line changes, but the breakdown stays the same: no adjuster reads the Week line.
    tuesday = _snapshot(TUESDAY)
    assert _texts(TRADE_A, tuesday, 10) != _texts(TRADE_A, thursday, 10)
    assert code_only(TRADE_A, tuesday).breakdowns == with_lines.breakdowns
    document = result_document(TRADE_A, thursday, with_lines)
    names = {factor["name"] for side in document["sides"] for factor in side["factors"]}
    assert not any("week" in name for name in names)
    assert [a.name for a in with_lines.breakdowns[0].adjusters] == [
        "roster fit", "standing", "trend and usage", "injury", "upside", "handcuff", "schedule"]


def test_the_fact_sheet_holds_one_week_line_fact_per_side_with_the_text_of_its_two_lines(thursday):
    facts = trade_fact_sheet(TRADE_A, thursday)
    assert [fid for fid in facts if "week_line" in fid] == ["10.week_line", "6.week_line"]
    for roster_id in (10, 6):
        assert facts[f"{roster_id}.week_line"].text == " ".join(_texts(TRADE_A, thursday, roster_id))


def test_the_prose_checks_accept_the_numbers_and_the_names_of_the_week_line(thursday):
    facts = trade_fact_sheet(TRADE_A, thursday)
    breakdowns = code_only(TRADE_A, thursday).breakdowns
    bullets = {10: ["Washington plays at BAL in week 9, 9th most points to WRs.",
                    "The WRs in the top 36 who play stay at 2 in weeks 9 and 10."],
               6: ["Cooper plays BUF at home in week 10.", "The WRs in the top 36 who play stay at 3."]}
    out = AnalysisOut.model_validate({
        "sides": [{"roster_id": b.roster_id, "final_letter": b.final_letter, "reason": None,
                   "bullets": bullets[b.roster_id], "cited": [f"{b.roster_id}.week_line"]} for b in breakdowns],
        "verdict": {"choice": "accept", "reason": "Washington plays at TEN in week 10, 1st most points to WRs."}})
    assert check_response(out, thursday, breakdowns, facts) == []


def test_no_week_line_holds_an_inner_word(thursday):
    texts = [text for roster_id in (10, 6) for text in _texts(TRADE_A, thursday, roster_id)]
    assert [(text, failure) for text in texts if (failure := _inner_word_failures("week line", text))] == []


def test_with_no_schedule_the_week_line_says_so_and_names_no_bye_or_opponent(thursday):
    texts = _texts(TRADE_A, thursday.model_copy(update={"schedules": None}), 10)
    assert texts[0] == ("Week 9: WRs in the top 36 who play stay at 2. Egbuka and Samuel are listed Out. "
                        "No NFL schedule is on file, so no bye or opponent shows.")
