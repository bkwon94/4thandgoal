"""
Builds the family of facts for each matchup: the result, the lines, the story, and the context.
The recap and Matchup of the Week chapters read them.
"""
from datetime import datetime
from decimal import Decimal

from cornerstone.config import LeagueConfig
from cornerstone.models import (
    Fact,
    PlayerLine,
    sub,
)
from cornerstone.numbers import r2
from cornerstone.sheet.base import MOVE_WORDS, Context, Nums, fact


def facts(context: Context, config: LeagueConfig) -> list[Fact]:
    """The result, the lines, the story, and the context of each matchup.

    The Matchup of the Week, Game Changer, and recap chapters read them. The awards chapter reads each result.
    """
    return matchup_fact_family(context)


def matchup_fact_family(c: Context) -> list[Fact]:
    out = []
    for f, m in zip(c.mfacts, c.week.matchups):
        out += _result_facts(c, f, m)
        out += _line_facts(c, f, m)
        out += _story_facts(c, f)
        out += _injury_facts(c, f, m)
        out += _hurt_facts(c, f, m)
        out += _lead_facts(c, f, m)
        out += _context_facts(c, f, m)
    return out


def _result_facts(c, f, m) -> list[Fact]:
    n = Nums()
    mid = f"M{f.matchup_id}"
    a, b = c.team(m.a.roster_id), c.team(m.b.roster_id)
    if f.winner is None:
        text = f"{a} and {b} tied at {n(f.score_w)}."
        teams = [a, b]
    else:
        w, loser = c.team(f.winner), c.team(f.loser)
        text = f"{w} beat {loser} {n(f.score_w)} to {n(f.score_l)}, a margin of {n(f.margin)}."
        teams = [w, loser]
    out = [fact(f"{mid}.result", text, n, teams, [])]
    for rid, line in f.top_scorer.items():
        n = Nums()
        team = c.team(rid)
        text = f"{c.who(line)} was the top scorer for {team} with {n(line.points)}."
        out.append(fact(f"{mid}.top.{rid}", text, n, [team], [line.name]))
    return out


def _line_facts(c, f, m) -> list[Fact]:
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started:
                continue
            n = Nums()
            text = f"{c.who(line)} started for {team} and {c.against_projection(line, n)}."
            out.append(fact(f"M{f.matchup_id}.starter.{side.roster_id}.{line.player_id}", text, n, [team], [line.name]))
    return out


def _story_facts(c, f) -> list[Fact]:
    """Drivers, swing players, bench regret, and recent adds for one matchup."""
    mid = f"M{f.matchup_id}"
    out = []
    for line in f.drivers:
        n = Nums()
        team = c.team(c.line_owner[line.player_id])
        gap = abs(sub(line.points, line.projection))
        text = (
            f"{line.name} ({team}) is a margin driver: {n(line.points)} on a {n(line.projection)} "
            f"projection, a gap of {n(gap)} against a margin of {n(f.margin)}."
        )
        out.append(fact(f"{mid}.driver.{line.player_id}", text, n, [team], [line.name]))
    for line in f.swing:
        n = Nums()
        team = c.team(f.winner)
        text = f"{line.name} is a swing player for {team}: {n(line.points)} exceeded the margin of {n(f.margin)}."
        out.append(fact(f"{mid}.swing.{line.player_id}", text, n, [team], [line.name]))
    for bench, starter in f.bench_regret:
        n = Nums()
        team = c.team(f.loser)
        text = (
            f"{team} left {bench.name} ({n(bench.points)}) on the bench behind "
            f"{starter.name} ({n(starter.points)}); the swap would have flipped the result."
        )
        out.append(fact(f"{mid}.regret.{bench.player_id}", text, n, [team], [bench.name, starter.name]))
    for mv in f.recent_moves:
        n = Nums()
        line = c.lines[mv.player_id]
        team = c.team(mv.roster_id)
        text = (
            f"{line.name} is a recent add: {line.name} started for {team} after a "
            f"{MOVE_WORDS[mv.kind]} in week {n(mv.week)} "
            f"and {c.against_projection(line, n)}."
        )
        out.append(fact(f"{mid}.move.{mv.player_id}", text, n, [team], [line.name]))
    return out


