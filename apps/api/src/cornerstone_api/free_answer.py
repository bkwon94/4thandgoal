"""
The free answer of the ask box: Claude Sonnet 5.5 reads this season's data with at most 4 tool calls, the text streams
through VercelAIAdapter to useChat, and Jev checks each sentence against the tool results after the last word.
"""
import hashlib
import json
import logging
import threading
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import anyio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Caching
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.ui.vercel_ai.response_types import BaseChunk, DoneChunk, FinishChunk, StartChunk

from analyzer.routes import ServedClient
from cornerstone_api import free_tools
from cornerstone_api.answer_store import AnswerStore
from cornerstone_api.ask import QUESTION_MAX, WEEK_MAX, Asker, ClientAsker, Route
from cornerstone_api.claude_stream import Checker, Outcome, Writer, adapter, checked_answer, data, kept_text
from cornerstone_api.free_wording import INSTRUCTIONS, rewrite_prompt, run_instructions
from facts.writer import route_model
from league.live import fetch_live_week
from league.paths import history_root

logger = logging.getLogger(__name__)

router = APIRouter()

# The route table maps the free answer to its model and its effort (decision 04 and the spec).
ROUTE = route_model("free_answer")
# The hard cap of the spec. It holds an answer to about 10 to 20 s and under about $0.15 (decision 12).
TOOL_CALLS_MAX = 4
# A short answer needs few tokens, but a cut answer is worse than a long one, so the cap leaves room for the thinking.
MAX_TOKENS = 16000
# The tool result past the cap. Claude then answers with what it found.
LIMIT_RESULT = {"error": f"The limit of {TOOL_CALLS_MAX} tool calls is used up. Answer with what you found, and say "
                         "what you could not find."}
# The read of each tool by its name, so a repeat question reads the same data again for the key of its kept answer.
READERS: dict[str, Callable[..., dict]] = {
    "standings": free_tools.standings,
    "week_results": free_tools.week_results,
    "week_moves": free_tools.week_moves,
    "season_moves": free_tools.season_moves,
    "team_roster": free_tools.team_roster,
    "player_log": free_tools.player_log,
}
# The topic of the two rows of a kept free answer in the AnswerStore: the reads of the question, and the answer.
READS_TOPIC = "free_reads"
ANSWER_TOPIC = "free"


@dataclass
class FreeDeps:
    """What the tools of one answer read, the count of their calls, each result by the name of its call, and the tool
    and the arguments of each call by the same name."""

    data: free_tools.SeasonData
    calls: int = 0
    results: dict[str, Any] = field(default_factory=dict)
    reads: dict[str, tuple[str, dict]] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


AGENT = Agent(
    f"anthropic:{ROUTE.model}",
    name="free_answer",
    deps_type=FreeDeps,
    instructions=INSTRUCTIONS,
    model_settings=AnthropicModelSettings(anthropic_effort=ROUTE.effort, max_tokens=MAX_TOKENS),
    capabilities=[Caching()],
    defer_model_check=True,
)


def _call(ctx: RunContext[FreeDeps], name: str, tool: str, **args: Any) -> dict:
    """One tool call under the cap. Past the cap, the call reads nothing and says so."""
    with ctx.deps.lock:
        if ctx.deps.calls >= TOOL_CALLS_MAX:
            return LIMIT_RESULT
        ctx.deps.calls += 1
    result = READERS[tool](ctx.deps.data, **args)
    with ctx.deps.lock:
        ctx.deps.results[name] = result
        ctx.deps.reads[name] = (tool, args)
    return result


@AGENT.tool
def standings(ctx: RunContext[FreeDeps]) -> dict:
    """The standings of the league: each team's record, head-to-head record, points for, and points against."""
    return _call(ctx, "standings", "standings")


@AGENT.tool
def week_results(ctx: RunContext[FreeDeps], week: int) -> dict:
    """The score of each game of one fantasy week, its winner, the median score, and the high and low scores."""
    return _call(ctx, f"week_results_week_{week}", "week_results", week=week)


