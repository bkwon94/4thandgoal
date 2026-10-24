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


def _claim(position: str, bid: int, week: int = 3, won: bool = True, roster_id: int = 1) -> WaiverClaim:
    return WaiverClaim(player_id=f"7{week}{bid}", roster_id=roster_id, position=position, week=week, bid=bid, won=won)


def test_a_past_winning_claim_at_the_position_raises_the_floor_to_that_bid_plus_1():
    raw = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    # A $20 RB win raises the RB floor to $21. A lost $30 RB claim and a won $50 WR claim leave the RB floor.
    claims = [_claim("RB", 20), _claim("RB", 30, won=False), _claim("WR", 50)]
    assert _bid(raw, "RB", claims) == 21
    assert _bid(raw, "WR", claims) == 51


def test_the_price_never_exceeds_the_highest_rival_budget_left_and_is_a_whole_dollar():
    raw = _league([(40, [None, "Out"]), (60, [None, None]), (20, [None, None])])
    # A $70 RB win sets the floor at $71, but no rival has more than $60 left.
    bid = _bid(raw, "RB", [_claim("RB", 70)])
    assert bid == 60
    assert isinstance(bid, int)


def _last_like(raw: dict, position: str, claims: list[WaiverClaim]):
    return price_players([_free_agent("900", position)], raw, claims)[0].price.last_like


def test_the_last_like_him_is_the_latest_winning_claim_at_the_position_with_the_team_and_the_week():
    raw = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    raw["players"]["7101"] = {"position": "RB", "full_name": "Late Back", "team": "KC"}
    claims = [
        _claim("RB", 9, week=2, roster_id=1),
        WaiverClaim(player_id="7101", roster_id=2, position="RB", week=4, bid=3, won=True),
        # A lost claim and a claim at another position are never the last like him.
        _claim("RB", 12, week=5, won=False, roster_id=3),
        _claim("WR", 6, week=5, roster_id=3),
    ]
    last = _last_like(raw, "RB", claims)
    assert last.model_dump() == {"player_id": "7101", "name": "Late Back", "roster_id": 2, "team": "Team 2",
                                 "week": 4, "bid": 3}


def test_the_last_like_him_is_empty_when_the_history_has_no_win_at_the_position():
    raw = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    assert _last_like(raw, "TE", [_claim("RB", 9), _claim("TE", 4, won=False)]) is None
