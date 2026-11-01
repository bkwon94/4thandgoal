"""
The data snapshot the trade analyzer grades a proposed trade from, and the builder that loads it.
The builder reads saved raw Sleeper data, the saved history, trade values, and the returns file, with no network.
"""
import json
import logging
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, PrivateAttr

from cornerstone.config import LeagueConfig
from cornerstone.facts_league import standings
from cornerstone.history import load_saved_weeks, snap_share, target_share
from cornerstone.models import ChartValues, ExpectedPoints, History, Standing, Team, UsageShare
from cornerstone.nflverse import TeamSchedule
from cornerstone.points_allowed import PositionAllowed
from cornerstone.parse import parse_past_week, player_name, parse_week
from cornerstone.ranks import RANKED_POSITIONS, in_pool, lineup_value, rank_table
from cornerstone.slow_sources import SlowSources
from cornerstone.provider.raw import RawStatLine, RawWeek
from cornerstone.provider.sleeper import load_raw, read_fetch_time
from cornerstone.tunables import IN_PROGRESS_MINUTES

logger = logging.getLogger(__name__)

# The sources the snapshot lacks without a SlowSources, in the names of load_slow_sources.
# Each one is None and its name is in Snapshot.missing.
# Snap, target, and red-zone use need no source of their own: the history helpers read them from the stats.
SLOW_SOURCES = ("schedules", "depth_charts", "id_map", "points_allowed", "injuries", "expected_points", "player_weeks")


