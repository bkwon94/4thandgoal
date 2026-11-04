"""
The refresh route group: one route that refreshes the slow sources and the chart of the trade window now.
A daily cron pings it, because a stopped Fly machine cannot run a scheduler inside the service.
"""
from fastapi import APIRouter, Request

from cornerstone_api.errors import season_in_progress

router = APIRouter()


@router.post("/refresh")
def refresh(request: Request, season: int) -> dict[str, list[str]]:
    """Refresh what the live snapshot reads. Return what the run fetched again and what is still stale."""
    # The cron can start late, so the route fetches every file again, even one 23 hours old.
    with season_in_progress(season):
        result = request.app.state.sources.refresh(season, max_age_seconds=0)
    stale = list(result.stale)
    # The snapshot lists a missing chart as missing, not stale. The cron log must show it, so the route adds it here.
    # A chart read that raised is in the stale list already, so the route does not add it twice.
    if result.chart is None and "chart" not in stale:
        stale.append("chart")
    return {"refreshed": result.refreshed, "stale": stale}
