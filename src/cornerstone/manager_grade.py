"""
The roster grade and the slot ranks of the managers file, from the rosters, the projections, the points, and the chart.
The score stays in the pipeline. The entry carries the letter, one rank and one depth word per position, and one
rank per part of the score.
"""
from typing import Literal, NamedTuple

from pydantic import BaseModel

from cornerstone.adjusters import StartingSlot, fill_slots
from cornerstone.config import LeagueConfig
from cornerstone.history import player_points
from cornerstone.models import History, ProjectionsAhead
from cornerstone.season_inputs import SeasonInputs
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    GRADE_BANDS, GRADE_BELOW_BANDS, GRADE_DEPTH_SPARES, GRADE_HOLE_COST, GRADE_WEIGHTS,
)

# The positions the league starts that have a line, in the order of the slot ranks on the page.
SLOT_POSITIONS = ("QB", "RB", "WR", "TE")

Depth = Literal["stacked", "deep", "fine", "thin"]


class SlotRank(BaseModel):
    """One position of a roster: its rank of 1 to 12 in the league and one depth word."""
    position: str
    rank: int
    depth: Depth


class PartRank(BaseModel):
    """One part of the score of a roster: its key in GRADE_WEIGHTS and its rank of 1 to 12 in the league."""
    key: str
    rank: int


class ManagerGrade(BaseModel):
    """The roster grade of an entry: the letter, the slot ranks, the part ranks, and the read. The score never leaves
    the pipeline, so the part ranks show the place of the roster on each part and never the value."""
    letter: str
    slots: list[SlotRank]
    parts: list[PartRank]
    # One to four short sentences in words, from the slot ranks: "Strong at RB and TE. Soft at QB and WR."
    read: str


class GradeParts(NamedTuple):
    """The four parts of the score, each from 0 to 1. GRADE_WEIGHTS weighs each one."""
    # The mean of two reads by the projections ahead, each against the league from 0 at the lowest roster to 1 at
    # the highest: the mean of each ranked starter's place above the line, and the best lineup's total.
    projection: float
    # The best lineup's total by the season points per game against the league, from 0 at the lowest roster to 1
    # at the highest.
    production: float
    # The sum of the chart values of the roster against the league, from 0 at the lowest roster to 1 at the
    # highest. It is 0 for every roster when the week has no chart.
    trade_value: float
    # The mean of two reads against the league, from 0 at the lowest roster to 1 at the highest. One is one less
    # GRADE_HOLE_COST per hole, never under 0. The other is the mean over the positions of the depth against the
    # starters plus the spares.
    depth: float


def grade_score(parts: GradeParts) -> float:
    """The 0 to 100 score of the parts."""
    return sum(GRADE_WEIGHTS[name] * value for name, value in parts._asdict().items())


def grade_letter(score: float) -> str:
    """The letter of the score: the first band whose lowest score the score reaches."""
    return next((letter for letter, lowest in GRADE_BANDS if score >= lowest), GRADE_BELOW_BANDS)


def depth_word(spares: int, hole: bool) -> Depth:
    """The depth word of a position: thin with a hole, else by the spares inside the starter count past the starters.

    Two or more spares read stacked, one reads deep, and none reads fine. A hole wins over any spare.
    """
    if hole:
        return "thin"
    if spares >= 2:
        return "stacked"
    return "deep" if spares == 1 else "fine"


def _names(positions: list[str]) -> str:
    """Positions in a list: "RB", "RB and TE", or "QB, RB, and WR"."""
    if len(positions) <= 2:
        return " and ".join(positions)
    return ", ".join(positions[:-1]) + ", and " + positions[-1]


def grade_read(slots: list[SlotRank], *, config: LeagueConfig) -> str:
    """The grade in words, from the slot ranks: the strong positions, the deep ones, the soft ones, and the thin ones.

    A position is strong in the top quarter of the league and soft in the bottom quarter. A thin position is a hole,
    so it reads thin and never strong or soft too: one star cannot make a position with a hole strong. With nothing
    to say, the roster is middle of the league at every position.
    """
    thin = [s.position for s in slots if s.depth == "thin"]
    strong = [s.position for s in slots if s.rank <= config.grade_strong_rank and s.position not in thin]
    deep = [s.position for s in slots if s.depth in ("deep", "stacked")]
    soft = [s.position for s in slots if s.rank >= config.grade_soft_rank and s.position not in thin]
    sentences = [f"{word} at {_names(names)}." for word, names in (
        ("Strong", strong), ("Deep", deep), ("Soft", soft), ("Thin", thin)) if names]
    return " ".join(sentences) or "Middle of the league at every position."


