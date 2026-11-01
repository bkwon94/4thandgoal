"""
Tests for the trending bucket of the waiver board and the fetch of the trending file.
They feed a fake Sleeper client at the fetch seam and hand-set counts on the week 6 raw at the engine seam.
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone.config import cornerstone_config
from cornerstone.provider import sleeper
from cornerstone.sleeper import fetch_week, load_raw
from cornerstone.waiver import waiver_board

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))
# The league config the builds and fetches of these tests read.
CONFIG = cornerstone_config()

TRENDING_URL = "https://api.sleeper.app/v1/players/nfl/trending/add"
# The league fields that the raw model needs, with no rosters, slots, or scoring.
EMPTY_LEAGUE = {"roster_positions": [], "scoring_settings": {},
                "settings": {"last_scored_leg": 0, "reserve_slots": 0, "waiver_budget": 100}}


def _fake_trending_get(calls: list[tuple[str, object]]):
    """A fake of sleeper._get. It gives two trending rows and an empty body for every other call."""
    def get(client, url, params=None):
        calls.append((url, params))
        if url == TRENDING_URL:
            return [{"player_id": "4046", "count": 41200}, {"player_id": "NYJ", "count": 9}]
        if url.endswith("/state/nfl"):
            return {"season": "2026", "display_week": 6, "season_start_date": "2026-09-09"}
        if url.endswith("/players/nfl"):
            return {}
        return EMPTY_LEAGUE if url.endswith("/league/1") else []
    return get


def test_the_week_fetch_saves_the_trending_file(tmp_path, monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(sleeper, "_get", _fake_trending_get(calls))
    fetch_week("1", 2026, 6, tmp_path / "raw", tmp_path / "players.json", CONFIG.tz)
    saved = json.loads((tmp_path / "raw" / "trending.json").read_text())
    assert saved == [{"player_id": "4046", "count": 41200}, {"player_id": "NYJ", "count": 9}]
    assert [dict(params) for url, params in calls if url == TRENDING_URL] == [{"lookback_hours": 24, "limit": 50}]
    assert load_raw(tmp_path / "raw").file_json("trending") == saved


def _player(position: str, name: str, team: str = "KC") -> dict:
    return {"position": position, "team": team, "status": "Active", "active": True, "full_name": name}


def _raw(fixture_raw_dir, players: dict[str, dict], counts: dict[str, int]) -> dict:
    """The week 6 raw with `players` added to the players file and one trending row per ID in `counts`."""
    raw = load_raw(fixture_raw_dir)
    raw.players = {**raw.players, **players}
    raw.trending = [{"player_id": pid, "count": count} for pid, count in counts.items()]
    return raw


def _trending(raw) -> list[str]:
    return [p.player_id for p in waiver_board(raw, 6, BUILT).buckets["trending"]]


def test_the_trending_bucket_follows_the_counts_and_skips_rostered_players(fixture_raw_dir):
    rostered = load_raw(fixture_raw_dir).rosters[0].players[0]
    # Eight free agents at four positions, two each, so the per-position cap never stops one.
    positions = ("RB", "WR", "TE", "QB")
    players = {f"8000{i}": _player(positions[i % 4], f"Free Agent {i}") for i in range(8)}
    # The rostered player looks like a pool player in every other way, so only his roster keeps him out.
    players[rostered] = _player("RB", "Rostered Back")
    counts = {"80003": 900, "80000": 41200, "80006": 75, "80001": 5000, "80004": 300,
              "80007": 12, "80002": 2200, rostered: 99999}
    # 80005 has no trending row, so seven players have a count and the rostered player is out.
    assert _trending(_raw(fixture_raw_dir, players, counts)) == [
        "80000", "80001", "80002", "80003", "80004", "80006", "80007"]


def test_a_player_in_best_adds_and_trending_shows_in_both(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("WR", "Hot Hand")}, {"80001": 41200})
    raw.projections_ahead = [{"week": w, "projections": {"80001": 12.0}} for w in range(7, 18)]
    buckets = waiver_board(raw, 6, BUILT).buckets
    assert [p.player_id for p in buckets["best_adds"]] == ["80001"]
    assert [p.player_id for p in buckets["trending"]] == ["80001"]


def test_a_week_with_no_trending_file_gives_an_empty_bucket(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("WR", "Free Agent")}, {})
    raw.trending = None
    assert _trending(raw) == []


def test_every_trending_count_is_a_fact_with_the_digits_in_its_numbers(fixture_raw_dir):
    players = {"80001": _player("WR", "Hot Hand"), "80002": _player("TE", "Big Tight")}
    trending = waiver_board(_raw(fixture_raw_dir, players, {"80001": 41200, "80002": 7}), 6, BUILT).buckets["trending"]
    assert [(p.trending_count, [f.model_dump() for f in p.facts]) for p in trending] == [
        (41200, [{"id": "WV.trending.80001", "text": "Hot Hand was added in 41200 Sleeper leagues in the last day.",
                  "numbers": ["41200"], "teams": [], "players": ["Hot Hand"]}]),
        (7, [{"id": "WV.trending.80002", "text": "Big Tight was added in 7 Sleeper leagues in the last day.",
              "numbers": ["7"], "teams": [], "players": ["Big Tight"]}]),
    ]


def test_a_top_kicker_and_a_top_defense_by_count_stay_out_of_trending(fixture_raw_dir):
    players = {"80001": _player("K", "Big Leg"), "NYJ": _player("DEF", "Jets", team="NYJ"),
               "80002": _player("WR", "Hot Hand")}
    players["NYJ"]["status"] = None
    raw = _raw(fixture_raw_dir, players, {"80001": 90000, "NYJ": 80000, "80002": 41200})
    assert _trending(raw) == ["80002"]
