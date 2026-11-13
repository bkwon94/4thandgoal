"""
The personal Topics of the front door, live on the API: weak spots, how you stack up, and waiver targets. Each streams
its data block from code first (waiver targets after a Jev read of each free agent), then the Jev check of the text
of Claude over its slice, then the text that passed. A kept Answer comes back free.
"""
import hashlib
import json
import logging
import threading
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import anyio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent
from pydantic_ai.capabilities import Caching
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.ui.vercel_ai.response_types import (
    BaseChunk,
    DoneChunk,
    ErrorChunk,
    FinishChunk,
    StartChunk,
)

from analyzer.routes import ServedClient
from cornerstone_api.answer_store import AnswerStore
from cornerstone_api.ask import QUESTION_MAX, Asker, ClientAsker
from cornerstone_api.caps import CapHit
from cornerstone_api.chat_turns import Turn, Turns, turn_messages, turns_instructions
from cornerstone_api.claude_stream import (
    STREAM_ERROR,
    Checker,
    Outcome,
    Writer,
    adapter,
    checked_answer,
    data,
    kept_text,
)
from cornerstone_api.comparison import COMPARISON_KIND
from cornerstone_api.personal_facts import (
    PersonalFacts,
    PersonalTopic,
    judged_waiver,
    live_grades,
    topic_facts,
)
from cornerstone_api.personal_wording import (
    COMPARE_ASK,
    FACT_MEANINGS,
    INSTRUCTIONS,
    SWAP_BENCH,
    SWAP_MEANING,
    SWAP_QUESTION,
    SWAP_STARTER,
    TOPIC_ASKS,
    WAIVER_ADD,
    WAIVER_STASH,
    check_question,
    rewrite_prompt,
    topic_prompt,
)
from cornerstone_api.start_sit import START_SIT, LiveWeek, checked_block, load_live_week
from cornerstone_api.waiver_targets import judge
from facts.writer import route_model
from league.jev_port import Jev, JevError
from league.provider.raw import RawTrending
from league.snapshot import Snapshot
from managers.grade import ManagerGrade, Starter

logger = logging.getLogger(__name__)

router = APIRouter()

# The route table maps a personal Topic to its model and its effort (spec, "The Answers and the stream").
ROUTE = route_model("personal_topic")
# The model of the agent, in the form of Pydantic AI. The key of each Answer names it.
MODEL = f"anthropic:{ROUTE.model}"
# A short Answer needs few tokens, but a cut Answer is worse than a long one, so the cap leaves room for the thinking.
MAX_TOKENS = 16000
# The seconds that one live league serves each request of a client before the API loads Sleeper again. The tap on a
# Suggestion comes soon after the open, so it reads the league of the open and its kept Answer shows at once (AT-8).
# A waiver claim or a trade reaches the key and the stale check within this window, half the window of the teams route.
LIVE_CACHE_SECONDS = 120
# The seconds that one list of Sleeper trending adds serves a client. Its counts cover the last day of adds in every
# Sleeper league, so a list half an hour old reads the same crowd. The list is in the key of each waiver Answer, so a
# shorter window would make the kept Answers stale more often. The depth chart comes with the live league, from the
# nflverse file that the live snapshot refreshes each day, so it needs no cache of its own.
TRENDING_CACHE_SECONDS = 30 * 60
# The closest Topics of the honest miss of each personal Topic, after a second failed check.
CLOSEST: dict[str, list[str]] = {
    "weak_spots": ["stack_up", "waiver_targets", "trade_ideas"],
    "stack_up": ["weak_spots", "power_rankings", "your_season"],
    "waiver_targets": ["weak_spots", "stack_up", "trade_ideas"],
    "start_sit": ["next_matchup", "weak_spots", "waiver_targets"],
}

AGENT = Agent(
    MODEL,
    name="personal_topic",
    instructions=INSTRUCTIONS,
    model_settings=AnthropicModelSettings(anthropic_effort=ROUTE.effort, max_tokens=MAX_TOKENS),
    capabilities=[Caching()],
    defer_model_check=True,
)


class PersonalRequest(BaseModel):
    """The body of a personal Topic: the Topic, the roster id of Your team, the roster id of the team that the
    Answer is about, or None for Your team, the earlier turns of the Thread, and the typed question. Only a typed
    question carries turns and its text, and a tapped Topic has none. useChat adds its own fields, and the route reads
    none of them."""

    model_config = ConfigDict(extra="ignore")

    topic: PersonalTopic
    roster_id: int
    team: int | None = None
    turns: Turns = Field(default_factory=list)
    question: str | None = Field(default=None, min_length=1, max_length=QUESTION_MAX)


