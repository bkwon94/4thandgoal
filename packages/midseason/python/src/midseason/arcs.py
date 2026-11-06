"""
The arcs, a chapter of Act I: the shape of each team's season, found from the data. Decision ticket 05 sets the eight
arcs, the start and now windows, the streak arcs, the luck arcs, the 2-arc limit, and the order by the swing.
"""
from collections.abc import Mapping
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, Fact, History
from league.numbers import r2
from league.standings_table import head_to_head, week_median
from midseason.state import LeagueState

# The set of decision ticket 05, in its order. A tie of the swing goes to the arc earlier in this list.
ArcKind = Literal["Turnaround", "Collapse", "Wire to wire", "Never got going", "Roller coaster", "Snakebit",
                  "Smoke and mirrors", "Heater"]
ARC_ORDER: list[ArcKind] = ["Turnaround", "Collapse", "Wire to wire", "Never got going", "Roller coaster",
                            "Snakebit", "Smoke and mirrors", "Heater"]

# The start is weeks 1 to 4. Now is the last 4 weeks through the week of the report.
WINDOW_WEEKS = 4
# Good is a win rate of 60% or more in a window, and bad is 40% or less. Brian loosened the lines from 65% and 35% on
# 2026-11-05, because the real CPC week 8 data gave only 4 arcs.
GOOD_RATE = 0.6
BAD_RATE = 0.4
# An active head-to-head win streak of this length or more is a Heater.
HEATER_STREAK = 4
# Two head-to-head streaks of this length or more, in opposite directions, are a Roller coaster.
ROLLER_STREAK = 3
# Schedule luck at or beyond this line gives Smoke and mirrors (plus) or Snakebit (minus). Decision ticket 06.
LUCK_LINE = 1.5
MAX_ARCS = 2


class WindowRecord(BaseModel):
    """The full record of one window: the head-to-head game plus the median game in a league that has one."""
    first_week: int
    last_week: int
    wins: int
    losses: int
    ties: int

    @property
    def rate(self) -> float | None:
        games = self.wins + self.losses + self.ties
        # A tie counts half a win.
        return (self.wins + self.ties / 2) / games if games else None


class Arc(BaseModel):
    """One arc of a team with the numbers behind it. Each arc fills only the numbers that it reads."""
    kind: ArcKind
    # The size of the swing on a 0 to 1 scale. The page orders a team's arcs by it, the biggest first.
    swing: float
    start: WindowRecord | None = None
    now: WindowRecord | None = None
    # The longest head-to-head win streak and loss streak of a Roller coaster, or the active win streak of a Heater.
    win_streak: int | None = None
    loss_streak: int | None = None
    schedule_luck: float | None = None


class TeamArcs(BaseModel):
    roster_id: int
    name: str
    # At most 2 arcs, the biggest swing first. A team may have none.
    arcs: list[Arc]


class Arcs(BaseModel):
    """The facts of the arcs chapter: one row per team, in standings order."""
    teams: list[TeamArcs]


class ArcsChapter(BaseModel):
    """The arcs, a chapter of Act I."""
    key: Literal["arcs"] = "arcs"
    title: str = "Arcs"
    facts: Arcs
    blurb: Blurb | None = None
    roast: Blurb | None = None


def _window(history: History, roster_id: int, first: int, last: int, median_game: bool) -> WindowRecord:
    tally = {1: 0, -1: 0, 0: 0}
    for number in range(first, last + 1):
        week = history.weeks.get(number)
        if week is None or roster_id not in week.scores:
            continue
        game = head_to_head(week, roster_id)
        if game is not None:
            tally[game[1]] += 1
        if median_game:
            score = Decimal(str(week.scores[roster_id]))
            median = week_median(week)
            tally[(score > median) - (score < median)] += 1
    return WindowRecord(first_week=first, last_week=last, wins=tally[1], losses=tally[-1], ties=tally[0])


def _streaks(history: History, roster_id: int, through: int) -> tuple[list[int], int]:
    """The head-to-head results of each week with a game, oldest first, and the count of those games. The median game
    never counts."""
    results = []
    for number in range(1, through + 1):
        week = history.weeks.get(number)
        game = head_to_head(week, roster_id) if week is not None else None
        if game is not None:
            results.append(game[1])
    return results, len(results)


def _longest(results: list[int], kind: int) -> int:
    best = run = 0
    for result in results:
        # A tie ends a streak, as on the streak of the standings.
        run = run + 1 if result == kind else 0
        best = max(best, run)
    return best


def _active_wins(results: list[int]) -> int:
    run = 0
    for result in reversed(results):
        if result != 1:
            break
        run += 1
    return run


