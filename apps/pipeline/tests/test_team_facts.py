"""
Tests for the team facts of the Advisor sheet: the race group and the odds, the bye, the depth, and the Measures.
They read the saved cpc data of week 7, with the rosters before trade 6 of the eval, and FakeJev at the Jev port.
"""
import re
import shutil
from pathlib import Path

import pytest
from cpc import cpc_client
from fakes import FakeJev, no_news

from analyzer.advisor import advisor_sheet
from analyzer.trade import ProposedTrade, TradeSide
from analyzer.trade_news import NewsFeed
from league.paths import history_root, raw_dir
from league.slow_sources import load_slow_sources
from league.snapshot import Snapshot, load_snapshot

CLIENT = cpc_client()
# Trade 6 of the eval, in week 7: roster 10 asks, and gets Omar Cooper Jr. and Puka Nacua from roster 4 for Saquon
# Barkley and CeeDee Lamb.
COOPER, NACUA, BARKLEY, LAMB = "13276", "9493", "4866", "6786"
NFLVERSE = Path(__file__).parent / "fixtures" / "nflverse"
DEPTH = re.compile(r"RBs in the top 36 go from (\d+) to (\d+)\.")


@pytest.fixture(scope="module")
def week_7(tmp_path_factory) -> Snapshot:
    """The saved cpc snapshot of week 7. Its rosters are the rosters before trade 6. It loads once for the module,
    because the load takes seconds and no test changes it."""
    cache = tmp_path_factory.mktemp("cache") / "nflverse"
    shutil.copytree(NFLVERSE, cache)
    root = history_root(CLIENT.folder, 2026)
    slow = load_slow_sources(cache, 2026, 7, root)
    return load_snapshot(raw_dir(CLIENT.folder, 2026, 7), root, None, slow, client=CLIENT)


@pytest.fixture
def trade_6() -> ProposedTrade:
    return ProposedTrade(season=2026, asker=10, sides=(
        TradeSide(roster_id=10, gives=[{"player_id": BARKLEY, "to": 4}, {"player_id": LAMB, "to": 4}]),
        TradeSide(roster_id=4, gives=[{"player_id": COOPER, "to": 10}, {"player_id": NACUA, "to": 10}])))


def _rbs_in_the_top_36(snapshot: Snapshot, roster: list[str]) -> int:
    return sum(1 for pid in roster if snapshot.players[pid].position == "RB"
               and (rank := snapshot.position_rank(pid)) is not None and rank <= 36)


def test_each_side_of_trade_6_has_its_rb_depth_before_and_after_the_trade(week_7, trade_6):
    sheet = advisor_sheet(trade_6, week_7, FakeJev(), NewsFeed(fetch=no_news))
    for side in trade_6.sides:
        rid = side.roster_id
        before = week_7.rosters[rid]
        after = [pid for pid in before if pid not in side.player_ids] + trade_6.gets(rid)
        match = DEPTH.search(sheet[f"{rid}.depth.rb"].text)
        assert match is not None, sheet[f"{rid}.depth.rb"].text
        assert (int(match[1]), int(match[2])) == (_rbs_in_the_top_36(week_7, before), _rbs_in_the_top_36(week_7, after))


def test_each_side_has_the_depth_of_every_position_of_the_trade(week_7, trade_6):
    sheet = advisor_sheet(trade_6, week_7, FakeJev(), NewsFeed(fetch=no_news))
    for rid in (10, 4):
        assert "WRs in the top 36 go from" in sheet[f"{rid}.depth.wr"].text


def test_each_side_has_its_race_group_and_its_playoff_odds_after_the_last_week(week_7, trade_6):
    # The published rankings of week 6 give roster 10 odds of 24% and roster 4 odds of 1%, so both are Out.
    sheet = advisor_sheet(trade_6, week_7, FakeJev(), NewsFeed(fetch=no_news))
    assert sheet["10.team"].text.endswith("was 6-6, 8th of 12, before the trade. Its race group is Out, "
                                          "with 24% playoff odds after week 6.")
    assert "24" in sheet["10.team"].numbers
    assert "race group is Out, with 1% playoff odds" in sheet["4.team"].text
    assert "seller" not in sheet["4.team"].text


def test_a_side_that_starts_a_player_with_a_bye_in_the_trade_week_has_a_bye_fact(week_7, trade_6):
    # Josh Allen starts at QB for roster 10, and Buffalo has its bye in week 7. No starter of roster 4 has a bye then.
    sheet = advisor_sheet(trade_6, week_7, FakeJev(), NewsFeed(fetch=no_news))
    assert sheet["10.bye"].text.endswith("Josh Allen starts after the trade and has a bye in week 7, the trade week.")
    assert "Josh Allen" in sheet["10.bye"].players
    assert "4.bye" not in sheet


def test_a_bubble_side_that_gets_a_starter_with_a_bye_reads_both(week_7):
    # Roster 1 has 57% odds after week 6, so it is on the Bubble. It gets Omarion Hampton, and the Chargers have
    # their bye in week 7.
    hampton, etienne = "12507", "7543"
    trade = ProposedTrade(season=2026, asker=1, sides=(
        TradeSide(roster_id=1, gives=[{"player_id": etienne, "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": hampton, "to": 1}])))
    sheet = advisor_sheet(trade, week_7, FakeJev(), NewsFeed(fetch=no_news))
    assert "Its race group is Bubble, with 57% playoff odds after week 6." in sheet["1.team"].text
    assert "Omarion Hampton" in sheet["1.bye"].text and "week 7" in sheet["1.bye"].text


def test_each_measure_writes_its_read_as_a_fact_that_moves_nothing(week_7, trade_6):
    sheet = advisor_sheet(trade_6, week_7, FakeJev(), NewsFeed(fetch=no_news))
    trend = sheet["10.measure.trend"]
    # The trend Measure reads more than snaps: the carries of a back, and the targets and air yards of a receiver.
    assert "of the carries" in trend.text and "of the targets" in trend.text and "air yards" in trend.text
    assert "87" in trend.numbers
    for rid in (10, 4):
        assert {f"{rid}.measure.fit", f"{rid}.measure.standing", f"{rid}.measure.schedule"} <= set(sheet)
    # A Measure that says nothing, such as no superstar in the trade, writes no fact.
    assert "10.measure.superstar" not in sheet
    assert not any("step" in f.text for fid, f in sheet.items() if ".measure." in fid)
