"""
The Claude call of the trade analyzer: the prompt, the call, and its checks, on the fact sheet of a proposed trade.
A response that fails a check retries once, then the code's letters and verdict stand with no analysis.
"""
import logging
import re
from typing import Literal

import anthropic
from pydantic import BaseModel, ValidationError

from cornerstone.adjusters import STEP_WORDS
from cornerstone.models import Fact
from cornerstone.names import NAME_SUFFIXES
from cornerstone.rubric import LETTERS, Breakdown, Letter, ProposedTrade, Verdict, grade, verdict
from cornerstone.sheet import NUMBER_TOKEN
from cornerstone.snapshot import Snapshot
from cornerstone.trade_facts import trade_fact_sheet
from cornerstone.verifier import (
    normalize_number, number_failures, remove_names, repeat_failure, team_mentions, whole_word,
)
from cornerstone.writer import ClaudeCall, RefusalError, WriterError, analyzer_call, load_prompt

log = logging.getLogger(__name__)

PROMPT_FILES = ("rubric.md", "analysis.md")
UNAVAILABLE = "Analysis unavailable"
MIN_SENTENCES, MAX_SENTENCES = 3, 5
# User story 29: no chart value, chart name, or tier in the prose. The chart comes from the
# Peaked in High Skool site, so every form of its name is banned. A ratio word states a ratio of
# trade values. "value" stays allowed because the breakdown reasons say "trade value"; the number
# check keeps the values themselves out.
BANNED_WORDS = ["tier", "tiers", "peaked", "skool", "pihs", "peakedinhighskool", "twice", "double", "triple"]
# "chart" is banned too, except in "depth chart", which the breakdown reasons use.
CHART_WORD = re.compile(r"(?<!\w)(?<!depth )charts?(?!\w)", re.IGNORECASE)
# The document gives a decision, not letters, so no letter grade reaches the prose a manager reads.
LETTER_GRADE = re.compile(r"\b(?:grades?|graded|grade of|an?) [A-F]\b|\b[A-F]-(?:level|grade)\b")
LETTER_WORD = re.compile(r"\bletters?\b", re.IGNORECASE)
# A failure can quote a trade value, so the log line masks every number. Claude still gets the full text.
_ANY_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


class SideAnalysis(BaseModel):
    """One side: the final letter, the reason when it differs from the code's, the analysis, and its fact IDs.

    It is both what Claude gives for a side and the final word on that side, so the fields are the same.
    """

    roster_id: int
    final_letter: Letter
    reason: str | None
    analysis: str
    cited: list[str]


class VerdictOut(BaseModel):
    """Claude's verdict for the side that asked. The code compares it with its own default."""

    choice: Literal["accept", "counter", "decline"]
    reason: str


class AnalysisOut(BaseModel):
    """The structured output of the Claude call: exactly 2 sides, one per roster in the trade, then the verdict.

    The sides come in the order of the user message, and no side repeats.
    """

    sides: list[SideAnalysis]
    verdict: VerdictOut


class Analysis(BaseModel):
    """The breakdowns and the code verdict, with the final letters, the analysis per side, and the verdict that stands."""

    breakdowns: tuple[Breakdown, Breakdown]
    code_verdict: Verdict
    sides: tuple[SideAnalysis, SideAnalysis]
    verdict: Verdict
    # True when the verdict that stands differs from the code's default.
    verdict_differs: bool
    # True when the call failed twice, so the code's letters and verdict stand.
    fallback: bool

    @property
    def standing_letters(self) -> tuple[Letter, Letter]:
        """The final letters that stand, in the order of the trade's sides."""
        # Claude can move a letter one step, and the verdict and the fairness must read the same letters.
        return (self.sides[0].final_letter, self.sides[1].final_letter)


def _names(snapshot: Snapshot, pids: list[str]) -> str:
    return ", ".join(snapshot.players[pid].name for pid in pids)


def _side_shape(breakdowns: tuple[Breakdown, Breakdown]) -> str:
    """The one shape of the sides that the check accepts, in words, with both roster IDs."""
    return f"exactly 2 sides: roster {breakdowns[0].roster_id} first, then roster {breakdowns[1].roster_id}, each once"


