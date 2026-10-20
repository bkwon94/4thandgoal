"""
Tests for the nflverse fetch and parse code.
They read the fixtures cut from the real nflverse and ffverse files.
"""
import os

import httpx
import pytest

from cornerstone.nflverse import (
    PBP_URL, download, gsis_id, http_get, read_drops, read_id_map, read_injuries,
)
from cornerstone.sleeper import load_raw


def _boom(url):
    raise httpx.ConnectError("down")


def test_read_drops_golden(fixture_nflverse_dir):
    d = read_drops(fixture_nflverse_dir / "play_by_play_2026.csv.gz",
                   fixture_nflverse_dir / "ftn_charting_2026.csv", 6)
    assert [(p.play_id, p.air_yards, p.yardline_100) for p in d["00-0040667"]] == [
        ("1332", 39.0, 43.0), ("2120", 23.0, 23.0), ("2852", 5.0, 51.0)]


def test_read_drops_keeps_a_negative_air_yards(fixture_nflverse_dir):
    d = read_drops(fixture_nflverse_dir / "play_by_play_2026.csv.gz",
                   fixture_nflverse_dir / "ftn_charting_2026.csv", 6)
    assert [p.air_yards for p in d["00-0037840"]] == [4.0, -6.0]


def test_read_drops_without_the_week_is_none(fixture_nflverse_dir):
    assert read_drops(fixture_nflverse_dir / "play_by_play_2026.csv.gz",
                      fixture_nflverse_dir / "ftn_charting_2026.csv", 7) is None


def test_read_injuries(fixture_nflverse_dir):
    inj = read_injuries(fixture_nflverse_dir / "injuries_2026.csv.gz", 6)
    assert inj["00-0031588"] == {5: "Out", 6: "Questionable"}
    assert inj["00-0035659"] == {4: "Questionable", 5: "Questionable"}
    assert read_injuries(fixture_nflverse_dir / "injuries_2026.csv.gz", 7) is None


def test_gsis_from_blob_strips_space(fixture_raw_dir):
    assert gsis_id("5927", load_raw(fixture_raw_dir)["players"], {}) == "00-0035659"


def test_gsis_from_id_map_for_golden(fixture_raw_dir, fixture_nflverse_dir):
    ids = read_id_map(fixture_nflverse_dir / "db_playerids.csv")
    assert gsis_id("12501", load_raw(fixture_raw_dir)["players"], ids) == "00-0040667"


def test_download_falls_back_to_a_stale_cache(tmp_path):
    path = tmp_path / "f.csv"
    path.write_text("old")
    os.utime(path, (0, 0))
    assert download("u", path, fetch=_boom) == path and path.read_text() == "old"
    assert download("u", tmp_path / "none.csv", fetch=_boom) is None


def test_download_replaces_a_stale_cache(tmp_path):
    path = tmp_path / "f.csv"
    path.write_text("old")
    os.utime(path, (0, 0))
    assert download("u", path, fetch=lambda url: b"new") == path
    assert path.read_text() == "new"


def test_download_keeps_a_fresh_cache(tmp_path):
    path = tmp_path / "f.csv"
    path.write_text("fresh")
    assert download("u", path, fetch=_boom) == path and path.read_text() == "fresh"


def test_nflverse_week_from_fixtures(nfl_week6):
    assert all(nfl_week6.sources.values())
    assert len(nfl_week6.drops["12501"]) == 3
    assert nfl_week6.gsis["12501"] == "00-0040667"


@pytest.mark.live
def test_live_download_of_the_play_by_play(tmp_path):
    path = download(PBP_URL.format(season=2026), tmp_path / "pbp.csv.gz", fetch=http_get)
    assert path is not None and path.stat().st_size > 0
