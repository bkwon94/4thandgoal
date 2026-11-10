"""
Tests for the nflverse fetch and parse code.
They read the fixtures cut from the real nflverse and ffverse files.
"""
import csv
import gzip
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from league.nflverse import (
    DEPTH_CHARTS_URL,
    PBP_URL,
    SCHEDULES_URL,
    ScheduledGame,
    download,
    gsis_id,
    http_get,
    nflverse_week,
    read_depth_charts,
    read_drops,
    read_games,
    read_id_map,
    read_injuries,
    read_injury_plays,
    read_kickoffs,
    read_schedules,
)
from league.provider.sleeper import load_raw


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
    assert gsis_id("5927", load_raw(fixture_raw_dir).players, {}) == "00-0035659"


def test_gsis_from_id_map_for_golden(fixture_raw_dir, fixture_nflverse_dir):
    ids = read_id_map(fixture_nflverse_dir / "db_playerids.csv")
    assert gsis_id("12501", load_raw(fixture_raw_dir).players, ids) == "00-0040667"


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
    # The fixture play by play has no injury play, and the fixture schedule has no kickoff time.
    assert nfl_week6.injury_plays == {} and nfl_week6.kickoffs is None


PLAY_FIELDS = ("week", "game_id", "qtr", "time", "posteam", "away_team", "home_team", "desc", "passer_player_id",
               "passer_player_name", "rusher_player_id", "rusher_player_name", "receiver_player_id",
               "receiver_player_name")


def _plays(path, rows):
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PLAY_FIELDS, restval="")
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_read_injury_plays_gives_the_first_injury_play_of_each_carrier(tmp_path):
    game = {"week": "8", "game_id": "2026_08_BAL_LA", "away_team": "BAL", "home_team": "LA"}
    pbp = _plays(tmp_path / "pbp.csv.gz", [
        {**game, "qtr": "1", "time": "10:04", "posteam": "BAL", "passer_player_id": "00-1",
         "passer_player_name": "L.Jackson", "desc": "8-L.Jackson pass incomplete. BAL-8-L.Jackson was injured during "
         "the play. LA-99-A.Donald was injured during the play."},
        {**game, "qtr": "3", "time": "01:00", "posteam": "BAL", "rusher_player_id": "00-1",
         "rusher_player_name": "L.Jackson", "desc": "8-L.Jackson left end. BAL-8-L.Jackson was injured during the play."},
        # Two Rams carriers share the short name J.Smith, so neither gets the play.
        {**game, "qtr": "2", "time": "05:00", "posteam": "LA", "rusher_player_id": "00-2",
         "rusher_player_name": "J.Smith", "desc": "20-J.Smith up the middle. LA-20-J.Smith was injured during the play."},
        {**game, "qtr": "2", "time": "04:00", "posteam": "LA", "receiver_player_id": "00-3",
         "receiver_player_name": "J.Smith", "desc": "pass to 11-J.Smith."},
        {**game, "week": "7", "qtr": "1", "time": "15:00", "posteam": "BAL", "desc": "BAL-1-Z.Flowers was injured during "
         "the play."},
    ])
    plays = read_injury_plays(pbp, 8)
    # The defender is never a carrier, so he has no id, and the second Jackson play is not the first.
    assert list(plays) == ["00-1"]
    play = plays["00-1"]
    assert (play.quarter, play.clock, play.away, play.home) == (1, "10:04", "BAL", "LAR")


def test_read_injury_plays_reads_a_name_with_a_space_or_a_hyphen(tmp_path):
    game = {"week": "8", "game_id": "2026_08_DET_SEA", "away_team": "DET", "home_team": "SEA", "qtr": "4", "time": "02:00"}
    pbp = _plays(tmp_path / "pbp.csv.gz", [
        {**game, "posteam": "DET", "receiver_player_id": "00-4", "receiver_player_name": "A.St. Brown",
         "desc": "pass to 14-A.St. Brown. DET-14-A.St. Brown was injured during the play."},
        {**game, "posteam": "SEA", "receiver_player_id": "00-5", "receiver_player_name": "J.Smith-Njigba",
         "desc": "RECOVERED by DET-99-L.Overton at SEA 47. SEA-11-J.Smith-Njigba was injured during the play."},
    ])
    assert sorted(read_injury_plays(pbp, 8)) == ["00-4", "00-5"]


