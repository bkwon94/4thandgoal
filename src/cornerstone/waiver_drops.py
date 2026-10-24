"""
The drops bucket of the waiver board: rostered players whose snap share fell week after week.
Pure code over the raw files and the usage, so the same inputs give the same bucket.
"""
from cornerstone.history import _round_half_up
from cornerstone.models import BoardScores, DropPlayer, UsageWeek, WaiverPlayer, r2
from cornerstone.parse import player_name, team_name
from cornerstone.sheet import Nums, fact
from cornerstone.tunables import BUCKET_POSITIONS, DROP_WEEKS, LAST_SEASON_WEEK

THREE_FALLS = "three_falls"


def drop_candidates(
    raw: dict[str, object], week: int, usage: dict[str, list[UsageWeek]], pool: list[WaiverPlayer],
) -> list[DropPlayer]:
    """The rostered players after week `week` with DROP_WEEKS falls of the snap share and a better pool player.

    The falls are in a row. The better pool player has the highest rest of season projection at the position.
    The result is every candidate, the largest gap first. The engine applies the bucket cap.
    """
    ahead = {entry["week"]: entry["projections"] for entry in raw.get("projections_ahead", [])}
    best = _best_by_position(pool)
    users = {u["user_id"]: u for u in raw["users"]}
    remaining = LAST_SEASON_WEEK - week
    drops = []
    for roster in sorted(raw["rosters"], key=lambda r: r["roster_id"]):
        # A roster with no players has None in rosters.json.
        for pid in sorted(roster.get("players") or []):
            entry = raw["players"].get(pid) or {}
            top = best.get(entry.get("position"))
            if top is None or remaining <= 0 or not _falls(usage.get(pid, []), week):
                continue
            # The same sum as the pool's rest of season projection: weeks N+1 to 17, a week with none counts 0.
            ros = r2(sum(ahead.get(w, {}).get(pid, 0.0) for w in range(week + 1, LAST_SEASON_WEEK + 1)))
            if ros >= top.ros_projection:
                continue
            gap = _round_half_up((top.ros_projection - ros) / remaining, 1)
            drops.append(_drop(pid, entry, roster["roster_id"], team_name(users[roster["owner_id"]]), top, gap,
                               r2(ahead.get(week + 1, {}).get(pid, 0.0)), ros))
    return sorted(drops, key=lambda d: (-d.gap, d.player_id))


def _best_by_position(pool: list[WaiverPlayer]) -> dict[str, WaiverPlayer]:
    """The pool player with the highest rest of season projection at each bucket position.

    The player ID breaks a tie, so a tie has one result.
    """
    best: dict[str, WaiverPlayer] = {}
    for p in sorted(pool, key=lambda p: (-p.ros_projection, p.player_id)):
        if p.position in BUCKET_POSITIONS:
            best.setdefault(p.position, p)
    return best


def _falls(rows: list[UsageWeek], week: int) -> bool:
    """True when the snap share of each of the DROP_WEEKS weeks up to `week` is lower than the week before.

    A week with no row or no snap share, such as a bye, breaks the run, so the rule reads only weeks he played.
    """
    by_week = {u.week: u.snap_share for u in rows if u.snap_share is not None}
    shares = [by_week.get(w) for w in range(week - DROP_WEEKS, week + 1)]
    if None in shares:
        return False
    return all(later < earlier for earlier, later in zip(shares, shares[1:]))


def _drop(player_id: str, entry: dict, roster_id: int, holder: str, top: WaiverPlayer, gap: float,
          week_projection: float, ros: float) -> DropPlayer:
    name = player_name(player_id, entry)
    n = Nums()
    text = f"{holder} holds {name}, and {top.name} projects {n(gap)} points a week higher."
    return DropPlayer(
        player_id=player_id, name=name, position=entry["position"], team=entry.get("team") or "",
        week_projection=week_projection, ros_projection=ros, scores=BoardScores(), board_score=0.0,
        facts=[fact(f"WV.drop.{player_id}", text, n, [holder], [name, top.name])],
        roster_id=roster_id, holder=holder, reason=THREE_FALLS, beaten_by=top.player_id, beaten_by_name=top.name,
        gap=gap)
