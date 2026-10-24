"""
Parse the player usage and the team environment from the nflverse play by play and snap count files.
The waiver board reads both: the usage trend of each player and the offense around him.
"""
from collections import Counter
from pathlib import Path
from typing import NamedTuple

from cornerstone.history import _round_half_up
from cornerstone.models import TeamWeek, UsageWeek
from cornerstone.nflverse_rows import _number, _rows, _sleeper_team, _yardline

# The play types of an offensive play. A kneel, a spike, a penalty with no play, and a kick are not plays.
PLAY_TYPES = ("pass", "run")
# The play by play columns the two readers use. A play keeps only these, so the plays of a season fit in memory.
PLAY_COLUMNS = ("week", "posteam", "two_point_attempt", "pass", "rush", "receiver_player_id", "rusher_player_id",
                "yardline_100", "success", "down", "score_differential", "qtr", "game_seconds_remaining", "epa",
                "pass_oe")
# A target or a carry at this yard line or closer to the end zone is a red zone touch.
RED_ZONE_YARDS = 20
# A neutral down: the score is within this many points either way.
NEUTRAL_SCORE = 7
# Game seconds left at the two-minute warning of the first half.
HALF_TWO_MINUTES_SECONDS = 1800 + 120


class SnapWeek(NamedTuple):
    """One snap counts row of a player: his offensive snaps, his snap share in percent, and his Sleeper team code."""
    snaps: int
    share: int
    team: str


def _share(part: int, whole: int) -> int:
    return int(_round_half_up(100 * part / whole)) if whole else 0


def _regular_week(row: dict[str, str], season_key: str) -> int | None:
    """The week of a regular season row. None for a playoff row or a row with no week."""
    if row.get(season_key, "REG") != "REG" or not row["week"].isdigit():
        return None
    return int(row["week"])


def read_plays(pbp: Path, week: int) -> list[dict[str, str]] | None:
    """The offensive plays of weeks 1 to `week`, regular season only. None when the file has no row for week `week`.

    The usage reader and the environment reader both take these plays, so the large file is parsed once.
    """
    has_week = False
    plays = []
    for row in _rows(pbp):
        row_week = _regular_week(row, "season_type")
        has_week = has_week or row_week == week
        if row_week is not None and row_week <= week and row["play_type"] in PLAY_TYPES:
            plays.append({column: row[column] for column in PLAY_COLUMNS})
    return plays if has_week else None


def read_snaps(
    snaps: Path, first_week: int, week: int, sleeper_of_pfr: dict[str, str]
) -> dict[tuple[str, int], SnapWeek]:
    """The snap counts of weeks `first_week` to `week` by Sleeper ID and week. A player with no PFR ID is not in it."""
    out = {}
    for row in _rows(snaps):
        row_week = _regular_week(row, "game_type")
        pid = sleeper_of_pfr.get(row["pfr_player_id"])
        if row_week is not None and pid is not None and first_week <= row_week <= week:
            # nflverse writes the snap share as a fraction, such as 0.71.
            out[(pid, row_week)] = SnapWeek(snaps=int(_number(row["offense_snaps"])),
                                            share=int(_round_half_up(100 * _number(row["offense_pct"]))),
                                            team=_sleeper_team(row["team"]))
    return out