def answer_key(topic: str, own: bool, facts: PersonalFacts, roster: list[str]) -> str:
    """The key of an Answer: the facts it read, the roster of its team, whom it addresses, and the wording and the
    model that wrote it. A waiver claim or a trade changes the roster, so the key changes and Claude writes a fresh
    Answer. The roster is in the key, because a bench add can leave the slice the same and still change the read."""
    body = {"topic": topic, "own": own, "slice": facts.slice, "block": facts.block, "roster": sorted(roster),
            "instructions": INSTRUCTIONS, "ask": TOPIC_ASKS[topic], "model": MODEL, "effort": ROUTE.effort}
    if topic == "waiver_targets":
        # The Jev read picks the players that the Answer names, so a change of its wording gives a fresh Answer.
        body["judge"] = {"add": WAIVER_ADD, "stash": WAIVER_STASH}
    if topic == START_SIT:
        # The Jev read picks the Swaps that the Answer shows, so a change of its wording gives a fresh Answer.
        body["judge"] = {"question": SWAP_QUESTION, "bench": SWAP_BENCH, "starter": SWAP_STARTER,
                         "means": SWAP_MEANING}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Live:
    """The live league of one request: the snapshot, the roster grade and the starters of each roster now, and the
    Sleeper trending adds."""

    snapshot: Snapshot
    grades: dict[int, ManagerGrade]
    starters: dict[int, list[Starter]]
    trending: list[RawTrending]

    def facts(self, topic: PersonalTopic, subject: int) -> PersonalFacts:
        """The facts of `topic` for the team of `subject`. The waiver targets give the facts before the Jev read."""
        return topic_facts(topic, self.snapshot, subject, self.grades, self.starters, self.trending)

    def key(self, topic: PersonalTopic, roster_id: int, subject: int) -> tuple[PersonalFacts, str]:
        """The facts and the key of the Answer of `topic` about `subject`, for the manager of `roster_id`."""
        facts = self.facts(topic, subject)
        return facts, answer_key(topic, subject == roster_id, facts, self.snapshot.rosters[subject])


class LiveCache:
    """The last live league of one client per season, with the monotonic time of its load, and the last trending list.

    One lock covers the check and the load, so the open, its head start, and a quick tap make one load and not three.
    A load that raises leaves the cache as it was, so the next request tries again.
    """

    def __init__(self, max_age_seconds: float, clock: Callable[[], float] = time.monotonic,
                 trending_seconds: float = TRENDING_CACHE_SECONDS) -> None:
        self.max_age_seconds = max_age_seconds
        self.clock = clock
        self.trending_seconds = trending_seconds
        self._lock = threading.Lock()
        self._entries: dict[int, tuple[float, Live]] = {}
        self._trending: tuple[float, list[RawTrending]] | None = None

    def trending(self, fetch: Callable[[], list[RawTrending]]) -> list[RawTrending]:
        """The trending list from memory within its window. Past it, `fetch` runs. A load of the league calls it under
        the lock of get_or_load."""
        if self._trending is not None and self.clock() - self._trending[0] < self.trending_seconds:
            return self._trending[1]
        rows = fetch()
        self._trending = (self.clock(), rows)
        return rows

    def get_or_load(self, season: int, load: Callable[[], Live]) -> Live:
        """The league of `season` from memory within the window. Past it, `load` runs and the cache keeps its league."""
        with self._lock:
            entry = self._entries.get(season)
            if entry is not None and self.clock() - entry[0] < self.max_age_seconds:
                return entry[1]
            live = load()
            self._entries[season] = (self.clock(), live)
            return live


def _load(served: Any, season: int, cache: LiveCache) -> Live:
    """The live league for the client of `served`, from a fresh snapshot. It raises ValueError as the snapshot does."""
    snapshot = served.sources.snapshot(season)
    grades, starters = live_grades(snapshot)
    return Live(snapshot, grades, starters, cache.trending(served.sources.fetch_trending))


async def load_live(served: Any, season: int, cache: LiveCache) -> Live:
    """The live league for the client of `served`, from `cache` within its window. Raises HTTPException 503 when the
    facts do not load."""
    try:
        return await anyio.to_thread.run_sync(cache.get_or_load, season, lambda: _load(served, season, cache))
    except ValueError as error:
        logger.warning("The facts of a personal Topic did not load (%s)", error)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None


