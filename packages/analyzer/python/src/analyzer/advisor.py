"""
The read of one trade by the Advisor: the sheet of facts and Jev answers, the Claude call, and the guards on its words.
A read that fails a guard retries once. After two failed calls, AdvisorFailed stands, and no code answer takes its place.
"""
import logging
import re
from typing import Literal

from pydantic import BaseModel

from analyzer import RULE_PROMPTS
from analyzer.rubric import Fairness, FairnessSide, ProposedTrade
from analyzer.trade_facts import trade_fact_sheet
from analyzer.trade_jev import trade_jev_facts
from facts.tokens import NUMBER_TOKEN
from facts.verifier import normalize_number, remove_names
from facts.writer import ClaudeCall, analyzer_call, call_with_retry, load_prompt
from league.jev_port import Jev
from league.models import Fact
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

PROMPT_FILE = "advisor.md"
Lean = Literal["Send it", "Lean yes", "Gut call", "Lean no", "Pass"]
Mark = Literal["for", "against", "even"]
MIN_BULLETS, MAX_BULLETS = 3, 5
# The inner words of GLOSSARY.md that no Bullet, no case, and no gains may hold, plus "rival", which the copy never says.
INNER_WORDS = ["trade value", "highest-value", "best lineup", "the line", "hole", "return bet", "one step", "no step",
               "takes RB", "takes WR", "takes TE", "takes QB", "sits on the bench", "rival"]
# A word matches whole and in any case, plus its plural, so "hole" never matches "whole" and "the line" never matches
# "the lineup". A "takes" word matches before a slot number too, as in "takes RB1".
_WHOLE_END = r"s?(?![\w-])"
_INNER = {word: re.compile(r"(?<![\w-])" + re.escape(word) + ("" if word.startswith("takes ") else _WHOLE_END),
                           re.IGNORECASE) for word in INNER_WORDS}
# The first sentence of the case holds the condition the call rests on (AT-18).
CONDITION = re.compile(r"\b(?:if|as long as)\b", re.IGNORECASE)
FIRST_SENTENCE = re.compile(r"^.*?[.!?](?=\s|$)", re.DOTALL)
# The words of the scoring of a client, from the points key of its League settings.
SCORING = {"pts_ppr": "full PPR", "pts_half_ppr": "half PPR", "pts_std": "standard scoring"}
# A hyphen between a letter and a digit joins a word to a number, as in "top-36", so it is no minus sign.
_JOINING_HYPHEN = re.compile(r"(?<=[A-Za-z])-(?=\d)")
# A trade value never reaches the prose, even from a cited value fact, so the numbers of a value fact never count.
VALUE_SUFFIX = ".value"


class Bullet(BaseModel):
    """One claim of the Advisor about one side, with its Mark and the one fact it rests on."""

    text: str
    mark: Mark
    fact_id: str


class AdvisorSide(BaseModel):
    """What the Advisor gives for one side: one sentence of what it gains, and 3 to 5 Bullets."""

    roster_id: int
    gains: str
    bullets: list[Bullet]


class AdvisorOut(BaseModel):
    """The structured output of the Advisor call. The shape came from prototype 04."""

    lean: Lean
    case: str
    fairness: Literal["fair", "lopsided"]
    # The roster id of the side that gives more when the trade is lopsided, else null.
    gives_more: int | None
    sides: list[AdvisorSide]


class ReadBullet(BaseModel):
    """One Bullet as the page shows it: the claim, the Mark, and the id and text of its fact, so a tap opens the fact."""

    text: str
    mark: Mark
    fact_id: str
    fact_text: str


class ReadSide(BaseModel):
    roster_id: int
    bullets: list[ReadBullet]


class TradeRead(BaseModel):
    """The read of one trade: the Lean, the Case, the fairness for every side, and the Bullets per side."""

    lean: Lean
    case: str
    fairness: Fairness
    # In the order of the trade's sides.
    sides: tuple[ReadSide, ...]


