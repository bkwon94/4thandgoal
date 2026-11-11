"""
The facts of the personal Topics of the front door, from the live snapshot: the roster grade, the slot ranks, the
starters of the best lineup, and the free agents of the waiver targets. Code picks the slice and adds no formula.
"""
from dataclasses import dataclass
from typing import Literal

from analyzer.trade_jev import weak_slot_rows, weak_starting_slots
from cornerstone_api.waiver_targets import waiver_facts
from league.lineup import cannot_play_now, lineup_now
from league.numbers import ordinal
from league.provider.raw import RawTrending
from league.season_inputs import SeasonInputs
from league.snapshot import Snapshot
from managers.grade import ManagerGrade, Starter, roster_grades, roster_starters

PersonalTopic = Literal["weak_spots", "stack_up", "waiver_targets"]

# The fact groups of each personal Topic (decision 03). The slice holds only these groups.
FACT_GROUPS: dict[str, tuple[str, ...]] = {
    "weak_spots": ("slot_ranks", "starters", "grade_read", "weak_starting_slots"),
    "stack_up": ("grade", "part_ranks", "slot_ranks", "grade_read"),
    # The facts before the Jev read: the need of the team and each candidate. The read keeps the players worth a claim,
    # and Claude reads only those, in `kept_players` of judged_waiver.
    "waiver_targets": ("team_need", "candidates"),
}

# The name of each part of the roster grade, as the managers page names it (packages/managers/site/page/part-names.ts).
PART_NAMES = {"projection": "Projection Ahead", "production": "Season Production", "trade_value": "Trade Value",
              "depth": "Depth And Holes"}

# What each depth word of the slot ranks means (GLOSSARY.md, "Depth"). The slice carries the meaning with the word, so
# Claude and the Jev check read the same fact.
DEPTH_MEANINGS = {
    "thin": "a starter slot at this position is a hole",
    "fine": "no spare player inside the starter count past the starters",
    "deep": "one spare player inside the starter count past the starters",
    "stacked": "two or more spare players inside the starter count past the starters",
}


@dataclass(frozen=True)
class PersonalFacts:
    """The facts of one personal Topic of one team: the slice that Claude reads and the Jev check reads, and the data
    block that the site shows first. Both come from the same reads, so the key of the slice covers the block."""

    slice: dict
    block: dict


def _ahead(snapshot: Snapshot) -> dict[int, dict[str, float]]:
    """The projections ahead of the grade by week and player id, from the trade week on, as the weekly build reads
    them. The snapshot keeps them by player id and week."""
    if snapshot.projections_ahead is None:
        raise ValueError("the live snapshot has no projections ahead, so the roster grade has no input")
    by_week: dict[int, dict[str, float]] = {}
    for pid, weeks in snapshot.projections_ahead.items():
        for week, points in weeks.items():
            if week >= snapshot.week:
                by_week.setdefault(week, {})[pid] = points
    return by_week


def live_grades(snapshot: Snapshot) -> tuple[dict[int, ManagerGrade], dict[int, list[Starter]]]:
    """The roster grade and the starters of each roster now, with the formula of the managers page."""
    inputs = SeasonInputs(history=snapshot.stats, snapshot=snapshot, projections_ahead=_ahead(snapshot),
                          chart=snapshot.chart)
    return roster_grades(inputs), roster_starters(inputs)


def _of(rank: int, teams: int) -> str:
    return f"{ordinal(rank)} of {teams}"


def _name(snapshot: Snapshot, pid: str | None) -> str | None:
    return None if pid is None else snapshot.players[pid].name


def _slot_ranks(grade: ManagerGrade) -> list[dict]:
    return [{"position": slot.position, "rank": slot.rank, "depth": slot.depth,
             "depth_means": DEPTH_MEANINGS[slot.depth]} for slot in grade.slots]


def _starters(snapshot: Snapshot, starters: list[Starter]) -> list[dict]:
    lines = snapshot.client.settings.lines
    return [{"slot": s.slot, "player": _name(snapshot, s.player_id), "position": s.position,
             "projected_rank_at_position": s.rank, "starter_line": lines.get(s.position or ""), "hole": s.hole,
             "can_play_now": s.player_id is None or not cannot_play_now(snapshot, s.player_id)}
            for s in starters]


