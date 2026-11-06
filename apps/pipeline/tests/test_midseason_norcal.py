"""
Tests for the midseason report of NorCal end to end, from the real saved NorCal data of 2026. NorCal plays no median
game, starts no DEF, and has a fixed bracket, so each rule must read the League settings and never the client name.
"""
import json
from pathlib import Path

import pytest
from fakes import NORCAL_DRAFT_FIXTURES, NORCAL_TRANSACTIONS, FixtureProvider
from test_midseason import _call, _report
from test_midseason_draft import NORCAL_DATA, _norcal_week_8

from cornerstone.pipeline import run_midseason

# The provider of the NorCal build: the saved NorCal week 8, its history, its snake draft, and the full transactions.
NORCAL_PROVIDER = FixtureProvider(raw_dir=NORCAL_DATA / "week-08" / "raw", history_root=NORCAL_DATA / "history",
                                  draft_dir=NORCAL_DRAFT_FIXTURES, transactions=NORCAL_TRANSACTIONS)


@pytest.fixture(scope="module")
def norcal_build(tmp_path_factory) -> Path:
    """The midseason.json of one NorCal build. The build takes some seconds, so the tests of this file share it."""
    client = _norcal_week_8(tmp_path_factory.mktemp("norcal"))
    return run_midseason(2026, 8, _call(), client=client, provider=NORCAL_PROVIDER)


def _chapter(report: dict, key: str) -> dict:
    return next(chapter for act in report["acts"] for chapter in act["chapters"] if chapter["key"] == key)


def test_each_norcal_record_counts_one_game_a_week(norcal_build):
    # AT-2: NorCal plays no median game, so 8 weeks give 8 games.
    teams = _chapter(_report(norcal_build), "state")["facts"]["teams"]
    assert len(teams) == 12
    assert all(team["wins"] + team["losses"] + team.get("ties", 0) == 8 for team in teams)


def test_norcal_position_top_10_has_the_positions_of_its_lineup_and_no_def_list(norcal_build):
    # AT-2: NorCal starts no DEF and no kicker.
    boards = {b["position"]: b["players"] for b in _chapter(_report(norcal_build), "top10")["facts"]["positions"]}
    assert list(boards) == ["QB", "RB", "WR", "TE"]
    assert all(len(players) == 10 for players in boards.values())


def test_the_norcal_sim_has_a_fixed_bracket_with_no_reseed_and_no_median_game(norcal_build):
    # AT-2: 6 seeds, so seeds 1 and 2 get the byes, and seed 1 meets the winner of 4 against 5 in each stored run.
    sim = json.loads((norcal_build.parent / "sim.json").read_text(encoding="utf-8"))
    rule = sim["parameters"]
    assert (rule["reseed"], rule["median_game"], rule["playoff_spots"], rule["bye_count"]) == (False, False, 6, 2)
    assert sim["sample"]
    for run in sim["sample"]:
        seed = {rid: n for n, rid in enumerate(run["table"][:6], start=1)}
        first, second = run["bracket"][0], run["bracket"][1]
        assert sorted((seed[a], seed[b]) for a, b in first) == [(3, 6), (4, 5)]
        top = next(pair for pair in second if seed[pair[0]] == 1)
        assert seed[top[1]] in (4, 5)