def test_read_injury_plays_skips_a_malformed_row_with_one_log_line(tmp_path, caplog):
    game = {"week": "8", "game_id": "2026_08_BAL_BUF", "away_team": "BAL", "home_team": "BUF", "posteam": "BAL"}
    pbp = _plays(tmp_path / "pbp.csv.gz", [
        # The quarter is NA, so the row is malformed. The next play of the same carrier is the first good one.
        {**game, "qtr": "NA", "time": "10:04", "passer_player_id": "00-1", "passer_player_name": "L.Jackson",
         "desc": "BAL-8-L.Jackson was injured during the play."},
        {**game, "qtr": "3", "time": "01:00", "rusher_player_id": "00-2", "rusher_player_name": "D.Henry",
         "desc": "BAL-22-D.Henry was injured during the play. BAL-8-L.Jackson was injured during the play."},
    ])
    plays = read_injury_plays(pbp, 8)
    assert sorted(plays) == ["00-1", "00-2"] and plays["00-1"].quarter == 3
    skipped = [r for r in caplog.records if "malformed" in r.getMessage()]
    assert len(skipped) == 1 and "L.Jackson" in skipped[0].getMessage()


def test_nflverse_week_with_no_play_by_play_and_no_schedule_has_no_injury_plays_and_no_kickoffs(tmp_path):
    # Every download fails and the cache is empty, so the build goes on with no game story inputs.
    nfl = nflverse_week(2026, 8, [], {}, tmp_path, fetch=_boom)
    assert nfl.injury_plays is None and nfl.kickoffs is None


def test_read_injury_plays_without_the_week_is_none(tmp_path):
    pbp = _plays(tmp_path / "pbp.csv.gz", [{"week": "7", "desc": "BAL-8-L.Jackson was injured during the play."}])
    assert read_injury_plays(pbp, 8) is None


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


def test_read_schedules_gives_the_bye_week_and_the_playoff_opponents(fixture_nflverse_dir):
    schedules = read_schedules(fixture_nflverse_dir / "games.csv", 2026)
    assert schedules["SF"].bye_week == 8
    assert schedules["SF"].playoff_opponents == {15: "LAC", 16: "KC", 17: "PHI"}
    assert schedules["BAL"].bye_week == 13


def test_read_schedules_gives_the_opponent_and_the_home_team_of_each_week(fixture_nflverse_dir):
    # JAX plays at BAL in week 9 and at TEN in week 10. NYJ plays BUF at home in week 10.
    schedules = read_schedules(fixture_nflverse_dir / "games.csv", 2026)
    assert schedules["JAX"].games[9] == ScheduledGame(opponent="BAL", home=False)
    assert schedules["JAX"].games[10] == ScheduledGame(opponent="TEN", home=False)
    assert schedules["NYJ"].games[10] == ScheduledGame(opponent="BUF", home=True)
    # A bye week has no game.
    assert 7 not in schedules["JAX"].games


def test_read_schedules_names_the_rams_as_sleeper_does(fixture_nflverse_dir):
    schedules = read_schedules(fixture_nflverse_dir / "games.csv", 2026)
    assert "LAR" in schedules and "LA" not in schedules
    assert schedules["SF"].playoff_opponents != {} and schedules["ARI"].playoff_opponents[17] in schedules


def test_read_schedules_without_the_season_is_none(fixture_nflverse_dir):
    assert read_schedules(fixture_nflverse_dir / "games.csv", 2030) is None


def test_read_games_gives_the_away_and_home_teams_of_the_week(fixture_nflverse_dir):
    games = read_games(fixture_nflverse_dir / "games.csv", 2026, 7)
    assert games[0] == ("NE", "CHI") and ("KC", "SEA") in games and ("LAR", "LV") in games
    assert len(games) == 14


def test_read_games_without_the_week_is_none(fixture_nflverse_dir):
    assert read_games(fixture_nflverse_dir / "games.csv", 2030, 7) is None


