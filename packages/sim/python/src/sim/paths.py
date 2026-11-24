"""
The Finish lists and the Paths of The Race. The sim loop writes the results of each run into a RunTable as it draws
them, and this module splits those runs by Finish and finds the Paths of each Finish by a greedy cover (decision 03).
"""
import math
from array import array
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

from league.models import OddsStatus
from sim.percent import shown, tenths
from sim.tunables import (
    ABOUT_RUNS,
    ANY_ORDER_SHARE,
    PATH_LIFT,
    PATH_ODDS,
    PATH_RUNS,
    PATH_SKIP_SHARE,
    PATH_TEAMS,
    PATHS_PER_FINISH,
    PLAN_ROOT_FOR,
    PLAN_ROOT_RUNS,
    ROOT_FOR_LIFT,
    SURE_BEAT,
    SURE_FINISH,
)

# The case of a Finish, which sets its copy (decision 06). "sure" is 99.5% or more, "none" is under 0.5%, "paths" has
# Paths that reach PATH_ODDS, "best" has one best Path below it, and "open" has no Path to show.
FinishCase = Literal["sure", "paths", "best", "open", "none"]
# The Goals whose Finishes hold Paths. A seed holds its Finish list only, to keep sim.json small (decision 03).
PATH_GOALS = ("spot", "bye")
Pair = tuple[int, int]
# The code of one result of a team in one week: 2 for a win of its game, plus 1 for a score above the median.
_WIN, _ABOVE = 2, 1
# The code of one game in one week: the first team of the pair won, the second won, or a tie.
_FIRST, _SECOND, _TIE = 0, 1, 2


@dataclass
class RunTable:
    """The results of each run, as the sim loop draws them: the weight, and for each team its more wins in the weeks
    left and its seed, 0 out of the playoffs. One byte per team and run, so the Path search reads no run record.

    For the Week plans and the Score to beat, it also holds the result code of each game of each regular week left,
    the drawn score of each opponent of a team of `pages` in each week, and for each team of `pages` its result code
    and its median line in each week. `pairs` holds the head-to-head pairs of each regular week left, in week order."""
    pairs: list[list[Pair]] = field(default_factory=list)
    pages: frozenset[int] = frozenset()
    median_game: bool = False
    weights: list[float] = field(default_factory=list)
    more: dict[int, bytearray] = field(default_factory=dict)
    seat: dict[int, bytearray] = field(default_factory=dict)
    # The code of each game, by week and pair: _FIRST, _SECOND, or _TIE.
    games: list[list[bytearray]] = field(default_factory=list)
    # The code of the result of each team of `pages` in each week: _WIN plus _ABOVE.
    results: dict[int, list[bytearray]] = field(default_factory=dict)
    # The drawn score of each opponent of a team of `pages`, by week and roster ID.
    scores: dict[int, dict[int, array]] = field(default_factory=dict)
    # The score that a team of `pages` must pass in each week to beat the median: the k-th highest of the other scores.
    lines: dict[int, list[array]] = field(default_factory=dict)

    def add(
        self, weight: float, more: Mapping[int, int], seat: Mapping[int, int],
        weeks: Sequence[tuple[frozenset[int], frozenset[int]]] = (), drawn: Mapping[int, Sequence[float]] | None = None,
    ) -> None:
        """Add one run. `weeks` holds the winners and the teams above the median of each regular week left, and
        `drawn` the drawn score of each team in each week, as the sim loop has them."""
        self.weights.append(weight)
        for rid, wins in more.items():
            self.more.setdefault(rid, bytearray()).append(wins)
            self.seat.setdefault(rid, bytearray()).append(seat.get(rid, 0))
        if not self.games:
            self.games = [[bytearray() for _ in pairs] for pairs in self.pairs]
        for i, (won, above) in enumerate(weeks):
            for (a, b), codes in zip(self.pairs[i], self.games[i], strict=True):
                codes.append(_FIRST if a in won else _SECOND if b in won else _TIE)
            for rid in self.pages:
                self.results.setdefault(rid, [bytearray() for _ in self.pairs])[i].append(
                    _WIN * (rid in won) + _ABOVE * (rid in above))
        if drawn is None or not self.pages:
            return
        if not self.scores:
            # The Score to beat reads the scores of the opponents of the teams of `pages` only, which keeps the loop of
            # a What-if short.
            self._opponents = [sorted({b if a == rid else a for a, b in pairs for rid in self.pages if rid in (a, b)})
                               for pairs in self.pairs]
            self.scores = {i: {rid: array("f") for rid in opponents} for i, opponents in enumerate(self._opponents)}
            self.lines = {rid: [array("f") for _ in self.pairs] for rid in self.pages}
        for i in range(len(weeks)):
            for rid, scores in self.scores[i].items():
                scores.append(drawn[rid][i])
            if not self.median_game:
                continue
            ordered = sorted((scores[i] for scores in drawn.values()), reverse=True)
            k = len(ordered) // 2
            top, below = ordered[k - 1], ordered[k]
            for rid in self.pages:
                # Without the team itself, the k-th highest score moves up one place when the team is in the top k.
                self.lines[rid][i].append(below if drawn[rid][i] >= top else top)


