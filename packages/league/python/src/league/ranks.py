"""
The position rank and what it reads: the lineup value of each player, his due-back week, and the pool rule.
It imports no snapshot at run time, so the snapshot, the adjusters, and the waiver board all import it with no cycle.
"""
from __future__ import annotations

from collections.abc import Collection
from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from league.history import player_points
from league.models import PastWeek
from league.tunables import LINEUP_WEEKS

if TYPE_CHECKING:
    # The snapshot module imports this one, so the snapshot is a name for the type checker only.
    from league.snapshot import Snapshot

# The tie rule at equal points per game. A position not in the order ranks last.
POSITION_ORDER = ("RB", "WR", "TE", "QB", "K", "DEF")

# Injury report statuses that keep a player out of games. A player with one of them and no row in the
# returns file has no known return, so the standing adjuster counts him as back after the return-by week of the
# client. The lineup value counts him as due back at that week, so his projection ahead gives his value.
OUT_STATUSES = frozenset({"Out", "IR", "NA", "Sus", "PUP"})

# The points per game that the lineup value reads. GLOSSARY.md, "Position rank".
# "recent" reads the last LINEUP_WEEKS weeks. The weekly report reads it.
# "season" reads every week of the season. The grade reads it, so one big game in a short window cannot move a player
# about 40 spots. Decision 01 of grade-clarity.
RankMeasure = Literal["recent", "season"]


def recent_points_per_game(snapshot: Snapshot, player_id: str) -> Decimal:
    """The points per game over the last weeks through the player stat bound, LINEUP_WEEKS at most.

    The window ends at the known games for a player who played in week N, and at the last completed week otherwise.
    So a player's points per game move only when he plays. A player with no game in the window has 0.
    """
    return _points_per_game(snapshot, player_id, _played_weeks(snapshot, player_id, "recent"))


def season_points_per_game(snapshot: Snapshot, player_id: str) -> Decimal:
    """The points per game over every game the player played this season, through the player stat bound.

    The season ends at the known games by the rule of recent_points_per_game. A player with no game has 0.
    """
    return _points_per_game(snapshot, player_id, _played_weeks(snapshot, player_id, "season"))


def _points_per_game(snapshot: Snapshot, player_id: str, played: list[PastWeek]) -> Decimal:
    if not played:
        return Decimal(0)
    # Sleeper leaves out a stat whose value is 0. A game with no points entry is a game of 0 points.
    total = sum((Decimal(str(player_points(past, player_id) or 0)) for past in played), Decimal(0))
    return total / len(played)


def _played_weeks(snapshot: Snapshot, player_id: str, measure: RankMeasure | None = None) -> list[PastWeek]:
    """The weeks the player played in the window of `measure`, the rank measure of the snapshot by default.

    The "recent" window holds LINEUP_WEEKS weeks at most. The "season" window starts at week 1.
    """
    measure = measure or snapshot.rank_measure
    last = snapshot.as_of.stats_through
    if last > snapshot.as_of.completed_through and not _has_known_game(snapshot, player_id):
        last = snapshot.as_of.completed_through
    first = 1 if measure == "season" else max(1, last - LINEUP_WEEKS + 1)
    return [
        snapshot.stats.weeks[week] for week in range(first, last + 1)
        if week in snapshot.stats.weeks
        and (snapshot.stats.weeks[week].stats.get(player_id) or {}).get("gp", 0) > 0
    ]


def projection_ahead(snapshot: Snapshot, player_id: str) -> Decimal:
    """The mean of the player's weekly projections from his due-back week through the last regular week.

    A week with no projection row, such as a bye, is no game. With no row in those weeks, he counts for 0.
    """
    rows = snapshot.projections_ahead.get(player_id, {})
    last = snapshot.client.settings.last_regular_week
    weeks = [rows[week] for week in range(due_back_week(snapshot, player_id), last + 1) if week in rows]
    if not weeks:
        return Decimal(0)
    return sum((Decimal(str(points)) for points in weeks), Decimal(0)) / len(weeks)


def lineup_value(snapshot: Snapshot, player_id: str) -> Decimal:
    """The points per game the player counts for in a best lineup.

    A player due back has no recent games, so his projection ahead gives his lineup value.
    Every other player keeps his points per game by the rank measure of the snapshot: recent or season.
    With no projections file, all players keep them.
    A player out for the season plays no more games, so he counts for 0.
    """
    # He is never due back, so without this he would keep the recent points of the games before his injury.
    if player_id in snapshot.out_for_season:
        return Decimal(0)
    if snapshot.projections_ahead is not None and due_back_week(snapshot, player_id) is not None:
        return projection_ahead(snapshot, player_id)
    if snapshot.rank_measure == "season":
        return season_points_per_game(snapshot, player_id)
    return recent_points_per_game(snapshot, player_id)


# The positions with a position rank. K and DEF have none. GLOSSARY.md, "Position rank".
RANKED_POSITIONS = ("QB", "RB", "WR", "TE")


