"""
Tests for the Sleeper client.
Offline tests read recorded data. Live tests call the real Sleeper API.
"""
import pytest
from cornerstone.sleeper import RAW_FILES, load_raw, fetch_week, fetch_state, read_fetch_time

def test_load_raw_returns_every_file(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert set(raw) == {*RAW_FILES, "schedule"}
    assert raw["league"]["name"] == "Cornerstone League"
    assert len(raw["matchups"]) == 12

@pytest.mark.live
def test_fetch_week_writes_every_file(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json")
    assert {p.stem for p in (tmp_path / "raw").glob("*.json")} == {*RAW_FILES, "fetched", "transactions_prev", "schedule"}


@pytest.mark.live
def test_fetch_week_records_the_fetch_time(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json")
    assert read_fetch_time(tmp_path / "raw").tzinfo is not None


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


def _fake_get(calls: list[str]):
    """A fake of sleeper._get. It gives 12 matchup rows with points for each week and an empty body for the rest."""
    def get(client, url, params=None):
        calls.append(url)
        if "/matchups/" in url:
            return [{"roster_id": r, "matchup_id": (r + 1) // 2, "points": 0.0, "starters": ["1"],
                     "starters_points": [0.0], "players_points": {"1": 0.0}} for r in range(1, 13)]
        return {} if url.endswith(("/league/1", "/state/nfl")) else []
    return get


def _fetch_schedule(tmp_path, monkeypatch, week: int) -> tuple[list, list[str]]:
    import json

    from cornerstone import sleeper

    calls: list[str] = []
    monkeypatch.setattr(sleeper, "_get", _fake_get(calls))
    fetch_week("1", 2026, week, tmp_path / "raw", tmp_path / "players.json")
    return json.loads((tmp_path / "raw" / "schedule.json").read_text()), calls


def test_fetch_week_saves_the_schedule(tmp_path, monkeypatch):
    schedule, calls = _fetch_schedule(tmp_path, monkeypatch, 6)
    assert [entry["week"] for entry in schedule] == list(range(8, 15))
    assert [url.rsplit("/", 1)[1] for url in calls if "/matchups/" in url] == [str(w) for w in range(6, 15)]
    # Points and lineups are dropped, so only the pair keys stay.
    assert all(set(row) == {"roster_id", "matchup_id"} for entry in schedule for row in entry["matchups"])
    assert len(schedule[0]["matchups"]) == 12


def test_fetch_week_12_saves_one_schedule_week(tmp_path, monkeypatch):
    schedule, _ = _fetch_schedule(tmp_path, monkeypatch, 12)
    assert [entry["week"] for entry in schedule] == [14]


def test_fetch_week_13_and_14_save_an_empty_schedule(tmp_path, monkeypatch):
    assert _fetch_schedule(tmp_path, monkeypatch, 13)[0] == []
    assert _fetch_schedule(tmp_path, monkeypatch, 14)[0] == []


def test_load_raw_without_schedule(fixture_raw_dir, tmp_path):
    import shutil

    raw_dir = tmp_path / "raw"
    shutil.copytree(fixture_raw_dir, raw_dir)
    (raw_dir / "schedule.json").unlink()
    assert set(load_raw(raw_dir)) == set(RAW_FILES)
