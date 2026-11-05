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
from conftest import strip_trend_numbers
from cpc import FIXTURE_LEAGUE, cli_root, cpc_client, four_week
from fastapi.testclient import TestClient

from analyzer.adjusters import INJURY, ROSTER_FIT, SCHEDULE, TREND
from analyzer.analysis import (
    Analysis,
    SideAnalysis,
    _allowed,
    _breakdown_text,
    _letter_failures,
    _prose_failures,
    analyze,
    code_only,
)
from analyzer.cache import cache_key, finder_cache_key
from analyzer.finder import find_win_wins
from analyzer.finder_reasons import FinderReasonsOut, check_reasons, trade_facts, write_reasons
from analyzer.ratelimit import GradeLimiter, seconds_to_midnight
from analyzer.routes import result_document
from analyzer.rubric import BAND_REASONS, LETTERS, ProposedTrade, grade, verdict
from analyzer.tunables import GRADES_PER_MINUTE
from cornerstone_api.app import GRADE_COUNTS_FILE, create_app, load_clients
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources
from league.client import ClientError
from league.live import RefreshResult
from league.nflverse import CACHE_MAX_AGE_SECONDS, DEPTH_CHARTS_URL, SCHEDULES_URL, cache_path
from league.paths import client_dir, league_file
from league.player_ids import is_def
from league.provider.raw import RawLeague
from league.provider.sleeper import league_settings, load_raw
from league.ranks import recent_points_per_game
from league.snapshot import SnapshotPlayer
from league.tunables import TEAMS_CACHE_SECONDS

ET = ZoneInfo("America/New_York")
# The client the builds and fetches of these tests read.
CLIENT = cpc_client()
FETCHED = datetime(2026, 10, 19, 9, 30, tzinfo=ET)
# Monday night before the week 7 cutoff, so the trade week and the chart week are 6.
NOW = datetime(2026, 10, 19, 12, 0, tzinfo=ET)
PASSPHRASE = "cornerstone-test"
# The response fixture shared with the site repo. The route's output must keep its shape.
RESPONSE_FIXTURE = Path(__file__).parent / "fixtures" / "api" / "analyze-response.json"
# The finder response fixture shared with the site repo, with three trades.
FIND_FIXTURE = Path(__file__).parent / "fixtures" / "api" / "find-response.json"
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


def _here(sources: Sources, settings: Settings) -> Sources:
    """The sources with the client of the test folder, so a snapshot reads and writes only that folder."""
    return dataclasses.replace(sources, client=cpc_client(at=settings.repo))


@pytest.fixture
def sources(fixture_raw_dir, chart_week6):
    return Sources(
        fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), FETCHED),
        fetch_nflverse=_no_network,
        fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines, **_: chart_week6,
        clock=lambda: NOW, client=CLIENT,
    )


@pytest.fixture
def settings(repo):
    return Settings(passphrases={"cpc": PASSPHRASE}, repo=repo, result_cache_dir=repo / "results")


# The bullets of each side in a stub analysis.
BULLETS = ["Nico Collins leads the trade in points per game.", "His role is large."]


class StubAnalyzer:
    """The Claude call as a plain function: the code's grade and verdict, plus fixed bullets.

    `claude_letters` are the final letters Claude gives. One more than a step from the code's letter falls back,
    so the code's letters and verdict stand and each side has no bullets.
    """

    def __init__(self, claude_letters=None):
        self.calls = 0
        self.claude_letters = claude_letters

    def __call__(self, trade, snapshot):
        self.calls += 1
        breakdowns = grade(trade, snapshot)
        letters = self.claude_letters or [b.final_letter for b in breakdowns]
        far = any(
            abs(LETTERS.index(letter) - LETTERS.index(b.final_letter)) > 1 for letter, b in zip(letters, breakdowns)
        )
        if far:
            return code_only(trade, snapshot)
        code = verdict(trade, breakdowns)
        sides = tuple(SideAnalysis(roster_id=b.roster_id, final_letter=letter,
                                   reason=None if letter == b.final_letter else "Claude reads it one step off.",
                                   bullets=BULLETS, cited=[])
                      for letter, b in zip(letters, breakdowns))
        return Analysis(breakdowns=breakdowns, code_verdict=code, sides=sides, verdict=code,
                        verdict_differs=False, fallback=False)


class FakeClaude:
    """The Claude call as a callable with no network: the code's letters, one cited fact per side, fixed bullets."""

    BULLETS = ("Nico Collins is the best player in the trade.", "His role is large.", "The trade changes his roster.")

    def __call__(self, system, user, output_model):
        fact = re.findall(r"^- (\d+\.\w+|\d+\.\w+\.\w+): ", user, re.MULTILINE)
        cited = [fid for fid in fact if not fid.endswith(".value")][:1]
        letters = re.findall(r"^Final letter: (\w)", user, re.MULTILINE)
        sides = [{"roster_id": roster_id, "final_letter": letter, "reason": None, "bullets": list(self.BULLETS),
                  "cited": cited}
                 for roster_id, letter in zip((4, 12), letters)]
        return output_model.model_validate(
            {"sides": sides, "verdict": {"choice": "accept", "reason": "The trade is fair for both sides."}})


# Nico Collins for Dalton Kincaid and Garrett Wilson, asked by roster 4.
def _sides(four_gives: list[str], twelve_gives: list[str]) -> list[dict]:
    """The sides of a trade of roster 4 and roster 12, each given player sent to the other side."""
    return [{"roster_id": 4, "gives": [{"player_id": pid, "to": 12} for pid in four_gives]},
            {"roster_id": 12, "gives": [{"player_id": pid, "to": 4} for pid in twelve_gives]}]


TRADE = {"season": 2026, "sides": _sides(["7569"], ["10236", "8146"]), "asker": 4}


def _cpc(sources):
    """The sources of each client the test app serves, by slug: only cpc."""
    return {"cpc": sources}


def _client(settings, sources, analyzer=None):
    return TestClient(create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), analyzer=analyzer))


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

    def __call__(self, repo, season_start, week, lines, chart):
        self.calls += 1
        raise TypeError("no api key")


