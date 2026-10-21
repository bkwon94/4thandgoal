"""
The data snapshot the trade analyzer grades a proposed trade from, and the builder that loads it.
The builder reads saved raw Sleeper data, the saved history, and trade values, with no network.
"""
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from cornerstone.facts_league import standings
from cornerstone.history import load_saved_weeks
from cornerstone.models import ChartValues, History, Standing, Team
from cornerstone.nflverse import TeamSchedule
from cornerstone.points_allowed import PositionAllowed
from cornerstone.parse import parse_past_week, player_name, parse_week
from cornerstone.slow_sources import SlowSources
from cornerstone.sleeper import load_raw, read_fetch_time

logger = logging.getLogger(__name__)

# The sources the snapshot lacks without a SlowSources. The first four use the names of load_slow_sources.
# Each one is None and its name is in Snapshot.missing. Usage and injuries have no loader yet.
SLOW_SOURCES = ("schedules", "depth_charts", "id_map", "points_allowed", "usage", "injuries")
# The sources that no SlowSources fills, so they stay missing in every case.
UNLOADED_SOURCES = ("usage", "injuries")


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
    # The trade week N. Every stat input ends at week N-1.
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
    # Season stats from week 1 through as_of.stats_through, which is week N-1 when the history holds it.
    stats: History
    as_of: AsOf
    # Snap, target, and red-zone use, by player id.
    usage: dict[str, dict[str, float]] | None = None
    # The injury report status, by player id and week.
    injuries: dict[str, dict[int, str]] | None = None
    # The opponent of each NFL team, by team and week. A bye week has no entry.
    schedules: dict[str, TeamSchedule] | None = None
    # The gsis_ids in depth order, by NFL team and position. The id map joins them to Sleeper ids.
    depth_charts: dict[str, dict[str, list[str]]] | None = None
    # Sleeper id to gsis_id.
    id_map: dict[str, str] | None = None
    # The points each defense allows to a position, by NFL team and position.
    points_allowed: dict[str, dict[str, PositionAllowed]] | None = None
    # The names of the sources the snapshot lacks, so the breakdown can say what it could not use.
    missing: list[str] = []
    # The sources whose refresh failed, so the cache is older than a day or absent.
    # "history" is here when the history lacks week N-1, on a live or a saved build.
    stale: list[str] = []


def load_snapshot(
        raw_dir: Path, history_root: Path, chart: ChartValues | None, slow: SlowSources | None = None) -> Snapshot:
    """The snapshot of the saved week in raw_dir. It reads only files, so it never calls the network.

    Without `slow`, the slow sources stay None and all of them are named as missing.
    """
    return build_snapshot(load_raw(raw_dir), history_root, chart, slow, read_fetch_time(raw_dir))


def build_snapshot(
        raw: dict[str, object], history_root: Path, chart: ChartValues | None, slow: SlowSources | None = None,
        rosters_fetched: datetime | None = None, stale: list[str] | None = None,
        trade_week: int | None = None) -> Snapshot:
    """The snapshot of parsed raw data. A saved week and a live fetch both build it here, so they grade the same.

    `trade_week` is the week N of the proposed trade. Without it, N is the raw week, as for a saved week.
    """
    week = parse_week(raw)
    stale = list(stale or [])
    # GLOSSARY.md, "Before the trade": weeks 1 to N-1, for a proposed trade in week N. Every grade input ends there.
    # So the history and the standings stop at N-1, and the games of week N never count, even when they are final.
    trade_week = week.week if trade_week is None else trade_week
    through = trade_week - 1
    weeks = load_saved_weeks(history_root, through)
    # On the Tuesday after the cutoff, Sleeper still shows week N-1 and its games are final.
    # The raw data of this run is then the freshest copy of week N-1.
    if week.week == through:
        weeks[through] = parse_past_week(raw, through)
    # Sleeper may not have scored week N-1 yet, or its fetch failed. The stamp then shows the last week held.
    stats_through = through if through in weeks else max(weeks, default=0)
    if stats_through < through and "history" not in stale:
        stale.append("history")
    history = History(week=stats_through, weeks=weeks)
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
    # Without a loader result, every slow source is missing. With one, the loader names what it lacks.
    slow_missing = list(SLOW_SOURCES) if slow is None else [*slow.missing, *UNLOADED_SOURCES]
    missing = ([] if chart is not None else ["chart"]) + slow_missing
    return Snapshot(
        season=week.season,
        week=trade_week,
        rosters=rosters,
        teams=week.teams,
        # The standings run through the same week as the stats. Before week 1 the rosters give the records.
        standings=standings(week.model_copy(update={"week": stats_through}), history if stats_through else None),
        roster_positions=raw["league"]["roster_positions"],
        players=players,
        chart=chart,
        stats=history,
        as_of=AsOf(
            chart_week=chart.week if chart is not None else None,
            stats_through=stats_through,
            rosters_fetched=rosters_fetched,
        ),
        schedules=slow.schedules if slow else None,
        depth_charts=slow.depth_charts if slow else None,
        id_map=slow.id_map if slow else None,
        points_allowed=slow.points_allowed if slow else None,
        missing=missing,
        stale=stale,
    )
