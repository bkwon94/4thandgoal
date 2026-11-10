"""
The personal Topics of the front door, live on the API: weak spots, how you stack up, and waiver targets. Each streams
its data block from code first, then the text of Claude over its slice, then the Jev check. A kept Answer comes back free.
"""
import hashlib
import json
import logging
from collections.abc import AsyncIterator
from typing import Annotated, Any

import anyio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.capabilities import Caching
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.ui.vercel_ai.response_types import (
    BaseChunk,
    DoneChunk,
    ErrorChunk,
    FinishChunk,
    StartChunk,
    TextDeltaChunk,
    TextEndChunk,
    TextStartChunk,
)

from cornerstone_api.answer_store import AnswerStore
from cornerstone_api.ask import Asker, ClientAsker
from cornerstone_api.caps import CapHit, sonnet_cost
from cornerstone_api.free_answer import MODEL, STREAM_ERROR, _adapter, _Attempt, _data, _run, check
from cornerstone_api.personal_facts import (
    PersonalFacts,
    PersonalTopic,
    live_grades,
    published_waiver,
    topic_facts,
)
from cornerstone_api.personal_wording import (
    INSTRUCTIONS,
    TOPIC_ASKS,
    check_question,
    rewrite_prompt,
    topic_prompt,
)
from league.jev_port import JevError

logger = logging.getLogger(__name__)

router = APIRouter()

# A personal Topic runs Sonnet 5.5 at medium effort (spec, "The Answers and the stream").
EFFORT = "medium"
# A short Answer needs few tokens, but a cut Answer is worse than a long one, so the cap leaves room for the thinking.
MAX_TOKENS = 16000
# The closest Topics of the honest miss of each personal Topic, after a second failed check.
CLOSEST: dict[str, list[str]] = {
    "weak_spots": ["stack_up", "waiver_targets", "trade_ideas"],
    "stack_up": ["weak_spots", "power_rankings", "your_season"],
    "waiver_targets": ["weak_spots", "stack_up", "trade_ideas"],
}

AGENT = Agent(
    MODEL,
    name="personal_topic",
    instructions=INSTRUCTIONS,
    model_settings=AnthropicModelSettings(anthropic_effort=EFFORT, max_tokens=MAX_TOKENS),
    capabilities=[Caching()],
    defer_model_check=True,
)


class PersonalRequest(BaseModel):
    """The body of a personal Topic: the Topic, the roster id of Your team, and the roster id of the team that the
    Answer is about, or None for Your team. useChat adds its own fields, and the route reads none of them."""

    model_config = ConfigDict(extra="ignore")

    topic: PersonalTopic
    roster_id: int
    team: int | None = None


def _served(request: Request) -> Any:
    return request.app.state.served[request.path_params["slug"]]


Served = Annotated[Any, Depends(_served)]


def answer_key(topic: str, own: bool, facts: PersonalFacts) -> str:
    """The key of an Answer: the facts it read, whom it addresses, and the wording and the model that wrote it. A waiver
    claim or a trade changes the facts, so the key changes and Claude writes a fresh Answer."""
    body = {"topic": topic, "own": own, "slice": facts.slice, "block": facts.block, "instructions": INSTRUCTIONS,
            "ask": TOPIC_ASKS[topic], "model": MODEL, "effort": EFFORT}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _usage_line(topic: str, attempts: list[_Attempt], outcome: str) -> str:
    usages = [a.result.usage for a in attempts if a.result is not None]
    costs = [u.cost for u in usages if u.cost is not None]
    cost = f"${float(sum(costs)):.4f}" if len(costs) == len(usages) and usages else "unknown"
    return (f"The personal Topic {topic} ended as {outcome}, with {len(attempts)} texts, "
            f"{sum(u.input_tokens for u in usages)} input tokens, {sum(u.output_tokens for u in usages)} output "
            f"tokens, and a cost of {cost}")


