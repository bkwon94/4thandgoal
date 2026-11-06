"""
Schedule luck and the Schedule swap, the second chapter of Act I: All-play wins, Schedule luck, points against, the
close-game record, and the 12 by 12 grid of each team's record under every schedule. Decision ticket 06 sets the rules.
"""
from collections.abc import Iterator
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, Fact, History, PastWeek
from league.numbers import r2
from league.standings_table import week_median
from midseason.state import LeagueState

# A head-to-head margin under this many points is a close game. Decision ticket 06.
CLOSE_GAME_MARGIN = Decimal(5)


class TeamLuck(BaseModel):
    """One row of the Schedule luck table. A tie counts half a win in each count."""
    roster_id: int
    name: str
    head_to_head_wins: float
    # The sum of the weekly all-play win rates. GLOSSARY.md, "All-play wins".
    all_play_wins: float
    # Head-to-head wins minus All-play wins. The median game stays out, because its result depends only on the
    # team's own score.
    schedule_luck: float
    # The two context lines. Neither feeds a measure, an arc, or a rank. The rank puts the most points against first.
    points_against: float
    points_against_rank: int
    close_wins: int
    close_losses: int
    close_ties: int


class SwapCell(BaseModel):
    """The record of the row team with the schedule of `schedule_of`. A league with a median game adds the row team's
    own median results, so the diagonal is the full record of the standings."""
    schedule_of: int
    wins: int
    losses: int
    ties: int


class SwapRow(BaseModel):
    roster_id: int
    name: str
    cells: list[SwapCell]


class BestMissed(BaseModel):
    """The best schedule other than its own for one team, with the record that it gives."""
    roster_id: int
    schedule_of: int
    wins: int
    losses: int
    ties: int


class MostBetter(BaseModel):
    """The callout of the team with the most schedules that give it a better record than its own, and the count."""
    roster_id: int
    count: int
    # The place of the team in the ranking. The spread rule gives the callout to the next team when the #1 team holds
    # 3 headlines, so the place is then 2 or more.
    place: int = 1


class BiggestMiss(BaseModel):
    """The callout of the team with the most wins to gain from the best schedule that it missed."""
    roster_id: int
    schedule_of: int
    # The wins of the best schedule minus the real wins. A tie counts half.
    gain: float
    place: int = 1


class ScheduleSwap(BaseModel):
    """The grid: a row is a team, a column is a schedule, both in standings order."""
    rows: list[SwapRow]
    best_missed: list[BestMissed]
    most_better: MostBetter | None
    # None when no team gains a win from another schedule.
    biggest_miss: BiggestMiss | None = None


class ScheduleLuck(BaseModel):
    """The facts of the Schedule luck chapter: the table, most luck first, and the swap."""
    teams: list[TeamLuck]
    swap: ScheduleSwap


class LuckChapter(BaseModel):
    """Schedule luck with the Schedule swap, a chapter of Act I."""
    key: Literal["luck"] = "luck"
    title: str = "Schedule Luck"
    facts: ScheduleLuck
    blurb: Blurb | None = None


def _scores(week: PastWeek) -> dict[int, Decimal]:
    return {rid: Decimal(str(points)) for rid, points in week.scores.items()}


def _opponent(week: PastWeek, roster_id: int) -> int | None:
    return next((b if a == roster_id else a for a, b in week.pairs if roster_id in (a, b)), None)


def _result(mine: Decimal, theirs: Decimal) -> int:
    return (mine > theirs) - (mine < theirs)


def _weeks(history: History, through: int) -> Iterator[PastWeek]:
    return (history.weeks[number] for number in range(1, through + 1) if number in history.weeks)


def _swap_cell(history: History, through: int, row: int, schedule_of: int, median_game: bool) -> SwapCell:
    """Team `row` plays the opponent of `schedule_of` each week with its own score. In the week that `schedule_of`
    played `row`, `row` plays `schedule_of`."""
    tally = {1: 0, -1: 0, 0: 0}
    for week in _weeks(history, through):
        scores = _scores(week)
        if row not in scores:
            continue
        opponent = _opponent(week, schedule_of)
        if opponent == row:
            opponent = schedule_of
        if opponent is not None and opponent in scores:
            tally[_result(scores[row], scores[opponent])] += 1
        if median_game:
            tally[_result(scores[row], week_median(week))] += 1
    return SwapCell(schedule_of=schedule_of, wins=tally[1], losses=tally[-1], ties=tally[0])


