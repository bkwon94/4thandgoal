"""
The waiver chapter of Act II: the top waiver hits by Points over the line, the top misses by the dollars spent, the
top outbid claims, and the streaming king data. It reads the transactions of each week that the app fetched again.
"""
from collections.abc import Mapping, Sequence

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Fact, History
from league.provider.raw import RawTransaction
from midseason.moves import PlayerInfo, line_scores, stint

# Decision ticket 03. The hits list reads these positions. QB, K, and DEF adds feed the streaming king.
HIT_POSITIONS = ("RB", "WR", "TE")
STREAM_POSITIONS = ("QB", "K", "DEF")
HIT_COUNT = 5
MISS_COUNT = 5
OUTBID_COUNT = 3
# A miss cost this share of the FAAB budget or more.
MISS_BUDGET_SHARE = 0.10
# A miss gave back this count of starts or fewer, or Points over the line below zero.
MISS_MAX_STARTS = 1
# The note of a failed claim that another roster won. Sleeper gives other notes for a roster too full to add.
LOST_NOTE = "claimed by another owner"


class Pickup(BaseModel):
    """One stint of an added player on the roster that added him: a waiver claim or a free agent add."""
    player_id: str
    player: str
    position: str
    roster_id: int
    team: str
    # The week of the add, the leg of the transaction.
    week: int
    # 0 for a free agent add, which has no bid.
    bid: int
    starts: int
    points: float
    # None for a position with no line.
    points_over_line: float | None
    swung_wins: int
    # False when the player sat on the roster in no week of the report, so no game came after the add.
    played: bool


class Outbid(BaseModel):
    """A lost claim on a player who became a top waiver hit, with the margin of the lost bid."""
    player_id: str
    player: str
    roster_id: int
    team: str
    bid: int
    winner_roster_id: int
    winner: str
    winner_bid: int
    margin: int
    winner_points_over_line: float


class Streamer(BaseModel):
    """The streamed QB, K, and DEF adds of one team that it started."""
    roster_id: int
    team: str
    players: int
    starts: int
    points: float


class WaiverFacts(BaseModel):
    """The facts of the waiver chapter."""
    hits: list[Pickup]
    misses: list[Pickup]
    outbid: list[Outbid]
    # Each team with a started stream, most points first. The first is the streaming king.
    streamers: list[Streamer]


def _when(transaction: RawTransaction) -> int:
    """The time of the waiver run of a claim, or the time of the add. Sleeper gives both in milliseconds."""
    extra = transaction.model_extra or {}
    return int(extra.get("status_updated") or transaction.created)


def _note(transaction: RawTransaction) -> str:
    metadata = (transaction.model_extra or {}).get("metadata") or {}
    return str(metadata.get("notes") or "")


def _bid(transaction: RawTransaction) -> int:
    return (transaction.settings.waiver_bid if transaction.settings else None) or 0


def _adds(transactions: Mapping[int, Sequence[RawTransaction]]) -> list[RawTransaction]:
    """The complete waiver claims and free agent adds, oldest first."""
    rows = [t for week in transactions.values() for t in week
            if t.status == "complete" and t.type in ("waiver", "free_agent") and t.adds]
    return sorted(rows, key=_when)


def waiver_facts(
    history: History, through: int, transactions: Mapping[int, Sequence[RawTransaction]],
    players: Mapping[str, PlayerInfo], names: Mapping[int, str], lines: Mapping[str, int], budget: int,
) -> WaiverFacts:
    """The waiver facts of weeks 1 to `through` from the transactions of each week by week.

    Each add is its own stint, so a player added twice is two pickups. A stint ends at the next add of the same
    player by the same roster, or when he leaves the roster.
    """
    line_at = line_scores(history, lines, through)
    adds = _adds(transactions)
    pickups: list[Pickup] = []
    for index, row in enumerate(adds):
        for player_id, roster_id in (row.adds or {}).items():
            info = players.get(player_id)
            if info is None:
                continue
            again = next((later.leg for later in adds[index + 1:]
                          if (later.adds or {}).get(player_id) == roster_id), None)
            last = through if again is None else min(through, again - 1)
            run = stint(history, line_at, player_id, info.position, roster_id, row.leg, last)
            pickups.append(Pickup(
                player_id=player_id, player=info.name, position=info.position, roster_id=roster_id,
                team=names[roster_id], week=row.leg, bid=_bid(row) if row.type == "waiver" else 0,
                starts=run.starts, points=run.points, points_over_line=run.points_over_line,
                swung_wins=run.swung_wins, played=bool(run.weeks)))

    hits = sorted((p for p in pickups if p.position in HIT_POSITIONS and p.starts and (p.points_over_line or 0) > 0),
                  key=lambda p: (-(p.points_over_line or 0), -p.bid, p.player))[:HIT_COUNT]
    misses = sorted((p for p in pickups if _is_miss(p, budget)),
                    key=lambda p: (-p.bid, p.points_over_line or 0, p.player))[:MISS_COUNT]
    return WaiverFacts(hits=hits, misses=misses, outbid=_outbid(transactions, hits, names),
                       streamers=_streamers(pickups))


