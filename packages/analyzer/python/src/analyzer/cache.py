"""
The two caches of the API. The result cache keeps one JSON file per graded trade or finder pair, and data.
The teams cache keeps the teams answer per season in memory for a short window, so the trade form fills at once.
"""
import hashlib
import json
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from analyzer.finder_search import Anchor, Limit
from analyzer.trade import ProposedTrade
from analyzer.week_line import chart_is_fresh, counted_status, last_game_status
from league.ranks import due_back_week
from league.snapshot import Snapshot

# The stat fields the grade reads from a week N line, past the points key of the League settings of the client.
# A change to any other field keeps the hit.
STAT_FIELDS = ("gp", "off_snp", "tm_off_snp", "rec_tgt", "rec_rz_tgt", "rush_rz_att")


# The shape of the stored result document. A change of shape bumps it, so the key changes and a result stored on
# the volume in an old shape never serves again.
# A bump is the right move for a shape change: the stored document holds no letter, so no code can add a new
# block to it later, and only a new key keeps a document in the old shape from a hit.
# A change to a grade rule bumps it too, so a grade stored under the old rule never serves.
DOCUMENT_VERSION = 26


def cache_key(trade: ProposedTrade, snapshot: Snapshot) -> str:
    """The hash of the trade and the content of the snapshot that the grade reads.

    The key holds a hash of every roster in the trade and of each record, not the fetch time. The fetch time changes on
    every request, so it would never hit. A roster change on Sleeper changes the hash, so a stale grade never serves.
    """
    as_of = snapshot.as_of
    roster_ids = [side.roster_id for side in trade.sides]
    parts = {
        "document_version": DOCUMENT_VERSION,
        "season": trade.season,
        # The sides keep their order, because the document lists the sides in the order of the request.
        # Each player keeps his destination, because in a trade of three or more sides it changes what a side gets.
        "sides": [[side.roster_id, sorted([p.player_id, p.to] for p in side.gives)] for side in trade.sides],
        "asker": trade.asker,
        # None for a week with no chart, so the first chart post of the week gives a new key and a fresh grade.
        "chart_week": as_of.chart_week,
        "stats_through": as_of.stats_through,
        # On a Tuesday and a Wednesday the Week line says "listed Out last week", so a grade of another day misses it.
        "last_game_status": last_game_status(snapshot),
        # A new depth chart can move a step-up, and a chart that grows too old names none. Decision 02.
        "depth_chart_dt": snapshot.depth_chart_dt.isoformat() if snapshot.depth_chart_dt else None,
        "chart_is_fresh": chart_is_fresh(snapshot),
        "week_line_statuses": _week_line_statuses(snapshot, roster_ids),
        "content": _content_hash(snapshot, roster_ids),
    }
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()


def _week_line_statuses(snapshot: Snapshot, roster_ids: list[int]) -> dict[str, list]:
    """The status of each player on the rosters in the trade, and of the player ahead of him on his depth chart.

    The Week line reads both: the first for the absences, the second for a step-up. The player ahead is often on no
    roster, so no other part of the key holds his status or his return week. A status that the Week line never
    counts, such as Questionable, reads as None, so a move between two of them keeps the hit.
    """
    statuses: dict[str, list] = {}
    for player in sorted({pid for roster_id in roster_ids for pid in snapshot.rosters[roster_id]}):
        entry: list = [counted_status(snapshot.players[player].injury_status)]
        ahead = snapshot.ahead_on_chart.get(player)
        if ahead is not None:
            entry += [ahead.player_id, counted_status(ahead.injury_status), snapshot.returns.get(ahead.player_id)]
        statuses[player] = entry
    return statuses