def rank_table(snapshot: Snapshot) -> dict[str, list[str]]:
    """The player ids at each of QB, RB, WR, and TE in position rank order, first to last.

    GLOSSARY.md, "Position rank". The index in the list plus one is the rank.

    The pool is every player with a stat line in the known games, rostered or not, plus every rostered player.
    A rostered player due back can have no stat line, and his projection ahead still gives him a lineup value.
    The order is lineup value, then the position order, then the player id. A player with no game in the window
    ranks last. His lineup value is 0, but so is the value of a player who scored 0, so the value alone cannot
    put him last. A due-back player ranks by his projection ahead, so he never counts as a player with no game.
    Snapshot.position_rank reads this table, so it builds once per snapshot. The finder grades about a thousand
    trades per call and must not rank the league per side.
    """
    # The known games end at the player stat bound, and a player is in the pool only with a stat line there.
    positions = {pid: past.positions[pid] for week, past in snapshot.stats.weeks.items()
                 if week <= snapshot.as_of.stats_through for pid in past.stats if pid in past.positions}
    # The players file is the source for a rostered player, as best_lineup reads it. A stat line gives the rest.
    positions.update({pid: player.position for pid, player in snapshot.players.items()})
    pool = [pid for pid, position in positions.items() if position in RANKED_POSITIONS]

    def due_back(pid: str) -> bool:
        return snapshot.projections_ahead is not None and due_back_week(snapshot, pid) is not None

    def order(pid: str) -> tuple[bool, Decimal, int, str]:
        no_game = not due_back(pid) and not _played_weeks(snapshot, pid)
        return (no_game, -lineup_value(snapshot, pid), POSITION_ORDER.index(positions[pid]), pid)

    return {position: sorted((pid for pid in pool if positions[pid] == position), key=order)
            for position in RANKED_POSITIONS}


def recent_rank(snapshot: Snapshot, player_id: str) -> int | None:
    """The player's Recent rank: his place at his position by points per game over the last LINEUP_WEEKS weeks.

    GLOSSARY.md, "Recent rank". The pool is the pool of the position rank. The rank has no due-back step and no
    out-for-season step, so it shows what the player scored, not what the grade counts him for.
    A tie shares the better place. None for a player outside the pool or with no game in the window.
    """
    player = snapshot.players.get(player_id)
    position = player.position if player is not None else None
    if position not in RANKED_POSITIONS or not _played_weeks(snapshot, player_id, "recent"):
        return None
    peers = snapshot.rank_table()[position]
    if player_id not in peers:
        return None
    mine = recent_points_per_game(snapshot, player_id)
    return 1 + sum(recent_points_per_game(snapshot, pid) > mine for pid in peers)


def _has_known_game(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player has a game played in the known games of the trade week."""
    if snapshot.as_of.stats_through <= snapshot.as_of.completed_through:
        return False
    known = snapshot.stats.weeks.get(snapshot.as_of.stats_through)
    return known is not None and (known.stats.get(player_id) or {}).get("gp", 0) > 0


def _back_in_a_known_game(snapshot: Snapshot, player_id: str) -> bool:
    """True when the returns file has the player back by the trade week and he played in its known games.

    A player out with no row who played is the player hurt in his game, so his known game does not end his absence.
    """
    week = snapshot.returns.get(player_id)
    return week is not None and week <= snapshot.as_of.stats_through and _has_known_game(snapshot, player_id)


def due_back_week(snapshot: Snapshot, player_id: str) -> int | None:
    """The week the player counts as back, or None when he is not due back.

    The returns file gives the week. A player out with no row counts as back at the return-by week of the client, the
    week the standing adjuster reads too. Sleeper projects 0 for the weeks he is out, so his projection ahead must
    start at that week.
    A week through the last completed week is no return ahead, so he is not due back.
    A player with a returns row by the trade week who played in its known games is back, so he is not due back.
    A player out for the season has no return, so he is never due back. GLOSSARY.md, "Out for the season".
    """
    if player_id in snapshot.out_for_season:
        return None
    if _back_in_a_known_game(snapshot, player_id):
        return None
    week = snapshot.returns.get(player_id)
    # The position rank reads players on no roster, and the snapshot holds no injury status for them.
    player = snapshot.players.get(player_id)
    if week is None and player is not None and player.injury_status in OUT_STATUSES:
        week = snapshot.client.settings.return_by_week
    return week if week is not None and week > snapshot.as_of.completed_through else None


def in_pool(entry: dict, rostered: set[str], player_id: str, positions: Collection[str]) -> bool:
    """The waiver pool rule: a player with a team, active, at a pool position, and on no roster in the league.

    The pool positions are `positions`, the positions the League settings start.
    A player with the status Inactive and an out injury status joins too, for stashes only.
    The waiver board and the snapshot's free agents both read this rule, so the two read the same pool.
    """
    if player_id in rostered or not entry.get("team") or entry.get("position") not in positions:
        return False
    # Sleeper gives a defense no status, only the active flag.
    if entry["position"] == "DEF":
        return entry.get("active") is True
    # Sleeper gives an IR player the status Inactive. He is the classic stash, so he joins the pool.
    if entry.get("status") == "Inactive" and entry.get("active") is True:
        return entry.get("injury_status") in OUT_STATUSES
    return entry.get("status") == "Active"

def back_inside(week: int | None, after: int, by: int) -> bool:
    """True when a return week falls after week `after` and by week `by`. No return week is never inside."""
    return week is not None and after < week <= by
