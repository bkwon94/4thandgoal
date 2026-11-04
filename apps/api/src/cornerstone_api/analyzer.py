"""
The analyzer route group: the teams for the trade form, the analyze route that grades a proposed trade, and the
find route that lists the top win-win trades between two rosters.
The routes build the live snapshot through the sources on the app state, so a test swaps every fetch.
The teams route keeps its answer per season in memory for a short window, so the form fills at once.
"""
from collections.abc import Callable
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from cornerstone.adjusters import Adjuster, Lean
from cornerstone.analysis import Analysis
from cornerstone.finder import NO_WIN_WIN, FinderTrade, find_win_wins
from cornerstone.finder_reasons import FinderReasons
from cornerstone.player_ids import headshot_url, is_def
from cornerstone.rubric import ProposedTrade, TradeInputError, check_trade, fairness
from cornerstone.snapshot import Snapshot
from cornerstone_api.cache import cache_key, finder_cache_key
from cornerstone_api.errors import season_in_progress
from cornerstone_api.ratelimit import client_address

router = APIRouter()

# The line the site shows when the trade week has no chart. The grade then reads the adjusters alone.
NO_CHART_NOTE = "Week {week} has no trade value chart yet, so the chart gives neither side an edge."
# One 429 body for each full window.
GRADE_LIMIT_DETAIL = {
    "minute": "Too many grades this minute. Try again later.",
    "day": "Too many grades today. Try again tomorrow.",
}


# The grade plus the Claude call: a proposed trade and its snapshot in, the analysis out.
Analyzer = Callable[[ProposedTrade, Snapshot], Analysis]
# The Claude call of the finder sits on the app state, so a test swaps in a writer with a fake call.
ReasonWriter = Callable[[list[FinderTrade], Snapshot], FinderReasons]


def _snapshot(request: Request, season: int) -> Snapshot:
    """The live snapshot for `season`. A season that Sleeper is not in is a bad input, so it is 422."""
    with season_in_progress(season):
        return request.app.state.sources.snapshot(season)


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
        snapshot = request.app.state.sources.rosters_snapshot(season)
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
        "completed_through": stamps.completed_through,
        "rosters_fetched": stamps.rosters_fetched.isoformat() if stamps.rosters_fetched else None,
        # The week N games that the player stats read. None when the grade reads no week N game.
        "known_games": stamps.known_games.model_dump() if stamps.known_games else None,
        # The chart site posts the new chart hours after the trade week starts. The grade runs in that window too,
        # so the document says the week has no chart, and the site shows the note with no words of its own.
        "no_chart": snapshot.chart is None,
        "no_chart_note": NO_CHART_NOTE.format(week=snapshot.week) if snapshot.chart is None else None,
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


def _echoed_sides(trade: ProposedTrade, snapshot: Snapshot) -> list[dict]:
    """Each side of the trade as the site shows it: the roster, the team, and the players it gives and gets."""
    # The analyze document and the finder document share this shape, so the site renders a side one way.
    # Each given player carries `to` and each got player carries `from`, so the site can tag a player by team.
    givers = trade.givers
    return [
        {
            "roster_id": side.roster_id,
            "team": snapshot.teams[side.roster_id].name,
            "gives": [{**_player(snapshot, player.player_id), "to": player.to} for player in side.gives],
            "gets": [{**_player(snapshot, pid), "from": givers[pid]} for pid in trade.gets(side.roster_id)],
        }
        for side in trade.sides
    ]


