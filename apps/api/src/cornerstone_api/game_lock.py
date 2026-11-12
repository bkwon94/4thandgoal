"""
The game lock of Start or sit: the kickoff of each NFL game of a week from the Sleeper `scores` query, with the ESPN
scoreboard as the fallback, and the rule that locks a game once it starts (decision 06 of front-door-lineup).
"""
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

logger = logging.getLogger(__name__)

# The GraphQL endpoint of the sleeper.com web app. It needs no key, and it has no docs, so Sleeper can change it.
SLEEPER_GRAPHQL_URL = "https://sleeper.com/graphql"
# The public scoreboard of ESPN. It needs no key either, and it has no docs.
ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
TIMEOUT_SECONDS = 10
SCORES_QUERY = ("query batch_scores {{ scores(sport: \"nfl\", season_type: \"regular\", season: \"{season}\", "
                "week: {week}) {{ date game_id metadata season season_type sport status week start_time }} }}")
# The ESPN codes that differ from the Sleeper codes. Every other team has the same code in both.
ESPN_TO_SLEEPER = {"WSH": "WAS"}

ScoresFetcher = Callable[[int, int], dict]


class KickoffsError(ValueError):
    """Neither source gave the kickoffs of the week, so no lineup can respect the game lock."""


@dataclass(frozen=True)
class Kickoff:
    """One NFL game of the week: the two Sleeper team codes, the kickoff in UTC, and the live flag of its start."""

    home: str
    away: str
    start: datetime
    started: bool

    def locked(self, now: datetime) -> bool:
        """True when the game has started: the clock is past the kickoff, or the source says it started. The two
        checks cover a slow flag and a wrong clock."""
        return self.started or now >= self.start


def fetch_sleeper_scores(season: int, week: int) -> dict:
    """The answer of the Sleeper `scores` query for `week` of `season`, as JSON."""
    query = {"operationName": "batch_scores", "variables": {}, "query": SCORES_QUERY.format(season=season, week=week)}
    response = httpx.post(SLEEPER_GRAPHQL_URL, json=query, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def fetch_espn_scoreboard(season: int, week: int) -> dict:
    """The ESPN scoreboard of `week` of the regular season of `season`, as JSON."""
    response = httpx.get(ESPN_SCOREBOARD_URL, params={"seasontype": 2, "week": week, "dates": season},
                         timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def sleeper_kickoffs(payload: dict) -> list[Kickoff]:
    """The games of a `scores` answer. `start_time` is the kickoff in epoch ms, UTC."""
    games = []
    for game in payload["data"]["scores"]:
        meta = game["metadata"]
        games.append(Kickoff(home=meta["home_team"], away=meta["away_team"],
                             start=datetime.fromtimestamp(game["start_time"] / 1000, UTC),
                             started=bool(meta.get("has_started"))))
    return games


def _sleeper_code(espn: str) -> str:
    return ESPN_TO_SLEEPER.get(espn, espn)


def espn_kickoffs(payload: dict) -> list[Kickoff]:
    """The games of an ESPN scoreboard, with the team codes of Sleeper. A game is started past the state "pre"."""
    games = []
    for event in payload["events"]:
        teams = {side["homeAway"]: side["team"]["abbreviation"] for side in event["competitions"][0]["competitors"]}
        games.append(Kickoff(home=_sleeper_code(teams["home"]), away=_sleeper_code(teams["away"]),
                             start=datetime.fromisoformat(event["date"]),
                             started=event["status"]["type"]["state"] != "pre"))
    return games


def week_kickoffs(season: int, week: int, sleeper: ScoresFetcher, espn: ScoresFetcher) -> list[Kickoff]:
    """The kickoffs of the week, fresh for each Answer, because a moved game changes its kickoff. The Sleeper query
    comes first, and the ESPN scoreboard answers when it fails or gives no game. Raises KickoffsError when both fail."""
    try:
        games = sleeper_kickoffs(sleeper(season, week))
        if games:
            return games
        logger.warning("The Sleeper scores query gave no game of week %d, so the ESPN scoreboard answers", week)
    except (httpx.HTTPError, OSError, ValueError, KeyError, TypeError) as error:
        logger.warning("The Sleeper scores query failed (%s), so the ESPN scoreboard answers", error)
    try:
        games = espn_kickoffs(espn(season, week))
    except (httpx.HTTPError, OSError, ValueError, KeyError, TypeError) as error:
        raise KickoffsError(f"no source gave the kickoffs of week {week} ({error})") from None
    if not games:
        raise KickoffsError(f"no source gave the kickoffs of week {week}")
    return games