def projected_values(projections_ahead: ProjectionsAhead, config: LeagueConfig) -> dict[str, float]:
    """The value of each player in the projections: the mean of his projections over the weeks ahead.

    A week with no projection for him counts 0 in the mean. The weeks stop at the last regular week of `config`,
    because the file runs to the end of the NFL season and a playoff week says nothing of the roster in the regular
    season.
    """
    weeks = [projections for week, projections in projections_ahead.items() if week <= config.last_regular_week]
    players = {pid for projections in weeks for pid in projections}
    return {pid: sum(projections.get(pid, 0.0) for projections in weeks) / len(weeks) for pid in players}


def season_points_per_game(history: History) -> dict[str, float]:
    """The points per game of each player over the saved weeks in which he had a stat line, on any roster.

    PastWeek.positions holds a player in a week with a stat line. A week with a stat line and no points counts 0
    in the sum. A player with no stat line is not in the result, so he counts 0.
    """
    weeks: dict[str, list[float]] = {}
    for past in history.weeks.values():
        for pid in past.positions:
            weeks.setdefault(pid, []).append(player_points(past, pid) or 0.0)
    return {pid: sum(points) / len(points) for pid, points in weeks.items()}


def position_ranks(values: dict[str, float], positions: dict[str, str]) -> dict[str, int]:
    """The place of each player from 1 at his position by value, most first, among the players with a value.

    Only the positions in SLOT_POSITIONS, the positions with a line, get a rank. A player with no value has no rank,
    so he is below the line. The player id breaks a tie, so no two share a place.
    """
    ranks: dict[str, int] = {}
    for position in SLOT_POSITIONS:
        pool = sorted((pid for pid in values if positions.get(pid) == position), key=lambda pid: (-values[pid], pid))
        ranks.update({pid: place for place, pid in enumerate(pool, start=1)})
    return ranks


def roster_parts(inputs: SeasonInputs) -> dict[int, GradeParts]:
    """The four parts of the score of each roster of the snapshot, by roster id. GLOSSARY.md, "Roster grade"."""
    return {rid: read.parts(league) for rid, read, league in _league_reads(inputs)}


def roster_grades(inputs: SeasonInputs) -> dict[int, ManagerGrade]:
    """The grade of each roster of the snapshot by roster id. The slot ranks read the projections ahead only.

    The snapshot gives the rosters, the roster slots, and the positions. The injury status and the returns file play
    no part, so a starter out one week with a projection ahead is no hole.
    """
    reads = _league_reads(inputs)
    ranks = {position: _ranks({rid: read.position_total(position) for rid, read, _ in reads})
             for position in SLOT_POSITIONS}
    parts = {rid: read.parts(league) for rid, read, league in reads}
    # With no chart every roster has trade value 0, so the roster id alone breaks that tie and sets the rank.
    part_ranks = {key: _ranks({rid: getattr(parts[rid], key) for rid in parts}) for key in GRADE_WEIGHTS}
    grades = {}
    for rid, read, _ in reads:
        slots = [SlotRank(position=position, rank=ranks[position][rid], depth=read.depth_word(position))
                 for position in SLOT_POSITIONS]
        grades[rid] = ManagerGrade(
            letter=grade_letter(grade_score(parts[rid])),
            slots=slots,
            parts=[PartRank(key=key, rank=part_ranks[key][rid]) for key in GRADE_WEIGHTS],
            read=grade_read(slots, config=inputs.snapshot.config),
        )
    return grades


class _League(NamedTuple):
    """The five reads of one roster against the league, each from 0 at the lowest roster to 1 at the highest."""
    places: float
    lineup: float
    production: float
    trade_value: float
    depth: float


def _league_reads(inputs: SeasonInputs) -> list[tuple[int, "_RosterRead", _League]]:
    """The read of each roster and its parts against the league, in roster id order."""
    snapshot, projections_ahead, chart = inputs.snapshot, inputs.projections_ahead, inputs.chart
    # The grade has no meaning without the rosters and the projections, so the caller checks for both first.
    if snapshot is None or projections_ahead is None:
        raise ValueError("the roster grade needs a snapshot and the projections ahead")
    values = projected_values(projections_ahead, snapshot.config)
    ranks_by_player = position_ranks(values, {pid: player.position for pid, player in snapshot.players.items()})
    per_game = season_points_per_game(inputs.history)
    reads = {rid: _RosterRead(snapshot, roster, values, ranks_by_player) for rid, roster in snapshot.rosters.items()}
    places = _against_league({rid: read.places_total() for rid, read in reads.items()})
    lineup = _against_league({rid: read.lineup_total for rid, read in reads.items()})
    production = _against_league({rid: read.best_lineup_total(per_game) for rid, read in reads.items()})
    # A player the chart does not list counts 0. With no chart, no roster has a trade value.
    trade_value = (_against_league({rid: sum(chart.values.get(pid, 0.0) for pid in snapshot.rosters[rid])
                                    for rid in reads})
                   if chart is not None else dict.fromkeys(reads, 0.0))
    depth = _against_league({rid: read.depth_total() for rid, read in reads.items()})
    return [(rid, reads[rid], _League(places[rid], lineup[rid], production[rid], trade_value[rid], depth[rid]))
            for rid in sorted(reads)]


