"""
The waiver board engine: it ranks the free agent pool into buckets and builds the budget table of the league.
Pure code: no network and no Claude, so the same raw data gives the same board.
"""
from datetime import datetime

from cornerstone.models import BoardScores, BudgetRow, WaiverBoard, WaiverPlayer, r2
from cornerstone.parse import player_name
from cornerstone.sleeper import LAST_SEASON_WEEK
from cornerstone.tunables import BOARD_WEIGHTS, BUCKET_SIZE, PER_POSITION

# The positions of the pool. A player at another position, such as a linebacker, is never a free agent add.
POOL_POSITIONS = ("QB", "RB", "WR", "TE", "K", "DEF")
BEST_ADDS = "best_adds"


def waiver_board(raw: dict[str, object], week: int, built: datetime) -> WaiverBoard:
    """The board after week `week` from the raw files of the week. `built` is the build time the file shows."""
    ahead = {entry["week"]: entry["projections"] for entry in raw.get("projections_ahead", [])}
    rostered = _rostered(raw)
    pool = [_pool_player(pid, entry, ahead, week) for pid, entry in sorted(raw["players"].items())
            if _in_pool(entry, rostered, pid)]
    _score(pool)
    best_adds = _capped(sorted(pool, key=_rank_key))
    return WaiverBoard(week=week, built=built, buckets={BEST_ADDS: best_adds}, budgets=_budgets(raw))


def _budgets(raw: dict[str, object]) -> list[BudgetRow]:
    """One row per roster in roster order: the league budget minus the budget used, and the waiver position."""
    budget = raw["league"]["settings"]["waiver_budget"]
    return [
        BudgetRow(
            roster_id=roster["roster_id"],
            budget_left=budget - roster["settings"]["waiver_budget_used"],
            waiver_order=roster["settings"]["waiver_position"],
        )
        for roster in sorted(raw["rosters"], key=lambda r: r["roster_id"])
    ]


def _rostered(raw: dict[str, object]) -> set[str]:
    # A roster with no players has None in rosters.json.
    return {pid for roster in raw["rosters"] for pid in roster.get("players") or []}


def _in_pool(entry: dict, rostered: set[str], player_id: str) -> bool:
    """A player with a team, active, at a pool position, and on no roster in the league."""
    if player_id in rostered or not entry.get("team") or entry.get("position") not in POOL_POSITIONS:
        return False
    # Sleeper gives a defense no status, only the active flag.
    if entry["position"] == "DEF":
        return entry.get("active") is True
    return entry.get("status") == "Active"


def _pool_player(player_id: str, entry: dict, ahead: dict[int, dict[str, float]], week: int) -> WaiverPlayer:
    # A week with no projection for the player, such as his bye, counts 0.
    ros = sum(ahead.get(w, {}).get(player_id, 0.0) for w in range(week + 1, LAST_SEASON_WEEK + 1))
    return WaiverPlayer(
        player_id=player_id,
        name=player_name(player_id, entry),
        position=entry["position"],
        team=entry["team"],
        week_projection=r2(ahead.get(week + 1, {}).get(player_id, 0.0)),
        ros_projection=r2(ros),
        scores=BoardScores(),
        board_score=0.0,
    )


def _score(pool: list[WaiverPlayer]) -> None:
    """Set the projection score and the board score of each player in place.

    The projection score is the rest of season rank inside the position, from 1 for the best to 0 for the last.
    Players with the same projection share the better rank.
    """
    by_position: dict[str, list[float]] = {}
    for p in pool:
        by_position.setdefault(p.position, []).append(p.ros_projection)
    for values in by_position.values():
        values.sort(reverse=True)
    for p in pool:
        values = by_position[p.position]
        ahead_of = values.index(p.ros_projection)
        p.scores.projection = 1.0 if len(values) == 1 else round(1 - ahead_of / (len(values) - 1), 4)
        p.board_score = round(sum(weight * getattr(p.scores, key) for key, weight in BOARD_WEIGHTS.items()), 4)


def _capped(ranked: list[WaiverPlayer]) -> list[WaiverPlayer]:
    """The first BUCKET_SIZE players of `ranked`, with at most PER_POSITION of one position."""
    bucket: list[WaiverPlayer] = []
    taken: dict[str, int] = {}
    for p in ranked:
        if len(bucket) == BUCKET_SIZE:
            break
        if taken.get(p.position, 0) < PER_POSITION:
            bucket.append(p)
            taken[p.position] = taken.get(p.position, 0) + 1
    return bucket


def _rank_key(p: WaiverPlayer) -> tuple[float, float, str]:
    """Best board score first, then the higher rest of season projection, then the player ID, so a tie has one order."""
    return -p.board_score, -p.ros_projection, p.player_id
