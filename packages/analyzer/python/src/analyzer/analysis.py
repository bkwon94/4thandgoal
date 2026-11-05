"""
The Claude call of the trade analyzer: the prompt, the call, and its checks, on the fact sheet of a proposed trade.
A response that fails a check retries once, then the code's letters and verdict stand with no bullets.
"""
import logging
import re
from typing import Literal

from pydantic import BaseModel

from analyzer import RULE_PROMPTS
from analyzer.adjusters import STEP_WORDS, UPSIDE
from analyzer.rubric import LETTERS, Breakdown, Letter, ProposedTrade, Verdict, grade, verdict
from analyzer.trade_facts import trade_fact_sheet
from facts.names import NAME_SUFFIXES
from facts.tokens import NUMBER_TOKEN
from facts.verifier import (
    normalize_number,
    number_failures,
    remove_names,
    repeat_failure,
    team_mentions,
    whole_word,
)
from facts.writer import ClaudeCall, analyzer_call, call_with_retry, load_prompt
from league.models import Fact
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

PROMPT_FILES = ("rubric.md", "analysis.md")
# A manager reads 2 or 3 short bullets for each side in seconds, where a paragraph takes minutes.
MIN_BULLETS, MAX_BULLETS = 2, 3
# User story 29: no chart value, chart name, or tier in the prose. The chart comes from the
# Peaked in High Skool site, so every form of its name is banned. A ratio word states a ratio of
# trade values. "value" stays allowed because the breakdown reasons say "trade value"; the number
# check keeps the values themselves out.
# Roster fit says "position rank", "the line", and "hole". GLOSSARY.md bans "replacement" and "floor" for them, so
# a reader meets one word per idea. "gap" stays allowed, because the expected gap adjuster owns it.
BANNED_WORDS = ["tier", "tiers", "peaked", "skool", "pihs", "peakedinhighskool", "twice", "double", "triple",
                "replacement", "replacements", "floor", "floors"]
# "chart" is banned too, except in "depth chart", which the breakdown reasons use.
CHART_WORD = re.compile(r"(?<!\w)(?<!depth )charts?(?!\w)", re.IGNORECASE)
# The document gives a decision, not letters, so no letter grade reaches the prose a manager reads.
LETTER_GRADE = re.compile(r"\b(?:grades?|graded|grade of|an?) [A-F]\b|\b[A-F]-(?:level|grade)\b")
LETTER_WORD = re.compile(r"\bletters?\b", re.IGNORECASE)
# A side's prose may claim upside only when the upside adjuster credits a player of that side. GLOSSARY.md, "Upside".
UPSIDE_WORDS = re.compile(r"\b(?:upside|return bets?|opportunit(?:y|ies))\b", re.IGNORECASE)


class SideAnalysis(BaseModel):
    """One side: the final letter, the reason when it differs from the code's, the bullets, and their fact IDs.

    It is both what Claude gives for a side and the final word on that side, so the fields are the same.
    """

    roster_id: int
    final_letter: Letter
    reason: str | None
    # Each bullet is one sentence that makes one claim. The fallback has none.
    bullets: list[str]
    cited: list[str]


class VerdictOut(BaseModel):
    """Claude's verdict for the side that asked. The code compares it with its own default."""

    choice: Literal["accept", "counter", "decline"]
    reason: str


class AnalysisOut(BaseModel):
    """The structured output of the Claude call: exactly one side per roster in the trade, then the verdict.

    The sides come in the order of the user message, and no side repeats.
    """

    sides: list[SideAnalysis]
    verdict: VerdictOut


class Analysis(BaseModel):
    """The breakdowns and the code verdict, with the final letters, the bullets per side,
    and the verdict that stands."""

    # In the order of the trade's sides, one per side, two to four in all.
    breakdowns: tuple[Breakdown, ...]
    code_verdict: Verdict
    sides: tuple[SideAnalysis, ...]
    verdict: Verdict
    # True when the verdict that stands differs from the code's default.
    verdict_differs: bool
    # True when the call failed twice, so the code's letters and verdict stand.
    fallback: bool

    @property
    def standing_letters(self) -> tuple[Letter, ...]:
        """The final letters that stand, in the order of the trade's sides."""
        # Claude can move a letter one step, and the verdict and the fairness must read the same letters.
        return tuple(side.final_letter for side in self.sides)


