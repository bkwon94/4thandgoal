"""
Sleeper API client with a disk cache for the large players file.
It writes one raw JSON file per endpoint and reads them back.
"""
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from league.files import write_bytes_atomic
from league.league_settings import BENCH_SLOTS, LeagueSettings, bracket_byes, star_ranks
from league.provider.raw import RawAheadWeek, RawLeague, RawPastWeek, RawState, RawTransaction, RawWeek

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

# The pairs of weeks N+2 to the last regular week. matchups_next already holds week N+1.
# Past weeks never need the file, so load_raw reads it only when it exists.
SCHEDULE_FILE = "schedule.json"
# The per-player projections of weeks N+1 to the last NFL week. projections.json holds week N only.
# Past weeks never need the file, so load_raw reads it only when it exists.
PROJECTIONS_AHEAD_FILE = "projections_ahead.json"
# The adds of each player across all Sleeper leagues in the last day. Past weeks have no such file,
# so load_raw reads it only when it exists.
TRENDING_FILE = "trending.json"
# The bucket holds 8, and the pool filter and the position filter drop some of the top adds, so 50 leaves room.
TRENDING_PARAMS = {"lookback_hours": 24, "limit": 50}
# The players file in the cache dir of the adapter. It is about 5 MB, so the adapter keeps one copy for every league.
PLAYERS_FILE = "players.json"
# The positions the adapter asks Sleeper for. The pool of a league keeps only the positions of its roster slots,
# so a position the league does not start leaves after the fetch, in the League settings.
FETCH_POSITIONS = ("QB", "RB", "WR", "TE", "K", "DEF")


def _position_params() -> list[tuple[str, str]]:
    # httpx repeats the key for each tuple, which Sleeper needs for position[].
    return [("season_type", "regular")] + [("position[]", p) for p in FETCH_POSITIONS]


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
        logger.warning("Sleeper endpoint failed: %s (%s)", url, error)
        return []


def _get_or_none(client: httpx.Client, url: str, params=None) -> list | None:
    """The body of an unofficial endpoint, or None when the call fails, so a failure differs from an empty body."""
    try:
        return _get(client, url, params)
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("Sleeper endpoint failed: %s (%s)", url, error)
        return None


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
    write_bytes_atomic(players_cache, json.dumps(players, indent=None).encode("utf-8"))
    return players


def fetch_state(transport: httpx.BaseTransport | None = None) -> RawState:
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
        return RawState.model_validate(_get(client, f"{OFFICIAL_URL}/state/nfl"))


def fetch_players(players_cache: Path, transport: httpx.BaseTransport | None = None) -> dict[str, dict]:
    """The players file, from the cache when it is less than a day old, else from Sleeper."""
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
        return _players(client, players_cache)


def fetch_news(player_id: str, transport: httpx.BaseTransport | None = None) -> list[dict]:
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
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


def read_prev_transactions(raw_dir: Path) -> list[RawTransaction] | None:
    """The fresh transactions of week N-1 that fetch_week saved. None when no file is saved."""
    path = raw_dir / PREV_TRANSACTIONS_FILE
    if not path.exists():
        return None
    return [RawTransaction.model_validate(t) for t in json.loads(path.read_text(encoding="utf-8"))]


def _schedule(client: httpx.Client, league: str, week: int, last_regular_week: int) -> list[dict]:
    """One entry per week from week + 2 to `last_regular_week`, with the roster id and matchup id of each row."""
    # Only the pair keys stay. A future week has zero points and a lineup that can still change.
    return [
        {"week": w, "matchups": [
            {"roster_id": row["roster_id"], "matchup_id": row["matchup_id"]}
            for row in _get(client, f"{league}/matchups/{w}")
        ]}
        for w in range(week + 2, last_regular_week + 1)
    ]


def _projections_ahead(client: httpx.Client, season: int, week: int, last: int, points_key: str) -> list[dict]:
    """One entry per week from week + 1 to `last`, with the projection of each player at the points key of the league,
    such as pts_half_ppr."""
    # Every player stays, so the waiver board can rank the waiver pool.
    # A player with no projection at the points key has no entry.
    return [
        {"week": w, "projections": {
            item["player_id"]: item["stats"][points_key]
            for item in _get_or_empty(client, f"{UNOFFICIAL_URL}/projections/nfl/{season}/{w}", _position_params())
            if (item.get("stats") or {}).get(points_key) is not None
        }}
        for w in range(week + 1, last + 1)
    ]


def fetch_projections_ahead(
        season: int, week: int, last_regular_week: int, points_key: str, transport: httpx.BaseTransport | None = None,
) -> list[RawAheadWeek]:
    """The projections ahead of `week` through `last_regular_week` at `points_key`, in the entries that fetch_week saves.

    The trade grade reads no later week, so the live grade skips those calls.
    """
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
        ahead = _projections_ahead(client, season, week, last_regular_week, points_key)
    return [RawAheadWeek.model_validate(entry) for entry in ahead]


