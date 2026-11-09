"""
Tests for the Jev answers of one trade: the questions it asks, the state it sends, and the facts the answers give.
They read the week 6 snapshot and use FakeJev, so no test calls TypeSafe.
"""
import shutil

import pytest
from cpc import cpc_client, four_week
from fakes import FakeJev

from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.trade_jev import trade_jev_facts
from league.jev_port import JevError
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
# Roster 4 gives Nico Collins to roster 12 for Dalton Kincaid and Garrett Wilson. Roster 4 asks.
COLLINS, KINCAID, WILSON = "7569", "10236", "8146"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT))


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": COLLINS, "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": KINCAID, "to": 4}, {"player_id": WILSON, "to": 4}])))


def test_one_request_asks_if_the_trade_is_fair_who_needs_it_and_if_the_other_manager_accepts(snap, trade):
    jev = FakeJev(yes=0.9)
    facts = trade_jev_facts(trade, snap, jev)
    assert len(jev.requests) == 1
    request = jev.requests[0]
    assert set(request.questions) == {"fair", "need.4", "need.12", "accept.12"}
    four, twelve = snap.teams[4].name, snap.teams[12].name
    fair = request.questions["fair"].instructions
    assert isinstance(fair, str) and four in fair and twelve in fair and "Nico Collins" in fair
    # Each team in the state names its weak starting slots, so the need question can point at them.
    assert set(request.state["teams"]) == {"asker", "partner"}
    for team in request.state["teams"].values():
        assert isinstance(team["weak_starting_slots"], list)
    assert "teams.partner.weak_starting_slots" in request.questions["need.12"].yes
    assert set(facts) == {"JEV.fair", "JEV.need.4", "JEV.need.12", "JEV.accept.12"}
    assert facts["JEV.fair"].text.endswith("yes.")
    assert facts["JEV.accept.12"].teams == [twelve]
    # A fact of a Jev answer holds no number, so no probability reaches the prose.
    assert all(fact.numbers == [] for fact in facts.values())


@pytest.mark.parametrize("p, word", [(0.1, "no."), (0.5, "unsure."), (0.75, "yes.")])
def test_the_fact_reads_the_probability_as_a_word(snap, trade, p, word):
    facts = trade_jev_facts(trade, snap, FakeJev(yes=p))
    assert facts["JEV.fair"].text.endswith(word)


def test_a_failed_jev_call_gives_no_fact_and_never_raises(snap, trade):
    assert trade_jev_facts(trade, snap, FakeJev(error=JevError("timeout"))) == {}


def test_a_three_side_trade_asks_the_need_and_the_accept_of_each_other_side(snap, trade):
    three = ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": COLLINS, "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": KINCAID, "to": 1}]),
        TradeSide(roster_id=1, gives=[{"player_id": snap.rosters[1][0], "to": 4}])))
    jev = FakeJev()
    facts = trade_jev_facts(three, snap, jev)
    assert set(jev.requests[0].questions) == {"fair", "need.4", "need.12", "need.1", "accept.12", "accept.1"}
    assert set(jev.requests[0].state["teams"]) == {"asker", "partner_1", "partner_2"}
    assert "JEV.accept.1" in facts
