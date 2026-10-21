"""
The refresh route group: one route that refreshes the slow sources and the chart of the trade window now.
A daily cron pings it, because a stopped Fly machine cannot run a scheduler inside the service.
"""
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.post("/refresh")
def refresh(request: Request, season: int) -> dict[str, list[str]]:
    """Refresh what the live snapshot reads. Return what the run fetched again and what is still stale."""
    try:
        done = request.app.state.sources.refresh(request.app.state.settings.repo, season)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"The season {season} is not in progress.")
    stale = list(done.stale)
    # The snapshot lists a missing chart as missing, not stale. The cron log must show it, so the route adds it here.
    if done.chart is None:
        stale.append("chart")
    return {"refreshed": done.refreshed, "stale": stale}
