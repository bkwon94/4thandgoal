"""
The Claude call of the trade analyzer: the fact sheet of a proposed trade, the prompt, the call, and its checks.
A response that fails a check retries once, then the code's letters and verdict stand with no analysis.
"""
import logging
import re
from importlib import resources
from typing import Literal

import anthropic
from pydantic import BaseModel, ValidationError

from cornerstone.adjusters import team_race
from cornerstone.history import points_per_game, red_zone, season_rank, snap_share, target_share
from cornerstone.models import Fact, UsageShare
from cornerstone.rubric import LETTERS, Breakdown, Letter, ProposedTrade, Verdict, grade, verdict
from cornerstone.sheet import NUMBER_TOKEN, Nums
from cornerstone.snapshot import Snapshot
from cornerstone.verifier import NUMBER_WORDS, normalize_number, remove_names
from cornerstone.writer import ClaudeCall, RefusalError, WriterError, claude_call

log = logging.getLogger(__name__)

PROMPT_FILES = ("rubric.md", "analysis.md")
UNAVAILABLE = "Analysis unavailable"
MIN_SENTENCES, MAX_SENTENCES = 3, 5
# User story 29: no chart value, chart name, or tier in the prose. The chart comes from the
# Peaked in High Skool site, so its name is banned along with the words.
BANNED = re.compile(r"(?<!\w)(charts?|tiers?|values?|valued|peaked|skool)(?!\w)", re.IGNORECASE)
# The prompt names an adjuster's step in words, as the analyze command prints it.
_STEP_WORDS = {1: "one step up", 0: "no step", -1: "one step down"}
_RACE_TEXT = {
    "contender": "a contender in a playoff spot",
    "seller": "a seller out of the playoff race",
    "middle": "a middle team, neither in a playoff spot nor out of the race",
}


class SideOut(BaseModel):
    """What Claude gives for one side: the final letter, the reason when it differs, the analysis, and its fact IDs."""

    roster_id: int
    final_letter: Letter
    reason: str | None
    analysis: str
    cited: list[str]


class VerdictOut(BaseModel):
    """Claude's verdict for the side that asked, and a flag when it differs from the code's default."""

    choice: Literal["accept", "counter", "decline"]
    reason: str
    differs: bool


class AnalysisOut(BaseModel):
    """The structured output of the Claude call."""

    sides: list[SideOut]
    verdict: VerdictOut


class SideAnalysis(BaseModel):
    """The final word on one side: Claude's letter or the code's, the reason when it differs, and the analysis."""

    roster_id: int
    final_letter: Letter
    reason: str | None
    analysis: str
    cited: list[str]


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


def _fact(fid: str, text: str, n: Nums, teams: list[str], players: list[str]) -> Fact:
    return Fact(id=fid, text=text, numbers=n.seen, teams=teams, players=players)


def _plural(count: int, one: str, many: str) -> str:
    return one if count == 1 else many


