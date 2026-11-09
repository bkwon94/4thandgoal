"""
The team facts of the Advisor sheet: per side the race group and the odds, a bye in the trade week, and the depth.
The depth reads the RBs always and every position of the trade for every side. The Measures of each side follow.
"""
import json
import logging
from pathlib import Path

from analyzer.adjusters import Side, trade_handcuffs
from analyzer.measures import measure_facts
from analyzer.rubric import ProposedTrade, build_sides
from facts.tokens import Nums, fact
from league.models import Fact, OddsStatus
from league.ranks import RANKED_POSITIONS
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# The RB room is a fact on every sheet, because the Advisor must never tell a side to give up its last reliable RB.
ALWAYS = ("RB",)
# The lowest playoff odds of In and of Bubble, in whole percents, as the race group of the site reads them.
IN_FROM, BUBBLE_FROM = 75, 25


def race_group(playoff: int, status: OddsStatus) -> str:
    """The race group of a team: In, Bubble, or Out. GLOSSARY.md, "Race group". The status wins over the odds."""
    if status == "in" or (status == "open" and playoff >= IN_FROM):
        return "In"
    if status == "out" or playoff < BUBBLE_FROM:
        return "Out"
    return "Bubble"


def _rankings_file(snapshot: Snapshot) -> Path:
    """The published rankings of the season. The weekly build writes the odds of each roster there."""
    return snapshot.client.folder / "published" / str(snapshot.season) / "rankings.json"


def _odds(snapshot: Snapshot, week: int) -> dict[int, dict]:
    """The odds of each roster after `week`, from the published rankings. A missing or bad file gives none.

    The analyzer reads the odds the weekly build wrote, because the odds engine sits in the rankings package.
    """
    path = _rankings_file(snapshot)
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
        rows = next((w["rows"] for w in body["weeks"] if w["week"] == week), [])
        return {row["roster_id"]: row["odds"] for row in rows if "odds" in row}
    except (OSError, ValueError, KeyError, TypeError) as err:
        log.info("no playoff odds for week %d in %s: %s", week, path, err)
        return {}


def _team_fact(snapshot: Snapshot, rid: int, odds: dict | None) -> Fact:
    """The record, the rank, the race group, and the playoff odds of a roster before the trade."""
    n = Nums()
    team = snapshot.teams[rid].name
    week = snapshot.as_of.completed_through
    standing = next(s for s in snapshot.standings if s.roster_id == rid)
    text = (f"{team} was {n.record(standing.wins, standing.losses)}, {n.ord(standing.rank)} of "
            f"{n(len(snapshot.standings))}, before the trade.")
    if odds is None:
        text += f" No playoff odds are on file for week {n(week)}, so it has no race group."
    else:
        group = race_group(odds["playoff"], odds["status"])
        state = {"in": " It has clinched a playoff spot.", "out": " It is eliminated from the playoffs."}
        text += (f" Its race group is {group}, with {n(odds['playoff'])}% playoff odds after week {n(week)}."
                 + state.get(odds["status"], ""))
    return fact(f"{rid}.team", text, n, [team], [])


def _depth_fact(snapshot: Snapshot, side: Side, position: str) -> Fact:
    """The depth of a side at a position before and after the trade, in plain words, even when it does not change."""
    before, after = side.depth(snapshot, position)
    n = Nums()
    team = snapshot.teams[side.roster_id].name
    line = snapshot.client.settings.lines[position]
    # One shape for every count, so "go from 2 to 2" says plainly that the trade leaves the room as it is.
    text = f"For {team}, the {position}s in the top {n(line)} go from {n(before)} to {n(after)}."
    return fact(f"{side.roster_id}.depth.{position.lower()}", text, n, [team], [])


def _bye_fact(snapshot: Snapshot, side: Side) -> Fact | None:
    """The starters of a side after the trade whose NFL team has its bye in the trade week, or None with none.

    ADR 0030: a bye is a fact for every side, and the Advisor weighs it with the race group. No schedule reads no bye.
    """
    def has_bye(pid: str) -> bool:
        team = snapshot.players[pid].nfl_team
        schedule = None if snapshot.schedules is None or team is None else snapshot.schedules.get(team)
        return schedule is not None and schedule.bye_week == snapshot.week

    byes = [slot.player for slot in side.slots_after if slot.player is not None and has_bye(slot.player)]
    if not byes:
        return None
    n = Nums()
    team = snapshot.teams[side.roster_id].name
    names = [snapshot.players[pid].name for pid in byes]
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    verbs = "starts after the trade and has" if len(names) == 1 else "start after the trade and have"
    text = f"For {team}, {joined} {verbs} a bye in week {n(snapshot.week)}, the trade week."
    return fact(f"{side.roster_id}.bye", text, n, [team], names)


def team_facts(trade: ProposedTrade, snapshot: Snapshot) -> dict[str, Fact]:
    """The team facts of each side by id. The team fact and a depth fact keep the ids of the trade sheet, so each
    takes the place of the old fact. The team fact says race group, as the site does, not contender or seller.
    The Measures of each side follow."""
    traded = {snapshot.players[pid].position for pid in trade.player_ids}
    positions = [p for p in RANKED_POSITIONS if (p in ALWAYS or p in traded) and p in snapshot.client.settings.lines]
    odds = _odds(snapshot, snapshot.as_of.completed_through)
    facts = [_team_fact(snapshot, side.roster_id, odds.get(side.roster_id)) for side in trade.sides]
    sides = build_sides(trade, snapshot, trade_handcuffs(trade, snapshot))
    for side in sides:
        facts += [_depth_fact(snapshot, side, position) for position in positions]
        if (bye := _bye_fact(snapshot, side)) is not None:
            facts.append(bye)
    facts += measure_facts(snapshot, sides)
    return {f.id: f for f in facts}
