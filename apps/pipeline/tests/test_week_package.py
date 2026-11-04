"""
Tests for the week package through its published file: page.json of the week 6 fixtures, built for a test client.
Each client is the CPC client with one change: the median game off, no DEF slot, or the package list ["week"].
"""
import json

import pytest
from cpc import cpc_client

from cornerstone.sheet import build_bundle
from facts.writer import template_blurb
from league.history import load_history
from league.parse import parse_week
from league.provider.sleeper import load_raw
from league.snapshot import week_snapshot
from week.page import render_page_json


def _page(client, raw_dir, history_root, site_dir) -> tuple[dict, object]:
    """The page.json of week 6 for `client`, with a template blurb for each chapter, and the bundle it came from."""
    raw = load_raw(raw_dir)
    bundle = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(history_root, raw, week=6),
                          snapshot=week_snapshot(raw, history_root, 6, client=client), client=client)
    blurbs = {c.key: template_blurb(c, bundle.sheet) for c in bundle.sheet.chapters}
    return json.loads(render_page_json(bundle, blurbs, site_dir).read_text(encoding="utf-8")), bundle


def _week_only(client):
    return client.model_copy(update={"values": client.values.model_copy(update={"packages": ["week"]})})


@pytest.fixture
def page_of(fixture_raw_dir, fixture_history_root, tmp_path):
    return lambda client: _page(client, fixture_raw_dir, fixture_history_root, tmp_path / "site")


def test_cpc_with_its_median_game_has_the_median_game_chapter(page_of):
    page, bundle = page_of(cpc_client())
    assert page["median"] is not None
    assert "median" in page["blurbs"]
    assert "median" in [c.key for c in bundle.sheet.chapters]


def test_a_league_with_no_median_game_has_no_median_game_chapter_in_page_json(page_of):
    page, bundle = page_of(cpc_client(median_game=False))
    assert page["median"] is None
    assert "median" not in page["blurbs"]
    assert "median" not in [c.key for c in bundle.sheet.chapters]
    assert not [fid for fid in bundle.sheet.facts if fid.startswith("MED.")]
    # The impact fact of each matchup has no median part either.
    assert not [f.id for f in bundle.sheet.facts.values() if f.id.endswith(".impact") and "median" in f.text]


def test_a_league_with_no_def_slot_has_no_def_in_the_pool_and_the_leaders(page_of, fixture_raw_dir,
                                                                           fixture_history_root):
    slots = tuple(slot for slot in cpc_client().settings.roster_slots if slot != "DEF")
    assert "DEF" in cpc_client().settings.positions
    client = cpc_client(roster_slots=slots)
    page, bundle = page_of(client)
    assert [board["position"] for board in page["leaders"]] == ["QB", "RB", "WR", "TE"]
    assert not [lead for lead in bundle.data.leaders if lead.position == "DEF"]
    assert not [fid for fid in bundle.sheet.facts if fid.startswith("LEAD.DEF")]
    # The pool of the league: the positions it starts, as the snapshot and the waiver board read them.
    assert "DEF" not in client.settings.positions
    snapshot = week_snapshot(load_raw(fixture_raw_dir), fixture_history_root, 6, client=client)
    assert not [p for players in snapshot.free_agents.values() for p in players if p.position == "DEF"]


def test_a_client_with_only_week_has_no_rankings_chapter_and_no_odds(page_of):
    page, bundle = page_of(_week_only(cpc_client()))
    assert "rankings" not in [c.key for c in bundle.sheet.chapters]
    assert "rankings" not in page["blurbs"]
    assert bundle.odds is None
    assert not [fid for fid in bundle.sheet.facts if fid.startswith(("PR.", "ODDS.", "SW."))]
    # The week keeps each of its own chapters.
    assert {"motw", "awards", "median", "next_week"} <= {c.key for c in bundle.sheet.chapters}


def test_cpc_gets_the_rankings_chapter_through_the_chapter_port(page_of):
    page, bundle = page_of(cpc_client())
    assert bundle.sheet.chapters[-1].key == "rankings"
    assert "rankings" in page["blurbs"]
    assert bundle.odds is not None