def _ppg_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The points per game and the position rank of a traded player, from weeks 1 to N-1 only."""
    n = Nums()
    player = snapshot.players[pid]
    through = snapshot.as_of.stats_through
    who = f"{player.name} ({player.position}, {player.nfl_team})" if player.nfl_team else player.name
    profile = points_per_game(snapshot.stats, pid, through)
    if profile is None:
        text = f"{who} has no stats before the trade."
    elif profile[1] == 0:
        text = f"{who} has no scored game before the trade."
    else:
        text = (f"{who} scored {n(profile[0])} points per game over {n(profile[1])} "
                f"{_plural(profile[1], 'game', 'games')} before the trade")
        rank = season_rank(snapshot.stats, pid, through)
        if rank is not None:
            text += f", position rank {n(rank[0])} of {n(rank[1])} by season points"
        text += "."
    return _fact(f"{pid}.ppg", text, n, [], [player.name])


def _share_fact(snapshot: Snapshot, pid: str, kind: str, share: UsageShare | None) -> Fact | None:
    """The snap share or the target share of a player before the trade. `kind` is the fact ID suffix."""
    if share is None:
        return None
    n = Nums()
    name = snapshot.players[pid].name
    label = "snap share" if kind == "usage" else "target share"
    if share.direction is None:
        text = (f"{name}'s {label} was {n(share.percent)} percent over {n(share.weeks)} "
                f"{_plural(share.weeks, 'game', 'games')} before the trade.")
    else:
        text = (f"{name}'s {label} was {n(share.percent)} percent over the last {n(share.weeks)} weeks before "
                f"the trade, {share.direction} from the {n(share.weeks)} weeks before that.")
    return _fact(f"{pid}.{kind}", text, n, [], [name])


def _redzone_fact(snapshot: Snapshot, pid: str) -> Fact | None:
    zone = red_zone(snapshot.stats, pid, snapshot.as_of.stats_through)
    if zone is None:
        return None
    n = Nums()
    name = snapshot.players[pid].name
    targets, carries = zone
    text = (f"{name} had {n(targets)} red-zone {_plural(targets, 'target', 'targets')} and {n(carries)} "
            f"red-zone {_plural(carries, 'carry', 'carries')} this season before the trade.")
    return _fact(f"{pid}.redzone", text, n, [], [name])


def _report_weeks(snapshot: Snapshot, pid: str) -> int | None:
    """The count of weeks before the trade with the player on the NFL injury report, or None with no report or id."""
    if snapshot.injuries is None or snapshot.id_map is None or pid not in snapshot.id_map:
        return None
    weeks = snapshot.injuries.get(snapshot.id_map[pid], {})
    return sum(1 for week in weeks if week <= snapshot.as_of.stats_through)


def _injury_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The injury status now, the return week on file, and the count of injury report weeks before the trade."""
    n = Nums()
    player = snapshot.players[pid]
    back = snapshot.returns.get(pid)
    if player.injury_status is None:
        text = f"{player.name} has no injury status now"
    else:
        text = f"{player.name} is listed {player.injury_status} now"
    if back is not None:
        text += f", and his return week on file is week {n(back)}."
    elif player.injury_status is not None:
        text += ", with no return week on file."
    else:
        text += "."
    weeks = _report_weeks(snapshot, pid)
    if weeks:
        text += (f" He was on the NFL injury report in {n(weeks)} {_plural(weeks, 'week', 'weeks')} "
                 "this season before the trade.")
    return _fact(f"{pid}.injury", text, n, [], [player.name])