def build_analysis_prompt(
    trade: ProposedTrade, snapshot: Snapshot, breakdowns: tuple[Breakdown, Breakdown], code_verdict: Verdict,
    facts: dict[str, Fact], feedback: str | None,
) -> tuple[str, str]:
    system = "\n\n".join(load_prompt(name) for name in PROMPT_FILES)
    lines = []
    for side, other, breakdown in ((trade.sides[0], trade.sides[1], breakdowns[0]),
                                   (trade.sides[1], trade.sides[0], breakdowns[1])):
        asked = ", the side that asked" if side.roster_id == trade.asker else ""
        lines += [
            f"Side: roster {side.roster_id}, {snapshot.teams[side.roster_id].name}{asked}",
            f"Gives: {_names(snapshot, side.gives)}",
            f"Gets: {_names(snapshot, other.gives)}",
            f"Start letter: {breakdown.start_letter}. {breakdown.reason}",
            *(f"{a.name.capitalize()}: {a.lean if a.lean is not None else STEP_WORDS[a.step]}. {a.reason}"
              for a in breakdown.adjusters),
            f"Final letter: {breakdown.final_letter}",
            "",
        ]
    lines += [
        f"Code's default verdict for {snapshot.teams[trade.asker].name}: {code_verdict.choice}. {code_verdict.reason}",
        "",
        "Facts:",
        *(f"- {fid}: {fact.text}" for fid, fact in facts.items()),
    ]
    if feedback is not None:
        # A failure names one side, so without this line Claude can send that side alone or twice.
        lines += ["", "Feedback from the last attempt:", feedback,
                  f"Give the whole response again with {_side_shape(breakdowns)}, and the verdict."]
    return system, "\n".join(lines)


# A period after a title or "vs" ends no sentence. A period after a name suffix before a lowercase word ends
# no sentence. A period in a run of initials such as "A.J." ends no sentence.
# Claude writes the short form "St. Brown". The code removes the full name first, so the short form stays.
# A lone capital still ends a sentence, because "the grade is a B." is a real end.
_TITLES = ("St", "Mr", "Dr", "vs")
# NAME_SUFFIXES in the names module is the one list of name suffixes. Only a suffix with a period matters here.
_DOTTED_SUFFIXES = sorted(suffix.removesuffix(".") for suffix in NAME_SUFFIXES if suffix.endswith("."))
# The titles and suffixes match in any case. The word after a suffix must be lowercase, so that part has no flag.
_NOT_AN_END = re.compile(
    rf"(?<!\w)(?:(?i:{'|'.join(_TITLES)})|(?i:{'|'.join(_DOTTED_SUFFIXES)})(?=\.\s+[a-z])|(?:[A-Z]\.)+[A-Z])\."
)


def _sentences(text: str) -> int:
    # A period inside a decimal is not followed by a space, so it ends no sentence.
    text = _NOT_AN_END.sub(lambda match: match.group()[:-1], text)
    return len(re.findall(r"[.!?]+(?=\s|$)", text.strip()))


def _prose_failures(label: str, text: str, allowed: set[str], allowed_text: str, names: list[str]) -> list[str]:
    """The verifier's number rule and the banned words, on one piece of prose."""
    # Digits inside a name, such as a team called "Pukancun on 3", are not numbers.
    bare = remove_names(text, names)
    failures = [f"{label}: {message}" for message in number_failures(bare, allowed, allowed_text)]
    failures += [f"{label}: the word '{word}' is not allowed" for word in BANNED_WORDS if whole_word(word, bare)]
    failures += [f"{label}: the word '{match.group()}' is not allowed" for match in CHART_WORD.finditer(bare)]
    return failures


def _letter_failures(label: str, text: str) -> list[str]:
    """The letter rule on one piece of prose: no letter grade and no word "letter"."""
    failures = [f"{label}: '{match.group()}' names a letter grade" for match in LETTER_GRADE.finditer(text)]
    failures += [f"{label}: the word '{match.group()}' is not allowed" for match in LETTER_WORD.finditer(text)]
    return failures


def _breakdown_text(breakdowns: tuple[Breakdown, Breakdown]) -> str:
    """The reasons of both breakdowns. The prompt shows them, so their numbers may appear in the prose."""
    return " ".join(reason for b in breakdowns for reason in (b.reason, *(a.reason for a in b.adjusters)))


def _allowed(facts: dict[str, Fact], fids: list[str], breakdown_text: str) -> set[str]:
    # A trade value never reaches the prose, even from a cited value fact.
    cited = {normalize_number(x) for fid in fids if not fid.endswith(".value") for x in facts[fid].numbers}
    return cited | {normalize_number(token) for token in NUMBER_TOKEN.findall(breakdown_text)}


