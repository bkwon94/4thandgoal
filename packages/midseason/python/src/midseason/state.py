"""
The state of the league, the first chapter of Act I: each team's full record, points for and against, the streak,
and the playoff odds, in standings order. It reads the saved history of the season and the odds that the app hands in.
"""
from collections.abc import Mapping
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from league.models import History
from league.numbers import r2
from league.standings_table import head_to_head, standings_order, week_median


class Streak(BaseModel):
    """Head-to-head wins or losses in a row, newest week back. The median game never counts, and a tie ends it."""
    kind: Literal["W", "L"]
    length: int


class TeamState(BaseModel):
    """One row of the state of the league. GLOSSARY.md, "Median game": in CPC the full record counts both games."""
    roster_id: int
    name: str
    # The place in the standings: most wins first, then most points for, as the weekly standings order them.
    rank: int
    wins: int
    losses: int
    ties: int
    # The sum of the weekly scores, the same sum as the standings. The season total of Sleeper can differ after a
    # stat correction, so the report never reads it.
    points_for: float
    # The sum of the head-to-head opponent's score of each week. The median game has no opponent.
    points_against: float
    # None when the team has no head-to-head result yet, or its last game was a tie.
    streak: Streak | None
    # The playoff odds in whole percent that the app hands in. None when the app has no odds for the team.
    playoff_odds: int | None


class LeagueState(BaseModel):
    """The facts of the state of the league: one row per team, in standings order."""
    teams: list[TeamState]


def _streak(history: History, roster_id: int, through: int) -> Streak | None:
    run = 0
    for number in range(through, 0, -1):
        game = head_to_head(history.weeks[number], roster_id)
        if game is None:
            continue
        _, result = game
        if result == 0 or (run and result != (1 if run > 0 else -1)):
            break
        run += result
    if run == 0:
        return None
    return Streak(kind="W" if run > 0 else "L", length=abs(run))


def league_state(
    history: History, through: int, names: Mapping[int, str], *, playoff_odds: Mapping[int, int],
    median_game: bool = True,
) -> LeagueState:
    """The state of the league over weeks 1 to `through` of `history`.

    `playoff_odds` is the port of the odds: the app hands in the playoff odds by roster ID, so the report imports
    no odds engine. With `median_game` off, the league scores no median game, so each week is one game.
    """
    wins: dict[int, int] = {}
    losses: dict[int, int] = {}
    ties: dict[int, int] = {}
    points_for: dict[int, Decimal] = {}
    points_against: dict[int, Decimal] = {}

    def settle(roster_id: int, mine: Decimal, theirs: Decimal) -> None:
        if mine > theirs:
            wins[roster_id] += 1
        elif mine < theirs:
            losses[roster_id] += 1
        else:
            ties[roster_id] += 1

    for number in range(1, through + 1):
        week = history.weeks[number]
        # Exact decimals, so a sum of many scores never drifts from the standings.
        scores = {rid: Decimal(str(points)) for rid, points in week.scores.items()}
        for rid in scores:
            for table in (wins, losses, ties):
                table.setdefault(rid, 0)
            points_for.setdefault(rid, Decimal(0))
            points_against.setdefault(rid, Decimal(0))
        for a, b in week.pairs:
            settle(a, scores[a], scores[b])
            settle(b, scores[b], scores[a])
            points_against[a] += scores[b]
            points_against[b] += scores[a]
        median = week_median(week) if median_game else None
        for rid, score in scores.items():
            if median is not None:
                settle(rid, score, median)
            points_for[rid] += score

    records = {rid: (wins[rid], losses[rid], r2(float(points_for[rid]))) for rid in points_for}
    return LeagueState(teams=[
        TeamState(
            roster_id=rid,
            name=names[rid],
            rank=place,
            wins=wins[rid],
            losses=losses[rid],
            ties=ties[rid],
            points_for=records[rid][2],
            points_against=r2(float(points_against[rid])),
            streak=_streak(history, rid, through),
            playoff_odds=playoff_odds.get(rid),
        )
        for place, rid in enumerate(standings_order(records), start=1)
    ])