def result_document(trade: ProposedTrade, snapshot: Snapshot, analysis: Analysis) -> dict:
    """The result the site renders: a decision first, the fairness, then the analysis, chart lean, and factors per side.

    It holds no letter, no step, and never a trade value, sum, or ratio. A manager acts on a decision, not a letter.
    """
    echoed = _echoed_sides(trade, snapshot)
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
    # The fairness reads the letters that stand after the Claude call, the same letters the verdict that stands
    # comes with. The document drops the letters, so this function builds the block and a stored document cannot.
    fairness_result = fairness(analysis.standing_letters, analysis.breakdowns)
    return {
        "trade": {"asker": trade.asker, "sides": echoed},
        "decision": {
            "for_roster": trade.asker,
            "answer": ANSWERS[analysis.verdict.choice],
            "reason": analysis.verdict.reason,
            "differs": analysis.verdict_differs,
        },
        # The fairness is for every side, after the decision, so the asker's own answer stays the lead.
        "fairness": fairness_result.model_dump(mode="json"),
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
    cache = request.app.state.cache
    key = cache_key(trade, snapshot)
    cached = cache.get(key)
    if cached is not None:
        return cached
    # The count comes after the cache, because a cached repeat makes no Claude call and costs nothing.
    _count_grade(request)
    analysis = request.app.state.analyzer(trade, snapshot)
    document = result_document(trade, snapshot, analysis)
    # A fallback is not stored, so the next request of the same trade tries the Claude call again.
    if not analysis.fallback:
        cache.put(key, document)
    return document


def _count_grade(request: Request) -> None:
    """Count one grade for the client, or stop the request with a 429 past the minute or the day limit."""
    # The analyze route and the find route share it, so a finder call costs one grade, as a trade does.
    limited = request.app.state.grade_limiter.hit(client_address(request))
    if limited is not None:
        raise HTTPException(status_code=429, detail=GRADE_LIMIT_DETAIL[limited.window],
                            headers={"Retry-After": str(limited.retry_after)})


class FindRequest(BaseModel):
    """The body of the find route: the season, the roster that asks, and the partner roster."""

    season: int
    asker: int
    partner: int


def _team(snapshot: Snapshot, roster_id: int) -> dict:
    """One roster of the pair as the finder document shows it: the roster id and the team name."""
    return {"roster_id": roster_id, "team": snapshot.teams[roster_id].name}


def finder_document(pair: FindRequest, snapshot: Snapshot, found: list[FinderTrade], reasons: FinderReasons) -> dict:
    """The finder result the site renders: the season, the two teams, the trades, and the as-of stamps.

    Each trade holds its sides, its fairness, and its reason. A reason is null after a fallback.
    Each item's sides and fairness have the shape of the analyze document, so the site renders them the same way.
    An empty list carries the line that no swap is good for both, so the page needs no words of its own.
    """
    trades = [
        {
            "sides": _echoed_sides(item.trade, snapshot),
            "fairness": item.fairness.model_dump(mode="json"),
            "reason": reason,
        }
        for item, reason in zip(found, reasons.reasons)
    ]
    return {
        # The site calls the analyze route per card, and that route needs the season with the pair and the sides.
        "season": pair.season,
        "trade_pair": {"asker": _team(snapshot, pair.asker), "partner": _team(snapshot, pair.partner)},
        "trades": trades,
        # The key is always there, so the document keeps one shape with a list and without one.
        "empty": None if trades else NO_WIN_WIN,
        "as_of": _as_of(snapshot),
        "fallback": reasons.fallback,
        "missing": list(snapshot.missing),
        "stale": list(snapshot.stale),
    }


@router.post("/find")
def find(request: Request, pair: FindRequest) -> dict:
    """List the top win-win trades between the asker and the partner on the live snapshot, each with one reason."""
    # The same roster twice needs no snapshot, so it fails before the load runs. The teams cache stays.
    if pair.asker == pair.partner:
        raise HTTPException(status_code=422, detail={"message": "Pick two different teams."})
    snapshot = _snapshot(request, pair.season)
    gone = [roster_id for roster_id in (pair.asker, pair.partner) if roster_id not in snapshot.rosters]
    if gone:
        # The form showed a roster that Sleeper no longer has, so the next teams request builds from Sleeper again.
        request.app.state.teams_cache.clear(pair.season)
        # The same words as check_trade, so the form shows one message for a roster that is gone.
        raise HTTPException(status_code=422, detail={"message": f"Roster {gone[0]} is not in the league"})
    cache = request.app.state.cache
    key = finder_cache_key(pair.season, pair.asker, pair.partner, snapshot)
    cached = cache.get(key)
    if cached is not None:
        return cached
    # The count comes after the cache, because a cached repeat runs no finder and makes no Claude call.
    _count_grade(request)
    found = find_win_wins(pair.asker, pair.partner, snapshot)
    reasons = request.app.state.finder_reasons(found, snapshot)
    document = finder_document(pair, snapshot, found, reasons)
    # A fallback is not stored, so the next request of the same pair tries the Claude call again.
    if not reasons.fallback:
        cache.put(key, document)
    return document