class Condition(BaseModel):
    """One condition of a Path: another team ends at the final record `record` or worse."""
    roster_id: int
    record: tuple[int, int]


class PlanGame(BaseModel):
    """One game to root for in one week of a Week plan: the winner to root for, and the odds of the Goal on the plan
    when it wins, in whole percent."""
    winner: int
    loser: int
    odds: int


class PlanWeek(BaseModel):
    """One week of a Week plan: the result of Your team, and the 1 or PLAN_ROOT_FOR games of the week to root for."""
    week: int
    opponent: int
    game: Literal["win", "loss"]
    # Above or below the median in a league with a median game. None with none.
    median: Literal["above", "below"] | None
    root_for: list[PlanGame]


class WeekPlan(BaseModel):
    """The results of Your team week by week on one Path or one Finish, in the most common order of its runs.
    GLOSSARY.md, "Week plan"."""
    weeks: list[PlanWeek]
    # True when the most common order holds under ANY_ORDER_SHARE of the runs, so other orders of the same wins work.
    any_order: bool
    # The odds of "Try it": the odds of the Goal over every run where the results of Your team follow the plan, by
    # the rule of the shown odds. A What-if of the plan draws the same runs with weights, so it gives the same odds
    # within the error of the sample.
    odds: int


class ScoreToBeat(BaseModel):
    """The scores that Your team needs in one week left, in whole points, from the score draws of the runs: the score
    with a 50% chance to win and the score with a SURE_BEAT chance, against the opponent and against the median."""
    week: int
    opponent: int
    win: int
    win_sure: int
    # None in a league with no median game.
    median: int | None
    median_sure: int | None


class Path(BaseModel):
    """A set of 1 to PATH_TEAMS conditions on other teams at one Finish. GLOSSARY.md, "Path"."""
    conditions: list[Condition]
    # How often the Path happens at its Finish, in percent of the runs of the Finish, with one decimal.
    chance: float
    # The odds of the Goal over the runs of the Finish where the Path happens, in whole percent.
    odds: int
    # The count of runs of the Finish where the Path happens. It is PATH_RUNS or more.
    runs: int
    # The Week plan of the Path. None in a file written before the Week plans.
    plan: WeekPlan | None = None


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
    # The Week plan of a Finish of a seed Goal, which holds no Path (decision 03). None for the spot and the bye, and
    # for a Finish with no way in.
    plan: WeekPlan | None = None


class _Bits:
    """The runs of a RunTable as bitsets, one bit per run, so an AND and a popcount split the runs at C speed."""

    def __init__(self, table: RunTable) -> None:
        self.table = table
        self.size = len(table.weights)
        # With equal weights a popcount gives each sum. A What-if has unequal weights, so a sum reads each weight.
        self.even = len(set(table.weights)) <= 1
        self.unit = table.weights[0] if table.weights else 0.0
        self._sums: list[list[float]] | None = None

    def of(self, codes: bytearray, match) -> int:
        """The runs whose code matches. Run i is bit i from the top, as the bytes run."""
        digits = bytes(49 if match(code) else 48 for code in range(256))
        return int(bytes(codes).translate(digits), 2) if codes else 0

    def mass(self, bits: int) -> float:
        """The sum of the weights of the runs in `bits`."""
        if self.even:
            return bits.bit_count() * self.unit
        tables = self._byte_sums()
        return sum(map(list.__getitem__, tables, bits.to_bytes(len(tables))))

    def _byte_sums(self) -> list[list[float]]:
        """For each byte of a bitset, the sum of the weights of the runs of each of its 256 values. A sum then reads one
        entry per byte, not one per run, which keeps the many sums of the Week plans of a What-if fast."""
        if self._sums is None:
            weights = self.table.weights
            count = (self.size + 7) // 8
            # Run i is bit i from the top, so the top byte holds the pad bits above run 0.
            pad = count * 8 - self.size
            self._sums = []
            for j in range(count):
                runs = [j * 8 + k - pad for k in range(8)]
                # Bit 7 - k of the byte is run runs[k]. Each value adds the weight of its lowest bit to the value without it.
                weight = [weights[runs[7 - b]] if runs[7 - b] >= 0 else 0.0 for b in range(8)]
                sums = [0.0] * 256
                for value in range(1, 256):
                    low = (value & -value).bit_length() - 1
                    sums[value] = sums[value & (value - 1)] + weight[low]
                self._sums.append(sums)
        return self._sums


