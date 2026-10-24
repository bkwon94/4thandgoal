"""
Download and parse the nflverse drop, injury, schedule, and depth chart files and the ffverse id map.
A failure of any source never stops a build, so each read returns None for missing data.
"""
import csv
import gzip
import logging
import time
from collections import Counter
from collections.abc import Callable, Collection
from pathlib import Path

import httpx
from pydantic import BaseModel

from cornerstone.files import write_bytes_atomic
from cornerstone.history import _round_half_up
from cornerstone.models import DropPlay, NflverseWeek, TeamWeek, UsageWeek

logger = logging.getLogger(__name__)

PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"
FTN_URL = "https://github.com/nflverse/nflverse-data/releases/download/ftn_charting/ftn_charting_{season}.csv"
INJURIES_URL = "https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{season}.csv.gz"
# One file holds the games of every season, so this URL has no season field.
SCHEDULES_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
DEPTH_CHARTS_URL = "https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_{season}.csv.gz"
FFIDS_URL = "https://github.com/dynastyprocess/data/raw/master/files/db_playerids.csv"

# The season files grow each week, so a one-day cache keeps them fresh on build day.
CACHE_MAX_AGE_SECONDS = 24 * 60 * 60
TIMEOUT_SECONDS = 120


def http_get(url: str) -> bytes:
    # GitHub release URLs redirect to a storage host, so redirects must be followed.
    response = httpx.get(url, follow_redirects=True, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.content


def is_fresh(path: Path, max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> bool:
    """True when the file exists and is younger than `max_age_seconds`, by the clock of the disk."""
    return path.exists() and time.time() - path.stat().st_mtime < max_age_seconds


def download(url: str, path: Path, max_age_seconds: int = CACHE_MAX_AGE_SECONDS,
             fetch: Callable[[str], bytes] = http_get) -> Path | None:
    """The cached file, fresh if possible. A stale cache on a failure, None with no cache."""
    if is_fresh(path, max_age_seconds):
        return path
    try:
        body = fetch(url)
    except httpx.HTTPError as error:
        if path.exists():
            logger.warning("Download of %s failed (%s), so the stale cache is used", url, error)
            return path
        logger.warning("Download of %s failed (%s) and no cache exists", url, error)
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(path, body)
    return path


def _rows(path: Path):
    # Plain and gzip files share one reader, so the caller does not care which one it has.
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def _number(text: str) -> float:
    # nflverse writes NA for a missing value. A negative value is real data and stays.
    return 0.0 if text in ("", "NA") else float(text)


# Sleeper and nflverse share every team code but this one.
NFLVERSE_TEAM = {"LAR": "LA"}


# The inverse of NFLVERSE_TEAM: the readers below name teams as Sleeper does, so they join the rosters.
SLEEPER_TEAM = {nflverse: sleeper for sleeper, nflverse in NFLVERSE_TEAM.items()}

# The weeks of the fantasy playoffs, when a team schedule decides a title.
PLAYOFF_WEEKS = (15, 16, 17)
REGULAR_SEASON_WEEKS = range(1, 19)
SKILL_POSITIONS = ("QB", "RB", "WR", "TE")


class TeamSchedule(BaseModel):
    bye_week: int | None
    # Week to the Sleeper code of the opponent, for the weeks of PLAYOFF_WEEKS with a game.
    playoff_opponents: dict[int, str]


def _sleeper_team(code: str) -> str:
    return SLEEPER_TEAM.get(code, code)


def _bye_week(played: set[int]) -> int | None:
    # A team with a game in every week but one has that week off. A short file has no bye, not a wrong one.
    off = set(REGULAR_SEASON_WEEKS) - played
    return next(iter(off)) if len(off) == 1 else None


def _yardline(text: str) -> float | None:
    # A missing yard line is unknown, not the goal line: 0 would put every such drop in the end zone.
    return None if text in ("", "NA") else float(text)


def read_drops(pbp: Path, ftn: Path, week: int, teams: Collection[str] = ()) -> dict[str, list[DropPlay]] | None:
    """Drops of the week by receiver gsis_id. None when the files hold a partial week.

    A partial week is one with no row in either file, a game in one file and not the other, or a
    team in `teams` with no game in the play-by-play. `teams` holds the Sleeper codes of the NFL
    teams whose started players played. A partial week must not count as complete, because the
    build saves a complete extract and never fetches it again.
    """
    week_text = str(week)
    drop_keys = set()
    ftn_games = set()
    for row in _rows(ftn):
        if row["week"] != week_text:
            continue
        ftn_games.add(row["nflverse_game_id"])
        if row["is_drop"] == "TRUE":
            drop_keys.add((row["nflverse_game_id"], row["nflverse_play_id"]))
    drops: dict[str, list[DropPlay]] = {}
    pbp_games = set()
    pbp_teams = set()
    for row in _rows(pbp):
        if row["week"] != week_text:
            continue
        pbp_games.add(row["game_id"])
        pbp_teams.update((row["home_team"], row["away_team"]))
        if (row["game_id"], row["play_id"]) in drop_keys and row["receiver_player_id"]:
            drops.setdefault(row["receiver_player_id"], []).append(DropPlay(
                game_id=row["game_id"], play_id=row["play_id"],
                air_yards=_number(row["air_yards"]), yardline_100=_yardline(row["yardline_100"])))
    if not ftn_games or ftn_games != pbp_games:
        if ftn_games or pbp_games:
            logger.warning("nflverse week %d is partial: FTN has %d games, play-by-play has %d",
                           week, len(ftn_games), len(pbp_games))
        return None
    missing = {t for t in teams if NFLVERSE_TEAM.get(t, t) not in pbp_teams}
    if missing:
        logger.warning("nflverse week %d is partial: no game for %s", week, ", ".join(sorted(missing)))
        return None
    return drops


def read_injuries(path: Path, week: int) -> dict[str, dict[int, str]] | None:
    """The report status by gsis_id and week, regular season only. None when no row for the week."""
    injuries: dict[str, dict[int, str]] = {}
    has_week = False
    for row in _rows(path):
        if row["season_type"] != "REG":
            continue
        if int(row["week"]) == week:
            has_week = True
        if row["report_status"]:
            injuries.setdefault(row["gsis_id"], {})[int(row["week"])] = row["report_status"]
    return injuries if has_week else None


def read_schedules(path: Path, season: int) -> dict[str, TeamSchedule] | None:
    """The bye week and the opponents of weeks 15 to 17 by Sleeper team code. None when no game of the season.

    The file holds every season, so the reader filters the rows by season. Only regular-season games count.
    """
    weeks: dict[str, set[int]] = {}
    playoff: dict[str, dict[int, str]] = {}
    for row in _rows(path):
        if row["season"] != str(season) or row["game_type"] != "REG":
            continue
        week = int(row["week"])
        away, home = (_sleeper_team(row[side]) for side in ("away_team", "home_team"))
        for team, opponent in ((away, home), (home, away)):
            weeks.setdefault(team, set()).add(week)
            if week in PLAYOFF_WEEKS:
                playoff.setdefault(team, {})[week] = opponent
    if not weeks:
        return None
    return {team: TeamSchedule(
                bye_week=_bye_week(played),
                playoff_opponents=playoff.get(team, {}))
            for team, played in weeks.items()}


def read_depth_charts(path: Path) -> dict[str, dict[str, list[str]]] | None:
    """The ordered gsis_ids by Sleeper team code and position, from the latest snapshot. None when no row.

    The file holds a snapshot of every day of the season, so only the latest is the live depth chart.
    The ids are gsis_ids, as the id map gives, so a caller joins them to Sleeper players with that map.
    A player is on a chart once, even when he is in more than one formation.
    """
    latest = ""
    rows: list[dict[str, str]] = []
    for row in _rows(path):
        # A row with a pos_rank such as NA has no place in the order, so it is skipped and the rest stay.
        if (row["pos_abb"] not in SKILL_POSITIONS or not row["gsis_id"] or not row["pos_rank"].isdigit()
                or row["dt"] < latest):
            continue
        if row["dt"] > latest:
            latest, rows = row["dt"], []
        rows.append(row)
    charts: dict[str, dict[str, list[str]]] = {}
    for row in sorted(rows, key=lambda r: int(r["pos_rank"])):
        ordered = charts.setdefault(SLEEPER_TEAM.get(row["team"], row["team"]), {}).setdefault(row["pos_abb"], [])
        if row["gsis_id"] not in ordered:
            ordered.append(row["gsis_id"])
    return charts or None


def read_id_map(path: Path) -> dict[str, str]:
    return {row["sleeper_id"]: row["gsis_id"] for row in _rows(path)
            if row["sleeper_id"] not in ("", "NA") and row["gsis_id"] not in ("", "NA")}


# The play types of an offensive play. A kneel, a spike, a penalty with no play, and a kick are not plays.
PLAY_TYPES = ("pass", "run")
# A target or a carry at this yard line or closer to the end zone is a red zone touch.
RED_ZONE_YARDS = 20


def _share(part: int, whole: int) -> int:
    return int(_round_half_up(100 * part / whole)) if whole else 0


def _regular_week(row: dict[str, str], season_key: str) -> int | None:
    """The week of a regular season row. None for a playoff row or a row with no week."""
    if row.get(season_key, "REG") != "REG" or not row["week"].isdigit():
        return None
    return int(row["week"])


def read_usage(pbp: Path, snaps: Path | None, week: int, first_week: int, sleeper_of_gsis: dict[str, str],
               sleeper_of_pfr: dict[str, str]) -> dict[str, list[UsageWeek]] | None:
    """The usage of weeks `first_week` to `week` by Sleeper ID, in week order. None when the play by play has no week `week`.

    The play by play gives the targets and the carries, and the snap counts give the snaps. A player with
    no Sleeper ID in the two maps is not in the result. A share is of the team's targets, carries, or snaps
    that week. A carry is a designed run: a scramble is a pass play in nflverse, so it is no carry.
    """
    has_week = False
    counts: dict[tuple[str, int], Counter] = {}
    teams: dict[tuple[str, int], str] = {}
    team_totals: dict[tuple[str, int], Counter] = {}
    for row in _rows(pbp):
        n = _regular_week(row, "season_type")
        has_week = has_week or n == week
        if n is None or not first_week <= n <= week or row["play_type"] not in PLAY_TYPES:
            continue
        team = _sleeper_team(row["posteam"])
        for column, kind in (("receiver_player_id", "targets"), ("rusher_player_id", "carries")):
            if not row[column] or (kind == "carries" and not _number(row["rush"])):
                continue
            team_totals.setdefault((team, n), Counter())[kind] += 1
            pid = sleeper_of_gsis.get(row[column])
            if pid is None:
                continue
            player = counts.setdefault((pid, n), Counter())
            player[kind] += 1
            teams[(pid, n)] = team
            yardline = _yardline(row["yardline_100"])
            if yardline is not None and yardline <= RED_ZONE_YARDS:
                player["red_zone"] += 1
    if not has_week:
        return None
    snap_rows: dict[tuple[str, int], tuple[int, int, str]] = {}
    for row in _rows(snaps) if snaps else ():
        n = _regular_week(row, "game_type")
        pid = sleeper_of_pfr.get(row["pfr_player_id"])
        if n is not None and pid is not None and first_week <= n <= week:
            # nflverse writes the snap share as a fraction, such as 0.71.
            snap_rows[(pid, n)] = (int(_number(row["offense_snaps"])),
                                   int(_round_half_up(100 * _number(row["offense_pct"]))), _sleeper_team(row["team"]))
    usage: dict[str, list[UsageWeek]] = {}
    for key in sorted(set(counts) | set(snap_rows), key=lambda k: (k[0], k[1])):
        pid, n = key
        player, snap = counts.get(key, Counter()), snap_rows.get(key)
        team = teams.get(key) or snap[2]
        totals = team_totals.get((team, n), Counter())
        usage.setdefault(pid, []).append(UsageWeek(
            week=n, team=team, snaps=snap[0] if snap else None, snap_share=snap[1] if snap else None,
            targets=player["targets"], target_share=_share(player["targets"], totals["targets"]),
            carries=player["carries"], carry_share=_share(player["carries"], totals["carries"]),
            red_zone_touches=player["red_zone"]))
    return usage


# A neutral down: the score is within this many points either way.
NEUTRAL_SCORE = 7
# The game clock of the end of the first half's two-minute warning: 30 minutes left plus 2.
HALF_TWO_MINUTES_SECONDS = 1800 + 120


def _is_neutral(row: dict[str, str]) -> bool:
    """First or second down, the score within NEUTRAL_SCORE, in the first three quarters, outside the half's last two minutes.

    On these downs the play call shows the coach's plan, not the score or the clock.
    """
    if row["down"] not in ("1", "2") or row["qtr"] not in ("1", "2", "3"):
        return False
    if row["qtr"] == "2" and _number(row["game_seconds_remaining"]) <= HALF_TWO_MINUTES_SECONDS:
        return False
    return row["score_differential"] not in ("", "NA") and abs(_number(row["score_differential"])) <= NEUTRAL_SCORE


def read_environment(pbp: Path, week: int) -> dict[str, list[TeamWeek]] | None:
    """The offense counts of weeks 1 to `week` by Sleeper team code, in week order. None when no row for week `week`."""
    has_week = False
    counts: dict[tuple[str, int], Counter] = {}
    for row in _rows(pbp):
        n = _regular_week(row, "season_type")
        has_week = has_week or n == week
        if n is None or n > week or row["play_type"] not in PLAY_TYPES:
            continue
        team = counts.setdefault((_sleeper_team(row["posteam"]), n), Counter())
        passed, rushed = bool(_number(row["pass"])), bool(_number(row["rush"]))
        team["plays"] += 1
        team["passes"] += passed
        team["rushes"] += rushed
        team["rush_successes"] += rushed and bool(_number(row["success"]))
        if _is_neutral(row):
            team["neutral_plays"] += 1
            team["neutral_passes"] += passed
    if not has_week:
        return None
    environment: dict[str, list[TeamWeek]] = {}
    for (team, n), c in sorted(counts.items()):
        environment.setdefault(team, []).append(TeamWeek(
            week=n, plays=c["plays"], passes=c["passes"], rushes=c["rushes"], rush_successes=c["rush_successes"],
            neutral_plays=c["neutral_plays"], neutral_passes=c["neutral_passes"]))
    return environment


def gsis_id(player_id: str, players: dict, id_map: dict[str, str]) -> str | None:
    # The Sleeper blob has stray spaces in some ids and no id for some new players.
    blob = (players.get(player_id) or {}).get("gsis_id")
    if blob and blob.strip():
        return blob.strip()
    return id_map.get(player_id)


def cache_path(cache_dir: Path, url_template: str, season: int) -> Path:
    """Where the download of a URL lives in the cache. Every reader and every download uses this one name."""
    return cache_dir / url_template.format(season=season).rsplit("/", 1)[-1]


def nflverse_week(season: int, week: int, player_ids: list[str], players: dict, cache_dir: Path,
                  teams: Collection[str] = (), fetch: Callable[[str], bytes] = http_get) -> NflverseWeek:
    def get(url_template: str) -> Path | None:
        # The ffverse URL has no season field, and format leaves it as it is.
        url = url_template.format(season=season)
        return download(url, cache_path(cache_dir, url_template, season), fetch=fetch)

    pbp, ftn = get(PBP_URL), get(FTN_URL)
    # These two only fill the cache. The slow source loader reads them, and a failure shows there as a missing source.
    get(SCHEDULES_URL)
    get(DEPTH_CHARTS_URL)
    injuries_path, ffids_path = get(INJURIES_URL), get(FFIDS_URL)
    drops = read_drops(pbp, ftn, week, teams) if pbp and ftn else None
    injuries = read_injuries(injuries_path, week) if injuries_path else None
    id_map = read_id_map(ffids_path) if ffids_path else {}
    gsis = {pid: g for pid in player_ids if (g := gsis_id(pid, players, id_map))}
    return NflverseWeek(
        sources={"nflverse_pbp": pbp is not None and drops is not None,
                 "nflverse_ftn": ftn is not None and drops is not None,
                 "nflverse_injuries": injuries is not None,
                 "ffverse": ffids_path is not None},
        gsis=gsis,
        drops=None if drops is None else {pid: drops[g] for pid, g in gsis.items() if g in drops},
        injuries=None if injuries is None else {pid: injuries[g] for pid, g in gsis.items() if g in injuries})
