"""
Asks Claude for one blurb per chapter from the fact sheet, with fact IDs on every sentence.
The template blurb is the safe fallback when the writer fails twice.
"""
import logging
import re
import threading
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Literal, NamedTuple, TypeVar

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

SONNET = "claude-sonnet-5-5"
# The effort levels of the Claude API.
Effort = Literal["low", "medium", "high", "xhigh", "max"]


class RouteModel(NamedTuple):
    """The Claude model and the effort of one route of the front door."""

    model: str
    effort: Effort


# The table in code that maps each route of the front door to its model and its effort (spec of front-door, "The
# Answers and the stream"). Each call site reads its row, so one place names the model of each route. A league Topic
# and a miss make no Claude call. A judgment Topic runs the Advisor, so its row is the model of the Advisor call behind
# it: the read of one trade for the trade check, the Finder pick for trade ideas, and the sell high pick.
ROUTE_MODELS: dict[str, RouteModel | None] = {
    "league_topic": None,
    "miss": None,
    # A personal Topic reads a small slice and a manager waits on it.
    "personal_topic": RouteModel(SONNET, "medium"),
    # A free answer is short and reads at most 4 tool results, so low effort keeps it to about 10 to 20 s.
    "free_answer": RouteModel(SONNET, "low"),
    "trade_check": RouteModel(MODEL, "medium"),
    "trade_ideas": RouteModel(SONNET, "medium"),
    "sell_high": RouteModel(SONNET, "medium"),
}


def route_model(route: str) -> RouteModel:
    """The row of a route that calls Claude. A route with no row, or with no Claude call, is a bug, so it raises."""
    row = ROUTE_MODELS[route]
    if row is None:
        raise ValueError(f"The route {route} makes no Claude call.")
    return row


# The analyzer answers a waiting browser, so it trades some depth for a faster call. The route table holds its row.
# The writer and the verifier keep the default, because the Tuesday build has no reader who waits.
ANALYZER_MODEL, ANALYZER_EFFORT = route_model("trade_check")
# The Finder pick reads 10 offers in one call, about 28,000 input tokens, and a Finder press must end in 35 s and
# cost $0.15 or less. On Opus one call cost about $0.13, so a retry of the pick went past the limit. Sonnet costs half
# of Opus per token. The read of one trade stays on Opus. The route table holds the row of trade ideas.
FINDER_PICK_MODEL, FINDER_PICK_EFFORT = route_model("trade_ideas")
# A repair call fixes the text of one failed pick on its one sheet, so it reads a small message and writes one pick.
# A retry of the whole pick call doubled the time and the cost of a press, so a failed pick gets this small call
# instead. Low effort keeps it short. It runs on FINDER_PICK_MODEL.
FINDER_REPAIR_EFFORT = "low"
# The sell high pick reads one roster side by side, a small sheet, and a manager waits on it, so it runs on Sonnet 5.5
# at medium effort, as the Finder pick does (spec of front-door). The route table holds its row.
SELL_HIGH_MODEL, SELL_HIGH_EFFORT = route_model("sell_high")

log = logging.getLogger(__name__)


class Price(NamedTuple):
    """Dollars per million tokens of one model: input, output, cache read, and cache write."""

    input: float
    output: float
    cache_read: float
    cache_write: float


# The prices of the pricing page of Anthropic. Opus 5.5 is $4 for input, $20 for output, and $0.20 for a cache read,
# and Sonnet 5.5 costs half of Opus per token. The analyzer calls keep the one-hour cache, which writes at twice the
# input price. A model that is not here counts at the price of MODEL, so a cost never reads low.
PRICES = {MODEL: Price(4.0, 20.0, 0.20, 8.0), FINDER_PICK_MODEL: Price(2.0, 10.0, 0.10, 4.0)}


def call_cost(model: str, usage: anthropic.types.Usage) -> float:
    """The dollars of one Claude call, from the tokens of its usage."""
    price = PRICES.get(model, PRICES[MODEL])

    def tokens(name: str) -> int:
        return getattr(usage, name, 0) or 0

    return (tokens("input_tokens") * price.input + tokens("output_tokens") * price.output
            + tokens("cache_read_input_tokens") * price.cache_read
            + tokens("cache_creation_input_tokens") * price.cache_write) / 1_000_000