def _value_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The trade value of a traded player. The model reads it, and the number check keeps it out of the prose."""
    n = Nums()
    name = snapshot.players[pid].name
    if pid in snapshot.chart.values:
        text = f"{name}'s trade value is {n(snapshot.chart.values[pid])} in the week of the trade."
    else:
        text = f"{name} has no trade value in the week of the trade."
    return _fact(f"{pid}.value", text, n, [], [name])


def _team_fact(snapshot: Snapshot, rid: int) -> Fact:
    """The record, the rank, and the race of a roster before the trade."""
    n = Nums()
    team = snapshot.teams[rid].name
    standing = next(s for s in snapshot.standings if s.roster_id == rid)
    text = (f"{team} was {n.record(standing.wins, standing.losses)}, {n.ord(standing.rank)} of "
            f"{n(len(snapshot.standings))}, before the trade: {_RACE_TEXT[team_race(snapshot, rid)]}.")
    return _fact(f"{rid}.team", text, n, [team], [])


def _need_fact(snapshot: Snapshot, trade: ProposedTrade, rid: int) -> Fact:
    """The depth of a roster after the trade at each position the trade touches, and its open roster spots."""
    n = Nums()
    team = snapshot.teams[rid].name
    gives = next(s.gives for s in trade.sides if s.roster_id == rid)
    gets = next(s.gives for s in trade.sides if s.roster_id != rid)
    after = [pid for pid in snapshot.rosters[rid] if pid not in gives] + gets
    traded = [pid for side in trade.sides for pid in side.gives]
    positions = sorted({snapshot.players[pid].position for pid in traded})
    depth = [f"{n(sum(snapshot.players[pid].position == pos for pid in after if pid in snapshot.players))} {pos}"
             for pos in positions]
    spots = max(0, len(snapshot.roster_positions) - len(after))
    joined = depth[0] if len(depth) == 1 else ", ".join(depth[:-1]) + " and " + depth[-1]
    text = f"{team} has {joined} after the trade and {n(spots)} open roster {_plural(spots, 'spot', 'spots')}."
    return _fact(f"{rid}.need", text, n, [team], [])


def _week_fact(snapshot: Snapshot) -> Fact:
    n = Nums()
    text = (f"The trade is in week {n(snapshot.week)} of the {n(snapshot.season)} season. "
            f"Every stat runs through week {n(snapshot.as_of.stats_through)}.")
    return _fact("trade.week", text, n, [], [])


def trade_fact_sheet(trade: ProposedTrade, snapshot: Snapshot) -> dict[str, Fact]:
    """The facts of a proposed trade by ID: per traded player the points per game, rank, usage, injury, and
    trade value, and per side the team record and race and the roster need. Every number ends at week N-1."""
    facts = [_week_fact(snapshot)]
    through = snapshot.as_of.stats_through
    for side in trade.sides:
        for pid in side.gives:
            position = snapshot.players[pid].position
            facts.append(_ppg_fact(snapshot, pid))
            facts.append(_share_fact(snapshot, pid, "usage", snap_share(snapshot.stats, pid, through)))
            if position in ("RB", "WR", "TE"):
                facts.append(_share_fact(snapshot, pid, "targets", target_share(snapshot.stats, pid, through)))
            if position in ("QB", "RB", "WR", "TE"):
                facts.append(_redzone_fact(snapshot, pid))
            facts.append(_injury_fact(snapshot, pid))
            if snapshot.chart is not None:
                facts.append(_value_fact(snapshot, pid))
    for side in trade.sides:
        facts.append(_team_fact(snapshot, side.roster_id))
        facts.append(_need_fact(snapshot, trade, side.roster_id))
    return {f.id: f for f in facts if f is not None}


def _load_prompt(name: str) -> str:
    return resources.files("cornerstone.prompts").joinpath(name).read_text(encoding="utf-8").strip()


def _names(snapshot: Snapshot, pids: list[str]) -> str:
    return ", ".join(snapshot.players[pid].name for pid in pids)


def build_analysis_prompt(
    trade: ProposedTrade, snapshot: Snapshot, breakdowns: tuple[Breakdown, Breakdown], code_verdict: Verdict,
    facts: dict[str, Fact], feedback: str | None,
) -> tuple[str, str]:
    system = "\n\n".join(_load_prompt(name) for name in PROMPT_FILES)
    lines = []
    for side, other, breakdown in ((trade.sides[0], trade.sides[1], breakdowns[0]),
                                   (trade.sides[1], trade.sides[0], breakdowns[1])):
        asked = ", the side that asked" if side.roster_id == trade.asker else ""
        lines += [
            f"Side: roster {side.roster_id}, {snapshot.teams[side.roster_id].name}{asked}",
            f"Gives: {_names(snapshot, side.gives)}",
            f"Gets: {_names(snapshot, other.gives)}",
            f"Start letter: {breakdown.start_letter}. {breakdown.reason}",
            *(f"{a.name.capitalize()}: {a.lean if a.lean is not None else _STEP_WORDS[a.step]}. {a.reason}"
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
        lines += ["", "Feedback from the last attempt:", feedback]
    return system, "\n".join(lines)


def _sentences(text: str) -> int:
    # A period inside a decimal is not followed by a space, so it ends no sentence.
    return len(re.findall(r"[.!?]+(?=\s|$)", text.strip()))


def _prose_failures(label: str, text: str, allowed: set[str], allowed_text: str, names: list[str]) -> list[str]:
    """The verifier's number rule and the banned words, on one piece of prose."""
    failures = []
    # Digits inside a name, such as a team called "Pukancun on 3", are not numbers.
    bare = remove_names(text, names)
    for token in NUMBER_TOKEN.findall(bare):
        if normalize_number(token) not in allowed:
            failures.append(f"{label}: number {token} is not in a cited fact")
    for word in NUMBER_WORDS:
        if re.search(rf"(?<!\w){word}(?!\w)", bare, re.IGNORECASE) and not re.search(
                rf"(?<!\w){word}(?!\w)", allowed_text, re.IGNORECASE):
            failures.append(f"{label}: number word '{word}' is not in a cited fact")
    for match in BANNED.finditer(bare):
        failures.append(f"{label}: the word '{match.group()}' is not allowed")
    return failures


