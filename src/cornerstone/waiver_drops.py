"""
The drops bucket of the waiver board: rostered players whose snap share fell three weeks in a row.
Pure code over the raw files and the usage, so the same inputs give the same bucket.
"""
from cornerstone.config import LeagueConfig
from cornerstone.numbers import round_half_up
from cornerstone.models import BoardScores, DropInfo, UsageWeek, WaiverPlayer
from cornerstone.parse import player_name, team_name
from cornerstone.sheet.base import Nums, fact
from cornerstone.provider.raw import RawWeek
from cornerstone.tunables import BUCKET_POSITIONS, DROP_WEEKS
from cornerstone.waiver_projection import next_week, projections_ahead, rest_of_season


def drop_candidates(
    raw: RawWeek, week: int, usage: dict[str, list[UsageWeek]], pool: list[WaiverPlayer], config: LeagueConfig,
) -> list[WaiverPlayer]:
    """The drop candidates after week `week`: rostered players with DROP_WEEKS falls of the snap share in a row.

    A drop candidate also has a better pool player: the one with the highest rest of season projection at
    his position. The result is every drop candidate, the largest margin first. The engine applies the cap.
    """
    ahead = projections_ahead(raw)
    best = _best_by_position(pool)
    users = {u.user_id: u for u in raw.users}
    remaining = config.last_season_week - week
    candidates = []
    for roster in sorted(raw.rosters, key=lambda r: r.roster_id):
        # A roster with no players has None in rosters.json.
        for pid in sorted(roster.players or []):
            entry = raw.players.get(pid) or {}
            top = best.get(entry.get("position"))
            if top is None or remaining <= 0 or not _falls(usage.get(pid, []), week):
                continue
            ros = rest_of_season(ahead, pid, week, config)
            if ros >= top.ros_projection:
                continue
            info = DropInfo(roster_id=roster.roster_id, holder=team_name(users[roster.owner_id]),
                            beaten_by=top.player_id, beaten_by_name=top.name,
                            margin=round_half_up((top.ros_projection - ros) / remaining, 1))
            candidates.append(_candidate(pid, entry, info, next_week(ahead, pid, week), ros))
    return sorted(candidates, key=lambda c: (-c.drop.margin, c.player_id))


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


def _candidate(player_id: str, entry: dict, info: DropInfo, week_projection: float, ros: float) -> WaiverPlayer:
    """The drop candidate with his drop fact. He has no board score, as the bucket ranks by the margin."""
    name = player_name(player_id, entry)
    n = Nums()
    text = f"{info.holder} holds {name}, and {info.beaten_by_name} projects {n(info.margin)} points a week higher."
    return WaiverPlayer(
        player_id=player_id, name=name, position=entry["position"], team=entry.get("team") or "",
        week_projection=week_projection, ros_projection=ros, scores=BoardScores(), board_score=0.0,
        facts=[fact(f"WV.drop.{player_id}", text, n, [info.holder], [name, info.beaten_by_name])], drop=info)
