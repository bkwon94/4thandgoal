"""
The ask route of the front door: one Jev request per typed question, and the route table in code that reads its answers.
The app mounts the router at /clients/<slug>/ behind the passphrase. A miss writes one entry in the miss log.
"""
import dataclasses
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from cornerstone_api.ask_wording import (
    ABOUT_LEAGUE,
    ABUSE,
    DATA_CAN_ANSWER,
    FITS_TOPIC,
    NAMES_TEAM,
    TEAM,
    TOPIC,
    route_questions,
    route_state,
    team_key,
)
from cornerstone_api.caps import Caps
from cornerstone_api.chat_turns import Turn, Turns, with_turns
from cornerstone_api.miss_log import MissLog
from cornerstone_api.named_players import named_players
from league.jev_port import Jev, JevError, JevResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# The hard cutoffs of the spec on each Noul: above YES reads as yes, below NO reads as no, and between is unsure.
YES = 0.7
NO = 0.3
# An honest miss offers this many of the closest Topics.
CLOSEST_COUNT = 3
# A longer body is not a question for the ask box, so the API answers 422 before any Jev call.
QUESTION_MAX = 300
# The last week of a fantasy season that the site can show.
WEEK_MAX = 18
# How long the route of a free answer stays kept for its stream. The site calls the stream right after the route.
FREE_ROUTE_SECONDS = 600

RouteKind = Literal["topic", "free", "miss", "refuse"]
# The kinds of the answer of the ask route: a route, or the calm line of a cap in place of a free answer.
AskKind = Literal["topic", "free", "miss", "refuse", "cap"]
# The team name of each roster of the league, by roster id. The app gives the live rosters of the client.
Rosters = Callable[[], dict[int, str]]
# The name of each rostered player by player id, for each roster of the league by roster id.
RosterPlayers = Callable[[], dict[int, dict[str, str]]]
# The Topic of the lineup of Your team. A typed start question about a player of another roster is not about it.
START_SIT = "start_sit"


@dataclass(frozen=True)
class Route:
    """The route of one question: its kind, the Topic of a Topic route, the team that the question names, the closest
    Topics of a miss, the Suggestion under a free answer, and the Jev answers that decided it."""

    kind: RouteKind
    topic: str | None
    team: str | None
    closest: list[str]
    suggestion: str | None
    jev: JevResponse


def _level(probability: float) -> str:
    return "yes" if probability > YES else "no" if probability < NO else "unsure"


def decide(answers: JevResponse) -> tuple[RouteKind, str | None, str | None]:
    """The route table of the spec over the Jev answers: the kind, the Topic of a Topic route, and the Suggestion.

    Each row is a hard rule, in this order. Jev makes each judgment, and code only reads the cutoffs.
    """
    level = {key: _level(p) for key, p in answers.nouls.items()}
    top = _ranked(answers.choices[TOPIC])[0]
    if level[ABUSE] == "yes":
        return "refuse", None, None
    # The unsure band of "about the league" is a miss, because "write me a poem about my kicker" scored 0.39.
    if level[ABOUT_LEAGUE] != "yes":
        return "miss", None, None
    if level[FITS_TOPIC] == "yes":
        return "topic", top, None
    # A stat lookup sits halfway between a Topic and a free answer, so a half fit shows its Topic as a Suggestion.
    if level[DATA_CAN_ANSWER] == "yes":
        return "free", None, top if level[FITS_TOPIC] == "unsure" else None
    # A judgment question such as "worst move all year" lands in the unsure band, and the check of the free answer
    # holds a wrong answer back.
    if level[DATA_CAN_ANSWER] == "unsure":
        return "free", None, None
    return "miss", None, None


def _ranked(probabilities: dict[str, float]) -> list[str]:
    return sorted(probabilities, key=lambda key: -probabilities[key])


def route_question(jev: Jev, question: str, teams: list[str], season: int, week: int,
                   turns: list[Turn] | None = None) -> Route:
    """One Jev request for `question` over the team names `teams` in week `week` of `season`, and its route.

    The earlier `turns` of the Thread go in the state, so a follow-up routes like the whole question would.
    A failed request raises JevError.
    """
    state = with_turns(route_state(question, teams, season, week), turns or [])
    answers = jev.ask(state, route_questions(teams))
    kind, topic, suggestion = decide(answers)
    team = None
    if kind != "refuse" and _level(answers.nouls[NAMES_TEAM]) == "yes":
        by_key = {team_key(name): name for name in teams}
        team = by_key[_ranked(answers.choices[TEAM])[0]]
    return Route(kind=kind, topic=topic, team=team, closest=_ranked(answers.choices[TOPIC])[:CLOSEST_COUNT],
                 suggestion=suggestion, jev=answers)


