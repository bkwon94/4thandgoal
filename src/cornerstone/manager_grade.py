"""
The roster grade and the slot ranks of the managers file, from the current rosters and the projections ahead.
The score stays in the pipeline. The entry carries the letter and one rank and one depth word per position.
"""
from typing import Literal, NamedTuple

from pydantic import BaseModel

from cornerstone.adjusters import StartingSlot, fill_slots
from cornerstone.ranks import LINES
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    GRADE_BANDS, GRADE_BELOW_BANDS, GRADE_DEPTH_SPARES, GRADE_HOLE_COST, GRADE_WEIGHTS, LAST_REGULAR_WEEK,
)

# The positions the league starts that have a line, in the order of the slot ranks on the page.
SLOT_POSITIONS = ("QB", "RB", "WR", "TE")

Depth = Literal["deep", "fine", "thin"]


class SlotRank(BaseModel):
    """One position of a roster: its rank of 1 to 12 in the league and one depth word."""
    position: str
    rank: int
    depth: Depth


class ManagerGrade(BaseModel):
    """The roster grade of an entry: the letter and the slot ranks. The score never leaves the pipeline."""
    letter: str
    slots: list[SlotRank]


class GradeParts(NamedTuple):
    """The four parts of the score, each from 0 to 1. GRADE_WEIGHTS weighs each one."""
    # The mean of each ranked starter's place above the line.
    slots: float
    # One less GRADE_HOLE_COST per hole, never under 0.
    holes: float
    # The mean over the positions of the depth against the starters plus the spares.
    depth: float
    # The best lineup's total against the league, from 0 at the lowest roster to 1 at the highest.
    lineup: float


def grade_score(parts: GradeParts) -> float:
    """The 0 to 100 score of the parts."""
    return sum(GRADE_WEIGHTS[name] * value for name, value in parts._asdict().items())


def grade_letter(score: float) -> str:
    """The letter of the score: the first band whose lowest score the score reaches."""
    return next((letter for letter, lowest in GRADE_BANDS if score >= lowest), GRADE_BELOW_BANDS)


def depth_word(starters: int, above: int, hole: bool) -> Depth:
    """The depth word of a position: thin with a hole, deep with more players above the line than starters."""
    if hole:
        return "thin"
    return "deep" if above > starters else "fine"


def projected_values(projections_ahead: dict[int, dict[str, float]]) -> dict[str, float]:
    """The value of each player in the projections: the mean of his projections over the weeks ahead.

    A week with no projection for him counts 0 in the mean. The weeks stop at LAST_REGULAR_WEEK, because the file
    runs to the end of the NFL season and a playoff week says nothing of the roster in the regular season.
    """
    weeks = [projections for week, projections in projections_ahead.items() if week <= LAST_REGULAR_WEEK]
    players = {pid for projections in weeks for pid in projections}
    return {pid: sum(projections.get(pid, 0.0) for projections in weeks) / len(weeks) for pid in players}


def position_ranks(values: dict[str, float], positions: dict[str, str]) -> dict[str, int]:
    """The place of each player from 1 at his position by value, most first, among the players with a value.

    Only the positions in LINES get a rank. A player with no value has no rank, so he is below the line. The player
    id breaks a tie, so no two share a place.
    """
    ranks: dict[str, int] = {}
    for position in LINES:
        pool = sorted((pid for pid in values if positions.get(pid) == position), key=lambda pid: (-values[pid], pid))
        ranks.update({pid: place for place, pid in enumerate(pool, start=1)})
    return ranks


def roster_grades(snapshot: Snapshot, projections_ahead: dict[int, dict[str, float]]) -> dict[int, ManagerGrade]:
    """The grade of each roster of the snapshot by the projections ahead, by roster id.

    The snapshot gives the rosters, the roster slots, and the positions. The injury status and the returns file play
    no part, so a starter out one week with a projection ahead is no hole.
    """
    values = projected_values(projections_ahead)
    ranks_by_player = position_ranks(values, {pid: player.position for pid, player in snapshot.players.items()})
    reads = {rid: _RosterRead(snapshot, roster, values, ranks_by_player) for rid, roster in snapshot.rosters.items()}
    totals = [read.lineup_total for read in reads.values()]
    low, high = min(totals), max(totals)
    ranks = {position: _ranks({rid: read.position_total(position) for rid, read in reads.items()})
             for position in SLOT_POSITIONS}
    grades = {}
    for rid, read in reads.items():
        # With every roster equal, no roster is ahead of the league, so each takes the part in full.
        lineup = 1.0 if high == low else float((read.lineup_total - low) / (high - low))
        letter = grade_letter(grade_score(read.parts(lineup)))
        grades[rid] = ManagerGrade(letter=letter, slots=[
            SlotRank(position=position, rank=ranks[position][rid], depth=read.depth_word(position))
            for position in SLOT_POSITIONS
        ])
    return grades


