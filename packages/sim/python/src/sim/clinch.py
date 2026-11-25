"""
The Clinch lines of the League board: each way that a set of results of this week makes a team Clinched or Out of a
spot or a bye, by the plain check on wins. An exact count of every set of results of this week, in the weekly build only.
"""
from collections.abc import Mapping, Sequence
from itertools import product
from typing import Literal

from league.standings_table import roster_status
from sim.goals import ClinchLine, ClinchWay, GameResult, MedianResult
from sim.percent import tenths
from sim.tunables import CLINCH_WAYS

Pair = tuple[int, int]


# One condition on the results of this week: ("game", winner, loser) or ("median", roster, "above" or "below").
_Atom = tuple[str, int, int | str]


def clinch_lines(
    records: Mapping[int, tuple[int, int, float, float]], pairs: Sequence[Pair], *, weeks_left: int, spots: int,
    bye_count: int, median_game: bool, runs: Sequence[tuple[float, frozenset[int], frozenset[int]]],
) -> dict[int, list[ClinchLine]]:
    """The Clinch lines of each team by roster ID, for the spot and the bye, of the week whose head-to-head `pairs`
    come next. `runs` holds the weight, the winners, and the teams above the median of this week in each run of the
    sim, for the chance of each way. A team already Clinched or Out of a Goal has no line for it."""
    rosters = sorted(records)
    sets = _every_set(rosters, pairs, median_game)
    index = {s: i for i, s in enumerate(sets)}
    weight = [0.0] * len(sets)
    for w, winners, above in runs:
        i = index.get((winners, above if median_game else frozenset()))
        # A tied game fits no set, so its run counts in no chance.
        if i is not None:
            weight[i] += w
    total = sum(w for w, _, _ in runs) or 1.0
    atoms = _atom_bits(sets, rosters, pairs, median_game)
    goals: dict[Literal["spot", "bye"], int] = {"spot": spots}
    if bye_count:
        goals["bye"] = bye_count
    status_bits: dict[tuple[int, str, str], int] = {}
    for i, (winners, above) in enumerate(sets):
        after = {r: (records[r][0] + (r in winners) + (r in above), records[r][1], records[r][2], records[r][3])
                 for r in rosters}
        for r in rosters:
            for goal, k in goals.items():
                status = roster_status(r, after, weeks_left - 1, k, median_game=median_game)
                if status != "open":
                    status_bits[(r, goal, status)] = status_bits.get((r, goal, status), 0) | 1 << i
    out: dict[int, list[ClinchLine]] = {}
    for r in rosters:
        lines = []
        for goal, k in goals.items():
            if roster_status(r, dict(records), weeks_left, k, median_game=median_game) != "open":
                continue
            for status in ("in", "out"):
                target = status_bits.get((r, goal, status), 0)
                if target:
                    ways = _ways(r, target, atoms, weight, total, len(sets), pairs, median_game)
                    lines.append(ClinchLine(goal=goal, status=status, ways=ways))
        out[r] = lines
    return out


def _every_set(rosters: list[int], pairs: Sequence[Pair], median_game: bool) -> list[tuple[frozenset, frozenset]]:
    """Each set of results of the week: the winners, and the teams above the median. A winner outscores its loser, so a
    loser above the median has its winner above it too, and exactly half the league is above the line."""
    half = len(rosters) // 2
    # Each game gives its winner and loser: both above, the winner alone above, or both below.
    sides = [(set(), set())]
    for a, b in pairs:
        grown = []
        for winner, loser in ((a, b), (b, a)):
            options = [(winner, loser), (winner,), ()] if median_game else [()]
            for won, above in sides:
                for up in options:
                    grown.append((won | {winner}, above | set(up)))
        sides = grown
    sets = [(frozenset(won), frozenset(above)) for won, above in sides if not median_game or len(above) == half]
    return sorted(set(sets), key=lambda s: (sorted(s[0]), sorted(s[1])))


