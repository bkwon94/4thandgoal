"""
The trades of one week: the time window that picks them and the late-trade test.
A trade belongs to the week whose calendar span holds it: after the Tuesday cutoff that opens
the week, up to and including the Tuesday cutoff that opens the next. Build time plays no part.
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from cornerstone.models import Trade, Week

EASTERN = ZoneInfo("America/New_York")


def default_cutoff(season_start: date, week: int) -> datetime:
    """08:00 on the Tuesday after week N-1. It opens the window of week N and closes the window of week N-1."""
    tuesday = season_start + timedelta(days=6 + 7 * (week - 2))
    return datetime(tuesday.year, tuesday.month, tuesday.day, 8, 0, tzinfo=EASTERN)


def trades_for_week(
    this_week: list[Trade],
    last_week: list[Trade],
    after: datetime,
    until: datetime,
) -> list[Trade]:
    """The trades with after < created <= until, once each, oldest first."""
    unique = {t.transaction_id: t for t in [*last_week, *this_week]}
    chosen = [t for t in unique.values() if after < t.created <= until]
    return sorted(chosen, key=lambda t: t.created)


def is_late(trade: Trade, week: Week) -> bool:
    """True when a moved player is in this week's lines of the roster that gave him.

    The trade then happened after his game, so his points went to the old roster.
    """
    lines = {
        side.roster_id: {line.player_id for line in side.lines}
        for matchup in week.matchups
        for side in (matchup.a, matchup.b)
    }
    return any(player_id in lines.get(giver, set()) for player_id, giver in trade.drops.items())
