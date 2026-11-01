"""
Builds the position leader facts, the position rank facts, and the history facts.
The position leaders chapter and the history caps read them.
"""

from cornerstone.config import LeagueConfig
from cornerstone.facts_league import (
    TREND_WEEKS,
)
from cornerstone.facts_nflverse import volume_ranks
from cornerstone.history import (
    player_trend,
)
from cornerstone.models import (
    Fact,
    PlayerLine,
)
from cornerstone.numbers import r2
from cornerstone.sheet.base import Context, Nums, fact, trend_text


def facts(bundle: Context, config: LeagueConfig) -> list[Fact]:
    """The facts of the leaders chapter, in the order the sheet lists them.

    Every chapter takes the same two inputs, so the assembly calls each one the same way. This chapter reads no
    config field.
    """
    return (
        rank_facts(bundle) + leader_facts(bundle) + strength_facts(bundle) + history_facts(bundle)
        + player_trend_facts(bundle)
    )


def rank_facts(c: Context) -> list[Fact]:
    out = []
    for r in c.ranks:
        n = Nums()
        line = c.lines[r.player_id]
        team = c.team(c.line_owner[r.player_id])
        text = f"{line.name} ranked {n(r.rank)} of {n(r.of)} among started {r.position}s this week, for {team}."
        out.append(fact(f"RANK.{r.player_id}", text, n, [team], [line.name]))
    return out


def leader_facts(c: Context) -> list[Fact]:
    out = []
    volumes = {p: volume_ranks(c.week, c.nfl, p) for p in {lead.position for lead in c.leaders}}
    for lead in c.leaders:
        n = Nums()
        line = lead.line
        team = c.team(lead.roster_id)
        text = (
            f"{c.who(line)} scored {n(line.points)} for {team}, "
            f"{n.ord(lead.rank)} of {n(lead.of)} among started {lead.position}s this week."
        )
        out.append(fact(f"LEAD.{lead.position}.{lead.rank}", text, n, [team], [line.name]))
        if line.player_id in volumes[lead.position]:
            fid = f"LEAD.{lead.position}.{lead.rank}.volume"
            out.append(_volume_fact(c, fid, lead.position, line, team, volumes[lead.position][line.player_id]))
    return out


# The volume label and its unit at each position with a volume line.
# WOPR is a weighted sum and not a share, so only the carry share carries a percent.
VOLUME_LABELS = {"RB": ("carry share", " percent"), "WR": ("WOPR", ""), "TE": ("WOPR", "")}


def _volume_fact(c: Context, fid: str, position: str, line: PlayerLine, team: str, volume: tuple[int, int]) -> Fact:
    """The week N volume of one position leader and its rank among the started players at his position."""
    value, rank = volume
    label, unit = VOLUME_LABELS[position]
    n = Nums()
    text = f"{c.who(line)} had a {label} of {n(value)}{unit}, {n.ord(rank)} among started {position}s this week."
    return fact(fid, text, n, [team], [line.name])


def strength_facts(c: Context) -> list[Fact]:
    out = []
    for s in c.table:
        if s.schedule_strength is None:
            continue
        n = Nums()
        team = c.team(s.roster_id)
        # Version 1 knows only the next opponent, so the fact names next week, not the rest of the season.
        text = (
            f"{team}'s opponent next week has a win rate of {n(s.schedule_strength)}, "
            f"ranked {n(s.strength_rank)} of {n(12)}, toughest first."
        )
        out.append(fact(f"SOS.{s.roster_id}", text, n, [team], []))
    return out


def history_facts(c: Context) -> list[Fact]:
    """Streak, trend, season high or low, and season average of each team.

    A missing or incomplete history gives no facts, so a fact is never wrong.
    """
    if c.history is None or not c.history.complete():
        return []
    out = []
    for h in c.season_history:
        team = c.team(h.roster_id)
        rid = h.roster_id
        if abs(h.streak) >= 2:
            n = Nums()
            verb = "won" if h.streak > 0 else "lost"
            out.append(fact(f"H.{rid}.streak", f"{team} has {verb} {n(abs(h.streak))} straight.", n, [team], []))
        if h.trend is not None and r2(h.trend) != r2(h.average):
            n = Nums()
            side = "up" if h.trend > h.average else "down"
            text = (
                f"{team} has scored {n(h.trend)} per week over the last {n(TREND_WEEKS)} weeks, "
                f"{side} from a season average of {n(h.average)}."
            )
            out.append(fact(f"H.{rid}.trend", text, n, [team], []))
        # Week 1 has no earlier week, so no score there is a high or a low.
        if c.week.week > 1 and (h.new_high or h.new_low):
            n = Nums()
            kind = "high" if h.new_high else "low"
            text = f"{team}'s {n(c.scores[rid])} this week is a season {kind}."
            out.append(fact(f"H.{rid}.high", text, n, [team], []))
        n = Nums()
        out.append(fact(f"H.{rid}.avg", f"{team} averages {n(h.average)} per week this season.", n, [team], []))
    return out


def player_trend_facts(c: Context) -> list[Fact]:
    """One trend fact for each started line. A missing or incomplete history gives none."""
    if c.history is None or not c.history.complete():
        return []
    out = []
    for pid, line in c.lines.items():
        beaten = player_trend(c.history, pid)
        if not line.started or beaten is None:
            continue
        n = Nums()
        out.append(fact(f"P.{pid}.trend", trend_text(line.name, beaten, n), n, [], [line.name]))
    return out
