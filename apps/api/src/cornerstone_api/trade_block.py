"""
The trade card of the trade Topics: the two sides of each trade, the projected points of each player for the rest of
the season, and the Lean, the Case, and the top Bullets that the analyzer gives. It adds no grade and no edge.
"""
from league.projection import rest_of_season
from league.snapshot import Snapshot

# The Bullets of Your side that a trade check shows, and of each offer of trade ideas, as the cards before.
TOP_BULLETS = 3
TOP_OFFER_BULLETS = 2

KIND = "trade"


def rest_points(snapshot: Snapshot) -> dict[str, float]:
    """The projected points of each player from the trade week to the last season week. No file gives no points."""
    by_week: dict[int, dict[str, float]] = {}
    for pid, weeks in (snapshot.projections_ahead or {}).items():
        for week, points in weeks.items():
            if week >= snapshot.week:
                by_week.setdefault(week, {})[pid] = points
    pids = {pid for weeks in by_week.values() for pid in weeks}
    return {pid: rest_of_season(by_week, pid, snapshot.week - 1, snapshot.client) for pid in pids}


def _side(side: dict, asker: int, points: dict[str, float]) -> dict:
    """One side of the card: its team and each player it gets with his points. A player with no projection has 0."""
    gets = [{"player_id": p["player_id"], "name": p["name"], "position": p["position"], "nfl_team": p["nfl_team"],
             "points": points.get(p["player_id"], 0.0)} for p in side["gets"]]
    return {"roster_id": side["roster_id"], "team": side["team"], "yours": side["roster_id"] == asker, "gets": gets,
            "total": round(sum(p["points"] for p in gets), 2)}


def _offer(offer_id: str, sides: list[dict], asker: int, points: dict[str, float], *, gist: str | None,
           lean: str | None, case: str | None, bullets: list[dict]) -> dict:
    mine = next((side for side in sides if side["roster_id"] == asker), sides[0])
    partner = next((side for side in sides if side["roster_id"] != mine["roster_id"]), None)
    names = ", ".join(p["name"] for p in mine["gives"])
    gets = ", ".join(p["name"] for p in mine["gets"])
    # Your side leads, so the tug bar reads the same way in every card.
    ordered = [mine, *[side for side in sides if side is not mine]]
    return {"id": offer_id, "partner": partner["team"] if partner else mine["team"],
            "gist": gist or f"{names} for {gets}", "lean": lean, "case": case, "bullets": bullets,
            "sides": [_side(side, asker, points) for side in ordered]}


def check_block(document: dict, points: dict[str, float]) -> dict:
    """The card of a trade check: one trade, closed by the Lean, with the Case and the top Bullets of Your side."""
    trade = document["trade"]
    asker = trade["asker"]
    bullets = next((side["bullets"] for side in document["sides"] if side["roster_id"] == asker), [])
    ids = "-".join(p["player_id"] for side in trade["sides"] for p in side["gives"])
    offer = _offer(ids, trade["sides"], asker, points, gist=None, lean=document["lean"], case=document["case"],
                   bullets=bullets[:TOP_BULLETS])
    return {"kind": KIND, "offers": [offer]}


def ideas_block(document: dict, points: dict[str, float]) -> dict:
    """The card of trade ideas: one row per offer with its partner and its headline as the gist. An offer has no Lean,
    because each pick is an offer the analyzer would send."""
    asker = document["trade_pair"]["asker"]["roster_id"]
    offers = [_offer(trade["offer_id"], trade["sides"], asker, points, gist=trade["headline"], lean=None, case=None,
                     bullets=trade["bullets"][:TOP_OFFER_BULLETS]) for trade in document["trades"]]
    return {"kind": KIND, "offers": offers}