def _against_league(totals: dict[int, float]) -> dict[int, float]:
    """Each total against the league, from 0 at the lowest roster to 1 at the highest."""
    low, high = min(totals.values()), max(totals.values())
    # With every roster equal, no roster is ahead of the league, so each takes the part in full.
    return {rid: 1.0 if high == low else float((total - low) / (high - low)) for rid, total in totals.items()}


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
        self.positions = positions
        filled = fill_slots(roster, snapshot.roster_positions, positions, {pid: self._value(pid) for pid in roster})
        starting = [StartingSlot(name=slot, player=pid, rank=None if pid is None else ranks.get(pid), roster_slot=slot)
                    for slot, pid in filled]
        # K and DEF have no line, so the grade reads only the slots of the positions in SLOT_POSITIONS. An empty slot is
        # a hole only when a lined player could fill it, so an empty FLEX counts in the score but at no position.
        self.slots = [slot for slot in starting
                      if self._position(slot) in SLOT_POSITIONS or (slot.player is None and slot.is_hole(snapshot))]
        self.lineup_total = sum(self._value(slot.player) for slot in self.slots if slot.player is not None)

    def best_lineup_total(self, values: dict[str, float]) -> float:
        """The total of the best lineup the values fill, over the starters at the positions in SLOT_POSITIONS.

        A player with no value counts 0. K and DEF have no line, so they count in neither lineup total.
        """
        points = {pid: values.get(pid, 0.0) for pid in self.roster}
        filled = fill_slots(self.roster, self.snapshot.roster_positions, self.positions, points)
        return sum(points[pid] for _, pid in filled if pid is not None and self.positions[pid] in SLOT_POSITIONS)

    def _value(self, player_id: str) -> float:
        """The projected value of the player. A player with no projection ahead counts 0."""
        return self.values.get(player_id, 0.0)

    def _position(self, slot: StartingSlot) -> str | None:
        """The position the slot counts for: its player's, or its fixed roster slot when it holds no player."""
        if slot.player is not None:
            return self.snapshot.players[slot.player].position
        return slot.roster_slot if slot.roster_slot in SLOT_POSITIONS else None

    def _at(self, position: str) -> list[StartingSlot]:
        return [slot for slot in self.slots if self._position(slot) == position]

    def position_total(self, position: str) -> float:
        """The projected value of the starters at the position, the FLEX starters included."""
        return sum(self._value(slot.player) for slot in self._at(position) if slot.player is not None)

    def above(self, position: str) -> int:
        """The depth at the position: the players, starters and bench, above the line. GLOSSARY.md, "Depth"."""
        line = self.snapshot.config.lines[position]
        return sum(1 for pid in self.roster
                   if self.snapshot.players[pid].position == position and self.ranks.get(pid, line + 1) <= line)

    def spares(self, position: str) -> int:
        """The players at the position inside the league's starter count, past the starters the roster has there.
        The score's depth part reads the line instead, so a backup still counts there."""
        bar = self.snapshot.config.grade_spare_rank[position]
        inside = sum(1 for pid in self.roster
                     if self.snapshot.players[pid].position == position and self.ranks.get(pid, bar + 1) <= bar)
        return max(0, inside - len(self._at(position)))

    def depth_word(self, position: str) -> Depth:
        return depth_word(self.spares(position), any(slot.is_hole(self.snapshot) for slot in self._at(position)))

    def places_total(self) -> float:
        """The mean of each starter's place against the line, before the league read. With no slot it is 0."""
        places = [self._place(slot) for slot in self.slots]
        return sum(places) / len(places) if places else 0.0

    def depth_total(self) -> float:
        """The depth before the league read: the mean of two reads. One is one less GRADE_HOLE_COST per hole, never
        under 0. The other is the mean over the positions of the depth against the starters plus the spares."""
        holes = sum(1 for slot in self.slots if slot.is_hole(self.snapshot))
        depth = [min(self.above(position), len(self._at(position)) + GRADE_DEPTH_SPARES)
                 / (len(self._at(position)) + GRADE_DEPTH_SPARES) for position in SLOT_POSITIONS]
        return (max(0.0, 1 - GRADE_HOLE_COST * holes) + sum(depth) / len(depth)) / 2

    def parts(self, league: "_League") -> GradeParts:
        """The four parts of the score from the league read alone, so each part runs 0 to 1 across the league."""
        return GradeParts(
            projection=(league.places + league.lineup) / 2,
            production=league.production,
            trade_value=league.trade_value,
            depth=league.depth,
        )

    def _place(self, slot: StartingSlot) -> float:
        """The starter against the line: 1 at rank 1, down to 1 / line at the line, and 0 below it or with no player."""
        if slot.player is None or slot.rank is None:
            return 0.0
        line = self.snapshot.config.lines[self._position(slot)]
        return max(0.0, (line + 1 - slot.rank) / line)