class SnapshotPlayer(BaseModel):
    """What the analyzer shows of a rostered player or a free agent: the name, the position, and the NFL team."""

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
    # The game count of each count that its source has not posted yet, by the name of the count.
    # "snaps" is the Sleeper snap count. "usage" is the WOPR of the nflverse player file, a word the page can show.
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

    # The league the snapshot belongs to. Its sizes, such as the line and the return-by week, go with the data,
    # so every reader of the snapshot reads the numbers of the same league.
    config: LeagueConfig
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
    # The players the returns file marks with `season` in place of a week. GLOSSARY.md, "Out for the season".
    # Sleeper's IR status does not mean out for the season, so this mark is the only sign of one. ADR 0005.
    out_for_season: set[str] = set()
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
    # The Sleeper codes of the NFL teams whose known game of week N is in progress. A reason that quotes a week N
    # number of one of their players says "game in progress". Empty for a saved week.
    in_progress_teams: set[str] = set()
    # The free agents at each of QB, RB, WR, and TE in player id order: the players on no roster that the waiver
    # pool reads. The hole fact names the best of them, and `players` holds rostered players only, so each one
    # carries his name here. Empty when the raw data has no free agent.
    free_agents: dict[str, list[SnapshotPlayer]] = {}
    # The player ids per position in position rank order, and the rank of each player, built on the first read.
    # GLOSSARY.md, "Position rank".
    _rank_table: dict[str, list[str]] | None = PrivateAttr(default=None)
    _position_ranks: dict[str, int] | None = PrivateAttr(default=None)
    # The lineup value of each player, the snap and target shares of each player, and the read of each roster as it
    # is now, by roster id, each built on the first read. The finder grades about a thousand trades per call, and
    # these reads depend on the snapshot only, so they must not run again per trade.
    _lineup_values: dict[str, Decimal] = PrivateAttr(default_factory=dict)
    _usage_shares: dict[str, tuple[UsageShare | None, UsageShare | None]] = PrivateAttr(default_factory=dict)
    _roster_reads: dict[int, object] = PrivateAttr(default_factory=dict)

    def rank_table(self) -> dict[str, list[str]]:
        """The player ids at each of QB, RB, WR, and TE in position rank order, first to last.

        The table builds once per snapshot, so the finder's thousand trades and every reader share one ranking.
        """
        if self._rank_table is None:
            self._rank_table = rank_table(self)
            self._position_ranks = {pid: rank for players in self._rank_table.values()
                                    for rank, pid in enumerate(players, start=1)}
        return self._rank_table

    def position_rank(self, player_id: str) -> int | None:
        """The player's position rank, or None for a K, a DEF, or a player outside the rank pool."""
        self.rank_table()
        return self._position_ranks.get(player_id)

    def lineup_value(self, player_id: str) -> Decimal:
        """The points per game the player counts for in a best lineup, built once per player per snapshot."""
        if player_id not in self._lineup_values:
            self._lineup_values[player_id] = lineup_value(self, player_id)
        return self._lineup_values[player_id]

    def usage_shares(self, player_id: str) -> tuple[UsageShare | None, UsageShare | None]:
        """The snap share and the target share of the player through the player stat bound, built once per player."""
        if player_id not in self._usage_shares:
            through = self.as_of.stats_through
            self._usage_shares[player_id] = (snap_share(self.stats, player_id, through),
                                             target_share(self.stats, player_id, through))
        return self._usage_shares[player_id]

    def roster_read(self, roster_id: int, build: Callable[["Snapshot", list[str]], object]) -> object:
        """The read of the roster as it is now, built once per roster by `build`.

        The adjusters own the read, and the adjusters import this module, so the caller passes the build.
        """
        if roster_id not in self._roster_reads:
            self._roster_reads[roster_id] = build(self, self.rosters[roster_id])
        return self._roster_reads[roster_id]

    def best_free_agent(self, positions: Iterable[str]) -> tuple[SnapshotPlayer, int] | None:
        """The free agent at any of `positions` with the most lineup value, and his rank at his own position.

        A free agent with no stat line has no rank, so he is never the best. At one position, the most lineup value is
        the best position rank. The rank, then the player id, breaks a tie of lineup values.
        None when no free agent at the positions has a rank.
        """
        ranked = [(player, rank) for position in positions for player in self.free_agents.get(position, [])
                  if (rank := self.position_rank(player.player_id)) is not None]
        if not ranked:
            return None
        # Each position ranks its own pool, so RB51 and TE9 do not compare. The lineup value compares across positions.
        return min(ranked, key=lambda each: (-lineup_value(self, each[0].player_id), each[1], each[0].player_id))

    def model_copy(self, *, update: dict | None = None, deep: bool = False) -> "Snapshot":
        """A copy with no rank table and no cached reads, so a copy with new rosters, returns, or stats reads its own
        data."""
        copy = super().model_copy(update=update, deep=deep)
        copy._rank_table = None
        copy._position_ranks = None
        copy._lineup_values = {}
        copy._usage_shares = {}
        copy._roster_reads = {}
        return copy


def _games_with_a_stat_line(stats: list[RawStatLine]) -> int:
    """The count of distinct games with a stat line of a player who played. A line of an inactive player has no gp."""
    return len({row.game_id for row in stats if row.game_id and row.stats.get("gp", 0) > 0})


def _teams_in_progress(stats: list[RawStatLine], kickoffs: dict[str, datetime], now: datetime) -> dict[str, str]:
    """The game id of each NFL team with a played line whose game is in progress at `now`. GLOSSARY.md, "In progress".

    A game is in progress when `now` is past its kickoff by less than IN_PROGRESS_MINUTES.
    A team with no kickoff has a game that counts as final.
    `now` must be an aware datetime, because the kickoffs carry the Eastern time zone.
    """
    length = timedelta(minutes=IN_PROGRESS_MINUTES)
    teams = {}
    for row in stats:
        team, kickoff = row.team, kickoffs.get(row.team or "")
        if (row.game_id and row.stats.get("gp", 0) > 0 and kickoff is not None
                and kickoff <= now < kickoff + length):
            teams[team] = row.game_id
    return teams


