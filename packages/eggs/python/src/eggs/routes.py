"""
The eggs route groups of the API: the open egg check and egg board, the claim, and the drop and the undo.
The app mounts each group at /clients/<slug>/eggs/ with its own guard, and each route reads the Hunt of its client.
"""
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, tzinfo
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from eggs.conditions import conditions_hold
from eggs.letters import drop_letters
from eggs.rules import refusal, winner
from eggs.store import AlreadyClaimed, Claim, Egg, EggStore
from eggs.tokens import ClaimTokens
from eggs.values import EggsValues

# The open routes: the egg check and the egg board need no key. The check has its own limit, so it has its own group.
check_router = APIRouter()
open_router = APIRouter()
# The claim needs the passphrase of the client. The app gives the guard.
claim_router = APIRouter()
# The drop and the undo need the commissioner key. The app gives the guard.
commissioner_router = APIRouter()

# The team name of each roster of the league, by roster id. The API app gives the live rosters of the client.
Rosters = Callable[[], dict[int, str]]

CLAIMED_FIRST = "Another manager claimed first."
BAD_TOKEN = "The claim is too late or the egg is not found. Find the egg again."


@dataclass
class Hunt:
    """The egg hunt of one client: its store, its package values, its claim tokens, its rosters, and its clock."""

    store: EggStore
    values: EggsValues
    rosters: Rosters
    clock: Callable[[], datetime]
    tokens: ClaimTokens = field(default_factory=ClaimTokens)
    # The timezone of the client. The clock window and the weekday of an egg hold on the clock of the client.
    tz: tzinfo | None = None
    # FastAPI runs the sync routes in a thread pool. The lock keeps the take of a token and its claim in one step.
    lock: threading.Lock = field(default_factory=threading.Lock)


def client_hunt(request: Request) -> Hunt:
    """The hunt of the client of the path. A client without the eggs package has none, so its eggs routes are 404."""
    hunt = request.app.state.hunts.get(request.path_params.get("slug"))
    if hunt is None:
        raise HTTPException(status_code=404, detail="This client has no egg hunt.")
    return hunt


ClientHunt = Annotated[Hunt, Depends(client_hunt)]


class CheckRequest(BaseModel):
    """The body of the egg check: the page, the stable id of the element, the action, the trail of a tap combo, the
    word of a selection, and the state of the conditions."""

    page: str
    target: str
    action: str
    # The stable ids of the two taps before the double-tap of a tap combo, oldest first. An egg holds it as "trail".
    trail: list[str] = []
    # The selected word of the action "select", in lower case. An egg holds it as "word".
    word: str | None = None
    conditions: dict[str, Any] = {}

    def state(self) -> dict[str, Any]:
        """The state that the conditions of an egg match: the conditions, the trail, and the word."""
        return {**self.conditions, "trail": self.trail, "word": self.word}


@check_router.post("/check")
def check(body: CheckRequest, hunt: ClientHunt) -> dict:
    """No match, a match with the letter and a one-time claim token, or a match on an egg that a manager claimed."""
    now = hunt.clock()
    local = now.astimezone(hunt.tz) if hunt.tz is not None else now
    for egg in hunt.store.find(body.page, body.target, body.action):
        # Each condition of the egg must hold in the state that the listener sends and on the clock of the client.
        if not conditions_hold(egg.conditions, body.state(), local):
            continue
        if hunt.store.claim_of(egg.id) is not None:
            return {"match": True, "claimed": True, "letter": egg.letter}
        token = hunt.tokens.issue(egg.id, now)
        return {"match": True, "claimed": False, "letter": egg.letter, "token": token}
    return {"match": False}


class ClaimRequest(BaseModel):
    """The body of the claim: the token of the check, the roster, and the egg word, or None for a block."""

    token: str
    roster_id: int
    word: str | None
    browser: str | None = None


def _letters(claims: list[Claim], roster_id: int, word: str) -> list[str]:
    """The letters of the roster in the egg word, in the order of the claims."""
    return [claim.letter for claim in reversed(claims) if claim.roster_id == roster_id and claim.word == word]


@claim_router.post("/claim")
def claim(body: ClaimRequest, hunt: ClientHunt) -> dict:
    """Claim the egg of the token for the roster. The answer holds the letters of the roster in each egg word."""
    words = [each.word for each in hunt.values.words]
    if body.word is not None and body.word not in words:
        raise HTTPException(status_code=422, detail=f"{body.word} is not an egg word.")
    if body.roster_id not in hunt.rosters():
        raise HTTPException(status_code=422, detail=f"Roster {body.roster_id} is not in the league.")
    now = hunt.clock()
    with hunt.lock:
        egg_id = hunt.tokens.peek(body.token, now)
        if egg_id is None:
            raise HTTPException(status_code=410, detail=BAD_TOKEN)
        letter = next(each.letter for each in hunt.store.eggs() if each.id == egg_id)
        # A refusal comes before the take, so the token stays good for a claim that stands.
        reason = refusal(hunt.values, hunt.store.claims(), body.roster_id, body.word, letter)
        if reason is not None:
            raise HTTPException(status_code=422, detail=reason)
        hunt.tokens.take(body.token, now)
        try:
            hunt.store.claim(egg_id, body.roster_id, body.word, body.browser, now)
        except AlreadyClaimed:
            raise HTTPException(status_code=409, detail=CLAIMED_FIRST) from None
    claims = hunt.store.claims()
    # The claim fills the egg word when the manager now wins it.
    won = body.word is not None and winner(claims, body.word) == body.roster_id
    return {
        "egg_id": egg_id,
        "letter": letter,
        "roster_id": body.roster_id,
        "word": body.word,
        "letters": {word: _letters(claims, body.roster_id, word) for word in words},
        "winner": {"roster_id": body.roster_id, "word": body.word} if won else None,
    }


