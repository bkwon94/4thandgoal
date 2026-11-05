"""
Tests for the nflverse usage and environment readers.
They read a small hand-built play by play and snap counts file, the week extract from the fixtures, and a real
week 6 play by play cut of six teams beside the nflverse targets of the same team weeks.
"""
import csv
import gzip
from collections import Counter
from pathlib import Path

import httpx

from league.nflverse import nflverse_week
from league.nflverse_rows import _sleeper_team
from league.nflverse_usage import read_environment, read_plays, read_snaps, read_usage

FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"
PBP_FIELDS = ("game_id", "season_type", "week", "posteam", "play_type", "two_point_attempt", "pass", "rush",
              "receiver_player_id", "rusher_player_id", "yardline_100", "success", "down", "score_differential",
              "qtr", "game_seconds_remaining", "epa", "pass_oe")
SNAP_FIELDS = ("game_type", "week", "pfr_player_id", "team", "offense_snaps", "offense_pct")


def _play(week, team="KC", kind="pass", receiver="", rusher="", yardline=50, success=0, down=1, score=0, qtr=1,
          seconds=3000, two_point=0, epa=0.25, pass_oe=-12.5):
    """One play by play row. A pass with no receiver is a sack or a throw away; a run has a rusher.

    The default epa and pass_oe are hand-set values in the range of real plays, not values from a real play.
    """
    return {"game_id": f"2026_{week:02d}_{team}", "season_type": "REG", "week": week, "posteam": team,
            "play_type": kind, "two_point_attempt": two_point, "pass": int(kind == "pass"), "rush": int(kind == "run"),
            "receiver_player_id": receiver, "rusher_player_id": rusher, "yardline_100": yardline,
            "success": success, "down": down, "score_differential": score, "qtr": qtr,
            "game_seconds_remaining": seconds, "epa": epa, "pass_oe": pass_oe}


def _csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _snap(week, pfr, snaps, pct, team="KC"):
    return {"game_type": "REG", "week": week, "pfr_player_id": pfr, "team": team, "offense_snaps": snaps,
            "offense_pct": pct}


def test_the_usage_reader_gives_snaps_targets_carries_and_shares_per_week(tmp_path):
    # Week 6: the receiver takes 2 of 4 targets, one at the 15; the back takes 3 of 3 carries.
    week6 = [_play(6, receiver="00-W", yardline=15), _play(6, receiver="00-W"), _play(6, receiver="00-X"),
             _play(6, receiver="00-X"), _play(6, kind="run", rusher="00-R"), _play(6, kind="run", rusher="00-R"),
             _play(6, kind="run", rusher="00-R", yardline=3)]
    week5 = [_play(5, receiver="00-W"), _play(5, receiver="00-X"), _play(5, receiver="00-X"),
             _play(5, receiver="00-X")]
    pbp = _csv(tmp_path / "pbp.csv", PBP_FIELDS, week5 + week6)
    snaps = _csv(tmp_path / "snaps.csv", SNAP_FIELDS,
                 [_snap(5, "WideRe00", 30, 0.48), _snap(6, "WideRe00", 50, 0.71), _snap(6, "BackRu00", 40, 0.6)])
    snap_weeks = read_snaps(snaps, 5, 6, {"WideRe00": "100", "BackRu00": "200"})
    usage = read_usage(read_plays(pbp, 6), snap_weeks, 6, 5, {"00-W": "100", "00-R": "200"})
    receiver = {u.week: u for u in usage["100"]}
    assert (receiver[6].snaps, receiver[6].snap_share, receiver[6].targets, receiver[6].target_share) == (50, 71, 2, 50)
    assert receiver[6].red_zone_touches == 1 and receiver[6].team == "KC"
    assert (receiver[5].snap_share, receiver[5].targets, receiver[5].target_share) == (48, 1, 25)
    back = usage["200"][0]
    assert (back.week, back.carries, back.carry_share, back.red_zone_touches, back.snap_share) == (6, 3, 100, 1, 60)
    # 00-X has no Sleeper ID in the map, so he is not in the usage.
    assert set(usage) == {"100", "200"}


def test_a_two_point_try_is_no_target_no_carry_and_no_red_zone_touch(tmp_path):
    # nflverse counts a target only on a play with a receiver and no two-point try. Each try is at the 2 or the 1.
    plays = [_play(6, receiver="00-W", yardline=10), _play(6, receiver="00-X"),
             _play(6, receiver="00-W", yardline=2, two_point=1), _play(6, kind="run", rusher="00-R"),
             _play(6, kind="run", rusher="00-R", yardline=2, two_point=1)]
    pbp = _csv(tmp_path / "pbp.csv", PBP_FIELDS, plays)
    usage = read_usage(read_plays(pbp, 6), {}, 6, 6, {"00-W": "100", "00-R": "200"})
    receiver, back = usage["100"][0], usage["200"][0]
    assert (receiver.targets, receiver.target_share, receiver.red_zone_touches) == (1, 50, 1)
    assert (back.carries, back.carry_share, back.red_zone_touches) == (1, 100, 0)


