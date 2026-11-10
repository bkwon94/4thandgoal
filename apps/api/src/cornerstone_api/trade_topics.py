"""
The trade Topics of the front door: the trade check calls the analyze press, trade ideas the find press, and sell high
the sell high press. Each route streams a plain step for each stage of the Advisor, then the whole Answer.
"""
import contextvars
import json
import logging
import queue
import threading
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from analyzer import routes as analyzer_routes
from analyzer.routes import FindRequest, ServedClient
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from cornerstone_api.ask import QUESTION_MAX, YES, ClientAsker
from cornerstone_api.trade_wording import (
    GETS_NAMED,
    GETS_PLAYER,
    GIVES_NAMED,
    GIVES_PLAYER,
    option_keys,
    pick_questions,
    pick_state,
    player_line,
)
from league.jev_port import Jev, JevError, JevResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# The line of a failed Jev pick or a failed press with no message of its own. A failed call is never a "no".
RETRY_LINE = "The question did not go through. Ask again."
# The header of the stream protocol of the AI SDK, so useChat can read the stream as it is.
STREAM_HEADERS = {"x-vercel-ai-ui-message-stream": "v1", "Cache-Control": "no-cache"}

# One part of the stream: its type, such as "data-step", and its data.
Emit = Callable[[str, dict], None]


@dataclass(frozen=True)
class Pick:
    """The pick of one side: the probability that the question names a player, and the top player of the Choice with
    his probability and his roster. A sure pick has both above YES, so the form fills only a player that Jev is sure
    of."""

    named: float
    player_id: str
    name: str
    probability: float
    roster_id: int

    @property
    def sure(self) -> bool:
        return self.named > YES and self.probability > YES


def _top(probabilities: dict[str, float]) -> tuple[str, float]:
    key = max(probabilities, key=lambda option: probabilities[option])
    return key, probabilities[key]


def pick_players(jev: Jev, question: str, teams: list[dict], asker: int) -> tuple[Pick, Pick, JevResponse]:
    """One Jev request for the player that the manager gives and the player that the manager gets, over the real
    rosters of `teams`, as the teams route gives them. A failed request raises JevError."""
    team_of = {player["player_id"]: team for team in teams for player in team["players"]}
    mine = next(team for team in teams if team["roster_id"] == asker)
    others = [team for team in teams if team["roster_id"] != asker]

    def line(player: dict, team: str | None = None) -> str:
        return player_line(player["name"], player["position"], player["nfl_team"], team)

    gives = {player["player_id"]: line(player) for player in mine["players"]}
    gets = {player["player_id"]: line(player, team["team"]) for team in others for player in team["players"]}
    give_keys = option_keys({pid: _name(team_of[pid], pid) for pid in gives})
    get_keys = option_keys({pid: _name(team_of[pid], pid) for pid in gets})
    state = pick_state(question, mine["team"], list(gives.values()),
                       {team["team"]: [line(player) for player in team["players"]] for team in others})
    answers = jev.ask(state, pick_questions({give_keys[pid]: text for pid, text in gives.items()},
                                            {get_keys[pid]: text for pid, text in gets.items()}))

    def side(named: str, choice: str, keys: dict[str, str]) -> Pick:
        key, probability = _top(answers.choices[choice])
        pid = next(pid for pid, option in keys.items() if option == key)
        return Pick(named=answers.nouls[named], player_id=pid, name=_name(team_of[pid], pid), probability=probability,
                    roster_id=team_of[pid]["roster_id"])

    return side(GIVES_NAMED, GIVES_PLAYER, give_keys), side(GETS_NAMED, GETS_PLAYER, get_keys), answers


def _name(team: dict, player_id: str) -> str:
    return next(player["name"] for player in team["players"] if player["player_id"] == player_id)


def _line(error: HTTPException) -> str:
    """The plain line of a failed press: its own message, or the retry line."""
    detail = error.detail
    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
        return detail["message"]
    return detail if isinstance(detail, str) else RETRY_LINE


def _part(kind: str, data: dict | None = None) -> str:
    body = {"type": kind} if data is None else {"type": kind, "data": data}
    return f"data: {json.dumps(body)}\n\n"