def _winner_of(claims: list[Claim], teams: dict[int, str], word: str) -> dict | None:
    """The winner of the egg word with the team name, or None while the word is open."""
    roster_id = winner(claims, word)
    return None if roster_id is None else {"roster_id": roster_id, "team": teams.get(roster_id, "")}


def _last_drop(eggs: list[Egg]) -> dict | None:
    """The week, the count, and the time of the newest drop, or None before the first drop. The egg banner reads it."""
    if not eggs:
        return None
    # The store lists the eggs in the order of the drop, so the last egg is of the newest drop.
    newest = eggs[-1]
    count = sum(1 for egg in eggs if egg.week == newest.week)
    return {"week": newest.week, "count": count, "dropped_at": newest.dropped_at}


@open_router.get("/board")
def board(hunt: ClientHunt) -> dict:
    """The egg board: the counts, the state of each slot by week, each manager in each egg word, the latest claims,
    and the week, the count, and the time of the last drop.

    It holds no page, no target, no action, and no condition, so the board gives no hint.
    """
    values = hunt.values
    eggs = hunt.store.eggs()
    claims = hunt.store.claims()
    found = {claim.egg_id for claim in claims}
    teams = hunt.rosters()
    # The commissioner places every egg, so the board and the claim sheet list only the managers who hunt.
    managers = [{"roster_id": roster_id, "team": team} for roster_id, team in sorted(teams.items())
                if roster_id != values.commissioner]
    weeks = list(range(values.first_week, values.last_week + 1))
    slots = []
    for week in weeks:
        dropped = ["found" if egg.id in found else "out" for egg in eggs if egg.week == week]
        slots.append({"week": week, "slots": dropped + ["future"] * max(0, values.drop_size - len(dropped))})
    return {
        "counts": {
            "left": len(eggs) - len(found),
            "found": len(found),
            "to_drop": max(0, len(weeks) * values.drop_size - len(eggs)),
        },
        "weeks": slots,
        "words": [
            {
                "word": each.word,
                "prize": each.prize,
                "winner": _winner_of(claims, teams, each.word),
                "managers": [{**manager, "letters": _letters(claims, manager["roster_id"], each.word)}
                             for manager in managers],
            }
            for each in values.words
        ],
        # A block takes an egg into no egg word, so the feed shows no block.
        "latest": [{"roster_id": claim.roster_id, "team": teams.get(claim.roster_id, ""), "letter": claim.letter,
                    "word": claim.word, "claimed_at": claim.claimed_at} for claim in claims if claim.word is not None],
        "managers": managers,
        "last_drop": _last_drop(eggs),
    }


class DropEgg(BaseModel):
    """One confirmed egg of a drop: where it hides, and the action and the conditions that find it.

    The API gives the letter by the letter rule, so the body holds none, and the model refuses a letter.
    """

    model_config = ConfigDict(extra="forbid")

    page: str
    target: str
    action: str
    conditions: dict[str, Any] = {}


class DropRequest(BaseModel):
    """The body of the drop: the week and its confirmed eggs."""

    week: int
    eggs: list[DropEgg]


@commissioner_router.post("/drop")
def drop(body: DropRequest, hunt: ClientHunt) -> dict:
    """Give each egg of the week its letter by the letter rule and make the eggs live.

    A second drop of one week adds nothing and answers with the eggs there.
    """
    before = len(hunt.store.eggs(body.week))
    managers = [roster_id for roster_id in hunt.rosters() if roster_id != hunt.values.commissioner]
    letters = drop_letters([each.word for each in hunt.values.words], managers, hunt.store.claims(), len(body.eggs))
    eggs = hunt.store.drop(body.week, [{**egg.model_dump(), "letter": letter}
                                       for egg, letter in zip(body.eggs, letters, strict=True)], hunt.clock())
    return {
        "week": body.week,
        "dropped": len(eggs) - before,
        "eggs": [{"id": egg.id, "page": egg.page, "target": egg.target, "action": egg.action,
                  "conditions": egg.conditions, "letter": egg.letter} for egg in eggs],
    }


class UndoRequest(BaseModel):
    """The body of the undo: the id of the egg whose claim goes."""

    egg_id: int


@commissioner_router.post("/undo")
def undo(body: UndoRequest, hunt: ClientHunt) -> dict:
    """Undo the claim of the egg, so the egg is live again. The claims table keeps the row with its undo time."""
    if not hunt.store.undo(body.egg_id, hunt.clock()):
        raise HTTPException(status_code=404, detail=f"No claim holds the egg {body.egg_id}.")
    return {"egg_id": body.egg_id, "undone": True}
