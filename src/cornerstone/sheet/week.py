"""
Builds the week facts: the week line, the recent adds, and the injured starters.
The recap chapters read them for the context of each game.
"""

from cornerstone.models import (
    Fact,
)
from cornerstone.sheet.base import MOVE_WORDS, Context, Nums, fact, week_dates


def week_facts(c: Context) -> list[Fact]:
    w = c.week
    n = Nums()
    week_text = f"This is week {n(w.week)} of the {n(w.season)} season, {n.text(week_dates(w.season_start, w.week))}."
    n2 = Nums()
    publish = f"The report was published on {n2.text(c.today.strftime('%a %b %-d, %Y'))}."
    return [
        fact("W.week", week_text, n, [], []),
        fact("W.publish", publish, n2, [], []),
    ]


def recent_add_facts(c: Context) -> list[Fact]:
    """The top three started lines added in this week or the week before, by points."""
    found = []
    for f in c.mfacts:
        for mv in f.recent_moves:
            found.append((c.lines[mv.player_id], mv))
    top = sorted(found, key=lambda x: x[0].points, reverse=True)[:3]
    if not top:
        return []
    n = Nums()
    parts = [
        f"{c.who(line)} for {c.team(mv.roster_id)}, a {MOVE_WORDS[mv.kind]} in week {n(mv.week)}, "
        + c.against_projection(line, n)
        for line, mv in top
    ]
    text = "The top recent adds who started: " + "; ".join(parts) + "."
    teams = sorted({c.team(mv.roster_id) for _, mv in top})
    return [fact("W.adds", text, n, teams, [line.name for line, _ in top])]


def injured_facts(c: Context) -> list[Fact]:
    """Every started line with a Sleeper injury status, league-wide."""
    found = [
        (line, c.team(side.roster_id))
        for m in c.week.matchups for side in (m.a, m.b) for line in side.lines
        if line.started and line.injury_status
    ]
    if not found:
        return []
    parts = [f"{line.name} ({team}, {line.injury_status})" for line, team in found]
    text = "Now on the injury report after this week's games: " + "; ".join(parts) + "."
    teams = sorted({team for _, team in found})
    return [fact("W.injured", text, Nums(), teams, [line.name for line, _ in found])]
