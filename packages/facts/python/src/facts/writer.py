"""
Asks Claude for one blurb per chapter from the fact sheet, with fact IDs on every sentence.
The template blurb is the safe fallback when the writer fails twice.
"""
import logging
import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

from facts.chapters import BYE_FACT_PREFIX, repeats_motw_headline
from league.claude_errors import RefusalError, WriterError
from league.claude_port import Writer
from league.models import Blurb, Chapter, FactSheet, Sentence, WriterOut

MODEL = "claude-opus-5-5"
PROMPT_FILES = ("vocabulary.md", "tone.md", "writer.md")
# The prompts of the facts package: the default voice and the rule prompts of the writer and the verifier.
DEFAULT_PROMPTS = Path(__file__).parent / "prompts"
# The voice files. The prompts folder of a client can replace only these two.
VOICE_FILES = frozenset({"tone.md", "vocabulary.md"})
# The recap of the Matchup of the Week holds the same facts as that chapter. Each chapter is one call,
# so the writer cannot see the other blurb, and this note keeps it off the same sentences.
# The game changer and awards chapters get it too when the Game Changer plays in that matchup.
# The game story is not the headline, so the note keeps the recap on the turn, the lead, and the injury.
MOTW_HEADLINE_NOTE = (
    "Note: the Matchup of the Week chapter and its recap already told this game's headline: the score, "
    "the upset, and the player who won it. Lead with a different fact. Never repeat a sentence from those chapters. "
    "The turn, the lead, and the injury are not the headline. A recap tells them."
)
# The Next Week chapter gets this line when it lists a bye fact, so the writer treats the byes as part of the preview.
BYES_NOTE = "Note: the byes next week are part of the preview."
# The header of the words that other chapters of the page already say. Rule 14 of the writer prompt names it.
PAGE_WORDS_HEADER = "Words this page already uses:"

# The errors of one failed Claude check: a refusal, an empty or bad output, or a failed API call. A package outside
# facts catches them by this name, so only facts and league import the Claude SDK (ADR 0023).
CHECK_ERRORS = (RefusalError, WriterError, anthropic.APIError, ValidationError)

# (system, user, output_model) -> parsed output. Tests pass a fake in place of Claude.
ClaudeCall = Callable[[str, str, type[BaseModel]], BaseModel]
# The output model of one retried call, so the caller gets back the type it asked for.
Out = TypeVar("Out", bound=BaseModel)

# A failure can quote a trade value, so the log line of a retried call masks every number.
# Claude still gets the full text as feedback.
ANY_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")

# The analyzer prefix stays warm for an hour, because trade requests come minutes
# apart. Every other call keeps the default five minutes, because the weekly build
# runs its calls back to back.
ANALYZER_CACHE_TTL = "1h"

# The analyzer answers a waiting browser, so it trades some depth for a faster call.
# The writer and the verifier keep the default, because the Tuesday build has no reader who waits.
ANALYZER_EFFORT = "medium"

log = logging.getLogger(__name__)


