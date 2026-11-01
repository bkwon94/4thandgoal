"""
The projections of the waiver board: the week N+1 projection and the rest of season projection of one player.
One place for the sum, so the pool and the drops bucket read a player the same way.
"""
from cornerstone.models import ProjectionsAhead
from cornerstone.numbers import r2
from cornerstone.tunables import LAST_SEASON_WEEK


def projections_ahead(raw: dict[str, object]) -> ProjectionsAhead:
    """The projections ahead file of the raw files by week. A week with no file has no projections."""
    return {entry["week"]: entry["projections"] for entry in raw.get("projections_ahead", [])}


def next_week(ahead: ProjectionsAhead, player_id: str, week: int) -> float:
    """The projection of week N+1 after week `week`. A player with none, such as on a bye, gets 0."""
    return r2(ahead.get(week + 1, {}).get(player_id, 0.0))


def rest_of_season(ahead: ProjectionsAhead, player_id: str, week: int) -> float:
    """The sum of the projections of weeks N+1 to LAST_SEASON_WEEK.

    A week with no projection, such as his bye, counts 0.
    """
    return r2(sum(ahead.get(w, {}).get(player_id, 0.0) for w in range(week + 1, LAST_SEASON_WEEK + 1)))
