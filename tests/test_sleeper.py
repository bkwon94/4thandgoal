"""
Tests for the Sleeper client.
Offline tests read recorded data. Live tests call the real Sleeper API.
"""
import pytest
from cornerstone.sleeper import RAW_FILES, load_raw, fetch_week, fetch_state

def test_load_raw_returns_every_file(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert set(raw) == set(RAW_FILES)
    assert raw["league"]["name"] == "Cornerstone League"
    assert len(raw["matchups"]) == 12

@pytest.mark.live
def test_fetch_week_writes_every_file(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json")
    assert {p.stem for p in (tmp_path / "raw").glob("*.json")} == set(RAW_FILES)

@pytest.mark.live
def test_fetch_state_has_week():
    assert "display_week" in fetch_state()
