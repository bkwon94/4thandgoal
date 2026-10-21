"""
Tests for the FastAPI app at the analyze route seam, through the FastAPI test client.
The Sleeper fetch, the slow-source fetchers, the chart read, and the Claude call are fixture-backed callables.
"""
import dataclasses
import functools
import itertools
import json
import math
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest
from fastapi.testclient import TestClient

from cornerstone.analysis import Analysis, SideAnalysis, analyze, code_only
from cornerstone.nflverse import DEPTH_CHARTS_URL, SCHEDULES_URL, cache_path
from cornerstone.rubric import LETTERS, grade, verdict
from cornerstone.sleeper import load_raw
from cornerstone_api.app import GRADE_COUNTS_FILE, create_app
from cornerstone_api.ratelimit import GradeLimiter, seconds_to_midnight
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
        letters = self.claude_letters or [b.final_letter for b in breakdowns]
        far = any(abs(LETTERS.index(l) - LETTERS.index(b.final_letter)) > 1 for l, b in zip(letters, breakdowns))
        if far:
            return code_only(trade, snapshot)
        code = verdict(trade, breakdowns)
        sides = tuple(SideAnalysis(roster_id=b.roster_id, final_letter=l,
                                   reason=None if l == b.final_letter else "Claude reads it one step off.",
                                   analysis="Nico Collins leads the trade in points per game.", cited=[])
                      for l, b in zip(letters, breakdowns))
        return Analysis(breakdowns=breakdowns, code_verdict=code, sides=sides, verdict=code,
                        verdict_differs=False, fallback=False)


class FakeClaude:
    """The Claude call as a callable with no network: the code's letters, one cited fact per side, fixed text."""

    TEXT = "Nico Collins is the best player in the trade. His role is large. The trade changes his roster."

    def __call__(self, system, user, output_model):
        fact = re.findall(r"^- (\d+\.\w+|\d+\.\w+\.\w+): ", user, re.MULTILINE)
        cited = [fid for fid in fact if not fid.endswith(".value")][:1]
        letters = re.findall(r"^Final letter: (\w)", user, re.MULTILINE)
        sides = [{"roster_id": roster_id, "final_letter": letter, "reason": None, "analysis": self.TEXT,
                  "cited": cited}
                 for roster_id, letter in zip((4, 12), letters)]
        return output_model.model_validate(
            {"sides": sides, "verdict": {"choice": "accept", "reason": "The trade is fair for both sides."}})


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
    # Roster 4's user has no metadata avatar, so the fixture gives the thumb URL.
    assert four["avatar"] == (
        "https://sleepercdn.com/avatars/thumbs/578c6b253dd7b4bab45382e1af102204"
    )
    nico = next(p for p in four["players"] if p["player_id"] == "7569")
    assert nico == {"player_id": "7569", "name": "Nico Collins", "position": "WR", "nfl_team": "HOU",
                    "headshot": "https://sleepercdn.com/content/nfl/players/7569.jpg"}
    # A team defense has no headshot, so the form shows the team logo.
    chiefs = next(p for p in four["players"] if p["player_id"] == "KC")
    assert chiefs["headshot"] == "https://sleepercdn.com/images/team_logos/nfl/kc.png"


class RaisingChart:
    """A chart read that counts its calls and raises TypeError, as the Anthropic client does with no API key."""

    def __init__(self):
        self.calls = 0

    def __call__(self, repo, season_start, week, lines):
        self.calls += 1
        raise TypeError("no api key")


