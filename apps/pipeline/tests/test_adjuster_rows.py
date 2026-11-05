"""
Tests for the rows of the result document: a silent row hides, and the deal, roster, and standing rows read in plain
words with no inner word. They grade real trades on the week 6 and the week 9 snapshots at the result document seam.
"""
import shutil

import pytest
from cpc import cpc_client, four_week

from analyzer.analysis import INNER_WORDS, _inner_word_failures, code_only
from analyzer.routes import result_document
from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.tunables import EXPECTED_ADJUSTER_ON
from league.paths import returns_path
from league.provider.sleeper import load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import build_snapshot, load_out_for_season, load_returns, load_snapshot

CLIENT = cpc_client()

# Week 6: Brian Robinson on roster 7 and Keaton Mitchell on roster 11. Mitchell backs up a starter on no roster of
# the trade, so no player is a handcuff. The id map fixture lacks the LAC players, so the test adds them.
B_ROBINSON, MITCHELL = "8154", "9511"
LAC_IDS = {MITCHELL: "00-0038454", "12507": "00-0040666", "11647": "00-0039391"}


@pytest.fixture
def slow_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources from the nflverse fixture, and the LAC players in the id map."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    snap = four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT))
    return snap.model_copy(update={"id_map": {**snap.id_map, **LAC_IDS}})


def _trade(first: int, first_gives: list[str], second: int, second_gives: list[str]) -> ProposedTrade:
    return ProposedTrade(season=2026, asker=first, sides=(
        TradeSide(roster_id=first, gives=[{"player_id": pid, "to": second} for pid in first_gives]),
        TradeSide(roster_id=second, gives=[{"player_id": pid, "to": first} for pid in second_gives])))


def _document(trade: ProposedTrade, snapshot) -> dict:
    return result_document(trade, snapshot, code_only(trade, snapshot))


def _rows(document: dict, roster_id: int) -> dict[str, str]:
    """The factors of one side, by name, with the reason of each."""
    side = next(side for side in document["sides"] if side["roster_id"] == roster_id)
    return {factor["name"]: factor["reason"] for factor in side["factors"]}


def test_a_row_that_says_nothing_is_not_in_the_document(slow_snap):
    rows = _rows(_document(_trade(7, [B_ROBINSON], 11, [MITCHELL]), slow_snap), 7)
    # "No player it gets is a handcuff." and "No player it gets is a star out now or has an opportunity." say nothing.
    assert "handcuff" not in rows
    assert "upside" not in rows
    # The deal row, the roster row, and the standing row always show.
    assert {"deal", "roster fit", "standing"} <= set(rows)


SAVED = CLIENT.folder / "data" / "2026"
# Trade A: roster 10, a seller, gives Omar Cooper Jr. to roster 6, a contender, for Parker Washington.
COOPER, WASHINGTON = "13276", "9487"


@pytest.fixture(scope="module")
def week_9():
    returns_file = returns_path(CLIENT.nfl_dir, 2026)
    return build_snapshot(load_raw(SAVED / "week-08" / "raw"), SAVED / "history", None, trade_week=9,
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          client=CLIENT)


@pytest.fixture(scope="module")
def trade_a_document(week_9):
    return _document(_trade(10, [COOPER], 6, [WASHINGTON]), week_9)


def test_the_roster_row_counts_the_players_in_the_top_n_before_and_after(trade_a_document):
    # The WR line of the client is 36. Roster 10 has 2 WRs above it before and after, and gets Washington, the
    # better player by points per game. Roster 6 has 3 before and after.
    assert _rows(trade_a_document, 10)["roster fit"] == "You keep 2 WRs in the top 36, and you get the better player."
    assert _rows(trade_a_document, 6)["roster fit"] == "You keep 3 WRs in the top 36."


def test_the_standing_row_names_the_race_the_need_and_whether_the_trade_meets_it(trade_a_document):
    # Roster 10 is out of the race and gets the better player. Roster 6 holds a playoff spot, and its lineup
    # changes by less than the fit threshold.
    assert _rows(trade_a_document, 10)["standing"] == (
        "Out of the playoff race, so you want the better player for the rest of the season, and you get him.")
    assert _rows(trade_a_document, 6)["standing"] == (
        "In a playoff spot, so you need points now, and this trade keeps your points about the same.")


# The rows this test owns. Ticket 05 of grade-clarity rewords the usage, injury, upside, handcuff, and schedule rows,
# then adds them here.
PLAIN_ROWS = ("deal", "roster fit", "standing")


def _one_for_one_trades(snapshot, first: int, second: int) -> list[ProposedTrade]:
    """Every trade of one player for one player between two rosters."""
    return [_trade(first, [mine], second, [theirs])
            for mine in snapshot.rosters[first] for theirs in snapshot.rosters[second]]


@pytest.mark.parametrize("first, second", [(7, 11), (1, 4), (3, 12)])
def test_no_deal_roster_or_standing_row_holds_an_inner_word_on_the_week_6_trades(slow_snap, first, second):
    # Rosters 1 and 3 hold a playoff spot, roster 4 is out of the race, and rosters 7, 11, and 12 are middle teams.
    texts = [reason for trade in _one_for_one_trades(slow_snap, first, second)
             for side in (first, second) for name, reason in _rows(_document(trade, slow_snap), side).items()
             if name in PLAIN_ROWS]
    assert texts
    assert [(text, failure) for text in texts if (failure := _inner_word_failures("row", text))] == []


def test_no_deal_roster_or_standing_row_holds_an_inner_word_on_the_week_9_trades(week_9):
    texts = [reason for trade in _one_for_one_trades(week_9, 10, 6)
             for side in (10, 6) for name, reason in _rows(_document(trade, week_9), side).items()
             if name in PLAIN_ROWS]
    assert [(text, failure) for text in texts if (failure := _inner_word_failures("row", text))] == []


def test_the_check_reads_each_inner_word_of_decision_03():
    assert INNER_WORDS == ["trade value", "highest-value", "best lineup", "the line", "hole", "win-now move",
                           "return bet", "star", "opportunity", "one step", "no step", "takes RB", "takes WR",
                           "takes TE", "takes QB", "sits on the bench"]


def test_each_row_is_one_sentence_with_no_step_word(trade_a_document):
    for side in trade_a_document["sides"]:
        for factor in side["factors"]:
            if factor["name"] in PLAIN_ROWS:
                assert factor["reason"].count(". ") == 0 and factor["reason"].endswith(".")
            for words in ("one step up", "one step down", "no step"):
                assert words not in factor["reason"].lower()


def test_no_document_has_an_expected_gap_row(trade_a_document):
    assert EXPECTED_ADJUSTER_ON is False
    assert [f["name"] for side in trade_a_document["sides"] for f in side["factors"] if f["name"] == "expected gap"] == []
