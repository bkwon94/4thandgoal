"""
Tests for the usage and environment of the waiver board.
They read a small play by play at the usage seam and feed hand-set usage at the engine seam.
"""
import csv
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone.models import NflverseWeek, TeamWeek, UsageWeek
from cornerstone.nflverse import read_environment, read_usage
from cornerstone.sleeper import load_raw
from cornerstone.waiver import waiver_board

PBP_FIELDS = ("game_id", "season_type", "week", "posteam", "play_type", "pass", "rush", "receiver_player_id",
              "rusher_player_id", "yardline_100", "success", "down", "score_differential", "qtr",
              "game_seconds_remaining")
SNAP_FIELDS = ("game_type", "week", "pfr_player_id", "team", "offense_snaps", "offense_pct")


def _play(week, team="KC", kind="pass", receiver="", rusher="", yardline=50, success=0, down=1, score=0, qtr=1,
          seconds=3000):
    """One play by play row. A pass with no receiver is a sack or a throw away; a run has a rusher."""
    return {"game_id": f"2026_{week:02d}_{team}", "season_type": "REG", "week": week, "posteam": team,
            "play_type": kind, "pass": int(kind == "pass"), "rush": int(kind == "run"),
            "receiver_player_id": receiver, "rusher_player_id": rusher, "yardline_100": yardline,
            "success": success, "down": down, "score_differential": score, "qtr": qtr,
            "game_seconds_remaining": seconds}


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
    usage = read_usage(pbp, snaps, 6, 5, {"00-W": "100", "00-R": "200"}, {"WideRe00": "100", "BackRu00": "200"})
    receiver = {u.week: u for u in usage["100"]}
    assert (receiver[6].snaps, receiver[6].snap_share, receiver[6].targets, receiver[6].target_share) == (50, 71, 2, 50)
    assert receiver[6].red_zone_touches == 1 and receiver[6].team == "KC"
    assert (receiver[5].snap_share, receiver[5].targets, receiver[5].target_share) == (48, 1, 25)
    back = usage["200"][0]
    assert (back.week, back.carries, back.carry_share, back.red_zone_touches, back.snap_share) == (6, 3, 100, 1, 60)
    # 00-X has no Sleeper ID in the map, so he is not in the usage.
    assert set(usage) == {"100", "200"}


def test_a_week_with_no_play_by_play_rows_gives_no_usage(tmp_path):
    pbp = _csv(tmp_path / "pbp.csv", PBP_FIELDS, [_play(5, receiver="00-W")])
    assert read_usage(pbp, None, 6, 5, {"00-W": "100"}, {}) is None
    assert read_environment(pbp, 6) is None


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
    week = read_environment(pbp, 6)["KC"][0]
    assert (week.week, week.plays, week.passes, week.rushes, week.rush_successes) == (6, 9, 6, 3, 2)
    assert (week.neutral_plays, week.neutral_passes) == (4, 2)
    assert set(read_environment(pbp, 6)) == {"KC", "BUF"}


def test_the_week_extract_carries_the_usage_and_the_environment(nfl_week6):
    # Matthew Golden takes all 4 Packers targets of the fixture, one at the 9, and plays 83% of the snaps.
    golden = nfl_week6.usage["12501"]
    assert [(u.week, u.team, u.snaps, u.snap_share, u.targets, u.target_share, u.red_zone_touches)
            for u in golden] == [(6, "GB", 52, 83, 4, 100, 1)]
    assert nfl_week6.environment["GB"][0].plays == 4 and "LAR" in nfl_week6.environment
    assert nfl_week6.sources["nflverse_snaps"]


BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))


def _player(position, team="KC", name="Free Agent"):
    return {"position": position, "team": team, "status": "Active", "active": True, "full_name": name}


def _raw(fixture_raw_dir, players, per_week):
    """The week 6 raw with `players` added and a flat projection per week, weeks 7 to 17, for each ID in `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw["players"] = {**raw["players"], **players}
    raw["projections_ahead"] = [{"week": w, "projections": dict(per_week)} for w in range(7, 18)]
    return raw


def _usage(week, snap_share, targets=0, carries=0, team="KC"):
    """One usage week. The target share and the carry share are four times the count, as on a team of 25 each."""
    return UsageWeek(week=week, team=team, snaps=snap_share, snap_share=snap_share, targets=targets,
                     target_share=4 * targets, carries=carries, carry_share=4 * carries, red_zone_touches=0)


def _team(plays=60, neutral_passes=30, rush_successes=10):
    """One game of a team with 40 neutral plays and 25 rushes."""
    return [TeamWeek(week=6, plays=plays, passes=plays - 25, rushes=25, rush_successes=rush_successes,
                     neutral_plays=40, neutral_passes=neutral_passes)]


def _nfl(usage, environment=None):
    return NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage,
                        environment=environment or {"KC": _team()})


def _best_adds(raw, nfl):
    return waiver_board(raw, 6, BUILT, nfl).buckets["best_adds"]


def test_a_rising_snap_share_outranks_a_higher_projection_with_flat_usage(fixture_raw_dir):
    players = {"80001": _player("WR", name="Riser"), "80002": _player("WR", name="Steady")}
    raw = _raw(fixture_raw_dir, players, {"80001": 5.0, "80002": 10.0})
    nfl = _nfl({"80001": [_usage(5, 48, targets=2), _usage(6, 71, targets=5)],
                "80002": [_usage(5, 70, targets=6), _usage(6, 70, targets=6)]})
    assert [p.player_id for p in _best_adds(raw, nfl)] == ["80001", "80002"]