@AGENT.tool
def week_moves(ctx: RunContext[FreeDeps], week: int) -> dict:
    """The trades, the waiver claims with their FAAB bids, the free agent adds, and the drops of one fantasy week."""
    return _call(ctx, f"week_moves_week_{week}", "week_moves", week=week)


@AGENT.tool
def season_moves(ctx: RunContext[FreeDeps]) -> dict:
    """The trades, the waiver claims with their FAAB bids, the free agent adds, and the drops of every week so far."""
    return _call(ctx, "season_moves", "season_moves")


@AGENT.tool
def team_roster(ctx: RunContext[FreeDeps], team: str) -> dict:
    """The players on one team of the league now, with each player's fantasy points this season."""
    return _call(ctx, f"team_roster_{team}", "team_roster", team=team)


@AGENT.tool
def player_log(ctx: RunContext[FreeDeps], player: str) -> dict:
    """The game log of one NFL player this season: fantasy points and main stats each week, and the league team that
    held him."""
    return _call(ctx, f"player_log_{player}", "player_log", player=player)


class FreeRequest(BaseModel):
    """The body of a free answer, as the route of the ask box. useChat adds its own fields, such as the messages, and
    the route reads none of them, so a client never writes the prompt of Claude."""

    model_config = ConfigDict(extra="ignore")

    question: str = Field(min_length=1, max_length=QUESTION_MAX)
    roster_id: int
    week: int = Field(ge=1, le=WEEK_MAX)


def question_key(question: str, instructions: str) -> str:
    """The key of the reads of a question: its text, the run instructions with Your team, the week, and the team that
    the question names, and the wording and the model that answer it."""
    body = {"question": question, "run": instructions, "instructions": INSTRUCTIONS, "model": ROUTE.model,
            "effort": ROUTE.effort}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def answer_key(base: str, results: dict[str, Any]) -> str:
    """The key of a free answer: the key of its question plus the data it read (decision 11). A new week, a trade, or a
    waiver claim changes a tool result, so the key changes and Claude writes a fresh answer."""
    body = {"question": base, "results": results}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()


def keep(store: AnswerStore, base: str, roster_id: int, deps: FreeDeps, text: str, now: datetime) -> None:
    """Keep a checked free answer: the reads of its question, and its text under the key of the data it read."""
    reads = [[name, tool, args] for name, (tool, args) in deps.reads.items()]
    store.put(base, READS_TOPIC, roster_id, {"reads": reads}, now)
    store.put(answer_key(base, deps.results), ANSWER_TOPIC, roster_id, {"text": text}, now)


def kept_answer(store: AnswerStore, base: str, data: free_tools.SeasonData) -> dict | None:
    """The kept answer of a repeat question, or None. The reads of the last checked answer run again on the data now,
    so the key holds only while each result is the same. The tools read code and saved data, with no Claude call."""
    reads = store.get(base)
    if reads is None:
        return None
    results = {name: READERS[tool](data, **args) for name, tool, args in reads["reads"]}
    return store.get(answer_key(base, results))


async def kept_stream(route: Route, teams: dict[int, str], text: str) -> AsyncIterator[BaseChunk]:
    """The whole stream of a kept free answer: its text at once with its check, and the Suggestion of a half fit."""
    named = next((rid for rid, name in teams.items() if name == route.team), None)
    yield StartChunk()
    async for chunk in kept_text(text):
        yield chunk
    if route.suggestion is not None:
        yield data("suggestion", {"topic": route.suggestion, "team": named})
    yield FinishChunk(finish_reason="stop")
    yield DoneChunk()


