"""
The personal Topics of the front door, live on the API: weak spots, how you stack up, and waiver targets. Each streams
its data block from code first, then the text of Claude over its slice, then the Jev check. A kept Answer comes back free.
"""
import hashlib
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import anyio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.capabilities import Caching
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.ui.vercel_ai.response_types import (
    BaseChunk,
    DoneChunk,
    FinishChunk,
    StartChunk,
    TextDeltaChunk,
    TextEndChunk,
    TextStartChunk,
)

from analyzer.routes import ServedClient
from cornerstone_api.answer_store import AnswerStore
from cornerstone_api.ask import Asker, ClientAsker
from cornerstone_api.caps import CapHit
from cornerstone_api.claude_stream import Checker, Outcome, Writer, adapter, checked_answer, data
from cornerstone_api.free_answer import MODEL
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
from league.snapshot import Snapshot
from managers.grade import ManagerGrade, Starter

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


def answer_key(topic: str, own: bool, facts: PersonalFacts, roster: list[str]) -> str:
    """The key of an Answer: the facts it read, the roster of its team, whom it addresses, and the wording and the
    model that wrote it. A waiver claim or a trade changes the roster, so the key changes and Claude writes a fresh
    Answer. The roster is in the key, because a bench add can leave the slice the same and still change the read."""
    body = {"topic": topic, "own": own, "slice": facts.slice, "block": facts.block, "roster": sorted(roster),
            "instructions": INSTRUCTIONS, "ask": TOPIC_ASKS[topic], "model": MODEL, "effort": EFFORT}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Live:
    """The live league of one request: the snapshot, and the roster grade and the starters of each roster now."""

    snapshot: Snapshot
    grades: dict[int, ManagerGrade]
    starters: dict[int, list[Starter]]

    def facts(self, topic: PersonalTopic, subject: int) -> PersonalFacts:
        """The facts of `topic` for the team of `subject`. Waiver targets read the published waiver list."""
        snapshot = self.snapshot
        board = (published_waiver(snapshot.client.folder, snapshot.season, snapshot.week)
                 if topic == "waiver_targets" else None)
        return topic_facts(topic, snapshot, subject, self.grades, self.starters, board)

    def key(self, topic: PersonalTopic, roster_id: int, subject: int) -> tuple[PersonalFacts, str]:
        """The facts and the key of the Answer of `topic` about `subject`, for the manager of `roster_id`."""
        facts = self.facts(topic, subject)
        return facts, answer_key(topic, subject == roster_id, facts, self.snapshot.rosters[subject])


async def load_live(served: Any, season: int) -> Live:
    """The live league for the client of `served`. Raises HTTPException 503 when the facts do not load."""
    try:
        snapshot = await anyio.to_thread.run_sync(served.sources.snapshot, season)
        grades, starters = await anyio.to_thread.run_sync(live_grades, snapshot)
    except ValueError as error:
        logger.warning("The facts of a personal Topic did not load (%s)", error)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None
    return Live(snapshot, grades, starters)


async def claude_answer(asker: Asker, store: AnswerStore, topic: str, facts: PersonalFacts, key: str, own: bool,
                        your_team: str, model: Model | None, roster_id: int | None) -> AsyncIterator[BaseChunk]:
    """The one place where a personal Answer calls Claude: the first text, the Jev check of each sentence against the
    slice, at most one rewrite, and the honest miss of a second failed check. A checked text goes to the store.

    A kept Answer never reaches this function, so a count of its calls is the count of the Claude Answers. The caller
    asks the caps first. After the runs, the cost goes to the league month. Only a checked Answer of `roster_id` counts
    toward the team cap. The head start gives None, so it counts toward the league cap only (decision 04).
    """
    team = facts.slice["team"]
    instructions = f"The facts are the league data now, before the games of week {facts.slice['week']}."
    writer = Writer(label=f"personal Topic {topic}", agent=AGENT, prompt=topic_prompt(topic, facts.slice, own),
                    deps=None, instructions=instructions, model=model, rewrite=rewrite_prompt)
    checker = Checker(question=check_question(topic, team), your_team=your_team,
                      results={"team_facts": facts.slice}, closest=CLOSEST[topic])
    outcome = Outcome()
    async for chunk in checked_answer(asker, writer, checker, roster_id, outcome):
        yield chunk
    if outcome.end == "checked":
        await anyio.to_thread.run_sync(store.put, key, topic, facts.block["team"], {"text": outcome.text},
                                       asker.clock())


async def _kept(answer: dict) -> AsyncIterator[BaseChunk]:
    """The text of a kept Answer at once, with its check, and no Claude call."""
    yield TextStartChunk(id="kept")
    yield TextDeltaChunk(id="kept", delta=answer["text"])
    yield TextEndChunk(id="kept")
    yield data("check", {"state": "checked"}, id="check")


async def _capped(topic: str, hit: CapHit) -> AsyncIterator[BaseChunk]:
    """The calm line of a cap in place of the text, with the 3 closest Topics, and no Claude call."""
    yield data("cap", {"cap": hit.cap, "line": hit.line, "closest": CLOSEST[topic]})


async def answer_stream(facts: PersonalFacts, key: str, text: AsyncIterator[BaseChunk]) -> AsyncIterator[BaseChunk]:
    """The whole stream of one personal Topic: the data block from code first, the key of the Answer, then the text."""
    yield StartChunk()
    yield data("block", facts.block)
    yield data("key", {"key": key})
    async for chunk in text:
        yield chunk
    yield FinishChunk(finish_reason="stop")
    yield DoneChunk()


@router.post("/personal")
async def personal(body: PersonalRequest, asker: ClientAsker, served: ServedClient,
                   request: Request) -> StreamingResponse:
    """The stream of one personal Topic for the team of the body. The facts come from the live snapshot, so the
    Answer follows each waiver claim and trade."""
    live = await load_live(served, asker.season)
    snapshot = live.snapshot
    subject = body.roster_id if body.team is None else body.team
    if body.roster_id not in snapshot.rosters or subject not in snapshot.rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    facts, key = live.key(body.topic, body.roster_id, subject)
    own = subject == body.roster_id
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
    return adapter(AGENT, "").streaming_response(answer_stream(facts, key, text))