def _content_hash(snapshot: Snapshot, roster_ids: list[int]) -> str:
    """The hash of the players, the record, the week rows, and the week N lines and WOPR rows of each roster.

    The analyze key and the find key share it.

    The week rows are the due-back week and the projections ahead of each rostered player due back. The commissioner
    edits the returns file by hand, Sleeper moves projections daily, and a move into the out set makes a player due
    back. `DOCUMENT_VERSION` covers a deploy only, so the rows must be in the key.
    The week N lines are the stat lines of a known-games week, cut to the fields the grade reads. A new fetch with a
    new number for a rostered player is a new key. A week with no known games adds none.
    Only the rows and lines of the rosters in the trade go in, so a change to any other player keeps the hit. A change
    that moves a position rank is one exception.
    The key holds only the projection rows the grade can read. These are the rows of a player due back, from his
    return week through the last regular week. A change to any other row would miss, but the grade would not change.
    The NFL teams whose known game is in progress go in too, because the reasons name a game in progress.
    The known-games block of the stamp goes in, because the document shows its counts. A stale stats fetch goes in,
    because a failed week N fetch grades from the completed week. The week N WOPR rows of the rosters in the trade go
    in, because the trend step reads them once the player file posts them.
    The rank table goes in: the player ids per position in position rank order. A rank reads every player at the
    position, rostered or not, so a line of a free agent or of a third roster can move it. The table itself is
    the exact input. A line that moves a rank misses. A line that moves none, such as a K line, keeps the hit.
    The free agent ids per position go in, because the hole fact names the best free agent. The rank table
    already covers their stat lines, so a new free agent or one who leaves the pool is the only change left.
    The players out for the season go in, from every roster. A mark zeroes a chart value, moves a rank, and opens an
    opportunity for a teammate on any roster, so a mark on any player is the other exception.
    """
    standings = {standing.roster_id: standing for standing in snapshot.standings}
    projections_ahead = snapshot.projections_ahead or {}
    # The returns file keeps a return week after the player is back, but the grade reads only a week still ahead.
    # The grade reads the due-back week through the same rule, so the key and the grade agree on who is due back.
    rostered = {player for roster_id in roster_ids for player in snapshot.rosters[roster_id]}
    due_back = {player: week for player in rostered if (week := due_back_week(snapshot, player)) is not None}
    week_n_lines = _week_n_lines(snapshot)
    week_n_wopr = _week_n_wopr(snapshot)
    content = {
        roster_id: {
            "players": sorted(snapshot.rosters[roster_id]),
            "record": standings[roster_id].model_dump(mode="json") if roster_id in standings else None,
            "returns": {player: due_back[player] for player in snapshot.rosters[roster_id] if player in due_back},
            # A player out with no returns row gets other words in the reason than a row of the same week.
            "on_file": sorted(player for player in snapshot.rosters[roster_id]
                              if player in due_back and player in snapshot.returns),
            "projections_ahead": {player: _rows_read(projections_ahead.get(player, {}), due_back[player],
                                                     snapshot.client.settings.last_regular_week)
                                  for player in snapshot.rosters[roster_id] if player in due_back},
            "week_n_lines": {player: week_n_lines[player] for player in sorted(snapshot.rosters[roster_id])
                             if player in week_n_lines},
            "week_n_wopr": {player: week_n_wopr[player] for player in sorted(snapshot.rosters[roster_id])
                            if player in week_n_wopr},
        }
        for roster_id in roster_ids
    }
    # With no projections file every player keeps his recent points, so None and an empty file grade apart.
    content = {"has_projections_ahead": snapshot.projections_ahead is not None, "rosters": content,
               # A reason says "game in progress" only while the game is on, so a final game must miss that grade.
               "in_progress_teams": sorted(snapshot.in_progress_teams),
               "known_games": snapshot.as_of.known_games.model_dump() if snapshot.as_of.known_games else None,
               "stats_stale": "stats" in snapshot.stale,
               "rank_table": snapshot.rank_table(),
               "out_for_season": sorted(snapshot.out_for_season),
               "free_agents": {position: [player.player_id for player in players]
                               for position, players in snapshot.free_agents.items()}}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def _week_n_lines(snapshot: Snapshot) -> dict[str, dict[str, float]]:
    """The week N stat line of each player, cut to the fields the grade reads. Empty with no known games.

    Week N is in the player stats when the stat bound is past the completed week. A player with no line, or a line
    with none of the fields, has no entry, so no lines and empty lines give one key.
    """
    as_of = snapshot.as_of
    if as_of.stats_through <= as_of.completed_through or as_of.stats_through not in snapshot.stats.weeks:
        return {}
    lines = snapshot.stats.weeks[as_of.stats_through].stats
    # The grade reads the points of the scoring of the client, such as pts_ppr for a full PPR league.
    fields = (snapshot.client.settings.points_key, *STAT_FIELDS)
    reduced = {player: {field: line[field] for field in fields if field in line} for player, line in lines.items()}
    return {player: line for player, line in reduced.items() if line}


