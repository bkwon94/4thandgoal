"""
The trade Topics of the front door: the trade check calls the analyze press, trade ideas the find press, and sell high
the sell high press. Each route streams a plain step for each stage of the Advisor, then its key and the whole Answer.
"""
import contextvars
import hashlib
import json
import logging
import queue
import threading
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from analyzer import routes as analyzer_routes
from analyzer.finder_search import Anchor, Limit
from analyzer.routes import FindRequest, ServedClient
from analyzer.stage import Stage
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from cornerstone_api.ask import QUESTION_MAX, YES, Asker, ClientAsker
from cornerstone_api.chat_turns import Turn, Turns, with_turns
from cornerstone_api.sell_list import sell_list
from cornerstone_api.trade_block import check_block, ideas_block, rest_points
from cornerstone_api.trade_wording import (
    AIM_POSITION,
    AIMS_POSITION,
    CONTEXT,
    GETS_ALSO_NAMED,
    GETS_ALSO_PLAYER,
    GETS_NAMED,
    GETS_PLAYER,
    GIVES_ALSO_NAMED,
    GIVES_ALSO_PLAYER,
    GIVES_NAMED,
    GIVES_PLAYER,
    IDEAS_CONTEXT,
    KEEPS_NAMED,
    KEEPS_POSITION,
    KEPT_PLAYER,
    limit_questions,
    option_keys,
    pick_questions,
    pick_state,
    player_line,
)
from facts.writer import metered_press
from league.jev_port import Jev, JevError, JevResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# The line of a failed Jev pick or a failed press with no message of its own. A failed call is never a "no".
RETRY_LINE = "The question did not go through. Ask again."
# The step line of trade ideas when the typed question names no one player that Jev is sure of. The search then aims at
# the weakest slot, as a tap does.
NO_ONE_PLAYER = "Found no one player in the question, so these ideas aim at your weakest spot"
# The header of the stream protocol of the AI SDK, so useChat can read the stream as it is.
STREAM_HEADERS = {"x-vercel-ai-ui-message-stream": "v1", "Cache-Control": "no-cache"}

# One part of the stream: its type, such as "data-step", and its data.
Emit = Callable[[str, dict], None]

TradeTopic = Literal["trade_check", "trade_ideas", "sell_high"]


def trade_key(topic: TradeTopic, rosters: dict[int, list[str]], roster_id: int, partner: int | None) -> str:
    """The key of a trade Answer: its Topic and each roster that it read. Sell high reads Your team. A trade check and
    trade ideas with a partner read Your team and the partner. Trade ideas with no partner search each team, so they
    read each roster. A waiver claim or a trade on one of those rosters changes the key, so the Answer reads as stale.
    """
    if topic == "sell_high":
        read = [roster_id]
    elif partner is not None:
        read = [roster_id, partner]
    else:
        read = sorted(rosters)
    body = {"topic": topic, "rosters": {str(each): sorted(rosters[each]) for each in read}}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _send_key(asker: Asker, served: analyzer_routes.Served, emit: Emit, topic: TradeTopic, roster_id: int,
              partner: int | None) -> None:
    """Send the key of the Answer and the time of the read, before the whole Answer. The rosters come from Sleeper now,
    as the key check reads them."""
    rosters = served.sources.rosters_snapshot(asker.season).rosters
    emit("data-key", {"key": trade_key(topic, rosters, roster_id, partner), "at": asker.clock().isoformat()})


@dataclass(frozen=True)
class Pick:
    """The pick of one side: the probability that the question names a player, and the top player of the Choice with
    his probability and his roster. A sure pick has both above YES, so the form fills only a player that Jev is sure
    of.

    `also` is the pick of a second player of the side, such as the second player of a 1-for-2 trade, when Jev is sure
    that the question names two. A sure second player on another roster makes the side unsure, because the trade
    check weighs a trade of two teams only."""

    named: float
    player_id: str
    name: str
    probability: float
    roster_id: int
    also: "Pick | None" = None

    @property
    def sure(self) -> bool:
        return (self.named > YES and self.probability > YES
                and (self.second is None or self.second.roster_id == self.roster_id))

    @property
    def second(self) -> "Pick | None":
        """The sure second player of the side, or None. A second pick of the first player is no second player."""
        if self.also is None or not self.also.sure or self.also.player_id == self.player_id:
            return None
        return self.also

    @property
    def players(self) -> list["Pick"]:
        """The pick of each player of the side: the first player, then the sure second player."""
        return [self] if self.second is None else [self, self.second]


