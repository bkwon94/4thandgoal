"""
The players to watch, a chapter of Act III: Due to rise and Due to fall from the Expected gap over the whole season,
and Grab him now from the projections of the rest of the regular season. Decision 10, "Players to watch".
"""
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, ExpectedGame, Fact, History
from league.numbers import r2
from midseason.players import SKILL_POSITIONS, PlayerCard, league_points

# Each list names 3 players.
WATCH_SIZE = 3
# A player needs this many games with expected points and a stat line for Due to rise or Due to fall.
MIN_GAMES = 4


class GapPlayer(BaseModel):
    """A player of Due to rise or Due to fall."""
    player_id: str
    name: str
    position: str
    nfl_team: str | None
    # The Expected gap per game over the season: his points minus his expected points. Under zero is under expected.
    gap: float
    games: int
    roster_id: int
    manager: str


class GrabPlayer(BaseModel):
    """A free agent of Grab him now."""
    player_id: str
    name: str
    position: str
    nfl_team: str | None
    # The sum of his projections for the weeks after the report week, through the last regular week.
    projection: float
    # Always None: Grab him now names free agents only. The field keeps the row shape of the other lists.
    roster_id: None = None


class PlayersToWatch(BaseModel):
    """The facts of the players to watch: the three lists."""
    due_to_rise: list[GapPlayer]
    due_to_fall: list[GapPlayer]
    grab_him_now: list[GrabPlayer]


class WatchChapter(BaseModel):
    """The players to watch chapter of Act III."""
    key: Literal["watch"] = "watch"
    title: str = "Players to watch"
    facts: PlayersToWatch
    blurb: Blurb | None = None
    roast: Blurb | None = None


def _season_gaps(
    history: History, through: int, scoring: Mapping[str, float], expected: Mapping[str, Sequence[ExpectedGame]],
) -> dict[str, tuple[Decimal, int]]:
    """The mean Expected gap and the games of each player with MIN_GAMES or more games, weeks 1 to `through`.

    A game counts when the file has its expected points and the league has his stat line of that week.
    """
    out = {}
    for pid, games in expected.items():
        gaps = [league_points(history.weeks[g.week].stats[pid], scoring) - Decimal(str(g.expected))
                for g in games if g.week <= through and pid in history.weeks[g.week].stats]
        if len(gaps) >= MIN_GAMES:
            out[pid] = (sum(gaps, Decimal(0)) / len(gaps), len(gaps))
    return out


def players_to_watch(
    history: History, through: int, players: Mapping[str, PlayerCard], scoring: Mapping[str, float],
    expected: Mapping[str, Sequence[ExpectedGame]], owners: Mapping[str, int], names: Mapping[int, str], *,
    ahead: Mapping[int, Mapping[str, float]], last_regular_week: int, positions: Sequence[str],
) -> PlayersToWatch:
    """The three lists of the report of week `through`.

    The ports come from the app: `expected` holds the expected points of each game by Sleeper ID, `owners` the
    roster ID of each rostered player now, and `ahead` the projection of each player by week. Due to rise and Due to
    fall name rostered QB, RB, WR, and TE. Grab him now names free agents at `positions`, the positions the league
    starts.
    """
    gaps = _season_gaps(history, through, scoring, expected)
    rostered = [pid for pid in gaps if pid in owners and pid in players
                and players[pid].position in SKILL_POSITIONS]

    def gap_row(pid: str) -> GapPlayer:
        card, (gap, games) = players[pid], gaps[pid]
        return GapPlayer(player_id=pid, name=card.name, position=card.position, nfl_team=card.nfl_team,
                         gap=r2(float(gap)), games=games, roster_id=owners[pid], manager=names[owners[pid]])

    rise = sorted((pid for pid in rostered if gaps[pid][0] < 0), key=lambda pid: (gaps[pid][0], players[pid].name))
    fall = sorted((pid for pid in rostered if gaps[pid][0] > 0), key=lambda pid: (-gaps[pid][0], players[pid].name))

    projection: dict[str, Decimal] = {}
    for number in range(through + 1, last_regular_week + 1):
        for pid, points in ahead.get(number, {}).items():
            projection[pid] = projection.get(pid, Decimal(0)) + Decimal(str(points))
    free = sorted((pid for pid in projection if pid not in owners and pid in players
                   and players[pid].position in positions),
                  key=lambda pid: (-projection[pid], players[pid].name))
    return PlayersToWatch(
        due_to_rise=[gap_row(pid) for pid in rise[:WATCH_SIZE]],
        due_to_fall=[gap_row(pid) for pid in fall[:WATCH_SIZE]],
        grab_him_now=[GrabPlayer(player_id=pid, name=players[pid].name, position=players[pid].position,
                                 nfl_team=players[pid].nfl_team, projection=r2(float(projection[pid])))
                      for pid in free[:WATCH_SIZE]],
    )


def watch_facts(watch: PlayersToWatch) -> list[Fact]:
    """The facts of the players to watch: each player of the three lists with the number behind him."""
    facts = []
    for label, rows in (("rise", watch.due_to_rise), ("fall", watch.due_to_fall)):
        # The voice bans the phrase "expected points", so the fact says what the volume says.
        side = "under" if label == "rise" else "over"
        for place, row in enumerate(rows, start=1):
            n = Nums()
            facts.append(fact(f"PW.{label}.{place}",
                              f"{row.name} of {row.manager} scores {n(abs(row.gap))} points per game {side} what his "
                              f"volume says, over {n(row.games)} games, so he is due to {label}.",
                              n, [row.manager], [row.name]))
    for place, row in enumerate(watch.grab_him_now, start=1):
        n = Nums()
        facts.append(fact(f"PW.grab.{place}",
                          f"{row.name} is a free agent with {n(row.projection)} projected points through the regular "
                          "season.", n, [], [row.name]))
    return facts
