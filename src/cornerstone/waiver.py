"""
The waiver board engine: it ranks the waiver pool into buckets and builds the budget table of the league.
Pure code: no network and no Claude, so the same raw data gives the same board.
"""
from datetime import datetime

from cornerstone.models import BoardScores, BudgetRow, Fact, WaiverBoard, WaiverPlayer, r2
from cornerstone.parse import player_name
from cornerstone.tunables import BEST_ADDS_POSITIONS, BOARD_WEIGHTS, BUCKET_SIZE, LAST_SEASON_WEEK, PER_POSITION

# The positions of the pool. The Sleeper fetch asks for the same positions. A player at another position,
# such as a linebacker, is never in the pool.
POOL_POSITIONS = ("QB", "RB", "WR", "TE", "K", "DEF")
BEST_ADDS = "best_adds"
TRENDING = "trending"


def waiver_board(raw: dict[str, object], week: int, built: datetime) -> WaiverBoard:
    """The board after week `week` from the raw files of the week. `built` is the build time the file shows."""
    ahead = {entry["week"]: entry["projections"] for entry in raw.get("projections_ahead", [])}
    rostered = _rostered(raw)
    pool = {pid: entry for pid, entry in sorted(raw["players"].items()) if _in_pool(entry, rostered, pid)}
    # A week with no projection for the player, such as his bye, counts 0.
    ros = {pid: r2(sum(ahead.get(w, {}).get(pid, 0.0) for w in range(week + 1, LAST_SEASON_WEEK + 1)))
           for pid in pool}
    projection = _projection_scores({pid: entry["position"] for pid, entry in pool.items()}, ros)
    players = [
        _pool_player(pid, entry, r2(ahead.get(week + 1, {}).get(pid, 0.0)), ros[pid],
                     BoardScores(projection=projection[pid]))
        for pid, entry in pool.items()
    ]
    players = _with_trending(players, _trending_counts(raw))
    best_adds = _capped(sorted((p for p in players if p.position in BEST_ADDS_POSITIONS), key=_rank_key))
    return WaiverBoard(week=week, built=built, buckets={BEST_ADDS: best_adds, TRENDING: _trending_bucket(players)},
                       budgets=_budgets(raw))


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


def _projection_scores(positions: dict[str, str], ros: dict[str, float]) -> dict[str, float]:
    """The projection score of each player: his rest of season rank inside the position, from 1 for the best to 0.

    Players with the same projection share the better rank.
    """
    by_position: dict[str, list[float]] = {}
    for pid, position in positions.items():
        by_position.setdefault(position, []).append(ros[pid])
    for values in by_position.values():
        values.sort(reverse=True)
    scores = {}
    for pid, position in positions.items():
        values = by_position[position]
        ahead_of = values.index(ros[pid])
        scores[pid] = 1.0 if len(values) == 1 else round(1 - ahead_of / (len(values) - 1), 4)
    return scores


def _pool_player(player_id: str, entry: dict, week_projection: float, ros: float, scores: BoardScores) -> WaiverPlayer:
    return WaiverPlayer(
        player_id=player_id,
        name=player_name(player_id, entry),
        position=entry["position"],
        team=entry["team"],
        week_projection=week_projection,
        ros_projection=ros,
        scores=scores,
        board_score=round(sum(weight * getattr(scores, key) for key, weight in BOARD_WEIGHTS.items()), 4),
    )


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


def _trending_counts(raw: dict[str, object]) -> dict[str, int]:
    """The trending count of each player in the trending file. A week with no file has no counts."""
    return {row["player_id"]: row["count"] for row in raw.get("trending", [])}


def _with_trending(players: list[WaiverPlayer], counts: dict[str, int]) -> list[WaiverPlayer]:
    """The players with the trending count of each. A player with no count keeps 0."""
    return [p.model_copy(update={"trending_count": counts[p.player_id],
                                 "facts": [*p.facts, _trending_fact(p, counts[p.player_id])]})
            if p.player_id in counts else p
            for p in players]


def _trending_fact(p: WaiverPlayer, count: int) -> Fact:
    """The count fact of a trending player. The count is written plain, as a comma would split it into two numbers."""
    # The sheet module imports the Sleeper client, which imports this module, so the fact skips its Nums helper.
    # The one number goes into the text and the numbers from the same string.
    number = str(count)
    text = f"{p.name} was added in {number} Sleeper leagues in the last day."
    return Fact(id=f"WV.trending.{p.player_id}", text=text, numbers=[number], teams=[], players=[p.name])


def _trending_bucket(players: list[WaiverPlayer]) -> list[WaiverPlayer]:
    """The pool players with a trending count, the most adds first.

    The player ID breaks a tie, so a tie has one order.
    """
    return _capped(sorted((p for p in players if p.trending_count),
                          key=lambda p: (-p.trending_count, p.player_id)))
