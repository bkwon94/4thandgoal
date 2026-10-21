"""
The fact sheet of a proposed trade: per traded player the grade inputs and the trade value, per side the team and need.
Every number ends at week N-1, and each fact carries every number in its text, as the weekly fact sheet does.
"""
from cornerstone.adjusters import team_race
from cornerstone.history import points_per_game, red_zone, season_rank, snap_share, target_share
from cornerstone.models import Fact, UsageShare
from cornerstone.rubric import ProposedTrade
from cornerstone.sheet import Nums, fact
from cornerstone.snapshot import Snapshot

_RACE_TEXT = {
    "contender": "a contender in a playoff spot",
    "seller": "a seller out of the playoff race",
    "middle": "a middle team, neither in a playoff spot nor out of the race",
}


def _plural(count: int, one: str, many: str) -> str:
    return one if count == 1 else many


def _ppg_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The points per game and the position rank of a traded player, from weeks 1 to N-1 only."""
    n = Nums()
    player = snapshot.players[pid]
    through = snapshot.as_of.stats_through
    who = f"{player.name} ({player.position}, {player.nfl_team})" if player.nfl_team else player.name
    profile = points_per_game(snapshot.stats, pid, through)
    if profile is None:
        text = f"{who} has no stats before the trade."
    elif profile[1] == 0:
        text = f"{who} has no scored game before the trade."
    else:
        text = (f"{who} scored {n(profile[0])} points per game over {n(profile[1])} "
                f"{_plural(profile[1], 'game', 'games')} before the trade")
        rank = season_rank(snapshot.stats, pid, through)
        if rank is not None:
            text += f", position rank {n(rank[0])} of {n(rank[1])} by season points"
        text += "."
    return fact(f"{pid}.ppg", text, n, [], [player.name])


def _share_fact(snapshot: Snapshot, pid: str, kind: str, share: UsageShare | None) -> Fact | None:
    """The snap share or the target share of a player before the trade. `kind` is the fact ID suffix."""
    if share is None:
        return None
    n = Nums()
    name = snapshot.players[pid].name
    label = "snap share" if kind == "usage" else "target share"
    if share.direction is None:
        text = (f"{name}'s {label} was {n(share.percent)} percent over {n(share.weeks)} "
                f"{_plural(share.weeks, 'game', 'games')} before the trade.")
    else:
        text = (f"{name}'s {label} was {n(share.percent)} percent over the last {n(share.weeks)} weeks before "
                f"the trade, {share.direction} from the {n(share.weeks)} weeks before that.")
    return fact(f"{pid}.{kind}", text, n, [], [name])


def _redzone_fact(snapshot: Snapshot, pid: str) -> Fact | None:
    zone = red_zone(snapshot.stats, pid, snapshot.as_of.stats_through)
    if zone is None:
        return None
    n = Nums()
    name = snapshot.players[pid].name
    targets, carries = zone
    text = (f"{name} had {n(targets)} red-zone {_plural(targets, 'target', 'targets')} and {n(carries)} "
            f"red-zone {_plural(carries, 'carry', 'carries')} this season before the trade.")
    return fact(f"{pid}.redzone", text, n, [], [name])


def _report_weeks(snapshot: Snapshot, pid: str) -> int | None:
    """The count of weeks before the trade with the player on the NFL injury report, or None with no report or id."""
    if snapshot.injuries is None or snapshot.id_map is None or pid not in snapshot.id_map:
        return None
    weeks = snapshot.injuries.get(snapshot.id_map[pid], {})
    return sum(1 for week in weeks if week <= snapshot.as_of.stats_through)


def _injury_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The injury status now, the return week on file, and the count of injury report weeks before the trade."""
    n = Nums()
    player = snapshot.players[pid]
    back = snapshot.returns.get(pid)
    if player.injury_status is None:
        text = f"{player.name} has no injury status now"
    else:
        text = f"{player.name} is listed {player.injury_status} now"
    if back is not None:
        text += f", and his return week on file is week {n(back)}."
    elif player.injury_status is not None:
        text += ", with no return week on file."
    else:
        text += "."
    weeks = _report_weeks(snapshot, pid)
    if weeks:
        text += (f" He was on the NFL injury report in {n(weeks)} {_plural(weeks, 'week', 'weeks')} "
                 "this season before the trade.")
    return fact(f"{pid}.injury", text, n, [], [player.name])


