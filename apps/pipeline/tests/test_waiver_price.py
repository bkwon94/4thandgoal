"""
Tests for the waiver price: the bid history, the bid to win, the last like him, and the outbid counts.
They price players in a small hand-built league, and they read the bid history from the fixture history.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from cpc import cpc_client

from cornerstone.waiver import waiver_board
from cornerstone.waiver_price import bid_history, price_players
from facts.tokens import NUMBER_TOKEN
from league.models import BoardScores, WaiverClaim, WaiverPlayer
from league.provider.raw import RawWeek
from league.provider.sleeper import load_raw

CLIENT = cpc_client()

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))

# The lineup needs 1 QB, 2 RBs, and 1 WR. The FLEX slot needs no one position.
LINEUP = ["QB", "RB", "RB", "WR", "FLEX", "BN", "BN"]


def _league(rosters: list[tuple[int, list[str | None]]]) -> RawWeek:
    """A league of 100 dollar budgets. Each roster is its budget left and the injury status of each of its RBs.

    Each roster also holds one healthy QB and one healthy WR, so no roster needs a QB or a WR.
    """
    # The price reads only the league, the users, the rosters, and the players. The other files stay empty.
    raw = {"league": {"settings": {"waiver_budget": 100, "last_scored_leg": 6, "reserve_slots": 0},
                      "roster_positions": LINEUP, "scoring_settings": {}},
           "users": [], "rosters": [], "players": {},
           "state": {"season": "2026", "display_week": 6, "season_start_date": "2026-09-09"},
           "matchups": [], "matchups_next": [], "transactions": [], "stats": [], "projections": [], "bracket": []}
    for roster_id, (left, rb_statuses) in enumerate(rosters, start=1):
        owned = {f"{roster_id}0": ("QB", None), f"{roster_id}1": ("WR", None)}
        owned |= {f"{roster_id}{2 + i}": ("RB", status) for i, status in enumerate(rb_statuses)}
        raw["players"] |= {pid: {"position": pos, "injury_status": status, "team": "KC"}
                           for pid, (pos, status) in owned.items()}
        raw["users"].append({"user_id": f"u{roster_id}", "display_name": f"owner{roster_id}",
                             "metadata": {"team_name": f"Team {roster_id}"}})
        raw["rosters"].append({"roster_id": roster_id, "owner_id": f"u{roster_id}", "players": list(owned),
                               "settings": {"waiver_budget_used": 100 - left, "waiver_position": roster_id,
                                            "fpts": 0, "wins": 0, "losses": 0}})
    return RawWeek.model_validate(raw)


def _free_agent(player_id: str, position: str, board_score: float = 0.75) -> WaiverPlayer:
    return WaiverPlayer(player_id=player_id, name=f"Player {player_id}", position=position, team="KC",
                        week_projection=0.0, ros_projection=0.0, scores=BoardScores(), board_score=board_score)


def _bid(raw: dict, position: str = "RB", claims: list[WaiverClaim] = (), board_score: float = 0.75) -> int:
    """The bid to win of one free agent after week 6."""
    return price_players([_free_agent("900", position, board_score)], raw, list(claims), 6)[0].price.bid


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
    # Team 1 has $40 left and one of its two RBs is out. At a board score of 0.75 it bids 35% of $40 times
    # 0.75, $10.50. The bid to win is $11.
    needy = _league([(40, [None, "Out"]), (60, [None, None]), (20, [None, None])])
    # With both RBs healthy, the top bid is 12% of team 2's $60 times 0.75, $5.40, so the bid to win is $6.
    covered = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    assert _bid(needy) == 11
    assert _bid(covered) == 6
    # No roster needs a WR, so the WR price stays at $6 in both leagues.
    assert _bid(needy, "WR") == 6


def test_the_player_with_the_higher_board_score_costs_more_at_the_same_position():
    needy = _league([(40, [None, "Out"]), (60, [None, None]), (20, [None, None])])
    # Team 1 bids 35% of $40 times the score: $14 at 1, so $15, and $7 at 0.5, so $8.
    assert _bid(needy, board_score=1.0) == 15
    assert _bid(needy, board_score=0.5) == 8


def _claim(position: str, bid: int, week: int = 5, won: bool = True, roster_id: int = 1) -> WaiverClaim:
    return WaiverClaim(player_id=f"7{week}{bid}", roster_id=roster_id, position=position, week=week, bid=bid, won=won)


def test_a_past_winning_claim_at_the_position_raises_the_floor_to_that_bid_plus_1():
    raw = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    # A $20 RB win in week 5 raises the RB floor to $21. A lost $30 RB claim and a won $50 WR claim leave
    # the RB floor.
    claims = [_claim("RB", 20), _claim("RB", 30, won=False), _claim("WR", 50)]
    assert _bid(raw, "RB", claims) == 21
    assert _bid(raw, "WR", claims) == 51


def test_only_the_most_recent_win_of_the_last_3_weeks_sets_the_floor():
    raw = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    # After week 6 the window is weeks 4 to 6. A $30 win in week 3 is older, so the price stays at $6.
    assert _bid(raw, "RB", [_claim("RB", 30, week=3)]) == 6
    # The $10 win of week 5 sets the floor at $11, though the $25 win of week 4 is larger.
    assert _bid(raw, "RB", [_claim("RB", 25, week=4), _claim("RB", 10, week=5)]) == 11


def test_the_price_never_exceeds_the_highest_rival_budget_left_and_is_a_whole_dollar():
    raw = _league([(40, [None, "Out"]), (60, [None, None]), (20, [None, None])])
    # A $70 RB win sets the floor at $71, but no rival has more than $60 left.
    bid = _bid(raw, "RB", [_claim("RB", 70)])
    assert bid == 60
    assert isinstance(bid, int)


def _last_like(raw: dict, position: str, claims: list[WaiverClaim]):
    return price_players([_free_agent("900", position)], raw, claims, 6)[0].price.last_like


def test_the_last_like_him_is_the_latest_winning_claim_at_the_position_with_the_team_and_the_week():
    raw = _league([(40, [None, None]), (60, [None, None]), (20, [None, None])])
    raw.players["7101"] = {"position": "RB", "full_name": "Late Back", "team": "KC"}
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


def test_every_number_in_the_price_fact_text_is_in_its_numbers():
    raw = _league([(41, [None, "IR"]), (60, [None, None]), (20, [None, None])])
    # The fact names the need, the past win, and the cap, so every part of the text is in play.
    price = price_players([_free_agent("900", "RB")], raw, [_claim("RB", 70)], 6)[0].price
    assert price.fact.text == ("Bid $60 to win Player 900. The top rival bid is about $10.76, from Team 1 with $41 left"
                               " and a need at RB. The last winning RB claim in the last 3 weeks is $70."
                               " No rival has more than $60 left.")
    # The digits of the names in this hand-built league are names, not numbers.
    text = price.fact.text.replace("Player 900", "").replace("Team 1", "")
    assert set(NUMBER_TOKEN.findall(text)) == set(price.fact.numbers)
    assert price.fact.teams == ["Team 1"]


def test_the_board_prices_best_adds_with_the_outbid_count_per_budget_level(fixture_raw_dir):
    # The week 6 budgets left: 90, 82, 72, 69, 67, 65, 61, 58, 51, 25, 19, and 9.
    raw = load_raw(fixture_raw_dir)
    raw.players["80001"] = {"position": "RB", "team": "KC", "status": "Active", "full_name": "Free Back"}
    raw.projections_ahead = [{"week": w, "projections": {"80001": 10.0}} for w in range(7, 18)]
    # A $40 RB win in week 5 sets the floor at $41. The top expected bid is at most 35% of $90, $31.50.
    best = waiver_board(raw, 6, BUILT, claims=[_claim("RB", 40)], client=CLIENT).buckets["best_adds"]
    price = next(p.price for p in best if p.player_id == "80001")
    assert price.bid == 41
    assert sorted(price.outbid) == [9, 19, 25, 51, 58, 61, 65, 67, 69, 72, 82, 90]
    # A viewer at $51 can bid the $41: 9 rosters have more than $41, his own among them, so 8 rivals can outbid him.
    assert price.outbid[51] == 8
    # A viewer at $9 can bid only $9: the 11 other rosters have more than $9.
    assert price.outbid[9] == 11


def test_a_player_in_best_adds_and_trending_carries_one_price(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw.players["80001"] = {"position": "WR", "team": "KC", "status": "Active", "full_name": "Hot Wideout"}
    raw.projections_ahead = [{"week": w, "projections": {"80001": 10.0}} for w in range(7, 18)]
    raw.trending = [{"player_id": "80001", "count": 5000}]
    buckets = waiver_board(raw, 6, BUILT, client=CLIENT).buckets
    best = next(p for p in buckets["best_adds"] if p.player_id == "80001")
    trending = next(p for p in buckets["trending"] if p.player_id == "80001")
    assert best.price is not None
    assert best.price is trending.price
