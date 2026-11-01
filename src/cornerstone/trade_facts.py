"""
The fact sheet of a proposed trade: per traded player the grade inputs and the trade value, per side the team, the
need, and the roster fit reads. Every player stat ends at the known games and every record at week N-1.
Each fact carries every number in its text.
It reads the snapshot and a proposed trade, not the weekly bundle, so it is not a chapter.
"""
from cornerstone.adjusters import (
    FLEX_SLOTS, STRENGTH_SLOTS, Side, StartingSlot, allowed_positions, due_back_week, hole_sentence, team_race,
    trade_handcuffs,
)
from cornerstone.history import points_per_game, red_zone, season_rank, snap_share, target_share
from cornerstone.models import Fact, UsageShare
from cornerstone.numbers import plural
from cornerstone.ranks import RANKED_POSITIONS
from cornerstone.rubric import ProposedTrade, build_sides
from cornerstone.sheet.base import Nums, fact
from cornerstone.snapshot import Snapshot

_RACE_TEXT = {
    "contender": "a contender in a playoff spot",
    "seller": "a seller out of the playoff race",
    "middle": "a middle team, neither in a playoff spot nor out of the race",
}


def _ppg_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The points per game and the season rank of a traded player, through the player stat bound only, and his
    position rank by lineup value. GLOSSARY.md, "Position rank"."""
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
                f"{plural(profile[1], 'game', 'games')} before the trade")
        rank = season_rank(snapshot.stats, pid, through)
        if rank is not None:
            # "Position rank" is the league rank by lineup value, so this rank by season points has its own words.
            text += f", season rank {n(rank[0])} of {n(rank[1])} by season points"
        text += "."
    # The position rank is a league rank by lineup value, so the analysis can say "RB15" and the reader can check it.
    # The number goes through Nums, so the analysis checker accepts the rank in the prose.
    rank = snapshot.position_rank(pid)
    if rank is not None:
        by = ("his projection ahead" if snapshot.projections_ahead is not None and due_back_week(snapshot, pid)
              is not None else "points per game")
        text += f" {player.name} is {player.position}{n(rank)} by {by}."
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
                f"{plural(share.weeks, 'game', 'games')} before the trade.")
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
    text = (f"{name} had {n(targets)} red-zone {plural(targets, 'target', 'targets')} and {n(carries)} "
            f"red-zone {plural(carries, 'carry', 'carries')} this season before the trade.")
    return fact(f"{pid}.redzone", text, n, [], [name])


def _report_weeks(snapshot: Snapshot, pid: str) -> int | None:
    """The count of weeks before the trade with the player on the NFL injury report, or None with no report or id."""
    if snapshot.injuries is None or snapshot.id_map is None or pid not in snapshot.id_map:
        return None
    weeks = snapshot.injuries.get(snapshot.id_map[pid], {})
    return sum(1 for week in weeks if week <= snapshot.as_of.completed_through)


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
        text += (f" He was on the NFL injury report in {n(weeks)} {plural(weeks, 'week', 'weeks')} "
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
    gives = next(s.player_ids for s in trade.sides if s.roster_id == rid)
    gets = trade.gets(rid)
    after = [pid for pid in snapshot.rosters[rid] if pid not in gives] + gets
    traded = trade.player_ids
    positions = sorted({snapshot.players[pid].position for pid in traded})
    depth = [f"{n(sum(snapshot.players[pid].position == pos for pid in after if pid in snapshot.players))} {pos}"
             for pos in positions]
    spots = max(0, len(snapshot.roster_positions) - len(after))
    joined = depth[0] if len(depth) == 1 else ", ".join(depth[:-1]) + " and " + depth[-1]
    text = f"{team} has {joined} after the trade and {n(spots)} open roster {plural(spots, 'spot', 'spots')}."
    return fact(f"{rid}.need", text, n, [team], [])


def _slot_fact(snapshot: Snapshot, side: Side, pid: str) -> Fact:
    """The starting slot a player the side gets takes after the trade, and the player who held it before.

    The holder before moves to another slot, sits on the bench, or leaves in the trade. A player in no slot sits on the
    bench. The slot names carry digits, such as RB2, so they go through Nums and the checker accepts them in prose.
    """
    n = Nums()
    name = snapshot.players[pid].name
    taken = next((slot for slot in side.slots_after if slot.player == pid), None)
    if taken is None:
        return fact(f"{pid}.slot", f"{name} sits on the bench.", n, [], [name])
    held = next(slot.player for slot in side.slots_before if slot.name == taken.name)
    text = f"{name} takes {n.text(taken.name)}"
    if held is None:
        text += ", which was empty before the trade."
    elif held in side.gives:
        text += f", which {snapshot.players[held].name} held before the trade."
    else:
        # The holder can move up as well as down, as when the side gives its WR1, so a move says "moves to".
        moved = next((slot.name for slot in side.slots_after if slot.player == held), None)
        held_name = snapshot.players[held].name
        text += (f" and pushes {held_name} to the bench." if moved is None
                 else f", and {held_name} moves to {n.text(moved)}.")
    players = [name] if held is None else [name, snapshot.players[held].name]
    return fact(f"{pid}.slot", text, n, [], players)


def _depth_fact(snapshot: Snapshot, side: Side, position: str) -> Fact | None:
    """The depth of a side at a position before and after the trade, or None when the count does not change."""
    before, after = side.depth(snapshot, position)
    if before == after:
        return None
    n = Nums()
    team = snapshot.teams[side.roster_id].name
    text = f"For {team}, {position} depth above the line goes from {n(before)} to {n(after)}."
    return fact(f"{side.roster_id}.depth.{position.lower()}", text, n, [team], [])


def _strength_fact(snapshot: Snapshot, side: Side) -> Fact | None:
    """The strength of a side before and after the trade, or None when the count does not change.

    "Top 24" carries no hyphen, because the number rule reads "-24" as a negative number.
    """
    before, after = side.strength(snapshot)
    if before == after:
        return None
    n = Nums()
    team = snapshot.teams[side.roster_id].name
    slots = n.text(", ".join(STRENGTH_SLOTS[:-1]) + f", and {STRENGTH_SLOTS[-1]}")
    text = (f"For {team}, the starters at {slots} with a position rank of {n(snapshot.config.strength_rank)} or better "
            f"go from {n(before)} to {n(after)}.")
    return fact(f"{side.roster_id}.strength", text, n, [team], [])


def _hole_fact(snapshot: Snapshot, side: Side, slot: StartingSlot) -> Fact:
    """A new hole of a side: the hole sentence of the fit reason, the player the trade took from a slot of its kind,
    and the best free agent at the hole's position with his position rank. GLOSSARY.md, "Hole".

    The player who left tells the reader what the trade cost. He is the player the side gives who held a slot of the
    same roster slot before the trade, and the one who held the hole's own slot comes first. With none, no sentence.
    The free agent tells the reader whether waivers fix the hole. He feeds this fact only, never the step.
    A FLEX hole reads the position of the player who holds it. An empty FLEX hole reads every position the slot allows.
    """
    n = Nums()
    team = snapshot.teams[side.roster_id].name
    if slot.player is not None and slot.roster_slot in FLEX_SLOTS:
        positions = [snapshot.players[slot.player].position]
    else:
        positions = [position for position in RANKED_POSITIONS if position in allowed_positions(slot.roster_slot)]
    where = positions[0] if len(positions) == 1 else ", ".join(positions[:-1]) + f", or {positions[-1]}"
    # The hole sentence carries the slot, the week, and the rank as digits, so Nums records each one.
    text = f"For {team}, {n.text(hole_sentence(snapshot, slot))}"
    players = [] if slot.player is None else [snapshot.players[slot.player].name]
    left = sorted((before for before in side.slots_before
                   if before.player in side.gives and before.roster_slot == slot.roster_slot),
                  key=lambda before: before.name != slot.name)
    if left:
        name = snapshot.players[left[0].player].name
        text += f" {name} held {n.text(left[0].name)} before the trade."
        players.append(name)
    best = snapshot.best_free_agent(positions)
    if best is None:
        text += f" No free agent at {where} has a position rank."
    else:
        player, rank = best
        text += f" The best free agent at {where} is {player.name}, {player.position}{n(rank)}."
        players.append(player.name)
    return fact(f"{side.roster_id}.hole.{slot.name.lower()}", text, n, [team], players)


def _week_fact(snapshot: Snapshot) -> Fact:
    n = Nums()
    as_of = snapshot.as_of
    text = f"The trade is in week {n(snapshot.week)} of the {n(snapshot.season)} season. "
    # On a game day the player stats read the known games of week N, but the record ends at week N-1.
    if as_of.stats_through > as_of.completed_through:
        text += (f"Player stats run through the known games of week {n(as_of.stats_through)}. "
                 f"The record runs through week {n(as_of.completed_through)}.")
    else:
        text += f"Every stat runs through week {n(as_of.stats_through)}."
    return fact("trade.week", text, n, [], [])


def trade_fact_sheet(trade: ProposedTrade, snapshot: Snapshot) -> dict[str, Fact]:
    """The facts of a proposed trade by ID: per traded player the points per game, rank, usage, injury, and
    trade value, and per side the team record and race, the roster need, the slot each player it gets takes, each
    new hole with the best free agent at its position, the depth at each position whose count changes, and the
    strength when its count changes.
    Every player stat ends at the known games, and the record and the race end at week N-1."""
    facts = [_week_fact(snapshot)]
    through = snapshot.as_of.stats_through
    for side in trade.sides:
        for pid in side.player_ids:
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
    # The sides come from the grade's own call, so the slot facts name the slots the roster fit step reads.
    for graded in build_sides(trade, snapshot, trade_handcuffs(trade, snapshot)):
        facts += [_slot_fact(snapshot, graded, pid) for pid in graded.gets]
        facts += [_hole_fact(snapshot, graded, slot) for slot in graded.new_holes(snapshot)]
        facts += [_depth_fact(snapshot, graded, position) for position in RANKED_POSITIONS]
        facts.append(_strength_fact(snapshot, graded))
    return {f.id: f for f in facts if f is not None}