def _now(snapshot: Snapshot, starters: list[Starter]) -> list[Starter]:
    """The starters of the roster grade, with each starter who cannot play now marked as a hole. GLOSSARY.md, "Hole".

    The roster grade reads the projections ahead only, so a starter on IR with points after his return still fills
    his slot there. He cannot start in the trade week, so the personal Topics read his slot as a hole, as the weak
    starting slots of `/find` read it empty.
    """
    return [s.model_copy(update={"hole": True})
            if s.player_id is not None and cannot_play_now(snapshot, s.player_id) else s for s in starters]


def _unshown(snapshot: Snapshot, roster_id: int, starters: list[Starter]) -> list[dict]:
    """The weak slot rows that `starters` does not show: an empty slot, or a player who is not a starter there, such as
    the stand-in for a starter on IR.

    The weak slot rows rank a player by points per game, and `starters` ranks him by the projections ahead. A row for a
    starter would give him two ranks, so a claim of "no hole" is true by one list and false by the other.
    """
    shown = {_name(snapshot, s.player_id) for s in starters if s.player_id is not None}
    return [row for row in weak_slot_rows(snapshot, roster_id) if row["player"] is None or row["player"] not in shown]


def _empty_now(snapshot: Snapshot, roster_id: int) -> list[str]:
    """The roster slot of each slot of the lineup now that no player who can play fills, in fill order.

    These are the empty slots of the weak starting slots of `/find`. A K or DEF slot is never a hole, so it is not here.
    """
    return [slot.roster_slot for slot in lineup_now(snapshot.rosters[roster_id], snapshot)
            if slot.player is None and slot.is_hole(snapshot)]


def _worst(grade: ManagerGrade):
    """The slot ranks from the lowest place in the league to the highest. The site shows the weakest first."""
    return sorted(grade.slots, key=lambda slot: (-slot.rank, slot.position))


def _slot_rows(snapshot: Snapshot, grade: ManagerGrade, starters: list[Starter], teams: int,
               empty: list[str]) -> list[dict]:
    rows = []
    # An empty slot now is the weakest spot, whatever the slot rank of its position, so its row comes first.
    for slot in sorted(_worst(grade), key=lambda slot: slot.position not in empty):
        holes = [_name(snapshot, s.player_id) or s.slot for s in starters if s.hole and s.position == slot.position]
        # The depth word comes from the grade, which counts a starter who is out now. A row with a hole reads "thin", the
        # word for a hole, so it never reads "fine" or "deep" next to the name of a hole.
        note = slot.depth if not holes else f"thin · hole: {', '.join(holes)}"
        rows.append({"label": slot.position, "value": _of(slot.rank, teams), "note": note, "roster_id": None,
                     "you": False})
    return rows


def trade_ideas_fact(snapshot: Snapshot, roster_id: int) -> str | None:
    """The fact of the trade ideas Suggestion: the first weak starting slot of the team, or None when it has none.

    It reads the weak starting slots that `/find` reads, not the slot ranks of weak spots, so the offers fill the slot
    that the fact names. A slot rank is a place in the league, and a position in the middle of the league can still
    start players above the weak rank, so the Finder fills no slot there.
    """
    weak = weak_starting_slots(snapshot, roster_id)
    return f"Offers for your {weak[0]}" if weak else None


def _weak_slot(need: dict) -> str | None:
    """The first weak starting slot of the team, such as "QB", or None when it has none."""
    weak = need["weak_starting_slots"]
    return weak[0].partition(":")[0] if weak else None


def _waiver_block(need: dict, read: int) -> dict:
    """The block of the waiver targets before the Jev read: the first weak slot and the count of free agents to read.
    The Suggestion shows its fact, so the fact costs no Jev call."""
    slot = _weak_slot(need)
    return {"fact": f"Free agents for the {slot} slot" if slot else "Free agents to stash",
            "stats": [{"label": "Weak slot", "value": slot or "None"},
                      {"label": "Free agents read", "value": str(read)}],
            "rows": []}


