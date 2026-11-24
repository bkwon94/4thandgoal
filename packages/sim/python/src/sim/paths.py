"""
The Finish lists and the Paths of The Race. The sim loop writes the results of each run into a RunTable as it draws
them, and this module splits those runs by Finish and finds the Paths of each Finish by a greedy cover (decision 03).
"""
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

from league.models import OddsStatus
from sim.percent import shown, tenths
from sim.tunables import (
    ABOUT_RUNS,
    PATH_LIFT,
    PATH_ODDS,
    PATH_RUNS,
    PATH_SKIP_SHARE,
    PATH_TEAMS,
    PATHS_PER_FINISH,
    SURE_FINISH,
)

# The case of a Finish, which sets its copy (decision 06). "sure" is 99.5% or more, "none" is under 0.5%, "paths" has
# Paths that reach PATH_ODDS, "best" has one best Path below it, and "open" has no Path to show.
FinishCase = Literal["sure", "paths", "best", "open", "none"]
# The Goals whose Finishes hold Paths. A seed holds its Finish list only, to keep sim.json small (decision 03).
PATH_GOALS = ("spot", "bye")


@dataclass
class RunTable:
    """The results of each run, as the sim loop draws them: the weight, and for each team its more wins in the weeks
    left and its seed, 0 out of the playoffs. One byte per team and run, so the Path search reads no run record."""
    weights: list[float] = field(default_factory=list)
    more: dict[int, bytearray] = field(default_factory=dict)
    seat: dict[int, bytearray] = field(default_factory=dict)

    def add(self, weight: float, more: Mapping[int, int], seat: Mapping[int, int]) -> None:
        self.weights.append(weight)
        for rid, wins in more.items():
            self.more.setdefault(rid, bytearray()).append(wins)
            self.seat.setdefault(rid, bytearray()).append(seat.get(rid, 0))


class Condition(BaseModel):
    """One condition of a Path: another team ends at the final record `record` or worse."""
    roster_id: int
    record: tuple[int, int]


class Path(BaseModel):
    """A set of 1 to PATH_TEAMS conditions on other teams at one Finish. GLOSSARY.md, "Path"."""
    conditions: list[Condition]
    # How often the Path happens at its Finish, in percent of the runs of the Finish, with one decimal.
    chance: float
    # The odds of the Goal over the runs of the Finish where the Path happens, in whole percent.
    odds: int
    # The count of runs of the Finish where the Path happens. It is PATH_RUNS or more.
    runs: int


class Finish(BaseModel):
    """One count of more wins in the weeks left, with the median results counted. GLOSSARY.md, "Finish"."""
    more_wins: int
    # The final record at this Finish: the record now plus the wins and the losses of the Finish.
    record: tuple[int, int]
    # The chance of the Finish in percent of all runs, with one decimal.
    chance: float
    # The odds of the Goal over the runs of the Finish.
    odds: int
    about: bool
    case: FinishCase
    paths: list[Path] = []


class _Bits:
    """The runs of a RunTable as bitsets, one bit per run, so an AND and a popcount split the runs at C speed."""

    def __init__(self, table: RunTable) -> None:
        self.table = table
        self.size = len(table.weights)
        # With equal weights a popcount gives each sum. A What-if has unequal weights, so a sum reads each weight.
        self.even = len(set(table.weights)) <= 1
        self.unit = table.weights[0] if table.weights else 0.0

    def of(self, codes: bytearray, match) -> int:
        """The runs whose code matches. Run i is bit i from the top, as the bytes run."""
        digits = bytes(49 if match(code) else 48 for code in range(256))
        return int(bytes(codes).translate(digits), 2) if codes else 0

    def mass(self, bits: int) -> float:
        """The sum of the weights of the runs in `bits`."""
        if self.even:
            return bits.bit_count() * self.unit
        marks = format(bits, f"0{self.size}b")
        return sum(w for w, mark in zip(self.table.weights, marks, strict=True) if mark == "1")


