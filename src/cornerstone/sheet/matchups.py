"""
Builds the family of facts for each matchup: the result, the lines, the story, and the context.
The recap and Matchup of the Week chapters read them.
"""

from cornerstone.models import (
    Fact,
    sub,
)
from cornerstone.sheet.base import MOVE_WORDS, Context, Nums, fact


def matchup_fact_family(c: Context) -> list[Fact]:
    out = []
    for f, m in zip(c.mfacts, c.week.matchups):
        out += _result_facts(c, f, m)
        out += _line_facts(c, f, m)
        out += _story_facts(c, f)
        out += _injury_facts(c, f, m)
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
