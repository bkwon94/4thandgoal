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
    DEPTH_CHARTS_URL, PBP_URL, SCHEDULES_URL, download, gsis_id, http_get, nflverse_week,
    read_depth_charts, read_drops, read_id_map, read_injuries, read_schedules,
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


def test_read_drops_keeps_a_missing_yardline_as_none(fixture_nflverse_dir, tmp_path):
    # A drop row with NA for yardline_100 has no field position, so it is never in the end zone.
    src = fixture_nflverse_dir / "play_by_play_2026.csv.gz"
    with gzip.open(src, "rt", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [{**r, "yardline_100": "NA"} if r["play_id"] == "2120" else r for r in reader]
        fields = reader.fieldnames
    pbp = tmp_path / "pbp.csv.gz"
    with gzip.open(pbp, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    d = read_drops(pbp, fixture_nflverse_dir / "ftn_charting_2026.csv", 6)
    assert [p.yardline_100 for p in d["00-0040667"]] == [43.0, None, 51.0]


def test_read_schedules_gives_the_bye_week_and_the_late_opponents(fixture_nflverse_dir):
    schedules = read_schedules(fixture_nflverse_dir / "games.csv", 2026)
    assert schedules["SF"].bye_week == 8
    assert schedules["SF"].late_opponents == {15: "LAC", 16: "KC", 17: "PHI"}
    assert schedules["BAL"].bye_week == 13


def test_read_schedules_names_the_rams_as_sleeper_does(fixture_nflverse_dir):
    schedules = read_schedules(fixture_nflverse_dir / "games.csv", 2026)
    assert "LAR" in schedules and "LA" not in schedules
    assert schedules["SF"].late_opponents != {} and schedules["ARI"].late_opponents[17] in schedules


def test_read_schedules_without_the_season_is_none(fixture_nflverse_dir):
    assert read_schedules(fixture_nflverse_dir / "games.csv", 2030) is None


def test_read_depth_charts_gives_the_backfield_in_order(fixture_nflverse_dir):
    charts = read_depth_charts(fixture_nflverse_dir / "depth_charts_2026.csv.gz")
    assert charts["SF"]["RB"] == ["00-0033280", "00-0041052", "00-0040177", "00-0039363"]
    assert "LAR" in charts and "LA" not in charts


def test_read_depth_charts_uses_only_the_latest_snapshot(tmp_path):
    path = tmp_path / "depth_charts_2026.csv"
    path.write_text(
        "dt,team,player_name,gsis_id,pos_abb,pos_slot,pos_rank\n"
        "2026-10-20T12:00:00Z,SF,Old Starter,00-1,RB,11,1\n"
        "2026-10-21T12:00:00Z,SF,New Backup,00-3,RB,11,2\n"
        "2026-10-21T12:00:00Z,SF,New Starter,00-2,RB,11,1\n"
        "2026-10-21T12:00:00Z,SF,New Starter,00-2,RB,12,1\n")
    assert read_depth_charts(path) == {"SF": {"RB": ["00-2", "00-3"]}}


def test_read_depth_charts_without_a_row_is_none(tmp_path):
    path = tmp_path / "depth_charts_2026.csv"
    path.write_text("dt,team,player_name,gsis_id,pos_abb,pos_slot,pos_rank\n")
    assert read_depth_charts(path) is None


def test_the_downloads_cache_the_schedules_and_the_depth_charts(tmp_path):
    seen = []

    def fetch(url):
        seen.append(url)
        if url in (SCHEDULES_URL, DEPTH_CHARTS_URL.format(season=2026)):
            return b"x"
        raise httpx.ConnectError("down")

    nflverse_week(2026, 6, [], {}, tmp_path, fetch=fetch)
    assert SCHEDULES_URL in seen and DEPTH_CHARTS_URL.format(season=2026) in seen
    assert (tmp_path / "games.csv").exists() and (tmp_path / "depth_charts_2026.csv.gz").exists()
