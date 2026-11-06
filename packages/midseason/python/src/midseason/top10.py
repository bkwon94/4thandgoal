"""
Position top 10, a chapter of Act I: the 10 players with the most points at each position the league starts, weeks 1
to the report week, in the league's own scoring. GLOSSARY.md, "Position top 10". Every NFL player counts.
"""
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Blurb, History
from league.numbers import r2
from midseason.blocks import ProseBlock
from midseason.players import PlayerCard, league_points

BOARD_SIZE = 10
# The tag of a player on no roster now, in place of a manager. Decision 10, "Position top 10".
FREE_AGENT = "Free agent"


class TopPlayer(BaseModel):
    """One row of a position board."""
    rank: int
    player_id: str
    name: str
    position: str
    nfl_team: str | None
    points: float
    # The weeks with a game played. A bye or a missed game is no game.
    games: int
    points_per_game: float
    # The team that rosters him now. None, with the tag, for a free agent.
    roster_id: int | None
    manager: str | None
    tag: str | None


class PositionBoard(BaseModel):
    position: str
    players: list[TopPlayer]


class PositionTop10(BaseModel):
    """The facts of Position top 10: one board per position the league starts, in lineup order."""
    positions: list[PositionBoard]


class Top10Chapter(BaseModel):
    """The Position top 10 chapter of Act I."""
    key: Literal["top10"] = "top10"
    title: str = "Position top 10"
    facts: PositionTop10
    blurb: Blurb | None = None
    roast: Blurb | None = None


def season_points(
    history: History, through: int, scoring: Mapping[str, float],
) -> tuple[dict[str, Decimal], dict[str, int]]:
    """The points of each player with a stat line in weeks 1 to `through`, and his games, by Sleeper ID.

    A game is a week whose stat line has a game played. A stat line with no `gp` stat still counts its points.
    """
    points: dict[str, Decimal] = {}
    games: dict[str, int] = {}
    for number in range(1, through + 1):
        for pid, stats in history.weeks[number].stats.items():
            points[pid] = points.get(pid, Decimal(0)) + league_points(stats, scoring)
            games[pid] = games.get(pid, 0) + (1 if stats.get("gp", 0.0) > 0 else 0)
    return points, games


def position_top10(
    history: History, through: int, players: Mapping[str, PlayerCard], scoring: Mapping[str, float],
    positions: Sequence[str], owners: Mapping[str, int], names: Mapping[int, str],
) -> PositionTop10:
    """The boards of weeks 1 to `through`, one per position of `positions`, the positions the league starts.

    `owners` maps each rostered player to his roster ID now. The app hands it in from the rosters now, so a player
    a manager dropped after the report week shows as a free agent.
    """
    points, games = season_points(history, through, scoring)
    boards = []
    for position in positions:
        pool = sorted((pid for pid in points if pid in players and players[pid].position == position),
                      key=lambda pid: (-points[pid], players[pid].name))[:BOARD_SIZE]
        rows = []
        for place, pid in enumerate(pool, start=1):
            card, owner = players[pid], owners.get(pid)
            played = games[pid]
            rows.append(TopPlayer(
                rank=place, player_id=pid, name=card.name, position=card.position, nfl_team=card.nfl_team,
                points=r2(float(points[pid])), games=played,
                points_per_game=r2(float(points[pid] / played)) if played else 0.0,
                roster_id=owner, manager=names.get(owner) if owner is not None else None,
                tag=None if owner is not None else FREE_AGENT))
        boards.append(PositionBoard(position=position, players=rows))
    return PositionTop10(positions=boards)


# The writer reads the top 3 of each board. The table on the page shows all 10.
PROSE_RANKS = 3


def top10_prose(top: PositionTop10) -> ProseBlock:
    """The facts of Position top 10: the top rows of each board, with the manager now or the free agent tag. A fact
    holds 2 numbers, the most a sentence may hold, so the points per game stay on the page only."""
    facts = []
    for board in top.positions:
        for row in board.players[:PROSE_RANKS]:
            n = Nums()
            who = f"rostered by {row.manager}" if row.manager else "a free agent"
            facts.append(fact(f"TOP.{board.position}.{row.rank}",
                              f"{row.name} is the {board.position} #{n(row.rank)} with {n(row.points)} points, {who}.",
                              n, [row.manager] if row.manager else [], [row.name]))
    return ProseBlock(key="top10", title="Position top 10", facts=facts,
                      teams=sorted({f.teams[0] for f in facts if f.teams}),
                      players=[f.players[0] for f in facts])