def _pending(stats: list[RawStatLine], week: int, wopr: dict[str, dict[int, int]] | None) -> dict[str, int]:
    """The game count of each pending count of the known games, GLOSSARY.md "Pending". A count of 0 is left out.

    A game is pending for snaps when no line of a player who played has the team snap count. Sleeper posts the
    snaps of a game together, and a final line can lack the player's own snaps because Sleeper leaves out a 0.
    A game is pending for usage when no player who played in it has a WOPR row for the week. A missing file is a
    missing source, not a pending count.
    The usage count is per game, but the WOPR window is per player. A WR who played with no row keeps a window
    that ends at N-1, even when a teammate's row keeps his game out of the count.
    """
    played = [row for row in stats if row.game_id and row.stats.get("gp", 0) > 0]
    games = {row.game_id for row in played}
    with_snaps = {row.game_id for row in played if "tm_off_snp" in row.stats}
    counts = {"snaps": len(games - with_snaps)}
    if wopr is not None:
        with_usage = {row.game_id for row in played if week in wopr.get(row.player_id, {})}
        counts["usage"] = len(games - with_usage)
    return {name: count for name, count in counts.items() if count > 0}


def _snapshot_player(pid: str, entry: dict) -> SnapshotPlayer:
    return SnapshotPlayer(
        player_id=pid,
        name=player_name(pid, entry),
        position=entry.get("position") or "?",
        nfl_team=entry.get("team"),
        injury_status=entry.get("injury_status"),
    )


def _free_agents(entries: dict[str, dict], rosters: dict[int, list[str]]) -> dict[str, list[SnapshotPlayer]]:
    """The free agents at each of QB, RB, WR, and TE in player id order, by the waiver pool's rule.

    The saved path and the live path both build here from the raw players file, so a Saturday grade and the Tuesday
    build read the same free agents.
    """
    rostered = {pid for pids in rosters.values() for pid in pids}
    free_agents: dict[str, list[SnapshotPlayer]] = {position: [] for position in RANKED_POSITIONS}
    for pid, entry in sorted(entries.items()):
        if entry.get("position") in free_agents and in_pool(entry, rostered, pid):
            free_agents[entry["position"]].append(_snapshot_player(pid, entry))
    return free_agents


# The word the commissioner writes in the returns file in place of a week for a player out for the season.
SEASON_MARK = "season"


def load_returns(path: Path) -> dict[str, int] | None:
    """The return week by player id, or None when the season has no returns file.

    A player marked `season` has no return week, so he is not here. load_out_for_season reads him.
    """
    if not path.exists():
        return None
    return {pid: int(week) for pid, week in json.loads(path.read_text(encoding="utf-8")).items()
            if week != SEASON_MARK}


def load_out_for_season(path: Path) -> set[str]:
    """The player ids the returns file marks `season`, or none when the season has no returns file."""
    if not path.exists():
        return set()
    return {pid for pid, week in json.loads(path.read_text(encoding="utf-8")).items() if week == SEASON_MARK}


def _projections_by_player(raw: RawWeek, week: int) -> dict[str, dict[int, float]] | None:
    """The half-PPR projections of the raw week and the weeks ahead by player id and week.

    It is None when the raw data has no projections ahead.
    """
    if raw.projections_ahead is None:
        return None
    by_player: dict[str, dict[int, float]] = {}
    for item in raw.projections:
        points = item.stats.get("pts_half_ppr")
        if points is not None:
            by_player.setdefault(item.player_id, {})[week] = float(points)
    for entry in raw.projections_ahead:
        for pid, points in entry.projections.items():
            by_player.setdefault(pid, {})[entry.week] = float(points)
    return by_player


def load_snapshot(
        raw_dir: Path, history_root: Path, chart: ChartValues | None, slow: SlowSources | None = None, *,
        config: LeagueConfig) -> Snapshot:
    """The snapshot of the saved week in raw_dir. It reads only files, so it never calls the network.

    Without `slow`, the slow sources stay None and all of them are named as missing.
    """
    # The returns file sits beside the history, so the history root locates it.
    returns_file = history_root.parent / "returns.json"
    return build_snapshot(load_raw(raw_dir), history_root, chart, slow, read_fetch_time(raw_dir),
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          config=config)