def test_teams_skips_the_chart_read(settings, sources):
    chart = RaisingChart()
    response = _client(settings, dataclasses.replace(sources, read_chart=chart)).get(
        "/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 200
    assert chart.calls == 0


def test_a_chart_read_that_raises_makes_analyze_503(settings, sources):
    analyzer = StubAnalyzer()
    chart = RaisingChart()
    response = _client(settings, dataclasses.replace(sources, read_chart=chart), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 503
    assert chart.calls == 1
    assert analyzer.calls == 0


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


def test_the_real_analyzer_with_a_fake_claude_gives_the_document_with_its_text(settings, sources):
    analyzer = functools.partial(analyze, call=FakeClaude())
    doc = _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is False
    assert [side["analysis"] for side in doc["sides"]] == [FakeClaude.TEXT] * 2


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


class MovingClock:
    """An aware datetime in Eastern time that a test moves on, for the minute window and the day of the grades."""

    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, **delta):
        self.now += timedelta(**delta)


def _graded_client(settings, sources, clock, analyzer):
    """A client whose grade limit and general limit both read the moving clock."""
    client = _client(settings, sources, analyzer)
    client.app.state.grade_limiter.clock = clock
    # The general limit reads the same clock, so a test can make more than its 10 requests in one real minute.
    client.app.state.limiter.clock = lambda: clock().timestamp()
    return client


def _uncached():
    """An analyzer whose result falls back. A fallback is not cached, so each repeat is a new grade."""
    return StubAnalyzer(claude_letters=["A", "C"])


def test_the_sixth_grade_in_a_minute_is_429_with_the_minute_text(settings, sources):
    from cornerstone.tunables import GRADES_PER_MINUTE

    client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    for _ in range(GRADES_PER_MINUTE):
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    response = client.post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many grades this minute. Try again later."}
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    # The teams route keeps the general limit, so the form still loads.
    assert client.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 200


def test_the_twenty_first_grade_in_a_day_is_429_across_a_restart(settings, sources):
    from cornerstone.tunables import GRADES_PER_DAY

    clock = MovingClock(NOW)
    first = _graded_client(settings, sources, clock, _uncached())
    for _ in range(GRADES_PER_DAY):
        # Past the minute window each time, so only the day limit can stop a grade.
        clock.advance(seconds=61)
        assert first.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    clock.advance(seconds=61)
    restarted = _graded_client(settings, sources, clock, _uncached())
    response = restarted.post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many grades today. Try again tomorrow."}
    retry_after = int(response.headers["Retry-After"])
    assert 1 <= retry_after <= 86400
    midnight = datetime(2026, 10, 20, 0, 0, tzinfo=ET)
    assert retry_after == math.ceil((midnight - clock()).total_seconds())
    # The next calendar day in Eastern time starts at zero.
    clock.now = midnight
    assert restarted.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200


def test_the_count_file_holds_only_today(settings, sources):
    clock = MovingClock(NOW)
    client = _graded_client(settings, sources, clock, _uncached())
    client.post("/analyze", json=TRADE, headers=HEADERS)
    clock.advance(days=1)
    client.post("/analyze", json=TRADE, headers={**HEADERS, "Fly-Client-IP": "203.0.113.9"})
    path = settings.result_cache_dir / GRADE_COUNTS_FILE
    assert json.loads(path.read_text()) == {"day": "2026-10-20", "counts": {"203.0.113.9": 1}}


def test_a_malformed_count_file_starts_at_zero(settings, sources):
    path = settings.result_cache_dir / GRADE_COUNTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json")
    client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert json.loads(path.read_text())["counts"] == {"testclient": 1}


def test_a_cached_repeat_does_not_count_as_a_grade(settings, sources):
    from cornerstone.tunables import GRADES_PER_MINUTE

    analyzer = StubAnalyzer()
    client = _graded_client(settings, sources, MovingClock(NOW), analyzer)
    for _ in range(GRADES_PER_MINUTE + 1):
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert analyzer.calls == 1


def test_each_fly_client_address_has_its_own_grade_limit(settings, sources):
    from cornerstone.tunables import GRADES_PER_MINUTE

    client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    one = {**HEADERS, "Fly-Client-IP": "203.0.113.1"}
    for _ in range(GRADES_PER_MINUTE):
        client.post("/analyze", json=TRADE, headers=one)
    over = client.post("/analyze", json=TRADE, headers=one)
    other = client.post("/analyze", json=TRADE, headers={**HEADERS, "Fly-Client-IP": "203.0.113.2"})
    assert over.status_code == 429
    assert other.status_code == 200


def test_grades_at_once_on_many_threads_never_pass_the_day_limit(tmp_path):
    from cornerstone.tunables import GRADES_PER_DAY, GRADES_PER_MINUTE

    # Each read of the clock is 61 seconds on, so only the day limit can stop a grade.
    ticks = itertools.count()
    limiter = GradeLimiter(GRADES_PER_MINUTE, GRADES_PER_DAY, tmp_path / GRADE_COUNTS_FILE,
                           clock=lambda: NOW + timedelta(seconds=61 * next(ticks)))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: limiter.hit("203.0.113.1"), range(GRADES_PER_DAY + 5)))
    assert results.count(None) == GRADES_PER_DAY
    assert [r.window for r in results if r is not None] == ["day"] * 5
    assert json.loads((tmp_path / GRADE_COUNTS_FILE).read_text())["counts"] == {"203.0.113.1": GRADES_PER_DAY}


def test_the_seconds_to_midnight_count_the_extra_hour_when_the_clocks_go_back():
    # On 2026-11-01 the clocks go back at 2:00, so 00:30 to midnight is 24.5 real hours.
    assert seconds_to_midnight(datetime(2026, 11, 1, 0, 30, tzinfo=ET)) == 88200


