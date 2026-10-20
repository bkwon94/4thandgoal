"""
Sleeper API client with a disk cache for the large players file.
It writes one raw JSON file per endpoint and reads them back.
"""
import json
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

logger = logging.getLogger(__name__)

RAW_FILES: tuple[str, ...] = (
    "state", "league", "users", "rosters", "matchups", "matchups_next",
    "transactions", "projections", "stats", "players", "bracket",
)

OFFICIAL_URL = "https://api.sleeper.app/v1"
UNOFFICIAL_URL = "https://api.sleeper.app"
TIMEOUT_SECONDS = 30
# The players file is about 5 MB. The cache keeps it one day, because the injury status in it
# changes daily and must be fresh on build day.
PLAYERS_CACHE_MAX_AGE_SECONDS = 24 * 60 * 60

# The fetch time is saved beside the raw files but is not one of them, so load_raw ignores it.
FETCHED_FILE = "fetched.json"
# The transactions of week N-1, fetched again at the build of week N. A trade made after the
# build of week N-1 carries leg N-1, so only this fresh copy has it. load_raw ignores the file.
PREV_TRANSACTIONS_FILE = "transactions_prev.json"

POSITIONS = ("QB", "RB", "WR", "TE", "DEF", "K")


def _position_params() -> list[tuple[str, str]]:
    # httpx repeats the key for each tuple, which Sleeper needs for position[].
    return [("season_type", "regular")] + [("position[]", p) for p in POSITIONS]


def _get(client: httpx.Client, url: str, params=None):
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.json()


def _get_or_empty(client: httpx.Client, url: str, params=None) -> list:
    # Unofficial endpoints change without notice, so a failure must not stop the report.
    try:
        return _get(client, url, params)
    except (httpx.HTTPError, ValueError) as error:
        # ValueError covers a 200 response with a body that is not JSON.
        logger.warning("Unofficial Sleeper endpoint failed: %s (%s)", url, error)
        return []


def _write_json(path: Path, obj) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=None)


def _players(client: httpx.Client, players_cache: Path):
    if players_cache.exists() and time.time() - players_cache.stat().st_mtime < PLAYERS_CACHE_MAX_AGE_SECONDS:
        try:
            with players_cache.open(encoding="utf-8") as f:
                return json.load(f)
        except ValueError:
            # A cut-off cache file is not data. Fetch the players again.
            logger.warning("Players cache %s does not parse, so it is fetched again", players_cache)
    players = _get(client, f"{OFFICIAL_URL}/players/nfl")
    players_cache.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file in the same directory, then replace, so a stopped write never
    # leaves a half file in the cache.
    fd, tmp = tempfile.mkstemp(dir=players_cache.parent, suffix=".tmp")
    os.close(fd)
    try:
        _write_json(Path(tmp), players)
        os.replace(tmp, players_cache)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return players


def fetch_state() -> dict:
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        return _get(client, f"{OFFICIAL_URL}/state/nfl")


def fetch_news(player_id: str) -> list[dict]:
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        return _get_or_empty(client, f"{UNOFFICIAL_URL}/players/nfl/{player_id}/news")


def read_fetch_time(raw_dir: Path) -> datetime | None:
    """The aware time at which fetch_week got the transactions. None when no time is saved."""
    path = raw_dir / FETCHED_FILE
    if not path.exists():
        return None
    # A cut-off or hand-edited file must not stop the build. The caller has a fallback for None.
    try:
        return datetime.fromisoformat(json.loads(path.read_text(encoding="utf-8"))["transactions"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        logger.warning("Fetch time file %s is unreadable, so it is ignored (%s)", path, error)
        return None


def read_prev_transactions(raw_dir: Path) -> list | None:
    """The fresh transactions of week N-1 that fetch_week saved. None when no file is saved."""
    path = raw_dir / PREV_TRANSACTIONS_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_week(league_id: str, season: int, week: int, raw_dir: Path, players_cache: Path) -> None:
    league = f"{OFFICIAL_URL}/league/{league_id}"
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        # Week N-1 comes first, so the fetch time below bounds both calls.
        previous = _get(client, f"{league}/transactions/{week - 1}") if week > 1 else None
        transactions = _get(client, f"{league}/transactions/{week}")
        # The time is taken right after the call returns. It is the end of the trade window.
        fetched = datetime.now(ZoneInfo("America/New_York"))
        data = {
            "state": _get(client, f"{OFFICIAL_URL}/state/nfl"),
            "league": _get(client, league),
            "users": _get(client, f"{league}/users"),
            "rosters": _get(client, f"{league}/rosters"),
            "matchups": _get(client, f"{league}/matchups/{week}"),
            "matchups_next": _get(client, f"{league}/matchups/{week + 1}"),
            "transactions": transactions,
            "projections": _get_or_empty(
                client, f"{UNOFFICIAL_URL}/projections/nfl/{season}/{week}", _position_params()),
            "stats": _get_or_empty(
                client, f"{UNOFFICIAL_URL}/stats/nfl/{season}/{week}", _position_params()),
            "players": _players(client, players_cache),
            "bracket": _get(client, f"{league}/winners_bracket"),
        }
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name in RAW_FILES:
        _write_json(raw_dir / f"{name}.json", data[name])
    if previous is not None:
        _write_json(raw_dir / PREV_TRANSACTIONS_FILE, previous)
    _write_json(raw_dir / FETCHED_FILE, {"transactions": fetched.isoformat()})


def fetch_past_week(league_id: str, season: int, week: int, out_dir: Path) -> None:
    league = f"{OFFICIAL_URL}/league/{league_id}"
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        data = {
            "matchups": _get(client, f"{league}/matchups/{week}"),
            "transactions": _get(client, f"{league}/transactions/{week}"),
            "stats": _get_or_empty(
                client, f"{UNOFFICIAL_URL}/stats/nfl/{season}/{week}", _position_params()),
            "projections": _get_or_empty(
                client, f"{UNOFFICIAL_URL}/projections/nfl/{season}/{week}", _position_params()),
        }
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, obj in data.items():
        _write_json(out_dir / f"{name}.json", obj)


def load_raw(raw_dir: Path) -> dict[str, object]:
    raw = {}
    for name in RAW_FILES:
        with (raw_dir / f"{name}.json").open(encoding="utf-8") as f:
            raw[name] = json.load(f)
    return raw
