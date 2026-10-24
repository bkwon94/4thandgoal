"""
Tests for the waiver price: the bid history, the bid to win, the last like him, and the outbid counts.
They feed a small hand-built league at the price seam, and the fixture history at the bid history seam.
"""
from cornerstone.sleeper import load_raw
from cornerstone.waiver_price import bid_history


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
