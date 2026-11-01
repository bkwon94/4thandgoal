"""
Builds the trade facts and the inputs to the trade grade.
Each trade gets its own facts, so a trade chapter cites only its own trade.
"""
# The weekly assembly does not call this module, so it has no facts function and is not in CHAPTER_FACTS.
# Only the trade bundle in the tests calls it. Ticket 19 decides whether it joins the assembly or goes.
from decimal import Decimal

from cornerstone.facts_league import (
    season_records,
)
from cornerstone.history import (
    player_trend,
    points_per_game,
    red_zone,
    season_rank,
    snap_share,
    target_share,
)
from cornerstone.models import (
    Fact,
    Trade,
    UsageShare,
)
from cornerstone.numbers import r2
from cornerstone.sheet.base import Context, Nums, fact, trend_text, weeks_text
from cornerstone.trades import is_late


def _join(items: list[str]) -> str:
    """A, A and B, or A, B and C."""
    if len(items) < 2:
        return "".join(items)
    return f"{', '.join(items[:-1])} and {items[-1]}"


def _got_with_lines(c: Context, trade: Trade, rid: int) -> list[str]:
    """The player IDs a roster got that have a line this week."""
    return [pid for pid in _moved(trade, rid, True) if pid in c.lines]


def _moved(trade: Trade, rid: int, got: bool) -> list[str]:
    """The player IDs a roster got or gave, in the order of `adds`."""
    if got:
        return [pid for pid, owner in trade.adds.items() if owner == rid]
    return [pid for pid in trade.adds if trade.drops.get(pid) == rid]


def _items(c: Context, trade: Trade, rid: int, got: bool, n: Nums) -> list[str]:
    """The players, then the picks, that a roster got or gave. Players keep the order of `adds`."""
    # A player with no line was on no roster at lineup lock, so the week has no points to cite for him.
    # He stays in the sides text under a plain label, and gets no got or gave fact.
    names = [c.lines[pid].name if pid in c.lines else "an unlisted player" for pid in _moved(trade, rid, got)]
    picks = [
        f"{n(int(p.season))} round {n(p.round)} pick" for p in trade.draft_picks
        if (p.owner_id if got else p.previous_owner_id) == rid
    ]
    return names + picks


def _sides_fact(c: Context, i: int, trade: Trade) -> Fact:
    n = Nums()
    ids = trade.roster_ids
    if len(ids) == 2:
        a, b = ids
        text = (
            f"{c.team(a)} traded {_join(_items(c, trade, a, False, n))} to {c.team(b)} "
            f"for {_join(_items(c, trade, a, True, n))}."
        )
    else:
        clauses = [f"{c.team(r)} got {_join(_items(c, trade, r, True, n))}" for r in ids]
        text = f"In a {n(len(ids))}-team trade, {'; '.join(clauses)}."
    players = [c.lines[pid].name for pid in trade.adds if pid in c.lines]
    return fact(f"T{i}.sides", text, n, [c.team(r) for r in ids], players)


def _player_trade_fact(c: Context, i: int, rid: int, pid: str, verb: str) -> Fact:
    """The points per game of a traded player and his position rank, from weeks 1 to N-1 only."""
    n = Nums()
    line = c.lines[pid]
    team = c.team(rid)
    through = c.week.week - 1
    # Without a history there is nothing before the trade to cite, so the fact only names the move.
    profile = points_per_game(c.history, pid, through) if c.history is not None else None
    if profile is None:
        text = f"{team} {verb} {line.name}."
    elif profile[1] == 0:
        text = f"{team} {verb} {line.name}: no scored game before the trade."
    else:
        text = (
            f"{team} {verb} {line.name}: {n(profile[0])} points per game over {n(profile[1])} "
            f"{'game' if profile[1] == 1 else 'games'} before the trade"
        )
        rank = season_rank(c.history, pid, through)
        if rank is not None:
            text += f", position rank {n(rank[0])} of {n(rank[1])} by season points"
        text += "."
    beaten = player_trend(c.history, pid, through=through) if c.history is not None else None
    if beaten is not None:
        text += " " + trend_text(line.name, beaten, n)
    return fact(f"T{i}.{rid}.{verb}.{pid}", text, n, [team], [line.name])


