"""
The projections ahead of the waiver board, by week, from the raw files. The week N+1 and the rest of season sums of
one player live in league.projection, so the pool, the drops bucket, and the API read a player the same way.
"""
from league.models import ProjectionsAhead
from league.provider.raw import RawWeek


def projections_ahead(raw: RawWeek) -> ProjectionsAhead:
    """The projections ahead file of the raw files by week. A week with no file has no projections."""
    return {entry.week: entry.projections for entry in raw.projections_ahead or []}