def finish_lists(
    you: int, table: RunTable, goals: Mapping[str, OddsStatus], *, records: Mapping[int, tuple[int, int, float, float]],
    wins_left: int, weeks_left: int, spots: int, bye_count: int, effective_runs: int,
) -> dict[str, list[Finish]]:
    """The Finish list of each Goal of `you`, best Finish first. `goals` holds the status of each Goal by its key.
    The spot and the bye hold the Paths of each Finish. A Finish that no run reaches is left out."""
    if not goals or not table.weights:
        return {}
    bits = _Bits(table)
    every = (1 << bits.size) - 1
    total = bits.mass(every)
    finish_bits = {k: bits.of(table.more[you], lambda code, k=k: code == k) for k in range(wins_left + 1)}
    # "Ends at k more wins or fewer" of each other team, for k below the most it can win.
    at_most = {rid: [bits.of(table.more[rid], lambda code, k=k: code <= k) for k in range(wins_left)]
               for rid in sorted(table.more) if rid != you}
    wins, losses = records[you][:2]
    out: dict[str, list[Finish]] = {}
    for goal, status in goals.items():
        reach = bits.of(table.seat[you], _seat_match(goal, spots, bye_count))
        finishes = []
        for k in range(wins_left, -1, -1):
            runs = finish_bits[k]
            mass = bits.mass(runs)
            if not mass:
                continue
            made = bits.mass(runs & reach)
            share = made / mass
            case: FinishCase = "sure" if share >= SURE_FINISH else "none" if share < 1 - SURE_FINISH else "open"
            paths: list[Path] = []
            if case == "open" and goal in PATH_GOALS:
                paths, case = _paths(bits, runs, reach, at_most, records, wins_left)
            chance = tenths(mass, total)
            finishes.append(Finish(
                more_wins=k, record=(wins + k, losses + wins_left - k), chance=chance,
                odds=shown(status, made, mass, weeks_left), about=chance / 100 * effective_runs < ABOUT_RUNS,
                case=case, paths=paths))
        out[goal] = finishes
    return out


def _seat_match(goal: str, spots: int, bye_count: int):
    """The seeds that reach `goal`: 1 to the spots, 1 to the byes, or one seed."""
    if goal == "spot":
        return lambda seat: 1 <= seat <= spots
    if goal == "bye":
        return lambda seat: 1 <= seat <= bye_count
    seed = int(goal.removeprefix("seed-"))
    return lambda seat: seat == seed


def _paths(
    bits: _Bits, runs: int, reach: int, at_most: Mapping[int, list[int]],
    records: Mapping[int, tuple[int, int, float, float]], wins_left: int,
) -> tuple[list[Path], FinishCase]:
    """The Paths of one open Finish by a greedy cover (decision 03). Each Path adds the condition with the best FOIL
    gain over the runs the Paths before it do not cover, and stops at PATH_ODDS or at PATH_TEAMS teams. A Path keeps
    PATH_RUNS runs or more, and a repeated Path ends the search. When the first Path stays under PATH_ODDS, the Finish
    keeps it alone as its best chance."""
    size = runs.bit_count()
    left = runs & reach
    found: list[tuple[frozenset[tuple[int, int]], int]] = []
    for _ in range(PATHS_PER_FINISH):
        conditions, held = _cover(runs, reach, left, at_most, size)
        if not conditions or any(conditions == seen for seen, _ in found):
            break
        found.append((conditions, held))
        left &= ~held
        if not left:
            break
    if not found:
        return [], "open"

    def odds_of(held: int) -> float:
        return bits.mass(held & reach) / bits.mass(held)

    first = found[0]
    if odds_of(first[1]) < PATH_ODDS / 100:
        chosen, case = [first], "best"
    else:
        chosen, case = [path for path in found if odds_of(path[1]) >= PATH_ODDS / 100], "paths"
    mass = bits.mass(runs)
    paths = [
        Path(conditions=[Condition(roster_id=rid, record=(records[rid][0] + k, records[rid][1] + wins_left - k))
                         for rid, k in sorted(conditions)],
             chance=tenths(bits.mass(held), mass), odds=shown("open", bits.mass(held & reach), bits.mass(held), 1),
             runs=held.bit_count())
        for conditions, held in chosen]
    return paths, case


def _cover(
    runs: int, reach: int, left: int, at_most: Mapping[int, list[int]], size: int,
) -> tuple[frozenset[tuple[int, int]], int]:
    """One Path of the greedy cover: its conditions as (roster id, most more wins), and the runs where it holds. The
    search counts runs, not weights, so a What-if picks its Paths on the runs it drew."""
    held = runs
    conditions: set[tuple[int, int]] = set()
    while len(conditions) < PATH_TEAMS:
        n0 = held.bit_count()
        p0 = (held & left).bit_count()
        odds0 = (held & reach).bit_count() / n0
        if odds0 >= PATH_ODDS / 100 or not p0:
            break
        best: tuple[float, int, int, int] | None = None
        used = {rid for rid, _ in conditions}
        for rid, limits in at_most.items():
            if rid in used:
                continue
            for k, limit in enumerate(limits):
                # A condition true in most runs of the Finish says almost nothing.
                if (runs & limit).bit_count() > PATH_SKIP_SHARE * size:
                    continue
                part = held & limit
                n1 = part.bit_count()
                if n1 < PATH_RUNS:
                    continue
                p1 = (part & left).bit_count()
                if not p1 or (part & reach).bit_count() / n1 - odds0 < PATH_LIFT / 100:
                    continue
                gain = p1 * (math.log(p1 / n1) - math.log(p0 / n0))
                if best is None or gain > best[0]:
                    best = (gain, rid, k, part)
        if best is None:
            break
        _, rid, k, held = best
        conditions.add((rid, k))
    return frozenset(conditions), held