def _candidates(history: History, through: int, roster_id: int, luck: float | None, median_game: bool) -> list[Arc]:
    arcs: list[Arc] = []
    start = _window(history, roster_id, 1, min(WINDOW_WEEKS, through), median_game)
    now = _window(history, roster_id, max(1, through - WINDOW_WEEKS + 1), through, median_game)
    if start.rate is not None and now.rate is not None:
        s, n = start.rate, now.rate
        kind: ArcKind | None = None
        swing = 0.0
        if s <= BAD_RATE and n >= GOOD_RATE:
            kind, swing = "Turnaround", n - s
        elif s >= GOOD_RATE and n <= BAD_RATE:
            kind, swing = "Collapse", s - n
        elif s >= GOOD_RATE and n >= GOOD_RATE:
            kind, swing = "Wire to wire", min(s, n)
        elif s <= BAD_RATE and n <= BAD_RATE:
            kind, swing = "Never got going", 1 - max(s, n)
        if kind is not None:
            arcs.append(Arc(kind=kind, swing=r2(swing), start=start, now=now))
    results, games = _streaks(history, roster_id, through)
    if games:
        wins, losses = _longest(results, 1), _longest(results, -1)
        if wins >= ROLLER_STREAK and losses >= ROLLER_STREAK:
            arcs.append(Arc(kind="Roller coaster", swing=r2(min(1.0, (wins + losses) / games)),
                            win_streak=wins, loss_streak=losses))
        active = _active_wins(results)
        if active >= HEATER_STREAK:
            arcs.append(Arc(kind="Heater", swing=r2(active / games), win_streak=active))
        if luck is not None and abs(luck) >= LUCK_LINE:
            # Schedule luck cannot pass the count of head-to-head games, so the share stays on the 0 to 1 scale.
            arcs.append(Arc(kind="Snakebit" if luck < 0 else "Smoke and mirrors",
                            swing=r2(min(1.0, abs(luck) / games)), schedule_luck=luck))
    return arcs


def team_arcs(
    history: History, through: int, state: LeagueState, luck: Mapping[int, float], *, median_game: bool = True,
) -> Arcs:
    """The arcs of each team over weeks 1 to `through`. `luck` is the Schedule luck by roster ID. With `median_game`
    on, the window arcs count the median game, so an arc agrees with the standings."""
    teams = []
    for team in state.teams:
        found = _candidates(history, through, team.roster_id, luck.get(team.roster_id), median_game)
        found.sort(key=lambda arc: (-arc.swing, ARC_ORDER.index(arc.kind)))
        teams.append(TeamArcs(roster_id=team.roster_id, name=team.name, arcs=found[:MAX_ARCS]))
    return Arcs(teams=teams)


def _record(n: Nums, record: WindowRecord) -> str:
    if record.ties:
        return n.text(f"{record.wins}-{record.losses}-{record.ties}")
    return n.record(record.wins, record.losses)


# The length of an arc window as a word. The verifier takes a number word that the cited fact holds.
COUNT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]


def _count_word(window: WindowRecord) -> str:
    return COUNT_WORDS[window.last_week - window.first_week + 1]


def _arc_text(name: str, arc: Arc, n: Nums) -> str:
    """The plain sentence of one arc with the numbers behind it."""
    head = f"{name} has the {arc.kind} arc"
    if arc.start is not None and arc.now is not None:
        start, now = arc.start, arc.now
        # The windows read as words, so the fact holds two numbers, as a sentence of the writer may.
        return (f"{head}: {_record(n, start)} in the first {_count_word(start)} weeks and {_record(n, now)} in the "
                f"last {_count_word(now)}.")
    if arc.kind == "Roller coaster":
        return (f"{head}: a head-to-head win streak of {n(arc.win_streak or 0)} and a head-to-head loss streak of "
                f"{n(arc.loss_streak or 0)}.")
    if arc.kind == "Heater":
        return f"{head}: {n(arc.win_streak or 0)} head-to-head wins in a row, and the streak is still alive."
    return f"{head}: a Schedule luck of {n.text(f'{arc.schedule_luck or 0:+.2f}')}."


def arcs_facts(arcs: Arcs) -> list[Fact]:
    """The facts of the arcs chapter: one fact per arc, with the id of the team and the arc."""
    facts = []
    for team in arcs.teams:
        for arc in team.arcs:
            n = Nums()
            slug = arc.kind.lower().replace(" ", "-")
            facts.append(fact(f"ARC.{team.roster_id}.{slug}", _arc_text(team.name, arc, n), n, [team.name], []))
    return facts