def finish_lists(
    you: int, table: RunTable, goals: Mapping[str, OddsStatus], *, records: Mapping[int, tuple[int, int, float, float]],
    wins_left: int, weeks_left: int, spots: int, bye_count: int, effective_runs: int, weeks: Sequence[int] = (),
) -> dict[str, list[Finish]]:
    """The Finish list of each Goal of `you`, best Finish first. `goals` holds the status of each Goal by its key.
    The spot and the bye hold the Paths of each Finish, each with its Week plan. A Finish of a seed holds a Week plan
    of its own. `weeks` holds the regular weeks left, in the order of `table.pairs`. A Finish that no run reaches is
    left out."""
    if not goals or not table.weights:
        return {}
    bits = _Bits(table)
    planner = _Planner(bits, you, list(weeks)) if you in table.results else None
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
                held, case = _paths(bits, runs, reach, at_most, records, wins_left)
                for path, path_runs in held:
                    if planner is not None:
                        path.plan = planner.plan(path_runs, reach, status, weeks_left)
                    paths.append(path)
            plan = None
            if planner is not None and goal not in PATH_GOALS and case != "none":
                plan = planner.plan(runs, reach, status, weeks_left)
            chance = tenths(mass, total)
            finishes.append(Finish(
                more_wins=k, record=(wins + k, losses + wins_left - k), chance=chance,
                odds=shown(status, made, mass, weeks_left), about=chance / 100 * effective_runs < ABOUT_RUNS,
                case=case, paths=paths, plan=plan))
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
) -> tuple[list[tuple[Path, int]], FinishCase]:
    """The Paths of one open Finish by a greedy cover (decision 03), each with the runs where it holds. Each Path adds the condition with the best FOIL
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
        (Path(conditions=[Condition(roster_id=rid, record=(records[rid][0] + k, records[rid][1] + wins_left - k))
                          for rid, k in sorted(conditions)],
              chance=tenths(bits.mass(held), mass), odds=shown("open", bits.mass(held & reach), bits.mass(held), 1),
              runs=held.bit_count()), held)
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


class _Planner:
    """The Week plans of one team over the runs of a RunTable. It holds the runs of each result of the team in each
    week and of each side of each other game, as bitsets, so a plan is a few ANDs."""

    def __init__(self, bits: _Bits, you: int, weeks: list[int]) -> None:
        table = bits.table
        self.bits = bits
        self.you = you
        self.weeks = weeks
        codes = (_WIN + _ABOVE, _WIN, _ABOVE, 0) if table.median_game else (_WIN, 0)
        # The runs of each result code of Your team in each week, best result first.
        self.results = [[(code, bits.of(week, lambda c, code=code: c == code)) for code in codes]
                        for week in table.results[you]]
        self.pairs = table.pairs
        # The runs where each side of each game of each week wins, by week and pair.
        self.sides = [[(bits.of(game, lambda c: c == _FIRST), bits.of(game, lambda c: c == _SECOND))
                       for game in games] for games in table.games]

    def plan(self, runs: int, reach: int, status: OddsStatus, weeks_left: int) -> WeekPlan | None:
        """The Week plan over `runs`: the order of results that holds the most of `runs` (PRD, the Week plan). The
        pick reads no outcome, so the odds of "Try it" carry no pick of the luckiest order. As in the Path search, the
        pick counts runs, not weights, and only the odds it shows are sums of weights. None with no run."""
        orders = self._orders(runs)
        if not orders:
            return None
        best_count, best_codes, best_bits = max(orders, key=lambda order: order[0])
        bits = self.bits
        followed = runs & best_bits
        weeks = [self._week(i, code, followed, reach) for i, code in enumerate(best_codes)]
        return WeekPlan(weeks=weeks, any_order=best_count / runs.bit_count() < ANY_ORDER_SHARE,
                        odds=shown(status, bits.mass(best_bits & reach), bits.mass(best_bits), weeks_left))

    def _orders(self, pool: int) -> list[tuple[int, tuple[int, ...], int]]:
        """Each order of results of Your team that some run of `pool` holds: its count of runs in `pool`, its result
        code of each week, and every run that holds it. The search drops an order as soon as no run of `pool` holds it, so a
        long season stays small."""
        found: list[tuple[int, tuple[int, ...], int]] = []

        def walk(i: int, codes: tuple[int, ...], every: int, held: int) -> None:
            if not held:
                return
            if i == len(self.results):
                found.append((held.bit_count(), codes, every))
                return
            for code, runs in self.results[i]:
                walk(i + 1, (*codes, code), every & runs, held & runs)

        walk(0, (), (1 << self.bits.size) - 1, pool)
        return found

    def _week(self, i: int, code: int, followed: int, reach: int) -> PlanWeek:
        """Week `i` of a plan: the result `code` of Your team, and the games of the week whose winner lifts the odds
        of the Goal most over the `followed` runs, by ROOT_FOR_LIFT points or more."""
        bits = self.bits
        median = None if not self.bits.table.median_game else "above" if code & _ABOVE else "below"
        pairs = self.pairs[i]
        opponent = next(b if a == self.you else a for a, b in pairs if self.you in (a, b))
        base = followed.bit_count()
        odds0 = (followed & reach).bit_count() / base if base else 0.0
        rows: list[tuple[float, int, int, int]] = []
        for (a, b), sides in zip(pairs, self.sides[i], strict=True):
            if self.you in (a, b):
                continue
            best: tuple[float, int, int, int] | None = None
            for (winner, loser), side in (((a, b), sides[0]), ((b, a), sides[1])):
                part = followed & side
                count = part.bit_count()
                if count < PLAN_ROOT_RUNS:
                    continue
                lift = (part & reach).bit_count() / count - odds0
                if best is None or lift > best[0]:
                    best = (lift, winner, loser, part)
            if best is not None and best[0] * 100 >= ROOT_FOR_LIFT:
                rows.append(best)
        rows.sort(key=lambda row: -row[0])
        games = [PlanGame(winner=winner, loser=loser, odds=shown("open", bits.mass(part & reach), bits.mass(part), 1))
                 for _, winner, loser, part in rows[:PLAN_ROOT_FOR]]
        return PlanWeek(week=self.weeks[i], opponent=opponent, game="win" if code & _WIN else "loss", median=median,
                        root_for=games)


def scores_to_beat(you: int, table: RunTable, weeks: Sequence[int]) -> list[ScoreToBeat]:
    """The Score to beat of `you` in each regular week left, from the score draws of the runs. A score beats the
    opponent with the chance of the runs where the opponent scores less, so the score of a chance q is the q quantile
    of the opponent's drawn scores. The median works the same way on the median line of `you`."""
    if you not in table.results or not table.scores:
        return []
    out = []
    for i, week in enumerate(weeks):
        opponent = next(b if a == you else a for a, b in table.pairs[i] if you in (a, b))
        theirs = table.scores[i][opponent]
        line = table.lines[you][i] if table.median_game else None
        out.append(ScoreToBeat(
            week=week, opponent=opponent, win=_quantile(theirs, table.weights, 0.5),
            win_sure=_quantile(theirs, table.weights, SURE_BEAT),
            median=None if line is None else _quantile(line, table.weights, 0.5),
            median_sure=None if line is None else _quantile(line, table.weights, SURE_BEAT)))
    return out


def _quantile(values: Sequence[float], weights: Sequence[float], q: float) -> int:
    """The `q` quantile of `values` with `weights`, rounded to whole points: the least value with a share of the
    weight of q or more at or below it."""
    ordered = sorted(zip(values, weights, strict=True))
    goal = q * sum(weights)
    held = 0.0
    for value, weight in ordered:
        held += weight
        if held >= goal:
            return round(value)
    return round(ordered[-1][0])
