"""
Tests for the nflverse fetch and parse code.
They read the fixtures cut from the real nflverse and ffverse files.
"""
import csv
import gzip
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


# The 28 Sleeper team codes of the week 6 starters who played. Sleeper writes LAR for the Rams.
WEEK_6_TEAMS = {
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CLE", "DAL", "DEN", "GB", "HOU", "IND", "JAX", "KC",
    "LAC", "LAR", "LV", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS",
}


def _without_game(src, dst, game_key, game_id):
    """Copy a fixture file without the rows of one game, so the copy holds a partial week."""
    opener = gzip.open if src.suffix == ".gz" else open
    with opener(src, "rt", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r[game_key] != game_id]
        fields = reader.fieldnames
    with opener(dst, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return dst


def test_read_drops_with_every_game_and_team(fixture_nflverse_dir):
    d = read_drops(fixture_nflverse_dir / "play_by_play_2026.csv.gz",
                   fixture_nflverse_dir / "ftn_charting_2026.csv", 6, WEEK_6_TEAMS)
    assert len(d["00-0040667"]) == 3


def test_read_drops_with_a_game_missing_from_ftn_is_none(fixture_nflverse_dir, tmp_path):
    # Play-by-play has 14 games and FTN 13: FTN has not charted the last game yet.
    ftn = _without_game(fixture_nflverse_dir / "ftn_charting_2026.csv", tmp_path / "ftn.csv",
                        "nflverse_game_id", "2026_06_WAS_SF")
    assert read_drops(fixture_nflverse_dir / "play_by_play_2026.csv.gz", ftn, 6) is None


def test_read_drops_with_a_team_missing_from_play_by_play_is_none(fixture_nflverse_dir, tmp_path):
    # The Monday game is not in either file yet, but Sleeper says its starters played.
    pbp = _without_game(fixture_nflverse_dir / "play_by_play_2026.csv.gz", tmp_path / "pbp.csv.gz",
                        "game_id", "2026_06_ARI_LA")
    ftn = _without_game(fixture_nflverse_dir / "ftn_charting_2026.csv", tmp_path / "ftn.csv",
                        "nflverse_game_id", "2026_06_ARI_LA")
    assert read_drops(pbp, ftn, 6) is not None
    assert read_drops(pbp, ftn, 6, WEEK_6_TEAMS) is None
    assert read_drops(pbp, ftn, 6, WEEK_6_TEAMS - {"ARI", "LAR"}) is not None


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
