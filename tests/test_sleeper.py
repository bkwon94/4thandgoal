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


def test_truncated_players_cache_refetches(tmp_path, monkeypatch):
    import json

    from cornerstone import sleeper

    cache = tmp_path / "cache" / "players.json"
    cache.parent.mkdir()
    cache.write_text('{"1": {"full_name": "Cut')
    fetched = {"1": {"full_name": "Whole Name"}}
    monkeypatch.setattr(sleeper, "_get", lambda client, url, params=None: fetched)

    assert sleeper._players(None, cache) == fetched
    assert json.loads(cache.read_text()) == fetched
    assert [p.name for p in cache.parent.iterdir()] == ["players.json"]


def test_unofficial_non_json_body_gives_empty():
    import httpx

    from cornerstone import sleeper

    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="<html>"))
    with httpx.Client(transport=transport) as client:
        assert sleeper._get_or_empty(client, "https://example.test/news") == []