async def load_week(served: Any, season: int) -> LiveWeek:
    """The live week of Start or sit for the client of `served`. Raises HTTPException 503 when Sleeper or the kickoffs
    do not load."""
    try:
        return await anyio.to_thread.run_sync(load_live_week, served.sources, season)
    except ValueError as error:
        logger.warning("The live week of Start or sit did not load (%s)", error)
        raise HTTPException(status_code=503, detail="The question did not go through. Ask again.") from None


async def claude_answer(asker: Asker, store: AnswerStore, topic: str, facts: PersonalFacts, key: str, own: bool,
                        your_team: str, model: Model | None, roster_id: int | None,
                        turns: list[Turn] | None = None, question: str | None = None) -> AsyncIterator[BaseChunk]:
    """The one place where a personal Answer calls Claude: the first text, the Jev check of each sentence against the
    slice, at most one rewrite, and the honest miss of a second failed check. A checked text goes to the store.

    A kept Answer never reaches this function, so a count of its calls is the count of the Claude Answers. The caller
    asks the caps first. After the runs, the cost goes to the league month. Only a checked Answer of `roster_id` counts
    toward the team cap. The head start gives None, so it counts toward the league cap only (decision 04).

    Claude reads the earlier `turns` of a typed question as messages before the prompt, and the typed `question` in the
    prompt. The text then fits that question, so it never goes to the store, and the kept Answer of a tap stays as the
    tap wrote it.
    """
    team = facts.slice["team"]
    turns = turns or []
    instructions = turns_instructions(f"The facts are the league data now, before the games of week "
                                      f"{facts.slice['week']}.", turns)
    # The comparison of two players has its own ask, because its slice holds two Fact sheets and not a lineup.
    ask = COMPARE_ASK if facts.block.get("kind") == COMPARISON_KIND else None
    writer = Writer(label=f"personal Topic {topic}", agent=AGENT,
                    prompt=topic_prompt(topic, facts.slice, own, question, ask),
                    deps=None, instructions=instructions, model=model, rewrite=rewrite_prompt,
                    history=turn_messages(turns))
    checker = Checker(question=check_question(topic, team, question), your_team=your_team,
                      results={"team_facts": facts.slice, "meanings": FACT_MEANINGS}, closest=CLOSEST[topic])
    outcome = Outcome()
    async for chunk in checked_answer(asker, writer, checker, roster_id, outcome):
        yield chunk
    block = facts.block
    if outcome.end == "checked" and topic == START_SIT:
        # Claude writes the reason of each Swap and the reason of a pick, so the block comes again after the check with
        # the checked sentences of each Swap, or the dot on each fact that the checked text cites.
        block = checked_block(facts.block, outcome.text)
        if block != facts.block:
            yield data("block", block)
    if outcome.end == "checked" and not turns and question is None:
        # The block goes with the text, so a kept waiver Answer shows the players of its Jev read with no second read.
        await anyio.to_thread.run_sync(store.put, key, topic, block["team"],
                                       {"text": outcome.text, "block": block}, asker.clock())


async def shown_facts(jev: Jev, topic: str, facts: PersonalFacts) -> PersonalFacts:
    """The facts that the block shows and Claude reads. The waiver targets run the Jev read of each candidate first, and
    keep the players worth a claim. Every other Topic shows its facts as they are. A failed read raises JevError."""
    if topic != "waiver_targets":
        return facts
    started = time.monotonic()
    judged = await anyio.to_thread.run_sync(judge, jev, facts.slice["week"], facts.slice["team_need"],
                                            facts.slice["candidates"])
    logger.info("The waiver read of %s took %.1f s: %d Jev requests, %d input tokens, %d kept",
                facts.slice["team"], time.monotonic() - started, judged.requests, judged.input_tokens,
                len(judged.kept))
    return judged_waiver(facts, judged.kept)


async def _capped(topic: str, hit: CapHit) -> AsyncIterator[BaseChunk]:
    """The calm line of a cap in place of the text, with the 3 closest Topics, and no Claude call."""
    yield data("cap", {"cap": hit.cap, "line": hit.line, "closest": CLOSEST[topic]})


