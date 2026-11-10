"""
The fact sheet of a proposed trade: per traded player the stats and the trade value, per side the need and the
roster fit reads. Every player stat ends at the known games and every record at week N-1.
Each fact carries every number in its text.
It reads the snapshot and a proposed trade, not the weekly bundle, so it is not a chapter.
"""
from analyzer.chart_facts import chart_facts
from analyzer.measures import Side, hole_sentence, trade_handcuffs
from analyzer.nfl_team_facts import nfl_team_facts
from analyzer.trade import ProposedTrade, build_sides
from analyzer.tunables import RECENT_RANK_GAP
from analyzer.week_line import WeekLine, week_lines
from facts.tokens import Nums, fact
from league.history import points_per_game, red_zone, season_rank, snap_share, target_share
from league.lineup import FLEX_SLOTS, STRENGTH_SLOTS, StartingSlot, allowed_positions
from league.models import Fact, UsageShare
from league.numbers import plural
from league.ranks import RANKED_POSITIONS, recent_rank
from league.snapshot import Snapshot
from league.tunables import LINEUP_WEEKS


def shown_ranks(snapshot: Snapshot, pid: str) -> tuple[str | None, str | None]:
    """The ranks the text of a grade shows for a player: his Season rank, such as WR60, and his Recent rank.

    The Recent rank is None unless it differs from the Season rank by RECENT_RANK_GAP spots or more.
    The Season rank is None when the stats of the season are not complete. GLOSSARY.md, "Season rank", "Recent rank".
    """
    position = snapshot.players[pid].position
    season = season_rank(snapshot.stats, pid, snapshot.as_of.stats_through)
    if season is None:
        return None, None
    recent = recent_rank(snapshot, pid)
    shown = f"{position}{recent}" if recent is not None and abs(season[0] - recent) >= RECENT_RANK_GAP else None
    return f"{position}{season[0]}", shown


def _ppg_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The points per game of a traded player, through the player stat bound only, his Season rank, and his Recent
    rank when the gap holds. No Position rank number: the text shows the rank that Sleeper shows."""
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
                f"{plural(profile[1], 'game', 'games')} before the trade.")
    # The rank strings go through Nums, so the analysis checker accepts "WR60" and "WR18" in the prose.
    season, recent = shown_ranks(snapshot, pid)
    if season is not None:
        text += f" His Season rank is {n.text(season)}, by total points this season."
    if recent is not None:
        text += f" His Recent rank is {n.text(recent)}, by points per game over the last {n(LINEUP_WEEKS)} weeks."
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


def _depth_fact(snapshot: Snapshot, side: Side, position: str) -> Fact | None:
    """The depth of a side at a position before and after the trade, or None when the count does not change."""
    before, after = side.depth(snapshot, position)
    if before == after:
        return None
    n = Nums()
    team = snapshot.teams[side.roster_id].name
    # The line reads as a plain rank, as the roster row says it, so the fact holds no inner word of decision 03.
    line = snapshot.client.settings.lines[position]
    text = f"For {team}, the {position}s in the top {n(line)} go from {n(before)} to {n(after)}."
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
    text = (f"For {team}, the starters at {slots} with a position rank of {n(snapshot.client.settings.strength_rank)} or better "
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


def _week_line_fact(snapshot: Snapshot, rid: int, lines: list[WeekLine], players: list[str]) -> Fact:
    """The Week lines of a side for the trade week and the next week, so the Case and the Bullets can name them.
    `players` are the names of the players the side gets, whose opponents the lines name.

    The code writes the text, and the fact records each number in it: the weeks, the counts, the top N, and the ranks.
    """
    n = Nums()
    text = n.text(" ".join(line.text for line in lines))
    return fact(f"{rid}.week_line", text, n, [snapshot.teams[rid].name], players)


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
    trade value, and per side the roster need, the Week line, each
    new hole with the best free agent at its position, the depth at each position whose count changes, and the
    strength when its count changes.
    Every player stat ends at the known games. The team facts of team_facts.py hold the record and the race group."""
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
    facts += [*nfl_team_facts(trade, snapshot), *chart_facts(trade, snapshot)]
    lines = week_lines(trade, snapshot)
    for side in trade.sides:
        facts.append(_need_fact(snapshot, trade, side.roster_id))
    # The Week line facts follow the need facts, one for each side.
    for side in trade.sides:
        gets = [snapshot.players[pid].name for pid in trade.gets(side.roster_id)]
        facts.append(_week_line_fact(snapshot, side.roster_id, lines[side.roster_id], gets))
    # The sides come from build_sides, so the hole facts name the slots the roster fit Measure reads.
    # No fact names the slot a player takes: the best lineup is a measure of depth, not the lineup a manager sets.
    for graded in build_sides(trade, snapshot, trade_handcuffs(trade, snapshot)):
        facts += [_hole_fact(snapshot, graded, slot) for slot in graded.new_holes(snapshot)]
        facts += [_depth_fact(snapshot, graded, position) for position in RANKED_POSITIONS]
        facts.append(_strength_fact(snapshot, graded))
    return {f.id: f for f in facts if f is not None}
