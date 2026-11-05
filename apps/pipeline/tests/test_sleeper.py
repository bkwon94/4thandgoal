"""
Tests for the Sleeper client.
Offline tests read recorded data. Live tests call the real Sleeper API.
"""
import pytest
from cpc import cpc_client
from fakes import json_transport

from league.provider.sleeper import RAW_FILES, fetch_state, fetch_week, load_raw, read_fetch_time

# The client the fetches of these tests read.
CLIENT = cpc_client()
# The league fields that the raw model needs, with no rosters, slots, or scoring.
EMPTY_LEAGUE = {"roster_positions": [], "scoring_settings": {},
                "settings": {"last_scored_leg": 0, "reserve_slots": 0, "waiver_budget": 100}}

def test_load_raw_returns_every_file(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert raw.model_fields_set == {*RAW_FILES, "schedule", "projections_ahead"}
    assert raw.league.name == "Cornerstone League"
    assert len(raw.matchups) == 12

@pytest.mark.live
def test_fetch_week_writes_every_file(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json", CLIENT.tz,
               CLIENT.settings.last_regular_week, CLIENT.settings.last_season_week, CLIENT.settings.points_key)
    assert {p.stem for p in (tmp_path / "raw").glob("*.json")} == {
        *RAW_FILES, "fetched", "transactions_prev", "schedule", "projections_ahead", "trending"}


@pytest.mark.live
def test_fetch_week_records_the_fetch_time(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json", CLIENT.tz,
               CLIENT.settings.last_regular_week, CLIENT.settings.last_season_week, CLIENT.settings.points_key)
    assert read_fetch_time(tmp_path / "raw").tzinfo is not None


@pytest.mark.live
def test_fetch_state_has_week():
    assert "display_week" in fetch_state()


def test_truncated_players_cache_refetches(tmp_path):
    import json

    from league.provider import sleeper

    cache = tmp_path / "cache" / "players.json"
    cache.parent.mkdir()
    cache.write_text('{"1": {"full_name": "Cut')
    fetched = {"1": {"full_name": "Whole Name"}}

    assert sleeper.fetch_players(cache, json_transport(lambda url, params: fetched)) == fetched
    assert json.loads(cache.read_text()) == fetched
    assert [p.name for p in cache.parent.iterdir()] == ["players.json"]


def test_unofficial_non_json_body_gives_empty():
    import httpx

    from league.provider import sleeper

    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="<html>"))
    with httpx.Client(transport=transport) as client:
        assert sleeper._get_or_empty(client, "https://example.test/news") == []


def _fake_get(calls: list[str]):
    """A fake Sleeper body. It gives 12 matchup rows with points for each week and an empty body for the rest."""
    def get(url, params):
        calls.append(url)
        if "/matchups/" in url:
            return [{"roster_id": r, "matchup_id": (r + 1) // 2, "points": 0.0, "starters": ["1"],
                     "starters_points": [0.0], "players_points": {"1": 0.0}} for r in range(1, 13)]
        return {} if url.endswith(("/league/1", "/state/nfl")) else []
    return get


def _fetch_schedule(tmp_path, week: int) -> tuple[list, list[str]]:
    import json

    calls: list[str] = []
    fetch_week("1", 2026, week, tmp_path / "raw", tmp_path / "players.json", CLIENT.tz,
               CLIENT.settings.last_regular_week, CLIENT.settings.last_season_week, CLIENT.settings.points_key,
               json_transport(_fake_get(calls)))
    return json.loads((tmp_path / "raw" / "schedule.json").read_text()), calls


def test_fetch_week_saves_the_schedule(tmp_path):
    schedule, calls = _fetch_schedule(tmp_path, 6)
    assert [entry["week"] for entry in schedule] == list(range(8, 15))
    assert [url.rsplit("/", 1)[1] for url in calls if "/matchups/" in url] == [str(w) for w in range(6, 15)]
    # Points and lineups are dropped, so only the pair keys stay.
    assert all(set(row) == {"roster_id", "matchup_id"} for entry in schedule for row in entry["matchups"])
    assert len(schedule[0]["matchups"]) == 12


def test_fetch_week_12_saves_one_schedule_week(tmp_path):
    schedule, _ = _fetch_schedule(tmp_path, 12)
    assert [entry["week"] for entry in schedule] == [14]


def test_fetch_week_13_and_14_save_an_empty_schedule(tmp_path):
    assert _fetch_schedule(tmp_path, 13)[0] == []
    assert _fetch_schedule(tmp_path, 14)[0] == []