class FreeRoutes:
    """The free routes that the ask route gave, in memory, each for FREE_ROUTE_SECONDS. The free answer reads its route
    here, so each typed question gets one Jev request, and only a question routed to a free answer reaches Claude.

    The key is the roster id, the week, and the question text. A restart drops the map, so the manager asks again.
    """

    def __init__(self, seconds: float = FREE_ROUTE_SECONDS, now: Callable[[], float] = time.monotonic) -> None:
        self.seconds = seconds
        self.now = now
        self._routes: dict[tuple[int, int, str], tuple[float, Route]] = {}
        self._lock = threading.Lock()

    def put(self, roster_id: int, week: int, question: str, route: Route) -> None:
        """Keep the free route of `question`. Each route past its time limit leaves the map here, so the map stays
        small."""
        now = self.now()
        with self._lock:
            self._routes = {key: kept for key, kept in self._routes.items() if now - kept[0] < self.seconds}
            self._routes[(roster_id, week, question)] = (now, route)

    def get(self, roster_id: int, week: int, question: str) -> Route | None:
        """The kept free route of `question`, or None when the ask route gave none in the time limit."""
        with self._lock:
            kept = self._routes.get((roster_id, week, question))
        if kept is None or self.now() - kept[0] >= self.seconds:
            return None
        return kept[1]


@dataclass
class Asker:
    """The ask route of one client: its season, its Jev, its miss log, its rosters, its clock, its caps, the free
    routes it gave, and the rostered players. Each client has its own Asker, so the free routes of one client never reach another."""

    season: int
    jev: Jev
    misses: MissLog
    rosters: Rosters
    clock: Callable[[], datetime]
    caps: Caps
    free_routes: FreeRoutes = field(default_factory=FreeRoutes)
    # The rostered players of the league. None reads no names, so a start question always stays with Start or sit.
    roster_players: RosterPlayers | None = None


def client_asker(request: Request) -> Asker:
    """The ask route of the client of the path. A slug that the app does not serve has none, so it is 404."""
    asker = request.app.state.askers.get(request.path_params.get("slug"))
    if asker is None:
        raise HTTPException(status_code=404, detail="This client has no ask box.")
    return asker


ClientAsker = Annotated[Asker, Depends(client_asker)]


class AskRequest(BaseModel):
    """The body of the ask route: the question as the manager typed it, the roster id of Your team, the latest week
    that the site shows, because each Topic Answer of the site covers that week only, and the earlier turns of the
    Thread, oldest first."""

    question: str = Field(min_length=1, max_length=QUESTION_MAX)
    roster_id: int
    week: int = Field(ge=1, le=WEEK_MAX)
    turns: Turns = Field(default_factory=list)


def _names_other_rosters(asker: Asker, question: str, roster_id: int) -> bool:
    """True when `question` names a player of a roster other than the roster of `roster_id`."""
    if asker.roster_players is None:
        return False
    rosters = asker.roster_players()
    own = rosters.get(roster_id, {})
    others = {pid: name for other, players in rosters.items() if other != roster_id for pid, name in players.items()}
    return bool(named_players(question, own, others).others)


@router.post("/ask")
def ask(body: AskRequest, asker: ClientAsker) -> dict:
    """The route of one typed question, with each Jev answer. A failed Jev request is a 503, never a "no"."""
    rosters = asker.rosters()
    if body.roster_id not in rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    question = body.question.strip()
    try:
        route = route_question(asker.jev, question, list(rosters.values()), asker.season, body.week, body.turns)
    except JevError as error:
        logger.warning("The route of a question failed (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None
    if route.kind == "topic" and route.topic == START_SIT and _names_other_rosters(asker, question, body.roster_id):
        # Start or sit is about the lineup of Your team, so a question about a player of another roster goes to the
        # free answer (AT-18).
        route = dataclasses.replace(route, kind="free", topic=None, team=None, suggestion=None)
    if route.kind == "miss":
        asker.misses.write(question, body.roster_id, rosters[body.roster_id], route.closest, asker.clock())
    if route.kind == "free":
        asker.free_routes.put(body.roster_id, body.week, question, route)
    kind: AskKind = route.kind
    line = None
    # A free answer is a Claude call, so past a cap the route gives the calm line with the closest Topics instead.
    if route.kind == "free" and (hit := asker.caps.check(body.roster_id, asker.clock())) is not None:
        logger.info("A free answer stopped at the %s cap, with no Claude call", hit.cap)
        kind, line = "cap", hit.line
    by_name = {name: roster_id for roster_id, name in rosters.items()}
    return {
        "route": kind,
        "line": line,
        "topic": route.topic,
        "team": None if route.team is None else by_name[route.team],
        "closest": route.closest,
        "suggestion": route.suggestion,
        "jev": {"model": route.jev.model, "nouls": route.jev.nouls, "choices": route.jev.choices},
    }