def _trade_value_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The trade value of a traded player. The model reads it, and the number check keeps it out of the prose."""
    n = Nums()
    name = snapshot.players[pid].name
    if pid in snapshot.chart.values:
        text = f"{name}'s trade value is {n(snapshot.chart.values[pid])} in the week of the trade."
    else:
        text = f"{name} has no trade value in the week of the trade."
    return fact(f"{pid}.value", text, n, [], [name])


def _team_fact(snapshot: Snapshot, rid: int) -> Fact:
    """The record, the rank, and the race of a roster before the trade."""
    n = Nums()
    team = snapshot.teams[rid].name
    standing = next(s for s in snapshot.standings if s.roster_id == rid)
    text = (f"{team} was {n.record(standing.wins, standing.losses)}, {n.ord(standing.rank)} of "
            f"{n(len(snapshot.standings))}, before the trade: {_RACE_TEXT[team_race(snapshot, rid)]}.")
    return fact(f"{rid}.team", text, n, [team], [])


def _need_fact(snapshot: Snapshot, trade: ProposedTrade, rid: int) -> Fact:
    """The depth of a roster after the trade at each position the trade touches, and its open roster spots."""
    n = Nums()
    team = snapshot.teams[rid].name
    gives = next(s.gives for s in trade.sides if s.roster_id == rid)
    gets = next(s.gives for s in trade.sides if s.roster_id != rid)
    after = [pid for pid in snapshot.rosters[rid] if pid not in gives] + gets
    traded = [pid for side in trade.sides for pid in side.gives]
    positions = sorted({snapshot.players[pid].position for pid in traded})
    depth = [f"{n(sum(snapshot.players[pid].position == pos for pid in after if pid in snapshot.players))} {pos}"
             for pos in positions]
    spots = max(0, len(snapshot.roster_positions) - len(after))
    joined = depth[0] if len(depth) == 1 else ", ".join(depth[:-1]) + " and " + depth[-1]
    text = f"{team} has {joined} after the trade and {n(spots)} open roster {_plural(spots, 'spot', 'spots')}."
    return fact(f"{rid}.need", text, n, [team], [])


def _week_fact(snapshot: Snapshot) -> Fact:
    n = Nums()
    text = (f"The trade is in week {n(snapshot.week)} of the {n(snapshot.season)} season. "
            f"Every stat runs through week {n(snapshot.as_of.stats_through)}.")
    return fact("trade.week", text, n, [], [])


def trade_fact_sheet(trade: ProposedTrade, snapshot: Snapshot) -> dict[str, Fact]:
    """The facts of a proposed trade by ID: per traded player the points per game, rank, usage, injury, and
    trade value, and per side the team record and race and the roster need. Every number ends at week N-1."""
    facts = [_week_fact(snapshot)]
    through = snapshot.as_of.stats_through
    for side in trade.sides:
        for pid in side.gives:
            position = snapshot.players[pid].position
            facts.append(_ppg_fact(snapshot, pid))
            facts.append(_share_fact(snapshot, pid, "usage", snap_share(snapshot.stats, pid, through)))
            if position in ("RB", "WR", "TE"):
                facts.append(_share_fact(snapshot, pid, "targets", target_share(snapshot.stats, pid, through)))
            if position in ("QB", "RB", "WR", "TE"):
                facts.append(_redzone_fact(snapshot, pid))
            facts.append(_injury_fact(snapshot, pid))
            if snapshot.chart is not None:
                facts.append(_trade_value_fact(snapshot, pid))
    for side in trade.sides:
        facts.append(_team_fact(snapshot, side.roster_id))
        facts.append(_need_fact(snapshot, trade, side.roster_id))
    return {f.id: f for f in facts if f is not None}
