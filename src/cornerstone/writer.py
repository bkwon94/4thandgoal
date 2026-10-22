"""
Asks Claude for one blurb per chapter from the fact sheet, with fact IDs on every sentence.
The template blurb is the safe fallback when the writer fails twice.
"""
import logging
from collections.abc import Callable
from importlib import resources

import anthropic
from pydantic import BaseModel

from cornerstone.models import Blurb, Chapter, FactSheet, Sentence, WriterOut
from cornerstone.sheet import is_motw_recap

MODEL = "claude-opus-5-5"
PROMPT_FILES = ("vocabulary.md", "tone.md", "writer.md")
# The recap of the Matchup of the Week holds the same facts as that chapter. Each chapter is one call,
# so the writer cannot see the other blurb, and this note keeps it off the same sentences.
MOTW_RECAP_NOTE = (
    "Note: the Matchup of the Week chapter already told this game's headline: the score, the upset, "
    "and the player who won it. Lead with a different fact. Never repeat a sentence from that chapter."
)

# (system, user, output_model) -> parsed output. Tests pass a fake in place of Claude.
ClaudeCall = Callable[[str, str, type[BaseModel]], BaseModel]

# The analyzer prefix stays warm for an hour, because trade requests come minutes
# apart. Every other call keeps the default five minutes, because the weekly build
# runs its calls back to back.
ANALYZER_CACHE_TTL = "1h"

# The analyzer answers a waiting browser, so it trades some depth for a faster call.
# The writer and the verifier keep the default, because the Tuesday build has no reader who waits.
ANALYZER_EFFORT = "medium"

log = logging.getLogger(__name__)

_client: anthropic.Anthropic | None = None


class RefusalError(Exception):
    """Claude refused the request, so there is no parsed output."""


class WriterError(Exception):
    """Claude gave no parsed output, for example when the output does not fit the model."""


def _get_client() -> anthropic.Anthropic:
    # One client per process: it holds the connection pool.
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def parse_call(
    content: str | list[dict], output_model: type[BaseModel], system: str | None = None,
    cache_ttl: str | None = None, effort: str = "high",
) -> BaseModel:
    """One user message to Claude, parsed into the output model.

    Every Claude call in the tool goes through here. The system prompt goes out as
    one cached block. `cache_ttl` None keeps the default five-minute lifetime.
    `effort` sets the depth of the answer.
    """
    # The chart read has no system prompt, so the argument goes out only when there is one.
    extra = {}
    if system is not None:
        cache_control = {"type": "ephemeral"}
        if cache_ttl is not None:
            cache_control["ttl"] = cache_ttl
        extra["system"] = [
            {"type": "text", "text": system, "cache_control": cache_control}
        ]
    response = _get_client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": content}],
        output_format=output_model,
        output_config={"effort": effort},
        **extra,
    )
    # A cache read of zero on a repeat call shows a cold or unstable prefix.
    usage = response.usage
    # A response with no usage skips the log line. The parsed output still counts.
    if usage is not None:
        log.info(
            "%s call: cache_creation_input_tokens=%s cache_read_input_tokens=%s"
            " input_tokens=%s",
            output_model.__name__,
            usage.cache_creation_input_tokens,
            usage.cache_read_input_tokens,
            usage.input_tokens,
        )
    if response.stop_reason == "refusal":
        raise RefusalError(f"Claude refused the request for {output_model.__name__}.")
    if response.parsed_output is None:
        raise WriterError(f"Claude gave no parsed output for {output_model.__name__}.")
    return response.parsed_output


def claude_call(system: str, user: str, output_model: type[BaseModel]) -> BaseModel:
    return parse_call(user, output_model, system)


def analyzer_call(system: str, user: str, output_model: type[BaseModel]) -> BaseModel:
    """The analyzer's Claude call. It is `claude_call` with the one-hour lifetime."""
    return parse_call(
        user, output_model, system, cache_ttl=ANALYZER_CACHE_TTL, effort=ANALYZER_EFFORT
    )


def load_prompt(name: str) -> str:
    return resources.files("cornerstone.prompts").joinpath(name).read_text(encoding="utf-8").strip()


def build_writer_prompt(
    chapter: Chapter, sheet: FactSheet, feedback: str | None
) -> tuple[str, str]:
    system = "\n\n".join(load_prompt(name) for name in PROMPT_FILES)
    lines = [
        f"Chapter: {chapter.title}",
        f"Write {chapter.min_sentences} to {chapter.max_sentences} sentences.",
        "",
        "Facts:",
        *(f"- {fid}: {sheet.facts[fid].text}" for fid in chapter.fact_ids),
    ]
    if is_motw_recap(chapter, sheet):
        lines += ["", MOTW_RECAP_NOTE]
    if feedback is not None:
        lines += ["", "Feedback from the last attempt:", feedback]
    return system, "\n".join(lines)


def write_blurb(
    chapter: Chapter, sheet: FactSheet, call: ClaudeCall, feedback: str | None = None
) -> Blurb:
    system, user = build_writer_prompt(chapter, sheet, feedback)
    out = call(system, user, WriterOut)
    # Any call, real or injected, can come back empty. That is a failed attempt, not a blurb.
    if out is None:
        raise WriterError(f"no parsed output for {chapter.key}")
    return Blurb(
        chapter=chapter.key,
        sentences=out.sentences,
        attempt=1 if feedback is None else 2,
        fallback=False,
    )


def template_blurb(chapter: Chapter, sheet: FactSheet) -> Blurb:
    """One sentence built from a fact. A boring sentence beats a wrong one."""
    result_id = next(
        (f for f in chapter.fact_ids if f.endswith(".result")), None
    ) if chapter.key == "motw" or chapter.key.startswith("recap_") else None
    fid = result_id or chapter.fact_ids[0]
    return Blurb(
        chapter=chapter.key,
        sentences=[Sentence(text=sheet.facts[fid].text, fact_ids=[fid])],
        attempt=0,
        fallback=True,
    )