def _team_fact(c: Context, i: int, rid: int) -> Fact | None:
    """The record and rank of the roster before the trade. A missing or partial history gives none."""
    through = c.week.week - 1
    if c.history is None or not c.history.complete() or through < 1:
        return None
    n = Nums()
    team = c.team(rid)
    wins, losses, _ = season_records(c.history, through)[rid]
    text = f"{team} was {n.record(wins, losses)}, {n.ord(c.before[rid])} of {n(12)}, before the trade."
    return fact(f"T{i}.{rid}.team", text, n, [team], [])


def _need_fact(c: Context, i: int, trade: Trade, rid: int) -> Fact:
    n = Nums()
    team = c.team(rid)
    side = next(s for m in c.week.matchups for s in (m.a, m.b) if s.roster_id == rid)
    positions = sorted({c.lines[pid].position for pid in (*trade.adds, *trade.drops) if pid in c.lines})
    depth = [f"{n(sum(line.position == pos for line in side.lines))} {pos}" for pos in positions]
    spots = max(0, c.week.roster_slots - len(side.lines))
    text = (
        f"{team} has {_join(depth)} after the trade and "
        f"{n(spots)} open roster {'spot' if spots == 1 else 'spots'}."
    )
    return fact(f"T{i}.{rid}.need", text, n, [team], [])


def _impact_fact(c: Context, i: int, trade: Trade, rid: int, pid: str) -> Fact | None:
    """What a player that the roster got scored this week, for the team that held him in the lineup."""
    # A later trade can move him on. Only a roster of this trade is in the scope of the chapter.
    owner = c.line_owner.get(pid)
    if owner not in trade.roster_ids:
        return None
    n = Nums()
    line = c.lines[pid]
    team = c.team(owner)
    where = "for" if line.started else "on the bench for"
    text = f"{line.name} scored {n(line.points)} this week {where} {team}."
    return fact(f"T{i}.{rid}.impact.{pid}", text, n, [team], [line.name])


def _swing_fact(c: Context, i: int, trade: Trade, rid: int) -> Fact | None:
    """The points of the traded starters against the margin of the roster's matchup."""
    # A player with no line counts 0, so he is left out of both sums.
    got = [c.lines[pid] for pid in _moved(trade, rid, True) if pid in c.lines]
    gave = [c.lines[pid] for pid in _moved(trade, rid, False) if pid in c.lines]
    # A later trade can move a player on, so a line counts only for the roster that holds it in the lineup.
    # The roster that got him must own the line. The roster that got him from the giver must own it for "gave".
    got_started = [line for line in got if line.started and c.line_owner[line.player_id] == rid]
    gave_started = [
        line for line in gave if line.started and c.line_owner[line.player_id] == trade.adds[line.player_id]
    ]
    if not got_started and not gave_started:
        return None
    n = Nums()
    x = sum((Decimal(str(line.points)) for line in got_started), Decimal(0))
    y = sum((Decimal(str(line.points)) for line in gave_started), Decimal(0))
    f = next(f for f, m in zip(c.mfacts, c.week.matchups) if rid in (m.a.roster_id, m.b.roster_id))
    # A tie is neither a win nor a loss, and any gap would change it. No "decisive" or
    # "not enough" sentence is true for a tie, so a tied matchup gets no swing fact.
    if f.winner is None:
        return None
    # The trade decided the game only when it points the same way as the result: the winner gained
    # at least the margin, or the loser lost at least the margin.
    toward = float(x - y) if rid == f.winner else float(y - x)
    team = c.team(rid)
    others = [r for r in trade.roster_ids if r != rid]
    partners = c.team(others[0]) if len(others) == 1 else "its trade partners"
    text = (
        f"The players {team} got and started scored {n(float(x))} this week; "
        f"the players it gave that {partners} started scored {n(float(y))}. "
    )
    if r2(toward) >= r2(f.margin):
        side = "above" if r2(toward) > r2(f.margin) else "equal to"
        text += f"The gap is {n(toward)}, {side} the margin of {n(f.margin)} in its matchup."
    else:
        text += (
            f"In its matchup, that is a gap of {n(abs(float(x - y)))} against a margin of {n(f.margin)}, "
            "not enough to change the result."
        )
    teams = [team, *(c.team(r) for r in others)] if len(others) == 1 else [team]
    return fact(f"T{i}.{rid}.swing", text, n, teams, [line.name for line in (*got_started, *gave_started)])