class PressMeter:
    """The Claude calls and the dollars of one press of the analyzer, so the log shows the cost of each press.

    A lock guards the sums, because a call can come from a thread of the press. A meter inside another meter adds each
    call to the outer one too, so a caller of a press, such as the caps of the front door, reads the cost of the press.
    """

    def __init__(self, outer: "PressMeter | None" = None) -> None:
        self.calls = 0
        self.usd = 0.0
        self._outer = outer
        self._lock = threading.Lock()

    def add(self, model: str, usage: anthropic.types.Usage) -> None:
        with self._lock:
            self.calls += 1
            self.usd += call_cost(model, usage)
        if self._outer is not None:
            self._outer.add(model, usage)


# The meter of the press that runs in this context. A call outside a press finds None and counts on no meter.
_PRESS_METER: ContextVar[PressMeter | None] = ContextVar("press_meter", default=None)


@contextmanager
def metered_press() -> Iterator[PressMeter]:
    """A meter that adds up each Claude call of WRITER or of any ClaudeWriter made in this context."""
    meter = PressMeter(outer=_PRESS_METER.get())
    token = _PRESS_METER.set(meter)
    try:
        yield meter
    finally:
        _PRESS_METER.reset(token)


class ClaudeWriter:
    """The Claude implementation of the Writer port. Every Claude call in the tool goes through `parse`.

    A test passes a stub client to check the request shape. With no client, the writer makes one on its first call.
    `on_usage` gets the usage of each response, so a run can add up its tokens and its cost.
    """

    def __init__(
        self, client: anthropic.Anthropic | None = None,
        on_usage: Callable[[anthropic.types.Usage], None] | None = None,
    ):
        self._client = client
        self._on_usage = on_usage

    def parse(
        self, content: str | list[dict], output_model: type[BaseModel], system: str | None = None,
        cache_ttl: str | None = None, effort: str = "high", tools: list[dict] | None = None,
        model: str | None = None,
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
        model = MODEL if model is None else model
        response = self._client.messages.parse(
            model=model,
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
            if self._on_usage is not None:
                self._on_usage(usage)
            if (meter := _PRESS_METER.get()) is not None:
                meter.add(model, usage)
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
    *, writer: Writer | None = None, model: str | None = None,
) -> BaseModel:
    """`Writer.parse` on `writer`, or on WRITER when `writer` is None. Every Claude call in the tool goes through here.

    The CLI passes its writer, and a test passes a fake.
    """
    return (WRITER if writer is None else writer).parse(content, output_model, system, cache_ttl, effort, tools,
                                                        model)


def claude_call(system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None) -> BaseModel:
    return parse_call(user, output_model, system, writer=writer)


def analyzer_call(
    system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None
) -> BaseModel:
    """The analyzer's Claude call. It is `claude_call` with the one-hour lifetime, on the row of the trade check."""
    return parse_call(
        user, output_model, system, cache_ttl=ANALYZER_CACHE_TTL, effort=ANALYZER_EFFORT, writer=writer,
        model=ANALYZER_MODEL,
    )


def finder_pick_call(
    system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None
) -> BaseModel:
    """The Claude call of the Finder pick. It is `analyzer_call` on FINDER_PICK_MODEL at FINDER_PICK_EFFORT."""
    return parse_call(
        user, output_model, system, cache_ttl=ANALYZER_CACHE_TTL, effort=FINDER_PICK_EFFORT, writer=writer,
        model=FINDER_PICK_MODEL,
    )


def finder_repair_call(
    system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None
) -> BaseModel:
    """The Claude call that repairs one failed Finder pick. It is `finder_pick_call` at FINDER_REPAIR_EFFORT."""
    return parse_call(
        user, output_model, system, cache_ttl=ANALYZER_CACHE_TTL, effort=FINDER_REPAIR_EFFORT, writer=writer,
        model=FINDER_PICK_MODEL,
    )


def sell_high_call(
    system: str, user: str, output_model: type[BaseModel], *, writer: Writer | None = None
) -> BaseModel:
    """The Claude call of the sell high pick. It is `analyzer_call` on SELL_HIGH_MODEL at SELL_HIGH_EFFORT."""
    return parse_call(
        user, output_model, system, cache_ttl=ANALYZER_CACHE_TTL, effort=SELL_HIGH_EFFORT, writer=writer,
        model=SELL_HIGH_MODEL,
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
