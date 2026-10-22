"""
The analyzer route group: the teams for the trade form, and the analyze route that grades a proposed trade.
Both routes build the live snapshot through the sources on the app state, so a test swaps every fetch.
The teams route keeps its answer per season in memory for a short window, so the form fills at once.
"""
from collections.abc import Callable
from typing import Literal

from fastapi import APIRouter, HTTPException, Request

from cornerstone.adjusters import Adjuster, Lean
from cornerstone.analysis import Analysis
from cornerstone.render import headshot_url, is_def
from cornerstone.rubric import ProposedTrade, TradeInputError, check_trade
from cornerstone.snapshot import Snapshot
from cornerstone_api.cache import cache_key
from cornerstone_api.errors import season_in_progress
from cornerstone_api.ratelimit import client_address

router = APIRouter()

# The answer when the week has no chart. A grade with no trade value would mislead, so the route gives none.
NO_CHART_DETAIL = "The trade value chart for this week is not available."
# One 429 body for each full window.
GRADE_LIMIT_DETAIL = {
    "minute": "Too many grades this minute. Try again later.",
    "day": "Too many grades today. Try again tomorrow.",
}


# The grade plus the Claude call: a proposed trade and its snapshot in, the analysis out.
Analyzer = Callable[[ProposedTrade, Snapshot], Analysis]


def _snapshot(request: Request, season: int) -> Snapshot:
    """The live snapshot for `season`. A season that Sleeper is not in is a bad input, so it is 422."""
    with season_in_progress(season):
        return request.app.state.sources.snapshot(request.app.state.settings.repo, season)


def _player(snapshot: Snapshot, player_id: str) -> dict:
    """A rostered player as the site shows him: the name, the position, the NFL team, and the headshot URL."""
    player = snapshot.players[player_id]
    return {
        "player_id": player_id,
        "name": player.name,
        "position": player.position,
        "nfl_team": player.nfl_team,
        "headshot": headshot_url(player_id, is_def(player_id)),
    }


@router.get("/teams")
def teams(request: Request, season: int) -> dict:
    """Each roster of the league with its team name, its manager, and its players, for the trade form."""
    return request.app.state.teams_cache.get_or_build(season, lambda: _teams(request, season))


def _teams(request: Request, season: int) -> dict:
    """The teams answer built from a live Sleeper fetch."""
    # The form needs the rosters and not the chart or the slow sources, so the route skips their refresh and the
    # history save. The daily cron and the start-up refresh keep the slow sources fresh.
    with season_in_progress(season):
        snapshot = request.app.state.sources.rosters_snapshot(request.app.state.settings.repo, season)
    return {"teams": [
        {
            "roster_id": roster_id,
            "team": snapshot.teams[roster_id].name,
            "manager": snapshot.teams[roster_id].owner,
            # The form shows the avatar next to the team name.
            "avatar": snapshot.teams[roster_id].avatar_url,
            "players": [_player(snapshot, pid) for pid in players],
        }
        for roster_id, players in sorted(snapshot.rosters.items())
    ]}


def _as_of(snapshot: Snapshot) -> dict:
    """The as-of stamps of the snapshot as the document shows them."""
    stamps = snapshot.as_of
    return {
        "chart_week": stamps.chart_week,
        "stats_through": stamps.stats_through,
        "rosters_fetched": stamps.rosters_fetched.isoformat() if stamps.rosters_fetched else None,
    }


# The decision a manager acts on, from the verdict choice of the rubric.
Answer = Literal["yes", "no", "not_as_is"]
ANSWERS: dict[str, Answer] = {"accept": "yes", "decline": "no", "counter": "not_as_is"}
# The chart lean of a side, from its start letter. No letter reaches the document.
ChartLean = Literal["more", "even", "less"]
CHART_LEANS: dict[str, ChartLean] = {"A": "more", "B": "more", "C": "even", "D": "less", "F": "less"}


def _factor_lean(adjuster: Adjuster) -> Lean:
    """The lean of one adjuster. The schedule never steps, so it keeps its own lean."""
    if adjuster.lean is not None:
        return adjuster.lean
    return "for" if adjuster.step > 0 else "against" if adjuster.step < 0 else "even"


def result_document(trade: ProposedTrade, snapshot: Snapshot, analysis: Analysis) -> dict:
    """The result the site renders: a decision first, then the analysis, the chart lean, and the factors per side.

    It holds no letter, no step, and never a trade value, sum, or ratio. A manager acts on a decision, not a letter.
    """
    a, b = trade.sides
    echoed = [
        {
            "roster_id": side.roster_id,
            "team": snapshot.teams[side.roster_id].name,
            "gives": [_player(snapshot, pid) for pid in side.gives],
            "gets": [_player(snapshot, pid) for pid in other.gives],
        }
        for side, other in ((a, b), (b, a))
    ]
    sides = [
        {
            "roster_id": breakdown.roster_id,
            "analysis": side.analysis,
            "chart": {"lean": CHART_LEANS[breakdown.start_letter], "reason": breakdown.reason},
            "factors": [
                {"name": adj.name, "lean": _factor_lean(adj), "reason": adj.reason}
                for adj in breakdown.adjusters
            ],
        }
        for breakdown, side in zip(analysis.breakdowns, analysis.sides)
    ]
    return {
        "trade": {"asker": trade.asker, "sides": echoed},
        "decision": {
            "for_roster": trade.asker,
            "answer": ANSWERS[analysis.verdict.choice],
            "reason": analysis.verdict.reason,
            "differs": analysis.verdict_differs,
        },
        "sides": sides,
        "as_of": _as_of(snapshot),
        "fallback": analysis.fallback,
        "missing": list(snapshot.missing),
        "stale": list(snapshot.stale),
    }


@router.post("/analyze")
def analyze(request: Request, trade: ProposedTrade) -> dict:
    """Grade the proposed trade on the live snapshot and return the result document."""
    snapshot = _snapshot(request, trade.season)
    try:
        check_trade(trade, snapshot)
    except TradeInputError as error:
        # The form showed a roster that Sleeper no longer has, so the next teams request builds from Sleeper again.
        request.app.state.teams_cache.clear(trade.season)
        # The id lets the form mark the player who is no longer on the giving roster.
        raise HTTPException(status_code=422, detail={"message": str(error), "player_id": error.player_id})
    if snapshot.chart is None:
        raise HTTPException(status_code=503, detail=NO_CHART_DETAIL)
    cache = request.app.state.cache
    key = cache_key(trade, snapshot)
    cached = cache.get(key)
    if cached is not None:
        return cached
    # The count comes after the cache, because a cached repeat makes no Claude call and costs nothing.
    limited = request.app.state.grade_limiter.hit(client_address(request))
    if limited is not None:
        raise HTTPException(status_code=429, detail=GRADE_LIMIT_DETAIL[limited.window],
                            headers={"Retry-After": str(limited.retry_after)})
    analysis = request.app.state.analyzer(trade, snapshot)
    document = result_document(trade, snapshot, analysis)
    # A fallback is not stored, so the next request of the same trade tries the Claude call again.
    if not analysis.fallback:
        cache.put(key, document)
    return document