class AdvisorFailed(Exception):
    """The Advisor gave no read that passed the guards in two calls. The API answers with an honest error."""


def advisor_sheet(trade: ProposedTrade, snapshot: Snapshot, jev: Jev) -> dict[str, Fact]:
    """The facts the Advisor reads by id: the facts of the trade, then the Jev answers of the trade."""
    return {**trade_fact_sheet(trade, snapshot), **trade_jev_facts(trade, snapshot, jev)}


def _league_line(snapshot: Snapshot) -> str:
    starters = [slot for slot in snapshot.roster_positions if slot not in ("BN", "IR", "TAXI")]
    scoring = SCORING.get(snapshot.client.settings.points_key, "its own scoring")
    return f"The league: {len(snapshot.teams)} teams, {scoring}. Each team starts {', '.join(starters)}."


def build_advisor_prompt(
    trade: ProposedTrade, snapshot: Snapshot, facts: dict[str, Fact], feedback: str | None,
) -> tuple[str, str]:
    """The system prompt and the user message of the Advisor call.

    The system prompt is the same for every trade of a client, so the cache of its prefix holds across presses.
    """
    system = "\n\n".join([load_prompt(snapshot.client.voice_dir, PROMPT_FILE, RULE_PROMPTS), _league_line(snapshot)])
    team = {side.roster_id: snapshot.teams[side.roster_id].name for side in trade.sides}
    givers = trade.givers
    lines = []
    for side in trade.sides:
        asks = ", the side that asks" if side.roster_id == trade.asker else ""
        gives = ", ".join(f"{snapshot.players[p.player_id].name} to {team[p.to]}" for p in side.gives)
        gets = ", ".join(f"{snapshot.players[pid].name} from {team[givers[pid]]}" for pid in trade.gets(side.roster_id))
        lines += [f"Side: roster {side.roster_id}, {team[side.roster_id]}{asks}", f"Gives: {gives}", f"Gets: {gets}",
                  ""]
    lines += ["Facts:", *(f"- {fid}: {f.text}" for fid, f in facts.items())]
    if feedback is not None:
        order = ", then ".join(f"roster {side.roster_id}" for side in trade.sides)
        lines += ["", "Feedback from the last attempt:", feedback,
                  f"Give the whole response again, with the sides in this order: {order}."]
    return system, "\n".join(lines)


