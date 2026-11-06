"""
The injury toll, a chapter of Act I: the starter games that each team lost to injury, by NFL week. GLOSSARY.md,
"Injury toll". It reads the saved history and the injury statuses that the app hands in.
"""
from collections.abc import Collection, Mapping
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, Fact, History
from midseason.players import SKILL_POSITIONS, PlayerCard

# The Key starter rule of GLOSSARY.md, "Key starter": 3 starts in the last 4 completed weeks, or 2 starts with fewer
# weeks. Fewer than 2 weeks say nothing about a habit. The week package owns the weekly copy of the rule, and the
# midseason package may not import it.
KEY_STARTER_WEEKS = 4
KEY_STARTER_STARTS = 3
KEY_STARTER_SHORT_STARTS = 2
# The Sleeper statuses that say a player is out hurt. A suspension is no injury, so it stays out.
OUT_STATUSES = ("Out", "IR", "PUP")


class InjuredStarter(BaseModel):
    """One key starter of a team and the games he missed for it."""
    player_id: str
    name: str
    position: str
    games: int
    # The NFL weeks he missed, in order.
    weeks: list[int]


class TeamInjuryToll(BaseModel):
    """The injury toll of one team."""
    roster_id: int
    name: str
    # The place by starter games lost, most first. Teams with the same count share no place: the order is by name.
    rank: int
    games: int
    # Most games first.
    players: list[InjuredStarter]


class InjuryToll(BaseModel):
    """The facts of the injury toll: one row per team, most starter games lost first."""
    teams: list[TeamInjuryToll]


class InjuryChapter(BaseModel):
    """The injury toll chapter of Act I."""
    key: Literal["injuries"] = "injuries"
    title: str = "The injury toll"
    facts: InjuryToll
    blurb: Blurb | None = None
    roast: Blurb | None = None


def _key_starter(history: History, roster_id: int, player_id: str, week: int) -> bool:
    """True when the team started the player in enough of its completed weeks before `week`."""
    before = [number for number in range(max(1, week - KEY_STARTER_WEEKS), week) if number in history.weeks]
    if len(before) < KEY_STARTER_SHORT_STARTS:
        return False
    bar = KEY_STARTER_STARTS if len(before) >= KEY_STARTER_WEEKS else KEY_STARTER_SHORT_STARTS
    starts = sum(player_id in history.weeks[number].starters.get(roster_id, []) for number in before)
    return starts >= bar


def injury_toll(
    history: History, through: int, names: Mapping[int, str], players: Mapping[str, PlayerCard], *,
    report_out: Mapping[str, Collection[int]], roster_out: Mapping[int, Collection[str]],
    team_weeks: Mapping[str, Collection[int]],
) -> InjuryToll:
    """The injury toll of weeks 1 to `through`.

    A player misses a game in a week that his NFL team plays and he has no offensive snap, when the injury report
    lists him Out or, with no Out row, his roster status is out. The ports come from the app: `report_out` holds the
    weeks the nflverse injury report lists each player Out, `roster_out` the players with a Sleeper status of out
    each week, and `team_weeks` the weeks each NFL team plays. The fallback of `roster_out` covers a missing row of
    the injury report (PRD, "Missing injury rows").

    A missed game is a starter game when the player was a key starter of the team in the weeks before his absence
    started. A bye week neither counts nor ends the absence. A week he plays, or misses with no injury, ends it.
    """
    lost: dict[int, dict[str, list[int]]] = {rid: {} for rid in names}
    for roster_id in names:
        # The key starter verdict of each player at the start of his absence, while the absence lasts.
        absent: dict[str, bool] = {}
        for number in range(1, through + 1):
            week = history.weeks[number]
            for pid in week.rosters.get(roster_id, []):
                card = players.get(pid)
                if card is None or card.position not in SKILL_POSITIONS:
                    continue
                if card.nfl_team is None or number not in team_weeks.get(card.nfl_team, ()):
                    continue
                snaps = week.stats.get(pid, {}).get("off_snp", 0.0) > 0
                out = number in report_out.get(pid, ()) or pid in roster_out.get(number, ())
                if snaps or not out:
                    absent.pop(pid, None)
                    continue
                if pid not in absent:
                    absent[pid] = _key_starter(history, roster_id, pid, number)
                if absent[pid]:
                    lost[roster_id].setdefault(pid, []).append(number)
    rows = []
    for roster_id, missed in lost.items():
        starters = sorted(
            (InjuredStarter(player_id=pid, name=players[pid].name, position=players[pid].position, games=len(weeks),
                            weeks=weeks) for pid, weeks in missed.items()),
            key=lambda p: (-p.games, p.name))
        rows.append((roster_id, sum(p.games for p in starters), starters))
    rows.sort(key=lambda row: (-row[1], names[row[0]]))
    return InjuryToll(teams=[
        TeamInjuryToll(roster_id=rid, name=names[rid], rank=place, games=games, players=starters)
        for place, (rid, games, starters) in enumerate(rows, start=1)
    ])


def injury_facts(toll: InjuryToll) -> list[Fact]:
    """The facts of the injury toll: the starter games each team lost, and the player who cost it the most."""
    facts = []
    for team in toll.teams:
        n = Nums()
        games = "starter game" if team.games == 1 else "starter games"
        facts.append(fact(f"IT.{team.roster_id}", f"{team.name} lost {n(team.games)} {games} to injury, "
                          f"{n.ord(team.rank)} in the league.", n, [team.name], []))
        if team.players:
            top = team.players[0]
            n = Nums()
            missed = "game" if top.games == 1 else "games"
            facts.append(fact(f"IT.{team.roster_id}.top", f"{top.name} missed {n(top.games)} {missed} as a starter of "
                              f"{team.name}.", n, [team.name], [top.name]))
    return facts
