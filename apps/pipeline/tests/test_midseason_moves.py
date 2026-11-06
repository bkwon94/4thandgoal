"""
Tests for the waivers and the trades of Act II of the midseason report, on the real saved CPC data of 2026 with the
full transactions of each week that the build fetches again. AT-15 and AT-16.
"""
from collections import Counter
from pathlib import Path

import pytest
from test_midseason import CPC_PROVIDER, _call, _clean_call, _cpc_week_8, _report

from cornerstone.pipeline import run_midseason
from league.paths import build_dir


@pytest.fixture(scope="module")
def moves(tmp_path_factory) -> dict[str, dict]:
    """The chapters of Act II of the CPC week 8 report, by key."""
    tmp_path: Path = tmp_path_factory.mktemp("moves")
    report = _report(run_midseason(2026, 8, _clean_call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
    act = next(act for act in report["acts"] if act["key"] == "the-moves")
    return {chapter["key"]: chapter for chapter in act["chapters"]}


def test_act_two_holds_the_draft_waivers_trades_lineup_and_records(moves):
    assert list(moves) == ["draft", "waivers", "trades", "lineup", "records"]


def test_the_top_hit_is_ollie_gordon_ii_at_40_dollars_to_unsolicited_dak_picks(moves):
    # AT-15.
    hits = moves["waivers"]["facts"]["hits"]
    assert len(hits) == 5
    assert (hits[0]["player"], hits[0]["bid"], hits[0]["team"]) == ("Ollie Gordon II", 40, "Unsolicited Dak Picks")
    assert [hit["points_over_line"] for hit in hits] == sorted((hit["points_over_line"] for hit in hits), reverse=True)


def test_the_top_miss_is_joe_mixon_at_40_dollars(moves):
    # AT-15.
    misses = moves["waivers"]["facts"]["misses"]
    assert len(misses) == 5
    assert (misses[0]["player"], misses[0]["bid"]) == ("Joe Mixon", 40)
    assert all(miss["bid"] >= 10 for miss in misses)


def test_the_outbid_list_has_the_blue_tents_36_dollar_bid_on_ollie_gordon_ii(moves):
    # AT-15.
    outbid = moves["waivers"]["facts"]["outbid"]
    assert len(outbid) == 3
    assert (outbid[0]["team"], outbid[0]["bid"], outbid[0]["player"], outbid[0]["margin"]) == (
        "The Blue Tent", 36, "Ollie Gordon II", 4)


def test_the_streaming_king_has_the_most_points_of_streamed_starts(moves):
    streamers = moves["waivers"]["facts"]["streamers"]
    assert streamers[0]["team"] == "Return of T Mac"
    assert [s["points"] for s in streamers] == sorted((s["points"] for s in streamers), reverse=True)


def test_the_trade_report_card_lists_20_trades_with_the_lines_90_60_and_10(moves):
    # AT-16. On the CPC week 8 data, the lines give 2 Robberies and 2 Clear wins (PRD).
    trades = moves["trades"]["facts"]["trades"]
    assert len(trades) == 20
    counts = Counter(card["result"] for card in trades)
    assert (counts["Robbery"], counts["Clear win"], counts["Too soon"]) == (2, 2, 1)


def test_the_week_1_trade_of_maye_dforce_b_with_u_and_nfc_least_is_a_robbery(moves):
    # AT-16.
    trades = moves["trades"]["facts"]["trades"]
    card = next(card for card in trades
                if card["week"] == 1 and {s["team"] for s in card["sides"]} == {"Maye d'force B with U", "NFC Least"})
    assert (card["result"], card["winner"]) == ("Robbery", "Maye d'force B with U")


def test_the_week_8_trade_is_too_soon_and_comes_last(moves):
    # AT-16.
    trades = moves["trades"]["facts"]["trades"]
    week_8 = [card for card in trades if card["week"] == 8]
    assert [card["result"] for card in week_8] == ["Too soon"]
    assert trades[-1] == week_8[0]


def test_each_chapter_of_act_two_has_its_blurb_and_its_roast_through_the_writer(moves):
    for chapter in moves.values():
        assert chapter["blurb"]["chapter"] == chapter["key"]
        assert chapter["roast"]["chapter"] == chapter["key"] + ".roast"


def test_the_review_file_shows_the_blurbs_of_act_two(tmp_path):
    client = _cpc_week_8(tmp_path)
    run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "## waivers: Waiver hits and misses" in review
    assert "## trades: The trade report card" in review
    assert "- WV.hit.1: Ollie Gordon II went to Unsolicited Dak Picks for $40 in week 3" in review