def _names_in(text: str, names: list[str]) -> list[str]:
    return [name for name in names if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", text)]


class _Guard:
    """The guards of one read: the names and numbers each text may hold, from the facts it cites."""

    def __init__(self, trade: ProposedTrade, snapshot: Snapshot, facts: dict[str, Fact]) -> None:
        self.facts = facts
        self.trade_names = {snapshot.players[pid].name for pid in trade.player_ids} | {
            snapshot.teams[side.roster_id].name for side in trade.sides}
        # Longest first, so a long name goes before a short name inside it.
        self.names = sorted({p.name for p in snapshot.players.values()} | {t.name for t in snapshot.teams.values()},
                            key=len, reverse=True)

    def text_failures(self, label: str, text: str, cited: list[str]) -> list[str]:
        """The inner words, the names, and the numbers of one text against the facts it cites."""
        failures = [f"{label}: the words '{word}' are not allowed" for word, pattern in _INNER.items()
                    if pattern.search(text)]
        found = _names_in(text, self.names)
        allowed = set(self.trade_names)
        for fid in cited:
            allowed |= set(self.facts[fid].players) | set(self.facts[fid].teams)
        failures += [f"{label}: the name {name} is not in the trade or in a cited fact" for name in found
                     if name not in allowed and not any(name in other for other in found if other != name)]
        # The check reads digits only, as prototype 04 did. A count in words, such as "two starters for one", reads
        # the trade itself, and the playbook speaks of "two good ones".
        numbers = {normalize_number(n) for fid in cited if not fid.endswith(VALUE_SUFFIX)
                   for n in self.facts[fid].numbers}
        failures += [f"{label}: number {token} is not in the cited facts"
                     for token in NUMBER_TOKEN.findall(_JOINING_HYPHEN.sub(" ", remove_names(text, found)))
                     if normalize_number(token) not in numbers]
        return failures


def check_read(out: AdvisorOut, trade: ProposedTrade, snapshot: Snapshot, facts: dict[str, Fact]) -> list[str]:
    """Every guard a read breaks. An empty list means the read stands."""
    rosters = [side.roster_id for side in trade.sides]
    if [side.roster_id for side in out.sides] != rosters:
        got = ", ".join(str(side.roster_id) for side in out.sides) or "none"
        return [f"the read must have one side per roster in this order: {rosters}; it had rosters {got}"]
    failures = []
    first = FIRST_SENTENCE.match(out.case.strip())
    if first is None or not CONDITION.search(first.group()):
        failures.append("case: the first sentence must hold the condition, with 'if' or 'as long as'")
    if out.fairness == "lopsided" and out.gives_more not in rosters:
        failures.append(f"fairness: a lopsided read needs gives_more, one of the rosters {rosters}")
    guard = _Guard(trade, snapshot, facts)
    every: list[str] = []
    for side in out.sides:
        label = f"roster {side.roster_id}"
        if not MIN_BULLETS <= len(side.bullets) <= MAX_BULLETS:
            failures.append(f"{label}: it has {len(side.bullets)} bullets; the range is {MIN_BULLETS} to {MAX_BULLETS}")
        for number, bullet in enumerate(side.bullets, start=1):
            where = f"{label} bullet {number}"
            if bullet.fact_id not in facts:
                failures.append(f"{where}: fact ID {bullet.fact_id} is not on the sheet")
                continue
            every.append(bullet.fact_id)
            failures += guard.text_failures(where, bullet.text, [bullet.fact_id])
    for side in out.sides:
        failures += guard.text_failures(f"roster {side.roster_id} gains", side.gains, every)
    failures += guard.text_failures("case", out.case, every)
    return failures


def _read(out: AdvisorOut, facts: dict[str, Fact]) -> TradeRead:
    """The read of a checked output, with the text of each cited fact. A fair read names no side that gives more."""
    fairness = Fairness(state=out.fairness, gives_more=out.gives_more if out.fairness == "lopsided" else None,
                        sides=tuple(FairnessSide(roster_id=side.roster_id, reason=side.gains) for side in out.sides))
    sides = tuple(ReadSide(roster_id=side.roster_id, bullets=[
        ReadBullet(text=b.text, mark=b.mark, fact_id=b.fact_id, fact_text=facts[b.fact_id].text)
        for b in side.bullets]) for side in out.sides)
    return TradeRead(lean=out.lean, case=out.case, fairness=fairness, sides=sides)


def read_trade_on_sheet(
    trade: ProposedTrade, snapshot: Snapshot, facts: dict[str, Fact], *, call: ClaudeCall = analyzer_call,
) -> TradeRead:
    """The read of the Advisor on the trade, from a sheet that the caller built. A failed guard retries once.

    A caller that saves the sheet builds it with advisor_sheet, so the saved sheet is the one the Advisor read.
    Raises AdvisorFailed after two failed calls, a failed API call included.
    """
    out = call_with_retry(
        call, lambda feedback: build_advisor_prompt(trade, snapshot, facts, feedback), AdvisorOut,
        lambda out: check_read(out, trade, snapshot, facts), subject="trade read", log_label="advisor", logger=log)
    if out is None:
        raise AdvisorFailed("The Advisor gave no read that passed the guards in two calls.")
    return _read(out, facts)


def read_trade(trade: ProposedTrade, snapshot: Snapshot, *, jev: Jev, call: ClaudeCall = analyzer_call) -> TradeRead:
    """The read of the Advisor on the trade. A failed guard retries once with the failures as feedback.

    Raises AdvisorFailed after two failed calls, a failed API call included.
    """
    return read_trade_on_sheet(trade, snapshot, advisor_sheet(trade, snapshot, jev), call=call)