def _trending(client: httpx.Client) -> list[dict]:
    """The top adds across all Sleeper leagues in the last day, each with the player ID and the count."""
    # The board shows an empty trending bucket on a failure, so a failed call must not stop the fetch.
    return _get_or_empty(client, f"{OFFICIAL_URL}/players/nfl/trending/add", TRENDING_PARAMS)


def _league_raw(
        client: httpx.Client, league: str, season: int, week: int, players_cache: Path,
        known: dict[str, object]) -> dict[str, object]:
    """The raw data of the league in `week`, with the keys of RAW_FILES. A key in `known` keeps its value.

    Each caller fetches some keys first and stamps its fetch time after them, so the rest come from Sleeper here.
    """
    calls = {
        "state": lambda: _get(client, f"{OFFICIAL_URL}/state/nfl"),
        "league": lambda: _get(client, league),
        "users": lambda: _get(client, f"{league}/users"),
        "rosters": lambda: _get(client, f"{league}/rosters"),
        "matchups": lambda: _get(client, f"{league}/matchups/{week}"),
        "matchups_next": lambda: _get(client, f"{league}/matchups/{week + 1}"),
        "transactions": lambda: _get(client, f"{league}/transactions/{week}"),
        "projections": lambda: _get_or_empty(
            client, f"{UNOFFICIAL_URL}/projections/nfl/{season}/{week}", _position_params()),
        "stats": lambda: _get_or_empty(
            client, f"{UNOFFICIAL_URL}/stats/nfl/{season}/{week}", _position_params()),
        "players": lambda: _players(client, players_cache),
        "bracket": lambda: _get(client, f"{league}/winners_bracket"),
    }
    # The calls run in the order of RAW_FILES, as the dict keeps the order of its keys.
    return {name: known[name] if name in known else call() for name, call in calls.items()}


def fetch_week(
        league_id: str, season: int, week: int, raw_dir: Path, players_cache: Path, tz: ZoneInfo,
        last_regular_week: int, last_season_week: int, points_key: str,
        transport: httpx.BaseTransport | None = None) -> None:
    """Fetch the raw files of `week` into `raw_dir`. The saved fetch time is in the league timezone `tz`.

    The schedule runs to `last_regular_week`. The projections ahead run to `last_season_week`, because the waiver
    board reads the fantasy playoffs too. They hold the projection at `points_key` of the League settings.
    """
    league = f"{OFFICIAL_URL}/league/{league_id}"
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
        # Week N-1 comes first, so the fetch time below is later than both calls.
        previous = _get(client, f"{league}/transactions/{week - 1}") if week > 1 else None
        transactions = _get(client, f"{league}/transactions/{week}")
        # The code takes the time right after the call returns. The page shows it and the history keeps it.
        fetched = datetime.now(tz)
        data = _league_raw(client, league, season, week, players_cache, {"transactions": transactions})
        schedule = _schedule(client, league, week, last_regular_week)
        projections_ahead = _projections_ahead(client, season, week, last_season_week, points_key)
        trending = _trending(client)
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name in RAW_FILES:
        _write_json(raw_dir / f"{name}.json", data[name])
    _write_json(raw_dir / SCHEDULE_FILE, schedule)
    _write_json(raw_dir / PROJECTIONS_AHEAD_FILE, projections_ahead)
    _write_json(raw_dir / TRENDING_FILE, trending)
    if previous is not None:
        _write_json(raw_dir / PREV_TRANSACTIONS_FILE, previous)
    _write_json(raw_dir / FETCHED_FILE, {"transactions": fetched.isoformat()})


def fetch_live_raw(
        league_id: str, players_cache: Path, transport: httpx.BaseTransport | None = None,
) -> tuple[RawWeek, datetime]:
    """The raw data of the league now, in memory, and the time the rosters came back. It writes no weekly file.

    The key set is the same as load_raw gives, so the parse and the snapshot read it as a saved week.
    """
    league = f"{OFFICIAL_URL}/league/{league_id}"
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
        state = _get(client, f"{OFFICIAL_URL}/state/nfl")
        season, week = int(state["season"]), int(state["display_week"])
        rosters = _get(client, f"{league}/rosters")
        # The code takes the time right after the rosters return, because the rosters are the freshest fact here.
        # The fetcher shape has no timezone, so the time is in UTC and the caller puts it in the league timezone.
        fetched = datetime.now(UTC)
        # The stats are None on a failed call, so the snapshot names them stale. An empty list is no game yet.
        stats = _get_or_none(client, f"{UNOFFICIAL_URL}/stats/nfl/{season}/{week}", _position_params())
        data = _league_raw(client, league, season, week, players_cache,
                           {"state": state, "rosters": rosters, "stats": stats})
    return RawWeek.model_validate(data), fetched


