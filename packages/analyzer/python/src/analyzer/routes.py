"""
The analyzer route group of the API: the teams for the trade form, the analyze route, and the find route.
The app mounts it at /clients/<slug>/ for each client it serves. Each route reads the Served client of its path.
The routes build the live snapshot through the sources of the client, so a test swaps every fetch.
The teams route keeps its answer per season in memory for a short window, so the form fills at once.
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Literal, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from analyzer.adjusters import Adjuster, Lean
from analyzer.analysis import Analysis
from analyzer.cache import ResultCache, TeamsCache, cache_key, finder_cache_key
from analyzer.errors import season_in_progress
from analyzer.finder import NO_WIN_WIN, FinderTrade, find_win_wins
from analyzer.finder_reasons import FinderReasons
from analyzer.ratelimit import GradeLimiter, request_address
from analyzer.rubric import (
    NO_CHART_NOTE,
    Breakdown,
    ProposedTrade,
    TradeInputError,
    check_trade,
    deal_reason,
    fairness,
)
from analyzer.trade_facts import shown_ranks
from analyzer.week_line import week_lines
from league.client import Client
from league.player_ids import headshot_url, is_def
from league.snapshot import Snapshot

router = APIRouter()

# One 429 body for each full window.
GRADE_LIMIT_DETAIL = {
    "minute": "Too many grades this minute. Try again later.",
    "day": "Too many grades today. Try again tomorrow.",
}


# The grade plus the Claude call: a proposed trade and its snapshot in, the analysis out.
Analyzer = Callable[[ProposedTrade, Snapshot], Analysis]
# The Claude call of the finder sits on the app state, so a test swaps in a writer with a fake call.
ReasonWriter = Callable[[list[FinderTrade], Snapshot], FinderReasons]


class SnapshotSource(Protocol):
    """The live snapshots of one client. The API app gives its Sources, and a test gives fixture-backed ones."""

    def snapshot(self, season: int) -> Snapshot: ...

    def rosters_snapshot(self, season: int) -> Snapshot: ...


@dataclass(frozen=True)
class Served:
    """One client that the API serves, with its own sources, result cache, teams cache, and grade limit.

    Each client has its own of each, so the roster ids, the grades, and the limit of one league never reach another.
    """

    client: Client
    sources: SnapshotSource
    cache: ResultCache
    teams_cache: TeamsCache
    grade_limiter: GradeLimiter


def served_client(request: Request) -> Served:
    """The client of the request path. A path with no client is the default client of the app, for the old paths.

    A slug the app does not serve is 404, so a typo in the path never reads another league.
    """
    slug = request.path_params.get("slug", request.app.state.default_slug)
    served = request.app.state.served.get(slug)
    if served is None:
        raise HTTPException(status_code=404, detail=f"The API serves no client {slug}.")
    return served


# The client of the path as a route parameter, so each route reads its own Served client.
ServedClient = Annotated[Served, Depends(served_client)]


def _snapshot(served: Served, season: int) -> Snapshot:
    """The live snapshot for `season`. A season that Sleeper is not in is a bad input, so it is 422."""
    with season_in_progress(season):
        return served.sources.snapshot(season)


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


def _traded_player(snapshot: Snapshot, player_id: str) -> dict:
    """A traded player as a side card shows him: the player, his Season rank, and his Recent rank when the gap holds.

    `recent_rank` is null when the gap does not hold, so the card shows the Recent rank only when it is present.
    """
    season, recent = shown_ranks(snapshot, player_id)
    return {**_player(snapshot, player_id), "season_rank": season, "recent_rank": recent}


@router.get("/teams")
def teams(season: int, served: ServedClient) -> dict:
    """Each roster of the league with its team name, its manager, and its players, for the trade form."""
    return served.teams_cache.get_or_build(season, lambda: _teams(served, season))


def _teams(served: Served, season: int) -> dict:
    """The teams answer built from a live Sleeper fetch."""
    # The form needs the rosters and not the chart or the slow sources, so the route skips their refresh and the
    # history save. The daily cron and the start-up refresh keep the slow sources fresh.
    with season_in_progress(season):
        snapshot = served.sources.rosters_snapshot(season)
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
        "no_chart_note": NO_CHART_NOTE if snapshot.chart is None else None,
    }


# The decision a manager acts on, from the verdict choice of the rubric.
Answer = Literal["yes", "no", "not_as_is"]
ANSWERS: dict[str, Answer] = {"accept": "yes", "decline": "no", "counter": "not_as_is"}
# The deal row of a side, from its start letter. It is the first factor, and no letter reaches the document.
# Its words name no source of the values, so the row reads as plain advice.
DEAL = "deal"
DEAL_LEANS: dict[str, Lean] = {"A": "for", "B": "for", "C": "even", "D": "against", "F": "against"}


def _deal_row(breakdown: Breakdown) -> dict:
    """The deal row of one side: the start letter as a lean and one plain sentence."""
    return {"name": DEAL, "lean": DEAL_LEANS[breakdown.start_letter], "reason": deal_reason(breakdown)}


def _factor_lean(adjuster: Adjuster) -> Lean:
    """The lean of one adjuster. The schedule never steps, so it keeps its own lean."""
    if adjuster.lean is not None:
        return adjuster.lean
    return "for" if adjuster.step > 0 else "against" if adjuster.step < 0 else "even"


def _echoed_sides(trade: ProposedTrade, snapshot: Snapshot) -> list[dict]:
    """Each side of the trade as the site shows it: the roster, the team, and the players it gives and gets.

    Each player carries his Season rank and his Recent rank, in the finder document too, so a side has one shape.
    """
    # The analyze document and the finder document share this shape, so the site renders a side one way.
    # Each given player carries `to` and each got player carries `from`, so the site can tag a player by team.
    givers = trade.givers
    return [
        {
            "roster_id": side.roster_id,
            "team": snapshot.teams[side.roster_id].name,
            "gives": [{**_traded_player(snapshot, player.player_id), "to": player.to} for player in side.gives],
            "gets": [{**_traded_player(snapshot, pid), "from": givers[pid]} for pid in trade.gets(side.roster_id)],
        }
        for side in trade.sides
    ]


def result_document(trade: ProposedTrade, snapshot: Snapshot, analysis: Analysis) -> dict:
    """The result the site renders: a decision first, the fairness, then the bullets, the Week lines, and the factors
    per side.

    The deal row is the first factor of each side. The Week lines are never a factor, because they move no letter.

    It holds no letter, no step, and never a trade value, sum, or ratio. A manager acts on a decision, not a letter.
    """
    echoed = _echoed_sides(trade, snapshot)
    lines = week_lines(trade, snapshot)
    sides = [
        {
            "roster_id": breakdown.roster_id,
            "bullets": side.bullets,
            "week_lines": [line.model_dump() for line in lines[breakdown.roster_id]],
            "factors": [
                _deal_row(breakdown),
                # A row shows when it moves the grade or says something new, so a silent row with no step drops.
                # The letter math still reads every step.
                *({"name": adj.name, "lean": _factor_lean(adj), "reason": adj.reason}
                  for adj in breakdown.adjusters if adj.step != 0 or not adj.silent),
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
def analyze(request: Request, trade: ProposedTrade, served: ServedClient) -> dict:
    """Grade the proposed trade on the live snapshot and return the result document."""
    snapshot = _snapshot(served, trade.season)
    try:
        check_trade(trade, snapshot)
    except TradeInputError as error:
        # The form showed a roster that Sleeper no longer has, so the next teams request builds from Sleeper again.
        served.teams_cache.clear(trade.season)
        # The id lets the form mark the player who is no longer on the giving roster.
        raise HTTPException(status_code=422, detail={"message": str(error), "player_id": error.player_id})
    cache = served.cache
    key = cache_key(trade, snapshot)
    cached = cache.get(key)
    if cached is not None:
        return cached
    # The count comes after the cache, because a cached repeat makes no Claude call and costs nothing.
    _count_grade(request, served)
    analysis = request.app.state.analyzer(trade, snapshot)
    document = result_document(trade, snapshot, analysis)
    # A fallback is not stored, so the next request of the same trade tries the Claude call again.
    if not analysis.fallback:
        cache.put(key, document)
    return document


def _count_grade(request: Request, served: Served) -> None:
    """Count one grade for the address in the client, or stop the request with a 429 past the minute or the day limit."""
    # The analyze route and the find route share it, so a finder call costs one grade, as a trade does.
    # Each client has its own limiter, so the grades of one league never use up the limit of another.
    limited = served.grade_limiter.hit(request_address(request))
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
def find(request: Request, pair: FindRequest, served: ServedClient) -> dict:
    """List the top win-win trades between the asker and the partner on the live snapshot, each with one reason."""
    # The same roster twice needs no snapshot, so it fails before the load runs. The teams cache stays.
    if pair.asker == pair.partner:
        raise HTTPException(status_code=422, detail={"message": "Pick two different teams."})
    snapshot = _snapshot(served, pair.season)
    gone = [roster_id for roster_id in (pair.asker, pair.partner) if roster_id not in snapshot.rosters]
    if gone:
        # The form showed a roster that Sleeper no longer has, so the next teams request builds from Sleeper again.
        served.teams_cache.clear(pair.season)
        # The same words as check_trade, so the form shows one message for a roster that is gone.
        raise HTTPException(status_code=422, detail={"message": f"Roster {gone[0]} is not in the league"})
    cache = served.cache
    key = finder_cache_key(pair.season, pair.asker, pair.partner, snapshot)
    cached = cache.get(key)
    if cached is not None:
        return cached
    # The count comes after the cache, because a cached repeat runs no finder and makes no Claude call.
    _count_grade(request, served)
    found = find_win_wins(pair.asker, pair.partner, snapshot)
    reasons = request.app.state.finder_reasons(found, snapshot)
    document = finder_document(pair, snapshot, found, reasons)
    # A fallback is not stored, so the next request of the same pair tries the Claude call again.
    if not reasons.fallback:
        cache.put(key, document)
    return document