def _top(probabilities: dict[str, float]) -> tuple[str, float]:
    key = max(probabilities, key=lambda option: probabilities[option])
    return key, probabilities[key]


def pick_players(jev: Jev, question: str, teams: list[dict], asker: int, context: str = CONTEXT,
                 turns: list[Turn] | None = None, limit: bool = False) -> tuple[Pick, Pick, JevResponse]:
    """One Jev request for the players that the manager gives and the players that the manager gets, over the real
    rosters of `teams`, as the teams route gives them. `context` says what the manager asks for: a trade check by
    default, or trade ideas. The earlier `turns` of the Thread go in the state, so a follow-up reads like the whole
    question. With `limit`, the same request asks the questions of the limit of trade ideas, for `read_limit`. A failed
    request raises JevError."""
    team_of = {player["player_id"]: team for team in teams for player in team["players"]}
    mine = next(team for team in teams if team["roster_id"] == asker)
    others = [team for team in teams if team["roster_id"] != asker]

    def line(player: dict, team: str | None = None) -> str:
        return player_line(player["name"], player["position"], player["nfl_team"], team)

    gives = {player["player_id"]: line(player) for player in mine["players"]}
    gets = {player["player_id"]: line(player, team["team"]) for team in others for player in team["players"]}
    give_keys = option_keys({pid: _name(team_of[pid], pid) for pid in gives})
    get_keys = option_keys({pid: _name(team_of[pid], pid) for pid in gets})
    state = with_turns(pick_state(question, mine["team"], list(gives.values()),
                                  {team["team"]: [line(player) for player in team["players"]] for team in others},
                                  context), turns or [])
    give_options = {give_keys[pid]: text for pid, text in gives.items()}
    questions = pick_questions(give_options, {get_keys[pid]: text for pid, text in gets.items()})
    if limit:
        questions |= limit_questions(give_options)
    answers = jev.ask(state, questions)

    def side(named: str, choice: str, keys: dict[str, str], also: Pick | None = None) -> Pick:
        key, probability = _top(answers.choices[choice])
        pid = next(pid for pid, option in keys.items() if option == key)
        return Pick(named=answers.nouls[named], player_id=pid, name=_name(team_of[pid], pid), probability=probability,
                    roster_id=team_of[pid]["roster_id"], also=also)

    def second(named: str, choice: str, keys: dict[str, str]) -> Pick | None:
        return side(named, choice, keys) if answers.nouls[named] > YES else None

    gives = side(GIVES_NAMED, GIVES_PLAYER, give_keys, second(GIVES_ALSO_NAMED, GIVES_ALSO_PLAYER, give_keys))
    gets = side(GETS_NAMED, GETS_PLAYER, get_keys, second(GETS_ALSO_NAMED, GETS_ALSO_PLAYER, get_keys))
    return gives, gets, answers


@dataclass(frozen=True)
class ReadLimit:
    """The limit that one Jev request read from a question of trade ideas, and the name of each kept player for the
    step line."""

    limit: Limit
    kept_names: list[str]

    @property
    def empty(self) -> bool:
        return not (self.limit.keep_positions or self.limit.keep_players or self.limit.aim_position)


def read_limit(answers: JevResponse, teams: list[dict], asker: int) -> ReadLimit:
    """The limit of trade ideas from the answers of a pick request with `limit`. Each part needs a sure yes, as a pick
    does: a position Noul above YES keeps that position, and a Noul and its Choice above YES keep a player or aim at a
    position. An unsure part sets nothing, so the search runs as a tap does."""
    mine = next(team for team in teams if team["roster_id"] == asker)
    names = {player["player_id"]: player["name"] for player in mine["players"]}
    keep_positions = [position for position, key in KEEPS_POSITION.items() if answers.nouls[key] > YES]
    kept: list[str] = []
    key, probability = _top(answers.choices[KEPT_PLAYER])
    if answers.nouls[KEEPS_NAMED] > YES and probability > YES:
        kept = [pid for pid, option in option_keys(names).items() if option == key]
    aim, probability = _top(answers.choices[AIM_POSITION])
    aim_position = aim if answers.nouls[AIMS_POSITION] > YES and probability > YES else None
    return ReadLimit(limit=Limit(keep_positions=keep_positions, keep_players=kept, aim_position=aim_position),
                     kept_names=[names[pid] for pid in kept])