def _is_miss(pickup: Pickup, budget: int) -> bool:
    """A miss cost 10% of the budget or more, and gave back 1 start or fewer, or Points over the line below zero.
    A $0 add is never a miss, and an add with no game after it is never a miss."""
    if pickup.bid <= 0 or pickup.bid < MISS_BUDGET_SHARE * budget or not pickup.played:
        return False
    return pickup.starts <= MISS_MAX_STARTS or (pickup.points_over_line is not None and pickup.points_over_line < 0)


def _outbid(
    transactions: Mapping[int, Sequence[RawTransaction]], hits: Sequence[Pickup], names: Mapping[int, str],
) -> list[Outbid]:
    """The lost claims on the players of the top hits. A lost claim pairs with the won claim of the same player in the
    same waiver run, by the time of the run and not the leg."""
    rows = [t for week in transactions.values() for t in week if t.type == "waiver"]
    out: list[tuple[int, Outbid]] = []
    for place, hit in enumerate(hits):
        won = [t for t in rows if t.status == "complete" and (t.adds or {}).get(hit.player_id) == hit.roster_id
               and t.leg == hit.week]
        for claim in won:
            for lost in rows:
                if (lost.status != "failed" or LOST_NOTE not in _note(lost) or hit.player_id not in (lost.adds or {})
                        or _when(lost) != _when(claim)):
                    continue
                roster_id = lost.adds[hit.player_id] if lost.adds else lost.roster_ids[0]
                out.append((place, Outbid(
                    player_id=hit.player_id, player=hit.player, roster_id=roster_id, team=names[roster_id],
                    bid=_bid(lost), winner_roster_id=hit.roster_id, winner=hit.team, winner_bid=_bid(claim),
                    margin=_bid(claim) - _bid(lost), winner_points_over_line=hit.points_over_line or 0.0)))
    out.sort(key=lambda pair: (pair[0], pair[1].margin, pair[1].team))
    return [outbid for _, outbid in out[:OUTBID_COUNT]]


def _streamers(pickups: Sequence[Pickup]) -> list[Streamer]:
    by_team: dict[int, list[Pickup]] = {}
    for pickup in pickups:
        if pickup.position in STREAM_POSITIONS and pickup.starts:
            by_team.setdefault(pickup.roster_id, []).append(pickup)
    streamers = [
        Streamer(roster_id=rid, team=group[0].team, players=len({p.player_id for p in group}),
                 starts=sum(p.starts for p in group), points=round(sum(p.points for p in group), 2))
        for rid, group in by_team.items()
    ]
    return sorted(streamers, key=lambda s: (-s.points, s.team))


def waiver_prose_facts(facts: WaiverFacts) -> list[Fact]:
    """The facts that the waiver prose block cites: each hit, each miss, each outbid claim, and the streaming king."""
    out = []
    # Each move is a few facts, so each fact holds two numbers at most, as a sentence of the writer may.
    for place, hit in enumerate(facts.hits, start=1):
        n = Nums()
        out.append(fact(f"WV.hit.{place}", f"{hit.player} went to {hit.team} for ${n(hit.bid)} in week {n(hit.week)}.",
                        n, [hit.team], [hit.player]))
        n = Nums()
        out.append(fact(f"WV.hit.{place}.value",
                        f"{hit.player} has {n(hit.points_over_line or 0.0)} points over the line in {n(hit.starts)} "
                        f"starts for {hit.team}.", n, [hit.team], [hit.player]))
        n = Nums()
        wins = "win" if hit.swung_wins == 1 else "wins"
        out.append(fact(f"WV.hit.{place}.rank",
                        f"{hit.player} swung {n(hit.swung_wins)} {wins} for {hit.team}, the {n.ord(place)} waiver hit "
                        f"of the league.", n, [hit.team], [hit.player]))
    for place, miss in enumerate(facts.misses, start=1):
        n = Nums()
        out.append(fact(f"WV.miss.{place}", f"{miss.team} paid ${n(miss.bid)} for {miss.player} in week {n(miss.week)}.",
                        n, [miss.team], [miss.player]))
        n = Nums()
        out.append(fact(f"WV.miss.{place}.value",
                        f"{miss.player} got {n(miss.starts)} starts and {n(miss.points_over_line or 0.0)} points over "
                        f"the line for {miss.team}.", n, [miss.team], [miss.player]))
        n = Nums()
        out.append(fact(f"WV.miss.{place}.rank",
                        f"The ${n(miss.bid)} of {miss.team} for {miss.player} is the {n.ord(place)} waiver miss of "
                        f"the league.", n, [miss.team], [miss.player]))
    for place, lost in enumerate(facts.outbid, start=1):
        n = Nums()
        out.append(fact(f"WV.outbid.{place}",
                        f"{lost.team} bid ${n(lost.bid)} on {lost.player} and lost to the ${n(lost.winner_bid)} bid of "
                        f"{lost.winner}.", n, [lost.team, lost.winner], [lost.player]))
        n = Nums()
        out.append(fact(f"WV.outbid.{place}.margin", f"{lost.team} lost {lost.player} to {lost.winner} by "
                        f"${n(lost.margin)}.", n, [lost.team, lost.winner], [lost.player]))
    if facts.streamers:
        king = facts.streamers[0]
        n = Nums()
        out.append(fact(
            "WV.stream",
            f"{king.team} started streamed QBs, kickers, and defenses {n(king.starts)} times for {n(king.points)} "
            f"points, the most in the league.", n, [king.team], []))
    return out
