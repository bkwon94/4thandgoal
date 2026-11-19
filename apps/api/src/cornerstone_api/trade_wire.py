"""
The Trade Wire route: the accepted trades of the current leg of one client, newest first, with the team names, the
players each team gets, and the FAAB each team gets. It reads Sleeper itself and keeps its answer for a few seconds.
"""
from fastapi import APIRouter, Request

from analyzer import routes as analyzer_routes
from analyzer.cache import TeamsCache
from cornerstone_api.sources import Sources
from league.models import Trade
from league.parse import parse_trades

router = APIRouter()

# All phones share one Sleeper read in each window. At the dinner the phones poll every 10 s, so the window keeps the
# reads of Sleeper at 12 a minute, far under its limit of 1000.
TRADE_WIRE_CACHE_SECONDS = 5


def new_cache() -> TeamsCache:
    """The cache of one client. It keeps its answer by season, and the build of a stale entry reads Sleeper again."""
    return TeamsCache(TRADE_WIRE_CACHE_SECONDS)


def _team(roster_id: int, trade: Trade, teams: dict[int, dict], players: dict[str, dict]) -> dict:
    """One side of `trade`. The players it gets come from the `adds` of the trade, never from the cached rosters,
    because the cache can hold the rosters from before the trade."""
    roster = teams[roster_id]
    return {
        "roster_id": roster_id,
        "team": roster["team"],
        "avatar": roster["avatar"],
        "players": [
            {"player_id": player_id, "name": players[player_id]["name"], "position": players[player_id]["position"]}
            for player_id, to in trade.adds.items() if to == roster_id
        ],
        "faab": sum(transfer.amount for transfer in trade.faab if transfer.receiver == roster_id),
    }


def _build(sources: Sources, served: analyzer_routes.Served, season: int) -> dict:
    leg, transactions = sources.fetch_transactions(served.client.current_league_id)
    # Sleeper gives one leg, but a transaction of another leg never belongs in the list of this one.
    trades = sorted(parse_trades([each for each in transactions if each.leg == leg]),
                    key=lambda trade: trade.accepted or trade.created, reverse=True)
    roster_teams = analyzer_routes.teams(season, served)["teams"]
    teams = {team["roster_id"]: team for team in roster_teams}
    # Every player of a trade is on a roster before or after it, so the cached rosters name each one.
    players = {player["player_id"]: player for team in roster_teams for player in team["players"]}
    return {"leg": leg, "trades": [
        {
            "transaction_id": trade.transaction_id,
            "accepted_at": (trade.accepted or trade.created).isoformat(),
            "teams": [_team(roster_id, trade, teams, players) for roster_id in trade.roster_ids],
        }
        for trade in trades
    ]}


@router.get("/deadline/trades")
def trades(request: Request, served: analyzer_routes.ServedClient) -> dict:
    """The accepted trades of the current leg, newest first by the time Sleeper accepted them."""
    slug = served.client.slug
    season = served.client.values.latest_season
    return request.app.state.trade_wires[slug].get_or_build(
        season, lambda: _build(request.app.state.sources[slug], served, season))