def _injury_facts(c, f, m) -> list[Fact]:
    """One fact per started line with a Sleeper injury status in one matchup."""
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started or not line.injury_status:
                continue
            # The status comes from the players file fetched after the games, so it is post-game.
            # The fact must not imply that the player was hurt at kickoff.
            status = f"listed {line.injury_status}"
            if line.injury_body_part:
                status += f" ({line.injury_body_part})"
            text = (
                f"{line.name} is now {status} on Sleeper as of the Tuesday after this week's games. "
                "The status may have come from this game."
            )
            out.append(fact(f"M{f.matchup_id}.inj.{line.player_id}", text, Nums(), [team], [line.name]))
    return out


def _hurt_facts(c, f, m) -> list[Fact]:
    """The injury play and the snaps of each started line, so a recap can tell when a starter went down.

    The play comes from the nflverse play by play, through `NflverseWeek.injury_plays`. The snaps come from the
    Sleeper stats of the week. With no play by play, the play fact is absent, and the recap says nothing about it.
    """
    plays = c.nfl.injury_plays if c.nfl is not None and c.nfl.injury_plays is not None else {}
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started:
                continue
            play = plays.get(line.player_id)
            if play is not None:
                n = Nums()
                when = "overtime" if play.quarter == 5 else f"the {n.ord(play.quarter)} quarter"
                # The play by play writes "00:32" for a clock under a minute. The page reads "0:32".
                clock = n.text(play.clock.removeprefix("0"))
                text = f"{line.name} was injured on a play in {when} of {play.away} at {play.home}, with {clock} left."
                out.append(fact(f"M{f.matchup_id}.hurt.{line.player_id}", text, n, [team], [line.name]))
            # A starter with a Sleeper status but no injury play still gets his snaps, so the recap can say he left
            # early or played through it.
            stats = c.week.stats.get(line.player_id, {})
            if (play is not None or line.injury_status) and "off_snp" in stats and "tm_off_snp" in stats:
                n = Nums()
                text = (f"{line.name} played {n(int(stats['off_snp']))} of {n(int(stats['tm_off_snp']))} "
                        f"offensive snaps for {line.nfl_team}.")
                out.append(fact(f"M{f.matchup_id}.snaps.{line.player_id}", text, n, [team], [line.name]))
    return out


# The words of each slot after "after" and as the time of a play. The kickoffs are in Eastern time.
SUNDAY_SLOTS = (
    (16, "the early Sunday games", "in the early Sunday games"),
    (19, "the late Sunday games", "in the late Sunday games"),
    (24, "Sunday night", "on Sunday night"),
)
SUNDAY = 6


def _slot(kickoff: datetime) -> tuple[str, str]:
    """The slot of a kickoff, as the words after "after" and the words of the time. One slot per day but Sunday."""
    if kickoff.weekday() != SUNDAY:
        day = kickoff.strftime("%A")
        return day, f"on {day}"
    return next((after, during) for hour, after, during in SUNDAY_SLOTS if kickoff.hour < hour)


def _slot_lines(c, m) -> list[tuple[tuple[str, str], list[tuple[int, PlayerLine]]]] | None:
    """The started lines of both sides by slot, in kickoff order, each with its roster ID.

    None when the week has no kickoffs, or when a starter with points has no kickoff. Then the slot sums would not
    reach the final score, so the lead facts are absent, and the recap says nothing about the lead.
    """
    kickoffs = c.nfl.kickoffs if c.nfl is not None else None
    if not kickoffs:
        return None
    slots: dict[tuple[str, str], list[tuple[int, PlayerLine]]] = {}
    first: dict[tuple[str, str], datetime] = {}
    for side in (m.a, m.b):
        for line in side.lines:
            if not line.started:
                continue
            kickoff = kickoffs.get(line.nfl_team or "")
            if kickoff is None:
                # A starter on a bye or with no team scores 0, so he moves no lead.
                if line.points:
                    return None
                continue
            slot = _slot(kickoff)
            slots.setdefault(slot, []).append((side.roster_id, line))
            first[slot] = min(first.get(slot, kickoff), kickoff)
    return sorted(slots.items(), key=lambda item: first[item[0]])


