"""
Points allowed per position per defense, from the weekly stat lines saved in the history.
Each defense gets a rank per position, and 1 is the most points allowed.
"""
import json
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel

from cornerstone.history import history_dir

POSITIONS = ("QB", "RB", "WR", "TE")


class PositionAllowed(BaseModel):
    points: float
    # 1 is the defense that gave up the most half-PPR points to the position. Equal points share a rank.
    rank: int


def _stat_lines(root: Path, week: int) -> list[dict] | None:
    path = history_dir(root, week) / "stats.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")) or None


def points_allowed(root: Path, through: int) -> dict[str, dict[str, PositionAllowed]] | None:
    """The half-PPR points each defense gave up at each position in weeks 1 to `through`.

    The key is the Sleeper team code of the defense. The raw stat line names the opponent of the player,
    so the points need no schedule. None when a week is missing or empty: an outage gives an empty
    file, and a total over a gap would rank the defenses wrong.
    """
    # Decimals keep the sum exact, so a total shows the same digits as the stat lines.
    totals: dict[str, dict[str, Decimal]] = {}
    for week in range(1, through + 1):
        lines = _stat_lines(root, week)
        if lines is None:
            return None
        for line in lines:
            position = (line.get("player") or {}).get("position")
            if position not in POSITIONS or not line.get("opponent"):
                continue
            by_position = totals.setdefault(line["opponent"], {p: Decimal(0) for p in POSITIONS})
            by_position[position] += Decimal(str(line["stats"].get("pts_half_ppr", 0)))
    allowed: dict[str, dict[str, PositionAllowed]] = {team: {} for team in totals}
    for position in POSITIONS:
        for team, by_position in totals.items():
            above = sum(other[position] > by_position[position] for other in totals.values())
            allowed[team][position] = PositionAllowed(points=float(by_position[position]), rank=above + 1)
    return allowed or None
