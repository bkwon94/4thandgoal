"""
Tests for the facts of the sheet on the quality of the NFL team and on the chart value of a traded player.
They build the week 6 snapshot from the real fixtures, with the real team stats file of nflverse, and call no model.
"""
import shutil

import pytest
from cpc import cpc_client, four_week

from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.trade_facts import trade_fact_sheet
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
# Roster 12 gives Omarion Hampton (LAC, on the chart) to roster 4 for Rome Odunze (CHI, not on the chart).
HAMPTON, ODUNZE = "12507", "11620"


@pytest.fixture
def make_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)

    def make(*, chart=chart_week6, team_stats=True):
        if not team_stats:
            (cache / "stats_team_week_2026.csv.gz").unlink()
        slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
        return four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart, slow, client=CLIENT))

    return make


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, asker=12, sides=(
        TradeSide(roster_id=12, gives=[{"player_id": HAMPTON, "to": 4}]),
        TradeSide(roster_id=4, gives=[{"player_id": ODUNZE, "to": 12}])))


def test_the_sheet_states_the_quality_of_the_nfl_team_of_each_traded_player(make_snap, trade):
    facts = trade_fact_sheet(trade, make_snap())
    hampton = facts[f"{HAMPTON}.nfl_team"]
    # The Chargers have the fewest expected points per play of the 32 offenses in weeks 1 to 5.
    assert "Omarion Hampton" in hampton.text and "Chargers" in hampton.text
    assert "32nd of 32" in hampton.text and "5 games" in hampton.text
    assert {"32", "5", "-18.82"} <= set(hampton.numbers)
    assert hampton.players == ["Omarion Hampton"]
    assert "Bears" in facts[f"{ODUNZE}.nfl_team"].text


def test_the_sheet_has_no_nfl_team_fact_when_the_team_stats_file_is_missing(make_snap, trade):
    facts = trade_fact_sheet(trade, make_snap(team_stats=False))
    assert not [fid for fid in facts if fid.endswith(".nfl_team")]


def test_a_traded_player_on_the_chart_has_one_fact_with_his_value(make_snap, trade):
    facts = trade_fact_sheet(trade, make_snap())
    assert facts[f"{HAMPTON}.value"].text == "Omarion Hampton's trade value is 68.5 in the week of the trade."


def test_a_traded_player_not_on_the_chart_has_a_fact_that_says_so(make_snap, trade):
    facts = trade_fact_sheet(trade, make_snap())
    assert facts[f"{ODUNZE}.value"].text == "Rome Odunze is not on the chart of week 6."
    assert facts[f"{ODUNZE}.value"].players == ["Rome Odunze"]


def test_a_week_with_no_chart_has_one_fact_that_says_the_chart_is_missing(make_snap, trade):
    facts = trade_fact_sheet(trade, make_snap(chart=None))
    assert facts["trade.chart"].text == "The chart of week 6 is missing, so no player has a chart value."
    assert not [fid for fid in facts if fid.endswith(".value")]
    assert "trade.chart" not in trade_fact_sheet(trade, make_snap())