def test_the_target_count_equals_the_nflverse_count_for_every_team_week():
    # The play by play holds every week 6 play of six teams, and the weekly player file holds the nflverse targets
    # of the same team weeks. Both are cut from the real 2026 files. The DAL week has a two-point pass with a receiver.
    plays = read_plays(FIXTURES / "play_by_play_2026_week6_six_teams.csv.gz", 6)
    receivers = {play["receiver_player_id"] for play in plays if play["receiver_player_id"]}
    usage = read_usage(plays, {}, 6, 6, {gsis: gsis for gsis in receivers})
    ours = Counter()
    for weeks in usage.values():
        for u in weeks:
            ours[(u.team, u.week)] += u.targets
    theirs = Counter()
    # The player file also holds other weeks and teams of the week 6 fixture players, so only the cut's teams count.
    teams = {play["posteam"] for play in plays}
    with gzip.open(FIXTURES / "stats_player_week_2026.csv.gz", "rt", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["week"] == "6" and row["team"] in teams:
                theirs[(_sleeper_team(row["team"]), int(row["week"]))] += int(row["targets"])
    assert len(theirs) == 6
    assert ours == theirs


def test_a_week_with_no_play_by_play_rows_gives_no_plays(tmp_path):
    pbp = _csv(tmp_path / "pbp.csv", PBP_FIELDS, [_play(5, receiver="00-W")])
    assert read_plays(pbp, 6) is None


def test_the_environment_reader_counts_plays_neutral_passes_and_rush_successes(tmp_path):
    neutral = [_play(6, receiver="00-W"), _play(6), _play(6, kind="run", rusher="00-R", success=1),
               _play(6, kind="run", rusher="00-R", down=2)]
    # Each of these plays counts as a play but not as a neutral one.
    other = [_play(6, receiver="00-W", down=3), _play(6, receiver="00-W", score=-8),
             _play(6, receiver="00-W", qtr=2, seconds=1900), _play(6, receiver="00-W", qtr=4, seconds=600),
             _play(6, kind="run", rusher="00-R", success=1, down=4)]
    # A kick and a kneel are not plays.
    not_plays = [_play(6, kind="field_goal"), _play(6, kind="qb_kneel")]
    pbp = _csv(tmp_path / "pbp.csv", PBP_FIELDS, neutral + other + not_plays + [_play(6, team="BUF")])
    environment = read_environment(read_plays(pbp, 6))
    week = environment["KC"][0]
    assert (week.week, week.plays, week.passes, week.rushes, week.rush_successes) == (6, 9, 6, 3, 2)
    assert (week.neutral_plays, week.neutral_passes) == (4, 2)
    assert set(environment) == {"KC", "BUF"}


def test_the_environment_reader_sums_epa_and_pass_oe(tmp_path):
    plays = [_play(6, receiver="00-W", epa=1.75, pass_oe=40.0), _play(6, epa=-2.0, pass_oe=10.0),
             _play(6, kind="run", rusher="00-R", epa=0.5, pass_oe=-30.0)]
    # A two-point try, a kneel, a spike, and a kick add nothing. A try has no down, so its pass_oe is empty.
    not_plays = [_play(6, receiver="00-W", two_point=1, down="", epa=3.0, pass_oe=""),
                 _play(6, kind="run", rusher="00-R", two_point=1, down="", epa=-1.0, pass_oe=""),
                 _play(6, kind="qb_kneel", epa=-0.4, pass_oe=""), _play(6, kind="qb_spike", epa=-0.1, pass_oe=""),
                 _play(6, kind="punt", epa=0.8, pass_oe="")]
    pbp = _csv(tmp_path / "pbp.csv", PBP_FIELDS, plays + not_plays)
    week = read_environment(read_plays(pbp, 6))["KC"][0]
    assert (week.plays, week.passes, week.rushes) == (3, 2, 1)
    assert (week.epa, week.pass_oe) == (0.25, 20.0)
    assert (week.epa_per_play, week.pass_rate_over_expected) == (0.25 / 3, 20.0 / 3)


def test_the_environment_reader_matches_the_dallas_week_6_sums():
    # A script outside the reader summed these numbers from the fixture rows: 70 pass and run plays, with the one
    # two-point pass left out.
    # The EPA sum is -8.46435826329979 and the pass_oe sum is 357.572077214718.
    plays = read_plays(FIXTURES / "play_by_play_2026_week6_six_teams.csv.gz", 6)
    week = read_environment(plays)["DAL"][0]
    assert (week.week, week.plays, week.passes, week.rushes) == (6, 70, 56, 14)
    assert round(week.epa_per_play, 4) == -0.1209
    assert round(week.pass_rate_over_expected, 4) == 5.1082


def test_the_week_extract_carries_the_usage_and_the_environment(nfl_week6):
    # Matthew Golden takes all 4 Packers targets of the fixture, one at the 9, and plays 83% of the snaps.
    # The weekly player file replaces the targets and the target share with its own: 13 at 33%.
    golden = nfl_week6.usage["12501"]
    assert [(u.week, u.team, u.snaps, u.snap_share, u.targets, u.target_share, u.red_zone_touches)
            for u in golden] == [(6, "GB", 52, 83, 13, 33, 1)]
    assert nfl_week6.environment["GB"][0].plays == 4 and "LAR" in nfl_week6.environment
    assert nfl_week6.sources["nflverse_snaps"]


def _boom(url):
    raise httpx.ConnectError("down")


def test_the_extract_saves_4_weeks_of_usage(tmp_path):
    # The play by play holds weeks 2 to 6, so week 2 is one week too old to save.
    with gzip.open(tmp_path / "play_by_play_2026.csv.gz", "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PBP_FIELDS)
        writer.writeheader()
        writer.writerows(_play(w, receiver="00-W") for w in range(2, 7))
    _csv(tmp_path / "snap_counts_2026.csv", SNAP_FIELDS, [_snap(w, "WideRe00", 40, 0.6) for w in range(2, 7)])
    _csv(tmp_path / "db_playerids.csv", ("sleeper_id", "gsis_id", "pfr_id"), [{"sleeper_id": "100", "gsis_id": "00-W",
                                                                              "pfr_id": "WideRe00"}])
    nfl = nflverse_week(2026, 6, [], {"100": {"position": "WR"}}, tmp_path, fetch=_boom)
    assert [u.week for u in nfl.usage["100"]] == [3, 4, 5, 6]
    assert all(u.snap_share == 60 for u in nfl.usage["100"])
