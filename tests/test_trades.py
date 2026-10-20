"""
Tests for the trade window and the late-trade test.
They read the recorded week 6 data and the saved history.
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from cornerstone.history import load_history
from cornerstone.parse import parse_trades, parse_week
from cornerstone.sleeper import load_raw
from cornerstone.trades import default_cutoff, is_late, trades_for_week

ET = ZoneInfo("America/New_York")


def _six(fixture_raw_dir, fixture_history_root, until):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6), until)


def test_default_cutoff_week_6():
    assert default_cutoff(date(2026, 9, 9), 6) == datetime(2026, 10, 13, 8, 0, tzinfo=ET)


def test_window_holds_the_six_week_6_trades(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert [x.roster_ids for x in t] == [[4, 12], [7, 12], [4, 7], [6, 7], [11, 12], [7, 8]]


def test_window_end_drops_the_tuesday_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    assert len(t) == 5 and t[-1].roster_ids == [11, 12]


def test_late_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [is_late(x, wk) for x in t] == [False, False, False, False, False, True]
