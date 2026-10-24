"""
Tests for the waiver price: the bid history, the bid to win, the last like him, and the outbid counts.
They feed a small hand-built league at the price seam, and the fixture history at the bid history seam.
"""
from cornerstone.models import BoardScores, WaiverClaim, WaiverPlayer
from cornerstone.sleeper import load_raw
from cornerstone.waiver_price import bid_history, price_players

# The lineup needs 1 QB, 2 RBs, and 1 WR. The FLEX slot needs no one position.
LINEUP = ["QB", "RB", "RB", "WR", "FLEX", "BN", "BN"]


def _league(rosters: list[tuple[int, list[str | None]]]) -> dict:
    """A league of 100 dollar budgets. Each roster is its budget left and the injury status of each of its RBs.

    Each roster also holds one healthy QB and one healthy WR, so no roster needs a QB or a WR.
    """
    raw = {"league": {"settings": {"waiver_budget": 100}, "roster_positions": LINEUP},
           "users": [], "rosters": [], "players": {}}
    for roster_id, (left, rb_statuses) in enumerate(rosters, start=1):
        owned = {f"{roster_id}0": ("QB", None), f"{roster_id}1": ("WR", None)}
        owned |= {f"{roster_id}{2 + i}": ("RB", status) for i, status in enumerate(rb_statuses)}
        raw["players"] |= {pid: {"position": pos, "injury_status": status, "team": "KC"}
                           for pid, (pos, status) in owned.items()}
        raw["users"].append({"user_id": f"u{roster_id}", "display_name": f"owner{roster_id}",
                             "metadata": {"team_name": f"Team {roster_id}"}})
        raw["rosters"].append({"roster_id": roster_id, "owner_id": f"u{roster_id}", "players": list(owned),
                               "settings": {"waiver_budget_used": 100 - left, "waiver_position": roster_id}})
    return raw


def _free_agent(player_id: str, position: str) -> WaiverPlayer:
    return WaiverPlayer(player_id=player_id, name=f"Player {player_id}", position=position, team="KC",
                        week_projection=0.0, ros_projection=0.0, scores=BoardScores(), board_score=0.0)


def _bid(raw: dict, position: str = "RB", claims: list[WaiverClaim] = ()) -> int:
    return price_players([_free_agent("900", position)], raw, list(claims))[0].price.bid


def test_the_bid_history_holds_every_waiver_claim_of_the_season_with_its_bid_and_result(
    fixture_raw_dir, fixture_history_root,
):
    claims = bid_history(fixture_history_root, load_raw(fixture_raw_dir), 6)
    # Weeks 1 to 5 of the saved history and week 6 of the raw hold 158 waiver claims in all.
    assert len(claims) == 158
    assert {c.week for c in claims} == {1, 2, 3, 4, 5, 6}
    # Week 3: roster 11 won Keaton Mitchell at $25, and roster 10 lost him at $15.
    davis = [c.model_dump() for c in claims if c.player_id == "9511" and c.bid in (25, 15)]
    assert davis == [
        {"player_id": "9511", "roster_id": 11, "position": "RB", "week": 3, "bid": 25, "won": True},
        {"player_id": "9511", "roster_id": 10, "position": "RB", "week": 3, "bid": 15, "won": False},
    ]


def test_a_rival_with_a_need_at_the_position_raises_the_price_more_than_one_without():
    # Team 1 has $40 left and one of its two RBs is out, so it bids 35% of $40, $14. The bid to win is $15.
    needy = _league([(40, [None, "Out"]), (60, [None, None]), (20, [None, None])])
    # With both RBs healthy, the top bid is 12% of team 2's $60, $7.20, so the bid to win is $8.
    covered = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    assert _bid(needy) == 15
    assert _bid(covered) == 8
    # No roster needs a WR, so the WR price stays at $8 in both leagues.
    assert _bid(needy, "WR") == 8
