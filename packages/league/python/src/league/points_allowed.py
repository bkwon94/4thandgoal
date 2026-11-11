"""
Points allowed per game per position per defense, from the weekly stat lines saved in the history.
Each defense gets a rank per position, and 1 is the most points allowed per game.
"""
import json
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel

from league.league_settings import DEFAULT_POINTS_KEY
from league.nflverse import SKILL_POSITIONS
from league.numbers import ordinal
from league.paths import history_week_dir


class PositionAllowed(BaseModel):
    # Half-PPR points per game, so a defense with its bye done does not rank better for one game fewer.
    points: float
    games: int
    # 1 is the defense that gave up the most points per game to the position. Equal points share a rank.
    rank: int


def _stat_lines(root: Path, week: int) -> list[dict] | None:
    path = history_week_dir(root, week) / "stats.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")) or None


def points_allowed(
        root: Path, through: int, points_key: str = DEFAULT_POINTS_KEY) -> dict[str, dict[str, PositionAllowed]] | None:
    """The points per game at `points_key` each defense gave up at each position in weeks 1 to `through`.

    The key is the Sleeper team code of the defense. The raw stat line names the opponent of the player,
    so the points and the games need no schedule. A week with no line for a defense is its bye.
    None when a week is missing or empty: an outage gives an empty file, and a gap would rank the defenses wrong.
    """
    # Decimals keep the sum exact, so a total shows the same digits as the stat lines.
    totals: dict[str, dict[str, Decimal]] = {}
    weeks_played: dict[str, set[int]] = {}
    for week in range(1, through + 1):
        lines = _stat_lines(root, week)
        if lines is None:
            return None
        for line in lines:
            position = (line.get("player") or {}).get("position")
            if position not in SKILL_POSITIONS or not line.get("opponent"):
                continue
            weeks_played.setdefault(line["opponent"], set()).add(week)
            by_position = totals.setdefault(line["opponent"], {p: Decimal(0) for p in SKILL_POSITIONS})
            by_position[position] += Decimal(str(line["stats"].get(points_key, 0)))
    per_game = {team: {p: by_position[p] / len(weeks_played[team]) for p in SKILL_POSITIONS}
                for team, by_position in totals.items()}
    allowed: dict[str, dict[str, PositionAllowed]] = {team: {} for team in totals}
    for position in SKILL_POSITIONS:
        for team, by_position in per_game.items():
            above = sum(other[position] > by_position[position] for other in per_game.values())
            allowed[team][position] = PositionAllowed(
                points=float(by_position[position]), games=len(weeks_played[team]), rank=above + 1)
    return allowed or None


def opponent_rank(allowed: dict[str, dict[str, PositionAllowed]], opponent: str, position: str) -> int | None:
    """The rank of the opponent in points allowed per game to the position. None when the opponent has no row."""
    row = allowed.get(opponent, {}).get(position)
    return None if row is None else row.rank


def rank_word(rank: int, teams: int) -> str:
    """The rank of a defense out of `teams` as a plain word, such as "3rd most" or "4th fewest".

    A rank in the top half counts from the most points, and a rank in the bottom half counts from the fewest.
    A high ordinal of "most points", such as "29th most", reads like a soft defense, so the bottom half never says it.
    The middle rank of an odd count reads "most". Rank 1 reads "the most" and the last rank reads "the fewest".
    """
    if rank <= (teams + 1) // 2:
        return "the most" if rank == 1 else f"{ordinal(rank)} most"
    fewest = teams - rank + 1
    return "the fewest" if fewest == 1 else f"{ordinal(fewest)} fewest"


def most_points_text(rank: int, position: str, teams: int) -> str:
    """The rank of a defense out of `teams` at a position in a manager's words, such as "3rd most points to WRs".

    Rank 1 gives up the most, so it reads "the most points to WRs", never "1st most". A rank in the bottom half reads
    from the other end, so rank 29 of 32 reads "4th fewest points to RBs". See `rank_word`.
    The schedule row, the Week line of the grade, and the sell sheet all name an opponent this way.
    """
    return f"{rank_word(rank, teams)} points to {position}s"
