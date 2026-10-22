"""
The Claude call of the finder: one reason per win-win trade, all in one call, with the prose checks of the analysis.
A response that fails a check retries once, then each reason is empty and the result flags a fallback.
"""
import logging

from pydantic import BaseModel

from cornerstone.analysis import trade_prose_failures, trade_side_lines
from cornerstone.finder import FinderTrade
from cornerstone.models import Fact
from cornerstone.snapshot import Snapshot
from cornerstone.trade_facts import trade_fact_sheet
from cornerstone.writer import ClaudeCall, analyzer_call, call_with_retry, load_prompt

log = logging.getLogger(__name__)

# The rubric comes first, as in the analysis, so Claude reads the adjusters the breakdown lines name.
PROMPT_FILES = ("rubric.md", "finder.md")
# A manager pastes the reason into the group chat, so it is one sentence: the range is 1 to 1.
REASON_SENTENCES = (1, 1)


class FinderReason(BaseModel):
    """One reason as Claude gives it: the number of the trade in the user message, the reason, and its fact IDs."""

    trade: int
    reason: str
    cited: list[str]


class FinderReasonsOut(BaseModel):
    """The structured output of the Claude call: one reason per trade, in the order of the user message."""

    reasons: list[FinderReason]


class FinderReasons(BaseModel):
    """The reason that stands for each trade, in the order of the finder, and whether the call fell back."""

    # None after a fallback. The fairness block already holds the code's reasons, so the card shows those alone.
    reasons: list[str | None]
    # True when the call failed twice, so no trade has a reason.
    fallback: bool


def trade_facts(number: int, item: FinderTrade, snapshot: Snapshot) -> dict[str, Fact]:
    """The fact sheet of one trade, with the trade number in front of each ID.

    The need fact of a roster depends on the trade, so the same ID in two trades can hold two texts.
    The number keeps each ID to one trade, so a reason cites only the facts of its own trade.
    """
    return {f"t{number}.{fid}": fact for fid, fact in trade_fact_sheet(item.trade, snapshot).items()}


def _trade_shape(count: int) -> str:
    """The one shape of the reasons that the check accepts, in words."""
    return f"exactly {count} reasons: trades {', '.join(str(n) for n in range(1, count + 1))} in order, each once"


def build_finder_prompt(
    found: list[FinderTrade], snapshot: Snapshot, facts: list[dict[str, Fact]], feedback: str | None,
) -> tuple[str, str]:
    system = "\n\n".join(load_prompt(name) for name in PROMPT_FILES)
    lines = []
    for number, (item, trade_sheet) in enumerate(zip(found, facts), start=1):
        lines += [f"Trade {number}", ""]
        for block, gain in zip(trade_side_lines(item.trade, snapshot, item.breakdowns), item.fairness.sides):
            # The fairness reason is what the code says this side gains, so the reason can lead with it.
            lines += [*block, f"Gains: {gain.reason}", ""]
        lines += ["Facts:", *(f"- {fid}: {fact.text}" for fid, fact in trade_sheet.items()), ""]
    if feedback is not None:
        # A failure names one trade, so without this line Claude can send that trade alone.
        lines += ["Feedback from the last attempt:", feedback,
                  f"Give the whole response again with {_trade_shape(len(found))}."]
    return system, "\n".join(lines).rstrip()


def check_reasons(
    out: FinderReasonsOut, found: list[FinderTrade], snapshot: Snapshot, facts: list[dict[str, Fact]],
) -> list[str]:
    """Every rule a response breaks. An empty list means the reasons stand."""
    numbers = [reason.trade for reason in out.reasons]
    if numbers != list(range(1, len(found) + 1)):
        got = ", ".join(str(n) for n in numbers) or "none"
        return [f"the response must have {_trade_shape(len(found))}; it had trades {got}"]
    failures = []
    for reason, item, trade_sheet in zip(out.reasons, found, facts):
        # The same rules as the analysis, on the breakdowns and the facts of this trade only.
        failures += trade_prose_failures(f"trade {reason.trade}", "reason", reason.reason, snapshot, item.breakdowns,
                                         trade_sheet, reason.cited, REASON_SENTENCES)
    return failures


def write_reasons(found: list[FinderTrade], snapshot: Snapshot, call: ClaudeCall = analyzer_call) -> FinderReasons:
    """One reason per trade from one Claude call. An empty list makes no call.

    A failed check retries once with the failures as feedback. A second failure leaves each reason empty and
    flags the fallback.
    """
    if not found:
        # No trade, no reason to write, so the empty list costs no Claude call.
        return FinderReasons(reasons=[], fallback=False)
    facts = [trade_facts(number, item, snapshot) for number, item in enumerate(found, start=1)]
    out = call_with_retry(
        call, lambda feedback: build_finder_prompt(found, snapshot, facts, feedback),
        FinderReasonsOut, lambda out: check_reasons(out, found, snapshot, facts),
        subject="finder reasons", log_label="finder reasons", logger=log)
    if out is None:
        # The fairness block holds the code's reasons, so a second copy in the reason adds nothing.
        return FinderReasons(reasons=[None] * len(found), fallback=True)
    return FinderReasons(reasons=[reason.reason for reason in out.reasons], fallback=False)