def stream(work: Callable[[Emit], None]) -> StreamingResponse:
    """The event stream of one press: `work` runs in its own thread and emits each part as it comes, so each stage of
    the Advisor reaches the site before the whole Answer. A failed press ends the stream with one error part."""
    parts: queue.Queue[str | None] = queue.Queue()

    def emit(kind: str, data: dict) -> None:
        parts.put(_part(kind, data))

    def run() -> None:
        try:
            work(emit)
        except HTTPException as error:
            emit("data-error", {"status": error.status_code, "line": _line(error)})
        except JevError as error:
            logger.warning("The player pick of a trade check failed (%s)", type(error).__name__)
            emit("data-error", {"status": 503, "line": RETRY_LINE})
        except Exception:
            logger.exception("A trade press of the front door failed")
            emit("data-error", {"status": 500, "line": RETRY_LINE})
        finally:
            parts.put(None)

    # The copy of the context carries the press meter, so the cost line of the press counts each Claude call.
    threading.Thread(target=contextvars.copy_context().run, args=(run,), name="trade-press", daemon=True).start()

    def events() -> Iterator[str]:
        yield _part("start")
        while (part := parts.get()) is not None:
            yield part
        yield _part("finish")
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers=STREAM_HEADERS)


def _step(emit: Emit) -> Callable[[str], None]:
    return lambda line: emit("data-step", {"line": line})


def _teams(asker: ClientAsker, served: analyzer_routes.Served, roster_id: int) -> list[dict]:
    """The teams of the league from the cached teams route. A roster that is not in the league is 422, before the
    stream starts."""
    teams = analyzer_routes.teams(asker.season, served)["teams"]
    if roster_id not in {team["roster_id"] for team in teams}:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    return teams


class TradeCheckRequest(BaseModel):
    """The body of the trade check: the question as the manager typed it, and the roster id of Your team."""

    question: str = Field(min_length=1, max_length=QUESTION_MAX)
    roster_id: int


@router.post("/trade-check")
def trade_check(request: Request, body: TradeCheckRequest, asker: ClientAsker,
                served: ServedClient) -> StreamingResponse:
    """The trade check of a typed question. With two sure picks, the steps of the analyze press and its document.
    With an unsure pick, the form of the Trade page with each sure player and no unsure one (AT-58)."""
    teams = _teams(asker, served, body.roster_id)
    question = body.question.strip()

    def work(emit: Emit) -> None:
        gives, gets, answers = pick_players(asker.jev, question, teams, body.roster_id)
        emit("data-picks", {"model": answers.model, "gives": {**asdict(gives), "sure": gives.sure},
                            "gets": {**asdict(gets), "sure": gets.sure}})
        if not (gives.sure and gets.sure):
            emit("data-answer", {"kind": "form", "form": {
                "asker": body.roster_id, "partner": gets.roster_id if gets.sure else None,
                "gives": [gives.player_id] if gives.sure else [], "gets": [gets.player_id] if gets.sure else []}})
            return
        step = _step(emit)
        step(f"Found {gives.name} and {gets.name}")
        trade = ProposedTrade(season=asker.season, asker=body.roster_id, sides=[
            TradeSide(roster_id=body.roster_id, gives=[GivenPlayer(player_id=gives.player_id, to=gets.roster_id)]),
            TradeSide(roster_id=gets.roster_id, gives=[GivenPlayer(player_id=gets.player_id, to=body.roster_id)])])
        document = analyzer_routes.analyze_trade(request, trade, served, step)
        emit("data-answer", {"kind": "check", "document": document})

    return stream(work)


class TradeIdeasRequest(BaseModel):
    """The body of trade ideas: the roster id of Your team, and the partner roster that a typed question names."""

    roster_id: int
    partner: int | None = None


@router.post("/trade-ideas")
def trade_ideas(request: Request, body: TradeIdeasRequest, asker: ClientAsker,
                served: ServedClient) -> StreamingResponse:
    """Trade ideas for Your team: the steps of the find press and its document. It runs in each client, whatever the
    `finder` flag of the analyzer page says (spec, "The judgment Topics")."""
    _teams(asker, served, body.roster_id)

    def work(emit: Emit) -> None:
        pair = FindRequest(season=asker.season, asker=body.roster_id, partner=body.partner)
        document = analyzer_routes.find_trades(request, pair, served, _step(emit))
        emit("data-answer", {"kind": "ideas", "document": document})

    return stream(work)



class SellHighRequest(BaseModel):
    """The body of sell high: the roster id of Your team."""

    roster_id: int


@router.post("/sell-high")
def sell_high(request: Request, body: SellHighRequest, asker: ClientAsker, served: ServedClient) -> StreamingResponse:
    """Sell high or buy low for Your team: the steps of the sell high press and its document. The Advisor picks the
    players of the roster to sell from their facts side by side, and writes why."""
    _teams(asker, served, body.roster_id)

    def work(emit: Emit) -> None:
        document = analyzer_routes.sell_high_press(request, asker.season, body.roster_id, served, _step(emit))
        emit("data-answer", {"kind": "sell", "document": document})

    return stream(work)