def judged_waiver(facts: PersonalFacts, kept: list[dict]) -> PersonalFacts:
    """The facts of the waiver targets after the Jev read: Claude reads the need and the kept players only, best first,
    and the block lists the kept players. With no kept player, the block says so plainly."""
    slice_ = {key: value for key, value in facts.slice.items() if key != "candidates"}
    read = len(facts.slice["candidates"])
    slot = _weak_slot(facts.slice["team_need"])
    count = len(kept)
    fact = (f"{count} free {'agent' if count == 1 else 'agents'} worth a claim" if kept
            else "No free agent beats the starters this week")
    block = {**facts.block, "fact": fact,
             "stats": [{"label": "Weak slot", "value": slot or "None"},
                       {"label": "Free agents read", "value": str(read)},
                       {"label": "Worth a claim", "value": str(count)}],
             "rows": [{"label": player["name"], "value": "",
                       "note": " · ".join(part for part in (player["position"], player["nfl_team"]) if part),
                       "roster_id": None, "you": False} for player in kept]}
    return PersonalFacts(slice={**slice_, "kept_players": kept}, block=block)


def topic_facts(topic: PersonalTopic, snapshot: Snapshot, roster_id: int, grades: dict[int, ManagerGrade],
                starters: dict[int, list[Starter]], trending: list[RawTrending]) -> PersonalFacts:
    """The slice and the data block of `topic` for the team of `roster_id`. The waiver targets give the facts before
    the Jev read, and judged_waiver gives the facts after it."""
    grade, mine = grades[roster_id], _now(snapshot, starters[roster_id])
    teams = len(snapshot.rosters)
    groups = {
        "grade": {"letter": grade.letter},
        "part_ranks": [{"part": PART_NAMES[part.key], "rank": part.rank} for part in grade.parts],
        "slot_ranks": _slot_ranks(grade),
        "starters": _starters(snapshot, mine),
        "grade_read": grade.read,
        "weak_starting_slots": _unshown(snapshot, roster_id, mine) if topic == "weak_spots" else [],
    }
    if topic == "waiver_targets":
        groups["team_need"], groups["candidates"] = waiver_facts(snapshot, roster_id, trending)
    slice_ = {"team": snapshot.teams[roster_id].name, "teams_in_league": teams, "week": snapshot.week,
              **{group: groups[group] for group in FACT_GROUPS[topic]}}
    worst = _worst(grade)[0]
    hole_count = sum(1 for s in mine if s.hole)
    if topic == "weak_spots":
        empty = _empty_now(snapshot, roster_id)
        if empty:
            fact, weakest, rank = f"{empty[0]} empty now", empty[0], "Empty now"
        else:
            fact, weakest, rank = f"{worst.position} ranks {_of(worst.rank, teams)}", worst.position, _of(worst.rank, teams)
        block = {"fact": fact,
                 "stats": [{"label": "Weakest spot", "value": weakest},
                           {"label": "Rank", "value": rank},
                           {"label": "Holes", "value": str(hole_count)}],
                 "rows": _slot_rows(snapshot, grade, mine, teams, empty)}
    elif topic == "stack_up":
        best = _worst(grade)[-1]
        # The grade reads the live league, and the grade of the managers page reads the weekly build, so the two can
        # differ. The slice and the block both say that this one is from today.
        slice_["grade_as_of"] = "today"
        block = {"as_of": "as of today",
                 "fact": f"Grade {grade.letter}, {worst.position} ranks {_of(worst.rank, teams)}",
                 "stats": [{"label": "Grade", "value": grade.letter},
                           {"label": "Best spot", "value": f"{best.position} {ordinal(best.rank)}"},
                           {"label": "Weakest spot", "value": f"{worst.position} {ordinal(worst.rank)}"}],
                 "rows": [{"label": PART_NAMES[part.key], "value": _of(part.rank, teams), "note": None,
                           "roster_id": None, "you": False} for part in grade.parts]}
    else:
        block = _waiver_block(groups["team_need"], len(groups["candidates"]))
    return PersonalFacts(slice=slice_, block={"topic": topic, "team": roster_id, **block})