def _allowed(facts: dict[str, Fact], fids: list[str]) -> set[str]:
    # A trade value never reaches the prose, even from a cited value fact.
    return {normalize_number(x) for fid in fids if not fid.endswith(".value") for x in facts[fid].numbers}


def check_response(
    out: AnalysisOut, trade: ProposedTrade, snapshot: Snapshot, breakdowns: tuple[Breakdown, Breakdown],
    facts: dict[str, Fact],
) -> list[str]:
    """Every rule a response breaks. An empty list means the response stands."""
    failures = []
    by_roster = {s.roster_id: s for s in out.sides}
    if sorted(by_roster) != sorted(b.roster_id for b in breakdowns) or len(out.sides) != 2:
        return [f"the sides must be rosters {breakdowns[0].roster_id} and {breakdowns[1].roster_id}, once each"]
    names = [*(t.name for t in snapshot.teams.values()), *(p.name for p in snapshot.players.values())]
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
        cited_text = " ".join(facts[fid].text for fid in cited)
        failures += _prose_failures(f"{label} analysis", side.analysis, _allowed(facts, cited), cited_text, names)
        if side.reason:
            failures += _prose_failures(f"{label} reason", side.reason, _allowed(facts, cited), cited_text, names)
    # The verdict reason cites no fact of its own, so any fact the two analyses cite may back its numbers.
    every = [fid for s in out.sides for fid in s.cited if fid in facts]
    failures += _prose_failures("verdict reason", out.verdict.reason, _allowed(facts, every),
                                " ".join(facts[fid].text for fid in every), names)
    return failures


def _accepted(out: AnalysisOut, breakdowns: tuple[Breakdown, Breakdown], code_verdict: Verdict) -> tuple:
    sides = []
    for breakdown in breakdowns:
        side = next(s for s in out.sides if s.roster_id == breakdown.roster_id)
        differs = side.final_letter != breakdown.final_letter
        sides.append(SideAnalysis(roster_id=side.roster_id, final_letter=side.final_letter,
                                  reason=side.reason if differs else None,
                                  analysis=side.analysis, cited=side.cited))
    chosen = Verdict(choice=out.verdict.choice, reason=out.verdict.reason)
    # The code compares the choices itself, so a wrong flag from Claude cannot mislabel the verdict.
    return tuple(sides), chosen, chosen.choice != code_verdict.choice


def analyze(trade: ProposedTrade, snapshot: Snapshot, call: ClaudeCall = claude_call) -> Analysis:
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
            failures = check_response(out, trade, snapshot, breakdowns, facts)
            if failures:
                raise WriterError("; ".join(failures))
        except (RefusalError, WriterError, ValidationError, anthropic.AnthropicError) as err:
            # A bad response is a failed attempt, not a crash of the command or the route.
            log.warning("analysis attempt %d failed: %s", attempt, err)
            feedback = str(err)
            continue
        sides, chosen, differs = _accepted(out, breakdowns, code_verdict)
        return Analysis(breakdowns=breakdowns, code_verdict=code_verdict, sides=sides, verdict=chosen,
                        verdict_differs=differs, fallback=False)
    fallback = tuple(SideAnalysis(roster_id=b.roster_id, final_letter=b.final_letter, reason=None,
                                  analysis=UNAVAILABLE, cited=[]) for b in breakdowns)
    return Analysis(breakdowns=breakdowns, code_verdict=code_verdict, sides=fallback, verdict=code_verdict,
                    verdict_differs=False, fallback=True)