def test_load_raw_without_schedule(fixture_raw_dir, tmp_path):
    import shutil

    raw_dir = tmp_path / "raw"
    shutil.copytree(fixture_raw_dir, raw_dir)
    (raw_dir / "schedule.json").unlink()
    assert load_raw(raw_dir).model_fields_set == {*RAW_FILES, "projections_ahead"}


def _fake_projections_get(calls: list[str]):
    """A fake Sleeper body with 2 rosters and a projection row per week for a rostered and a free player."""
    base = _fake_get(calls)

    def get(url, params):
        if url.endswith("/rosters"):
            calls.append(url)
            return [{"roster_id": 1, "players": ["10", "11"]}, {"roster_id": 2, "players": None}]
        if "/projections/nfl/" in url:
            calls.append(url)
            week = int(url.rsplit("/", 1)[1])
            return [
                {"player_id": "10", "stats": {"pts_half_ppr": 10.0 + week, "pts_ppr": 99.0}},
                # A rostered player with no half-PPR projection, such as a player on a bye.
                {"player_id": "11", "stats": {}},
                {"player_id": "99", "stats": {"pts_half_ppr": 5.0}},
            ]
        return base(url, params)
    return get


def _fetch_projections_ahead(tmp_path, week: int) -> tuple[list, list[str]]:
    import json

    calls: list[str] = []
    fetch_week("1", 2026, week, tmp_path / "raw", tmp_path / "players.json", CLIENT.tz,
               CLIENT.settings.last_regular_week, CLIENT.settings.last_season_week, CLIENT.settings.points_key,
               json_transport(_fake_projections_get(calls)))
    return json.loads((tmp_path / "raw" / "projections_ahead.json").read_text()), calls


def test_fetch_week_saves_the_projections_ahead_of_every_player(tmp_path):
    ahead, calls = _fetch_projections_ahead(tmp_path, 6)
    assert [entry["week"] for entry in ahead] == list(range(7, 18))
    assert [url.rsplit("/", 1)[1] for url in calls if "/projections/nfl/" in url] == [str(w) for w in range(6, 18)]
    # The unrostered player "99" stays, so the waiver board can rank him. A player with no half-PPR projection drops.
    assert ahead[0] == {"week": 7, "projections": {"10": 17.0, "99": 5.0}}


def test_fetch_week_16_saves_one_projections_week_and_week_17_none(tmp_path):
    assert [entry["week"] for entry in _fetch_projections_ahead(tmp_path, 16)[0]] == [17]
    assert _fetch_projections_ahead(tmp_path, 17)[0] == []


def test_load_raw_without_projections_ahead(fixture_raw_dir, tmp_path):
    import shutil

    raw_dir = tmp_path / "raw"
    shutil.copytree(fixture_raw_dir, raw_dir)
    (raw_dir / "projections_ahead.json").unlink()
    assert "projections_ahead" not in load_raw(raw_dir)


def test_fetch_projections_ahead_stops_at_the_last_regular_week():
    # The trade grade reads no week after the last regular week, so the live fetch skips those calls.
    from league.provider import sleeper

    calls: list[str] = []
    ahead = sleeper.fetch_projections_ahead(2026, 6, CLIENT.settings.last_regular_week, CLIENT.settings.points_key,
                                            json_transport(_fake_projections_get(calls)))
    assert [entry.week for entry in ahead] == list(range(7, 15))
    assert [url.rsplit("/", 1)[1] for url in calls] == [str(w) for w in range(7, 15)]
    assert ahead[0].model_dump() == {"week": 7, "projections": {"10": 17.0, "99": 5.0}}


def _live_get(stats):
    """A fake Sleeper body for fetch_live_raw. The stats call gives `stats`, or raises when it is an error."""
    def get(url, params):
        if "/stats/nfl/" in url:
            if isinstance(stats, Exception):
                raise stats
            return stats
        if url.endswith("/state/nfl"):
            return {"season": "2026", "display_week": 7, "season_start_date": "2026-09-09"}
        # The players file is a dict by player id. An empty one keeps the raw model valid.
        if url.endswith("/players/nfl"):
            return {}
        return EMPTY_LEAGUE if url.endswith("/league/1") else []
    return get


def test_a_failed_live_stats_fetch_gives_no_stats_and_a_good_empty_one_gives_an_empty_list(tmp_path):
    import httpx

    from league.provider import sleeper

    # The snapshot names the stats as stale only for a failed fetch, so the two cases must differ in the raw.
    failed, _ = sleeper.fetch_live_raw("1", tmp_path / "players.json", json_transport(
        _live_get(httpx.ConnectError("down"))))
    assert failed.stats is None
    empty, _ = sleeper.fetch_live_raw("1", tmp_path / "players.json", json_transport(_live_get([])))
    assert empty.stats == []