def _week_n_wopr(snapshot: Snapshot) -> dict[str, int]:
    """The week N WOPR row of each player in the nflverse player file. Empty with no known games or no file."""
    as_of = snapshot.as_of
    if as_of.stats_through <= as_of.completed_through or snapshot.wopr is None:
        return {}
    return {player: weeks[as_of.stats_through] for player, weeks in snapshot.wopr.items()
            if as_of.stats_through in weeks}


def _rows_read(rows: dict[int, float], return_week: int, last_regular_week: int) -> dict[int, float]:
    """The projection rows of one player that the projection ahead reads, from the return week through the last."""
    return {week: points for week, points in rows.items() if return_week <= week <= last_regular_week}


def finder_cache_key(season: int, asker: int, partner: int | None, snapshot: Snapshot,
                     anchor: Anchor | None = None, limit: Limit | None = None) -> str:
    """The hash of the ordered pair of rosters and the content of the snapshot that the finder reads.

    With no partner, the search reads every roster, so the content of every roster goes in.
    The anchor of a search around one player goes in too, so a search around a player never serves the plain list.
    The limit of the manager goes in too, so a search with a limit never serves a list that breaks it.

    The pair keeps its order, so the asker is part of the key. The finder puts the asker's side first in each
    trade, and its rank breaks a tie by the asker's letter. So the document for A and B can differ from the one
    for B and A, and one key for both orders could serve the wrong list.
    """
    as_of = snapshot.as_of
    parts = {
        "document_version": DOCUMENT_VERSION,
        # The kind keeps a finder key apart from every analyze key in the shared directory.
        "kind": "find",
        "season": season,
        "rosters": [asker, partner],
        "anchor": None if anchor is None else [anchor.player_id, anchor.side],
        "limit": None if limit is None else limit.model_dump(),
        "chart_week": as_of.chart_week,
        "stats_through": as_of.stats_through,
        "content": _content_hash(snapshot, [asker, partner] if partner is not None else sorted(snapshot.rosters)),
    }
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()


def sell_high_cache_key(season: int, roster_id: int, snapshot: Snapshot) -> str:
    """The hash of the roster and the content of the snapshot that the sell high pick reads.

    The kind keeps a sell high key apart from every analyze key and every finder key in the shared directory.
    """
    as_of = snapshot.as_of
    parts = {
        "document_version": DOCUMENT_VERSION,
        "kind": "sell_high",
        "season": season,
        "roster": roster_id,
        "chart_week": as_of.chart_week,
        "stats_through": as_of.stats_through,
        "content": _content_hash(snapshot, [roster_id]),
    }
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()


class ResultCache:
    """The result documents on disk, one file per key, under a directory on the data volume."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, document: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        # A write to a temporary file and a rename, so a crash never leaves half a document for a later hit.
        path = self._path(key)
        partial = path.with_suffix(".tmp")
        partial.write_text(json.dumps(document), encoding="utf-8")
        partial.replace(path)


class TeamsEntry(NamedTuple):
    """One teams answer and the monotonic time of its build."""

    built_at: float
    answer: dict


class TeamsCache:
    """The last teams answer per season, with the monotonic time of its build.

    One lock covers the check and the build, so two first requests make one build and not two.
    Only the teams route builds through it, so the refresh route and the analyze route never wait on a build.
    """

    def __init__(self, max_age_seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.max_age_seconds = max_age_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._entries: dict[int, TeamsEntry] = {}

    def get_or_build(self, season: int, build: Callable[[], dict]) -> dict:
        """The answer for `season` from memory within the window. Past it, `build` runs and the cache keeps its answer.

        A build that raises leaves the cache as it was, so the next request tries again.
        """
        with self._lock:
            entry = self._entries.get(season)
            if entry is not None and self.clock() - entry.built_at < self.max_age_seconds:
                return entry.answer
            answer = build()
            self._entries[season] = TeamsEntry(built_at=self.clock(), answer=answer)
            return answer

    def clear(self, season: int) -> None:
        """Drop the answer for `season`, so the next request builds again."""
        # A dict pop is atomic, so the analyze route clears with no wait on a build that holds the lock.
        self._entries.pop(season, None)