def _atom_bits(sets, rosters, pairs, median_game) -> dict[_Atom, int]:
    """The sets that fit each condition, as one bit per set."""
    bits: dict[_Atom, int] = {}
    for i, (winners, above) in enumerate(sets):
        for a, b in pairs:
            winner, loser = (a, b) if a in winners else (b, a)
            bits[("game", winner, loser)] = bits.get(("game", winner, loser), 0) | 1 << i
        if median_game:
            for r in rosters:
                key = ("median", r, "above" if r in above else "below")
                bits[key] = bits.get(key, 0) | 1 << i
    return bits


def _ways(rid, target, atoms, weight, total, count, pairs, median_game) -> list[ClinchWay]:
    """The ways that cover the sets of `target` by a greedy cover: each way takes a result of the team itself, then
    adds the result of another team that keeps the most sets of the target, until each set that fits is in it."""
    every = (1 << count) - 1
    opponent = next(b if a == rid else a for a, b in pairs if rid in (a, b))
    own_game = {"win": atoms[("game", rid, opponent)], "loss": atoms[("game", opponent, rid)], None: every}
    own_median = ({"above": atoms[("median", rid, "above")], "below": atoms[("median", rid, "below")], None: every}
                  if median_game else {None: every})
    others = [a for a in atoms if rid not in (a[1], a[2])]

    def mass(bits: int) -> float:
        return sum(weight[i] for i in _members(bits))

    left = target
    found = []
    while left and len(found) < CLINCH_WAYS:
        best = None
        for game, median in product(own_game, own_median):
            way = _one_way(own_game[game] & own_median[median], target, left, others, atoms)
            if way is None:
                continue
            rule, fit = way
            # Drop each part that the way does not need, so "any loss" reads as one result.
            game, median, rule, fit = _pruned(game, median, rule, own_game, own_median, atoms, target, left)
            key = (mass(fit & left), (fit & left).bit_count(), -len(rule))
            if best is None or key > best[0]:
                best = (key, game, median, rule, fit)
        if best is None:
            break
        _, game, median, rule, fit = best
        found.append(ClinchWay(game=game, median=median, others=[_result(a) for a in rule],
                               chance=tenths(mass(fit), total)))
        left &= ~fit
    return sorted(found, key=lambda way: -way.chance)


def _one_way(start, target, left, others, atoms):
    """The results of other teams that make every set of `start` that fits them a set of `target`, or None."""
    fit, rule = start, []
    if not fit & left:
        return None
    while fit & ~target:
        best = None
        for atom in others:
            if atom in rule or (atom[0] == "game" and ("game", atom[2], atom[1]) in rule):
                continue
            kept = fit & atoms[atom]
            if not kept & target & left:
                continue
            key = ((kept & target).bit_count() / kept.bit_count(), (kept & target & left).bit_count())
            if best is None or key > best[0]:
                best = (key, atom, kept)
        if best is None:
            return None
        rule.append(best[1])
        fit = best[2]
    return rule, fit


def _pruned(game, median, rule, own_game, own_median, atoms, target, left):
    """The way with each result left out that keeps every fitting set in `target` and still covers a set of `left`."""
    def fit_of(g, m, r):
        bits = own_game[g] & own_median[m]
        for atom in r:
            bits &= atoms[atom]
        return bits

    def holds(g, m, r):
        bits = fit_of(g, m, r)
        return bits & left and not bits & ~target

    for atom in list(rule):
        rest = [a for a in rule if a != atom]
        if holds(game, median, rest):
            rule = rest
    if median is not None and holds(game, None, rule):
        median = None
    if game is not None and holds(None, median, rule):
        game = None
    return game, median, rule, fit_of(game, median, rule)


def _members(bits: int):
    i = 0
    while bits:
        if bits & 1:
            yield i
        bits >>= 1
        i += 1


def _result(atom: _Atom) -> GameResult | MedianResult:
    if atom[0] == "game":
        return GameResult(winner=int(atom[1]), loser=int(atom[2]))
    return MedianResult(roster_id=int(atom[1]), median="above" if atom[2] == "above" else "below")