def limit_lines(read: ReadLimit) -> list[str]:
    """The plain step lines of a limit: one per kept position or player, and one for the position to get."""
    lines = [f"Left out each offer that sends away a {position}" for position in read.limit.keep_positions]
    lines += [f"Left out each offer that sends away {name}" for name in read.kept_names]
    if read.limit.aim_position is not None:
        lines.append(f"Looked only for offers that bring back a {read.limit.aim_position}")
    return lines


def ideas_anchor(gives: Pick, gets: Pick) -> tuple[Anchor, Pick] | None:
    """The anchor of trade ideas from the two picks of one Jev request, and the pick of the anchor.

    Exactly one sure side names the player and the direction. Two sure sides or none name no one player, so the
    ideas aim at the weakest slot, as a tap does.
    """
    if gives.sure and not gets.sure:
        return Anchor(player_id=gives.player_id, side="gives"), gives
    if gets.sure and not gives.sure:
        return Anchor(player_id=gets.player_id, side="gets"), gets
    return None


def _names(names: list[str]) -> str:
    """The names as one phrase, such as "A and B" or "A, B, and C"."""
    if len(names) <= 2:
        return " and ".join(names)
    return f"{', '.join(names[:-1])}, and {names[-1]}"


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


def capped_press(asker: Asker, roster_id: int, emit: Emit, press: Callable[[], dict]) -> dict | None:
    """Run one press of the Advisor under the caps: the Answer, or None after the cap part when a cap stops it.

    The press meter adds up each Claude call, so the league pays what the press cost, even when it fails. Only a press
    with a Claude call counts as an Answer of the team, because a cached repeat is a kept Answer and costs nothing.
    """
    hit = asker.caps.check(roster_id, asker.clock())
    if hit is not None:
        logger.info("A trade Topic stopped at the %s cap, with no Claude call", hit.cap)
        emit("data-cap", {"cap": hit.cap, "line": hit.line})
        return None
    answered = False
    with metered_press() as meter:
        try:
            document = press()
            answered = True
            return document
        finally:
            if meter.calls:
                asker.caps.record(roster_id, meter.usd, asker.clock(), counts=answered)


def _step(emit: Emit) -> Stage:
    """The stage callback of a stream: each line goes out as a step part, with whether it is a live line."""

    def step(line: str, *, live: bool = False) -> None:
        emit("data-step", {"line": line, "live": live})

    return step


def _teams(asker: ClientAsker, served: analyzer_routes.Served, roster_id: int) -> list[dict]:
    """The teams of the league from the cached teams route. A roster that is not in the league is 422, before the
    stream starts."""
    teams = analyzer_routes.teams(asker.season, served)["teams"]
    if roster_id not in {team["roster_id"] for team in teams}:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    return teams


def _points(asker: Asker, served: analyzer_routes.Served) -> dict[str, float]:
    """The projected points of each player for the rest of the season, for the bars of the trade card. The live
    snapshot holds the projections ahead, and a repeat in the window of their cache fetches none."""
    return rest_points(served.sources.snapshot(asker.season))


class TradeCheckRequest(BaseModel):
    """The body of the trade check: the question as the manager typed it, and the roster id of Your team."""

    question: str = Field(min_length=1, max_length=QUESTION_MAX)
    roster_id: int


@router.post("/trade-check")
def trade_check(request: Request, body: TradeCheckRequest, asker: ClientAsker,
                served: ServedClient) -> StreamingResponse:
    """The trade check of a typed question. With two sure picks, the steps of the analyze press and its document. A
    side with a sure second player gives or gets both. With an unsure pick, the form of the Trade page with each sure
    player and no unsure one (AT-58)."""
    teams = _teams(asker, served, body.roster_id)
    question = body.question.strip()

    def work(emit: Emit) -> None:
        gives, gets, answers = pick_players(asker.jev, question, teams, body.roster_id)
        emit("data-picks", {"model": answers.model, "gives": {**asdict(gives), "sure": gives.sure},
                            "gets": {**asdict(gets), "sure": gets.sure}})
        if not (gives.sure and gets.sure):
            emit("data-answer", {"kind": "form", "form": {
                "asker": body.roster_id, "partner": gets.roster_id if gets.sure else None,
                "gives": [pick.player_id for pick in gives.players] if gives.sure else [],
                "gets": [pick.player_id for pick in gets.players] if gets.sure else []}})
            return
        step = _step(emit)
        step(f"Found {_names([pick.name for pick in gives.players + gets.players])}")
        trade = ProposedTrade(season=asker.season, asker=body.roster_id, sides=[
            TradeSide(roster_id=body.roster_id,
                      gives=[GivenPlayer(player_id=pick.player_id, to=gets.roster_id) for pick in gives.players]),
            TradeSide(roster_id=gets.roster_id,
                      gives=[GivenPlayer(player_id=pick.player_id, to=body.roster_id) for pick in gets.players])])
        document = capped_press(asker, body.roster_id, emit,
                                lambda: analyzer_routes.analyze_trade(request, trade, served, step))
        if document is not None:
            _send_key(asker, served, emit, "trade_check", body.roster_id, gets.roster_id)
            emit("data-answer", {"kind": "check", "document": document,
                                 "block": check_block(document, _points(asker, served))})

    return stream(work)


