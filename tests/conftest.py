"""
Shared pytest fixtures for the Cornerstone Weekly tests.
They give tests the path to the recorded Sleeper data.
"""
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from cornerstone.history import load_history
from cornerstone.parse import parse_trades, parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.trades import default_cutoff, trades_for_week

ET = ZoneInfo("America/New_York")


@pytest.fixture
def fixture_raw_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw"


@pytest.fixture
def fixture_history_root() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "history"


@pytest.fixture
def hbundle(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    return build_bundle(parse_week(raw), news=lambda pid: [],
                        history=load_history(fixture_history_root, raw, week=6))


@pytest.fixture
def tbundle(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    trades = trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                             default_cutoff(date(2026, 9, 9), 6), datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    return build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=trades)
