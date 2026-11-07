"""
The shared reads of the waiver and the trade chapters: the score at the line of each position each week, the starts
of one stint of a player on a roster. GLOSSARY.md, "Points over the line".
"""
from collections.abc import Mapping
from decimal import Decimal

from pydantic import BaseModel

from league.history import player_points
from league.models import History, PastWeek
from league.numbers import r2


class Stint(BaseModel):
    """The weeks of one player on one roster: the weeks he sat on it, his starts, his Points over the line, and the
    wins that his points swung."""
    weeks: list[int]
    starts: int
    # The points of each start, so the streaming king reads them for a position with no line.
    points: float
    # None for a position with no line, such as K and DEF.
    points_over_line: float | None
    swung_wins: int


def line_scores(history: History, lines: Mapping[str, int], through: int) -> dict[int, dict[str, float]]:
    """The score at the line of each position with a line, by week: the points of the player at that rank of the
    week, over every NFL player with a stat line, in the league scoring."""
    out: dict[int, dict[str, float]] = {}
    for number in range(1, through + 1):
        past = history.weeks[number]
        by_position: dict[str, list[float]] = {}
        for pid, position in past.positions.items():
            points = player_points(past, pid)
            if points is not None and position in lines:
                by_position.setdefault(position, []).append(points)
        out[number] = {
            position: sorted(scores, reverse=True)[lines[position] - 1]
            for position, scores in by_position.items() if len(scores) >= lines[position]
        }
    return out


def _won_by(past: PastWeek, roster_id: int) -> float | None:
    """The margin of the head-to-head win of the roster in the week, or None when it did not win."""
    for a, b in past.pairs:
        if roster_id in (a, b):
            other = b if roster_id == a else a
            margin = Decimal(str(past.scores[roster_id])) - Decimal(str(past.scores[other]))
            return float(margin) if margin > 0 else None
    return None


def stint(
    history: History, line_at: Mapping[int, Mapping[str, float]], player_id: str, position: str, roster_id: int,
    start: int, through: int,
) -> Stint:
    """The stint of the player on the roster from week `start` to week `through` at most.

    The stint ends at the first week he is off the roster after a week on it. A player who is not on the roster in
    `start` or the week after never joined it in a week with games, so his stint has no week.
    """
    weeks: list[int] = []
    starts = 0
    points = Decimal(0)
    over = Decimal(0)
    swung = 0
    has_line = True
    for number in range(start, through + 1):
        past = history.weeks[number]
        if player_id not in past.rosters.get(roster_id, []):
            if weeks or number > start:
                break
            continue
        weeks.append(number)
        if player_id not in past.starters.get(roster_id, []):
            continue
        scored = player_points(past, player_id) or 0.0
        starts += 1
        points += Decimal(str(scored))
        line = line_at.get(number, {}).get(position)
        if line is None:
            has_line = False
        else:
            over += Decimal(str(scored)) - Decimal(str(line))
        margin = _won_by(past, roster_id)
        if margin is not None and scored > margin:
            swung += 1
    return Stint(weeks=weeks, starts=starts, points=r2(float(points)),
                 points_over_line=r2(float(over)) if has_line else None, swung_wins=swung)
