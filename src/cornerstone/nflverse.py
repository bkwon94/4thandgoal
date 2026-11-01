"""
Download and parse the nflverse play by play, snap count, injury, schedule, and depth chart files, the ffverse id map,
and the ffopportunity expected points.
A failure of any source never stops a build, so each read returns None for missing data.
"""
import logging
import time
from collections.abc import Callable, Collection
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel

from cornerstone import nflverse_expected, nflverse_players, nflverse_usage
from cornerstone.files import write_bytes_atomic
from cornerstone.models import DropPlay, NflverseWeek
from cornerstone.nflverse_rows import NFLVERSE_TEAM, SLEEPER_TEAM, _number, _rows, _sleeper_team, _yardline
from cornerstone.tunables import USAGE_SAVED_WEEKS

logger = logging.getLogger(__name__)

PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"
FTN_URL = "https://github.com/nflverse/nflverse-data/releases/download/ftn_charting/ftn_charting_{season}.csv"
INJURIES_URL = "https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{season}.csv.gz"
# One file holds the games of every season, so this URL has no season field.
SCHEDULES_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
DEPTH_CHARTS_URL = "https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_{season}.csv.gz"
SNAP_COUNTS_URL = "https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{season}.csv"
STATS_PLAYER_URL = ("https://github.com/nflverse/nflverse-data/releases/download/stats_player/"
                    "stats_player_week_{season}.csv.gz")
FFIDS_URL = "https://github.com/dynastyprocess/data/raw/master/files/db_playerids.csv"
FFOPPORTUNITY_URL = "https://github.com/ffverse/ffopportunity/releases/download/latest-data/ep_weekly_{season}.csv"

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


# The weeks of the fantasy playoffs, when a team schedule decides a title.
PLAYOFF_WEEKS = (15, 16, 17)
REGULAR_SEASON_WEEKS = range(1, 19)
SKILL_POSITIONS = ("QB", "RB", "WR", "TE")


class TeamSchedule(BaseModel):
    bye_week: int | None
    # Week to the Sleeper code of the opponent, for the weeks of PLAYOFF_WEEKS with a game.
    playoff_opponents: dict[int, str]


def _bye_week(played: set[int]) -> int | None:
    # A team with a game in every week but one has that week off. A short file has no bye, not a wrong one.
    off = set(REGULAR_SEASON_WEEKS) - played
    return next(iter(off)) if len(off) == 1 else None


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


def read_games(path: Path, season: int, week: int) -> list[tuple[str, str]] | None:
    """The away and home Sleeper team codes of each regular-season game of the week, in file order.

    None when the file has no game that week.
    """
    games = [(_sleeper_team(row["away_team"]), _sleeper_team(row["home_team"])) for row in _rows(path)
             if row["season"] == str(season) and row["game_type"] == "REG" and row["week"] == str(week)]
    return games or None


