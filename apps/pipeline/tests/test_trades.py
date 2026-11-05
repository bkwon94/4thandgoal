"""
Tests for the trade window and the late-trade test.
They read the recorded week 6 data and the saved history.
They also test that the weekly sheet has no trade chapter and no trade fact.
"""
import re
from datetime import date, datetime
from importlib import resources
from zoneinfo import ZoneInfo

from cpc import cpc_client

from league.history import load_history
from league.parse import parse_trades, parse_week
from league.provider.sleeper import load_raw
from league.trades import default_cutoff, is_late, trades_for_week

CLIENT = cpc_client()

ET = ZoneInfo("America/New_York")


def _week(fixture_raw_dir, fixture_history_root, week):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw.transactions), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), week, ET), default_cutoff(date(2026, 9, 9), week + 1, ET))


def _six(fixture_raw_dir, fixture_history_root, until):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw.transactions), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6, ET), until)


def test_default_cutoff_week_6():
    assert default_cutoff(date(2026, 9, 9), 6, ET) == datetime(2026, 10, 13, 8, 0, tzinfo=ET)


def test_week_6_window_holds_the_five_trades_before_the_cutoff(fixture_raw_dir, fixture_history_root):
    t = _week(fixture_raw_dir, fixture_history_root, 6)
    assert [x.roster_ids for x in t] == [[4, 12], [7, 12], [4, 7], [6, 7], [11, 12]]


def test_week_7_window_holds_the_tuesday_trade(fixture_raw_dir, fixture_history_root):
    t = _week(fixture_raw_dir, fixture_history_root, 7)
    assert [x.roster_ids for x in t] == [[7, 8]]


def _trade_at(fixture_raw_dir, created):
    trade = parse_trades(load_raw(fixture_raw_dir).transactions)[0]
    return trade.model_copy(update={"created": created})


def _holds(trade, week):
    return trades_for_week(
        [trade], [], default_cutoff(date(2026, 9, 9), week, ET), default_cutoff(date(2026, 9, 9), week + 1, ET)
    )


def test_a_trade_at_the_week_6_cutoff_is_in_week_5_only(fixture_raw_dir):
    trade = _trade_at(fixture_raw_dir, datetime(2026, 10, 13, 8, 0, tzinfo=ET))
    assert _holds(trade, 5) == [trade]
    assert _holds(trade, 6) == []


def test_a_trade_at_the_week_7_cutoff_is_in_week_6_only(fixture_raw_dir):
    trade = _trade_at(fixture_raw_dir, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    assert _holds(trade, 6) == [trade]
    assert _holds(trade, 7) == []


def test_late_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [is_late(x, wk) for x in t] == [False, False, False, False, False, True]


def test_roster_slots_count_the_reserve_slot(fixture_raw_dir):
    assert parse_week(load_raw(fixture_raw_dir)).roster_slots == 15


def test_vocabulary_has_the_profile_terms():
    text = resources.files("facts").joinpath("prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("points per game", "position rank by season points"):
        assert f"**{term}**" in text


def test_vocabulary_drops_the_recap_terms_and_the_grade_terms():
    text = resources.files("facts").joinpath("prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("trade impact", "trade swing", "late trade"):
        assert f"**{term}**" not in text
    for term in ("trade grade", "trade value", "roster need", "snap share", "target share", "red-zone use",
                 "injury before the trade"):
        assert f"**{term}**" not in text
    assert "grade" not in text


def test_the_week_6_sheet_has_no_trade_chapter_and_no_trade_fact(tbundle):
    assert tbundle.data.trades and tbundle.data.trade_players
    assert not [c.key for c in tbundle.sheet.chapters if c.key.startswith("trade")]
    assert not [fid for fid in tbundle.sheet.facts if re.match(r"T\d+\.", fid)]