def read_usage(plays: list[dict[str, str]], snaps: dict[tuple[str, int], SnapWeek], week: int, first_week: int,
               sleeper_of_gsis: dict[str, str]) -> dict[str, list[UsageWeek]]:
    """The usage of weeks `first_week` to `week` by Sleeper ID, in week order.

    The plays give the targets and the carries, and the snap counts give the snaps. A player with no Sleeper
    ID in the gsis map has no targets or carries. A share is of the team's targets, carries, or snaps that
    week. A carry is a designed run: a scramble is a pass play in nflverse, so it is no carry. A two-point try
    is no target, no carry, and no red zone touch, as in the nflverse target count.
    """
    counts: dict[tuple[str, int], Counter] = {}
    teams: dict[tuple[str, int], str] = {}
    team_totals: dict[tuple[str, int], Counter] = {}
    for play in plays:
        play_week = int(play["week"])
        if play_week < first_week or _number(play["two_point_attempt"]) == 1:
            continue
        team = _sleeper_team(play["posteam"])
        for column, kind in (("receiver_player_id", "targets"), ("rusher_player_id", "carries")):
            if not play[column] or (kind == "carries" and not _number(play["rush"])):
                continue
            team_totals.setdefault((team, play_week), Counter())[kind] += 1
            pid = sleeper_of_gsis.get(play[column])
            if pid is None:
                continue
            player = counts.setdefault((pid, play_week), Counter())
            player[kind] += 1
            teams[(pid, play_week)] = team
            yardline = _yardline(play["yardline_100"])
            if yardline is not None and yardline <= RED_ZONE_YARDS:
                player["red_zone"] += 1
    usage: dict[str, list[UsageWeek]] = {}
    for key in sorted(set(counts) | {k for k in snaps if first_week <= k[1] <= week}):
        pid, usage_week = key
        player, snap = counts.get(key, Counter()), snaps.get(key)
        team = teams.get(key) or snap.team
        totals = team_totals.get((team, usage_week), Counter())
        usage.setdefault(pid, []).append(UsageWeek(
            week=usage_week, team=team, snaps=snap.snaps if snap else None, snap_share=snap.share if snap else None,
            targets=player["targets"], target_share=_share(player["targets"], totals["targets"]),
            carries=player["carries"], carry_share=_share(player["carries"], totals["carries"]),
            red_zone_touches=player["red_zone"]))
    return usage


def _is_neutral(play: dict[str, str]) -> bool:
    """First or second down, the score within NEUTRAL_SCORE, in the first three quarters,
    outside the half's last two minutes.

    On these downs the play call shows the coach's plan, not the score or the clock.
    """
    if play["down"] not in ("1", "2") or play["qtr"] not in ("1", "2", "3"):
        return False
    if play["qtr"] == "2" and _number(play["game_seconds_remaining"]) <= HALF_TWO_MINUTES_SECONDS:
        return False
    return (play["score_differential"] not in ("", "NA")
            and abs(_number(play["score_differential"])) <= NEUTRAL_SCORE)


def read_environment(plays: list[dict[str, str]]) -> dict[str, list[TeamWeek]]:
    """The offense counts and the EPA and pass_oe sums of each week of the plays by Sleeper team code, in week order.

    A two-point try is not a down, so it adds nothing. It also has no pass_oe, so every play left has both columns.
    """
    counts: dict[tuple[str, int], Counter] = {}
    for play in plays:
        if _number(play["two_point_attempt"]) == 1:
            continue
        team = counts.setdefault((_sleeper_team(play["posteam"]), int(play["week"])), Counter())
        passed, rushed = bool(_number(play["pass"])), bool(_number(play["rush"]))
        team["plays"] += 1
        team["passes"] += passed
        team["rushes"] += rushed
        team["rush_successes"] += rushed and bool(_number(play["success"]))
        if _is_neutral(play):
            team["neutral_plays"] += 1
            team["neutral_passes"] += passed
        team["epa"] += _number(play["epa"])
        team["pass_oe"] += _number(play["pass_oe"])
    environment: dict[str, list[TeamWeek]] = {}
    for (team, team_week), c in sorted(counts.items()):
        environment.setdefault(team, []).append(TeamWeek(
            week=team_week, plays=c["plays"], passes=c["passes"], rushes=c["rushes"],
            rush_successes=c["rush_successes"], neutral_plays=c["neutral_plays"], neutral_passes=c["neutral_passes"],
            epa=c["epa"], pass_oe=c["pass_oe"]))
    return environment


def read_pfr_map(path: Path) -> dict[str, str]:
    """The Sleeper ID by PFR ID. The snap counts name a player by his PFR ID only."""
    return {row["pfr_id"]: row["sleeper_id"] for row in _rows(path)
            if row["sleeper_id"] not in ("", "NA") and row["pfr_id"] not in ("", "NA")}
