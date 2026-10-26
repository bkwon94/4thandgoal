"""
The data snapshot the trade analyzer grades a proposed trade from, and the builder that loads it.
The builder reads saved raw Sleeper data, the saved history, trade values, and the returns file, with no network.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from cornerstone.facts_league import standings
from cornerstone.history import load_saved_weeks
from cornerstone.models import ChartValues, ExpectedPoints, History, Standing, Team
from cornerstone.nflverse import TeamSchedule
from cornerstone.points_allowed import PositionAllowed
from cornerstone.parse import parse_past_week, player_name, parse_week
from cornerstone.slow_sources import SlowSources
from cornerstone.sleeper import load_raw, read_fetch_time

logger = logging.getLogger(__name__)

# The sources the snapshot lacks without a SlowSources, in the names of load_slow_sources.
# Each one is None and its name is in Snapshot.missing.
# Snap, target, and red-zone use need no source of their own: the history helpers read them from the stats.
SLOW_SOURCES = ("schedules", "depth_charts", "id_map", "points_allowed", "injuries", "expected_points", "player_weeks")


class SnapshotPlayer(BaseModel):
    """What the analyzer shows of a rostered player: the name, the position, and the NFL team."""

    player_id: str
    name: str
    position: str
    nfl_team: str | None
    # The injury report status from Sleeper, such as Out, IR, or NA. None when the player is healthy.
    injury_status: str | None = None


class KnownGames(BaseModel):
    """The week N games that the player stats read, as the as-of stamp counts them. GLOSSARY.md, "Known games"."""

    # The trade week N.
    week: int
    # The count of distinct week N games with a stat line of a player who played.
    games: int
    # The count of those games in progress.
    in_progress: int = 0
    # The game count of each count that Sleeper has not posted yet, by the name of the count.
    pending: dict[str, int] = {}


class AsOf(BaseModel):
    """The stamps that say how fresh the snapshot is. The result shows them to the manager."""

    # None when the week has no chart values.
    chart_week: int | None
    # The player stat bound: the `through` week that every player stat reader takes.
    stats_through: int
    # The last completed week before the trade week. The standings, the due-back rule, and the injury report end here.
    completed_through: int
    # None when the saved raw data has no fetch time.
    rosters_fetched: datetime | None
    # None for a saved week, a failed week N fetch, or a raw week that is not the trade week.
    known_games: KnownGames | None = None


class Snapshot(BaseModel):
    """Everything the grade reads. A slow source that is not loaded is None and is named in missing."""

    season: int
    # The trade week N. Every player stat ends at the known games, and the standings end at week N-1.
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
    # Season stats from week 1 through as_of.stats_through, the player stat bound.
    # That is week N when the raw data holds week N stat lines, and week N-1 when only the history holds it.
    stats: History
    as_of: AsOf
    # The injury report status, by gsis_id and week. The id map joins it to Sleeper ids.
    injuries: dict[str, dict[int, str]] | None = None
    # The opponent of each NFL team, by team and week. A bye week has no entry.
    schedules: dict[str, TeamSchedule] | None = None
    # The gsis_ids in depth order, by NFL team and position. The id map joins them to Sleeper ids.
    depth_charts: dict[str, dict[str, list[str]]] | None = None
    # Sleeper id to gsis_id.
    id_map: dict[str, str] | None = None
    # The points each defense allows to a position, by NFL team and position.
    points_allowed: dict[str, dict[str, PositionAllowed]] | None = None
    # The expected window of each player by Sleeper id, from ffopportunity. None when the slow sources cannot read it.
    expected: ExpectedPoints | None = None
    # The WOPR by Sleeper id and week, from the nflverse weekly player file in the cache. None when the file or
    # the id map is missing, or the file has no row for the week before the trade week.
    # A whole number is fine: the rounding moves a week by half a point at most, far under WOPR_SWING.
    wopr: dict[str, dict[int, int]] | None = None
    # The week each player returns, by player id, from the returns file the commissioner keeps.
    # No data source holds a return week, so a suspended or injured player's week comes from that file.
    returns: dict[str, int] = {}
    # The Sleeper projection of each player by Sleeper id and week, from the week after the raw week on.
    # The raw week's own projection is here too, so a player due back in that week counts for it.
    # A week with no row is a bye or no game. It is None when the raw data has no projections ahead file.
    projections_ahead: dict[str, dict[int, float]] | None = None
    # The names of the sources the snapshot lacks, so the breakdown can say what it could not use.
    missing: list[str] = []
    # The sources whose refresh failed, so the cache is older than a day or absent.
    # "history" is here when the history lacks week N-1, on a live or a saved build.
    # "stats" is here when the stats fetch of the trade week failed, so the known games are unknown.
    stale: list[str] = []


def _games_with_a_stat_line(stats: list[dict]) -> int:
    """The count of distinct games with a stat line of a player who played. A line of an inactive player has no gp."""
    return len({row["game_id"] for row in stats if row.get("game_id") and (row.get("stats") or {}).get("gp", 0) > 0})


def load_returns(path: Path) -> dict[str, int] | None:
    """The return week by player id, or None when the season has no returns file."""
    if not path.exists():
        return None
    return {pid: int(week) for pid, week in json.loads(path.read_text(encoding="utf-8")).items()}


def _projections_by_player(raw: dict[str, object], week: int) -> dict[str, dict[int, float]] | None:
    """The half-PPR projections of the raw week and the weeks ahead by player id and week.

    It is None when the raw data has no projections ahead.
    """
    if "projections_ahead" not in raw:
        return None
    by_player: dict[str, dict[int, float]] = {}
    for item in raw["projections"]:
        points = (item.get("stats") or {}).get("pts_half_ppr")
        if points is not None:
            by_player.setdefault(item["player_id"], {})[week] = float(points)
    for entry in raw["projections_ahead"]:
        for pid, points in entry["projections"].items():
            by_player.setdefault(pid, {})[int(entry["week"])] = float(points)
    return by_player


def load_snapshot(
        raw_dir: Path, history_root: Path, chart: ChartValues | None, slow: SlowSources | None = None) -> Snapshot:
    """The snapshot of the saved week in raw_dir. It reads only files, so it never calls the network.

    Without `slow`, the slow sources stay None and all of them are named as missing.
    """
    # The returns file sits beside the history, so the history root locates it.
    returns = load_returns(history_root.parent / "returns.json")
    return build_snapshot(load_raw(raw_dir), history_root, chart, slow, read_fetch_time(raw_dir), returns=returns)


def build_snapshot(
        raw: dict[str, object], history_root: Path, chart: ChartValues | None, slow: SlowSources | None = None,
        rosters_fetched: datetime | None = None, stale: list[str] | None = None,
        trade_week: int | None = None, returns: dict[str, int] | None = None) -> Snapshot:
    """The snapshot of parsed raw data. A saved week and a live fetch both build it here, so they grade the same.

    `trade_week` is the week N of the proposed trade. Without it, N is the raw week, as for a saved week.
    A saved week passes no trade week and never counts its own games. Only the live path passes one, so only a
    fetch on a game day reads the known games of week N.
    `returns` is the hand-kept return week by player id. None means the season has no returns file.
    """
    # A failed live stats fetch gives None, and a raw can lack the key. The parses then read no lines.
    stats_lines = raw.get("stats")
    raw = {**raw, "stats": stats_lines or []}
    week = parse_week(raw)
    stale = list(stale or [])
    # GLOSSARY.md, "Before the trade": weeks 1 to N-1, for a proposed trade in week N. The standings end there.
    # Player stats end at the known games: weeks 1 to N-1, plus the week N games with a stat line.
    # A saved week passes no trade week, so it grades from the saved history only, as the weekly build does.
    graded_now = trade_week is not None
    trade_week = week.week if trade_week is None else trade_week
    through = trade_week - 1
    weeks = load_saved_weeks(history_root, through)
    # On the Tuesday after the cutoff, Sleeper still shows week N-1 and its games are final.
    # The raw data of this run is then the freshest copy of week N-1.
    if week.week == through:
        weeks[through] = parse_past_week(raw, through)
    # Sleeper may not have scored week N-1 yet, or its fetch failed. The stamp then shows the last week held.
    completed_through = through if through in weeks else max(weeks, default=0)
    if completed_through < through and "history" not in stale:
        stale.append("history")
    stats_through = completed_through
    known_games = None
    # A fetch on a game day of week N holds the week N stat lines, so those games join the player stats.
    # A week with no played line yet has zero known games, and the grade reads the week before.
    # A failed fetch has no stats, so the stamp names them stale.
    # A gap in the history keeps week N out too, so the player stats never skip a week.
    if graded_now and week.week == trade_week and completed_through == through:
        if stats_lines is None:
            if "stats" not in stale:
                stale.append("stats")
        else:
            games = _games_with_a_stat_line(stats_lines)
            known_games = KnownGames(week=trade_week, games=games)
            if games > 0:
                weeks[trade_week] = parse_past_week(raw, trade_week)
                stats_through = trade_week
    history = History(week=stats_through, weeks=weeks)
    rosters = {r["roster_id"]: list(r["players"] or []) for r in raw["rosters"]}
    entries = raw["players"]
    players = {
        pid: SnapshotPlayer(
            player_id=pid,
            name=player_name(pid, entry),
            position=entry.get("position") or "?",
            nfl_team=entry.get("team"),
            injury_status=entry.get("injury_status"),
        )
        for pids in rosters.values() for pid in pids
        for entry in [entries.get(pid) or {}]
    }
    # Without a loader result, every slow source is missing. With one, the loader names what it lacks.
    slow_missing = list(SLOW_SOURCES) if slow is None else list(slow.missing)
    missing = ([] if chart is not None else ["chart"]) + slow_missing + ([] if returns is not None else ["returns"])
    return Snapshot(
        season=week.season,
        week=trade_week,
        rosters=rosters,
        teams=week.teams,
        # The standings run through the last completed week, so the scores of the known games never count.
        # The history passes with that bound too, so its check for a full season stops there.
        # Before week 1 the rosters give the records.
        standings=standings(week.model_copy(update={"week": completed_through}),
                            history.model_copy(update={"week": completed_through}) if completed_through else None),
        roster_positions=raw["league"]["roster_positions"],
        players=players,
        chart=chart,
        stats=history,
        as_of=AsOf(
            chart_week=chart.week if chart is not None else None,
            stats_through=stats_through,
            completed_through=completed_through,
            rosters_fetched=rosters_fetched,
            known_games=known_games,
        ),
        schedules=slow.schedules if slow else None,
        depth_charts=slow.depth_charts if slow else None,
        id_map=slow.id_map if slow else None,
        points_allowed=slow.points_allowed if slow else None,
        injuries=slow.injuries if slow else None,
        expected=slow.expected if slow else None,
        wopr=slow.wopr if slow else None,
        returns=returns or {},
        projections_ahead=_projections_by_player(raw, week.week),
        missing=missing,
        stale=stale,
    )
