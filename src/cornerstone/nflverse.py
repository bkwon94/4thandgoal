"""
Download and parse the nflverse drop and injury files and the ffverse id map.
A failure of any source never stops a build, so each read returns None for missing data.
"""
import csv
import gzip
import logging
import os
import tempfile
import time
from collections.abc import Callable, Collection
from pathlib import Path

import httpx

from cornerstone.models import DropPlay, NflverseWeek

logger = logging.getLogger(__name__)

PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"
FTN_URL = "https://github.com/nflverse/nflverse-data/releases/download/ftn_charting/ftn_charting_{season}.csv"
INJURIES_URL = "https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{season}.csv.gz"
FFIDS_URL = "https://github.com/dynastyprocess/data/raw/master/files/db_playerids.csv"

# The season files grow each week, so a one-day cache keeps them fresh on build day.
CACHE_MAX_AGE_SECONDS = 24 * 60 * 60
TIMEOUT_SECONDS = 120


def http_get(url: str) -> bytes:
    # GitHub release URLs redirect to a storage host, so redirects must be followed.
    response = httpx.get(url, follow_redirects=True, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.content


def download(url: str, path: Path, max_age_seconds: int = CACHE_MAX_AGE_SECONDS,
             fetch: Callable[[str], bytes] = http_get) -> Path | None:
    """The cached file, fresh if possible. A stale cache on a failure, None with no cache."""
    if path.exists() and time.time() - path.stat().st_mtime < max_age_seconds:
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
    # Write to a temp file in the same directory, then replace, so a stopped write never
    # leaves a half file in the cache.
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(body)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
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


def read_id_map(path: Path) -> dict[str, str]:
    return {row["sleeper_id"]: row["gsis_id"] for row in _rows(path)
            if row["sleeper_id"] not in ("", "NA") and row["gsis_id"] not in ("", "NA")}


def gsis_id(player_id: str, players: dict, id_map: dict[str, str]) -> str | None:
    # The Sleeper blob has stray spaces in some ids and no id for some new players.
    blob = (players.get(player_id) or {}).get("gsis_id")
    if blob and blob.strip():
        return blob.strip()
    return id_map.get(player_id)


def nflverse_week(season: int, week: int, player_ids: list[str], players: dict, cache_dir: Path,
                  teams: Collection[str] = (), fetch: Callable[[str], bytes] = http_get) -> NflverseWeek:
    def get(url_template: str) -> Path | None:
        # The ffverse URL has no season field, and format leaves it as it is.
        url = url_template.format(season=season)
        return download(url, cache_dir / url.rsplit("/", 1)[-1], fetch=fetch)

    pbp, ftn = get(PBP_URL), get(FTN_URL)
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
