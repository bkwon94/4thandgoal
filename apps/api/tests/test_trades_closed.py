"""
Tests of Trades closed: closed at the Lock and after it, open before it, and never closed with no Lock.
"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from analyzer.values import AnalyzerValues
from cornerstone_api.trades_closed import trades_closed
from cornerstone_api.value_models import VALUE_MODELS
from league.client import read_client_values

EASTERN = ZoneInfo("America/New_York")
LOCK = datetime(2026, 11, 24, 0, 0, tzinfo=EASTERN)


def test_a_client_with_no_lock_is_never_closed():
    assert not trades_closed(None, datetime(2026, 11, 24, 12, 0, tzinfo=EASTERN))
    assert not trades_closed(None, datetime(2027, 6, 1, 12, 0, tzinfo=EASTERN))


def test_it_is_open_one_second_before_the_lock_and_closed_at_it():
    assert not trades_closed(LOCK, datetime(2026, 11, 23, 23, 59, 59, tzinfo=EASTERN))
    assert trades_closed(LOCK, LOCK)
    assert trades_closed(LOCK, datetime(2026, 11, 24, 0, 0, 1, tzinfo=EASTERN))


def test_the_lock_and_deadline_week_of_the_real_clients_come_from_client_toml():
    clients = Path(__file__).resolve().parents[3] / "clients"
    norcal = read_client_values(clients / "norcal", VALUE_MODELS).package(AnalyzerValues)
    cpc = read_client_values(clients / "cpc", VALUE_MODELS).package(AnalyzerValues)
    assert norcal.lock == datetime(2026, 12, 15, 0, 0, tzinfo=EASTERN)
    assert not norcal.deadline_week
    assert cpc.deadline_week
