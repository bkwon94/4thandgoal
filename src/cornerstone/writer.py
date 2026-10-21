"""
Asks Claude for one blurb per chapter from the fact sheet, with fact IDs on every sentence.
The template blurb is the safe fallback when the writer fails twice.
"""
from collections.abc import Callable
from importlib import resources

import anthropic
from pydantic import BaseModel

from cornerstone.models import Blurb, Chapter, FactSheet, Sentence, WriterOut

MODEL = "claude-opus-5-5"
PROMPT_FILES = ("vocabulary.md", "tone.md", "writer.md")

# (system, user, output_model) -> parsed output. Tests pass a fake in place of Claude.
ClaudeCall = Callable[[str, str, type[BaseModel]], BaseModel]

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


def parse_call(content: str | list[dict], output_model: type[BaseModel], system: str | None = None) -> BaseModel:
    """One user message to Claude, parsed into the output model. Every Claude call in the tool goes through here."""
    # The chart read has no system prompt, so the argument goes out only when there is one.
    extra = {"system": system} if system is not None else {}
    response = _get_client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": content}],
        output_format=output_model,
        output_config={"effort": "high"},
        **extra,
    )
    if response.stop_reason == "refusal":
        raise RefusalError(f"Claude refused the request for {output_model.__name__}.")
    if response.parsed_output is None:
        raise WriterError(f"Claude gave no parsed output for {output_model.__name__}.")
    return response.parsed_output


def claude_call(system: str, user: str, output_model: type[BaseModel]) -> BaseModel:
    return parse_call(user, output_model, system)


def _load_prompt(name: str) -> str:
    return resources.files("cornerstone.prompts").joinpath(name).read_text(encoding="utf-8").strip()


def build_writer_prompt(
    chapter: Chapter, sheet: FactSheet, feedback: str | None
) -> tuple[str, str]:
    system = "\n\n".join(_load_prompt(name) for name in PROMPT_FILES)
    lines = [
        f"Chapter: {chapter.title}",
        f"Write {chapter.min_sentences} to {chapter.max_sentences} sentences.",
        "",
        "Facts:",
        *(f"- {fid}: {sheet.facts[fid].text}" for fid in chapter.fact_ids),
    ]
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
    if chapter.key.startswith("trade_"):
        # One cited sentence: the sides fact says who moved. Find the
        # sides fact by ID, because fact order is not a contract.
        fid = f"T{chapter.key.removeprefix('trade_')}.sides"
        return Blurb(
            chapter=chapter.key,
            sentences=[Sentence(text=sheet.facts[fid].text, fact_ids=[fid])],
            attempt=0,
            fallback=True,
        )
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
