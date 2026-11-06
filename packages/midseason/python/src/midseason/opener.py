"""
The opener of the midseason report, the title race: the title odds of the leaders and of the record leader. Decision
ticket 09 sets it. The app hands in the title odds of the sim, so the report imports no sim.
"""
from collections.abc import Mapping

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, Fact
from midseason.state import LeagueState

# The key of the prose block of the opener.
OPENER = "opener"
# The count of teams with the best title odds that the opener names.
LEADERS = 3


class TitleLeader(BaseModel):
    roster_id: int
    name: str
    # The title odds in percent of all runs of the sim, with one decimal.
    title_odds: float


class RecordLeader(BaseModel):
    """The team first in the standings, with its record and its title odds."""
    roster_id: int
    name: str
    wins: int
    losses: int
    ties: int
    # None when the app has no title odds for the team.
    title_odds: float | None
    # The place of its title odds in the league, best first. A shared value shares the place.
    title_rank: int | None


class TitleRace(BaseModel):
    """The facts of the opener: the leaders by title odds, best first, and the record leader."""
    leaders: list[TitleLeader]
    record_leader: RecordLeader


class Opener(BaseModel):
    """The top of the report. GLOSSARY.md, "Opener"."""
    title: str = "The title race"
    facts: TitleRace
    blurb: Blurb | None = None
    roast: Blurb | None = None


class ReportTile(BaseModel):
    """The one big fact of the home tile after the takeover ends. GLOSSARY.md, "Report tile"."""
    label: str
    value: str
    note: str


def report_tile(race: TitleRace) -> ReportTile:
    """The tile of the title race: the title odds of the favorite. With no title odds, the record of the record leader."""
    if race.leaders:
        best = race.leaders[0]
        return ReportTile(label="Title favorite", value=f"{best.title_odds:.1f}%", note=best.name)
    top = race.record_leader
    record = f"{top.wins}-{top.losses}" + (f"-{top.ties}" if top.ties else "")
    return ReportTile(label="Record leader", value=record, note=top.name)


def _rank(odds: Mapping[int, float], value: float) -> int:
    return 1 + sum(1 for other in odds.values() if other > value)


def title_race(state: LeagueState, title_odds: Mapping[int, float]) -> TitleRace:
    """The title race from `title_odds`, the port of the title odds: the app hands in the odds by roster ID.

    A tie of the title odds keeps the standings order.
    """
    names = {team.roster_id: team.name for team in state.teams}
    order = [team.roster_id for team in state.teams if team.roster_id in title_odds]
    best = sorted(order, key=lambda rid: -title_odds[rid])[:LEADERS]
    top = state.teams[0]
    odds = title_odds.get(top.roster_id)
    return TitleRace(
        leaders=[TitleLeader(roster_id=rid, name=names[rid], title_odds=title_odds[rid]) for rid in best],
        record_leader=RecordLeader(roster_id=top.roster_id, name=top.name, wins=top.wins, losses=top.losses,
                                   ties=top.ties, title_odds=odds,
                                   title_rank=_rank(title_odds, odds) if odds is not None else None),
    )


def _place(n: Nums, rank: int) -> str:
    return "the best in the league" if rank == 1 else f"{n.ord(rank)} best in the league"


def title_race_facts(race: TitleRace) -> list[Fact]:
    """The facts of the opener: one fact per leader and one for the record leader."""
    odds = {leader.roster_id: leader.title_odds for leader in race.leaders}
    facts = []
    for leader in race.leaders:
        n = Nums()
        facts.append(fact(f"OP.{leader.roster_id}.title",
                          f"{leader.name} has {n(leader.title_odds)}% title odds, "
                          f"{_place(n, _rank(odds, leader.title_odds))}.", n, [leader.name], []))
    top = race.record_leader
    if top.title_odds is not None and top.title_rank is not None:
        n = Nums()
        record = n.text(f"{top.wins}-{top.losses}-{top.ties}") if top.ties else n.record(top.wins, top.losses)
        facts.append(fact("OP.record",
                          f"{top.name} leads the standings at {record} and has {n(top.title_odds)}% title odds, "
                          f"{_place(n, top.title_rank)}.", n, [top.name], []))
    return facts
