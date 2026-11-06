"""
The look ahead, the first chapter of Act III: each team's games left in the regular season with the opponents' records,
and the win rate of those opponents. The app hands in the pairs of the weeks left from the saved league data.
"""
from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, Fact
from league.numbers import r2
from midseason.state import LeagueState, TeamState

Pair = tuple[int, int]
# The key of the chapter and of its prose block.
LOOK_AHEAD = "look-ahead"


class Game(BaseModel):
    """One game left, with the full record of the opponent at the week of the report."""
    week: int
    opponent: int
    name: str
    wins: int
    losses: int
    ties: int


class TeamLookAhead(BaseModel):
    roster_id: int
    name: str
    games: list[Game]
    # The wins of all the opponents over their games, with a tie as half a win. None when the team has no game left.
    opponents_rate: float | None


class LookAhead(BaseModel):
    """The facts of the look ahead: one row per team, the softest schedule first, and the two ends."""
    teams: list[TeamLookAhead]
    softest: int | None
    hardest: int | None


class LookAheadChapter(BaseModel):
    """The look ahead, the first chapter of Act III."""
    key: Literal["look-ahead"] = "look-ahead"
    title: str = "The look ahead"
    facts: LookAhead
    blurb: Blurb | None = None
    roast: Blurb | None = None


def _game(week: int, opponent: TeamState) -> Game:
    return Game(week=week, opponent=opponent.roster_id, name=opponent.name, wins=opponent.wins,
                losses=opponent.losses, ties=opponent.ties)


def _rate(games: Sequence[Game]) -> float | None:
    played = sum(game.wins + game.losses + game.ties for game in games)
    return r2(sum(game.wins + game.ties / 2 for game in games) / played) if played else None


def look_ahead(state: LeagueState, schedule: Mapping[int, Sequence[Pair]]) -> LookAhead:
    """The look ahead of each team. `schedule` holds the head-to-head pairs of each regular week left, by week.

    The rate sums the opponents' records, so an opponent met twice counts twice. The median game has no opponent, so
    it adds no game, but each opponent's record is the full record of the standings.
    """
    teams = {team.roster_id: team for team in state.teams}
    rows = []
    for team in state.teams:
        games = [_game(week, teams[b if a == team.roster_id else a])
                 for week in sorted(schedule) for a, b in schedule[week] if team.roster_id in (a, b)]
        rows.append(TeamLookAhead(roster_id=team.roster_id, name=team.name, games=games,
                                  opponents_rate=_rate(games)))
    rated = [row for row in rows if row.opponents_rate is not None]
    # sorted is stable, so a tie keeps the standings order. A team with no game left goes last.
    rows.sort(key=lambda row: (row.opponents_rate is None, row.opponents_rate or 0.0))
    softest = min(rated, key=lambda row: row.opponents_rate or 0.0).roster_id if rated else None
    hardest = max(rated, key=lambda row: row.opponents_rate or 0.0).roster_id if rated else None
    return LookAhead(teams=rows, softest=softest, hardest=hardest)


def look_ahead_facts(look: LookAhead) -> list[Fact]:
    """One fact per team with games left: the win rate of its opponents and its place from the softest schedule. The
    last fact holds the weeks ahead."""
    facts = []
    rates = [team.opponents_rate for team in look.teams if team.opponents_rate is not None]
    for team in look.teams:
        if team.opponents_rate is None:
            continue
        n = Nums()
        head = f"{team.name} faces opponents with a {n(team.opponents_rate)} win rate in the weeks ahead, the"
        if team.roster_id == look.softest:
            place = "softest schedule"
        elif team.roster_id == look.hardest:
            place = "hardest schedule"
        else:
            # A shared rate shares the place.
            place = f"{n.ord(1 + sum(1 for rate in rates if rate < team.opponents_rate))} softest schedule"
        facts.append(fact(f"LA.{team.roster_id}.rate", f"{head} {place}.", n, [team.name], []))
    # The weeks are their own fact, so each rate fact holds two numbers at most, as a sentence of the writer may.
    weeks = [game.week for team in look.teams for game in team.games]
    if weeks:
        n = Nums()
        facts.append(fact("LA.weeks", f"The weeks ahead are weeks {n(min(weeks))} to {n(max(weeks))}.", n, [], []))
    return facts
