"""
The week card of The Race: for the next regular week, the odds of each Goal after each result of Your team, the root-for
list of every other game for each result, the median rooting, and the tiebreak gap, from the RunTable of one sim.
"""
from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import BaseModel

from league.models import OddsStatus
from sim.paths import _ABOVE, _FIRST, _SECOND, _WIN, PATH_GOALS, RunTable, _Bits, _seat_match
from sim.percent import shown, tenths
from sim.tunables import ABOUT_RUNS, MEDIAN_ROWS, ROOT_FOR_LIFT, TIE_POINTS, TIE_WINS


class CardRoot(BaseModel):
    """One other game of the week for one result of Your team: the side to root for and the odds of the Goal after
    each side wins, in whole percent. A game whose two odds differ by under ROOT_FOR_LIFT points does not matter, and
    the page reads that from the two odds, so the file holds no flag for it."""
    winner: int
    loser: int
    odds: int
    other: int


class CardMedian(BaseModel):
    """One other team whose median miss moves the odds of Your team: the odds of the Goal after it misses."""
    roster_id: int
    odds: int


class CardResult(BaseModel):
    """One result of Your team in the week and how likely it is. Each Goal of the card holds its odds after it."""
    game: Literal["win", "loss"]
    median: Literal["above", "below"] | None
    chance: float
    about: bool


class TieGap(BaseModel):
    """Another team across the edge of the Goal within TIE_WINS wins and TIE_POINTS Points For of Your team. `points`
    is the Points For of Your team minus theirs, with one decimal."""
    roster_id: int
    points: float


class CardGoal(BaseModel):
    """The week card for one Goal. Each list follows the order of `WeekCard.results`."""
    # The odds of the Goal after each result. None when no run has the result, as after a What-if of the week.
    odds: list[int | None]
    # For each result, every other head-to-head game of the week, by the lift, then by the standings place of the
    # loser. Empty for a seed and for a Goal that is not open, to keep sim.json small, as the Paths are (decision 03).
    root_for: list[list[CardRoot]] = []
    # For each result, the 1 or MEDIAN_ROWS other teams whose median miss lifts the odds most. Empty when `root_for`
    # is, and with no median game.
    median_root: list[list[CardMedian]] = []
    tiebreak: TieGap | None = None


class WeekCard(BaseModel):
    """The week card of the next regular week of Your team: its results, best first, and each Goal after them."""
    week: int
    opponent: int
    results: list[CardResult]
    goals: dict[str, CardGoal]


def week_card(
    you: int, table: RunTable, goals: Mapping[str, OddsStatus], *, records: Mapping[int, tuple[int, int, float, float]],
    spots: int, bye_count: int, effective_runs: int, weeks: Sequence[int], weeks_left: int,
) -> WeekCard | None:
    """The week card of `you` for the first of `weeks`, by a split of the runs of `table`. `goals` holds the
    status of each Goal by its key. None with no regular week left or no game of `you` that week."""
    if not goals or not weeks or not table.weights or you not in table.results:
        return None
    pairs = table.pairs[0]
    opponent = next((b if a == you else a for a, b in pairs if you in (a, b)), None)
    if opponent is None:
        return None
    bits = _Bits(table)
    total = bits.mass((1 << bits.size) - 1)
    median_game = table.median_game
    codes = (_WIN + _ABOVE, _WIN, _ABOVE, 0) if median_game else (_WIN, 0)
    results = [(code, bits.of(table.results[you][0], lambda c, code=code: c == code)) for code in codes]
    sides = [(bits.of(game, lambda c: c == _FIRST), bits.of(game, lambda c: c == _SECOND)) for game in table.games[0]]
    below = ({rid: bits.of(flags, lambda c: c == 0) for rid, flags in sorted(table.aboves.items()) if rid != you}
             if median_game else {})
    standings = sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2], -records[rid][3], rid))
    place = {rid: n for n, rid in enumerate(standings, start=1)}

    def about(mass: float) -> bool:
        # The flag reads the chance as the page shows it, as in the page block.
        return tenths(mass, total) / 100 * effective_runs < ABOUT_RUNS

    chances = [bits.mass(runs) for _, runs in results]
    cards = [CardResult(game="win" if code & _WIN else "loss",
                        median=None if not median_game else "above" if code & _ABOVE else "below",
                        chance=tenths(mass, total), about=about(mass))
             for (code, _), mass in zip(results, chances, strict=True)]
    out: dict[str, CardGoal] = {}
    for goal, status in goals.items():
        reach = bits.of(table.seat[you], _seat_match(goal, spots, bye_count))

        def odds(runs: int, reach: int = reach, status: OddsStatus = status) -> int | None:
            mass = bits.mass(runs)
            return shown(status, bits.mass(runs & reach), mass, weeks_left) if mass else None

        after = [odds(runs) for _, runs in results]
        card = CardGoal(odds=after)
        if goal in PATH_GOALS and status == "open":
            card.root_for = [_root_for(you, pairs, sides, runs, odds, place) if value is not None else []
                             for (_, runs), value in zip(results, after, strict=True)]
            if below:
                card.median_root = [_median_root(below, runs, value, odds, place) if value is not None else []
                                    for (_, runs), value in zip(results, after, strict=True)]
        if status == "open":
            edge = spots if goal == "spot" else bye_count if goal == "bye" else int(goal.removeprefix("seed-"))
            card.tiebreak = _tiebreak(you, records, standings, edge)
        out[goal] = card
    return WeekCard(week=weeks[0], opponent=opponent, results=cards, goals=out)


