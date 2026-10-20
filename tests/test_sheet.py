"""
Tests for the fact sheet, the bundle, and the week gate.
They run on the recorded week 6 data.
"""
from datetime import date

import pytest

from cornerstone.parse import parse_week
from cornerstone.sheet import (
    build_bundle,
    check_week_is_buildable,
    fmt,
    read_bundle,
    week_dates,
    write_bundle,
)
from cornerstone.sleeper import load_raw


@pytest.fixture
def bundle(fixture_raw_dir):
    return build_bundle(parse_week(load_raw(fixture_raw_dir)))


def test_week_dates():
    assert week_dates(date(2026, 9, 9), 6) == "Oct 15 – Oct 19, 2026"


def test_gate_messages():
    assert check_week_is_buildable(6, 6) is None
    assert "not final" in check_week_is_buildable(7, 6)
    assert "playoff" in check_week_is_buildable(15, 15)


def test_fmt_keeps_the_shortest_form():
    assert [fmt(106.83), fmt(24.2), fmt(21.0), fmt(106.80)] == ["106.83", "24.2", "21", "106.8"]


def test_bundle_roundtrip_and_ids(bundle, tmp_path):
    b = bundle
    assert b.data.dates == "Oct 15 – Oct 19, 2026"
    assert {c.key for c in b.sheet.chapters} >= {"motw", "game_changer", "awards", "median", "next_week", "recap_4"}
    motw = next(c for c in b.sheet.chapters if c.key == "motw")
    assert all(fid in b.sheet.facts for fid in motw.fact_ids)
    assert set(motw.scope_teams) == {"behold the lamb", "Bo Girds"}
    f = b.sheet.facts["MED.value"]
    assert "106.83" in f.text and "106.83" in f.numbers
    write_bundle(b, tmp_path / "facts.json")
    assert read_bundle(tmp_path / "facts.json").data.week == 6


def test_every_number_appears_in_its_text(bundle):
    for f in bundle.sheet.facts.values():
        assert all(n in f.text for n in f.numbers), f.id


def test_every_chapter_fact_id_exists(bundle):
    for c in bundle.sheet.chapters:
        assert all(fid in bundle.sheet.facts for fid in c.fact_ids), c.key


def test_upset_fact_exists_for_matchup_4_only_when_the_lower_rank_won(bundle):
    # The 8th-ranked team beat the 3rd-ranked team before this week, so M4 is an upset.
    assert "upset" in bundle.sheet.facts["M4.upset"].text
    assert "M1.upset" not in bundle.sheet.facts


def test_median_closest_carries_the_gap(bundle):
    assert "2.79" in bundle.sheet.facts["MED.closest"].text


def test_recap_scope_players_cover_both_rosters(bundle):
    recap = next(c for c in bundle.sheet.chapters if c.key == "recap_4")
    assert "Tyler Shough" in recap.scope_players
    assert "Tre Tucker" not in recap.scope_players