async def answer_stream(asker: Asker, route: Route, question: str, roster_id: int, deps: FreeDeps,
                        instructions: str, model: Model | None = None,
                        store: AnswerStore | None = None) -> AsyncIterator[BaseChunk]:
    """The whole stream of one free answer: the first text with its steps, the check, at most one rewrite, and the
    Suggestion of a half fit or the honest miss of a second failed check.

    The Suggestion names the roster of the team that the question names, or None for Your team. A test gives `model`,
    and the real app gives None, so the run takes the model of the agent. A checked answer goes to `store`.
    """
    named = next((rid for rid, name in deps.data.teams.items() if name == route.team), None)
    your_team = deps.data.teams[roster_id]
    writer = Writer(label="free answer", agent=AGENT, prompt=question, deps=deps, instructions=instructions,
                    model=model, rewrite=rewrite_prompt, tool_calls=lambda: deps.calls)
    checker = Checker(question=question, your_team=your_team, results=deps.results, closest=route.closest)
    outcome = Outcome()
    yield StartChunk()
    async for chunk in checked_answer(asker, writer, checker, roster_id, outcome):
        yield chunk
    if outcome.end == "checked" and store is not None:
        await anyio.to_thread.run_sync(keep, store, question_key(question, instructions), roster_id, deps,
                                       outcome.text, asker.clock())
    if outcome.end == "checked" and route.suggestion is not None:
        yield data("suggestion", {"topic": route.suggestion, "team": named})
    if outcome.end == "an honest miss":
        await anyio.to_thread.run_sync(asker.misses.write, question, roster_id, your_team, route.closest, asker.clock())
    yield FinishChunk(finish_reason="stop")
    yield DoneChunk()


def season_data(served: Any, season: int, week: int, teams: dict[int, str]) -> free_tools.SeasonData:
    """The data of one answer for the client of `served`: the saved weeks 1 to `week`, and the live Sleeper fetch."""
    client = served.client

    def fetch_raw():
        raw, _, _ = fetch_live_week(season, client, served.sources.fetch_sleeper)
        return raw

    return free_tools.SeasonData(season=season, week=week, teams=teams,
                                 history_root=history_root(client.folder, season),
                                 points_key=client.settings.points_key, median_game=client.settings.median_game,
                                 fetch_raw=fetch_raw)


@router.post("/ask/free")
async def free(body: FreeRequest, asker: ClientAsker, served: ServedClient,
               request: Request) -> StreamingResponse:
    """The stream of one free answer. It reads the free route that the ask route gave for the same question, team, and
    week, so the question gets no second Jev request. A question with no kept free route gets 409 and no Claude call,
    so only a question that Jev routes to a free answer reaches Claude, whatever the client sends."""
    rosters = await anyio.to_thread.run_sync(asker.rosters)
    if body.roster_id not in rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    question = body.question.strip()
    route = asker.free_routes.get(body.roster_id, body.week, question)
    if route is None:
        logger.info("A free answer had no free route from the ask route, so it makes no Claude call")
        raise HTTPException(status_code=409, detail="This question has no free answer. Ask again.")
    deps = FreeDeps(data=season_data(served, asker.season, body.week, rosters))
    instructions = run_instructions(asker.season, body.week, rosters[body.roster_id], route.team)
    store: AnswerStore = request.app.state.kept[request.path_params["slug"]]
    # A kept answer costs nothing, so it comes back before the caps, as a kept personal Answer does.
    kept = await anyio.to_thread.run_sync(kept_answer, store, question_key(question, instructions), deps.data)
    if kept is not None:
        logger.info("A free answer came from the store, with no Claude call")
        return adapter(AGENT, question).streaming_response(kept_stream(route, rosters, kept["text"]))
    hit = await anyio.to_thread.run_sync(asker.caps.check, body.roster_id, asker.clock())
    if hit is not None:
        # The ask route gives the cap line first, so only a client that skips it gets here. It makes no Claude call.
        logger.info("A free answer stopped at the %s cap, with no Claude call", hit.cap)
        raise HTTPException(status_code=429, detail={"cap": hit.cap, "line": hit.line})
    stream = answer_stream(asker, route, question, body.roster_id, deps, instructions, request.app.state.free_model,
                           store)
    return adapter(AGENT, question).streaming_response(stream)