def week_snapshot(raw: RawWeek, history_root: Path, week: int, *, config: LeagueConfig) -> Snapshot:
    """The snapshot the weekly build of week N reads: the league after week N, as the analyzer sees it in week N + 1.

    The bye facts read the position rank and the lineup value, and neither needs a chart or a slow source.
    """
    # The returns file sits beside the history, so the history root locates it.
    returns_file = history_root.parent / "returns.json"
    return build_snapshot(raw, history_root, None, trade_week=week + 1, returns=load_returns(returns_file),
                          out_for_season=load_out_for_season(returns_file), config=config)


def build_snapshot(
        raw: RawWeek, history_root: Path, chart: ChartValues | None, slow: SlowSources | None = None,
        rosters_fetched: datetime | None = None, stale: list[str] | None = None,
        trade_week: int | None = None, returns: dict[str, int] | None = None,
        now: datetime | None = None, out_for_season: set[str] | None = None, *, config: LeagueConfig) -> Snapshot:
    """The snapshot of parsed raw data. A saved week and a live fetch both build it here, so they grade the same.

    `trade_week` is the week N of the proposed trade. Without it, N is the raw week, as for a saved week.
    A saved week passes no trade week and never counts its own games. Only the live path passes one, so only a
    fetch on a game day reads the known games of week N.
    `returns` is the hand-kept return week by player id. None means the season has no returns file.
    `out_for_season` is the set of players the same file marks `season`.
    `now` is the clock of the request. With the kickoffs of the slow sources, it tells the known games in progress.
    `config` is the league of the raw data. The snapshot carries it, so its readers take the league sizes from it.
    """
    # A failed live stats fetch gives None. The parses then read no lines.
    stats_lines = raw.stats
    raw = raw.model_copy(update={"stats": stats_lines or []})
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
    in_progress: dict[str, str] = {}
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
            # The label changes no number, so a game in progress counts as a known game the same as a final one.
            if now is not None and slow is not None and slow.kickoffs:
                in_progress = _teams_in_progress(stats_lines, slow.kickoffs, now)
            known_games = KnownGames(week=trade_week, games=games, in_progress=len(set(in_progress.values())),
                                     pending=_pending(stats_lines, trade_week, slow.wopr if slow else None))
            if games > 0:
                weeks[trade_week] = parse_past_week(raw, trade_week)
                stats_through = trade_week
    history = History(week=stats_through, weeks=weeks)
    rosters = {r.roster_id: list(r.players or []) for r in raw.rosters}
    entries = raw.players
    players = {pid: _snapshot_player(pid, entries.get(pid) or {}) for pids in rosters.values() for pid in pids}
    # Without a loader result, every slow source is missing. With one, the loader names what it lacks.
    slow_missing = list(SLOW_SOURCES) if slow is None else list(slow.missing)
    missing = ([] if chart is not None else ["chart"]) + slow_missing + ([] if returns is not None else ["returns"])
    return Snapshot(
        config=config,
        season=week.season,
        week=trade_week,
        rosters=rosters,
        teams=week.teams,
        # The standings run through the last completed week, so the scores of the known games never count.
        # The history passes with that bound too, so its check for a full season stops there.
        # Before week 1 the rosters give the records.
        standings=standings(week.model_copy(update={"week": completed_through}),
                            history.model_copy(update={"week": completed_through}) if completed_through else None,
                            config=config),
        roster_positions=raw.league.roster_positions,
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
        out_for_season=out_for_season or set(),
        projections_ahead=_projections_by_player(raw, week.week),
        missing=missing,
        stale=stale,
        in_progress_teams=set(in_progress),
        free_agents=_free_agents(entries, rosters),
    )