class TradeIdeasRequest(BaseModel):
    """The body of trade ideas: the roster id of Your team, the partner roster that a typed question names, the typed
    question, and the earlier turns of the Thread, oldest first. A tap of the Suggestion sends no question."""

    roster_id: int
    partner: int | None = None
    question: str | None = Field(default=None, min_length=1, max_length=QUESTION_MAX)
    turns: Turns = Field(default_factory=list)


@router.post("/trade-ideas")
def trade_ideas(request: Request, body: TradeIdeasRequest, asker: ClientAsker,
                served: ServedClient) -> StreamingResponse:
    """Trade ideas for Your team: the steps of the find press and its document. It runs in each client, whatever the
    `finder` flag of the analyzer page says (spec, "The judgment Topics").

    A typed question goes first to one Jev pick of the player it names. With a sure pick, each offer holds him on his
    side, and a player that the manager gets makes his team the partner. An unsure pick says so in a step line, and
    the search aims at the weakest slot, as a tap does. The same request reads the limit of the question with the turns
    of the Thread, such as "not a WR" after earlier trade ideas, and no offer breaks it.
    """
    teams = _teams(asker, served, body.roster_id)

    def work(emit: Emit) -> None:
        step = _step(emit)
        anchor, partner, limit = None, body.partner, None
        if body.question is not None:
            gives, gets, answers = pick_players(asker.jev, body.question.strip(), teams, body.roster_id, IDEAS_CONTEXT,
                                                body.turns, limit=True)
            emit("data-picks", {"model": answers.model, "gives": {**asdict(gives), "sure": gives.sure},
                                "gets": {**asdict(gets), "sure": gets.sure}})
            read = read_limit(answers, teams, body.roster_id)
            emit("data-limit", read.limit.model_dump())
            picked = ideas_anchor(gives, gets)
            # The manager's keep wins over a give pick of the same player, because "keep Walker" names him too.
            if picked is not None and picked[0].side == "gives" and picked[0].player_id in read.limit.keep_players:
                picked = None
            if not read.empty:
                limit = read.limit
            if picked is None and limit is None:
                step(NO_ONE_PLAYER)
            if picked is not None:
                anchor, pick = picked
                step(f"Found {pick.name}")
                if anchor.side == "gets":
                    partner = pick.roster_id
            for line in [] if limit is None else limit_lines(read):
                step(line)
        pair = FindRequest(season=asker.season, asker=body.roster_id, partner=partner, anchor=anchor, limit=limit)
        document = capped_press(asker, body.roster_id, emit,
                                lambda: analyzer_routes.find_trades(request, pair, served, step))
        if document is not None:
            _send_key(asker, served, emit, "trade_ideas", body.roster_id, partner)
            emit("data-answer", {"kind": "ideas", "document": document,
                                 "block": ideas_block(document, _points(asker, served))})

    return stream(work)


class SellHighRequest(BaseModel):
    """The body of sell high: the roster id of Your team."""

    roster_id: int


@router.post("/sell-high")
def sell_high(request: Request, body: SellHighRequest, asker: ClientAsker, served: ServedClient) -> StreamingResponse:
    """Sell high or buy low for Your team: the steps of the sell high press, its sell list, and its document. The
    Advisor picks the players of the roster to sell from their facts side by side, and writes why."""
    _teams(asker, served, body.roster_id)

    def work(emit: Emit) -> None:
        document = capped_press(asker, body.roster_id, emit,
                                lambda: analyzer_routes.sell_high_press(request, asker.season, body.roster_id, served,
                                                                        _step(emit)))
        if document is not None:
            _send_key(asker, served, emit, "sell_high", body.roster_id, None)
            emit("data-block", sell_list(document))
            emit("data-answer", {"kind": "sell", "document": document})

    return stream(work)
