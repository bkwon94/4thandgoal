"""
The injury toll, a chapter of Act I: the starter games that each team lost to injury, by NFL week. GLOSSARY.md,
"Injury toll". It reads the saved history and the injury statuses that the app hands in. The missed-game rule here
also gives the "hurt" tag of a draft bust.
"""
from collections.abc import Collection, Mapping
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, Fact, History
from midseason.players import SKILL_POSITIONS, PlayerCard

# The Key starter rule of GLOSSARY.md, "Key starter": 3 starts in the last 4 completed weeks that the player could
# play, or 2 starts with fewer weeks. Fewer than 2 weeks say nothing about a habit. The week package owns the weekly
# copy of the rule, and the midseason package may not import it.
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
    title: str = "The Injury Toll"
    facts: InjuryToll
    blurb: Blurb | None = None


def _key_starter(history: History, roster_id: int, player_id: str, week: int, playable: Collection[int]) -> bool:
    """True when the team started the player in enough of the weeks before `week` that he could play.

    The window skips his injured weeks and his byes, so an earlier absence does not make a key starter a bench player.
    """
    before = [number for number in sorted(playable) if number < week and number in history.weeks][-KEY_STARTER_WEEKS:]
    if len(before) < KEY_STARTER_SHORT_STARTS:
        return False
    bar = KEY_STARTER_STARTS if len(before) >= KEY_STARTER_WEEKS else KEY_STARTER_SHORT_STARTS
    starts = sum(player_id in history.weeks[number].starters.get(roster_id, []) for number in before)
    return starts >= bar


def _absences(
    history: History, through: int, card: PlayerCard, *, report_out: Mapping[str, Collection[int]],
    roster_out: Mapping[int, Collection[str]], team_weeks: Mapping[str, Collection[int]],
) -> tuple[list[list[int]], set[int]]:
    """The injury absences of the player in weeks 1 to `through`, each one the weeks of his missed games in order, and
    the weeks he could play.

    An absence is a run of games of his NFL team with no offensive snap for him. A week he plays ends it, and a bye
    neither counts nor ends it. The run is an injury when the injury report lists him Out in one of its weeks or, as
    the fallback for a missing row, his roster status is out (PRD, "Missing injury rows"). So one Out week marks each
    game of the run, and a run with no out status is no injury, such as a healthy scratch.
    """
    runs: list[tuple[list[int], bool]] = []
    games: list[int] = []
    out = False
    if card.nfl_team is not None:
        for number in range(1, through + 1):
            if number not in team_weeks.get(card.nfl_team, ()):
                continue
            if history.weeks[number].stats.get(card.player_id, {}).get("off_snp", 0.0) > 0:
                if games:
                    runs.append((games, out))
                games, out = [], False
                continue
            games.append(number)
            out = out or number in report_out.get(card.player_id, ()) or card.player_id in roster_out.get(number, ())
    if games:
        runs.append((games, out))
    absences = [weeks for weeks, hurt in runs if hurt]
    injured = {number for weeks in absences for number in weeks}
    playable = {number for number in range(1, through + 1)
                if card.nfl_team is not None and number in team_weeks.get(card.nfl_team, ()) and number not in injured}
    return absences, playable


def missed_games(
    player_ids: Collection[str], history: History, through: int, players: Mapping[str, PlayerCard], *,
    report_out: Mapping[str, Collection[int]], roster_out: Mapping[int, Collection[str]],
    team_weeks: Mapping[str, Collection[int]],
) -> dict[str, int]:
    """The count of weeks 1 to `through` in which each player missed a game with an injury, on any roster or none.

    The rule and the ports are those of the injury toll. A player with no card misses no game.
    """
    counts: dict[str, int] = {}
    for pid in player_ids:
        card = players.get(pid)
        counts[pid] = 0 if card is None else sum(
            len(weeks) for weeks in _absences(history, through, card, report_out=report_out, roster_out=roster_out,
                                              team_weeks=team_weeks)[0])
    return counts


def injury_toll(
    history: History, through: int, names: Mapping[int, str], players: Mapping[str, PlayerCard], *,
    report_out: Mapping[str, Collection[int]], roster_out: Mapping[int, Collection[str]],
    team_weeks: Mapping[str, Collection[int]],
) -> InjuryToll:
    """The injury toll of weeks 1 to `through`.

    A player misses a game by the rule of `_absences`. The ports come from the app: `report_out` holds the
    weeks the nflverse injury report lists each player Out, `roster_out` the players with a Sleeper status of out
    each week, and `team_weeks` the weeks each NFL team plays.

    Each game of an absence is a starter game of a team when the team held the player in the week before the absence
    or in its first week, and he was a key starter of the team at its start. The key status holds for the whole
    absence, so a team that drops or trades him while he is out still loses each game until he plays again.
    """
    lost: dict[int, dict[str, list[int]]] = {rid: {} for rid in names}
    held = {pid for number in range(1, through + 1) for ids in history.weeks[number].rosters.values() for pid in ids}
    for pid in sorted(held):
        card = players.get(pid)
        if card is None or card.position not in SKILL_POSITIONS:
            continue
        absences, playable = _absences(history, through, card, report_out=report_out, roster_out=roster_out,
                                       team_weeks=team_weeks)
        for weeks in absences:
            first = weeks[0]
            # The team of the week before the absence covers a drop after the game he got hurt in.
            holders = {rid for number in (first - 1, first) if number in history.weeks
                       for rid, ids in history.weeks[number].rosters.items() if pid in ids}
            for roster_id in sorted(holders & lost.keys()):
                if _key_starter(history, roster_id, pid, first, playable):
                    lost[roster_id].setdefault(pid, []).extend(weeks)
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
