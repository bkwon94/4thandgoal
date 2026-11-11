"""
The facts of the personal Topics of the front door, from the live snapshot: the roster grade, the slot ranks, the
starters of the best lineup, and the waiver list of the latest published week. Code picks the slice and adds no formula.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from analyzer.trade_jev import weak_starting_slots
from league.lineup import cannot_play_now, lineup_now
from league.numbers import ordinal
from league.paths import week_label
from league.season_inputs import SeasonInputs
from league.snapshot import Snapshot
from managers.grade import ManagerGrade, Starter, roster_grades, roster_starters

PersonalTopic = Literal["weak_spots", "stack_up", "waiver_targets"]

# The fact groups of each personal Topic (decision 03). The slice holds only these groups.
FACT_GROUPS: dict[str, tuple[str, ...]] = {
    "weak_spots": ("slot_ranks", "starters", "grade_read", "weak_starting_slots"),
    "stack_up": ("grade", "part_ranks", "slot_ranks", "grade_read"),
    "waiver_targets": ("slot_ranks", "starters", "waiver_list"),
}

# The name of each part of the roster grade, as the managers page names it (packages/managers/site/page/part-names.ts).
PART_NAMES = {"projection": "Projection Ahead", "production": "Season Production", "trade_value": "Trade Value",
              "depth": "Depth And Holes"}

# The buckets of the waiver board that list a player to add. Trending comes first: it is Sleeper's own list of the
# players most added in the last day, the crowd signal, so the Answer leans on it. A player in two buckets keeps the
# first one of this order.
WAIVER_BUCKETS = ("trending", "best_adds", "sneaky", "stashes")
# What each depth word of the slot ranks means (GLOSSARY.md, "Depth"). The slice carries the meaning with the word, so
# Claude and the Jev check read the same fact.
DEPTH_MEANINGS = {
    "thin": "a starter slot at this position is a hole",
    "fine": "no spare player inside the starter count past the starters",
    "deep": "one spare player inside the starter count past the starters",
    "stacked": "two or more spare players inside the starter count past the starters",
}
WAIVER_FILE = "waiver.json"
# The data block lists the first players of the board in its own order, so the card stays one screen on a phone.
# Claude reads the whole list.
WAIVER_ROWS = 8


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


def published_waiver(folder: Path, season: int, week: int) -> dict | None:
    """The waiver file of the latest published week up to `week`, or None when the client published none."""
    season_dir = folder / "published" / str(season)
    for each in range(week, 0, -1):
        path = season_dir / week_label(each) / WAIVER_FILE
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if (season_dir / week_label(each)).exists():
            # The latest published week has no waiver file, so the client does not publish one this week.
            return None
    return None


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


def _empty_now(snapshot: Snapshot, roster_id: int) -> list[str]:
    """The roster slot of each slot of the lineup now that no player who can play fills, in fill order.

    These are the empty slots of the weak starting slots of `/find`. A K or DEF slot is never a hole, so it is not here.
    """
    return [slot.roster_slot for slot in lineup_now(snapshot.rosters[roster_id], snapshot)
            if slot.player is None and slot.is_hole(snapshot)]


def _waiver_list(board: dict | None, snapshot: Snapshot) -> list[dict]:
    """The players of the waiver board who are still free agents. A player on a roster now cannot be added, so that
    hard rule drops him. Sleeper projects no points in any week left for a player with a rest of season projection
    of 0 or none, so that hard rule drops him too. The list gives no bid: the bid of the board is flat per position,
    so it tells nothing about the player."""
    if board is None:
        return []
    rostered = {pid for players in snapshot.rosters.values() for pid in players}
    seen: set[str] = set()
    players = []
    for bucket in WAIVER_BUCKETS:
        for player in board["buckets"].get(bucket, []):
            pid = player["player_id"]
            if pid in rostered or pid in seen or not player.get("ros_projection"):
                continue
            seen.add(pid)
            players.append({"name": player["name"], "position": player["position"], "nfl_team": player.get("team"),
                            "bucket": bucket, "week_projection": player.get("week_projection"),
                            "rest_of_season_projection": player.get("ros_projection"),
                            "facts": [fact["text"] for fact in player.get("facts", [])]})
    return players


def _worst(grade: ManagerGrade):
    """The slot ranks from the lowest place in the league to the highest. The site shows the weakest first."""
    return sorted(grade.slots, key=lambda slot: (-slot.rank, slot.position))


def _slot_rows(snapshot: Snapshot, grade: ManagerGrade, starters: list[Starter], teams: int,
               empty: list[str]) -> list[dict]:
    rows = []
    # An empty slot now is the weakest spot, whatever the slot rank of its position, so its row comes first.
    for slot in sorted(_worst(grade), key=lambda slot: slot.position not in empty):
        holes = [_name(snapshot, s.player_id) or s.slot for s in starters if s.hole and s.position == slot.position]
        note = slot.depth if not holes else f"{slot.depth} · hole: {', '.join(holes)}"
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


def topic_facts(topic: PersonalTopic, snapshot: Snapshot, roster_id: int, grades: dict[int, ManagerGrade],
                starters: dict[int, list[Starter]], board: dict | None) -> PersonalFacts:
    """The slice and the data block of `topic` for the team of `roster_id`."""
    grade, mine = grades[roster_id], _now(snapshot, starters[roster_id])
    teams = len(snapshot.rosters)
    groups = {
        "grade": {"letter": grade.letter},
        "part_ranks": [{"part": PART_NAMES[part.key], "rank": part.rank} for part in grade.parts],
        "slot_ranks": _slot_ranks(grade),
        "starters": _starters(snapshot, mine),
        "grade_read": grade.read,
        "waiver_list": _waiver_list(board, snapshot) if topic == "waiver_targets" else [],
        "weak_starting_slots": weak_starting_slots(snapshot, roster_id) if topic == "weak_spots" else [],
    }
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
        block = {"fact": f"Grade {grade.letter}, {worst.position} ranks {_of(worst.rank, teams)}",
                 "stats": [{"label": "Grade", "value": grade.letter},
                           {"label": "Best spot", "value": f"{best.position} {ordinal(best.rank)}"},
                           {"label": "Weakest spot", "value": f"{worst.position} {ordinal(worst.rank)}"}],
                 "rows": [{"label": PART_NAMES[part.key], "value": _of(part.rank, teams), "note": None,
                           "roster_id": None, "you": False} for part in grade.parts]}
    else:
        free = groups["waiver_list"]
        block = {"fact": f"{len(free)} free agents on the list" if free else "No waiver list this week",
                 "stats": [{"label": "Weakest spot", "value": worst.position},
                           {"label": "Rank", "value": _of(worst.rank, teams)},
                           {"label": "On the list", "value": str(len(free))}],
                 "rows": [{"label": player["name"], "value": "",
                           "note": " · ".join(part for part in (player["position"], player["nfl_team"]) if part),
                           "roster_id": None, "you": False} for player in free[:WAIVER_ROWS]]}
    return PersonalFacts(slice=slice_, block={"topic": topic, "team": roster_id, **block})