def _root_for(you, pairs, sides, runs, odds, place) -> list[CardRoot]:
    """Every other game of the week over `runs`: the side whose win gives the higher odds first. A tie of the odds
    roots for the loss of the team higher in the standings. The rows rank by the lift, then by the place of the loser."""
    found: list[tuple[int, int, CardRoot]] = []
    for (a, b), (first, second) in zip(pairs, sides, strict=True):
        if you in (a, b):
            continue
        one, two = odds(runs & first), odds(runs & second)
        if one is None or two is None:
            continue
        (winner, loser, win_odds), (_, _, lose_odds) = sorted(
            [(a, b, one), (b, a, two)], key=lambda side: (-side[2], place[side[1]]))
        found.append((win_odds - lose_odds, place[loser],
                      CardRoot(winner=winner, loser=loser, odds=win_odds, other=lose_odds)))
    found.sort(key=lambda row: (-row[0], row[1]))
    return [row for _, _, row in found]


def _median_root(below, runs, base, odds, place) -> list[CardMedian]:
    """The other teams whose median miss over `runs` lifts the odds most from `base`. The first always shows, so the
    card names the team that matters most, and each later one needs a lift of ROOT_FOR_LIFT points."""
    found = []
    for rid, missed in below.items():
        after = odds(runs & missed)
        if after is not None:
            found.append((after - base, place[rid], rid, after))
    found.sort(key=lambda row: (-row[0], row[1]))
    rows = []
    for n, (lift, _, rid, value) in enumerate(found[:MEDIAN_ROWS]):
        if n and lift < ROOT_FOR_LIFT:
            break
        rows.append(CardMedian(roster_id=rid, odds=value))
    return rows


def _tiebreak(you, records, standings, edge) -> TieGap | None:
    """The team nearest to `you` in the standings on the other side of the edge of the Goal, the last place of its
    seeds, within TIE_WINS wins and TIE_POINTS Points For. None when no team is that close."""
    place = {rid: n for n, rid in enumerate(standings, start=1)}
    inside = place[you] <= edge
    wins, points = records[you][0], records[you][2]
    close = [rid for rid in standings if rid != you and (place[rid] <= edge) != inside
             and abs(records[rid][0] - wins) <= TIE_WINS and abs(records[rid][2] - points) <= TIE_POINTS]
    if not close:
        return None
    other = min(close, key=lambda rid: (abs(place[rid] - place[you]), rid))
    return TieGap(roster_id=other, points=round(points - records[other][2], 1))