def read_kickoffs(path: Path, season: int, week: int) -> dict[str, datetime]:
    """The kickoff of each regular-season game of the week by Sleeper team code, in Eastern time.

    The file gives the date and the Eastern time of each kickoff. A row with no time gives no kickoff.
    """
    # The feed gives every kickoff in Eastern time for every league, so this zone is a fact of the feed and not the
    # league timezone of the config.
    eastern = ZoneInfo("America/New_York")
    kickoffs: dict[str, datetime] = {}
    for row in _rows(path):
        if row["season"] != str(season) or row["game_type"] != "REG" or row["week"] != str(week):
            continue
        # The schedules fixture and an old file can lack the column, so a missing time is no kickoff.
        time_text = row.get("gametime") or ""
        if time_text in ("", "NA"):
            continue
        kickoff = datetime.fromisoformat(f"{row['gameday']}T{time_text}").replace(tzinfo=eastern)
        for side in ("away_team", "home_team"):
            kickoffs[_sleeper_team(row[side])] = kickoff
    return kickoffs


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
                  teams: Collection[str] = (), fetch: Callable[[str], bytes] = http_get,
                  scoring: dict[str, float] | None = None) -> NflverseWeek:
    """The nflverse extract of one week.

    `scoring` is the league scoring. Without it the extract has no expected points, because the rescale needs
    the league weights.
    """
    def get(url_template: str) -> Path | None:
        # The ffverse URL has no season field, and format leaves it as it is.
        url = url_template.format(season=season)
        return download(url, cache_path(cache_dir, url_template, season), fetch=fetch)

    pbp, ftn = get(PBP_URL), get(FTN_URL)
    # The slow source loader reads these two, and a failure shows there as a missing source. The expected points
    # reader reads the schedules too, for the last game of the week.
    schedules = get(SCHEDULES_URL)
    get(DEPTH_CHARTS_URL)
    injuries_path, ffids_path = get(INJURIES_URL), get(FFIDS_URL)
    drops = read_drops(pbp, ftn, week, teams) if pbp and ftn else None
    injuries = read_injuries(injuries_path, week) if injuries_path else None
    id_map = read_id_map(ffids_path) if ffids_path else {}
    gsis = {pid: g for pid in player_ids if (g := gsis_id(pid, players, id_map))}
    snaps = get(SNAP_COUNTS_URL)
    # The waiver pool is not rostered, so the usage maps every QB, RB, WR, and TE of the blob, not `player_ids`.
    skill = {pid for pid, entry in players.items() if (entry or {}).get("position") in SKILL_POSITIONS}
    sleeper_of_gsis = {g: pid for pid in sorted(skill) if (g := gsis_id(pid, players, id_map))}
    pfr_map = nflverse_usage.read_pfr_map(ffids_path) if ffids_path else {}
    sleeper_of_pfr = {pfr: pid for pfr, pid in pfr_map.items() if pid in skill}
    first_week = week - USAGE_SAVED_WEEKS + 1
    snap_weeks = nflverse_usage.read_snaps(snaps, first_week, week, sleeper_of_pfr) if snaps else {}
    plays = nflverse_usage.read_plays(pbp, week) if pbp else None
    usage = None if plays is None else nflverse_usage.read_usage(plays, snap_weeks, week, first_week, sleeper_of_gsis)
    stats_player = get(STATS_PLAYER_URL)
    player_weeks = (nflverse_players.read_player_weeks(stats_player, first_week, week, sleeper_of_gsis)
                    if stats_player else None)
    # The file is the nflverse count of targets, so it replaces our count wherever it has a row.
    if usage is not None and player_weeks is not None:
        usage = nflverse_players.with_player_weeks(usage, player_weeks)
    environment = None if plays is None else nflverse_usage.read_environment(plays)
    # The shootout facts look ahead, so they read the games of week N+1.
    next_games = read_games(schedules, season, week + 1) if schedules else None
    # The bye lines of the next-week games read the bye week of each NFL team.
    team_schedules = read_schedules(schedules, season) if schedules else None
    bye_weeks = None if team_schedules is None else {
        team: s.bye_week for team, s in team_schedules.items() if s.bye_week is not None
    }
    ep_path = get(FFOPPORTUNITY_URL)
    expected = (nflverse_expected.read_expected(ep_path, schedules, season, week, scoring, sleeper_of_gsis)
                if ep_path and schedules and scoring is not None else None)
    return NflverseWeek(
        sources={"nflverse_pbp": pbp is not None and drops is not None,
                 "nflverse_ftn": ftn is not None and drops is not None,
                 "nflverse_injuries": injuries is not None,
                 "ffverse": ffids_path is not None,
                 "nflverse_snaps": snaps is not None and usage is not None,
                 # A file that reads through week N-1 is incomplete, so the build does not save the extract. The
                 # cache keeps the lagged file for a day, so a build after the cache ages out reads a fresh file.
                 "ffopportunity": expected is not None and expected.through_week == week,
                 "nflverse_stats_player": player_weeks is not None},
        gsis=gsis,
        drops=None if drops is None else {pid: drops[g] for pid, g in gsis.items() if g in drops},
        injuries=None if injuries is None else {pid: injuries[g] for pid, g in gsis.items() if g in injuries},
        usage=usage, environment=environment, expected=expected, next_games=next_games,
        bye_weeks=bye_weeks)
