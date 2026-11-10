"""
The free answer of the ask box: Claude Sonnet 5.5 reads this season's data with at most 4 tool calls, the text streams
through VercelAIAdapter to useChat, and Jev checks each sentence against the tool results after the last word.
"""
import logging
import threading
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Annotated, Any

import anyio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.capabilities import Caching
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from pydantic_ai.ui.vercel_ai.request_types import SubmitMessage, TextUIPart, UIMessage
from pydantic_ai.ui.vercel_ai.response_types import (
    BaseChunk,
    DataChunk,
    DoneChunk,
    ErrorChunk,
    FinishChunk,
    MessageMetadataChunk,
    StartChunk,
    TextDeltaChunk,
)

from cornerstone_api import free_tools
from cornerstone_api.ask import QUESTION_MAX, WEEK_MAX, YES, Asker, ClientAsker, Route, route_question
from cornerstone_api.caps import sonnet_cost
from cornerstone_api.free_wording import (
    INSTRUCTIONS,
    check_questions,
    check_state,
    rewrite_prompt,
    run_instructions,
    sentence_key,
    sentences,
)
from league.jev_port import Jev, JevError
from league.live import fetch_live_week
from league.paths import history_root

logger = logging.getLogger(__name__)

router = APIRouter()

# Every Claude answer of the front door uses Sonnet 5.5. A free answer runs at low effort (decision 04 and the spec).
MODEL = "anthropic:claude-sonnet-5-5"
EFFORT = "low"
# The hard cap of the spec. It holds an answer to about 10 to 20 s and under about $0.15 (decision 12).
TOOL_CALLS_MAX = 4
# A short answer needs few tokens, but a cut answer is worse than a long one, so the cap leaves room for the thinking.
MAX_TOKENS = 16000
# The tool result past the cap. Claude then answers with what it found.
LIMIT_RESULT = {"error": f"The limit of {TOOL_CALLS_MAX} tool calls is used up. Answer with what you found, and say "
                         "what you could not find."}
# The error line of a stream that stops. The site shows its own retry line, so this text is for the log of the browser.
STREAM_ERROR = "The answer did not go through. Ask again."
SDK_VERSION = 7


@dataclass
class FreeDeps:
    """What the tools of one answer read, the count of their calls, and each result by the name of its call."""

    data: free_tools.SeasonData
    calls: int = 0
    results: dict[str, Any] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


AGENT = Agent(
    MODEL,
    name="free_answer",
    deps_type=FreeDeps,
    instructions=INSTRUCTIONS,
    model_settings=AnthropicModelSettings(anthropic_effort=EFFORT, max_tokens=MAX_TOKENS),
    capabilities=[Caching()],
    defer_model_check=True,
)


def _call(ctx: RunContext[FreeDeps], name: str, read: Callable[[], dict]) -> dict:
    """One tool call under the cap. Past the cap, the call reads nothing and says so."""
    with ctx.deps.lock:
        if ctx.deps.calls >= TOOL_CALLS_MAX:
            return LIMIT_RESULT
        ctx.deps.calls += 1
    result = read()
    with ctx.deps.lock:
        ctx.deps.results[name] = result
    return result


@AGENT.tool
def standings(ctx: RunContext[FreeDeps]) -> dict:
    """The standings of the league: each team's record, head-to-head record, points for, and points against."""
    return _call(ctx, "standings", lambda: free_tools.standings(ctx.deps.data))


@AGENT.tool
def week_results(ctx: RunContext[FreeDeps], week: int) -> dict:
    """The score of each game of one fantasy week, its winner, the median score, and the high and low scores."""
    return _call(ctx, f"week_results_week_{week}", lambda: free_tools.week_results(ctx.deps.data, week))


@AGENT.tool
def week_moves(ctx: RunContext[FreeDeps], week: int) -> dict:
    """The trades, the waiver claims with their FAAB bids, the free agent adds, and the drops of one fantasy week."""
    return _call(ctx, f"week_moves_week_{week}", lambda: free_tools.week_moves(ctx.deps.data, week))


@AGENT.tool
def season_moves(ctx: RunContext[FreeDeps]) -> dict:
    """The trades, the waiver claims with their FAAB bids, the free agent adds, and the drops of every week so far."""
    return _call(ctx, "season_moves", lambda: free_tools.season_moves(ctx.deps.data))


