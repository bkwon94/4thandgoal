"""
The stream engine of each checked Claude answer of the front door, for the free answer and each personal Topic: a run
through VercelAIAdapter, the Jev check of each sentence after the last word, at most one rewrite, and the cost record.
"""
import logging
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any

import anyio
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model
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
    TextEndChunk,
    TextStartChunk,
)

from cornerstone_api.ask import YES, Asker
from cornerstone_api.caps import sonnet_cost
from cornerstone_api.free_wording import check_questions, check_state, sentence_key, sentences
from league.jev_port import Jev, JevError

logger = logging.getLogger(__name__)

# The error line of a stream that stops. The site shows its own retry line, so this text is for the log of the browser.
STREAM_ERROR = "The answer did not go through. Ask again."
SDK_VERSION = 7
# The adapter frames each run with its own start, finish, and done. The caller has one frame for all its runs.
_FRAME = (StartChunk, FinishChunk, DoneChunk, MessageMetadataChunk)


@dataclass
class Attempt:
    """One run of Claude: its text, the text parts that wait for the check, the messages of the run, and its usage."""

    text: str = ""
    held: list[BaseChunk] = field(default_factory=list)
    messages: list[ModelMessage] = field(default_factory=list)
    errored: bool = False
    result: AgentRunResult | None = None


@dataclass
class Outcome:
    """How a checked answer ended: "checked", "an honest miss", or "an error", and the checked text."""

    end: str = "an error"
    text: str = ""


def adapter(agent: Agent[Any, str], prompt: str, message_id: str = "ask") -> VercelAIAdapter[Any, str]:
    """The adapter of one run of `agent`. Its one user message is the prompt from code, never a message from the client.

    Each run gives its message its own id, so the adapter never reads the rewrite as a repeat of the question.
    """
    message = UIMessage(id=message_id, role="user", parts=[TextUIPart(text=prompt)])
    run_input = SubmitMessage(id="free", messages=[message])
    return VercelAIAdapter(agent=agent, run_input=run_input, sdk_version=SDK_VERSION)


def data(kind: str, body: dict, id: str | None = None) -> DataChunk:
    """One data part of the stream, such as the check state, which the site reads as `data-<kind>`."""
    return DataChunk(type=f"data-{kind}", id=id, data=body)


async def kept_text(text: str) -> AsyncIterator[BaseChunk]:
    """The text of a kept answer at once, with its check, and no Claude call."""
    yield TextStartChunk(id="kept")
    yield TextDeltaChunk(id="kept", delta=text)
    yield TextEndChunk(id="kept")
    yield data("check", {"state": "checked"}, id="check")


async def run(agent: Agent[Any, str], prompt: str, deps: Any, instructions: str, history: list[ModelMessage],
              attempt: Attempt, model: Model | None) -> AsyncIterator[BaseChunk]:
    """The chunks of one run, with the frame chunks left out. The text parts wait in `attempt.held`, and the text in
    `attempt.text`, so a text goes to the manager only after its check passes (H10). The tool steps stream as they run.
    """

    async def keep(result: AgentRunResult) -> None:
        attempt.result = result
        attempt.messages = result.all_messages()

    texts: list[str] = []
    async for chunk in adapter(agent, prompt, f"ask-{len(history)}").run_stream(
            deps=deps, instructions=instructions, message_history=history, model=model, on_complete=keep):
        if isinstance(chunk, _FRAME):
            continue
        if isinstance(chunk, TextDeltaChunk):
            texts.append(chunk.delta)
        if isinstance(chunk, (TextStartChunk, TextDeltaChunk, TextEndChunk)):
            # A text that fails its check gets a rewrite, so no word of it may show before the check.
            attempt.held.append(chunk)
            continue
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


