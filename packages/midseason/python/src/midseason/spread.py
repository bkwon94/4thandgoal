"""
The spread rule of the midseason report: each team gets 1 to 3 headlines. Arcs, awards, and the opener never move.
A callout moves to the next team of its ranking. PRD, "The spread rule", and decision ticket 09.
"""
from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import BaseModel

from midseason.arcs import Arcs
from midseason.draft import DraftValue
from midseason.injury import InjuryToll
from midseason.lineups import LineupChoices
from midseason.luck import ScheduleLuck, swap_rankings
from midseason.records import RecordBook
from midseason.trades import TradeFacts
from midseason.waivers import WaiverFacts

# The most headlines that one team holds. GLOSSARY.md, "Spread rule".
MAX_HEADLINES = 3

HeadlineKind = Literal["opener", "arc", "award", "callout"]


class Headline(BaseModel):
    """One headline of one team. GLOSSARY.md, "Headline"."""
    kind: HeadlineKind
    # The headline itself, such as "arc.collapse", "award.mvp", or "luck.most_better".
    key: str
    # The key of the chapter that shows it. None for the opener, which sits above the acts.
    chapter: str | None
    roster_id: int
    # The place of the team in the ranking of a callout. 1 when the callout names the #1 team.
    place: int = 1


class Callout(BaseModel):
    """A callout before the rule: its key, its chapter, and the teams in the order of its ranking, the #1 first.
    A team shows once in a ranking."""
    key: str
    chapter: str
    ranking: list[int]


def spread_rule(fixed: Sequence[Headline], callouts: Sequence[Callout], teams: Sequence[int]) -> list[Headline]:
    """Every headline of the report: the fixed headlines as they are, then one per callout, in the order given.

    The fixed headlines are the opener, the arcs, and the awards. Each is a fact about its team, so it never moves.
    Each callout names the first team of its ranking with fewer than 3 headlines, so it goes to the next team when the
    #1 team is full. Then each team with no headline, in the order of `teams`, takes the callout where it ranks best
    from a team that keeps one or more. A callout that no team has room for names no team.
    """
    counts = {rid: 0 for rid in teams}
    for headline in fixed:
        counts[headline.roster_id] = counts.get(headline.roster_id, 0) + 1
    holders: dict[str, Headline] = {}
    for callout in callouts:
        place = next((i for i, rid in enumerate(callout.ranking, start=1) if counts.get(rid, 0) < MAX_HEADLINES), None)
        if place is None:
            continue
        holder = callout.ranking[place - 1]
        holders[callout.key] = Headline(kind="callout", key=callout.key, chapter=callout.chapter, roster_id=holder,
                                        place=place)
        counts[holder] = counts.get(holder, 0) + 1
    for rid in teams:
        if counts[rid]:
            continue
        # The team takes the callout where it ranks best. A tie goes to the callout earlier on the page.
        options = [(callout.ranking.index(rid), index, callout) for index, callout in enumerate(callouts)
                   if rid in callout.ranking and callout.key in holders and counts[holders[callout.key].roster_id] > 1]
        if not options:
            continue
        rank, _, callout = min(options, key=lambda option: option[:2])
        counts[holders[callout.key].roster_id] -= 1
        holders[callout.key] = Headline(kind="callout", key=callout.key, chapter=callout.chapter, roster_id=rid,
                                        place=rank + 1)
        counts[rid] += 1
    return [*fixed, *(holders[callout.key] for callout in callouts if callout.key in holders)]


def moved_off(headlines: Sequence[Headline], callouts: Sequence[Callout]) -> dict[str, set[int]]:
    """The teams that the rule moved off a callout, by chapter key: each team ranked ahead of the holder. The prose
    block of the chapter may not name them, so a blurb never names a team that lost its headline there."""
    holders: Mapping[str, Headline] = {h.key: h for h in headlines if h.kind == "callout"}
    out: dict[str, set[int]] = {}
    for callout in callouts:
        holder = holders.get(callout.key)
        ahead = callout.ranking if holder is None else callout.ranking[:holder.place - 1]
        if ahead:
            out.setdefault(callout.chapter, set()).update(ahead)
    return out


def _unique(roster_ids: Sequence[int]) -> list[int]:
    return list(dict.fromkeys(roster_ids))


def arc_and_award_headlines(arcs: Arcs, book: RecordBook) -> list[Headline]:
    """The headlines that never move: each arc of each team, then each award."""
    out = [Headline(kind="arc", key="arc." + arc.kind.lower().replace(" ", "-"), chapter="arcs",
                    roster_id=team.roster_id)
           for team in arcs.teams for arc in team.arcs]
    out += [Headline(kind="award", key=f"award.{award.key}", chapter="records", roster_id=award.roster_id)
            for award in book.awards]
    return out


def report_callouts(
    luck: ScheduleLuck, injuries: InjuryToll, draft: DraftValue, waivers: WaiverFacts, trades: TradeFacts,
    lineups: LineupChoices,
) -> list[Callout]:
    """The callouts of the report in page order, each with its ranking of teams. A table row is no callout: the
    table still shows every team. A chapter with no ranked team has no callout."""
    most_better, biggest_miss = swap_rankings(luck.swap)
    winners = [next(side.roster_id for side in card.sides if side.team == card.winner)
               for card in trades.trades if card.winner is not None]
    rankings = [
        ("luck.most_better", "luck", most_better),
        ("luck.biggest_miss", "luck", biggest_miss),
        ("injuries.toll", "injuries", [team.roster_id for team in injuries.teams if team.games]),
        ("draft.steal", "draft", [row.roster_id for row in draft.steals]),
        ("draft.bust", "draft", [row.roster_id for row in draft.busts]),
        ("waivers.hit", "waivers", [pickup.roster_id for pickup in waivers.hits]),
        ("waivers.miss", "waivers", [pickup.roster_id for pickup in waivers.misses]),
        ("trades.top", "trades", winners),
        ("lineup.bench", "lineup", [team.roster_id for team in lineups.teams if team.bench_points]),
    ]
    return [Callout(key=key, chapter=chapter, ranking=_unique(ranking)) for key, chapter, ranking in rankings
            if ranking]
