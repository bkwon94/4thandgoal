"""
Builds the drop facts and the NFL injury facts.
They come from the nflverse data, so a week with no nflverse data has none.
"""
from decimal import Decimal

from cornerstone.sheet.base import Context, weeks_text
from facts.tokens import Nums, fact
from league.client import Client
from league.models import (
    DropLine,
    Fact,
)


def facts(context: Context, client: Client) -> list[Fact]:
    """The drops and the NFL injury report of each started player, from the nflverse data.

    The Matchup of the Week, Game Changer, awards, and recap chapters read them.
    """
    return drop_facts(context) + injury_facts_nfl(context)


def _drop_fact(c: Context, d: DropLine) -> list[Fact]:
    line, team = c.lines[d.player_id], c.team(d.roster_id)
    n = Nums()
    if d.targets is None:
        text = f"{line.name} dropped {_passes(d.drops, n)} this week."
    else:
        text = f"{line.name} dropped {n(d.drops)} of {n(d.targets)} targets this week."
    out = [fact(f"D.{d.player_id}", text, n, [team], [line.name])]
    if d.value is not None:
        n = Nums()
        text = (
            f"{line.name}'s drops were worth about {n(d.value)} points by the drop value method, "
            f"with {n(d.end_zone)} in the end zone."
        )
        out.append(fact(f"D.{d.player_id}.value", text, n, [team], [line.name]))
    return out


def _dropswing_facts(c: Context) -> list[Fact]:
    """The losing side's started drop value against the margin. Only nflverse gives a value."""
    out = []
    for f in c.mfacts:
        if f.loser is None or not c.nfl_up:
            continue
        lost = [d for d in c.drops if d.roster_id == f.loser and d.matchup_id == f.matchup_id]
        value = sum((Decimal(str(d.value)) for d in lost), Decimal(0))
        if not lost or value < Decimal(str(f.margin)):
            continue
        n = Nums()
        team = c.team(f.loser)
        text = (
            f"{team}'s starters dropped {_passes(sum(d.drops for d in lost), n)} worth about "
            f"{n(float(value))}, at least the margin of {n(f.margin)}."
        )
        out.append(fact(f"M{f.matchup_id}.dropswing", text, n, [team], [c.lines[d.player_id].name for d in lost]))
    return out


def drop_facts(c: Context) -> list[Fact]:
    out = [fact for d in c.drops for fact in _drop_fact(c, d)]
    out += _dropswing_facts(c)
    if c.drops:
        n = Nums()
        top = c.drops[:3]
        parts = [
            f"{c.lines[d.player_id].name} ({c.team(d.roster_id)}), {n(d.drops)} {'drop' if d.drops == 1 else 'drops'}"
            for d in top
        ]
        out.append(fact("W.drops", "Most drops this week: " + "; ".join(parts) + ".", n,
                         [c.team(d.roster_id) for d in top], [c.lines[d.player_id].name for d in top]))
    return out


def _passes(count: int, n: Nums) -> str:
    return f"{n(count)} pass" + ("" if count == 1 else "es")


def injury_facts_nfl(c: Context) -> list[Fact]:
    """The pre-game status and the report history of each started player. None without nflverse."""
    if c.nfl is None or c.nfl.injuries is None:
        return []
    week = c.week.week
    out = []
    for pid, line in c.lines.items():
        weeks = c.nfl.injuries.get(pid)
        if not line.started or not weeks:
            continue
        team = [c.team(c.line_owner[pid])]
        pregame = _pregame_text(c, pid)
        if pregame is not None:
            out.append(fact(f"I.{pid}.pregame", pregame, Nums(), team, [line.name]))
        n = Nums()
        if week in weeks:
            text = f"{line.name} has been on the NFL injury report {weeks_text(sum(w <= week for w in weeks), n)}."
        # A return claim needs proof of play: nflverse only lists the injured, so a gap alone is not a return.
        elif week - 1 in weeks and c.week.stats.get(pid, {}).get("gp", 0) > 0:
            earlier = weeks_text(sum(w < week for w in weeks), n, "earlier ")
            text = f"{line.name} was on the NFL injury report in {earlier} this season and plays this week."
        else:
            continue
        out.append(fact(f"I.{pid}.history", text, n, team, [line.name]))
    return out


def _pregame_text(c: Context, pid: str) -> str | None:
    """The final NFL injury report status of this week, or None when the player has none."""
    if c.nfl is None or c.nfl.injuries is None:
        return None
    status = c.nfl.injuries.get(pid, {}).get(c.week.week)
    if status is None:
        return None
    return f"{c.lines[pid].name} was listed {status} on the final NFL injury report before his game this week."
