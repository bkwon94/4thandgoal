"""
The analyzer route group: the teams for the trade form, and the analyze route that grades a proposed trade.
Both routes build the live snapshot through the sources on the app state, so a test swaps every fetch.
"""
from collections.abc import Callable

from fastapi import APIRouter, HTTPException, Request

from cornerstone.analysis import Analysis
from cornerstone.render import headshot_url, is_def
from cornerstone.rubric import ProposedTrade, TradeInputError, check_trade
from cornerstone.snapshot import Snapshot
from cornerstone_api.cache import cache_key

router = APIRouter()

# The answer when the week has no chart. A grade with no trade value would mislead, so the route gives none.
NO_CHART_DETAIL = "The trade value chart for this week is not available."


# The grade plus the Claude call: a proposed trade and its snapshot in, the analysis out.
Analyzer = Callable[[ProposedTrade, Snapshot], Analysis]


def _snapshot(request: Request, season: int) -> Snapshot:
    """The live snapshot for `season`. A season that Sleeper is not in is a bad input, so it is 422."""
    try:
        return request.app.state.sources.snapshot(request.app.state.settings.repo, season)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"The season {season} is not in progress.")


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
    snapshot = _snapshot(request, season)
    return {"teams": [
        {
            "roster_id": roster_id,
            "team": snapshot.teams[roster_id].name,
            "manager": snapshot.teams[roster_id].owner,
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


def result_document(trade: ProposedTrade, snapshot: Snapshot, analysis: Analysis) -> dict:
    """The result the site renders. It holds letters, steps, and reasons, and never a trade value, sum, or ratio."""
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
            "start_letter": breakdown.start_letter,
            "reason": breakdown.reason,
            "adjusters": [
                {"name": adj.name, "step": adj.step, "lean": adj.lean, "reason": adj.reason}
                for adj in breakdown.adjusters
            ],
            "final_letter": side.final_letter,
            "final_reason": side.reason,
            "analysis": side.analysis,
        }
        for breakdown, side in zip(analysis.breakdowns, analysis.sides)
    ]
    return {
        "trade": {"asker": trade.asker, "sides": echoed},
        "sides": sides,
        "verdict": {
            "for_roster": trade.asker,
            "choice": analysis.verdict.choice,
            "reason": analysis.verdict.reason,
            "differs": analysis.verdict_differs,
        },
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
        # The id lets the form mark the player who is no longer on the giving roster.
        raise HTTPException(status_code=422, detail={"message": str(error), "player_id": error.player_id})
    if snapshot.chart is None:
        raise HTTPException(status_code=503, detail=NO_CHART_DETAIL)
    cache = request.app.state.cache
    key = cache_key(trade, snapshot)
    cached = cache.get(key)
    if cached is not None:
        return cached
    analysis = request.app.state.analyzer(trade, snapshot)
    document = result_document(trade, snapshot, analysis)
    # A fallback is not stored, so the next request of the same trade tries the Claude call again.
    if not analysis.fallback:
        cache.put(key, document)
    return document
