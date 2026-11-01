"""
Builds the award facts and the expected award facts.
The awards and Game Changer chapters read them.
"""

from cornerstone.facts_nflverse import expected_awards
from cornerstone.models import (
    Fact,
)
from cornerstone.sheet.base import AWARD_TITLES, Context, Nums, fact, _news_facts


def award_facts(c: Context) -> list[Fact]:
    out = []
    for aw in c.awards:
        n = Nums()
        team = c.team(aw.roster_id)
        text = f"{AWARD_TITLES[aw.key]}: {c.who(aw.line)}, {team}. {n.text(aw.reason)}"
        if aw.skipped:
            text += f" Skipped: {', '.join(aw.skipped)}."
        out.append(fact(f"AW.{aw.key}", text, n, [team], [aw.line.name, *aw.skipped]))
    gc = next((a for a in c.awards if a.key == "game_changer"), None)
    if gc:
        out += _news_facts(c, gc)
    return out


def expected_award_facts(c: Context) -> list[Fact]:
    """The unlucky and lucky awards from the expected gap. None when the expected points lack week N."""
    out = []
    for key, g in expected_awards(c.week, c.nfl, frozenset(a.line.player_id for a in c.awards)).items():
        n = Nums()
        team = c.team(g.roster_id)
        side = "under" if g.gap < 0 else "over"
        text = (
            f"{AWARD_TITLES[key]}: {c.who(g.line)}, {team}. "
            f"{g.line.name} scored {n(g.line.points)} on {n(g.expected)} expected points, {n(abs(g.gap))} {side}."
        )
        out.append(fact(f"AW.{key}", text, n, [team], [g.line.name]))
    return out
