"""
Tests for the FastAPI app at the analyze route seam, through the FastAPI test client.
The Sleeper fetch, the slow-source fetchers, the chart read, and the Claude call are fixture-backed callables.
"""
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from cornerstone.rubric import LETTERS, Breakdown, grade, verdict
from cornerstone.sleeper import load_raw
from cornerstone_api.app import create_app
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources

ET = ZoneInfo("America/New_York")
FETCHED = datetime(2026, 10, 19, 9, 30, tzinfo=ET)
# Monday night before the week 7 cutoff, so the trade week and the chart week are 6.
NOW = datetime(2026, 10, 19, 12, 0, tzinfo=ET)
PASSPHRASE = "cornerstone-test"
# The response fixture shared with the site repo. The route's output must keep its shape.
RESPONSE_FIXTURE = Path(__file__).parent / "fixtures" / "api" / "analyze-response.json"
HEADERS = {"X-League-Passphrase": PASSPHRASE}


def _no_network(url):
    raise AssertionError(f"network call to {url}")


def _no_history_fetch(league_id, season, week, out_dir):
    raise AssertionError(f"network call for history week {week}")


@pytest.fixture
def repo(tmp_path, fixture_history_root, fixture_nflverse_dir):
    """A repo with the week 6 history and a fresh nflverse cache."""
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached)
    return tmp_path


@pytest.fixture
def sources(fixture_raw_dir, chart_week6):
    return Sources(
        fetch_sleeper=lambda league_id, players_cache: (load_raw(fixture_raw_dir), FETCHED),
        fetch_nflverse=_no_network,
        fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines: chart_week6,
        clock=lambda: NOW,
    )


@pytest.fixture
def settings(repo):
    return Settings(passphrase=PASSPHRASE, repo=repo, result_cache_dir=repo / "results")


@dataclass
class StubSide:
    final_letter: str
    reason: str | None
    analysis: str


@dataclass
class StubVerdict:
    choice: str
    reason: str
    differs: bool


@dataclass
class StubAnalysis:
    breakdowns: tuple[Breakdown, Breakdown]
    sides: tuple[StubSide, StubSide]
    verdict: StubVerdict
    fallback: bool


class StubAnalyzer:
    """The Claude call as a plain function: the code's grade and verdict, plus a fixed analysis text.

    `claude_letters` are the final letters Claude gives. One more than a step from the code's letter falls back,
    so the code's letters and verdict stand and the analysis reads "Analysis unavailable".
    """

    def __init__(self, claude_letters=None):
        self.calls = 0
        self.claude_letters = claude_letters

    def __call__(self, trade, snapshot):
        self.calls += 1
        breakdowns = grade(trade, snapshot)
        code = verdict(trade, breakdowns)
        letters = self.claude_letters or [b.final_letter for b in breakdowns]
        far = any(abs(LETTERS.index(l) - LETTERS.index(b.final_letter)) > 1 for l, b in zip(letters, breakdowns))
        if far:
            sides = tuple(StubSide(b.final_letter, None, "Analysis unavailable") for b in breakdowns)
        else:
            sides = tuple(StubSide(l, None if l == b.final_letter else "Claude reads it one step off.",
                                   "Nico Collins leads the trade in points per game.")
                          for l, b in zip(letters, breakdowns))
        return StubAnalysis(breakdowns, sides, StubVerdict(code.choice, code.reason, False), fallback=far)


# Nico Collins for Dalton Kincaid and Garrett Wilson, asked by roster 4.
TRADE = {"season": 2026, "sides": [{"roster_id": 4, "gives": ["7569"]},
                                   {"roster_id": 12, "gives": ["10236", "8146"]}], "asker": 4}


def _client(settings, sources, analyzer=None):
    return TestClient(create_app(settings, sources=sources, analyzer=analyzer))


def test_health_needs_no_passphrase(settings, sources):
    response = _client(settings, sources).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _team(body, roster_id):
    return next(team for team in body["teams"] if team["roster_id"] == roster_id)


