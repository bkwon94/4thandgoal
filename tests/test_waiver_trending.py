"""
Tests for the trending bucket of the waiver board and the fetch of the trending file.
They feed a fake Sleeper client at the fetch seam and hand-set counts on the week 6 raw at the engine seam.
"""
import json

from cornerstone import sleeper
from cornerstone.sleeper import fetch_week, load_raw

TRENDING_URL = "https://api.sleeper.app/v1/players/nfl/trending/add"


def _fake_trending_get(calls: list[tuple[str, object]]):
    """A fake of sleeper._get. It gives two trending rows and an empty body for every other call."""
    def get(client, url, params=None):
        calls.append((url, params))
        if url == TRENDING_URL:
            return [{"player_id": "4046", "count": 41200}, {"player_id": "NYJ", "count": 9}]
        return {} if url.endswith(("/league/1", "/state/nfl")) else []
    return get


def test_the_week_fetch_saves_the_trending_file(tmp_path, monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(sleeper, "_get", _fake_trending_get(calls))
    fetch_week("1", 2026, 6, tmp_path / "raw", tmp_path / "players.json")
    saved = json.loads((tmp_path / "raw" / "trending.json").read_text())
    assert saved == [{"player_id": "4046", "count": 41200}, {"player_id": "NYJ", "count": 9}]
    assert [dict(params) for url, params in calls if url == TRENDING_URL] == [{"lookback_hours": 24, "limit": 50}]
    assert load_raw(tmp_path / "raw")["trending"] == saved
