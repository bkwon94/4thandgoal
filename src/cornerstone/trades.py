"""
The trades of one week: the time window that picks them and the late-trade test.
A trade belongs to the page of the week whose build first saw it, not to Sleeper's leg.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from cornerstone.models import Trade, Week

EASTERN = ZoneInfo("America/New_York")


def default_cutoff(season_start: date, week: int) -> datetime:
    """08:00 on the Tuesday after week N-1. It is the start of the window when no fetch time is saved."""
    tuesday = season_start + timedelta(days=6 + 7 * (week - 2))
    return datetime(tuesday.year, tuesday.month, tuesday.day, 8, 0, tzinfo=EASTERN)


def previous_fetch_time(repo: Path, season: int, week: int) -> datetime | None:
    """The fetch time that the build of week N-1 saved in its verify.json."""
    # The import is local because pipeline imports this module.
    from cornerstone.pipeline import read_verify, week_dir

    path = week_dir(repo, season, week - 1) / "verify.json"
    if not path.exists():
        return None
    record = read_verify(path).build
    return record.fetched if record else None


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
