"""
The waiver price: the bid to win of each player, the last like him, and the outbid counts per budget level.
Pure code over the raw files and the bid history of the season, so the same inputs give the same price.
"""
import json
import math
from collections import Counter
from pathlib import Path
from typing import NamedTuple

from cornerstone.adjusters import OUT_STATUSES
from cornerstone.history import history_dir
from cornerstone.models import LastLike, WaiverClaim, WaiverPlayer, WaiverPrice
from cornerstone.parse import player_name
from cornerstone.sheet import Nums, fact
from cornerstone.tunables import NEED_SHARE

# Sleeper marks a claim that won as complete and a claim that lost as failed.
CLAIM_RESULTS = {"complete": True, "failed": False}


def bid_history(root: Path, raw: dict[str, object], week: int) -> list[WaiverClaim]:
    """Every waiver claim of weeks 1 to `week`: the saved history before `week`, and the raw files of `week`."""
    positions = {pid: entry.get("position") for pid, entry in raw["players"].items()}
    claims = []
    for past in range(1, week):
        path = history_dir(root, past) / "transactions.json"
        # A week that is not saved has no claims, so a gap lowers the floor and never makes a claim wrong.
        if path.exists():
            claims += _claims(json.loads(path.read_text()), positions)
    return claims + _claims(raw["transactions"], positions)


def _claims(transactions: list[dict], positions: dict[str, str | None]) -> list[WaiverClaim]:
    return [
        WaiverClaim(
            player_id=player_id,
            roster_id=roster_id,
            position=positions.get(player_id),
            week=t["leg"],
            # A claim with no bid set is a $0 claim.
            bid=(t.get("settings") or {}).get("waiver_bid") or 0,
            won=CLAIM_RESULTS[t["status"]],
        )
        for t in transactions
        if t["type"] == "waiver" and t["status"] in CLAIM_RESULTS
        for player_id, roster_id in (t["adds"] or {}).items()
    ]


class Rival(NamedTuple):
    """One roster of the league as a bidder: its team name, its budget left, and its healthy players by position."""
    roster_id: int
    team: str
    budget_left: int
    healthy: Counter


class Bid(NamedTuple):
    """The bid the model expects from one rival on one player."""
    rival: Rival
    need: bool
    amount: float


def price_players(players: list[WaiverPlayer], raw: dict[str, object], claims: list[WaiverClaim]) -> list[WaiverPlayer]:
    """Each player of `players` with his price. A rival is every roster: the site takes out the viewer's own."""
    rivals = _rivals(raw)
    teams = {r.roster_id: r.team for r in rivals}
    # Only the dedicated slots count. A FLEX slot takes any of several positions, so no one position needs it.
    slots = Counter(raw["league"]["roster_positions"])
    return [
        p.model_copy(update={"price": _price(p, rivals, slots[p.position], claims,
                                             _last_like(p.position, claims, raw["players"], teams))})
        for p in players
    ]


def _price(
    player: WaiverPlayer, rivals: list[Rival], slots: int, claims: list[WaiverClaim], last_like: LastLike | None,
) -> WaiverPrice:
    top = max((_expected_bid(r, player.position, slots) for r in rivals), key=lambda b: b.amount)
    past = max((c.bid for c in claims if c.won and c.position == player.position), default=None)
    ceiling = max(r.budget_left for r in rivals)
    # The smallest whole dollar above the top expected bid, and above the top past win at the position.
    floor = max(math.floor(top.amount), past if past is not None else 0) + 1
    bid = min(floor, ceiling)
    n = Nums()
    text = (f"Bid ${n(bid)} to win {player.name}. The top rival bid is about ${n(top.amount)}, "
            f"from {top.rival.team} with ${n(top.rival.budget_left)} left")
    text += f" and a need at {player.position}." if top.need else "."
    if past is not None:
        text += f" The top winning {player.position} claim this season is ${n(past)}."
    if bid < floor:
        text += f" No rival has more than ${n(ceiling)} left."
    return WaiverPrice(bid=bid, fact=fact(f"waiver_price_{player.player_id}", text, n, [top.rival.team], [player.name]),
                       last_like=last_like)


def _last_like(position: str, claims: list[WaiverClaim], players: dict[str, dict], teams: dict[int, str]) -> LastLike | None:
    """The latest winning claim at `position`. Inside one week the higher bid, then the player ID, breaks the tie.

    The match is on position alone. The bucket tier joins the match once more buckets than best adds exist.
    """
    won = [c for c in claims if c.won and c.position == position]
    if not won:
        return None
    last = max(won, key=lambda c: (c.week, c.bid, c.player_id))
    return LastLike(player_id=last.player_id, name=player_name(last.player_id, players.get(last.player_id)),
                    roster_id=last.roster_id, team=teams.get(last.roster_id, ""), week=last.week, bid=last.bid)


def _expected_bid(rival: Rival, position: str, slots: int) -> Bid:
    need = rival.healthy[position] < slots
    share = NEED_SHARE["need" if need else "covered"]
    return Bid(rival=rival, need=need, amount=min(rival.budget_left * share, rival.budget_left))


def _rivals(raw: dict[str, object]) -> list[Rival]:
    budget = raw["league"]["settings"]["waiver_budget"]
    users = {u["user_id"]: u for u in raw["users"]}
    rivals = []
    for roster in sorted(raw["rosters"], key=lambda r: r["roster_id"]):
        # A roster with no players has None in rosters.json.
        entries = [raw["players"].get(pid) or {} for pid in roster.get("players") or []]
        healthy = Counter(e.get("position") for e in entries if e.get("injury_status") not in OUT_STATUSES)
        rivals.append(Rival(roster_id=roster["roster_id"], team=_team_name(users.get(roster["owner_id"]) or {}), healthy=healthy,
                            budget_left=budget - roster["settings"]["waiver_budget_used"]))
    return rivals


def _team_name(user: dict) -> str:
    # The same rule as the parse of the week: the team name, else the display name.
    return (user.get("metadata") or {}).get("team_name") or user.get("display_name") or ""