async def answer_stream(facts: Callable[[], Awaitable[PersonalFacts]], key: str,
                        text: Callable[[PersonalFacts], AsyncIterator[BaseChunk]],
                        miss: list[str] | None = None) -> AsyncIterator[BaseChunk]:
    """The whole stream of one personal Topic: the data block from code first, the key of the Answer, then the text.

    The stream starts before `facts` gives the facts to show, so the Jev read of the waiver targets and of the Swaps
    runs inside it. A failed read ends the stream with no block and no text: the honest miss with the closest Topics of
    `miss`, or else an error.
    """
    yield StartChunk()
    try:
        shown = await facts()
    except JevError as error:
        logger.warning("The Jev read of a personal Topic failed (%s)", error)
        if miss is not None:
            yield data("miss", {"closest": miss})
        else:
            yield ErrorChunk(error_text=STREAM_ERROR)
    else:
        yield data("block", shown.block)
        yield data("key", {"key": key})
        async for chunk in text(shown):
            yield chunk
    yield FinishChunk(finish_reason="stop")
    yield DoneChunk()


async def _as_is(facts: PersonalFacts) -> PersonalFacts:
    return facts


@router.post("/personal")
async def personal(body: PersonalRequest, asker: ClientAsker, served: ServedClient,
                   request: Request) -> StreamingResponse:
    """The stream of one personal Topic for the team of the body. The facts come from the live snapshot, so the
    Answer follows each waiver claim and trade. Start or sit reads the live Sleeper week and its kickoffs instead."""
    subject = body.roster_id if body.team is None else body.team
    own = subject == body.roster_id
    if body.topic == START_SIT:
        # Start or sit reads the live week and its kickoffs fresh for each Answer, because the game lock moves with the
        # clock, so it reads no live league of the cache.
        week = await load_week(served, asker.season)
        rosters, team_name = week.rosters, week.team_name
        facts_of: Callable[[], PersonalFacts] = lambda: week.facts(subject)
        # The Jev read of the Swaps runs in the stream. A failed read gives the honest miss, never the lineup by
        # projection, because a failed read is not a "keep the starter" (AT-20).
        # A typed question that names two players of the roster gets the comparison, and three or more get the slots
        # that they can fill.
        question = body.question
        judged: Callable[[], Awaitable[PersonalFacts]] = lambda: anyio.to_thread.run_sync(week.asked, asker.jev,
                                                                                           subject, question)
        miss: list[str] | None = CLOSEST[START_SIT]
    else:
        live = await load_live(served, asker.season, request.app.state.live[request.path_params["slug"]])
        rosters, team_name = live.snapshot.rosters, lambda roster_id: live.snapshot.teams[roster_id].name
        facts_of = lambda: live.facts(body.topic, subject)
        judged = lambda: shown_facts(asker.jev, body.topic, facts)
        miss = None
    if body.roster_id not in rosters or subject not in rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    facts = facts_of()
    key = answer_key(body.topic, own, facts, rosters[subject])
    store: AnswerStore = request.app.state.kept[request.path_params["slug"]]
    # A typed question gets an Answer that fits its text and its chat, so it reads no kept Answer. Only a tap reads one,
    # so a tap never gets the Answer of a typed question, and one typed question never gets the Answer of another.
    typed = bool(body.turns) or body.question is not None
    kept = None if typed else await anyio.to_thread.run_sync(store.get, key)
    if kept is not None:
        logger.info("The personal Topic %s came from the store, with no Claude call", body.topic)
        # A kept Answer shows the block it was written from. An Answer kept with no block shows the block of now.
        shown = PersonalFacts(slice=facts.slice, block=kept.get("block", facts.block))
        stream = answer_stream(lambda: _as_is(shown), key, lambda _: kept_text(kept["text"]))
    elif (hit := await anyio.to_thread.run_sync(asker.caps.check, body.roster_id, asker.clock())) is not None:
        # Past a cap, everything that costs nothing still works: the data block from code, and the cap line. The Jev
        # read of the waiver targets costs too, so its block shows the facts before the read.
        logger.info("The personal Topic %s stopped at the %s cap, with no Claude call", body.topic, hit.cap)
        cap = hit
        stream = answer_stream(lambda: _as_is(facts), key, lambda _: _capped(body.topic, cap))
    else:
        your_team = team_name(body.roster_id)
        model = request.app.state.personal_model
        stream = answer_stream(judged, key,
                               lambda shown: claude_answer(asker, store, body.topic, shown, key, own, your_team, model,
                                                           body.roster_id, body.turns, body.question), miss)
    return adapter(AGENT, "").streaming_response(stream)