def _share_fact(c: Context, i: int, pid: str, kind: str, share: UsageShare | None) -> Fact | None:
    """The snap share or target share of a player before the trade. `kind` is the fact ID suffix."""
    if share is None:
        return None
    n = Nums()
    name = c.lines[pid].name
    label = "snap share" if kind == "usage" else "target share"
    if share.direction is None:
        games = f"{n(share.weeks)} {'game' if share.weeks == 1 else 'games'}"
        text = f"{name}'s {label} was {n(share.percent)} percent over {games} before the trade."
    else:
        text = (
            f"{name}'s {label} was {n(share.percent)} percent over the last {n(2)} weeks before the trade, "
            f"{share.direction} from the {n(2)} weeks before that."
        )
    return fact(f"T{i}.{pid}.{kind}", text, n, [], [name])


def _redzone_fact(c: Context, i: int, pid: str, through: int) -> Fact | None:
    """The red-zone targets and carries of a player from week 1 to N-1."""
    zone = red_zone(c.history, pid, through)
    if zone is None:
        return None
    n = Nums()
    name = c.lines[pid].name
    targets, carries = zone
    text = (
        f"{name} had {n(targets)} red-zone {'target' if targets == 1 else 'targets'} and "
        f"{n(carries)} red-zone {'carry' if carries == 1 else 'carries'} this season before the trade."
    )
    return fact(f"T{i}.{pid}.redzone", text, n, [], [name])


def _injury_fact(c: Context, i: int, pid: str, through: int) -> Fact | None:
    """The NFL injury report of a player in weeks 1 to N-1. A week N entry is after the trade and never counts."""
    if c.nfl is None or c.nfl.injuries is None:
        return None
    reports = {w: status for w, status in c.nfl.injuries.get(pid, {}).items() if w <= through}
    if not reports:
        return None
    n = Nums()
    name = c.lines[pid].name
    count = weeks_text(len(reports), n)
    if through in reports:
        text = (
            f"{name} was listed {reports[through]} on the NFL injury report in week {n(through)}, "
            f"and in {count} this season before the trade."
        )
    else:
        text = f"{name} was on the NFL injury report in {count} this season before the trade."
    return fact(f"T{i}.{pid}.injury", text, n, [], [name])


def _usage_facts(c: Context, i: int, trade: Trade) -> list[Fact]:
    """The usage, red-zone, and injury facts of each moved player with a line this week, from weeks 1 to N-1."""
    through = c.week.week - 1
    out = []
    for pid in dict.fromkeys((*trade.adds, *trade.drops)):
        if pid not in c.lines:
            continue
        position = c.lines[pid].position
        if c.history is not None:
            out.append(_share_fact(c, i, pid, "usage", snap_share(c.history, pid, through)))
            if position in ("RB", "WR", "TE"):
                out.append(_share_fact(c, i, pid, "targets", target_share(c.history, pid, through)))
            if position in ("QB", "RB", "WR", "TE"):
                out.append(_redzone_fact(c, i, pid, through))
        out.append(_injury_fact(c, i, pid, through))
    return [f for f in out if f is not None]