def test_teams_lists_each_roster_with_its_players_for_the_form(settings, sources):
    response = _client(settings, sources).get("/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert len(body["teams"]) == 12
    four = _team(body, 4)
    assert four["team"] and four["manager"]
    nico = next(p for p in four["players"] if p["player_id"] == "7569")
    assert nico == {"player_id": "7569", "name": "Nico Collins", "position": "WR", "nfl_team": "HOU",
                    "headshot": "https://sleepercdn.com/content/nfl/players/7569.jpg"}
    # A team defense has no headshot, so the form shows the team logo.
    chiefs = next(p for p in four["players"] if p["player_id"] == "KC")
    assert chiefs["headshot"] == "https://sleepercdn.com/images/team_logos/nfl/kc.png"


def test_a_wrong_passphrase_is_401_with_no_body(settings, sources):
    response = _client(settings, sources).get("/teams", params={"season": 2026},
                                              headers={"X-League-Passphrase": "wrong"})
    assert response.status_code == 401
    assert response.content == b""


def test_a_missing_passphrase_is_401_with_no_body(settings, sources):
    response = _client(settings, sources).get("/teams", params={"season": 2026})
    assert response.status_code == 401
    assert response.content == b""


def test_a_good_request_returns_the_result_document(settings, sources):
    response = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    four, twelve = doc["trade"]["sides"]
    assert doc["trade"]["asker"] == 4
    assert [p["name"] for p in four["gives"]] == ["Nico Collins"]
    assert [p["name"] for p in four["gets"]] == ["Dalton Kincaid", "Garrett Wilson"]
    assert twelve["gets"][0]["headshot"] == "https://sleepercdn.com/content/nfl/players/7569.jpg"
    assert [side["roster_id"] for side in doc["sides"]] == [4, 12]
    assert [side["start_letter"] for side in doc["sides"]] == ["C", "C"]
    names = [a["name"] for a in doc["sides"][0]["adjusters"]]
    assert names[0] == "roster fit" and names[-1] == "schedule" and len(names) == 6
    assert doc["sides"][0]["analysis"] == "Nico Collins leads the trade in points per game."
    assert doc["verdict"]["for_roster"] == 4
    assert doc["verdict"]["choice"] in ("accept", "counter", "decline") and doc["verdict"]["reason"]
    assert doc["as_of"] == {"chart_week": 6, "stats_through": 5, "rosters_fetched": "2026-10-19T09:30:00-04:00"}
    assert doc["fallback"] is False


def test_the_document_holds_no_trade_value_sum_or_ratio(settings, sources):
    text = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).text
    # The trade values of the three players, the sum of the two, and the ratios never appear.
    for number in ("46.5", "31.5", "27.5", "59", "1.27", "0.78"):
        assert number not in text
    for word in ("value", "ratio", "chart_name"):
        assert f'"{word}' not in text


def test_a_player_not_on_the_giving_roster_is_422_with_the_id(settings, sources):
    analyzer = StubAnalyzer()
    # Garrett Wilson is on roster 12, not roster 4.
    trade = {**TRADE, "sides": [{"roster_id": 4, "gives": ["8146"]}, {"roster_id": 12, "gives": ["10236"]}]}
    response = _client(settings, sources, analyzer).post("/analyze", json=trade, headers=HEADERS)
    assert response.status_code == 422
    assert response.json()["detail"]["player_id"] == "8146"
    assert "8146" in response.json()["detail"]["message"]
    assert analyzer.calls == 0


