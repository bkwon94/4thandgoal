"""
The data snapshot the trade analyzer grades a proposed trade from, and the builder that loads it.
The builder reads saved raw Sleeper data, the saved history, and trade values, with no network.
"""
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from cornerstone.facts_league import standings
from cornerstone.history import load_history
from cornerstone.models import ChartValues, History, Standing, Team
from cornerstone.parse import player_name, parse_week
from cornerstone.sleeper import load_raw, read_fetch_time

logger = logging.getLogger(__name__)

# The sources the snapshot does not load. Each one is None and its name is in Snapshot.missing.
SLOW_SOURCES = ("usage", "injuries", "schedules", "depth_charts", "points_allowed")


class SnapshotPlayer(BaseModel):
    """What the analyzer shows of a rostered player: the name, the position, and the NFL team."""

    player_id: str
    name: str
    position: str
    nfl_team: str | None


class AsOf(BaseModel):
    """The stamps that say how fresh the snapshot is. The result shows them to the manager."""

    # None when the week has no chart values.
    chart_week: int | None
    stats_through: int
    # None when the saved raw data has no fetch time.
    rosters_fetched: datetime | None


class Snapshot(BaseModel):
    """Everything the grade reads. A slow source that is not loaded is None and is named in missing."""

    season: int
    week: int
    # The players on each roster now, by roster id.
    rosters: dict[int, list[str]]
    # Each roster with its manager's user name and team name, by roster id.
    teams: dict[int, Team]
    standings: list[Standing]
    # The league's lineup slots, in Sleeper's order, such as QB, RB, RB, WR, and BN.
    roster_positions: list[str]
    players: dict[str, SnapshotPlayer]
    chart: ChartValues | None
    # Season stats from week 1 through the last completed week.
    stats: History
    as_of: AsOf
    # Snap, target, and red-zone use, by player id.
    usage: dict[str, dict[str, float]] | None = None
    # The injury report status, by player id and week.
    injuries: dict[str, dict[int, str]] | None = None
    # The opponent of each NFL team, by team and week. A bye week has no entry.
    schedules: dict[str, dict[int, str]] | None = None
    # The player ids in depth order, by NFL team and position.
    depth_charts: dict[str, dict[str, list[str]]] | None = None
    # The points each defense allows to a position, by NFL team and position.
    points_allowed: dict[str, dict[str, float]] | None = None
    # The names of the sources the snapshot lacks, so the breakdown can say what it could not use.
    missing: list[str] = []


def load_snapshot(raw_dir: Path, history_root: Path, chart: ChartValues | None) -> Snapshot:
    """The snapshot of the saved week in raw_dir. It reads only files, so it never calls the network."""
    raw = load_raw(raw_dir)
    week = parse_week(raw)
    history = load_history(history_root, raw, week.week)
    rosters = {r["roster_id"]: list(r["players"] or []) for r in raw["rosters"]}
    entries = raw["players"]
    players = {
        pid: SnapshotPlayer(
            player_id=pid,
            name=player_name(pid, entry),
            position=entry.get("position") or "?",
            nfl_team=entry.get("team"),
        )
        for pids in rosters.values() for pid in pids
        for entry in [entries.get(pid) or {}]
    }
    missing = ([] if chart is not None else ["chart"]) + list(SLOW_SOURCES)
    return Snapshot(
        season=week.season,
        week=week.week,
        rosters=rosters,
        teams=week.teams,
        standings=standings(week, history),
        roster_positions=raw["league"]["roster_positions"],
        players=players,
        chart=chart,
        stats=history,
        as_of=AsOf(
            chart_week=chart.week if chart is not None else None,
            stats_through=week.last_scored_week,
            rosters_fetched=read_fetch_time(raw_dir),
        ),
        missing=missing,
    )