def _side_shape(breakdowns: tuple[Breakdown, ...]) -> str:
    """The one shape of the sides that the check accepts, in words, with every roster ID in order."""
    first, *rest = (b.roster_id for b in breakdowns)
    then = "".join(f", then roster {roster_id}" for roster_id in rest)
    return f"exactly {len(breakdowns)} sides: roster {first} first{then}, each once"


def trade_side_lines(
    trade: ProposedTrade, snapshot: Snapshot, breakdowns: tuple[Breakdown, ...],
) -> tuple[list[str], ...]:
    """The prompt lines of each side of a trade: the team, the players it gives and gets, and its breakdown."""
    # The analysis prompt and the finder prompt both show a side this way, so Claude reads one layout.
    # Each player names the team he goes to or comes from, so a trade of three or more sides reads plainly.
    team = {side.roster_id: snapshot.teams[side.roster_id].name for side in trade.sides}
    givers = trade.givers
    blocks = []
    for side, breakdown in zip(trade.sides, breakdowns):
        asked = ", the side that asked" if side.roster_id == trade.asker else ""
        gives = ", ".join(f"{snapshot.players[p.player_id].name} to {team[p.to]}" for p in side.gives)
        gets = ", ".join(f"{snapshot.players[pid].name} from {team[givers[pid]]}"
                         for pid in trade.gets(side.roster_id))
        blocks.append([
            f"Side: roster {side.roster_id}, {team[side.roster_id]}{asked}",
            f"Gives: {gives}",
            f"Gets: {gets}",
            f"Start letter: {breakdown.start_letter}. {breakdown.reason}",
            *(f"{a.name.capitalize()}: {a.lean if a.lean is not None else STEP_WORDS[a.step]}. {a.reason}"
              for a in breakdown.adjusters),
            f"Final letter: {breakdown.final_letter}",
        ])
    return tuple(blocks)


def build_analysis_prompt(
    trade: ProposedTrade, snapshot: Snapshot, breakdowns: tuple[Breakdown, ...], code_verdict: Verdict,
    facts: dict[str, Fact], feedback: str | None,
) -> tuple[str, str]:
    # The snapshot carries the client, so the prompts come from the folder that the client names.
    system = "\n\n".join(load_prompt(snapshot.client.voice_dir, name, RULE_PROMPTS) for name in PROMPT_FILES)
    lines = []
    for block in trade_side_lines(trade, snapshot, breakdowns):
        lines += [*block, ""]
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


def _upside_failures(label: str, text: str, breakdown: Breakdown) -> list[str]:
    """The upside rule on one piece of a side's prose: no upside claim when the upside adjuster credits no one."""
    if any(a.name == UPSIDE and a.step > 0 for a in breakdown.adjusters):
        return []
    return [f"{label}: '{match.group()}' claims upside, but the upside adjuster credits no player of this side"
            for match in UPSIDE_WORDS.finditer(text)]


def _breakdown_text(breakdowns: tuple[Breakdown, ...]) -> str:
    """The reasons of every breakdown. The prompt shows them, so their numbers may appear in the prose."""
    return " ".join(reason for b in breakdowns for reason in (b.reason, *(a.reason for a in b.adjusters)))


def _allowed(facts: dict[str, Fact], fids: list[str], breakdown_text: str) -> set[str]:
    # A trade value never reaches the prose, even from a cited value fact.
    cited = {normalize_number(x) for fid in fids if not fid.endswith(".value") for x in facts[fid].numbers}
    return cited | {normalize_number(token) for token in NUMBER_TOKEN.findall(breakdown_text)}


def _allowed_text(facts: dict[str, Fact], fids: list[str], breakdown_text: str) -> str:
    """The texts of the cited facts and the breakdown, where a number in the prose must appear."""
    return " ".join([*(facts[fid].text for fid in fids), breakdown_text])


def _names_of_everyone(snapshot: Snapshot) -> list[str]:
    """Every team name and player name, so a digit or a period inside a name counts as neither."""
    return [*(t.name for t in snapshot.teams.values()), *(p.name for p in snapshot.players.values())]