def _ranks(totals: dict[int, float]) -> dict[int, int]:
    """The place of each roster from 1 by the total, most first. The roster id breaks a tie, so no two share a place."""
    order = sorted(totals, key=lambda rid: (-totals[rid], rid))
    return {rid: place for place, rid in enumerate(order, start=1)}


class _RosterRead:
    """What the grade reads of one roster: the starters of its best lineup, with the FLEX filled, and its depth.

    The best lineup fills the roster slots by the projected value, and each starter carries his projected rank.
    A slot of a StartingSlot here has no absence, so a hole is a slot with no player or a player below the line.
    """

    def __init__(self, snapshot: Snapshot, roster: list[str], values: dict[str, float],
                 ranks: dict[str, int]) -> None:
        self.snapshot = snapshot
        self.roster = roster
        self.values = values
        self.ranks = ranks
        positions = {pid: snapshot.players[pid].position for pid in roster}
        filled = fill_slots(roster, snapshot.roster_positions, positions, {pid: self._value(pid) for pid in roster})
        starting = [StartingSlot(name=slot, player=pid, rank=None if pid is None else ranks.get(pid), roster_slot=slot)
                    for slot, pid in filled]
        # K and DEF have no line, so the grade reads only the slots of the positions in LINES. An empty slot is a
        # hole only when a lined player could fill it, so an empty FLEX counts in the score but at no position.
        self.slots = [slot for slot in starting
                      if self._position(slot) in LINES or (slot.player is None and slot.is_hole(snapshot))]
        self.lineup_total = sum(self._value(slot.player) for slot in self.slots if slot.player is not None)

    def _value(self, player_id: str) -> float:
        """The projected value of the player. A player with no projection ahead counts 0."""
        return self.values.get(player_id, 0.0)

    def _position(self, slot: StartingSlot) -> str | None:
        """The position the slot counts for: its player's, or its fixed roster slot when it holds no player."""
        if slot.player is not None:
            return self.snapshot.players[slot.player].position
        return slot.roster_slot if slot.roster_slot in LINES else None

    def _at(self, position: str) -> list[StartingSlot]:
        return [slot for slot in self.slots if self._position(slot) == position]

    def position_total(self, position: str) -> float:
        """The projected value of the starters at the position, the FLEX starters included."""
        return sum(self._value(slot.player) for slot in self._at(position) if slot.player is not None)

    def above(self, position: str) -> int:
        """The depth at the position: the players, starters and bench, above the line. GLOSSARY.md, "Depth"."""
        line = LINES[position]
        return sum(1 for pid in self.roster
                   if self.snapshot.players[pid].position == position and self.ranks.get(pid, line + 1) <= line)

    def depth_word(self, position: str) -> Depth:
        starters = self._at(position)
        return depth_word(len(starters), self.above(position), any(slot.is_hole(self.snapshot) for slot in starters))

    def parts(self, lineup: float) -> GradeParts:
        """The four parts of the score, with the lineup part the league read gives."""
        places = [self._place(slot) for slot in self.slots]
        holes = sum(1 for slot in self.slots if slot.is_hole(self.snapshot))
        depth = [min(self.above(position), len(self._at(position)) + GRADE_DEPTH_SPARES)
                 / (len(self._at(position)) + GRADE_DEPTH_SPARES) for position in SLOT_POSITIONS]
        return GradeParts(
            slots=sum(places) / len(places) if places else 0.0,
            holes=max(0.0, 1 - GRADE_HOLE_COST * holes),
            depth=sum(depth) / len(depth),
            lineup=lineup,
        )

    def _place(self, slot: StartingSlot) -> float:
        """The starter against the line: 1 at rank 1, down to 1 / line at the line, and 0 below it or with no player."""
        if slot.player is None or slot.rank is None:
            return 0.0
        line = LINES[self._position(slot)]
        return max(0.0, (line + 1 - slot.rank) / line)