def _value_facts(c: Context, i: int, trade: Trade) -> list[Fact]:
    """The trade value of each moved player and the value each side gave and got. No facts without a chart."""
    if c.chart is None:
        return []
    values = c.chart.values
    # A player with no line has no name to cite, so he stays out of the sums and the unlisted names.
    moved = [pid for pid in dict.fromkeys((*trade.adds, *trade.drops)) if pid in c.lines]
    valued = [pid for pid in moved if pid in values]
    if not valued:
        return []
    out = []
    for pid in valued:
        n = Nums()
        name = c.lines[pid].name
        text = f"{name}'s trade value was {n(values[pid])} in the week of the trade."
        out.append(fact(f"T{i}.{pid}.value", text, n, [], [name]))
    unlisted = [c.lines[pid].name for pid in moved if pid not in values]
    for rid in trade.roster_ids:
        n = Nums()
        team = c.team(rid)

        def total(got: bool) -> float:
            # Decimal sums keep a half-point total exact.
            pids = [pid for pid in _moved(trade, rid, got) if pid in valued]
            return float(sum((Decimal(str(values[pid])) for pid in pids), Decimal(0)))

        text = f"{team} gave {n(total(False))} and got {n(total(True))} in trade value"
        if unlisted:
            text += f", with {_join(unlisted)} unlisted"
        if trade.draft_picks:
            text += "; the pick is not valued." if len(trade.draft_picks) == 1 else "; the picks are not valued."
        else:
            text += "."
        out.append(fact(f"T{i}.{rid}.value", text, n, [team], unlisted))
    return out


def _late_fact(c: Context, i: int, trade: Trade) -> Fact:
    """A late trade came after the lineups locked, so the points of its players went to the old rosters."""
    text = "The trade came after the lineups locked, so the lineups show the rosters from before it."
    return fact(f"T{i}.late", text, Nums(), [c.team(r) for r in trade.roster_ids], [])


def trade_facts(c: Context) -> list[Fact]:
    """The sides, impact, swing, and late facts of each trade, kept for the trade analyzer.
    The weekly sheet leaves them out, because the page shows the trade card with no recap."""
    out = []
    for i, trade in enumerate(c.trades, start=1):
        out.append(_sides_fact(c, i, trade))
        for rid in trade.roster_ids:
            got = _got_with_lines(c, trade, rid)
            out += [f for f in (_impact_fact(c, i, trade, rid, pid) for pid in got) if f is not None]
        if is_late(trade, c.week):
            out.append(_late_fact(c, i, trade))
            continue
        for rid in trade.roster_ids:
            swing = _swing_fact(c, i, trade, rid)
            if swing is not None:
                out.append(swing)
    return out


def grade_input_facts(c: Context) -> list[Fact]:
    """The grade inputs of each trade. The trade analyzer uses them; the weekly sheet does not.

    They are the got and gave profiles, the team record, the usage, injury, and value facts, and the need.
    """
    out = []
    for i, trade in enumerate(c.trades, start=1):
        for rid in trade.roster_ids:
            got = _got_with_lines(c, trade, rid)
            out += [_player_trade_fact(c, i, rid, pid, "got") for pid in got]
            out += [_player_trade_fact(c, i, rid, pid, "gave") for pid in _moved(trade, rid, False) if pid in c.lines]
            team = _team_fact(c, i, rid)
            if team is not None:
                out.append(team)
        out += _usage_facts(c, i, trade)
        # The chart is for the week of the trade, so late trades keep their value facts.
        out += _value_facts(c, i, trade)
        # A late trade happened after the lineups locked, so the lineup shows the roster from before it.
        if is_late(trade, c.week):
            continue
        for rid in trade.roster_ids:
            out.append(_need_fact(c, i, trade, rid))
    return out
