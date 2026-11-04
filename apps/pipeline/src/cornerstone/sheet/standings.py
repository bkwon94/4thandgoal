"""
Builds the standings facts and the median facts.
The standings facts place each team against the last playoff spot.
"""
from decimal import Decimal

from cornerstone.sheet.base import Context
from facts.tokens import Nums, fact
from league.client import Client
from league.models import (
    Fact,
)
from league.numbers import r2

# The phrase for a team with the wins of the last playoff spot, keyed by its place against that spot.
# A team below it fills in its spots below the last playoff spot as a digit, such as "2 spots".
CUT_PHRASES = {
    "above": "level with the last playoff spot",
    "at": "in the last playoff spot",
    "below": "{spots} outside the playoff spots",
}


def facts(context: Context, client: Client) -> list[Fact]:
    """The place of each team in the standings, and each score against the league median.

    The Matchup of the Week, recap, median, next week, and rankings chapters read the standings. The median chapter
    reads the median.
    """
    return standings_facts(context) + median_facts_sheet(context)


def cut_phrase(rank: int, last_spot: int, n: Nums) -> str:
    """The fixed phrase for a team with the wins of the last playoff spot, from its rank."""
    if rank < last_spot:
        return CUT_PHRASES["above"]
    if rank == last_spot:
        return CUT_PHRASES["at"]
    distance = rank - last_spot
    spots = f"{n(distance)} spot" if distance == 1 else f"{n(distance)} spots"
    return CUT_PHRASES["below"].format(spots=spots)


def standings_facts(c: Context) -> list[Fact]:
    out = []
    last_spot = max((s.rank for s in c.table if s.in_playoffs), default=0)
    for s in c.table:
        n = Nums()
        cut = "in" if s.in_playoffs else "out of"
        side = "above" if s.games_from_cut > 0 else "below" if s.games_from_cut < 0 else "at"
        team = c.team(s.roster_id)
        gap = abs(s.games_from_cut)
        games = "game" if gap == 1 else "games"
        # "0 games at the cut" lets the writer say "still on the outside" for one tied team and "right at the cut"
        # for the next, and a reader sees a contradiction. One fixed phrase per spot keeps every chapter on one wording.
        if s.games_from_cut == 0:
            place = cut_phrase(s.rank, last_spot, n)
        else:
            place = f"{cut} the playoff spots, {n(gap)} {games} {side} the cut"
        text = (
            f"{team} is {n.ord(s.rank)} with a {n.record(s.wins, s.losses)} record "
            f"and {n(s.points_for)} points for, {place}."
        )
        out.append(fact(f"S.{s.rank}", text, n, [team], []))
    return out


def median_facts_sheet(c: Context) -> list[Fact]:
    m = c.median
    n = Nums()
    out = [fact("MED.value", f"The league median this week was {n(m.median)}.", n, [], [])]
    # Gaps use the exact median, as median_facts does, so a rounded median never shifts a gap.
    ordered = sorted(c.scores.values(), reverse=True)
    exact = (Decimal(str(ordered[5])) + Decimal(str(ordered[6]))) / 2
    for kind, rosters, word in (("above", m.above, "above"), ("below", m.below, "below")):
        for rid in rosters:
            n = Nums()
            gap = r2(abs(float(Decimal(str(c.scores[rid])) - exact)))
            team = c.team(rid)
            text = f"{team} scored {n(c.scores[rid])}, {n(gap)} {word} the median."
            out.append(fact(f"MED.{kind}.{rid}", text, n, [team], []))
    n = Nums()
    (up_id, up_gap), (down_id, down_gap) = m.closest_above, m.closest_below
    text = (
        f"{c.team(up_id)} cleared the median by {n(up_gap)}. "
        f"{c.team(down_id)} missed it by {n(down_gap)}."
    )
    out.append(fact("MED.closest", text, n, [c.team(up_id), c.team(down_id)], []))
    return out
