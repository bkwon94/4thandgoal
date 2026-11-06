"""
The player card of the midseason report: the name, the position, and the NFL team of one player by Sleeper ID, and the
points of a stat line in the league's own scoring. The app builds each card from the players file it reads.
"""
from collections.abc import Mapping
from decimal import Decimal

from pydantic import BaseModel

from league.numbers import r2

# The positions of the Key starter rule and of the expected gap. GLOSSARY.md, "Key starter" and "Due to rise".
SKILL_POSITIONS = ("QB", "RB", "WR", "TE")


class PlayerCard(BaseModel):
    """One player as the report names him."""
    player_id: str
    name: str
    position: str
    # None for a free agent of the NFL.
    nfl_team: str | None = None


def league_points(stats: Mapping[str, float], scoring: Mapping[str, float]) -> Decimal:
    """The points of one stat line in the league's own scoring, to the cent.

    Each stat counts at its weight in the scoring settings, so a free agent scores as a rostered player does.
    """
    total = sum((Decimal(str(value)) * Decimal(str(scoring[key])) for key, value in stats.items() if key in scoring),
                Decimal(0))
    return Decimal(str(r2(float(total))))