def _rate(cell: SwapCell) -> float:
    return cell.wins + cell.ties / 2


def _swap(history: History, through: int, state: LeagueState, median_game: bool) -> ScheduleSwap:
    order = [team.roster_id for team in state.teams]
    rows = [SwapRow(roster_id=team.roster_id, name=team.name,
                    cells=[_swap_cell(history, through, team.roster_id, col, median_game) for col in order])
            for team in state.teams]
    best_missed = []
    for row in rows:
        others = [cell for cell in row.cells if cell.schedule_of != row.roster_id]
        # max keeps the first of a tie, and the cells are in standings order, so the higher place wins a tie.
        best = max(others, key=_rate)
        best_missed.append(BestMissed(roster_id=row.roster_id, schedule_of=best.schedule_of, wins=best.wins,
                                      losses=best.losses, ties=best.ties))
    swap = ScheduleSwap(rows=rows, best_missed=best_missed, most_better=None)
    most, biggest = swap_rankings(swap)
    return _with_callouts(swap, (most[0], 1) if most else None, (biggest[0], 1) if biggest else None)


def _own(row: SwapRow) -> SwapCell:
    return next(cell for cell in row.cells if cell.schedule_of == row.roster_id)


def _better(row: SwapRow) -> int:
    return sum(1 for cell in row.cells if cell.schedule_of != row.roster_id and _rate(cell) > _rate(_own(row)))


def _gain(swap: ScheduleSwap, roster_id: int) -> float:
    row = next(row for row in swap.rows if row.roster_id == roster_id)
    best = next(best for best in swap.best_missed if best.roster_id == roster_id)
    return _rate(SwapCell(schedule_of=best.schedule_of, wins=best.wins, losses=best.losses, ties=best.ties)) - _rate(
        _own(row))


def swap_rankings(swap: ScheduleSwap) -> tuple[list[int], list[int]]:
    """The rankings of the two swap callouts, the #1 first: the most schedules better than its own, then the most
    wins to gain from the best schedule. A team with none is in no ranking. A tie keeps the standings order."""
    most = sorted((row for row in swap.rows if _better(row)), key=lambda row: -_better(row))
    biggest = sorted((row for row in swap.rows if _gain(swap, row.roster_id) > 0),
                     key=lambda row: -_gain(swap, row.roster_id))
    return [row.roster_id for row in most], [row.roster_id for row in biggest]


def _with_callouts(swap: ScheduleSwap, most_better: tuple[int, int] | None,
                   biggest_miss: tuple[int, int] | None) -> ScheduleSwap:
    most = None
    if most_better is not None:
        rid, place = most_better
        most = MostBetter(roster_id=rid, count=_better(next(row for row in swap.rows if row.roster_id == rid)),
                          place=place)
    biggest = None
    if biggest_miss is not None:
        rid, place = biggest_miss
        best = next(best for best in swap.best_missed if best.roster_id == rid)
        biggest = BiggestMiss(roster_id=rid, schedule_of=best.schedule_of, gain=_gain(swap, rid), place=place)
    return swap.model_copy(update={"most_better": most, "biggest_miss": biggest})


def with_swap_callouts(luck: ScheduleLuck, *, most_better: tuple[int, int] | None,
                       biggest_miss: tuple[int, int] | None) -> ScheduleLuck:
    """Schedule luck with the two swap callouts on the teams that the spread rule chose, each as (roster ID, place).
    None leaves the callout empty. The table and the grid still show every team."""
    return luck.model_copy(update={"swap": _with_callouts(luck.swap, most_better, biggest_miss)})