@AGENT.tool
def team_roster(ctx: RunContext[FreeDeps], team: str) -> dict:
    """The players on one team of the league now, with each player's fantasy points this season."""
    return _call(ctx, f"team_roster_{team}", lambda: free_tools.team_roster(ctx.deps.data, team))


@AGENT.tool
def player_log(ctx: RunContext[FreeDeps], player: str) -> dict:
    """The game log of one NFL player this season: fantasy points and main stats each week, and the league team that
    held him."""
    return _call(ctx, f"player_log_{player}", lambda: free_tools.player_log(ctx.deps.data, player))


class FreeRequest(BaseModel):
    """The body of a free answer, as the route of the ask box. useChat adds its own fields, such as the messages, and
    the route reads none of them, so a client never writes the prompt of Claude."""

    model_config = ConfigDict(extra="ignore")

    question: str = Field(min_length=1, max_length=QUESTION_MAX)
    roster_id: int
    week: int = Field(ge=1, le=WEEK_MAX)


def _served(request: Request) -> Any:
    return request.app.state.served[request.path_params["slug"]]


Served = Annotated[Any, Depends(_served)]


@dataclass
class _Attempt:
    """One run of Claude: the text that the manager saw, the messages of the run, and its usage."""

    text: str = ""
    messages: list[ModelMessage] = field(default_factory=list)
    errored: bool = False
    result: AgentRunResult | None = None


def _adapter(prompt: str, message_id: str = "ask") -> VercelAIAdapter[FreeDeps, str]:
    """The adapter of one run. Its one user message is the prompt from code, never a message from the client.

    Each run gives its message its own id, so the adapter never reads the rewrite as a repeat of the question.
    """
    message = UIMessage(id=message_id, role="user", parts=[TextUIPart(text=prompt)])
    run_input = SubmitMessage(id="free", messages=[message])
    return VercelAIAdapter(agent=AGENT, run_input=run_input, sdk_version=SDK_VERSION)


# The adapter frames each run with its own start, finish, and done. The free answer has one frame for all its runs.
_FRAME = (StartChunk, FinishChunk, DoneChunk, MessageMetadataChunk)


async def _run(prompt: str, deps: FreeDeps, instructions: str, history: list[ModelMessage], attempt: _Attempt,
               model: Model | None) -> AsyncIterator[BaseChunk]:
    """The chunks of one run, with the frame chunks left out. It keeps the text that streamed in `attempt`."""

    async def keep(result: AgentRunResult) -> None:
        attempt.result = result
        attempt.messages = result.all_messages()

    texts: list[str] = []
    async for chunk in _adapter(prompt, f"ask-{len(history)}").run_stream(deps=deps, instructions=instructions, message_history=history,
                                                   model=model, on_complete=keep):
        if isinstance(chunk, _FRAME):
            continue
        if isinstance(chunk, TextDeltaChunk):
            texts.append(chunk.delta)
        if isinstance(chunk, ErrorChunk):
            attempt.errored = True
        yield chunk
    attempt.text = "".join(texts)


def check(jev: Jev, question: str, your_team: str, text: str, results: dict[str, Any]) -> list[str]:
    """The sentences of `text` that Jev does not read as following from `results`. Raises JevError when the call fails.

    A sentence passes only above the yes cutoff, so an unsure sentence gets the rewrite and the manager never reads a
    number that the data does not hold.
    """
    parts = sentences(text)
    if not parts:
        return []
    answers = jev.ask(check_state(question, your_team, parts, results), check_questions(parts))
    return [part for i, part in enumerate(parts) if answers.nouls[sentence_key(i)] <= YES]


def _data(kind: str, data: dict, id: str | None = None) -> DataChunk:
    return DataChunk(type=f"data-{kind}", id=id, data=data)


def _usage_line(attempts: list[_Attempt], deps: FreeDeps, outcome: str) -> str:
    usages = [a.result.usage for a in attempts if a.result is not None]
    tokens_in = sum(u.input_tokens for u in usages)
    tokens_out = sum(u.output_tokens for u in usages)
    costs = [u.cost for u in usages if u.cost is not None]
    cost = f"${float(sum(costs)):.4f}" if len(costs) == len(usages) and usages else "unknown"
    return (f"The free answer ended as {outcome}, with {deps.calls} tool calls, {len(attempts)} texts, "
            f"{tokens_in} input tokens, {tokens_out} output tokens, and a cost of {cost}")