class ClaudeWriter:
    """The Claude implementation of the Writer port. Every Claude call in the tool goes through `parse`.

    A test passes a stub client to check the request shape. With no client, the writer makes one on its first call.
    """

    def __init__(self, client: anthropic.Anthropic | None = None):
        self._client = client

    def parse(
        self, content: str | list[dict], output_model: type[BaseModel], system: str | None = None,
        cache_ttl: str | None = None, effort: str = "high", tools: list[dict] | None = None,
    ) -> BaseModel:
        """The Claude call of `Writer.parse`. The docstring of the protocol in claude_port.py gives the arguments."""
        # One client per writer: it holds the connection pool. The first call makes it, so an import needs no API key.
        if self._client is None:
            self._client = anthropic.Anthropic()
        # The chart read has no system prompt, so the argument goes out only when there is one.
        extra = {}
        if system is not None:
            cache_control = {"type": "ephemeral"}
            if cache_ttl is not None:
                cache_control["ttl"] = cache_ttl
            extra["system"] = [
                {"type": "text", "text": system, "cache_control": cache_control}
            ]
        # Only the research call searches the web, so every other call sends no tools.
        if tools is not None:
            extra["tools"] = tools
        response = self._client.messages.parse(
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


# The one writer of the process, so the process has one client. The three functions below call it by default.
WRITER = ClaudeWriter()


def parse_call(
    content: str | list[dict], output_model: type[BaseModel], system: str | None = None,
    cache_ttl: str | None = None, effort: str = "high", tools: list[dict] | None = None,
    *, writer: Writer | None = None,
) -> BaseModel:
    """`Writer.parse` on `writer`, or on WRITER when `writer` is None. Every Claude call in the tool goes through here.

    The CLI passes its writer, and a test passes a fake.
    """
    return (WRITER if writer is None else writer).parse(content, output_model, system, cache_ttl, effort, tools)


def claude_call(system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None) -> BaseModel:
    return parse_call(user, output_model, system, writer=writer)


def analyzer_call(
    system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None
) -> BaseModel:
    """The analyzer's Claude call. It is `claude_call` with the one-hour lifetime."""
    return parse_call(
        user, output_model, system, cache_ttl=ANALYZER_CACHE_TTL, effort=ANALYZER_EFFORT, writer=writer
    )


def call_with_retry(
    call: ClaudeCall, prompt: Callable[[str | None], tuple[str, str]], output_model: type[Out],
    check: Callable[[Out], list[str]], subject: str, log_label: str, logger: logging.Logger,
) -> Out | None:
    """Two attempts at one checked Claude call. The output that passes the check, or None after two failures.

    The second attempt gets the failures of the first as feedback. `subject` names the output in the empty
    output error, and `log_label` starts the log line on the caller's logger.
    """
    feedback: str | None = None
    for attempt in (1, 2):
        system, user = prompt(feedback)
        try:
            out = call(system, user, output_model)
            # Any call, real or injected, can come back empty. That is a failed attempt.
            if out is None:
                raise WriterError(f"no parsed output for the {subject}")
            failures = check(out)
            if failures:
                raise WriterError("; ".join(failures))
        except (RefusalError, WriterError, ValidationError, anthropic.AnthropicError) as err:
            # A bad response is a failed attempt, not a crash of the command or the route.
            logger.warning("%s attempt %d failed: %s", log_label, attempt, ANY_NUMBER.sub("#", str(err)))
            feedback = str(err)
            continue
        return out
    return None


def load_prompt(voice_dir: Path, name: str, rules_dir: Path = DEFAULT_PROMPTS) -> str:
    """One prompt file. A voice file comes from the prompts folder `voice_dir` of the client when it holds the file,
    else from the default voice. A rule prompt always comes from `rules_dir`, the prompts folder of the package that
    owns it, so a client never changes a rule. The default is the folder of the writer and the verifier.
    """
    if name in VOICE_FILES:
        folder = voice_dir if (voice_dir / name).is_file() else DEFAULT_PROMPTS
    else:
        folder = rules_dir
    return (folder / name).read_text(encoding="utf-8").strip()


def with_terms(vocabulary: str, terms: Sequence[str]) -> str:
    """The vocabulary, then the extra terms that a core package adds, such as the median text of the week."""
    return "\n\n".join([vocabulary, *terms])


def build_writer_prompt(
    chapter: Chapter, sheet: FactSheet, feedback: str | None, page_words: str | None = None, *, prompts_dir: Path,
    terms: Sequence[str] = (),
) -> tuple[str, str]:
    """The system and the user prompt of one chapter. `terms` go right after the vocabulary."""
    system = "\n\n".join(
        with_terms(load_prompt(prompts_dir, name), terms) if name == "vocabulary.md" else load_prompt(prompts_dir, name)
        for name in PROMPT_FILES
    )
    lines = [
        f"Chapter: {chapter.title}",
        f"Write {chapter.min_sentences} to {chapter.max_sentences} sentences.",
    ]
    if chapter.max_words is not None:
        lines.append(f"Write {chapter.max_words} words or fewer.")
    # Rule 1 of the writer prompt allows one reaction. A chapter that allows more says so here, in the user prompt.
    if chapter.max_reactions > 1:
        lines.append(f"This block may hold up to {chapter.max_reactions} reaction sentences, after a cited sentence.")
    lines += [
        "",
        "Facts:",
        *(f"- {fid}: {sheet.facts[fid].text}" for fid in chapter.fact_ids),
    ]
    # The facts of the other chapters come after the facts of the block, so the block leads with its own story.
    if chapter.callback_ids:
        lines += ["", "Facts of the other chapters. Cite one only for a callback:",
                  *(f"- {fid}: {sheet.facts[fid].text}" for fid in chapter.callback_ids)]
    if chapter.required:
        lines += ["", f"Cite each of these facts in its team's sentences: {', '.join(chapter.required)}."]
    if repeats_motw_headline(chapter, sheet):
        lines += ["", MOTW_HEADLINE_NOTE]
    if any(fid.startswith(BYE_FACT_PREFIX) for fid in chapter.fact_ids):
        lines += ["", BYES_NOTE]
    if page_words is not None:
        lines += ["", PAGE_WORDS_HEADER, page_words]
    if feedback is not None:
        lines += ["", "Feedback from the last attempt:", feedback]
    return system, "\n".join(lines)


def write_blurb(
    chapter: Chapter,
    sheet: FactSheet,
    call: ClaudeCall,
    feedback: str | None = None,
    page_words: str | None = None,
    attempt: int = 1,
    *,
    prompts_dir: Path,
    terms: Sequence[str] = (),
) -> Blurb:
    system, user = build_writer_prompt(chapter, sheet, feedback, page_words, prompts_dir=prompts_dir, terms=terms)
    out = call(system, user, WriterOut)
    # Any call, real or injected, can come back empty. That is a failed attempt, not a blurb.
    if out is None:
        raise WriterError(f"no parsed output for {chapter.key}")
    return Blurb(
        chapter=chapter.key,
        sentences=out.sentences,
        attempt=attempt,
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
