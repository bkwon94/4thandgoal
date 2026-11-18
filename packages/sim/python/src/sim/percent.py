"""
The rule of the shown odds of the season sim, and its percent helpers. The team odds, the swings, and the page block
all read one rule, so a number of the page and a number of the rankings agree.
"""
from league.models import OddsStatus


def shown(status: OddsStatus, count: float, runs: float, weeks_left: int) -> int:
    """The odds as the weekly odds show them: 100 for `in`, 0 for `out`, else the whole percent clamped to 1 to 99.
    With no regular week left, the table is final, so the whole percent stands with no clamp."""
    if not weeks_left:
        return percent(count, runs)
    if status == "in":
        return 100
    if status == "out":
        return 0
    return min(99, max(1, percent(count, runs)))


def percent(part: float, total: float) -> int:
    """`part` over `total` as a whole percent, rounded half up. A whole count gives the exact integer result."""
    return int((200 * part + total) // (2 * total))


def tenths(part: float, total: float) -> float:
    """`part` over `total` as a percent with one decimal."""
    return round(100 * part / total, 1)
