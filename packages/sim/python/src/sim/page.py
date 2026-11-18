"""
The page block of the season sim: the numbers of the sim page for one team, each by a split of the runs of one
weighted sim (decision 07), and the league fact of the Sim tile. sim.json and the What-if share this one shape.
"""
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from league.models import OddsStatus
from sim.percent import shown, tenths
from sim.tunables import ABOUT_RUNS, IN_ODDS, RACE_FLOOR, ROOT_FOR_LIFT, ROOT_FOR_ROWS

Pair = tuple[int, int]
Reason = Literal["2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you",
                 "In the race for the last spot"]
# The reason of a root-for row by the gap in real wins from the loser to Your team. Any other gap is the race reason.
_REASONS: dict[int, Reason] = {2: "2 wins ahead of you", 1: "1 win ahead of you", 0: "Level with you",
                               -1: "1 win behind you"}
_RACE: Reason = "In the race for the last spot"


@dataclass(frozen=True)
class RunRecord:
    """What the page block reads of one run: its weight, the regular-season wins, the playoff teams, and for each
    regular week left the winners of the head-to-head games and the teams above the median."""
    weight: float
    wins: dict[int, int]
    made: frozenset[int]
    weeks: list[tuple[frozenset[int], frozenset[int]]]


class LadderStep(BaseModel):
    """One count of more wins in the weeks left. A head-to-head win and a win over the median each count one."""
    more_wins: int
    # The playoff odds over the runs with this count. None when no run has it.
    playoff: int | None
    # The chance of the count in percent of all runs, with one decimal.
    chance: float
    about: bool


class WeekResult(BaseModel):
    """One result of Your team in one week: the game, and the median in a league with a median game."""
    game: Literal["win", "loss"]
    median: Literal["above", "below"] | None
    wins_added: int
    # The playoff odds after the result. None when no run has it.
    playoff: int | None
    chance: float
    about: bool


class RootFor(BaseModel):
    """One result of another game that lifts the odds of Your team after a loss."""
    winner: int
    loser: int
    reason: Reason
    # The playoff odds after a loss of Your team and this result, in whole points.
    playoff: int
    about: bool


class PageWeek(BaseModel):
    """One regular week left, for Your team."""
    week: int
    opponent: int
    # Four results with a median game, best first: win above, win below, loss above, loss below. Two with none.
    results: list[WeekResult]
    # The playoff odds over all runs where Your team loses its game. A tie is a loss, as in a set result.
    loss_playoff: int | None
    loss_about: bool
    # At most ROOT_FOR_ROWS rows, by the lift, then by the standings place of the loser.
    root_for: list[RootFor]


class SimPage(BaseModel):
    """The page block of one team. The page reads one shape before and after a What-if."""
    you: int
    playoff: int
    status: OddsStatus
    # The real wins and losses at the start of the sim. The median game counts in both.
    record: tuple[int, int]
    weeks_left: int
    # The most more wins the weeks left can give.
    wins_left: int
    # The smallest count of more wins with playoff odds of IN_ODDS or more. None when no count reaches it.
    need: int | None
    sentence: str
    ladder: list[LadderStep]
    weeks: list[PageWeek]


