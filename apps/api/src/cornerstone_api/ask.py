"""
The ask route of the front door: one Jev request per typed question, and the route table in code that reads its answers.
The app mounts the router at /clients/<slug>/ behind the passphrase. A miss writes one entry in the miss log.
"""
import logging
from collections.abc import Callable
from dataclasses import dataclass
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
from cornerstone_api.miss_log import MissLog
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

RouteKind = Literal["topic", "free", "miss", "refuse"]
# The team name of each roster of the league, by roster id. The app gives the live rosters of the client.
Rosters = Callable[[], dict[int, str]]


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


def route_question(jev: Jev, question: str, teams: list[str], season: int, week: int) -> Route:
    """One Jev request for `question` over the team names `teams` in week `week` of `season`, and its route.

    A failed request raises JevError.
    """
    answers = jev.ask(route_state(question, teams, season, week), route_questions(teams))
    kind, topic, suggestion = decide(answers)
    team = None
    if kind != "refuse" and _level(answers.nouls[NAMES_TEAM]) == "yes":
        by_key = {team_key(name): name for name in teams}
        team = by_key[_ranked(answers.choices[TEAM])[0]]
    return Route(kind=kind, topic=topic, team=team, closest=_ranked(answers.choices[TOPIC])[:CLOSEST_COUNT],
                 suggestion=suggestion, jev=answers)


@dataclass
class Asker:
    """The ask route of one client: its season, its Jev, its miss log, its rosters, and its clock."""

    season: int
    jev: Jev
    misses: MissLog
    rosters: Rosters
    clock: Callable[[], datetime]


def client_asker(request: Request) -> Asker:
    """The ask route of the client of the path. A slug that the app does not serve has none, so it is 404."""
    asker = request.app.state.askers.get(request.path_params.get("slug"))
    if asker is None:
        raise HTTPException(status_code=404, detail="This client has no ask box.")
    return asker


ClientAsker = Annotated[Asker, Depends(client_asker)]


class AskRequest(BaseModel):
    """The body of the ask route: the question as the manager typed it, the roster id of Your team, and the latest week
    that the site shows, because each Topic Answer of the site covers that week only."""

    question: str = Field(min_length=1, max_length=QUESTION_MAX)
    roster_id: int
    week: int = Field(ge=1, le=WEEK_MAX)


@router.post("/ask")
def ask(body: AskRequest, asker: ClientAsker) -> dict:
    """The route of one typed question, with each Jev answer. A failed Jev request is a 503, never a "no"."""
    rosters = asker.rosters()
    if body.roster_id not in rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    question = body.question.strip()
    try:
        route = route_question(asker.jev, question, list(rosters.values()), asker.season, body.week)
    except JevError as error:
        logger.warning("The route of a question failed (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None
    if route.kind == "miss":
        asker.misses.write(question, body.roster_id, rosters[body.roster_id], route.closest, asker.clock())
    by_name = {name: roster_id for roster_id, name in rosters.items()}
    return {
        "route": route.kind,
        "topic": route.topic,
        "team": None if route.team is None else by_name[route.team],
        "closest": route.closest,
        "suggestion": route.suggestion,
        "jev": {"model": route.jev.model, "nouls": route.jev.nouls, "choices": route.jev.choices},
    }