def check_response(
    out: AnalysisOut, snapshot: Snapshot, breakdowns: tuple[Breakdown, Breakdown], facts: dict[str, Fact],
) -> list[str]:
    """Every rule a response breaks. An empty list means the response stands."""
    failures = []
    by_roster = {s.roster_id: s for s in out.sides}
    if sorted(by_roster) != sorted(b.roster_id for b in breakdowns) or len(out.sides) != 2:
        got_rosters = ", ".join(str(s.roster_id) for s in out.sides) or "none"
        return [f"the response must have {_side_shape(breakdowns)}; it had rosters {got_rosters}"]
    names = [*(t.name for t in snapshot.teams.values()), *(p.name for p in snapshot.players.values())]
    breakdown_text = _breakdown_text(breakdowns)
    trade_teams = [snapshot.teams[b.roster_id].name for b in breakdowns]
    for breakdown in breakdowns:
        side = by_roster[breakdown.roster_id]
        label = f"roster {side.roster_id}"
        steps = abs(LETTERS.index(side.final_letter) - LETTERS.index(breakdown.final_letter))
        if steps > 1:
            failures.append(f"{label}: final letter {side.final_letter} is {steps} steps from the code's "
                            f"{breakdown.final_letter}; one step is the most")
        if steps == 1 and not (side.reason or "").strip():
            failures.append(f"{label}: the final letter differs from the code's, so it needs a reason")
        count = _sentences(remove_names(side.analysis, names))
        if not MIN_SENTENCES <= count <= MAX_SENTENCES:
            failures.append(f"{label}: the analysis has {count} sentences; the range is "
                            f"{MIN_SENTENCES} to {MAX_SENTENCES}")
        unknown = [fid for fid in side.cited if fid not in facts]
        failures += [f"{label}: fact ID {fid} is not in the facts" for fid in unknown]
        if not side.cited:
            failures.append(f"{label}: the analysis cites no fact")
        cited = [fid for fid in side.cited if fid in facts]
        allowed = _allowed(facts, cited, breakdown_text)
        allowed_text = " ".join([*(facts[fid].text for fid in cited), breakdown_text])
        failures += _prose_failures(f"{label} analysis", side.analysis, allowed, allowed_text, names)
        failures += _letter_failures(f"{label} analysis", side.analysis)
        # The analysis names each team in the trade once, then says "this side", "they", or the player names.
        failures += [repeat_failure(f"{label} analysis", team, mentions) for team in trade_teams
                     if (mentions := team_mentions(team, side.analysis)) > 1]
        if side.reason:
            failures += _prose_failures(f"{label} reason", side.reason, allowed, allowed_text, names)
    # The verdict reason cites no fact of its own, so any fact the two analyses cite may back its numbers.
    every = [fid for s in out.sides for fid in s.cited if fid in facts]
    failures += _prose_failures("verdict reason", out.verdict.reason, _allowed(facts, every, breakdown_text),
                                " ".join([*(facts[fid].text for fid in every), breakdown_text]), names)
    failures += _letter_failures("verdict reason", out.verdict.reason)
    return failures


def _accepted(out: AnalysisOut, breakdowns: tuple[Breakdown, Breakdown], code_verdict: Verdict) -> Analysis:
    sides = []
    for breakdown in breakdowns:
        side = next(s for s in out.sides if s.roster_id == breakdown.roster_id)
        differs = side.final_letter != breakdown.final_letter
        sides.append(side.model_copy(update={"reason": side.reason if differs else None}))
    chosen = Verdict(choice=out.verdict.choice, reason=out.verdict.reason)
    # The code compares the choices itself, so Claude gives no flag that could mislabel the verdict.
    return Analysis(breakdowns=breakdowns, code_verdict=code_verdict, sides=tuple(sides), verdict=chosen,
                    verdict_differs=chosen.choice != code_verdict.choice, fallback=False)


def _fallback(breakdowns: tuple[Breakdown, Breakdown], code_verdict: Verdict) -> Analysis:
    """The code's letters and verdict with "Analysis unavailable" per side. The shape lives here once."""
    sides = tuple(SideAnalysis(roster_id=b.roster_id, final_letter=b.final_letter, reason=None,
                               analysis=UNAVAILABLE, cited=[]) for b in breakdowns)
    return Analysis(breakdowns=breakdowns, code_verdict=code_verdict, sides=sides, verdict=code_verdict,
                    verdict_differs=False, fallback=True)


def code_only(trade: ProposedTrade, snapshot: Snapshot) -> Analysis:
    """The fallback for a trade with no Claude call. The API uses it when a test or a caller wants no call."""
    breakdowns = grade(trade, snapshot)
    return _fallback(breakdowns, verdict(trade, breakdowns))


def analyze(trade: ProposedTrade, snapshot: Snapshot, call: ClaudeCall = analyzer_call) -> Analysis:
    """Grade the trade, then ask Claude for the final letters, the analysis, and the verdict.

    A failed check retries once with the failures as feedback. A second failure keeps the code's letters
    and verdict, with "Analysis unavailable" per side. It raises TradeInputError on a bad trade.
    """
    breakdowns = grade(trade, snapshot)
    code_verdict = verdict(trade, breakdowns)
    facts = trade_fact_sheet(trade, snapshot)
    feedback: str | None = None
    for attempt in (1, 2):
        system, user = build_analysis_prompt(trade, snapshot, breakdowns, code_verdict, facts, feedback)
        try:
            out = call(system, user, AnalysisOut)
            # Any call, real or injected, can come back empty. That is a failed attempt.
            if out is None:
                raise WriterError("no parsed output for the trade analysis")
            failures = check_response(out, snapshot, breakdowns, facts)
            if failures:
                raise WriterError("; ".join(failures))
        except (RefusalError, WriterError, ValidationError, anthropic.AnthropicError) as err:
            # A bad response is a failed attempt, not a crash of the command or the route.
            log.warning("analysis attempt %d failed: %s", attempt, _ANY_NUMBER.sub("#", str(err)))
            feedback = str(err)
            continue
        return _accepted(out, breakdowns, code_verdict)
    return _fallback(breakdowns, code_verdict)