def trade_prose_failures(
    owner: str, kind: str, text: str, snapshot: Snapshot, breakdowns: tuple[Breakdown, ...],
    facts: dict[str, Fact], cited: list[str], sentences: tuple[int, int],
) -> list[str]:
    """The prose rules of the analysis on one piece of prose about a trade, such as a finder reason.

    `owner` names who wrote it, such as "roster 2", and `kind` names the prose, such as "reason". The
    sentence count must be in the `sentences` range. The prose cites at least one fact, every number comes
    from a cited fact or the breakdown, and each team in the trade appears at most once.
    """
    label = f"{owner} {kind}"
    names = _names_of_everyone(snapshot)
    failures = []
    low, high = sentences
    count = _sentences(remove_names(text, names))
    if not low <= count <= high:
        need = f"it needs exactly {low}" if low == high else f"the range is {low} to {high}"
        failures.append(f"{owner}: the {kind} has {count} sentences; {need}")
    failures += [f"{owner}: fact ID {fid} is not in the facts" for fid in cited if fid not in facts]
    if not cited:
        failures.append(f"{owner}: the {kind} cites no fact")
    known = [fid for fid in cited if fid in facts]
    breakdown_text = _breakdown_text(breakdowns)
    failures += _prose_failures(label, text, _allowed(facts, known, breakdown_text),
                                _allowed_text(facts, known, breakdown_text), names)
    failures += _letter_failures(label, text)
    # The prose names each team in the trade once, then says "this side", "they", or the player names.
    trade_teams = [snapshot.teams[b.roster_id].name for b in breakdowns]
    failures += [repeat_failure(label, team, mentions) for team in trade_teams
                 if (mentions := team_mentions(team, text)) > 1]
    return failures


def _bullet_failures(
    label: str, bullets: list[str], snapshot: Snapshot, breakdowns: tuple[Breakdown, ...], breakdown: Breakdown,
    facts: dict[str, Fact], cited: list[str],
) -> list[str]:
    """The prose rules of the analysis on the bullets of one side, with each rule of one piece of prose on each bullet.

    The side has 2 or 3 bullets of one sentence each. The bullets together cite at least one fact and name each team
    in the trade at most once, because they are one read of the side.
    """
    failures = []
    if not MIN_BULLETS <= len(bullets) <= MAX_BULLETS:
        failures.append(f"{label}: it has {len(bullets)} bullets; the range is {MIN_BULLETS} to {MAX_BULLETS}")
    failures += [f"{label}: fact ID {fid} is not in the facts" for fid in cited if fid not in facts]
    if not cited:
        failures.append(f"{label}: the bullets cite no fact")
    names = _names_of_everyone(snapshot)
    known = [fid for fid in cited if fid in facts]
    breakdown_text = _breakdown_text(breakdowns)
    allowed, allowed_text = _allowed(facts, known, breakdown_text), _allowed_text(facts, known, breakdown_text)
    for number, bullet in enumerate(bullets, start=1):
        bullet_label = f"{label} bullet {number}"
        count = _sentences(remove_names(bullet, names))
        if count != 1:
            failures.append(f"{label}: bullet {number} has {count} sentences; it needs exactly 1")
        failures += _prose_failures(bullet_label, bullet, allowed, allowed_text, names)
        failures += _letter_failures(bullet_label, bullet)
        failures += _upside_failures(bullet_label, bullet, breakdown)
    text = " ".join(bullets)
    trade_teams = [snapshot.teams[b.roster_id].name for b in breakdowns]
    failures += [repeat_failure(f"{label} bullets", team, mentions) for team in trade_teams
                 if (mentions := team_mentions(team, text)) > 1]
    return failures