def fetch_past_week(
        league_id: str, season: int, week: int, out_dir: Path, transport: httpx.BaseTransport | None = None,
) -> RawPastWeek:
    """Save the four history files of `week` into `out_dir`, and give them back as the raw models."""
    league = f"{OFFICIAL_URL}/league/{league_id}"
    with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
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
    return RawPastWeek.model_validate(data)


def load_raw(raw_dir: Path) -> RawWeek:
    raw: dict[str, object] = {}
    for name in RAW_FILES:
        with (raw_dir / f"{name}.json").open(encoding="utf-8") as f:
            raw[name] = json.load(f)
    _read_if_exists(raw, "schedule", raw_dir / SCHEDULE_FILE)
    _read_if_exists(raw, "projections_ahead", raw_dir / PROJECTIONS_AHEAD_FILE)
    _read_if_exists(raw, "trending", raw_dir / TRENDING_FILE)
    return RawWeek.model_validate(raw)


def _read_if_exists(raw: dict[str, object], key: str, path: Path) -> None:
    """Put the JSON of `path` in `raw` at `key`. A file that does not exist adds no key."""
    if path.exists():
        raw[key] = json.loads(path.read_text(encoding="utf-8"))


def league_settings(league: RawLeague) -> LeagueSettings:
    """The League settings of a Sleeper league file. GLOSSARY.md, "League settings"."""
    settings = league.settings
    if settings.num_teams is None or settings.playoff_teams is None or settings.playoff_week_start is None:
        raise ValueError("The league file has no num_teams, playoff_teams, or playoff_week_start, so it gives no sizes.")
    slots = tuple(slot for slot in league.roster_positions if slot not in BENCH_SLOTS)
    return LeagueSettings(
        team_count=settings.num_teams,
        playoff_spots=settings.playoff_teams,
        bye_count=bracket_byes(settings.playoff_teams),
        star_rank_by_position=star_ranks(settings.num_teams, slots),
        roster_slots=slots,
        # The playoff bracket starts the week after the regular season ends.
        last_regular_week=settings.playoff_week_start - 1,
        reception_points=league.scoring_settings.get("rec", 0.0),
        median_game=settings.league_average_match == 1,
    )


def fetch_settings(
        league_id: str, cache: Path, transport: httpx.BaseTransport | None = None) -> LeagueSettings:
    """The League settings of the league `league_id`. The league file of the season at `cache` keeps them, so a
    saved file means no fetch. The sizes of a season do not change, so the file never goes stale."""
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=TIMEOUT_SECONDS, transport=transport) as client:
            _write_json(cache, _get(client, f"{OFFICIAL_URL}/league/{league_id}"))
    return league_settings(RawLeague.model_validate_json(cache.read_text(encoding="utf-8")))


class SleeperProvider:
    """The Sleeper implementation of the Provider protocol. Each method calls the module function of the same fetch.

    The class gives one object that satisfies Provider, so a caller can swap the provider for another one.
    The module functions stay, because the tests and the CLI call them with the Sleeper arguments.
    The cache dir holds the players file, which every league of the repo shares. The entry of a run builds the adapter
    with the shared NFL cache dir, so no fetch takes a cache argument.
    The transport goes to each httpx client. None is the real network, and a test passes an httpx.MockTransport.
    """

    def __init__(self, cache_dir: Path, transport: httpx.BaseTransport | None = None):
        self.players_cache = cache_dir / PLAYERS_FILE
        self.transport = transport

    def fetch_week(
            self, league_id: str, season: int, week: int, raw_dir: Path, tz: ZoneInfo,
            last_regular_week: int, last_season_week: int, points_key: str) -> RawWeek:
        fetch_week(league_id, season, week, raw_dir, self.players_cache, tz, last_regular_week, last_season_week,
                   points_key, self.transport)
        # The build reads the week from the saved files, so the model it gets is the one a rebuild loads.
        return load_raw(raw_dir)

    def fetch_settings(self, league_id: str, cache: Path) -> LeagueSettings:
        return fetch_settings(league_id, cache, self.transport)

    def fetch_live(self, league_id: str) -> tuple[RawWeek, datetime]:
        return fetch_live_raw(league_id, self.players_cache, self.transport)

    def fetch_past_leg(self, league_id: str, season: int, week: int, out_dir: Path) -> RawPastWeek:
        return fetch_past_week(league_id, season, week, out_dir, self.transport)

    # The protocol needs this fetch. No pipeline caller reads it yet.
    def fetch_players(self) -> dict[str, dict]:
        return fetch_players(self.players_cache, self.transport)

    def fetch_projections(
            self, season: int, week: int, last_regular_week: int, points_key: str) -> list[RawAheadWeek]:
        return fetch_projections_ahead(season, week, last_regular_week, points_key, self.transport)