def test_a_week_with_no_chart_is_503_with_no_grade(settings, fixture_raw_dir):
    analyzer = StubAnalyzer()
    no_chart = Sources(
        fetch_sleeper=lambda league_id, players_cache: (load_raw(fixture_raw_dir), FETCHED),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines: None, clock=lambda: NOW)
    response = _client(settings, no_chart, analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 503
    assert response.json() == {"detail": "The trade value chart for this week is not available."}
    assert analyzer.calls == 0


def test_a_claude_letter_two_steps_off_falls_back_to_the_code_letters(settings, sources):
    analyzer = StubAnalyzer(claude_letters=["A", "C"])
    doc = _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is True
    # The code's final letters stand: C for roster 4, and B for roster 12 after its adjusters.
    assert [side["final_letter"] for side in doc["sides"]] == ["C", "B"]
    assert [side["analysis"] for side in doc["sides"]] == ["Analysis unavailable"] * 2
    assert [side["final_reason"] for side in doc["sides"]] == [None, None]


def test_a_claude_letter_one_step_off_stands_with_its_reason(settings, sources):
    doc = _client(settings, sources, StubAnalyzer(claude_letters=["B", "C"])).post(
        "/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is False
    assert doc["sides"][0]["final_letter"] == "B"
    assert doc["sides"][0]["final_reason"] == "Claude reads it one step off."


def _at(fixture_raw_dir, chart, fetched):
    """Sources whose Sleeper fetch reports the time `fetched`."""
    return Sources(
        fetch_sleeper=lambda league_id, players_cache: (load_raw(fixture_raw_dir), fetched),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines: chart, clock=lambda: NOW)


def test_a_repeat_is_a_cache_hit_with_one_claude_call(settings, fixture_raw_dir, chart_week6):
    analyzer = StubAnalyzer()
    first = _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer)
    # The rosters fetch time moves on every request, but a repeat on unchanged rosters is the same trade.
    later = _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED.replace(minute=55)), analyzer)
    swapped = {**TRADE, "sides": [TRADE["sides"][0], {"roster_id": 12, "gives": ["8146", "10236"]}]}
    one = first.post("/analyze", json=TRADE, headers=HEADERS).json()
    two = later.post("/analyze", json=swapped, headers=HEADERS).json()
    assert analyzer.calls == 1
    assert two == one


def test_the_cache_survives_a_restart(settings, sources):
    _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS)
    restarted = StubAnalyzer()
    response = _client(settings, sources, restarted).post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 200
    assert restarted.calls == 0


def test_a_repeat_an_hour_later_on_unchanged_rosters_is_a_cache_hit(settings, fixture_raw_dir, chart_week6):
    analyzer = StubAnalyzer()
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED.replace(hour=10)), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 1


def _without_a_bench_player(fixture_raw_dir, chart, roster_id):
    """Sources whose Sleeper data drops one player, who is not in the trade, from a roster."""
    raw = load_raw(fixture_raw_dir)
    roster = next(r for r in raw["rosters"] if r["roster_id"] == roster_id)
    roster["players"] = roster["players"][:-1]
    return Sources(
        fetch_sleeper=lambda league_id, players_cache: (raw, FETCHED),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines: chart, clock=lambda: NOW)


def test_a_changed_roster_or_another_asker_misses_the_cache(settings, fixture_raw_dir, chart_week6):
    analyzer = StubAnalyzer()
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    _client(settings, _without_a_bench_player(fixture_raw_dir, chart_week6, 12), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer).post(
        "/analyze", json={**TRADE, "asker": 12}, headers=HEADERS)
    assert analyzer.calls == 3