def usage_line(label: str, attempts: list[Attempt], end: str, tool_calls: int | None) -> str:
    """The log line of one checked answer: how it ended, its tool calls if it has tools, its texts, and its usage."""
    usages = [a.result.usage for a in attempts if a.result is not None]
    costs = [u.cost for u in usages if u.cost is not None]
    cost = f"${float(sum(costs)):.4f}" if len(costs) == len(usages) and usages else "unknown"
    calls = "" if tool_calls is None else f"{tool_calls} tool calls, "
    return (f"The {label} ended as {end}, with {calls}{len(attempts)} texts, "
            f"{sum(u.input_tokens for u in usages)} input tokens, {sum(u.output_tokens for u in usages)} output "
            f"tokens, and a cost of {cost}")


@dataclass(frozen=True)
class Writer:
    """What one checked answer runs: the label of its log lines, its agent, its first prompt, its tool deps, its
    instructions, its model, and the rewrite prompt of the failed sentences. A test gives `model`, and the real app
    gives None, so the run takes the model of the agent. `history` holds the earlier turns of the Thread as messages,
    or nothing for a tapped Topic."""

    label: str
    agent: Agent[Any, str]
    prompt: str
    deps: Any
    instructions: str
    model: Model | None
    rewrite: Callable[[list[str]], str]
    tool_calls: Callable[[], int] | None = None
    history: list[ModelMessage] = field(default_factory=list)


@dataclass(frozen=True)
class Checker:
    """What the Jev check of one answer reads: the question, Your team, the results that each sentence must follow
    from, and the closest Topics of the honest miss. The tools of a free answer fill `results` during the run."""

    question: str
    your_team: str
    results: dict[str, Any]
    closest: list[str]


async def checked_answer(asker: Asker, writer: Writer, checker: Checker, roster_id: int | None,
                         outcome: Outcome) -> AsyncIterator[BaseChunk]:
    """The text of one checked answer, as stream parts with no frame: the tool steps of the first run, the check, at
    most one rewrite, and the honest miss of a second failed check. Only a text that passes its check streams, whole,
    just before "checked", so the manager never reads a text that a rewrite replaces (H10). `outcome` holds the end
    and the checked text for the caller.

    After the runs, the cost goes to the league month. Only a checked answer of `roster_id` counts toward the team
    cap, because an honest miss and an error do not count. A `roster_id` of None counts toward the league cap only.
    """
    attempts: list[Attempt] = []
    # The first run reads the earlier turns of the Thread. The rewrite reads the whole first run, turns and all.
    history: list[ModelMessage] = list(writer.history)
    prompt = writer.prompt
    for number in (1, 2):
        attempt = Attempt()
        attempts.append(attempt)
        if number == 2:
            # The site shows "Fixing a number…" at this part. The failed first text never left the API.
            yield data("check", {"state": "fixing"}, id="check")
            yield data("fix", {})
        async for chunk in run(writer.agent, prompt, writer.deps, writer.instructions, history, attempt, writer.model):
            yield chunk
        if attempt.errored:
            break
        yield data("check", {"state": "checking"}, id="check")
        try:
            failed = await anyio.to_thread.run_sync(check, asker.jev, checker.question, checker.your_team,
                                                    attempt.text, checker.results)
        except JevError as error:
            # A failed Jev call is an error, never a "no" and never a pass.
            logger.warning("The Jev check of the %s failed (%s)", writer.label, type(error).__name__)
            yield ErrorChunk(error_text=STREAM_ERROR)
            break
        if not failed:
            outcome.end, outcome.text = "checked", attempt.text.strip()
            for chunk in attempt.held:
                yield chunk
            yield data("check", {"state": "checked"}, id="check")
            break
        if number == 2:
            outcome.end = "an honest miss"
            yield data("check", {"state": "failed"}, id="check")
            yield data("miss", {"closest": checker.closest})
            break
        history = attempt.messages
        prompt = writer.rewrite(failed)
    tool_calls = None if writer.tool_calls is None else writer.tool_calls()
    logger.info(usage_line(writer.label, attempts, outcome.end, tool_calls))
    usd = sum(sonnet_cost(a.result.usage) for a in attempts if a.result is not None)
    counts = roster_id is not None and outcome.end == "checked"
    await anyio.to_thread.run_sync(lambda: asker.caps.record(roster_id, usd, asker.clock(), counts=counts))
