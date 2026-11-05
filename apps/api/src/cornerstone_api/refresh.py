"""
The refresh route group: one route that refreshes the slow sources and the chart of the trade window now.
A daily cron pings it for each client, because a stopped Fly machine cannot run a scheduler inside the service.
"""
from fastapi import APIRouter, Request

from analyzer.errors import season_in_progress
from analyzer.routes import ServedClient

router = APIRouter()


@router.post("/refresh")
def refresh(request: Request, season: int, served: ServedClient) -> dict[str, list[str]]:
    """Refresh what the live snapshot reads. Return what the run fetched again and what is still stale."""
    # The cron can start late, so the route fetches every file again, even one 23 hours old.
    with season_in_progress(season):
        # The app keeps the Sources of each client by slug, so the refresh runs the fetches of the client of the path.
        result = request.app.state.sources[served.client.slug].refresh(season, max_age_seconds=0)
    stale = list(result.stale)
    # The snapshot lists a missing chart as missing, not stale. The cron log must show it, so the route adds it here.
    # A chart read that raised is in the stale list already, so the route does not add it twice.
    if result.chart is None and "chart" not in stale:
        stale.append("chart")
    return {"refreshed": result.refreshed, "stale": stale}