def check_response(
    out: AnalysisOut, snapshot: Snapshot, breakdowns: tuple[Breakdown, ...], facts: dict[str, Fact],
) -> list[str]:
    """Every rule a response breaks. An empty list means the response stands."""
    failures = []
    by_roster = {s.roster_id: s for s in out.sides}
    # The sides must come in the order of the user message, each once, so a list in another order fails too.
    if [s.roster_id for s in out.sides] != [b.roster_id for b in breakdowns]:
        got_rosters = ", ".join(str(s.roster_id) for s in out.sides) or "none"
        return [f"the response must have {_side_shape(breakdowns)}; it had rosters {got_rosters}"]
    names = _names_of_everyone(snapshot)
    breakdown_text = _breakdown_text(breakdowns)
    for breakdown in breakdowns:
        side = by_roster[breakdown.roster_id]
        label = f"roster {side.roster_id}"
        steps = abs(LETTERS.index(side.final_letter) - LETTERS.index(breakdown.final_letter))
        if steps > 1:
            failures.append(f"{label}: final letter {side.final_letter} is {steps} steps from the code's "
                            f"{breakdown.final_letter}; one step is the most")
        if steps == 1 and not (side.reason or "").strip():
            failures.append(f"{label}: the final letter differs from the code's, so it needs a reason")
        failures += _bullet_failures(label, side.bullets, snapshot, breakdowns, breakdown, facts, side.cited)
        if side.reason:
            cited = [fid for fid in side.cited if fid in facts]
            failures += _prose_failures(f"{label} reason", side.reason, _allowed(facts, cited, breakdown_text),
                                        _allowed_text(facts, cited, breakdown_text), names)
            failures += _upside_failures(f"{label} reason", side.reason, breakdown)
    # The verdict reason cites no fact of its own, so any fact the bullets cite may back its numbers.
    every = [fid for s in out.sides for fid in s.cited if fid in facts]
    failures += _prose_failures("verdict reason", out.verdict.reason, _allowed(facts, every, breakdown_text),
                                _allowed_text(facts, every, breakdown_text), names)
    failures += _letter_failures("verdict reason", out.verdict.reason)
    return failures


def _accepted(out: AnalysisOut, breakdowns: tuple[Breakdown, ...], code_verdict: Verdict) -> Analysis:
    sides = []
    for breakdown in breakdowns:
        side = next(s for s in out.sides if s.roster_id == breakdown.roster_id)
        differs = side.final_letter != breakdown.final_letter
        sides.append(side.model_copy(update={"reason": side.reason if differs else None}))
    chosen = Verdict(choice=out.verdict.choice, reason=out.verdict.reason)
    # The code compares the choices itself, so Claude gives no flag that could mislabel the verdict.
    return Analysis(breakdowns=breakdowns, code_verdict=code_verdict, sides=tuple(sides), verdict=chosen,
                    verdict_differs=chosen.choice != code_verdict.choice, fallback=False)


def _fallback(breakdowns: tuple[Breakdown, ...], code_verdict: Verdict) -> Analysis:
    """The code's letters and verdict with no bullets per side. The shape lives here once."""
    sides = tuple(SideAnalysis(roster_id=b.roster_id, final_letter=b.final_letter, reason=None,
                               bullets=[], cited=[]) for b in breakdowns)
    return Analysis(breakdowns=breakdowns, code_verdict=code_verdict, sides=sides, verdict=code_verdict,
                    verdict_differs=False, fallback=True)


def code_only(trade: ProposedTrade, snapshot: Snapshot) -> Analysis:
    """The fallback for a trade with no Claude call. The API uses it when a test or a caller wants no call."""
    breakdowns = grade(trade, snapshot)
    return _fallback(breakdowns, verdict(trade, breakdowns))


def analyze(trade: ProposedTrade, snapshot: Snapshot, call: ClaudeCall = analyzer_call) -> Analysis:
    """Grade the trade, then ask Claude for the final letters, the bullets, and the verdict.

    A failed check retries once with the failures as feedback. A second failure keeps the code's letters
    and verdict, with no bullets per side. It raises TradeInputError on a bad trade.
    """
    breakdowns = grade(trade, snapshot)
    code_verdict = verdict(trade, breakdowns)
    facts = trade_fact_sheet(trade, snapshot)
    out = call_with_retry(
        call, lambda feedback: build_analysis_prompt(trade, snapshot, breakdowns, code_verdict, facts, feedback),
        AnalysisOut, lambda out: check_response(out, snapshot, breakdowns, facts),
        subject="trade analysis", log_label="analysis", logger=log)
    if out is None:
        return _fallback(breakdowns, code_verdict)
    return _accepted(out, breakdowns, code_verdict)