def test_teams_skips_the_chart_read(settings, sources):
    chart = RaisingChart()
    response = _client(settings, dataclasses.replace(sources, read_chart=chart)).get(
        "/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 200
    assert chart.calls == 0


class CountingSleeper:
    """The fixture Sleeper fetch, with a count of its calls."""

    def __init__(self, fixture_raw_dir):
        self.fixture_raw_dir = fixture_raw_dir
        self.calls = 0

    def __call__(self, league_id):
        self.calls += 1
        return load_raw(self.fixture_raw_dir), FETCHED


class MonotonicClock:
    """A monotonic clock in seconds that a test moves on, for the window of the teams cache."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_a_second_teams_request_in_the_window_answers_from_memory(settings, sources, fixture_raw_dir):
    sleeper = CountingSleeper(fixture_raw_dir)
    client = _client(settings, dataclasses.replace(sources, fetch_sleeper=sleeper))
    first = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    second = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert first.status_code == second.status_code == 200
    assert second.json() == first.json()
    assert sleeper.calls == 1


def test_a_teams_request_past_the_window_builds_again(settings, sources, fixture_raw_dir):
    sleeper = CountingSleeper(fixture_raw_dir)
    client = _client(settings, dataclasses.replace(sources, fetch_sleeper=sleeper))
    clock = MonotonicClock()
    client.app.state.served["cpc"].teams_cache.clock = clock
    client.get("/teams", params={"season": 2026}, headers=HEADERS)
    clock.now += TEAMS_CACHE_SECONDS - 1
    client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert sleeper.calls == 1
    clock.now += 2
    response = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 200
    assert sleeper.calls == 2


def test_two_first_teams_requests_make_one_build(settings, sources, fixture_raw_dir):
    sleeper = CountingSleeper(fixture_raw_dir)
    client = _client(settings, dataclasses.replace(sources, fetch_sleeper=sleeper))
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: client.get("/teams", params={"season": 2026}, headers=HEADERS), range(2)))
    assert [r.status_code for r in responses] == [200, 200]
    assert sleeper.calls == 1


def test_the_teams_build_fetches_no_slow_source_and_no_history(settings, sources):
    # Every nflverse file is two days old, so a slow-source refresh would fetch each one again.
    old = time.time() - 2 * 24 * 3600
    for cached in (settings.repo / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached, (old, old))
    nflverse, history = [], []
    counting = dataclasses.replace(
        sources, fetch_nflverse=lambda url: nflverse.append(url) or b"",
        fetch_history_week=lambda league_id, season, week, out_dir: history.append(week))
    response = _client(settings, counting).get("/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 200
    assert len(response.json()["teams"]) == 12
    assert nflverse == []
    assert history == []


def test_a_trade_input_error_from_analyze_clears_the_teams_of_its_season(settings, sources, fixture_raw_dir):
    sleeper = CountingSleeper(fixture_raw_dir)
    client = _client(settings, dataclasses.replace(sources, fetch_sleeper=sleeper), StubAnalyzer())
    client.get("/teams", params={"season": 2026}, headers=HEADERS)
    # Garrett Wilson is on roster 12, not roster 4, so the form showed a roster that Sleeper no longer has.
    trade = {**TRADE, "sides": _sides(["8146"], ["10236"])}
    assert client.post("/analyze", json=trade, headers=HEADERS).status_code == 422
    assert sleeper.calls == 2
    assert client.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 200
    assert sleeper.calls == 3


def test_a_season_that_is_not_in_progress_is_never_cached(settings, sources, fixture_raw_dir):
    sleeper = CountingSleeper(fixture_raw_dir)
    client = _client(settings, dataclasses.replace(sources, fetch_sleeper=sleeper))
    for _ in range(2):
        assert client.get("/teams", params={"season": 2025}, headers=HEADERS).status_code == 422
    assert sleeper.calls == 2


def test_the_start_up_refresh_refreshes_the_current_season_once(settings, sources, fixture_raw_dir, monkeypatch):
    calls = []
    monkeypatch.setattr("cornerstone_api.sources.refresh_sources",
                        lambda season, now, week, **kwargs: calls.append((season, kwargs["max_age_seconds"])))
    sleeper = CountingSleeper(fixture_raw_dir)
    app = create_app(settings, [CLIENT], sources=_cpc(_here(dataclasses.replace(sources, fetch_sleeper=sleeper), settings)),
                     refresh_on_start=True)
    app.state.refresh_thread.join(timeout=10)
    # The refresh keeps the normal max age, so it fetches only the files older than a day.
    assert calls == [(2026, CACHE_MAX_AGE_SECONDS)]
    assert sleeper.calls == 1


def test_the_start_up_refresh_is_off_unless_the_app_asks_for_it(settings, sources, monkeypatch):
    calls = []
    monkeypatch.setattr(Sources, "refresh_current_season", lambda self, **kwargs: calls.append(self.client.folder))
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)))
    assert app.state.refresh_thread is None
    assert calls == []


def test_a_start_up_refresh_that_raises_logs_and_the_app_still_answers(settings, sources, monkeypatch, caplog):
    def raising(self, **kwargs):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(Sources, "refresh_current_season", raising)
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), refresh_on_start=True)
    app.state.refresh_thread.join(timeout=10)
    assert "start-up refresh of the slow sources of cpc failed (ConnectError)" in caplog.text
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 200


def test_a_chart_read_that_raises_grades_the_trade_with_no_chart(settings, sources):
    # A chart read that raises gives no chart, and a week with no chart grades from the adjusters alone.
    analyzer = StubAnalyzer()
    chart = RaisingChart()
    response = _client(settings, dataclasses.replace(sources, read_chart=chart), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["as_of"]["no_chart"] is True
    assert chart.calls == 1
    assert analyzer.calls == 1


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
    # Each traded player carries his Season rank. A Recent rank 12 spots or more off it shows, else it is null.
    # Kincaid is TE10 by total points and TE39 by points per game over the last 4 weeks, so his Recent rank shows.
    assert [(p["season_rank"], p["recent_rank"]) for p in four["gives"] + four["gets"]] == [
        ("WR20", None), ("TE10", "TE39"), ("WR11", None)]
    assert [side["roster_id"] for side in doc["sides"]] == [4, 12]
    # The deal row comes first, in plain words that name no source. One player for two gets a discount.
    assert [side["factors"][0] for side in doc["sides"]] == [{
        "name": "deal", "lean": "even",
        "reason": "What you get and what you give are about even, after a discount on the side with more players.",
    }] * 2
    # The upside and the handcuff say nothing for this trade, so their rows hide.
    names = [f["name"] for f in doc["sides"][0]["factors"]]
    assert names == ["deal", "roster fit", "standing", "trend and usage", "injury", "schedule"]
    assert doc["sides"][0]["bullets"] == BULLETS
    # Roster 12 gets the highest-value player in the trade and keeps its step up, so the other side does better.
    assert doc["decision"] == {"for_roster": 4, "answer": "not_as_is",
                               "reason": "The other side does better, so ask for more.", "differs": False}
    # The document leads with the decision, and no letter or step reaches it.
    assert list(doc)[:4] == ["trade", "decision", "fairness", "sides"]
    assert list(doc["sides"][0]) == ["roster_id", "bullets", "factors"]
    assert list(doc["sides"][0]["factors"][0]) == ["name", "lean", "reason"]
    # The fetch on Monday holds the week 6 stat lines, so the player stats read the 14 known games of week 6.
    # The fixture player file has week 6 rows for 6 of those games, so the usage of 8 games is pending.
    assert doc["as_of"] == {"chart_week": 6, "stats_through": 6, "completed_through": 5,
                            "rosters_fetched": "2026-10-19T09:30:00-04:00",
                            "known_games": {"week": 6, "games": 14, "in_progress": 0, "pending": {"usage": 8}},
                            "no_chart": False, "no_chart_note": None}
    assert doc["fallback"] is False


def test_each_given_player_names_where_he_goes_and_each_got_player_where_he_comes_from(settings, sources):
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    four, twelve = doc["trade"]["sides"]
    assert [(p["player_id"], p["to"]) for p in four["gives"]] == [("7569", 12)]
    assert [(p["player_id"], p["from"]) for p in four["gets"]] == [("10236", 12), ("8146", 12)]
    assert [(p["player_id"], p["to"]) for p in twelve["gives"]] == [("10236", 4), ("8146", 4)]
    assert [(p["player_id"], p["from"]) for p in twelve["gets"]] == [("7569", 4)]


def _gives(pairs: list[tuple[str, int]]) -> list[dict]:
    return [{"player_id": pid, "to": to} for pid, to in pairs]


@pytest.mark.parametrize("four_gives, twelve_gives, message", [
    ([("7569", 7)], [("10236", 4)], "Player 7569 goes to roster 7, which is not a side of the trade"),
    ([("7569", 12)], [("10236", 12)], "Roster 4 gets no player in the trade"),
    ([("7569", 12), ("7569", 12)], [("10236", 4)], "A player can appear only once in a proposed trade"),
    ([("7569", 12), ("4881", 4)], [("10236", 4)], "Player 4881 goes to his own roster 4"),
])
def test_a_trade_with_a_bad_destination_or_a_repeat_is_422_with_a_plain_message(
        settings, sources, four_gives, twelve_gives, message):
    analyzer = StubAnalyzer()
    sides = [{"roster_id": 4, "gives": _gives(four_gives)}, {"roster_id": 12, "gives": _gives(twelve_gives)}]
    response = _client(settings, sources, analyzer).post("/analyze", json={**TRADE, "sides": sides},
                                                         headers=HEADERS)
    assert response.status_code == 422
    assert [error["msg"] for error in response.json()["detail"]] == [f"Value error, {message}"]
    assert analyzer.calls == 0


def test_a_fifth_side_is_422_with_a_plain_message(settings, sources):
    analyzer = StubAnalyzer()
    five = ((4, "7569", 12), (12, "10236", 7), (7, "11628", 3), (3, "4034", 1), (1, "1", 4))
    sides = [{"roster_id": roster_id, "gives": _gives([(pid, to)])} for roster_id, pid, to in five]
    response = _client(settings, sources, analyzer).post("/analyze", json={**TRADE, "sides": sides}, headers=HEADERS)
    assert response.status_code == 422
    message = "Value error, A proposed trade has four sides at most"
    assert [error["msg"] for error in response.json()["detail"]] == [message]
    assert analyzer.calls == 0


# Roster 4 sends Nico Collins to roster 12, roster 12 sends Kincaid to roster 4 and Wilson to roster 7,
# and roster 7 sends Marvin Harrison Jr. to roster 4.
THREE = {"season": 2026, "asker": 4, "sides": [
    {"roster_id": 4, "gives": _gives([("7569", 12)])},
    {"roster_id": 12, "gives": _gives([("10236", 4), ("8146", 7)])},
    {"roster_id": 7, "gives": _gives([("11628", 4)])},
]}


def test_a_three_side_request_grades_with_every_side_in_the_order_of_the_request(settings, sources):
    response = _client(settings, sources, StubAnalyzer()).post("/analyze", json=THREE, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert [side["roster_id"] for side in doc["trade"]["sides"]] == [4, 12, 7]
    assert [side["roster_id"] for side in doc["fairness"]["sides"]] == [4, 12, 7]
    assert [side["roster_id"] for side in doc["sides"]] == [4, 12, 7]
    four, twelve, seven = doc["trade"]["sides"]
    assert [(p["player_id"], p["from"]) for p in four["gets"]] == [("10236", 12), ("11628", 7)]
    assert [(p["player_id"], p["to"]) for p in twelve["gives"]] == [("10236", 4), ("8146", 7)]
    assert [(p["player_id"], p["from"]) for p in seven["gets"]] == [("8146", 12)]
    assert doc["decision"]["for_roster"] == 4
    assert all(len(side["factors"]) == len(doc["sides"][0]["factors"]) for side in doc["sides"])


def test_the_same_gives_with_other_destinations_is_another_cache_key(settings, sources):
    # In a three-side trade the destinations change what each side gets, so they are part of the key.
    swapped = {**THREE, "sides": [
        {"roster_id": 4, "gives": _gives([("7569", 7)])},
        {"roster_id": 12, "gives": _gives([("10236", 4), ("8146", 4)])},
        {"roster_id": 7, "gives": _gives([("11628", 12)])},
    ]}
    snapshot = _here(sources, settings).snapshot(2026)
    assert cache_key(ProposedTrade(**THREE), snapshot) != cache_key(ProposedTrade(**swapped), snapshot)


def test_the_document_holds_no_trade_value_sum_or_ratio(settings, sources):
    text = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).text
    # The trade values of the three players, the sum of the two, and the ratios never appear.
    for number in ("46.5", "31.5", "27.5", "59", "1.27", "0.78"):
        assert number not in text
    for word in ("value", "ratio", "chart_name"):
        assert f'"{word}' not in text


def test_a_player_not_on_the_giving_roster_is_422_with_the_names_and_the_id(settings, sources):
    analyzer = StubAnalyzer()
    # Garrett Wilson is on roster 12, not roster 4.
    trade = {**TRADE, "sides": _sides(["8146"], ["10236"])}
    response = _client(settings, sources, analyzer).post("/analyze", json=trade, headers=HEADERS)
    assert response.status_code == 422
    assert response.json()["detail"]["player_id"] == "8146"
    assert response.json()["detail"]["message"] == "Garrett Wilson is no longer on Pukancun on 3."
    assert analyzer.calls == 0


def _no_chart_sources(fixture_raw_dir):
    return Sources(
        fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), FETCHED),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines, **_: None, clock=lambda: NOW, client=CLIENT)


def test_a_week_with_no_chart_grades_from_the_adjusters_and_says_so(settings, fixture_raw_dir):
    # The chart posts hours after the trade week starts, so the grade runs in that window with no chart.
    analyzer = StubAnalyzer()
    response = _client(settings, _no_chart_sources(fixture_raw_dir), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert analyzer.calls == 1
    note = "This week's player values are not out yet, so both sides start even."
    for side in doc["sides"]:
        assert side["factors"][0] == {"name": "deal", "lean": "even", "reason": note}
    assert doc["as_of"]["chart_week"] is None
    assert doc["as_of"]["no_chart"] is True
    assert doc["as_of"]["no_chart_note"] == note
    assert "chart" in doc["missing"]


def test_a_grade_with_no_chart_and_a_grade_with_the_chart_have_different_keys(settings, sources, fixture_raw_dir):
    # The first chart post of the week must give a fresh grade, not the stored grade with no chart.
    trade = ProposedTrade.model_validate(TRADE)
    with_chart = _here(sources, settings).snapshot(trade.season)
    no_chart = _here(_no_chart_sources(fixture_raw_dir), settings).snapshot(trade.season)
    assert cache_key(trade, no_chart) != cache_key(trade, with_chart)
    assert finder_cache_key(2026, 4, 12, no_chart) != finder_cache_key(2026, 4, 12, with_chart)


def test_a_claude_letter_two_steps_off_falls_back_to_the_code_letters(settings, sources):
    analyzer = StubAnalyzer(claude_letters=["A", "C"])
    doc = _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is True
    # The code's letters and verdict stand, with no bullets. The rows still show, the deal row first.
    assert [side["bullets"] for side in doc["sides"]] == [[], []]
    assert all(side["factors"][0]["name"] == "deal" and len(side["factors"]) == 6 for side in doc["sides"])
    assert doc["decision"]["differs"] is False


def test_a_claude_letter_one_step_off_stands(settings, sources):
    doc = _client(settings, sources, StubAnalyzer(claude_letters=["B", "C"])).post(
        "/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is False
    assert doc["sides"][0]["bullets"] == BULLETS


def _document(settings, sources, breakdowns=None, choice=None):
    """The result document of TRADE from a built analysis, with the breakdowns and the verdict choice changed."""
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    breakdowns = breakdowns(grade(trade, snapshot)) if breakdowns else grade(trade, snapshot)
    code = verdict(trade, breakdowns)
    stands = code if choice is None else code.model_copy(update={"choice": choice})
    sides = tuple(SideAnalysis(roster_id=b.roster_id, final_letter=b.final_letter, reason=None,
                               bullets=BULLETS, cited=[])
                  for b in breakdowns)
    analysis = Analysis(breakdowns=breakdowns, code_verdict=code, sides=sides, verdict=stands,
                        verdict_differs=stands.choice != code.choice, fallback=False)
    return result_document(trade, snapshot, analysis)


@pytest.mark.parametrize("choice, answer", [("accept", "yes"), ("decline", "no"), ("counter", "not_as_is")])
def test_the_answer_maps_from_the_verdict_choice(settings, sources, choice, answer):
    doc = _document(settings, sources, choice=choice)
    assert doc["decision"]["answer"] == answer
    # The code's default for this trade is a counter, so any other choice differs from it.
    assert doc["decision"]["differs"] is (choice != "counter")


@pytest.mark.parametrize("letter, lean, reason", [
    ("A", "for", "You get far more than you give."),
    ("B", "for", "You get more than you give."),
    ("C", "even", "What you get and what you give are about even."),
    ("D", "against", "You give more than you get."),
    ("F", "against", "You give far more than you get."),
])
def test_the_deal_row_maps_from_the_start_letter_in_plain_words(settings, sources, letter, lean, reason):
    doc = _document(settings, sources, breakdowns=lambda bs: tuple(
        b.model_copy(update={"start_letter": letter, "reason": BAND_REASONS[letter]}) for b in bs))
    assert [side["factors"][0] for side in doc["sides"]] == [{"name": "deal", "lean": lean, "reason": reason}] * 2
    assert "chart" not in doc["sides"][0]


def _steps(steps, schedule_lean):
    """Breakdowns with the steps of the first six adjusters of each side and the lean of the schedule set."""
    def rework(breakdowns):
        reworked = []
        for b in breakdowns:
            adjusters = [a.model_copy(update={"step": step}) for a, step in zip(b.adjusters[:6], steps)]
            adjusters.append(b.adjusters[6].model_copy(update={"lean": schedule_lean}))
            reworked.append(b.model_copy(update={"adjusters": adjusters}))
        return tuple(reworked)
    return rework


@pytest.mark.parametrize("schedule_lean", ["for", "against", "even"])
def test_a_factor_lean_maps_from_the_step_and_the_schedule_keeps_its_lean(settings, sources, schedule_lean):
    doc = _document(settings, sources, breakdowns=_steps([1, -1, 0, 1, 1, -1], schedule_lean))
    factors = doc["sides"][0]["factors"][1:]
    assert [f["name"] for f in factors] == ["roster fit", "standing", "trend and usage", "injury", "upside",
                                            "handcuff", "schedule"]
    assert [f["lean"] for f in factors] == ["for", "against", "even", "for", "for", "against", schedule_lean]


def test_a_graded_trade_with_no_upside_hides_the_upside_factor_of_each_side(settings, sources):
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    # No player in TRADE is a star out now or has an opportunity, so the upside row says nothing and hides.
    for side in doc["sides"]:
        assert [f for f in side["factors"] if f["name"] == "upside"] == []


def test_a_silent_row_that_moves_the_grade_still_shows(settings, sources):
    # A row shows when it moves the grade, so a silent upside with a step up stays in the document.
    doc = _document(settings, sources, breakdowns=lambda bs: tuple(
        b.model_copy(update={"adjusters": [a.model_copy(update={"step": 1}) if a.name == "upside" else a
                                           for a in b.adjusters]}) for b in bs))
    assert all([f["lean"] for f in side["factors"] if f["name"] == "upside"] == ["for"] for side in doc["sides"])


def test_a_result_cached_under_another_document_version_never_serves(settings, sources, monkeypatch):
    import analyzer.cache as cache_module

    analyzer = StubAnalyzer()
    monkeypatch.setattr(cache_module, "DOCUMENT_VERSION", 1)
    _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    monkeypatch.setattr(cache_module, "DOCUMENT_VERSION", 2)
    _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 2


def test_the_document_has_the_fairness_block_after_the_decision(settings, sources):
    doc = _document(settings, sources)
    block = doc["fairness"]
    assert list(block) == ["state", "gives_more", "sides"]
    assert [list(side) for side in block["sides"]] == [["roster_id", "reason"]] * 2
    assert [side["roster_id"] for side in block["sides"]] == [4, 12]
    assert block["state"] in ("win_win", "fair", "lopsided")


@pytest.mark.parametrize("letters, state, gives_more", [(["B", "B"], "win_win", None), (["D", "B"], "lopsided", 4)])
def test_the_fairness_block_reads_the_letters_that_stand_after_the_claude_call(settings, sources, letters, state,
                                                                               gives_more):
    # Claude can move a final letter one step. That letter stands, so the fairness block reads it.
    doc = _client(settings, sources, StubAnalyzer(claude_letters=letters)).post(
        "/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is False
    assert doc["fairness"]["state"] == state
    assert doc["fairness"]["gives_more"] == gives_more


def test_the_fairness_text_passes_the_prose_checks_of_the_analysis(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    breakdowns = grade(trade, snapshot)
    names = [*(t.name for t in snapshot.teams.values()), *(p.name for p in snapshot.players.values())]
    breakdown_text = _breakdown_text(breakdowns)
    # Each step up in turn, so the block takes the reason of every adjuster and of the start letter once.
    for index in range(6):
        doc = _document(settings, sources, breakdowns=_steps([int(i == index) for i in range(5)], "even"))
        for side in doc["fairness"]["sides"]:
            text = side["reason"]
            # The checks of the analysis: no trade value, no ratio word, no chart name, and no letter grade.
            assert _prose_failures("fairness", text, _allowed({}, [], breakdown_text), breakdown_text, names) == []
            assert _letter_failures("fairness", text) == []
            assert not re.search(r"\b[A-F]\b", text)


def test_the_cache_key_changes_with_the_document_version(settings, sources, monkeypatch):
    import analyzer.cache as cache_module

    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    # A shape change bumps the version, so a document stored in the old shape never serves again.
    key = cache_key(trade, snapshot)
    monkeypatch.setattr(cache_module, "DOCUMENT_VERSION", cache_module.DOCUMENT_VERSION + 1)
    assert cache_key(trade, snapshot) != key


def _with_week_rows(snapshot, returns, projections_ahead):
    return snapshot.model_copy(update={"returns": returns, "projections_ahead": projections_ahead})


def _outside_player(snapshot, roster_ids):
    """A player on a roster outside `roster_ids`, so no grade of those rosters reads his rows.

    He is a DEF, which has no position rank, so a change to his rows or lines moves no rank of a traded player.
    """
    return next(player for roster_id, players in snapshot.rosters.items() if roster_id not in roster_ids
                for player in players if snapshot.players[player].position == "DEF")


def test_the_cache_key_changes_with_a_rostered_return_week(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    # A new returns file moves a return week inside the week, so the stored grade must miss.
    key = cache_key(trade, _with_week_rows(snapshot, {rostered: 8}, {}))
    assert cache_key(trade, _with_week_rows(snapshot, {rostered: 9}, {})) != key
    assert finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {rostered: 8}, {})) != finder_cache_key(
        2026, 4, 12, _with_week_rows(snapshot, {rostered: 9}, {}))


def test_the_cache_key_changes_with_a_team_in_progress(settings, sources):
    # A grade cached while a game is on says "game in progress", so the final game must miss that grade.
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    on = snapshot.model_copy(update={"in_progress_teams": {"CHI", "ATL"}})
    off = snapshot.model_copy(update={"in_progress_teams": set()})
    assert cache_key(trade, on) != cache_key(trade, off)
    assert finder_cache_key(2026, 4, 12, on) != finder_cache_key(2026, 4, 12, off)


def test_the_cache_key_changes_with_a_projection_ahead_of_a_rostered_player_due_back(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    # The lineup value of a player due back is his projection from the return week on, so a change there must miss.
    key = cache_key(trade, _with_week_rows(snapshot, {rostered: 8}, {rostered: {8: 12.5}}))
    assert cache_key(trade, _with_week_rows(snapshot, {rostered: 8}, {rostered: {8: 13.5}})) != key
    assert finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {rostered: 8}, {rostered: {8: 12.5}})) != (
        finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {rostered: 8}, {rostered: {8: 13.5}})))


def _with_status(snapshot, player, status):
    return snapshot.model_copy(update={"players": {
        **snapshot.players, player: snapshot.players[player].model_copy(update={"injury_status": status})}})


def test_the_cache_key_changes_when_a_rostered_player_moves_into_the_out_set(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = next(player for player in snapshot.rosters[4] if snapshot.players[player].injury_status is None)
    # A player out with no return week counts for his projection ahead from week 14, so the grade reads new rows.
    healthy = _with_week_rows(snapshot, {}, {rostered: {14: 12.5}})
    out = _with_status(healthy, rostered, "Out")
    assert cache_key(trade, out) != cache_key(trade, healthy)
    assert finder_cache_key(2026, 4, 12, out) != finder_cache_key(2026, 4, 12, healthy)
    # A move between two statuses outside the out set keeps the hit.
    assert cache_key(trade, _with_status(healthy, rostered, "Questionable")) == cache_key(trade, healthy)
    # His rows from week 14 on reach the grade now, so a change to them must miss.
    assert cache_key(trade, _with_week_rows(out, {}, {rostered: {14: 13.5}})) != cache_key(trade, out)
    # A returns row of week 14 gives the same week, but the reason says he is due back, so the key must miss.
    assert cache_key(trade, _with_week_rows(out, {rostered: 14}, {rostered: {14: 12.5}})) != cache_key(trade, out)


def test_the_cache_key_changes_with_a_season_mark_on_any_roster(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    outside = _outside_player(snapshot, [4, 12])
    # A season mark zeroes a chart value or opens an opportunity for a teammate, so each mark must miss.
    for player in (rostered, outside):
        marked = snapshot.model_copy(update={"out_for_season": {player}})
        assert cache_key(trade, marked) != cache_key(trade, snapshot)
        assert finder_cache_key(2026, 4, 12, marked) != finder_cache_key(2026, 4, 12, snapshot)


def test_the_cache_key_ignores_the_projection_rows_the_grade_never_reads(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    # Sleeper moves projections daily. A player not due back keeps his recent points, so his rows never reach the grade.
    key = cache_key(trade, _with_week_rows(snapshot, {}, {rostered: {8: 12.5}}))
    assert cache_key(trade, _with_week_rows(snapshot, {}, {rostered: {8: 13.5}})) == key
    # The weeks before the return week are outside the mean too.
    key = cache_key(trade, _with_week_rows(snapshot, {rostered: 9}, {rostered: {8: 12.5}}))
    assert cache_key(trade, _with_week_rows(snapshot, {rostered: 9}, {rostered: {8: 13.5}})) == key


def test_the_cache_key_ignores_the_projection_rows_of_a_player_already_back(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    # A return week at the last completed week is past. The player stat bound can be the trade week itself.
    past = snapshot.as_of.completed_through
    # The returns file keeps a past return week, but a player already back keeps his recent points.
    key = cache_key(trade, _with_week_rows(snapshot, {rostered: past}, {rostered: {past + 1: 12.5}}))
    assert cache_key(trade, _with_week_rows(snapshot, {rostered: past}, {rostered: {past + 1: 13.5}})) == key
    assert finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {rostered: past}, {rostered: {past + 1: 12.5}})) == (
        finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {rostered: past}, {rostered: {past + 1: 13.5}})))


def test_the_cache_key_tells_no_projections_file_from_no_rostered_rows(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    # With no projections file every player keeps his recent points, so the grade differs from an empty file.
    assert cache_key(trade, _with_week_rows(snapshot, {rostered: 8}, None)) != cache_key(
        trade, _with_week_rows(snapshot, {rostered: 8}, {}))


def test_the_cache_key_ignores_a_player_on_neither_roster(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    outside = _outside_player(snapshot, [4, 12])
    # The rows of a player on neither roster never reach the grade, so a change to them keeps the hit.
    key = cache_key(trade, _with_week_rows(snapshot, {outside: 8}, {outside: {7: 12.5}}))
    assert cache_key(trade, _with_week_rows(snapshot, {outside: 9}, {outside: {7: 13.5}})) == key
    assert finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {outside: 8}, {outside: {7: 12.5}})) == (
        finder_cache_key(2026, 4, 12, _with_week_rows(snapshot, {outside: 9}, {outside: {7: 13.5}})))


def _unrostered_with_a_game(snapshot, position):
    """A player at `position` on no roster, with a game in the last week of the player stats."""
    week = snapshot.stats.weeks[snapshot.as_of.stats_through]
    rostered = {player for players in snapshot.rosters.values() for player in players}
    return next(player for player, line in sorted(week.stats.items())
                if week.positions.get(player) == position and player not in rostered and line.get("gp", 0) > 0)


def _with_points(snapshot, player, points, position=None):
    """The snapshot with new points on the player's stat line in the last week of the player stats.

    With a `position`, the line is a played line at that position, so a test can add a player the fixture lacks.
    """
    through = snapshot.as_of.stats_through
    week = snapshot.stats.weeks[through]
    line = {**week.stats.get(player, {"gp": 1.0}), "pts_half_ppr": points}
    positions = {**week.positions, player: position} if position else week.positions
    weeks = {**snapshot.stats.weeks, through: week.model_copy(
        update={"stats": {**week.stats, player: line}, "positions": positions})}
    return snapshot.model_copy(update={"stats": snapshot.stats.model_copy(update={"weeks": weeks})})


def test_a_changed_stat_line_of_an_unrostered_rb_changes_the_grade_key_and_the_finder_key(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    back = _unrostered_with_a_game(snapshot, "RB")
    # The position rank pool holds every back with a stat line, so his points can move the rank of a traded back.
    assert cache_key(trade, _with_points(snapshot, back, 30.0)) != cache_key(trade, _with_points(snapshot, back, 3.0))
    assert finder_cache_key(2026, 4, 12, _with_points(snapshot, back, 30.0)) != finder_cache_key(
        2026, 4, 12, _with_points(snapshot, back, 3.0))


def test_a_changed_stat_line_of_an_unrostered_k_changes_neither_key(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    # The fixture has no K line, so the test adds one for a kicker on no roster.
    kicker = "unrostered-kicker"
    # K has no position rank, so no grade reads his line.
    assert cache_key(trade, _with_points(snapshot, kicker, 30.0, "K")) == cache_key(
        trade, _with_points(snapshot, kicker, 3.0, "K"))
    assert finder_cache_key(2026, 4, 12, _with_points(snapshot, kicker, 30.0, "K")) == finder_cache_key(
        2026, 4, 12, _with_points(snapshot, kicker, 3.0, "K"))


def test_a_new_free_agent_at_rb_changes_the_grade_key_and_the_finder_key(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    bigsby = SnapshotPlayer(player_id="9225", name="Tank Bigsby", position="RB", nfl_team="PHI")
    added = snapshot.model_copy(update={"free_agents": {**snapshot.free_agents, "RB": [bigsby]}})
    # His stat line is in the rank pool either way, so only the free agents tell the two keys apart. The hole fact
    # names the best free agent, so a new one must miss.
    assert added.rank_table() == snapshot.rank_table()
    assert cache_key(trade, added) != cache_key(trade, snapshot)
    assert finder_cache_key(2026, 4, 12, added) != finder_cache_key(2026, 4, 12, snapshot)


def _strings(value):
    """Every string in a document, at any depth."""
    if isinstance(value, dict):
        return [found for item in value.values() for found in _strings(item)]
    if isinstance(value, list):
        return [found for item in value for found in _strings(item)]
    return [value] if isinstance(value, str) else []


def test_a_trade_with_an_unlisted_player_leans_even_with_no_letter(settings, sources):
    snapshot = _here(sources, settings).snapshot(2026)
    unlisted = next(pid for pid in snapshot.rosters[12] if pid not in snapshot.chart.values and not is_def(pid))
    trade = {**TRADE, "sides": _sides(["7569"], [unlisted])}
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=trade, headers=HEADERS).json()
    for side in doc["sides"]:
        assert side["factors"][0] == {
            "name": "deal", "lean": "even",
            "reason": "Not every player in the trade has a value this week, so both sides start even."}


def test_the_fixture_document_names_no_letter():
    fixture = json.loads(RESPONSE_FIXTURE.read_text(encoding="utf-8"))
    # A letter grade on its own, as in "C", or the word "letter". Neither may reach the document.
    found = [text for text in _strings(fixture)
             if re.search(r"\b[A-F]\b", text) or re.search(r"\bletters?\b", text, re.IGNORECASE)]
    assert found == []


def test_the_real_analyzer_with_a_fake_claude_gives_the_document_with_its_text(settings, sources):
    analyzer = functools.partial(analyze, call=FakeClaude())
    doc = _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["fallback"] is False
    assert [side["bullets"] for side in doc["sides"]] == [list(FakeClaude.BULLETS)] * 2


def _at(fixture_raw_dir, chart, fetched):
    """Sources whose Sleeper fetch reports the time `fetched`."""
    return Sources(
        fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), fetched),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines, **_: chart, clock=lambda: NOW, client=CLIENT)


def test_a_repeat_is_a_cache_hit_with_one_claude_call(settings, fixture_raw_dir, chart_week6):
    analyzer = StubAnalyzer()
    first = _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer)
    # The rosters fetch time moves on every request, but a repeat on unchanged rosters is the same trade.
    later = _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED.replace(minute=55)), analyzer)
    swapped = {**TRADE, "sides": _sides(["7569"], ["8146", "10236"])}
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
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS
    )
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED.replace(hour=10)), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 1


def _without_a_bench_player(fixture_raw_dir, chart, roster_id):
    """Sources whose Sleeper data drops one player, who is not in the trade, from a roster."""
    raw = load_raw(fixture_raw_dir)
    roster = next(r for r in raw.rosters if r.roster_id == roster_id)
    roster.players = (roster.players or [])[:-1]
    return Sources(
        fetch_sleeper=lambda league_id: (raw, FETCHED),
        fetch_nflverse=_no_network, fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines, **_: chart, clock=lambda: NOW, client=CLIENT)


def test_a_changed_roster_or_another_asker_misses_the_cache(settings, fixture_raw_dir, chart_week6):
    analyzer = StubAnalyzer()
    _client(settings, _at(fixture_raw_dir, chart_week6, FETCHED), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS
    )
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
    from cornerstone_api.app import RATE_LIMIT_PER_MINUTE

    client = _client(settings, sources)
    for _ in range(RATE_LIMIT_PER_MINUTE):
        # Wrong guesses count too, so a stranger cannot loop through passphrases.
        assert client.get("/teams", params={"season": 2026}).status_code == 401
    response = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    assert client.get("/health").status_code == 200


def test_each_fly_client_address_has_its_own_rate_limit(settings, sources):
    from cornerstone_api.app import RATE_LIMIT_PER_MINUTE

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
    client.app.state.served["cpc"].grade_limiter.clock = clock
    # The general limit reads the same clock, so a test can make more than its 10 requests in one real minute.
    client.app.state.limiter.clock = lambda: clock().timestamp()
    return client


def _uncached():
    """An analyzer whose result falls back. A fallback is not cached, so each repeat is a new grade."""
    return StubAnalyzer(claude_letters=["A", "C"])


def test_the_sixth_grade_in_a_minute_is_429_with_the_minute_text(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

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
    from analyzer.tunables import GRADES_PER_DAY

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
    path = settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE
    assert json.loads(path.read_text()) == {"day": "2026-10-20", "counts": {"203.0.113.9": 1}}


def test_a_malformed_count_file_starts_at_zero(settings, sources):
    path = settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json")
    client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert json.loads(path.read_text())["counts"] == {"testclient": 1}


def test_a_cached_repeat_does_not_count_as_a_grade(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    analyzer = StubAnalyzer()
    client = _graded_client(settings, sources, MovingClock(NOW), analyzer)
    for _ in range(GRADES_PER_MINUTE + 1):
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert analyzer.calls == 1


def test_each_fly_client_address_has_its_own_grade_limit(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    one = {**HEADERS, "Fly-Client-IP": "203.0.113.1"}
    for _ in range(GRADES_PER_MINUTE):
        client.post("/analyze", json=TRADE, headers=one)
    over = client.post("/analyze", json=TRADE, headers=one)
    other = client.post("/analyze", json=TRADE, headers={**HEADERS, "Fly-Client-IP": "203.0.113.2"})
    assert over.status_code == 429
    assert other.status_code == 200


def test_grades_at_once_on_many_threads_never_pass_the_day_limit(tmp_path):
    from analyzer.tunables import GRADES_PER_DAY, GRADES_PER_MINUTE

    # Each read of the clock is 61 seconds on, so only the day limit can stop a grade.
    ticks = itertools.count()
    limiter = GradeLimiter(GRADES_PER_MINUTE, GRADES_PER_DAY, tmp_path / GRADE_COUNTS_FILE, CLIENT.tz,
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
    from analyzer.tunables import GRADES_PER_DAY

    def full_volume(src, dst):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr("league.files.os.replace", full_volume)
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
    assert not (settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).exists()


def test_a_bad_trade_does_not_count_as_a_grade(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    # Garrett Wilson is on roster 12, not roster 4.
    bad = {**TRADE, "sides": _sides(["8146"], ["10236"])}
    bad_client = _graded_client(settings, sources, MovingClock(NOW), _uncached())
    for _ in range(GRADES_PER_MINUTE + 1):
        assert bad_client.post("/analyze", json=bad, headers=HEADERS).status_code == 422
    assert not (settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).exists()
    assert bad_client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200


@pytest.mark.parametrize(
    "origin", ["https://cpc.4thandgoal.app", "https://norcal.4thandgoal.app", "https://cpcfantasy.com",
               "http://localhost:5173", "http://localhost:3000"])
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
        for factor in side["factors"]:
            assert _shape(factor) == _shape(fixture["sides"][0]["factors"][0])


# The keys whose numbers are ids, weeks, the season, or the stamp. No other number may appear in the document.
# The fairness block's gives_more is a roster id, and so are the to and from of each traded player.
NUMBER_KEYS = {"roster_id", "asker", "for_roster", "gives_more", "chart_week", "stats_through", "completed_through",
               "season", "week", "games", "in_progress", "snaps", "usage", "to", "from"}
# The strings that may hold digits: ids, URLs, the stamp, and the names that managers and Sleeper set.
# A Season rank and a Recent rank, such as WR60, hold the rank as digits.
DIGIT_STRING_KEYS = {"player_id", "headshot", "rosters_fetched", "team", "name", "season_rank", "recent_rank"}


# One count of the roster fit reason: the players at a position in the top N, before and after.
TOP_N_COUNT = re.compile(r"\d+ (?:QB|RB|WR|TE)s? in the top \d+(?: to \d+)?")
# The weeks and the ranks of the schedule row and the injury row, such as "week 13", "weeks 15 to 17", "3rd", and
# "5 of 8 weeks".
WEEKS_AND_RANKS = re.compile(r"\bweeks? \d+(?: to \d+)?|\b\d+(?:st|nd|rd|th)\b|\b\d+ of \d+ weeks")


def _digits_outside_ids(value, key=None):
    """The numbers and the strings with digits under any key that may not hold them."""
    if isinstance(value, dict):
        if value.get("name") == TREND:
            # The trend reason may give share percents and the air yards per target. Any other number in it fails.
            value = {**value, "reason": strip_trend_numbers(value["reason"])}
        if value.get("name") in (SCHEDULE, INJURY):
            # The code writes the weeks of a bye, a return, and the injury report, and the rank of each opponent.
            value = {**value, "reason": WEEKS_AND_RANKS.sub("", value["reason"])}
        if value.get("name") == ROSTER_FIT:
            # The roster row counts the players in the top N, such as "3 WRs in the top 36", and can name a week. The
            # code writes it, and this check guards Claude's prose, not the code's factor reasons.
            value = {**value, "reason": re.sub(r"week \d+", "", TOP_N_COUNT.sub("", value["reason"]))}
        if set(value) == {"roster_id", "reason"}:
            # A fairness side gives the reason of its first step up, which can be the roster row with its counts.
            value = {**value, "reason": TOP_N_COUNT.sub("", value["reason"])}
        return [found for k, item in value.items() for found in _digits_outside_ids(item, k)]
    if isinstance(value, list):
        return [found for item in value for found in _digits_outside_ids(item, key)]
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [] if key in NUMBER_KEYS else [(key, value)]
    return [] if key in DIGIT_STRING_KEYS or not re.search(r"\d", value) else [(key, value)]


def test_the_document_has_no_number_outside_ids_weeks_and_the_stamp(settings, sources):
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert _digits_outside_ids(doc) == []


def test_a_season_that_is_not_in_progress_is_422(settings, sources):
    response = _client(settings, sources).get("/teams", params={"season": 2025}, headers=HEADERS)
    assert response.status_code == 422
    assert response.json() == {"detail": "The season 2025 is not in progress."}


def test_settings_from_the_environment_need_a_passphrase_for_each_client(monkeypatch, tmp_path):
    monkeypatch.delenv("CORNERSTONE_PASSPHRASE_CPC", raising=False)
    monkeypatch.delenv("CORNERSTONE_PASSPHRASE_NORCAL", raising=False)
    # No passphrase is shared, so the old shared value counts for no client.
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE", "shared")
    with pytest.raises(RuntimeError, match="Set CORNERSTONE_PASSPHRASE_CPC before the API starts."):
        Settings.from_env(["cpc"])
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE_CPC", "secret")
    with pytest.raises(RuntimeError, match="Set CORNERSTONE_PASSPHRASE_NORCAL before the API starts."):
        Settings.from_env(["cpc", "norcal"])
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE_NORCAL", "other")
    monkeypatch.setenv("CORNERSTONE_REPO", str(tmp_path))
    settings = Settings.from_env(["cpc", "norcal"])
    assert settings.passphrases == {"cpc": "secret", "norcal": "other"}
    assert "secret" not in repr(settings) and "other" not in repr(settings)
    assert settings.result_cache_dir == tmp_path.resolve() / "data" / "cache" / "results"
    assert "https://cpc.4thandgoal.app" in settings.allowed_origins


# Every source that the refresh fetches, in the order of the refresh.
ALL_SOURCES = ["schedules", "depth charts", "id map", "injuries", "expected points", "player weeks"]


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
    no_chart = dataclasses.replace(sources, read_chart=lambda repo, season_start, week, lines, **_: None,
                                   fetch_nflverse=_fixture_fetch(fixture_nflverse_dir, []))
    response = _client(settings, no_chart).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert response.json() == {"refreshed": ALL_SOURCES, "stale": ["chart"]}


def test_a_refresh_with_a_chart_read_that_raises_lists_the_chart_once(settings, sources, fixture_nflverse_dir):
    def read_chart(repo, season_start, week, lines, chart):
        raise TypeError("no api key")

    raising = dataclasses.replace(sources, read_chart=read_chart,
                                  fetch_nflverse=_fixture_fetch(fixture_nflverse_dir, []))
    response = _client(settings, raising).post("/refresh", params={"season": 2026}, headers=HEADERS)
    assert response.json() == {"refreshed": ALL_SOURCES, "stale": ["chart"]}


def test_a_refresh_needs_the_passphrase(settings, sources):
    response = _client(settings, sources).post("/refresh", params={"season": 2026})
    assert response.status_code == 401
    assert response.content == b""


# The find route. The fixture chart lists mostly stars, so no pair of the week 6 snapshot has a win-win on it.
# The finder tests give chart rows to the players a test needs, and these tests do the same for rosters 2 and 3,
# so the pair has three win-wins that share no player.
CHART_POSITIONS = frozenset({"RB", "WR", "TE", "QB"})
FIND = {"season": 2026, "asker": 2, "partner": 3}


@pytest.fixture
def find_sources(settings, sources, chart_week6, fixture_raw_dir):
    """The sources with a chart row for every RB, WR, TE, and QB of rosters 2 and 3, at his recent points per game.

    The fetch has no week 6 stat lines, as before the first week 6 game, so the trades match the find fixture.
    """
    def before_kickoff(league_id):
        raw = load_raw(fixture_raw_dir)
        raw.stats = []
        return raw, FETCHED

    sources = dataclasses.replace(sources, fetch_sleeper=before_kickoff)
    snapshot = _here(sources, settings).snapshot(2026)
    rows = {pid: float(max(1, round(recent_points_per_game(snapshot, pid))))
            for roster_id in (2, 3) for pid in snapshot.rosters[roster_id]
            if snapshot.players[pid].position in CHART_POSITIONS and pid not in chart_week6.values}
    chart = chart_week6.model_copy(update={"values": {**chart_week6.values, **rows}})
    return dataclasses.replace(sources, read_chart=lambda repo, season_start, week, lines, **_: chart)


class FakeFinderClaude:
    """The Claude call of the finder with no network: one reason per trade in the user message.

    `texts` gives the reason text of each attempt in turn. The last text repeats past the end of the list.
    """

    TEXT = "Each side fills a need at a position it starts every week."

    def __init__(self, *texts):
        self.texts = list(texts) or [self.TEXT]
        self.calls = []

    def __call__(self, system, user, output_model):
        self.calls.append((system, user))
        text = self.texts[min(len(self.calls), len(self.texts)) - 1]
        numbers = [int(n) for n in re.findall(r"^Trade (\d+)$", user, re.MULTILINE)]
        reasons = [{"trade": n, "reason": text,
                    "cited": re.findall(rf"^- (t{n}\.[\w.]+): ", user, re.MULTILINE)[:1]} for n in numbers]
        return output_model.model_validate({"reasons": reasons})


def _find_client(settings, sources, fake, clock=None):
    """A client whose finder reasons make the fake call. With a clock, the grade and general limits read it."""
    client = TestClient(create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), analyzer=StubAnalyzer(),
                                   finder_reasons=functools.partial(write_reasons, call=fake)))
    if clock is not None:
        client.app.state.served["cpc"].grade_limiter.clock = clock
        client.app.state.limiter.clock = lambda: clock().timestamp()
    return client


def test_find_returns_three_win_win_trades_with_one_reason_each(settings, find_sources):
    fake = FakeFinderClaude()
    response = _find_client(settings, find_sources, fake).post("/find", json=FIND, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert len(fake.calls) == 1
    assert doc["fallback"] is False
    assert doc["empty"] is None
    assert [team["roster_id"] for team in doc["trade_pair"].values()] == [2, 3]
    assert len(doc["trades"]) == 3
    for item in doc["trades"]:
        assert item["fairness"]["state"] == "win_win"
        assert item["reason"] == FakeFinderClaude.TEXT
        # The asker's side comes first, as in the analyze document.
        assert [side["roster_id"] for side in item["sides"]] == [2, 3]
    assert doc["as_of"]["chart_week"] == 6
    assert doc["as_of"]["stats_through"] == 5
    assert doc["as_of"]["completed_through"] == 5


def test_find_with_no_win_win_gives_the_empty_line_and_makes_no_claude_call(settings, sources):
    fake = FakeFinderClaude()
    doc = _find_client(settings, sources, fake).post("/find", json=FIND, headers=HEADERS).json()
    assert doc["trades"] == []
    assert doc["empty"] == "No swap between these rosters is good for both."
    assert doc["fallback"] is False
    assert fake.calls == []
    # The finder reads the same bounds and the same known games as the grade.
    assert doc["as_of"]["stats_through"] == 6
    assert doc["as_of"]["completed_through"] == 5
    assert doc["as_of"]["known_games"] == {"week": 6, "games": 14, "in_progress": 0, "pending": {"usage": 8}}


def test_an_empty_find_counts_one_grade_and_a_repeat_is_cached_with_no_claude_call(settings, sources):
    fake = FakeFinderClaude()
    client = _find_client(settings, sources, fake, MovingClock(NOW))
    first = client.post("/find", json=FIND, headers=HEADERS).json()
    assert first["trades"] == []
    assert client.post("/find", json=FIND, headers=HEADERS).json() == first
    assert fake.calls == []
    assert json.loads((settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).read_text())["counts"] == {"testclient": 1}


def test_a_find_in_a_week_with_no_chart_answers_and_says_so(settings, fixture_raw_dir):
    # With no chart every player is unlisted, so the finder finds no win-win and makes no Claude call.
    fake = FakeFinderClaude()
    response = _find_client(settings, _no_chart_sources(fixture_raw_dir), fake).post(
        "/find", json=FIND, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert doc["trades"] == []
    assert doc["as_of"]["no_chart"] is True
    assert doc["as_of"]["no_chart_note"] == "This week's player values are not out yet, so both sides start even."
    assert fake.calls == []


def test_find_needs_the_passphrase(settings, sources):
    response = _find_client(settings, sources, FakeFinderClaude()).post("/find", json=FIND)
    assert response.status_code == 401
    assert response.content == b""


@pytest.mark.parametrize("pair, message", [
    ({"asker": 2, "partner": 2}, "Pick two different teams."),
    ({"asker": 2, "partner": 99}, "Roster 99 is not in the league"),
])
def test_find_with_the_same_roster_twice_or_a_roster_not_in_the_league_is_422(settings, sources, pair, message):
    response = _find_client(settings, sources, FakeFinderClaude()).post(
        "/find", json={"season": 2026, **pair}, headers=HEADERS)
    assert response.status_code == 422
    assert response.json() == {"detail": {"message": message}}
    assert not (settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).exists()


def test_the_sixth_find_in_a_minute_is_429_with_the_minute_text(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    client = _find_client(settings, sources, FakeFinderClaude(), MovingClock(NOW))
    # A new partner each time, so no request is a cached repeat and each one counts as one grade.
    for partner in range(3, 3 + GRADES_PER_MINUTE):
        assert client.post("/find", json={**FIND, "partner": partner}, headers=HEADERS).status_code == 200
    response = client.post("/find", json={**FIND, "partner": 3 + GRADES_PER_MINUTE}, headers=HEADERS)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many grades this minute. Try again later."}
    assert 1 <= int(response.headers["Retry-After"]) <= 60


def test_a_find_and_an_analyze_count_against_the_same_grade_limit(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    client = _find_client(settings, sources, FakeFinderClaude(), MovingClock(NOW))
    client.app.state.analyzer = _uncached()
    for _ in range(GRADES_PER_MINUTE - 1):
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert client.post("/find", json=FIND, headers=HEADERS).status_code == 200
    assert client.post("/find", json={**FIND, "partner": 4}, headers=HEADERS).status_code == 429


def test_a_cached_find_repeat_does_not_count_and_makes_no_claude_call(settings, find_sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    fake = FakeFinderClaude()
    client = _find_client(settings, find_sources, fake, MovingClock(NOW))
    first = client.post("/find", json=FIND, headers=HEADERS).json()
    for _ in range(GRADES_PER_MINUTE):
        assert client.post("/find", json=FIND, headers=HEADERS).json() == first
    assert len(fake.calls) == 1
    assert json.loads((settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).read_text())["counts"] == {"testclient": 1}


def _with_as_of(snapshot, **update):
    return snapshot.model_copy(update={"as_of": snapshot.as_of.model_copy(update=update)})


def test_the_find_cache_key_is_the_ordered_pair_and_the_chart_week(settings, sources):
    snapshot = _here(sources, settings).snapshot(2026)
    key = finder_cache_key(2026, 2, 3, snapshot)
    # The rosters fetch time moves on every request, so it is not in the key.
    assert finder_cache_key(2026, 2, 3, _with_as_of(snapshot, rosters_fetched=FETCHED.replace(minute=55))) == key
    # The asker's side comes first and the rank reads the asker's letter, so the other order is another key.
    assert finder_cache_key(2026, 3, 2, snapshot) != key
    assert finder_cache_key(2026, 2, 3, _with_as_of(snapshot, chart_week=7)) != key
    # A finder key never equals the key of a trade in the shared result directory.
    assert key != cache_key(ProposedTrade.model_validate(TRADE), snapshot)


def test_the_find_cache_key_changes_with_the_document_version(settings, sources, monkeypatch):
    import analyzer.cache as cache_module

    snapshot = _here(sources, settings).snapshot(2026)
    key = finder_cache_key(2026, 2, 3, snapshot)
    monkeypatch.setattr(cache_module, "DOCUMENT_VERSION", cache_module.DOCUMENT_VERSION + 1)
    assert finder_cache_key(2026, 2, 3, snapshot) != key


def test_the_other_order_of_the_pair_misses_the_cache(settings, find_sources):
    fake = FakeFinderClaude()
    client = _find_client(settings, find_sources, fake)
    client.post("/find", json=FIND, headers=HEADERS)
    swapped = client.post("/find", json={**FIND, "asker": 3, "partner": 2}, headers=HEADERS).json()
    assert len(fake.calls) == 2
    assert [team["roster_id"] for team in swapped["trade_pair"].values()] == [3, 2]
    assert all(item["sides"][0]["roster_id"] == 3 for item in swapped["trades"])


# A reason that names a letter grade. The prose checks of the analysis reject it.
LETTER_REASON = "Each side moves up to a grade of B in this swap."


def test_a_failed_claude_call_retries_once_then_each_reason_is_empty(settings, find_sources):
    fake = FakeFinderClaude(LETTER_REASON)
    client = _find_client(settings, find_sources, fake)
    doc = client.post("/find", json=FIND, headers=HEADERS).json()
    assert len(fake.calls) == 2
    # The second attempt carries the failures of the first as feedback.
    assert "Feedback from the last attempt:" in fake.calls[1][1]
    assert doc["fallback"] is True
    assert len(doc["trades"]) == 3
    for item in doc["trades"]:
        # The fairness block already holds the code's reasons, so the card shows the fairness line alone.
        assert item["reason"] is None
        assert all(side["reason"] for side in item["fairness"]["sides"])
    # A fallback is not stored, so a repeat tries the Claude call again.
    client.post("/find", json=FIND, headers=HEADERS)
    assert len(fake.calls) == 4


def test_a_reason_that_fails_once_and_passes_on_the_retry_stands(settings, find_sources):
    fake = FakeFinderClaude(LETTER_REASON, FakeFinderClaude.TEXT)
    doc = _find_client(settings, find_sources, fake).post("/find", json=FIND, headers=HEADERS).json()
    assert len(fake.calls) == 2
    assert doc["fallback"] is False
    assert [item["reason"] for item in doc["trades"]] == [FakeFinderClaude.TEXT] * 3


@pytest.fixture
def found(settings, find_sources):
    """The week 6 snapshot with the extra chart rows, and the three trades the finder finds for rosters 2 and 3.

    The find fixture is a run with the 4-week measure, so the snapshot takes it and the finder finds the same trades.
    """
    snapshot = four_week(_here(find_sources, settings).snapshot(2026))
    return snapshot, find_win_wins(2, 3, snapshot)


def _sheets(snapshot, items):
    return [trade_facts(n, item, snapshot) for n, item in enumerate(items, start=1)]


def _reasons(sheets, texts, cited=None):
    """One reason per trade. Each cites the first fact of its own trade, unless `cited` gives the IDs for all."""
    texts = [texts] * len(sheets) if isinstance(texts, str) else texts
    return FinderReasonsOut.model_validate({"reasons": [
        {"trade": n, "reason": text, "cited": list(cited) if cited is not None else [next(iter(sheet))]}
        for n, (sheet, text) in enumerate(zip(sheets, texts), start=1)]})


@pytest.mark.parametrize("text, rule", [
    (LETTER_REASON, "names a letter grade"),
    ("Each side gets the better letter in this swap.", "the word 'letter' is not allowed"),
    ("Each side climbs the chart in this swap.", "the word 'chart' is not allowed"),
    ("Each side gets 41 points of value in this swap.", "41"),
    ("Each side fills a need. Both start the player at once.", "it needs exactly 1"),
])
def test_the_prose_checks_reject_a_reason_that_breaks_a_rule(found, text, rule):
    snapshot, items = found
    sheets = _sheets(snapshot, items)
    failures = check_reasons(_reasons(sheets, text), items, snapshot, sheets)
    assert len(failures) == len(items)
    assert all(rule in failure for failure in failures)


def test_a_reason_that_cites_no_fact_fails(found):
    snapshot, items = found
    sheets = _sheets(snapshot, items)
    failures = check_reasons(_reasons(sheets, FakeFinderClaude.TEXT, cited=[]), items, snapshot, sheets)
    assert failures == [f"trade {n}: the reason cites no fact" for n in range(1, len(items) + 1)]


def test_a_reason_may_cite_only_the_facts_of_its_own_trade(found):
    snapshot, items = found
    sheets = _sheets(snapshot, items)
    other = next(iter(sheets[1]))
    failures = check_reasons(_reasons(sheets, FakeFinderClaude.TEXT, [other]), items, snapshot, sheets)
    assert f"trade 1: fact ID {other} is not in the facts" in failures


def test_a_response_with_a_trade_left_out_fails_the_shape(found):
    snapshot, items = found
    out = FinderReasonsOut.model_validate({"reasons": [{"trade": 1, "reason": FakeFinderClaude.TEXT, "cited": []}]})
    assert check_reasons(out, items, snapshot, _sheets(snapshot, items)) == [
        "the response must have exactly 3 reasons: trades 1, 2, 3 in order, each once; it had trades 1"]


def test_the_finder_prompt_holds_the_reason_rules(settings, find_sources):
    fake = FakeFinderClaude()
    _find_client(settings, find_sources, fake).post("/find", json=FIND, headers=HEADERS)
    # The prompt wraps its lines, so the check reads it as one line.
    system = " ".join(fake.calls[0][0].split())
    for line in (
        "Write one sentence for each trade. It ends with a period. A manager pastes it into the group chat.",
        "Cite only the facts of that trade.",
        "Use only numbers from the facts you cite or the breakdown of that trade.",
        "Never write a trade value, a sum, a ratio, a new number, or a difference.",
        "Never count the players, starters, or weeks in the trade yourself",
        "Put at most two numbers in the reason.",
        "Name each team in the trade at most once in the reason.",
        "Never name a letter grade. Never write the word letter.",
        'Never write win-win, lopsided, or fair. Write "good for both" if you need to.',
    ):
        assert line in system
    # The rubric comes before the finder rules, so the adjuster names in the breakdown lines mean what it says.
    assert system.index("# Finder rules") > 0


def test_a_good_find_returns_the_document_in_the_fixture_shape(settings, find_sources):
    doc = _find_client(settings, find_sources, FakeFinderClaude()).post("/find", json=FIND, headers=HEADERS).json()
    fixture = json.loads(FIND_FIXTURE.read_text(encoding="utf-8"))
    assert len(fixture["trades"]) == 3
    assert _same_shape(doc, _shape(fixture))
    # Every trade has the shape of the fixture's first, so no item drops a key.
    for item in doc["trades"]:
        assert _shape(item) == _shape(fixture["trades"][0])
    # The sides and the fairness of an item have the shape of the analyze document, so the site renders them once.
    analyze_fixture = json.loads(RESPONSE_FIXTURE.read_text(encoding="utf-8"))
    assert _shape(fixture["trades"][0]["sides"]) == _shape(analyze_fixture["trade"]["sides"])
    assert _shape(fixture["trades"][0]["fairness"]) == _shape(analyze_fixture["fairness"])
    assert doc["season"] == fixture["season"] == FIND["season"]


def test_the_find_fixture_reasons_pass_the_real_reason_checks(found):
    # The fixture reasons are written by hand, so the real checks keep a broken rule out of the site's copy.
    snapshot, items = found
    fixture = json.loads(FIND_FIXTURE.read_text(encoding="utf-8"))
    # The fixture is the run on these rosters, so its trades are the finder's trades in the same order.
    assert [[[player["player_id"] for player in side["gives"]] for side in item["sides"]]
            for item in fixture["trades"]] == [[side.player_ids for side in item.trade.sides] for item in items]
    sheets = _sheets(snapshot, items)
    out = _reasons(sheets, [item["reason"] for item in fixture["trades"]])
    assert check_reasons(out, items, snapshot, sheets) == []


def test_the_find_fixture_names_no_letter_and_no_number_outside_ids():
    fixture = json.loads(FIND_FIXTURE.read_text(encoding="utf-8"))
    found = [text for text in _strings(fixture)
             if re.search(r"\b[A-F]\b", text) or re.search(r"\bletters?\b", text, re.IGNORECASE)]
    assert found == []
    # The fairness reasons reuse the breakdown reasons, so a trend reason may give its share percents and air yards.
    for item in fixture["trades"]:
        for side in item["fairness"]["sides"]:
            side["reason"] = strip_trend_numbers(side["reason"])
    assert _digits_outside_ids(fixture) == []


WEEK_N_FIELDS = ("pts_half_ppr", "gp", "off_snp", "tm_off_snp", "rec_tgt", "rec_rz_tgt", "rush_rz_att")


def _with_week_n_stats(snapshot, stats):
    """The snapshot with week N holding `stats`, by player id."""
    week_n = snapshot.stats.weeks[snapshot.as_of.stats_through]
    reworked = week_n.model_copy(update={"stats": stats})
    weeks = {**snapshot.stats.weeks, week_n.week: reworked}
    return snapshot.model_copy(update={"stats": snapshot.stats.model_copy(update={"weeks": weeks})})


def _with_week_n_line(snapshot, player, **fields):
    """The snapshot with `fields` set on the week N stat line of `player`."""
    stats = snapshot.stats.weeks[snapshot.as_of.stats_through].stats
    return _with_week_n_stats(snapshot, {**stats, player: {**stats.get(player, {}), **fields}})


def _both_keys(trade, snapshot):
    return cache_key(trade, snapshot), finder_cache_key(2026, 4, 12, snapshot)


def test_the_cache_key_changes_with_a_week_n_line_of_a_rostered_player(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    assert snapshot.as_of.stats_through > snapshot.as_of.completed_through
    rostered = snapshot.rosters[4][0]
    points = snapshot.stats.weeks[snapshot.as_of.stats_through].stats.get(rostered, {}).get("pts_half_ppr", 0.0)
    # Six more points is a new fetch with a new number, so the stored grade must miss.
    scored = _with_week_n_line(snapshot, rostered, pts_half_ppr=points + 6)
    assert cache_key(trade, scored) != cache_key(trade, snapshot)
    assert finder_cache_key(2026, 4, 12, scored) != finder_cache_key(2026, 4, 12, snapshot)
    for field in WEEK_N_FIELDS:
        moved = _with_week_n_line(snapshot, rostered, **{field: 77.0})
        assert cache_key(trade, moved) != cache_key(trade, snapshot), field


def test_the_cache_key_reads_a_first_known_game_after_a_return_through_the_due_back_rule(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    week_n = snapshot.as_of.stats_through
    assert week_n > snapshot.as_of.completed_through
    rostered = next(player for player in snapshot.rosters[4]
                    if snapshot.stats.weeks[week_n].stats.get(player, {}).get("gp", 0) <= 0)
    # Due back in week N with no game yet, he counts for his projection ahead, so a change to its rows must miss.
    due = _with_week_rows(snapshot, {rostered: week_n}, {rostered: {week_n: 12.5}})
    assert cache_key(trade, _with_week_rows(due, {rostered: week_n}, {rostered: {week_n: 13.5}})) != cache_key(
        trade, due)
    # His first week N game ends due back, so the key misses, and his projection rows no longer reach the grade.
    played = _with_week_n_line(due, rostered, gp=1.0, pts_half_ppr=14.0)
    assert _both_keys(trade, played) != _both_keys(trade, due)
    moved = _with_week_n_line(_with_week_rows(due, {rostered: week_n}, {rostered: {week_n: 13.5}}),
                              rostered, gp=1.0, pts_half_ppr=14.0)
    assert _both_keys(trade, moved) == _both_keys(trade, played)


def test_the_cache_key_ignores_a_week_n_line_of_a_player_on_neither_roster(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    outside = _outside_player(snapshot, [4, 12])
    changed = _with_week_n_line(snapshot, outside, pts_half_ppr=31.5, gp=1.0, rec_tgt=9.0)
    assert _both_keys(trade, changed) == _both_keys(trade, snapshot)


def test_a_third_roster_line_that_moves_a_traded_players_rank_changes_the_key(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    collins = "7569"
    week_n = snapshot.stats.weeks[snapshot.as_of.stats_through].stats
    # A healthy receiver who played in week N, so he is not due back and his recent points read the week N line.
    receiver = next(player for roster_id, players in sorted(snapshot.rosters.items()) if roster_id not in (4, 12)
                    for player in players if snapshot.players[player].position == "WR"
                    and snapshot.players[player].injury_status is None and week_n.get(player, {}).get("gp", 0) > 0
                    and snapshot.position_rank(player) > snapshot.position_rank(collins))
    # 200 points in his week N game lift the receiver above Collins, so Collins drops one rank.
    # The roster points of a rostered player come before his stat line, so both change.
    lined = _with_week_n_line(snapshot, receiver, gp=1.0, pts_half_ppr=200.0)
    week = lined.stats.weeks[lined.as_of.stats_through]
    weeks = {**lined.stats.weeks, week.week: week.model_copy(update={"points": {**week.points, receiver: 200.0}})}
    moved = lined.model_copy(update={"stats": lined.stats.model_copy(update={"weeks": weeks})})
    assert moved.position_rank(collins) == snapshot.position_rank(collins) + 1
    assert cache_key(trade, moved) != cache_key(trade, snapshot)
    assert finder_cache_key(2026, 4, 12, moved) != finder_cache_key(2026, 4, 12, snapshot)


def test_the_cache_key_ignores_a_week_n_field_the_grade_never_reads(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    changed = _with_week_n_line(snapshot, rostered, pass_yd=412.0)
    assert _both_keys(trade, changed) == _both_keys(trade, snapshot)


def test_the_cache_key_tells_empty_week_n_lines_from_any_line(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    rostered = snapshot.rosters[4][0]
    outside = _outside_player(snapshot, [4, 12])
    empty = _with_week_n_stats(snapshot, {})
    # An empty line of a rostered player reads as no line.
    assert _both_keys(trade, _with_week_n_stats(snapshot, {rostered: {}})) == _both_keys(trade, empty)
    assert _both_keys(trade, _with_week_n_stats(snapshot, {outside: {"gp": 1.0}})) == _both_keys(trade, empty)
    assert cache_key(trade, _with_week_n_line(empty, rostered, gp=1.0)) != cache_key(trade, empty)
    assert finder_cache_key(2026, 4, 12, _with_week_n_line(empty, rostered, gp=1.0)) != finder_cache_key(
        2026, 4, 12, empty)


def test_the_cache_key_of_a_week_with_no_known_games_adds_no_week_n_line(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    # With no week N in the player stats the bound is the completed week, and the key adds nothing.
    completed = snapshot.as_of.completed_through
    weeks = {week: past for week, past in snapshot.stats.weeks.items() if week <= completed}
    past = _with_as_of(snapshot.model_copy(update={"stats": snapshot.stats.model_copy(update={"weeks": weeks})}),
                       stats_through=completed)
    empty = _with_as_of(_with_week_n_stats(snapshot, {}), stats_through=completed)
    assert _both_keys(trade, past) == _both_keys(trade, empty)


def test_the_cache_key_changes_with_the_known_games_block(settings, sources):
    # The document shows the block, so a stored grade must not show an old pending count.
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    known = snapshot.as_of.known_games
    assert known is not None
    fewer = known.model_copy(update={"pending": {**known.pending, "snaps": 3}})
    assert _both_keys(trade, _with_as_of(snapshot, known_games=fewer)) != _both_keys(trade, snapshot)
    without = _both_keys(trade, _with_as_of(snapshot, known_games=None))
    assert without[0] != cache_key(trade, snapshot)
    assert without[1] != finder_cache_key(2026, 4, 12, snapshot)


def test_the_cache_key_changes_when_the_stats_are_stale(settings, sources):
    # A failed week N fetch on a Sunday must not serve the document from before the games.
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    assert "stats" not in snapshot.stale
    stale = snapshot.model_copy(update={"stale": [*snapshot.stale, "stats"]})
    assert cache_key(trade, stale) != cache_key(trade, snapshot)
    assert finder_cache_key(2026, 4, 12, stale) != finder_cache_key(2026, 4, 12, snapshot)


def test_the_cache_key_changes_with_a_week_n_wopr_row_of_a_rostered_player(settings, sources):
    # The trend step reads the week N row when the player file brings it in.
    trade = ProposedTrade.model_validate(TRADE)
    snapshot = _here(sources, settings).snapshot(trade.season)
    week = snapshot.as_of.stats_through
    assert week > snapshot.as_of.completed_through
    rostered = snapshot.rosters[4][0]
    wopr = {**(snapshot.wopr or {}), rostered: {week - 1: 40}}
    before = snapshot.model_copy(update={"wopr": wopr})
    posted = snapshot.model_copy(update={"wopr": {**wopr, rostered: {week - 1: 40, week: 55}}})
    assert cache_key(trade, posted) != cache_key(trade, before)
    assert finder_cache_key(2026, 4, 12, posted) != finder_cache_key(2026, 4, 12, before)
    outside = _outside_player(snapshot, [4, 12])
    other = before.model_copy(update={"wopr": {**wopr, outside: {week: 55}}})
    assert _both_keys(trade, other) == _both_keys(trade, before)


def test_the_document_version_is_15():
    import analyzer.cache as cache_module

    # The position rank enters the facts, so a document stored before it must never serve.
    # The as-of block says when the week has no chart, so a document stored before that must never serve.
    # A bye is no longer a hole, so a grade stored under the old hole rule must never serve.
    # A grade of three or four sides and the zero rule for a player out for the season change the shape and the rules.
    # The bullets and the deal row take the place of the analysis and the chart block, so the shape changes.
    # Each traded player carries his Season rank and his Recent rank, so the shape changes.
    # A silent row hides, and the roster and standing rows read in plain words, so a stored row must never serve.
    # The usage, injury, upside, handcuff, and schedule rows and the fairness reasons read in plain words too.
    assert cache_module.DOCUMENT_VERSION == 15


# The API over more than one client: the routes at /clients/<slug>/, the old paths as cpc, the grade limit per
# client, the points key of each client in the cache key, and the start over each folder under clients/.

# The second client of these tests. Its folder lives only in the temp folder of a test, never under clients/.
SECOND = "norcal"
# The second client has its own passphrase, so the passphrase of cpc opens none of its routes.
SECOND_HEADERS = {"X-League-Passphrase": "norcal-test"}


def _two_clients(settings, sources, analyzer=None):
    """An app that serves cpc and a second client on the same fixture league, each with its own sources."""
    cpc = _here(sources, settings)
    second = dataclasses.replace(cpc, client=cpc.client.model_copy(update={"slug": SECOND}))
    settings = dataclasses.replace(settings, passphrases={"cpc": PASSPHRASE, SECOND: SECOND_HEADERS["X-League-Passphrase"]})
    app = create_app(settings, [cpc.client, second.client], sources={"cpc": cpc, SECOND: second}, analyzer=analyzer)
    for served in app.state.served.values():
        served.grade_limiter.clock = MovingClock(NOW)
    # The general limit counts every request of the address, so the test moves it past the minute with no wait.
    app.state.limiter.limit = 1000
    return TestClient(app)


def test_the_teams_route_of_a_client_lists_its_teams_and_the_old_path_answers_as_cpc(settings, sources):
    client = _two_clients(settings, sources)
    by_path = client.get("/clients/cpc/teams", params={"season": 2026}, headers=HEADERS)
    assert by_path.status_code == 200
    assert len(by_path.json()["teams"]) == 12
    old = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert old.status_code == 200
    assert old.json() == by_path.json()


def test_each_route_of_a_client_answers_at_its_path(settings, sources):
    client = _two_clients(settings, sources, StubAnalyzer())
    assert client.post(f"/clients/{SECOND}/analyze", json=TRADE, headers=SECOND_HEADERS).status_code == 200
    find = {"season": 2026, "asker": 4, "partner": 4}
    # The same roster twice is 422 from the find route itself, so the path reached the route.
    assert client.post(f"/clients/{SECOND}/find", json=find, headers=SECOND_HEADERS).status_code == 422
    refreshed = []

    class Recorder:
        """The refresh of the second client, which records its season and fetches nothing."""

        def refresh(self, season, *, max_age_seconds):
            refreshed.append(season)
            return RefreshResult(refreshed=[], stale=[], trade_week=6, chart=None)

    client.app.state.sources[SECOND] = Recorder()
    response = client.post(f"/clients/{SECOND}/refresh", params={"season": 2026}, headers=SECOND_HEADERS)
    assert response.json() == {"refreshed": [], "stale": ["chart"]}
    assert refreshed == [2026]


def test_each_client_checks_its_own_passphrase(settings, sources):
    client = _two_clients(settings, sources, StubAnalyzer())
    find = {"season": 2026, "asker": 4, "partner": 12}
    # The passphrase of cpc opens no route of the second client, and the passphrase of the second client opens no route
    # of cpc. The wrong passphrase is 401 with no body, as before.
    for path, body in ((f"/clients/{SECOND}/analyze", TRADE), (f"/clients/{SECOND}/find", find)):
        response = client.post(path, json=body, headers=HEADERS)
        assert (response.status_code, response.content) == (401, b""), path
    for path, body in (("/clients/cpc/analyze", TRADE), ("/clients/cpc/find", find)):
        assert client.post(path, json=body, headers=SECOND_HEADERS).status_code == 401, path
    assert client.post(f"/clients/{SECOND}/analyze", json=TRADE, headers=SECOND_HEADERS).status_code == 200
    assert client.post("/clients/cpc/analyze", json=TRADE, headers=HEADERS).status_code == 200


def test_an_app_with_a_client_that_has_no_passphrase_does_not_build(settings, sources):
    # A client with no passphrase would run open, so the app refuses it before any route exists.
    second = CLIENT.model_copy(update={"slug": SECOND})
    with pytest.raises(ValueError, match="CORNERSTONE_PASSPHRASE_NORCAL"):
        create_app(settings, [CLIENT, second], sources=_cpc(_here(sources, settings)))


def test_an_old_path_checks_the_passphrase_of_cpc(settings, sources):
    client = _two_clients(settings, sources, StubAnalyzer())
    assert client.post("/analyze", json=TRADE, headers=SECOND_HEADERS).status_code == 401
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200


def test_a_client_the_api_does_not_serve_is_404(settings, sources):
    client = _two_clients(settings, sources)
    response = client.get("/clients/nope/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 404
    assert response.json() == {"detail": "The API serves no client nope."}


def test_the_health_route_stays_at_the_root(settings, sources):
    client = _two_clients(settings, sources)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/clients/cpc/health").status_code == 404


def test_the_grade_limit_counts_per_client_and_per_address(settings, sources):
    # A fallback is never cached, so each repeat is a new grade.
    client = _two_clients(settings, sources, StubAnalyzer(claude_letters=["A", "C"]))
    for _ in range(GRADES_PER_MINUTE):
        assert client.post("/clients/cpc/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert client.post("/clients/cpc/analyze", json=TRADE, headers=HEADERS).status_code == 429
    # The old path is cpc, so it shares the limit of cpc.
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 429
    assert client.post(f"/clients/{SECOND}/analyze", json=TRADE, headers=SECOND_HEADERS).status_code == 200
    # Another address in the same client has its own count.
    other = {**HEADERS, "Fly-Client-IP": "203.0.113.7"}
    assert client.post("/clients/cpc/analyze", json=TRADE, headers=other).status_code == 200


def test_each_client_keeps_its_own_result_cache(settings, sources):
    analyzer = StubAnalyzer()
    client = _two_clients(settings, sources, analyzer)
    client.post("/clients/cpc/analyze", json=TRADE, headers=HEADERS)
    client.post("/clients/cpc/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 1
    # The same roster ids in another league are another trade, so the stored grade of cpc never serves it.
    client.post(f"/clients/{SECOND}/analyze", json=TRADE, headers=SECOND_HEADERS)
    assert analyzer.calls == 2
    assert (settings.result_cache_dir / "cpc").is_dir()
    assert (settings.result_cache_dir / SECOND).is_dir()


def _with_week_n_points(snapshot, player, key, points):
    """The snapshot with `key` set to `points` on the week N stat line of `player`."""
    week_n = snapshot.stats.weeks[snapshot.as_of.stats_through]
    stats = {**week_n.stats, player: {**week_n.stats.get(player, {}), key: points}}
    weeks = {**snapshot.stats.weeks, week_n.week: week_n.model_copy(update={"stats": stats})}
    return snapshot.model_copy(update={"stats": snapshot.stats.model_copy(update={"weeks": weeks})})


def test_the_cache_key_reads_the_points_key_of_the_client(settings, sources):
    trade = ProposedTrade.model_validate(TRADE)
    half = _here(sources, settings).snapshot(trade.season)
    client = half.client
    full = half.model_copy(update={"client": client.model_copy(
        update={"settings": client.settings.model_copy(update={"reception_points": 1.0})})})
    assert full.client.settings.points_key == "pts_ppr"
    player = half.rosters[4][0]
    # A full PPR league grades on pts_ppr, so a new pts_ppr number misses and a new pts_half_ppr number keeps the hit.
    assert cache_key(trade, _with_week_n_points(full, player, "pts_ppr", 77.0)) != cache_key(trade, full)
    assert cache_key(trade, _with_week_n_points(full, player, "pts_half_ppr", 77.0)) == cache_key(trade, full)
    assert finder_cache_key(2026, 4, 12, _with_week_n_points(full, player, "pts_ppr", 77.0)) != finder_cache_key(
        2026, 4, 12, full)
    # The half PPR league of cpc reads pts_half_ppr, as before.
    assert cache_key(trade, _with_week_n_points(half, player, "pts_half_ppr", 77.0)) != cache_key(trade, half)


def _fixture_settings(league_id, path):
    """The League settings of the week 6 fixture league, for any league id, with no fetch."""
    return league_settings(RawLeague.model_validate_json(FIXTURE_LEAGUE.read_text(encoding="utf-8")))


def _second_folder(root):
    """A second client folder in the temp repo `root`: the CPC client.toml and the league file of 2026."""
    folder = client_dir(root, SECOND)
    shutil.copytree(client_dir(root, "cpc"), folder)
    return folder


def test_the_start_reads_each_folder_under_clients(tmp_path):
    root = cli_root(tmp_path)
    _second_folder(root)
    clients = load_clients(root, _fixture_settings)
    assert [client.slug for client in clients] == ["cpc", SECOND]
    assert all(client.settings.team_count == 12 for client in clients)
    assert league_file(client_dir(root, SECOND), 2026).is_file()


def test_a_bad_client_toml_stops_the_start_with_the_file_and_the_key(tmp_path):
    root = cli_root(tmp_path)
    folder = _second_folder(root)
    path = folder / "client.toml"
    path.write_text("\n".join(line for line in path.read_text().splitlines() if not line.startswith("timezone")))
    with pytest.raises(ClientError) as error:
        load_clients(root, _fixture_settings)
    assert str(path) in str(error.value)
    assert "- timezone: is required" in str(error.value)