def test_read_kickoffs_gives_the_eastern_kickoff_of_each_team_of_the_week(tmp_path):
    path = tmp_path / "games.csv"
    path.write_text(
        "game_id,season,game_type,week,gameday,gametime,away_team,home_team\n"
        "2026_07_NE_CHI,2026,REG,7,2026-10-22,20:15,NE,CHI\n"
        "2026_07_ARI_LA,2026,REG,7,2026-10-25,16:25,ARI,LA\n"
        "2026_07_SF_ATL,2026,REG,7,2026-10-25,NA,SF,ATL\n"
        "2026_08_NE_BUF,2026,REG,8,2026-11-01,13:00,NE,BUF\n"
        "2025_07_NE_CHI,2025,REG,7,2025-10-19,13:00,NE,CHI\n",
        encoding="utf-8")
    kickoffs = read_kickoffs(path, 2026, 7)
    eastern = ZoneInfo("America/New_York")
    assert kickoffs == {
        "NE": datetime(2026, 10, 22, 20, 15, tzinfo=eastern), "CHI": datetime(2026, 10, 22, 20, 15, tzinfo=eastern),
        "ARI": datetime(2026, 10, 25, 16, 25, tzinfo=eastern), "LAR": datetime(2026, 10, 25, 16, 25, tzinfo=eastern),
    }


def test_read_kickoffs_of_a_file_with_no_game_time_is_empty(fixture_nflverse_dir):
    # A row with no kickoff time gives no kickoff, so its game counts as final.
    assert read_kickoffs(fixture_nflverse_dir / "games.csv", 2026, 7) == {}


def test_read_depth_charts_gives_the_backfield_in_order(fixture_nflverse_dir):
    charts = read_depth_charts(fixture_nflverse_dir / "depth_charts_2026.csv.gz").charts
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
    assert read_depth_charts(path).charts == {"SF": {"RB": ["00-2", "00-3"]}}


def test_read_depth_charts_gives_back_the_newest_dt(fixture_nflverse_dir):
    # The age rule of the step-up reads the scrape time of the newest snapshot. Decision 02 of grade-clarity.
    path = fixture_nflverse_dir / "depth_charts_2026.csv.gz"
    assert read_depth_charts(path).dt == datetime(2026, 10, 21, 12, 53, 27, tzinfo=ZoneInfo("UTC"))


def test_read_depth_charts_skips_a_row_with_a_bad_rank(tmp_path):
    path = tmp_path / "depth_charts_2026.csv"
    path.write_text(
        "dt,team,player_name,gsis_id,pos_abb,pos_slot,pos_rank\n"
        "2026-10-21T12:00:00Z,SF,Starter,00-1,RB,11,1\n"
        "2026-10-21T12:00:00Z,SF,Bad Row,00-9,RB,11,NA\n"
        "2026-10-21T12:00:00Z,SF,Backup,00-2,RB,11,2\n")
    assert read_depth_charts(path).charts == {"SF": {"RB": ["00-1", "00-2"]}}


@pytest.mark.serial
def test_a_second_read_of_the_same_depth_chart_file_takes_no_time(tmp_path):
    # Each press builds a live snapshot, and the season file holds a snapshot of every day, about 800,000 rows. A
    # full parse per press cost about 2.4 s of the 30 s of an analyze press (AT-33).
    path = tmp_path / "depth_charts_2026.csv"
    lines = ["dt,team,player_name,gsis_id,pos_abb,pos_slot,pos_rank"]
    lines += [f"2026-10-{day:02d}T12:00:00Z,SF,Back {n},00-{n},RB,11,{n % 5 + 1}"
              for day in range(1, 21) for n in range(5000)]
    path.write_text("\n".join(lines) + "\n")
    first = read_depth_charts(path)
    started = time.monotonic()
    assert read_depth_charts(path) == first
    assert time.monotonic() - started < 0.05


def test_a_depth_chart_file_that_changes_on_disk_is_read_again(tmp_path):
    path = tmp_path / "depth_charts_2026.csv"
    header = "dt,team,player_name,gsis_id,pos_abb,pos_slot,pos_rank\n"
    path.write_text(header + "2026-10-21T12:00:00Z,SF,Starter,00-1,RB,11,1\n")
    assert read_depth_charts(path).charts == {"SF": {"RB": ["00-1"]}}
    path.write_text(header + "2026-10-22T12:00:00Z,SF,New Starter,00-22,RB,11,1\n")
    os.utime(path, ns=(time.time_ns(), time.time_ns() + 10**9))
    assert read_depth_charts(path).charts == {"SF": {"RB": ["00-22"]}}


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
