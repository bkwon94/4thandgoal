"""
The lineup choices, a chapter of Act II: the Bench points of each team over the season, and each loss that its best
lineup would have won. GLOSSARY.md, "Bench points" and "Best lineup".
"""
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.history import player_points
from league.lineup import fill_slots
from league.models import Blurb, Fact, History, PastWeek
from league.numbers import r2


class LostWeek(BaseModel):
    """A head-to-head loss of one team that its best lineup would have won."""
    week: int
    opponent_roster_id: int
    opponent: str
    score: float
    # The points of the best lineup of the week, from the real points.
    best: float
    bench_points: float
    # The points the team lost by.
    margin: float


class TeamLineup(BaseModel):
    roster_id: int
    name: str
    # The place by Bench points, most first. A tie keeps the order of the names.
    rank: int
    # The Bench points of weeks 1 to the report week.
    bench_points: float
    # The losses that the best lineup would have won, oldest first.
    lost_with_better: list[LostWeek]


class LineupChoices(BaseModel):
    """The facts of the lineup choices: one row per team, most Bench points first."""
    teams: list[TeamLineup]


class LineupChapter(BaseModel):
    """The lineup choices, a chapter of Act II."""
    key: Literal["lineup"] = "lineup"
    title: str = "Lineup choices"
    facts: LineupChoices
    blurb: Blurb | None = None
    roast: Blurb | None = None


def best_score(past: PastWeek, roster_id: int, slots: Sequence[str], positions: Mapping[str, str]) -> Decimal:
    """The points of the best lineup of the roster in the week, by the real points of each player.

    A player with no position fills no slot. He scored no points, so he never belongs in a best lineup.
    """
    roster = [pid for pid in past.rosters.get(roster_id, []) if pid in past.positions or pid in positions]
    where = {pid: past.positions.get(pid) or positions[pid] for pid in roster}
    points: dict[str, Decimal | float] = {pid: Decimal(str(player_points(past, pid) or 0)) for pid in roster}
    return sum((Decimal(points[pid]) for _, pid in fill_slots(roster, list(slots), where, points) if pid is not None),
               Decimal(0))


def lineup_choices(
    history: History, through: int, names: Mapping[int, str], slots: Sequence[str], positions: Mapping[str, str],
) -> LineupChoices:
    """The lineup choices of weeks 1 to `through`.

    `slots` are the starter slots of the league, with no bench slot. `positions` maps each player to his position
    from the players file. The history's own position of a player comes first. The real score of a week is the team
    score, so the Bench points of a week are never below 0.
    """
    bench: dict[int, Decimal] = {rid: Decimal(0) for rid in names}
    lost: dict[int, list[LostWeek]] = {rid: [] for rid in names}
    for number in range(1, through + 1):
        past = history.weeks[number]
        for a, b in past.pairs:
            for mine, theirs in ((a, b), (b, a)):
                score, other = Decimal(str(past.scores[mine])), Decimal(str(past.scores[theirs]))
                best = max(best_score(past, mine, slots, positions), score)
                bench[mine] += best - score
                if score < other < best:
                    lost[mine].append(LostWeek(
                        week=number, opponent_roster_id=theirs, opponent=names[theirs], score=float(score),
                        best=float(best), bench_points=r2(float(best - score)), margin=r2(float(other - score))))
    order = sorted(names, key=lambda rid: (-bench[rid], names[rid]))
    return LineupChoices(teams=[
        TeamLineup(roster_id=rid, name=names[rid], rank=place, bench_points=r2(float(bench[rid])),
                   lost_with_better=lost[rid])
        for place, rid in enumerate(order, start=1)
    ])


def lineup_facts(choices: LineupChoices) -> list[Fact]:
    """The facts of the lineup choices: the Bench points of each team, and each loss its best lineup would have won."""
    facts = []
    for team in choices.teams:
        n = Nums()
        facts.append(fact(f"LC.{team.roster_id}", f"{team.name} left {n(team.bench_points)} points on the bench, "
                          f"{n.ord(team.rank)} most in the league.", n, [team.name], []))
        for week in team.lost_with_better:
            n = Nums()
            facts.append(fact(f"LC.{team.roster_id}.{week.week}",
                              f"{team.name} lost to {week.opponent} by {n(week.margin)} in week {n(week.week)} with "
                              f"{n(week.bench_points)} points on the bench, so its best lineup would have won.",
                              n, [team.name, week.opponent], []))
    return facts