async def answer_stream(asker: Asker, route: Route, question: str, roster_id: int, deps: FreeDeps,
                        instructions: str, model: Model | None = None) -> AsyncIterator[BaseChunk]:
    """The whole stream of one free answer: the first text with its steps, the check, at most one rewrite, and the
    Suggestion of a half fit or the honest miss of a second failed check.

    The Suggestion names the roster of the team that the question names, or None for Your team. A test gives `model`,
    and the real app gives None, so the run takes the model of the agent.
    """
    named = next((rid for rid, name in deps.data.teams.items() if name == route.team), None)
    yield StartChunk()
    attempts: list[_Attempt] = []
    history: list[ModelMessage] = []
    prompt = question
    outcome = "an error"
    for number in (1, 2):
        attempt = _Attempt()
        attempts.append(attempt)
        if number == 2:
            # The site fades the first text out at this part, and the second text streams under "Fixing a number…".
            yield _data("check", {"state": "fixing"}, id="check")
            yield _data("fix", {})
        async for chunk in _run(prompt, deps, instructions, history, attempt, model):
            yield chunk
        if attempt.errored:
            break
        yield _data("check", {"state": "checking"}, id="check")
        try:
            failed = await anyio.to_thread.run_sync(check, asker.jev, question, deps.data.teams[roster_id], attempt.text,
                                                    deps.results)
        except JevError as error:
            # A failed Jev call is an error, never a "no" and never a pass.
            logger.warning("The Jev check of a free answer failed (%s)", type(error).__name__)
            yield ErrorChunk(error_text=STREAM_ERROR)
            break
        if not failed:
            outcome = "checked"
            yield _data("check", {"state": "checked"}, id="check")
            if route.suggestion is not None:
                yield _data("suggestion", {"topic": route.suggestion, "team": named})
            break
        if number == 2:
            outcome = "an honest miss"
            yield _data("check", {"state": "failed"}, id="check")
            yield _data("miss", {"closest": route.closest})
            await anyio.to_thread.run_sync(asker.misses.write, question, roster_id, deps.data.teams[roster_id],
                                           route.closest, asker.clock())
            break
        history = attempt.messages
        prompt = rewrite_prompt(failed)
    logger.info(_usage_line(attempts, deps, outcome))
    # Each run costs the league, whatever its end. Only a checked answer counts as an Answer of the team, because an
    # honest miss and an error do not count toward the team cap.
    usd = sum(sonnet_cost(a.result.usage) for a in attempts if a.result is not None)
    await anyio.to_thread.run_sync(lambda: asker.caps.record(roster_id, usd, asker.clock(), counts=outcome == "checked"))
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
async def free(body: FreeRequest, asker: ClientAsker, served: Served, request: Request) -> StreamingResponse:
    """The stream of one free answer. The route runs again first, so only a question that Jev routes to a free answer
    reaches Claude, whatever the client sends."""
    rosters = await anyio.to_thread.run_sync(asker.rosters)
    if body.roster_id not in rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    question = body.question.strip()
    try:
        route = await anyio.to_thread.run_sync(route_question, asker.jev, question, list(rosters.values()),
                                               asker.season, body.week)
    except JevError as error:
        logger.warning("The route of a free answer failed (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None
    if route.kind != "free":
        raise HTTPException(status_code=409, detail="This question has no free answer. Ask again.")
    hit = await anyio.to_thread.run_sync(asker.caps.check, body.roster_id, asker.clock())
    if hit is not None:
        # The ask route gives the cap line first, so only a client that skips it gets here. It makes no Claude call.
        logger.info("A free answer stopped at the %s cap, with no Claude call", hit.cap)
        raise HTTPException(status_code=429, detail={"cap": hit.cap, "line": hit.line})
    deps = FreeDeps(data=season_data(served, asker.season, body.week, rosters))
    instructions = run_instructions(asker.season, body.week, rosters[body.roster_id], route.team)
    adapter = _adapter(question)
    return adapter.streaming_response(answer_stream(asker, route, question, body.roster_id, deps, instructions,
                                                    request.app.state.free_model))