def team_page(
    you: int, runs: Sequence[RunRecord], *, playoff: int, status: OddsStatus,
    records: Mapping[int, tuple[int, int, float]], schedule: Mapping[int, list[Pair]], median_game: bool,
    effective_runs: int,
) -> SimPage:
    """The page block of `you` by a split of the `runs` of one sim. `schedule` holds the pairs of each regular week
    left, in the order of `RunRecord.weeks`. `playoff` and `status` are the odds of the team over all runs."""
    regular = sorted(schedule)
    weeks_left = len(regular)
    per_week = 2 if median_game else 1
    wins_left = per_week * weeks_left
    total = 0.0
    ladder: list[list[float]] = [[0.0, 0.0] for _ in range(wins_left + 1)]
    results: list[defaultdict[tuple[bool, bool], list[float]]] = [defaultdict(lambda: [0.0, 0.0]) for _ in regular]
    losses: list[list[float]] = [[0.0, 0.0] for _ in regular]
    winners: list[defaultdict[int, list[float]]] = [defaultdict(lambda: [0.0, 0.0]) for _ in regular]
    for run in runs:
        weight, made = run.weight, you in run.made
        total += weight
        step = ladder[run.wins[you] - records[you][0]]
        step[0] += weight
        step[1] += weight if made else 0.0
        for i, (won, above) in enumerate(run.weeks):
            win = you in won
            cell = results[i][(win, median_game and you in above)]
            cell[0] += weight
            cell[1] += weight if made else 0.0
            if win:
                continue
            losses[i][0] += weight
            losses[i][1] += weight if made else 0.0
            for rid in won:
                side = winners[i][rid]
                side[0] += weight
                side[1] += weight if made else 0.0

    def odds(part: list[float]) -> int | None:
        return shown(status, part[1], part[0], weeks_left) if part[0] else None

    def about(part: float) -> bool:
        # The flag reads the chance as the page shows it, so a reader of the file gets the same flag from its numbers.
        return tenths(part, total) / 100 * effective_runs < ABOUT_RUNS

    steps = [LadderStep(more_wins=k, playoff=odds(part), chance=tenths(part[0], total), about=about(part[0]))
             for k, part in enumerate(ladder)]
    need = next((s.more_wins for s in steps if s.playoff is not None and s.playoff >= IN_ODDS), None)
    table = sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2], rid))
    place = {rid: n for n, rid in enumerate(table, start=1)}
    combos: list[tuple[bool, bool, Literal["win", "loss"], Literal["above", "below"] | None]] = (
        [(True, True, "win", "above"), (True, False, "win", "below"), (False, True, "loss", "above"),
         (False, False, "loss", "below")] if median_game else [(True, False, "win", None), (False, False, "loss", None)])
    weeks = []
    for i, week in enumerate(regular):
        opponent = next((b if a == you else a for a, b in schedule[week] if you in (a, b)), None)
        if opponent is None:
            continue
        week_results = [
            WeekResult(game=game, median=median, wins_added=(game == "win") + (median == "above"),
                       playoff=odds(results[i][(win, up)]), chance=tenths(results[i][(win, up)][0], total),
                       about=about(results[i][(win, up)][0]))
            for win, up, game, median in combos]
        loss_playoff = odds(losses[i])
        rows = _root_for(you, schedule[week], winners[i], loss_playoff, odds, about, records, place)
        weeks.append(PageWeek(week=week, opponent=opponent, results=week_results, loss_playoff=loss_playoff,
                              loss_about=about(losses[i][0]), root_for=rows))
    return SimPage(you=you, playoff=playoff, status=status, record=(records[you][0], records[you][1]),
                   weeks_left=weeks_left, wins_left=wins_left, need=need,
                   sentence=_sentence(status, need, wins_left, steps), ladder=steps, weeks=weeks)


def _root_for(
    you: int, pairs: list[Pair], winners: Mapping[int, list[float]], loss_playoff: int | None, odds, about,
    records: Mapping[int, tuple[int, int, float]], place: Mapping[int, int],
) -> list[RootFor]:
    """The root-for rows of one week: for each other game, the side whose win lifts the odds after a loss the most.
    A row stays when it lifts them by ROOT_FOR_LIFT whole points or more. The rows rank by the lift, then by the
    standings place of the loser, so a loss of a team higher in the table comes first."""
    if loss_playoff is None:
        return []
    found: list[tuple[int, int, RootFor]] = []
    for a, b in pairs:
        if you in (a, b):
            continue
        sides = []
        for winner, loser in ((a, b), (b, a)):
            after = odds(winners.get(winner, [0.0, 0.0]))
            if after is not None:
                sides.append((after - loss_playoff, winner, loser, after))
        if not sides:
            continue
        lift, winner, loser, after = max(sides, key=lambda side: (side[0], -place[side[2]]))
        if lift < ROOT_FOR_LIFT:
            continue
        reason = _REASONS.get(records[loser][0] - records[you][0], _RACE)
        found.append((lift, place[loser], RootFor(winner=winner, loser=loser, reason=reason, playoff=after,
                                                  about=about(winners[winner][0]))))
    found.sort(key=lambda row: (-row[0], row[1]))
    return [row for _, _, row in found[:ROOT_FOR_ROWS]]


def _sentence(status: OddsStatus, need: int | None, wins_left: int, ladder: list[LadderStep]) -> str:
    """The one line of more wins: the smallest count with playoff odds of IN_ODDS or more."""
    if status == "in":
        return "You're in."
    if status == "out":
        return "You're out of the playoff race."
    if need == 0:
        return f"You're in at {IN_ODDS}% or better even with no more wins."
    if need is not None:
        return f"Win {need} of the {wins_left} left and you're in."
    best = ladder[-1].playoff
    return f"Win all {wins_left} left for a {best}% shot." if best is not None else "No run gives you a playoff spot."


def league_fact(playoff: Mapping[int, int], spots: int, weeks_left: int) -> str | None:
    """The league fact of the Sim tile in the regular season: the race for the last spots. A team at IN_ODDS or more
    is safe, and a team from RACE_FLOOR to under IN_ODDS is in the race. None with no regular week left."""
    if not weeks_left:
        return None
    safe = sum(odds >= IN_ODDS for odds in playoff.values())
    race = sum(RACE_FLOOR <= odds < IN_ODDS for odds in playoff.values())
    left = spots - safe
    if not 0 < left < race:
        return "The playoff field is all but set"
    return f"{race} managers fight for the last {'spot' if left == 1 else f'{left} spots'}"
