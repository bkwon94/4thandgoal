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
from cornerstone.paths import history_week_dir
from cornerstone.models import LastLike, WaiverClaim, WaiverPlayer, WaiverPrice
from cornerstone.parse import player_name, team_name
from cornerstone.sheet.base import Nums, fact
from cornerstone.sleeper import RawRoster, RawTransaction, RawWeek
from cornerstone.tunables import FLOOR_WEEKS, NEED_SHARE

# Sleeper marks a claim that won as complete and a claim that lost as failed.
CLAIM_RESULTS = {"complete": True, "failed": False}


def bid_history(root: Path, raw: RawWeek, week: int) -> list[WaiverClaim]:
    """Every waiver claim of weeks 1 to `week`: the saved history before `week`, and the raw files of `week`."""
    positions = {pid: entry.get("position") for pid, entry in raw.players.items()}
    claims = []
    for past in range(1, week):
        path = history_week_dir(root, past) / "transactions.json"
        # A week that is not saved has no claims, so a gap lowers the floor and never makes a claim wrong.
        if path.exists():
            claims += _claims([RawTransaction.model_validate(t) for t in json.loads(path.read_text())], positions)
    return claims + _claims(raw.transactions, positions)


def _claims(transactions: list[RawTransaction], positions: dict[str, str | None]) -> list[WaiverClaim]:
    return [
        WaiverClaim(
            player_id=player_id,
            roster_id=roster_id,
            position=positions.get(player_id),
            week=t.leg,
            # A claim with no bid set is a $0 claim.
            bid=(t.settings.waiver_bid if t.settings else None) or 0,
            won=CLAIM_RESULTS[t.status],
        )
        for t in transactions
        if t.type == "waiver" and t.status in CLAIM_RESULTS
        for player_id, roster_id in (t.adds or {}).items()
    ]


class Rival(NamedTuple):
    """One roster of the league as a bidder: its team name, its budget left, and its healthy players by position."""
    roster_id: int
    team: str
    budget_left: int
    healthy: Counter


class ExpectedBid(NamedTuple):
    """The bid the model expects from one rival on one player."""
    rival: Rival
    need: bool
    amount: float


def price_players(
    players: list[WaiverPlayer], raw: RawWeek, claims: list[WaiverClaim], week: int,
) -> list[WaiverPlayer]:
    """Each player of `players` with his price after week `week`. A rival is every roster, the viewer's too."""
    rivals = _rivals(raw)
    teams = {r.roster_id: r.team for r in rivals}
    # Only the dedicated slots count. A FLEX slot takes any of several positions, so no one position needs it.
    slots = Counter(raw.league.roster_positions)
    return [
        p.model_copy(update={"price": _price(p, rivals, slots[p.position], week,
                                             _last_like(p.position, claims, raw.players, teams))})
        for p in players
    ]


def _price(player: WaiverPlayer, rivals: list[Rival], slots: int, week: int, last_like: LastLike | None) -> WaiverPrice:
    top = max((_expected_bid(r, player, slots) for r in rivals), key=lambda b: b.amount)
    # The last like him is the most recent win at the position. Only a win in weeks N-2 to N sets the floor.
    past = last_like.bid if last_like is not None and last_like.week > week - FLOOR_WEEKS else None
    ceiling = max(r.budget_left for r in rivals)
    # The smallest whole dollar above the top expected bid, and above the recent win at the position.
    floor = max(math.floor(top.amount), past if past is not None else 0) + 1
    bid = min(floor, ceiling)
    n = Nums()
    text = (f"Bid ${n(bid)} to win {player.name}. The top rival bid is about ${n(top.amount)}, "
            f"from {top.rival.team} with ${n(top.rival.budget_left)} left")
    text += f" and a need at {player.position}." if top.need else "."
    if past is not None:
        text += f" The last winning {player.position} claim in the last {n(FLOOR_WEEKS)} weeks is ${n(past)}."
    if bid < floor:
        text += f" No rival has more than ${n(ceiling)} left."
    return WaiverPrice(bid=bid, fact=fact(f"waiver_price_{player.player_id}", text, n, [top.rival.team], [player.name]),
                       last_like=last_like, outbid=_outbid(bid, [r.budget_left for r in rivals]))


def _outbid(bid: int, budgets: list[int]) -> dict[int, int]:
    """Per budget level, the count of rivals with more budget left than a viewer at that level can bid.

    A viewer can bid the bid to win, or his whole budget left when it is less. A viewer with more than the bid
    is in the count of budgets above the bid, so his own roster comes off.
    """
    return {level: sum(b > min(bid, level) for b in budgets) - (level > bid) for level in sorted(set(budgets))}


def _last_like(
    position: str, claims: list[WaiverClaim], players: dict[str, dict], teams: dict[int, str]
) -> LastLike | None:
    """The latest winning claim at `position`. Inside one week the higher bid, then the player ID, breaks the tie.

    The match is on position alone, because a past claim has no bucket tier.
    """
    won = [c for c in claims if c.won and c.position == position]
    if not won:
        return None
    last = max(won, key=lambda c: (c.week, c.bid, c.player_id))
    return LastLike(player_id=last.player_id, name=player_name(last.player_id, players.get(last.player_id)),
                    roster_id=last.roster_id, team=teams.get(last.roster_id, ""), week=last.week, bid=last.bid)


def _expected_bid(rival: Rival, player: WaiverPlayer, slots: int) -> ExpectedBid:
    need = rival.healthy[player.position] < slots
    share = NEED_SHARE["need" if need else "covered"]
    # The share and the board score are each at most 1, so the bid never exceeds the budget left.
    return ExpectedBid(rival=rival, need=need, amount=rival.budget_left * share * player.board_score)


def budget_left(raw: RawWeek, roster: RawRoster) -> int:
    """The league budget minus the budget the roster used."""
    return raw.league.settings.waiver_budget - roster.settings.waiver_budget_used


def _rivals(raw: RawWeek) -> list[Rival]:
    users = {u.user_id: u for u in raw.users}
    rivals = []
    for roster in sorted(raw.rosters, key=lambda r: r.roster_id):
        # A roster with no players has None in rosters.json.
        entries = [raw.players.get(pid) or {} for pid in roster.players or []]
        healthy = Counter(e.get("position") for e in entries if e.get("injury_status") not in OUT_STATUSES)
        rivals.append(Rival(roster_id=roster.roster_id, team=team_name(users[roster.owner_id]),
                            budget_left=budget_left(raw, roster), healthy=healthy))
    return rivals
