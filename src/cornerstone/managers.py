"""
The managers file entries: one entry per roster with the team and the record of the season to date.
Pure code over the saved history. The render module writes the entries as managers.json.
"""
from pydantic import BaseModel

from cornerstone.facts_league import season_records
from cornerstone.manager_grade import ManagerGrade, roster_grades
from cornerstone.manager_moves import Moves, roster_moves
from cornerstone.manager_players import BestAdd, TopPerformer, best_adds, top_performers
from cornerstone.manager_season import AwardCounts, Bench, SeasonWeek, award_counts, bench_points, season_weeks
from cornerstone.models import ChartValues, History, Team
from cornerstone.parse import player_name
from cornerstone.snapshot import Snapshot

# Under two saved weeks a manager page has too little to show, so the file waits for the second week.
MIN_WEEKS = 2


class ManagerTeam(BaseModel):
    """The team of an entry: the name, the owner, and the avatar URL, as the page teams carry them."""
    name: str
    owner: str
    avatar_url: str | None


class ManagerEntry(BaseModel):
    """One roster in the managers file. A later field goes at the end, so the keys that exist keep their meaning."""
    roster_id: int
    team: ManagerTeam
    # The record counts the head-to-head game and the median game of each week, as the rankings rows do.
    wins: int
    losses: int
    points_for: float
    moves: Moves
    best_adds: list[BestAdd]
    top_performers: list[TopPerformer]
    # The season so far: the points per saved week, the bench points, and the awards shelf.
    # The bench is None when the caller gives no roster slots.
    weeks: list[SeasonWeek]
    bench: Bench | None
    awards: AwardCounts
    # The roster grade from the current rosters, the projections ahead, the season points, and the chart. None when
    # the build has no snapshot or no projections ahead.
    grade: ManagerGrade | None = None


def managers(
    history: History, teams: dict[int, Team], players: dict[str, dict] | None = None, *,
    roster_slots: list[str] | None = None, week_awards: dict[int, list[tuple[str, int]]] | None = None,
    snapshot: Snapshot | None = None, projections_ahead: dict[int, dict[str, float]] | None = None,
    chart: ChartValues | None = None,
) -> list[ManagerEntry]:
    """One entry per roster through the history week, in roster id order."""
    records = season_records(history, history.week)
    # The raw players file of the current week names the players. Without it, a player reads as his id.
    players = players or {}
    names = {pid: player_name(pid, entry) for pid, entry in players.items()}
    grades = (roster_grades(snapshot, projections_ahead, history, chart)
              if snapshot is not None and projections_ahead else {})
    # The site joins the entry to the rankings row on the roster id, so a stable order helps a reader of the file only.
    return [
        ManagerEntry(
            roster_id=rid,
            team=ManagerTeam(name=teams[rid].name, owner=teams[rid].owner, avatar_url=teams[rid].avatar_url),
            wins=records[rid][0],
            losses=records[rid][1],
            points_for=records[rid][2],
            moves=roster_moves(history, rid, players),
            best_adds=best_adds(history, rid, players),
            top_performers=top_performers(history, rid, players),
            weeks=season_weeks(history, rid),
            bench=bench_points(history, rid, roster_slots, names) if roster_slots else None,
            awards=award_counts(week_awards or {}, rid, history.week),
            grade=grades.get(rid),
        )
        for rid in sorted(records)
    ]