def schedule_luck(history: History, through: int, state: LeagueState, *, median_game: bool = True) -> ScheduleLuck:
    """Schedule luck of each team over weeks 1 to `through`, and the Schedule swap. A week with no score for a team
    does not count for it. `state` gives the names and the standings order."""
    h2h: dict[int, Decimal] = {team.roster_id: Decimal(0) for team in state.teams}
    all_play = {rid: Decimal(0) for rid in h2h}
    against = {rid: Decimal(0) for rid in h2h}
    close = {rid: {1: 0, -1: 0, 0: 0} for rid in h2h}
    for week in _weeks(history, through):
        scores = _scores(week)
        for rid, score in scores.items():
            others = [_result(score, theirs) for other, theirs in scores.items() if other != rid]
            if others:
                all_play[rid] += sum((Decimal(r + 1) / 2 for r in others), Decimal(0)) / len(others)
            opponent = _opponent(week, rid)
            if opponent is None or opponent not in scores:
                continue
            result = _result(score, scores[opponent])
            h2h[rid] += Decimal(result + 1) / 2
            against[rid] += scores[opponent]
            if abs(score - scores[opponent]) < CLOSE_GAME_MARGIN:
                close[rid][result] += 1
    names = {team.roster_id: team.name for team in state.teams}
    teams = [
        TeamLuck(
            roster_id=rid,
            name=names[rid],
            head_to_head_wins=float(h2h[rid]),
            all_play_wins=r2(float(all_play[rid])),
            schedule_luck=r2(float(h2h[rid] - all_play[rid])),
            points_against=r2(float(against[rid])),
            # A shared total shares the rank, and the next rank skips.
            points_against_rank=1 + sum(1 for other in against.values() if other > against[rid]),
            close_wins=close[rid][1],
            close_losses=close[rid][-1],
            close_ties=close[rid][0],
        )
        for rid in h2h
    ]
    # sorted is stable, so a tie keeps the standings order.
    teams.sort(key=lambda team: -team.schedule_luck)
    return ScheduleLuck(teams=teams, swap=_swap(history, through, state, median_game))


def _cell_record(n: Nums, wins: int, losses: int, ties: int) -> str:
    return n.text(f"{wins}-{losses}-{ties}") if ties else n.record(wins, losses)


def luck_facts(luck: ScheduleLuck) -> list[Fact]:
    """The facts of the Schedule luck chapter: the luck, points against, and the close games of each team, the best
    schedule that each team missed, and the team with the most records better than its own."""
    facts = []
    names = {team.roster_id: team.name for team in luck.teams}
    for team in luck.teams:
        prefix = f"SL.{team.roster_id}"
        n = Nums()
        # The luck and its two parts are two facts, so each holds two numbers at most, as a sentence may.
        facts.append(fact(f"{prefix}.luck",
                          f"{team.name} has a Schedule luck of {n.text(f'{team.schedule_luck:+.2f}')}, its "
                          f"head-to-head wins minus its All-play wins.", n, [team.name], []))
        n = Nums()
        facts.append(fact(f"{prefix}.wins",
                          f"{team.name} has {n(team.head_to_head_wins)} head-to-head wins and {n(team.all_play_wins)} "
                          f"All-play wins.", n, [team.name], []))
        n = Nums()
        facts.append(fact(f"{prefix}.against",
                          f"{team.name} has {n(team.points_against)} points against, "
                          f"{n.ord(team.points_against_rank)} most in the league.", n, [team.name], []))
        n = Nums()
        close = _cell_record(n, team.close_wins, team.close_losses, team.close_ties)
        facts.append(fact(f"{prefix}.close",
                          f"{team.name} is {close} in close games, with a margin under {n(int(CLOSE_GAME_MARGIN))} points.",
                          n, [team.name], []))
    own = {row.roster_id: next(cell for cell in row.cells if cell.schedule_of == row.roster_id)
           for row in luck.swap.rows}
    for best in luck.swap.best_missed:
        name, other, mine = names[best.roster_id], names[best.schedule_of], own[best.roster_id]
        n = Nums()
        facts.append(fact(f"SW.{best.roster_id}.best",
                          f"{name} would be {_cell_record(n, best.wins, best.losses, best.ties)} with the schedule of "
                          f"{other}, its top record with any schedule, against "
                          f"{_cell_record(n, mine.wins, mine.losses, mine.ties)} for real.",
                          n, [name, other], []))
    if luck.swap.most_better is not None:
        most = luck.swap.most_better
        n = Nums()
        facts.append(fact("SW.most",
                          f"{names[most.roster_id]} has a better record with {n(most.count)} other schedules than "
                          f"with its own, {_most(n, most.place)} in the league.", n, [names[most.roster_id]], []))
    if luck.swap.biggest_miss is not None:
        miss = luck.swap.biggest_miss
        n = Nums()
        wins = "win" if miss.gain == 1 else "wins"
        facts.append(fact("SW.biggest",
                          f"{names[miss.roster_id]} would gain {n(miss.gain)} {wins} with the schedule of "
                          f"{names[miss.schedule_of]}, {_most(n, miss.place)} of any team.", n,
                          [names[miss.roster_id], names[miss.schedule_of]], []))
    return facts


def _most(n: Nums, place: int) -> str:
    """"the most" for the #1 team of a callout, or "the 2nd most" for a team that the spread rule moved it to."""
    return "the most" if place == 1 else f"the {n.ord(place)} most"