def _lead_facts(c, f, m) -> list[Fact]:
    """The lead after each slot of games, and the turn when the leader before the last slot lost.

    The slot of a starter comes from the kickoff of his NFL team, from the nflverse schedule through
    `NflverseWeek.kickoffs`. The points come from the Sleeper matchups. A slot with no starter of this matchup is not
    in the list, so a matchup with no Monday starter ends after Sunday night.
    """
    slots = _slot_lines(c, m)
    if slots is None or len(slots) < 2:
        return []
    mid = f"M{f.matchup_id}"
    a, b = m.a.roster_id, m.b.roster_id
    margin = Decimal(0)
    margins = []
    for slot, lines in slots:
        # Decimal sums keep the last margin equal to the final margin.
        margin += sum((Decimal(str(line.points)) * (1 if rid == a else -1) for rid, line in lines), Decimal(0))
        margins.append((slot, r2(float(margin))))
    n = Nums()
    parts, leaders = [], []
    for (after, _), x in margins:
        if x == 0:
            parts.append(f"after {after}, the teams were level")
            continue
        leader = a if x > 0 else b
        parts.append(f"after {after}, {c.team(leader)} led by {n(abs(x))}")
        if not leaders or leaders[-1] != leader:
            leaders.append(leader)
    changes = len(leaders) - 1
    if changes == 0:
        tail = "The lead never changed."
    else:
        tail = f"The lead changed {n(changes)} time{'' if changes == 1 else 's'}."
    text = "The lead by slot of games: " + "; ".join(parts) + ". " + tail
    out = [fact(f"{mid}.lead", text, n, [c.team(a), c.team(b)], [])]
    (prev_after, _), prev = margins[-2]
    if f.winner is None or prev == 0 or (a if prev > 0 else b) == f.winner:
        return out
    n = Nums()
    leader, winner = c.team(f.loser), c.team(f.winner)
    (_, during), last_lines = slots[-1]
    # The winner's starters come first, so the line reads as the turn.
    ordered = sorted(last_lines, key=lambda item: (item[0] != f.winner, -item[1].points))
    scored = "; ".join(f"{line.name} scored {n(line.points)} for {c.team(rid)}" for rid, line in ordered)
    text = (f"{leader} led {winner} by {n(abs(prev))} after {prev_after}, and {winner} took the lead {during} "
            f"and won. {during[0].upper()}{during[1:]}, {scored}.")
    out.append(fact(f"{mid}.turn", text, n, [leader, winner], [line.name for _, line in ordered]))
    return out


def _context_facts(c, f, m) -> list[Fact]:
    mid = f"M{f.matchup_id}"
    out = []
    if f.winner is not None and c.before[f.winner] > c.before[f.loser]:
        n = Nums()
        w, loser = c.team(f.winner), c.team(f.loser)
        text = (
            f"This was an upset: {w} was {n.ord(c.before[f.winner])} before this week "
            f"and {loser} was {n.ord(c.before[f.loser])}."
        )
        out.append(fact(f"{mid}.upset", text, n, [w, loser], []))
    n = Nums()
    parts = []
    for rid in (m.a.roster_id, m.b.roster_id):
        s = c.by_rank[rid]
        parts.append(f"{c.team(rid)} is now {n.record(s.wins, s.losses)} ({n.ord(s.rank)}).")
    teams = [c.team(m.a.roster_id), c.team(m.b.roster_id)]
    out.append(fact(f"{mid}.records", " ".join(parts), n, teams, []))
    return out
