"""
Builds the award facts and the expected award facts.
The awards and Game Changer chapters read them.
"""
import logging
from collections import Counter

from cornerstone.client import Client
from cornerstone.facts_nflverse import expected_awards
from cornerstone.models import (
    Fact,
)
from cornerstone.sheet.base import AWARD_TITLES, Context, Nums, fact

logger = logging.getLogger(__name__)

NEWS_MAX_CHARS = 300


def facts(context: Context, client: Client) -> list[Fact]:
    """The awards, the expected awards, and the latest news on the Game Changer.

    The awards and Game Changer chapters read them.
    """
    return award_facts(context) + expected_award_facts(context)


def award_facts(c: Context) -> list[Fact]:
    out = []
    for aw in c.awards:
        n = Nums()
        team = c.team(aw.roster_id)
        text = f"{AWARD_TITLES[aw.key]}: {c.who(aw.line)}, {team}. {n.text(aw.reason)}"
        out.append(fact(f"AW.{aw.key}", text, n, [team], [aw.line.name]))
    gc = next((a for a in c.awards if a.key == "game_changer"), None)
    if gc:
        out += _news_facts(c, gc)
    return out


def expected_award_facts(c: Context) -> list[Fact]:
    """The unlucky and lucky awards from the expected gap. None when the expected points lack week N."""
    out = []
    awards_held = Counter(a.line.player_id for a in c.awards)
    for key, g in expected_awards(c.week, c.nfl, awards_held).items():
        n = Nums()
        team = c.team(g.roster_id)
        side = "under" if g.gap < 0 else "over"
        text = (
            f"{AWARD_TITLES[key]}: {c.who(g.line)}, {team}. "
            f"{g.line.name} scored {n(g.line.points)} on {n(g.expected)} expected points, {n(abs(g.gap))} {side}."
        )
        out.append(fact(f"AW.{key}", text, n, [team], [g.line.name]))
    return out


def _news_facts(c: Context, gc) -> list[Fact]:
    # News is an unofficial endpoint. A failure must never stop a build.
    try:
        items = c.news(gc.line.player_id)
        # Items arrive in no promised order, and "published" is epoch milliseconds as a string.
        newest = max(items, key=lambda i: int(i.get("published") or 0), default={})
    except Exception:
        logger.exception("News fetch failed for %s", gc.line.name)
        return []
    description = (newest.get("metadata") or {}).get("description") or ""
    if not description:
        return []
    n = Nums()
    text = f"Latest news on {gc.line.name}: {n.text(_cut_at_word(description, NEWS_MAX_CHARS))}"
    return [fact("AW.game_changer.news", text, n, [], [gc.line.name])]


def _cut_at_word(text: str, limit: int) -> str:
    """Cut at the last whitespace before the limit, so no word or number is cut in half."""
    if len(text) <= limit:
        return text
    head = text[:limit]
    space = max(head.rfind(" "), head.rfind("\n"), head.rfind("\t"))
    return (head[:space] if space > 0 else head).rstrip()