async def claude_answer(asker: Asker, store: AnswerStore, topic: str, facts: PersonalFacts, key: str, own: bool,
                        your_team: str, model: Model | None, roster_id: int | None) -> AsyncIterator[BaseChunk]:
    """The one place where a personal Answer calls Claude: the first text, the Jev check of each sentence against the
    slice, at most one rewrite, and the honest miss of a second failed check. A checked text goes to the store.

    A kept Answer never reaches this function, so a count of its calls is the count of the Claude Answers. The caller
    asks the caps first. After the runs, the cost goes to the league month. Only a checked Answer of `roster_id` counts
    toward the team cap. The head start gives None, so it counts toward the league cap only (decision 04).
    """
    team = facts.slice["team"]
    question = check_question(topic, team)
    results = {"team_facts": facts.slice}
    instructions = f"The facts are the league data now, before the games of week {facts.slice['week']}."
    attempts: list[_Attempt] = []
    history: list[ModelMessage] = []
    prompt = topic_prompt(topic, facts.slice, own)
    outcome = "an error"
    for number in (1, 2):
        attempt = _Attempt()
        attempts.append(attempt)
        if number == 2:
            # The site fades the first text out at this part, and the second text streams under "Fixing a number…".
            yield _data("check", {"state": "fixing"}, id="check")
            yield _data("fix", {})
        async for chunk in _run(prompt, None, instructions, history, attempt, model, AGENT):
            yield chunk
        if attempt.errored:
            break
        yield _data("check", {"state": "checking"}, id="check")
        try:
            failed = await anyio.to_thread.run_sync(check, asker.jev, question, your_team, attempt.text, results)
        except JevError as error:
            # A failed Jev call is an error, never a "no" and never a pass.
            logger.warning("The Jev check of a personal Topic failed (%s)", type(error).__name__)
            yield ErrorChunk(error_text=STREAM_ERROR)
            break
        if not failed:
            outcome = "checked"
            yield _data("check", {"state": "checked"}, id="check")
            await anyio.to_thread.run_sync(store.put, key, topic, facts.block["team"], {"text": attempt.text.strip()},
                                           asker.clock())
            break
        if number == 2:
            outcome = "an honest miss"
            yield _data("check", {"state": "failed"}, id="check")
            yield _data("miss", {"closest": CLOSEST[topic]})
            break
        history = attempt.messages
        prompt = rewrite_prompt(failed)
    logger.info(_usage_line(topic, attempts, outcome))
    # Each run costs the league, whatever its end. An honest miss and an error do not count toward the team cap.
    usd = sum(sonnet_cost(a.result.usage) for a in attempts if a.result is not None)
    counts = roster_id is not None and outcome == "checked"
    await anyio.to_thread.run_sync(lambda: asker.caps.record(roster_id, usd, asker.clock(), counts=counts))


async def _kept(answer: dict) -> AsyncIterator[BaseChunk]:
    """The text of a kept Answer at once, with its check, and no Claude call."""
    yield TextStartChunk(id="kept")
    yield TextDeltaChunk(id="kept", delta=answer["text"])
    yield TextEndChunk(id="kept")
    yield _data("check", {"state": "checked"}, id="check")


async def _capped(topic: str, hit: CapHit) -> AsyncIterator[BaseChunk]:
    """The calm line of a cap in place of the text, with the 3 closest Topics, and no Claude call."""
    yield _data("cap", {"cap": hit.cap, "line": hit.line, "closest": CLOSEST[topic]})


async def answer_stream(facts: PersonalFacts, key: str, text: AsyncIterator[BaseChunk]) -> AsyncIterator[BaseChunk]:
    """The whole stream of one personal Topic: the data block from code first, the key of the Answer, then the text."""
    yield StartChunk()
    yield _data("block", facts.block)
    yield _data("key", {"key": key})
    async for chunk in text:
        yield chunk
    yield FinishChunk(finish_reason="stop")
    yield DoneChunk()


@router.post("/personal")
async def personal(body: PersonalRequest, asker: ClientAsker, served: Served, request: Request) -> StreamingResponse:
    """The stream of one personal Topic for the team of the body. The facts come from the live snapshot, so the
    Answer follows each waiver claim and trade."""
    try:
        snapshot = await anyio.to_thread.run_sync(served.sources.snapshot, asker.season)
        grades, starters = await anyio.to_thread.run_sync(live_grades, snapshot)
    except ValueError as error:
        logger.warning("The facts of a personal Topic did not load (%s)", error)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None
    subject = body.roster_id if body.team is None else body.team
    if body.roster_id not in snapshot.rosters or subject not in snapshot.rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    board = (published_waiver(snapshot.client.folder, asker.season, snapshot.week)
             if body.topic == "waiver_targets" else None)
    facts = topic_facts(body.topic, snapshot, subject, grades, starters, board)
    own = subject == body.roster_id
    key = answer_key(body.topic, own, facts)
    store: AnswerStore = request.app.state.kept[request.path_params["slug"]]
    kept = await anyio.to_thread.run_sync(store.get, key)
    if kept is not None:
        logger.info("The personal Topic %s came from the store, with no Claude call", body.topic)
        text = _kept(kept)
    elif (hit := await anyio.to_thread.run_sync(asker.caps.check, body.roster_id, asker.clock())) is not None:
        # Past a cap, everything that costs nothing still works: the data block from code, and the cap line.
        logger.info("The personal Topic %s stopped at the %s cap, with no Claude call", body.topic, hit.cap)
        text = _capped(body.topic, hit)
    else:
        text = claude_answer(asker, store, body.topic, facts, key, own, snapshot.teams[body.roster_id].name,
                             request.app.state.personal_model, body.roster_id)
    return _adapter("", agent=AGENT).streaming_response(answer_stream(facts, key, text))
