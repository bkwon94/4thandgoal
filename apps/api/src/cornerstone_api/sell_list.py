"""
The sell list of Sell high or buy low: the data block of the front door, built from the document of the sell high
press. One row per player to sell with his ranks and the headline, and the bullets that open in place.
"""

# The kind of the data block of sell high. Every block on the stream names its kind, so the site picks its view from it.
SELL_LIST_KIND = "sell_list"
# The fields of a player to sell that the row shows. A document from before the ranks has none, so they read as None.
PLAYER_FIELDS = ("player_id", "name", "position", "nfl_team", "headshot")


def sell_list(document: dict) -> dict:
    """The sell list of one sell high document, in the order of the picks of the Advisor. A roster with no clear sell
    gives no rows and its plain line."""
    rows = [{**{field: pick["player"][field] for field in PLAYER_FIELDS},
             "season_rank": pick["player"].get("season_rank"), "recent_rank": pick["player"].get("recent_rank"),
             "headline": pick["headline"],
             "bullets": [{"text": bullet["text"], "mark": bullet["mark"]} for bullet in pick["bullets"]]}
            for pick in document["picks"]]
    return {"kind": SELL_LIST_KIND, "team": document["team"]["roster_id"], "rows": rows, "empty": document["empty"]}