def test_a_failed_count_write_keeps_the_count_in_memory_and_the_grade_runs(settings, sources, monkeypatch, caplog):
    from cornerstone.tunables import GRADES_PER_DAY

    def full_volume(src, dst):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr("cornerstone_api.ratelimit.os.replace", full_volume)
    clock = MovingClock(NOW)
    client = _graded_client(settings, sources, clock, _uncached())
    for _ in range(GRADES_PER_DAY):
        clock.advance(seconds=61)
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    clock.advance(seconds=61)
    response = client.post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many grades today. Try again tomorrow."}
    assert "not writable" in caplog.text
    assert not (settings.result_cache_dir / GRADE_COUNTS_FILE).exists()


def test_a_bad_trade_or_a_week_with_no_chart_does_not_count_as_a_grade(settings, sources, fixture_raw_dir):
    from cornerstone.tunables import GRADES_PER_MINUTE

    # Garrett Wilson is on roster 12, not roster 4.
    bad = {**TRADE, "sides": [{"roster_id": 4, "gives": ["8146"]}, {"roster_id": 12, "gives": ["10236"]}]}
    no_chart = Sources(
        fetch_sleeper=lambda league_id, players_cache: (load_raw(fixture_raw_dir), FETCHED),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines: None, clock=lambda: NOW)
    bad_client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    no_chart_client = _graded_client(settings, no_chart, MovingClock(NOW), _uncached())
    for _ in range(GRADES_PER_MINUTE + 1):
        assert bad_client.post("/analyze", json=bad, headers=HEADERS).status_code == 422
        assert no_chart_client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 503
    assert not (settings.result_cache_dir / GRADE_COUNTS_FILE).exists()
    assert bad_client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200


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


# Every source that the refresh fetches, in the order of the refresh.
ALL_SOURCES = ["schedules", "depth charts", "id map", "injuries"]


def _fixture_fetch(fixture_nflverse_dir, asked):
    """A fetch that records each URL and gives the fixture file of the same name."""
    def fetch(url):
        asked.append(url)
        return (fixture_nflverse_dir / url.rsplit("/", 1)[-1]).read_bytes()
    return fetch


def test_a_refresh_fetches_every_source_even_on_a_fresh_cache(settings, sources, fixture_nflverse_dir):
    asked = []
    refreshing = dataclasses.replace(sources, fetch_nflverse=_fixture_fetch(fixture_nflverse_dir, asked))
    response = _client(settings, refreshing).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == {"refreshed": ALL_SOURCES, "stale": []}
    assert len(asked) == len(ALL_SOURCES)


def _aged(repo, url, seconds=2 * 24 * 60 * 60):
    """Make the cached file of `url` older by `seconds`. The default is two days."""
    path = cache_path(repo / "data" / "cache" / "nflverse", url, 2026)
    old = time.time() - seconds
    os.utime(path, (old, old))
    return path


def test_a_refresh_fetches_a_source_one_hour_old(settings, sources, fixture_nflverse_dir):
    # The cron can start late, so a file 23 hours old must still refresh at 06:00.
    path = _aged(settings.repo, SCHEDULES_URL, 60 * 60)
    asked = []
    refreshing = dataclasses.replace(sources, fetch_nflverse=_fixture_fetch(fixture_nflverse_dir, asked))
    response = _client(settings, refreshing).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert "schedules" in response.json()["refreshed"]
    assert SCHEDULES_URL in asked
    assert time.time() - path.stat().st_mtime < 60


def test_a_failed_refresh_fetch_is_stale_and_keeps_the_old_cache(settings, sources):
    path = _aged(settings.repo, DEPTH_CHARTS_URL)
    before = path.read_bytes()

    def fetch(url):
        raise httpx.ConnectError("down")

    failing = dataclasses.replace(sources, fetch_nflverse=fetch)
    response = _client(settings, failing).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert response.json() == {"refreshed": [], "stale": ["depth charts"]}
    assert path.read_bytes() == before


def test_a_refresh_with_no_chart_for_the_week_lists_the_chart_as_stale(settings, sources, fixture_nflverse_dir):
    no_chart = dataclasses.replace(sources, read_chart=lambda repo, season_start, week, lines: None,
                                   fetch_nflverse=_fixture_fetch(fixture_nflverse_dir, []))
    response = _client(settings, no_chart).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert response.json() == {"refreshed": ALL_SOURCES, "stale": ["chart"]}


def test_a_refresh_with_a_chart_read_that_raises_lists_the_chart_once(settings, sources, fixture_nflverse_dir):
    def read_chart(repo, season_start, week, lines):
        raise TypeError("no api key")

    raising = dataclasses.replace(sources, read_chart=read_chart,
                                  fetch_nflverse=_fixture_fetch(fixture_nflverse_dir, []))
    response = _client(settings, raising).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert response.json() == {"refreshed": ALL_SOURCES, "stale": ["chart"]}


def test_a_refresh_needs_the_passphrase(settings, sources):
    response = _client(settings, sources).post("/refresh", params={"season": 2026})
    assert response.status_code == 401
    assert response.content == b""