def test_a_fallback_is_not_cached_so_a_repeat_tries_claude_again(settings, sources):
    analyzer = StubAnalyzer(claude_letters=["A", "C"])
    client = _client(settings, sources, analyzer)
    client.post("/analyze", json=TRADE, headers=HEADERS)
    client.post("/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 2


def test_past_the_rate_limit_the_route_is_429_with_a_retry_after(settings, sources):
    from cornerstone.tunables import RATE_LIMIT_PER_MINUTE

    client = _client(settings, sources)
    for _ in range(RATE_LIMIT_PER_MINUTE):
        # Wrong guesses count too, so a stranger cannot loop through passphrases.
        assert client.get("/teams", params={"season": 2026}).status_code == 401
    response = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    assert client.get("/health").status_code == 200


def test_each_fly_client_address_has_its_own_rate_limit(settings, sources):
    from cornerstone.tunables import RATE_LIMIT_PER_MINUTE

    client = _client(settings, sources)
    # Behind the Fly proxy every request shares one peer address, so the header tells the clients apart.
    for _ in range(RATE_LIMIT_PER_MINUTE):
        client.get("/teams", params={"season": 2026}, headers={**HEADERS, "Fly-Client-IP": "203.0.113.1"})
    over = client.get("/teams", params={"season": 2026}, headers={**HEADERS, "Fly-Client-IP": "203.0.113.1"})
    other = client.get("/teams", params={"season": 2026}, headers={**HEADERS, "Fly-Client-IP": "203.0.113.2"})
    assert over.status_code == 429
    assert other.status_code == 200


@pytest.mark.parametrize("origin", ["https://cpcfantasy.com", "http://localhost:5173", "http://localhost:3000"])
def test_cors_allows_the_site_and_localhost(settings, sources, origin):
    response = _client(settings, sources).options("/analyze", headers={
        "Origin": origin, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-League-Passphrase, Content-Type"})
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == origin


def test_cors_refuses_another_origin(settings, sources):
    response = _client(settings, sources).options("/analyze", headers={
        "Origin": "https://example.com", "Access-Control-Request-Method": "POST"})
    assert "Access-Control-Allow-Origin" not in response.headers


def _shape(value):
    """The keys of a JSON value, all the way down. A list has the shape of its first item, and a leaf has none."""
    if isinstance(value, dict):
        return {key: _shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_shape(value[0])] if value else []
    return None


def _same_shape(actual, expected):
    """Whether `actual` has the shape of `expected`. An empty list in `expected` matches any list."""
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and actual.keys() == expected.keys()
                and all(_same_shape(actual[key], expected[key]) for key in expected))
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        return not expected or all(_same_shape(item, expected[0]) for item in actual)
    return not isinstance(actual, (dict, list))


def test_a_good_request_returns_the_document_in_the_fixture_shape(settings, sources):
    doc = _client(settings, sources, StubAnalyzer(claude_letters=["B", "C"])).post(
        "/analyze", json=TRADE, headers=HEADERS).json()
    fixture = json.loads(RESPONSE_FIXTURE.read_text(encoding="utf-8"))
    # The fixture's empty lists, such as stale, match any list, because a live run may fill them.
    assert _same_shape(doc, _shape(fixture))
    # Every item of a list has the shape of the fixture's first item, so no side or adjuster drops a key.
    for side in doc["sides"]:
        assert _shape(side) == _shape(fixture["sides"][0])
        for adjuster in side["adjusters"]:
            assert _shape(adjuster) == _shape(fixture["sides"][0]["adjusters"][0])


# The keys whose numbers are ids, weeks, steps, or the stamp. No other number may appear in the document.
NUMBER_KEYS = {"roster_id", "asker", "for_roster", "step", "chart_week", "stats_through"}
# The strings that may hold digits: ids, URLs, the stamp, and the names that managers and Sleeper set.
DIGIT_STRING_KEYS = {"player_id", "headshot", "rosters_fetched", "team", "name"}


def _digits_outside_ids(value, key=None):
    """The numbers and the strings with digits under any key that may not hold them."""
    if isinstance(value, dict):
        return [found for k, item in value.items() for found in _digits_outside_ids(item, k)]
    if isinstance(value, list):
        return [found for item in value for found in _digits_outside_ids(item, key)]
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [] if key in NUMBER_KEYS else [(key, value)]
    return [] if key in DIGIT_STRING_KEYS or not re.search(r"\d", value) else [(key, value)]


def test_the_document_has_no_number_outside_ids_weeks_steps_and_the_stamp(settings, sources):
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert _digits_outside_ids(doc) == []


def test_a_season_that_is_not_in_progress_is_422(settings, sources):
    response = _client(settings, sources).get("/teams", params={"season": 2025}, headers=HEADERS)
    assert response.status_code == 422
    assert response.json() == {"detail": "The season 2025 is not in progress."}


def test_settings_from_the_environment_need_a_passphrase(monkeypatch, tmp_path):
    monkeypatch.delenv("CORNERSTONE_PASSPHRASE", raising=False)
    with pytest.raises(RuntimeError, match="CORNERSTONE_PASSPHRASE"):
        Settings.from_env()
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE", "secret")
    monkeypatch.setenv("CORNERSTONE_REPO", str(tmp_path))
    settings = Settings.from_env()
    assert settings.passphrase == "secret"
    assert "secret" not in repr(settings)
    assert settings.result_cache_dir == tmp_path.resolve() / "data" / "cache" / "results"
    assert "https://cpcfantasy.com" in settings.allowed_origins
