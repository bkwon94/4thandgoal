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

import anthropic
import httpx
import pytest
from cpc import FIXTURE_LEAGUE, cli_root, cpc_client
from fakes import NEWS_RECORDED, FakeJev, recorded_news
from fastapi.testclient import TestClient

from analyzer.advisor import AdvisorOut, read_trade
from analyzer.cache import ResultCache, cache_key, finder_cache_key
from analyzer.finder_pick import NO_OFFER, SAME_FACT, FinderPickOut, PickOut, pick_trades
from analyzer.finder_search import search
from analyzer.ratelimit import GradeLimiter, seconds_to_midnight
from analyzer.trade import ProposedTrade
from analyzer.trade_news import NewsFeed
from analyzer.tunables import GRADES_PER_MINUTE
from cornerstone_api.app import GRADE_COUNTS_FILE, create_app, load_clients
from cornerstone_api.settings import RATE_LIMIT_PER_MINUTE, Settings
from cornerstone_api.sources import Sources
from cornerstone_api.value_models import VALUE_MODELS
from facts.writer import FINDER_PICK_MODEL, ClaudeWriter
from league.client import ClientError
from league.jev_port import JevError
from league.live import RefreshResult
from league.nflverse import CACHE_MAX_AGE_SECONDS, DEPTH_CHARTS_URL, SCHEDULES_URL, cache_path
from league.paths import client_dir, league_file
from league.provider.raw import RawLeague, RawTrending
from league.provider.sleeper import fetch_news, league_settings, load_raw
from league.snapshot import SnapshotPlayer
from league.tunables import TEAMS_CACHE_SECONDS

ET = ZoneInfo("America/New_York")
# The client the builds and fetches of these tests read.
# The models of the API, so the client holds the package values of eggs, as the real start reads them.
CLIENT = cpc_client(models=VALUE_MODELS)
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
    """A repo with the week 6 history, a fresh nflverse cache, and the cpc Playbook that the Advisor reads."""
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    (tmp_path / "prompts").mkdir()
    shutil.copy(CLIENT.voice_dir / "playbook.md", tmp_path / "prompts" / "playbook.md")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached)
    return tmp_path


def _here(sources: Sources, settings: Settings) -> Sources:
    """The sources with the client of the test folder, so a snapshot reads and writes only that folder."""
    return dataclasses.replace(sources, client=cpc_client(at=settings.repo, models=VALUE_MODELS))


def _recorded_trending() -> list[RawTrending]:
    """The trending adds that the week 9 build recorded. The week 6 fixture has no trending file, and a test makes no
    network call."""
    path = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "data" / "2026" / "week-09" / "raw" / "trending.json"
    return [RawTrending.model_validate(row) for row in json.loads(path.read_text())]


@pytest.fixture
def sources(fixture_raw_dir, chart_week6):
    return Sources(
        fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), FETCHED),
        fetch_nflverse=_no_network,
        fetch_history_week=_no_history_fetch,
        read_chart=lambda repo, season_start, week, lines, **_: chart_week6,
        clock=lambda: NOW, client=CLIENT, fetch_trending=_recorded_trending,
    )


@pytest.fixture
def settings(repo):
    return Settings(passphrases={"cpc": PASSPHRASE}, repo=repo, result_cache_dir=repo / "results",
                    commissioner_keys={"cpc": "commissioner-test"})


# The Case of the stub Advisor. It names no player and no number, so it passes the guards of any trade.
CASE = ("If you believe the role of the player you get holds, this is worth it. You give up a known starter. "
        "The other manager gets the steadier piece now. Push for it only if your lineup needs the help.")


def passing_read(user: str, **changes) -> dict:
    """A read that passes every guard for any trade: each Bullet cites the week fact and names no one."""
    rosters = [int(r) for r in re.findall(r"^Side: roster (\d+),", user, re.MULTILINE)]
    bullets = [{"text": "The trade lands in the middle of the season.", "mark": mark, "fact_id": "trade.week"}
               for mark in ("for", "against", "even")]
    # A week with no chart has the trade.chart fact, and the guard then needs the Case to say the chart is missing.
    case = CASE + " The chart of this week is missing." if "trade.chart" in user else CASE
    out = {"lean": "Lean yes", "case": case, "fairness": "fair", "gives_more": None,
           "sides": [{"roster_id": rid, "gains": "It gets help where it needs it.", "bullets": bullets}
                     for rid in rosters]}
    return out | changes


class StubAdvisor:
    """The Claude call of the Advisor with no network: it answers from a list of builders, one per call.

    Each builder takes the user message and gives the output. The last builder answers every later call.
    """

    def __init__(self, *builders):
        self.builders = list(builders) or [passing_read]
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system, user, output_model):
        assert output_model is AdvisorOut
        self.calls.append((system, user))
        build = self.builders[min(len(self.calls), len(self.builders)) - 1]
        return AdvisorOut.model_validate(build(user))


class StubAnalyzer:
    """The real read of the Advisor with the stub Advisor, FakeJev, and the recorded news, so the sheet, the guards,
    and the retry run.

    `store` False drops the result cache of the app, so each repeat is a new grade.
    """

    def __init__(self, advisor=None, jev=None, store=True, news=None):
        self.calls = 0
        self.advisor = advisor or StubAdvisor()
        self.jev = jev or FakeJev()
        self.store = store
        self.news = news or NewsFeed(fetch=recorded_news, now=lambda: NEWS_RECORDED)

    def __call__(self, trade, snapshot):
        self.calls += 1
        return read_trade(trade, snapshot, jev=self.jev, news=self.news, call=self.advisor)


class NoStore(ResultCache):
    """A result cache that keeps nothing, so each repeat runs the analyzer again."""

    def put(self, key, document):
        return None


def _drop_store(app):
    """Give each client of the app a cache that keeps nothing."""
    for slug, served in list(app.state.served.items()):
        app.state.served[slug] = dataclasses.replace(served, cache=NoStore(served.cache.directory))


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
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), analyzer=analyzer)
    if analyzer is not None and not getattr(analyzer, "store", True):
        _drop_store(app)
    return TestClient(app)


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
    # A chart read that raises gives no chart, and a week with no chart reads the other facts alone.
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


class MeteredAnalyzer(StubAnalyzer):
    """The stub read, after one Claude call of a ClaudeWriter over a stub client, so the press meter counts it."""

    def __call__(self, trade, snapshot):
        usage = type("Usage", (), {"input_tokens": 1000, "output_tokens": 100, "cache_read_input_tokens": 0,
                                   "cache_creation_input_tokens": 0})
        response = type("Response", (), {"stop_reason": "end_turn", "parsed_output": "parsed", "usage": usage})()
        messages = type("Messages", (), {"parse": lambda self, **kwargs: response})()
        ClaudeWriter(client=type("Client", (), {"messages": messages})()).parse("user", AdvisorOut, "system")
        return super().__call__(trade, snapshot)


def _press_lines(caplog, route):
    return [m for m in caplog.messages if m.startswith(f"Press of {route} for cpc: ")]


def test_each_analyze_press_logs_one_line_with_its_time_and_its_cost(settings, sources, caplog):
    caplog.set_level("INFO", logger="analyzer.routes")
    client = _client(settings, sources, MeteredAnalyzer())
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    # 1,000 input tokens at $4 per million and 100 output tokens at $20 per million on Opus.
    [line] = _press_lines(caplog, "analyze")
    assert re.search(r"time=\d+\.\ds cost=\$0\.0060 claude_calls=1$", line)
    # A cached repeat logs its own line, at no cost.
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert _press_lines(caplog, "analyze")[1].endswith("cost=$0.0000 claude_calls=0")


def test_each_find_press_logs_one_line_with_its_time_and_its_cost(settings, sources, caplog):
    caplog.set_level("INFO", logger="analyzer.routes")
    response = _find_client(settings, sources).post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS)
    assert response.status_code == 200
    [line] = _press_lines(caplog, "find")
    assert re.search(r"time=\d+\.\ds cost=\$\d+\.\d{4} claude_calls=\d+$", line)


def test_a_good_request_returns_the_read_of_the_advisor(settings, sources):
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
    # The document leads with the Lean and the Case, then the fairness, then the Bullets of each side.
    assert list(doc)[:5] == ["trade", "lean", "case", "fairness", "sides"]
    assert doc["lean"] == "Lean yes"
    assert doc["case"] == CASE
    assert doc["fairness"] == {"state": "fair", "gives_more": None, "sides": [
        {"roster_id": 4, "reason": "It gets help where it needs it."},
        {"roster_id": 12, "reason": "It gets help where it needs it."}]}
    assert [side["roster_id"] for side in doc["sides"]] == [4, 12]
    assert list(doc["sides"][0]) == ["roster_id", "bullets", "week_lines"]
    first = doc["sides"][0]["bullets"][0]
    assert list(first) == ["text", "mark", "fact_id", "fact_text"]
    assert first["fact_id"] == "trade.week"
    assert first["fact_text"].startswith("The trade is in week 6 of the 2026 season.")
    assert [b["mark"] for b in doc["sides"][0]["bullets"]] == ["for", "against", "even"]
    # The fetch on Monday holds the week 6 stat lines, so the player stats read the 14 known games of week 6.
    # The fixture player file has week 6 rows for 6 of those games, so the usage of 8 games is pending.
    assert doc["as_of"] == {"chart_week": 6, "stats_through": 6, "completed_through": 5,
                            "rosters_fetched": "2026-10-19T09:30:00-04:00",
                            "known_games": {"week": 6, "games": 14, "in_progress": 0, "pending": {"usage": 8}},
                            "no_chart": False, "no_chart_note": None}


# The words a key of the read must never hold: a letter, a factor, a decision, or an answer.
OLD_KEYS = ("letter", "factor", "decision", "answer")


def _keys(value) -> list[str]:
    """Every key of a document, at every depth."""
    if isinstance(value, dict):
        return [*value, *(key for item in value.values() for key in _keys(item))]
    if isinstance(value, list):
        return [key for item in value for key in _keys(item)]
    return []


def test_no_key_of_the_read_holds_a_letter_a_factor_a_decision_or_an_answer(settings, sources):
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert [key for key in _keys(doc) if any(word in key for word in OLD_KEYS)] == []


def test_a_lopsided_read_names_the_side_that_gives_more(settings, sources):
    advisor = StubAdvisor(lambda user: passing_read(user, lean="Pass", fairness="lopsided", gives_more=4))
    doc = _client(settings, sources, StubAnalyzer(advisor)).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert doc["lean"] == "Pass"
    assert doc["fairness"]["state"] == "lopsided"
    assert doc["fairness"]["gives_more"] == 4


def test_the_advisor_reads_the_jev_answers_of_the_trade(settings, sources):
    advisor, jev = StubAdvisor(), FakeJev()
    _client(settings, sources, StubAnalyzer(advisor, jev)).post("/analyze", json=TRADE, headers=HEADERS)
    # The first request asks the questions of the trade. The second holds the log-only checks of the read.
    assert len(jev.requests) == 2
    assert "fair" in jev.requests[0].questions
    _, user = advisor.calls[0]
    for fid in ("JEV.fair", "JEV.need.4", "JEV.need.12", "JEV.accept.12"):
        assert f"- {fid}: " in user


def _blocked(request):
    raise httpx.ConnectError("the host of the news feed is blocked", request=request)


def test_a_blocked_news_feed_still_gives_a_read_with_no_news_fact(settings, sources, caplog):
    advisor = StubAdvisor()
    news = NewsFeed(fetch=lambda pid: fetch_news(pid, transport=httpx.MockTransport(_blocked)))
    response = _client(settings, sources, StubAnalyzer(advisor, news=news)).post("/analyze", json=TRADE,
                                                                                headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["lean"] == "Lean yes"
    assert "NEWS." not in advisor.calls[0][1]
    assert "Sleeper endpoint failed: https://api.sleeper.app/players/nfl/7569/news" in caplog.text


def test_a_second_press_within_1_hour_fetches_no_news_for_the_same_player(settings, sources, caplog):
    fetched = []

    def counted(pid):
        fetched.append(pid)
        return recorded_news(pid)

    caplog.set_level("INFO", logger="analyzer.trade_news")
    client = _client(settings, sources, StubAnalyzer(news=NewsFeed(fetch=counted, now=lambda: NEWS_RECORDED)))
    client.post("/analyze", json=TRADE, headers=HEADERS)
    other = {"season": 2026, "sides": _sides(["7569"], ["8146"]), "asker": 4}
    assert client.post("/analyze", json=other, headers=HEADERS).status_code == 200
    assert fetched.count("7569") == 1
    assert "News of player 7569 from the cache" in caplog.text


def _bad_bullet(change):
    """A builder whose first Bullet of the asker breaks a guard with `change`."""
    def build(user):
        out = passing_read(user)
        out["sides"][0]["bullets"] = [out["sides"][0]["bullets"][0] | change, *out["sides"][0]["bullets"][1:]]
        return out
    return build


@pytest.mark.parametrize("change, failure", [
    ({"fact_id": "NO.such"}, "fact ID NO.such is not on the sheet"),
    ({"text": "The trade lands in week 9."}, "number 9 is not in the cited facts"),
    ({"text": "The trade moves trade value to the other side."}, "the words 'trade value' are not allowed"),
    ({"text": "Josh Jacobs would fit here."}, "the name Josh Jacobs is not in the trade"),
])
def test_a_read_that_fails_a_guard_retries_once_and_the_second_read_stands(settings, sources, change, failure):
    advisor = StubAdvisor(_bad_bullet(change), passing_read)
    doc = _client(settings, sources, StubAnalyzer(advisor)).post("/analyze", json=TRADE, headers=HEADERS).json()
    assert len(advisor.calls) == 2
    assert failure in advisor.calls[1][1]
    assert doc["sides"][0]["bullets"][0]["text"] == "The trade lands in the middle of the season."


# The plain error of a failed read. The page shows it with Try Again.
ADVISOR_ERROR = ("The read of this trade did not come through. Try again in a minute. "
                 "This try does not count toward your grades.")


def test_two_failed_reads_give_an_honest_error_that_costs_no_grade(settings, sources, caplog):
    advisor = StubAdvisor(_bad_bullet({"fact_id": "NO.such"}))
    analyzer = StubAnalyzer(advisor)
    client = _client(settings, sources, analyzer)
    response = client.post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 503
    assert response.json() == {"detail": {"message": ADVISOR_ERROR}}
    assert len(advisor.calls) == 2
    assert "advisor attempt 2 failed" in caplog.text
    # The count file holds no grade of the address, so a failure costs the manager nothing.
    path = settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE
    assert json.loads(path.read_text())["counts"].get("testclient", 0) == 0
    # A failed read is not stored, so the next press calls the Advisor again.
    client.post("/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 2


def test_an_anthropic_key_that_is_not_valid_gives_the_honest_error_after_two_calls(settings, sources):
    calls = []

    def refused(system, user, output_model):
        calls.append(user)
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        raise anthropic.AuthenticationError("invalid x-api-key", response=httpx.Response(401, request=request),
                                            body=None)

    analyzer = StubAnalyzer(advisor=refused)
    response = _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 503
    assert response.json() == {"detail": {"message": ADVISOR_ERROR}}
    assert len(calls) == 2
    path = settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE
    assert json.loads(path.read_text())["counts"].get("testclient", 0) == 0


def test_failed_reads_never_use_up_the_grade_limit(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    failing = StubAnalyzer(StubAdvisor(_bad_bullet({"fact_id": "NO.such"})))
    client = _graded_client(settings, sources, MovingClock(NOW), failing)
    for _ in range(GRADES_PER_MINUTE + 1):
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 503
    client.app.state.analyzer = StubAnalyzer()
    assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200


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
    # Each side has its own Bullets, so a trade of three sides reads one list per side.
    assert all(len(side["bullets"]) == 3 for side in doc["sides"])


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


def test_a_week_with_no_chart_still_reads_and_says_so(settings, fixture_raw_dir):
    # The chart posts hours after the trade week starts, so the grade runs in that window with no chart.
    analyzer = StubAnalyzer()
    response = _client(settings, _no_chart_sources(fixture_raw_dir), analyzer).post(
        "/analyze", json=TRADE, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert analyzer.calls == 1
    assert doc["lean"] == "Lean yes"
    assert doc["as_of"]["chart_week"] is None
    assert doc["as_of"]["no_chart"] is True
    assert doc["as_of"]["no_chart_note"] == "This week's player values are not out yet."
    assert "chart" in doc["missing"]


def test_a_grade_with_no_chart_and_a_grade_with_the_chart_have_different_keys(settings, sources, fixture_raw_dir):
    # The first chart post of the week must give a fresh grade, not the stored grade with no chart.
    trade = ProposedTrade.model_validate(TRADE)
    with_chart = _here(sources, settings).snapshot(trade.season)
    no_chart = _here(_no_chart_sources(fixture_raw_dir), settings).snapshot(trade.season)
    assert cache_key(trade, no_chart) != cache_key(trade, with_chart)
    assert finder_cache_key(2026, 4, 12, no_chart) != finder_cache_key(2026, 4, 12, with_chart)


def test_a_result_cached_under_another_document_version_never_serves(settings, sources, monkeypatch):
    import analyzer.cache as cache_module

    analyzer = StubAnalyzer()
    monkeypatch.setattr(cache_module, "DOCUMENT_VERSION", 1)
    _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    monkeypatch.setattr(cache_module, "DOCUMENT_VERSION", 2)
    _client(settings, sources, analyzer).post("/analyze", json=TRADE, headers=HEADERS)
    assert analyzer.calls == 2


def test_the_document_has_the_fairness_block_after_the_case(settings, sources):
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    block = doc["fairness"]
    assert list(block) == ["state", "gives_more", "sides"]
    assert [list(side) for side in block["sides"]] == [["roster_id", "reason"]] * 2
    assert [side["roster_id"] for side in block["sides"]] == [4, 12]


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


def _graded_at(snapshot, at: datetime):
    return snapshot.model_copy(update={"as_of": snapshot.as_of.model_copy(update={"graded_at": at})})


def test_the_cache_key_tells_a_tuesday_or_wednesday_grade_from_the_rest_of_the_week(settings, sources):
    # A Week line graded on a Tuesday or a Wednesday says "listed Out last week", so a grade of Thursday must miss it.
    trade = ProposedTrade.model_validate(TRADE)
    # The age of the depth chart changes the key too, so this snapshot holds no chart time and only the day counts.
    snapshot = _here(sources, settings).snapshot(trade.season).model_copy(update={"depth_chart_dt": None})
    tuesday, wednesday, thursday, friday = (datetime(2026, 10, day, 12, 0, tzinfo=ET) for day in (20, 21, 22, 23))
    assert cache_key(trade, _graded_at(snapshot, tuesday)) == cache_key(trade, _graded_at(snapshot, wednesday))
    assert cache_key(trade, _graded_at(snapshot, thursday)) == cache_key(trade, _graded_at(snapshot, friday))
    assert cache_key(trade, _graded_at(snapshot, tuesday)) != cache_key(trade, _graded_at(snapshot, thursday))


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


def test_the_fixture_document_names_no_letter():
    fixture = json.loads(RESPONSE_FIXTURE.read_text(encoding="utf-8"))
    # A letter grade on its own, as in "C", or the word "letter". Neither may reach the document.
    found = [text for text in _strings(fixture)
             if re.search(r"\b[A-F]\b", text) or re.search(r"\bletters?\b", text, re.IGNORECASE)]
    assert found == []


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





def test_past_the_rate_limit_the_route_is_429_with_a_retry_after(settings, sources):
    client = _client(settings, sources)
    for _ in range(RATE_LIMIT_PER_MINUTE):
        # Wrong guesses count too, so a stranger cannot loop through passphrases.
        assert client.get("/teams", params={"season": 2026}).status_code == 401
    response = client.get("/teams", params={"season": 2026}, headers=HEADERS)
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    assert client.get("/health").status_code == 200


@pytest.mark.parametrize("value, count", [("25", 25), (None, RATE_LIMIT_PER_MINUTE)])
def test_the_rate_limit_comes_from_the_environment_or_the_default(settings, sources, monkeypatch, value, count):
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE_CPC", PASSPHRASE)
    if value is None:
        monkeypatch.delenv("CORNERSTONE_RATE_LIMIT_PER_MINUTE", raising=False)
    else:
        monkeypatch.setenv("CORNERSTONE_RATE_LIMIT_PER_MINUTE", value)
    from_env = Settings.from_env(["cpc"])
    client = _client(dataclasses.replace(settings, rate_limit_per_minute=from_env.rate_limit_per_minute), sources)
    for _ in range(count):
        assert client.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 200
    assert client.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 429


@pytest.mark.parametrize("value", ["0", "-5", "2.5", "ten"])
def test_a_bad_rate_limit_value_stops_the_start_and_names_the_env_value(monkeypatch, value):
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE_CPC", PASSPHRASE)
    monkeypatch.setenv("CORNERSTONE_RATE_LIMIT_PER_MINUTE", value)
    with pytest.raises(RuntimeError, match="CORNERSTONE_RATE_LIMIT_PER_MINUTE"):
        Settings.from_env(["cpc"])


def test_each_fly_client_address_has_its_own_rate_limit(settings, sources):
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
    """An analyzer whose app keeps no result, so each repeat is a new grade."""
    return StubAnalyzer(store=False)


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
    doc = _client(settings, sources, StubAnalyzer()).post("/analyze", json=TRADE, headers=HEADERS).json()
    fixture = json.loads(RESPONSE_FIXTURE.read_text(encoding="utf-8"))
    # The fixture's empty lists, such as stale, match any list, because a live run may fill them.
    assert _same_shape(doc, _shape(fixture))
    # Every item of a list has the shape of the fixture's first item, so no side or Bullet drops a key.
    for side in doc["sides"]:
        assert _shape(side) == _shape(fixture["sides"][0])
        for bullet in side["bullets"]:
            assert _shape(bullet) == _shape(fixture["sides"][0]["bullets"][0])


# The keys whose numbers are ids, weeks, the season, or the stamp. No other number may appear in the document.
# The fairness block's gives_more is a roster id, and so are the to and from of each traded player.
NUMBER_KEYS = {"roster_id", "asker", "for_roster", "gives_more", "chart_week", "stats_through", "completed_through",
               "season", "week", "games", "in_progress", "snaps", "usage", "to", "from"}
# The strings that may hold digits: ids, URLs, the stamp, and the names that managers and Sleeper set.
# A Season rank and a Recent rank, such as WR60, hold the rank as digits. The offer id of a Finder trade holds ids.
DIGIT_STRING_KEYS = {"player_id", "headshot", "rosters_fetched", "team", "name", "season_rank", "recent_rank",
                     "offer_id"}


def _digits_outside_ids(value, key=None):
    """The numbers and the strings with digits under any key that may not hold them."""
    if isinstance(value, dict):
        if set(value) == {"week", "text"}:
            # The code writes the Week line with its weeks, its counts, its top N, and the rank of each opponent.
            value = {"week": value["week"]}
        if set(value) == {"text", "mark", "fact_id", "fact_text"}:
            # A Bullet holds only the numbers of its fact, and the guards of the Advisor check that. The fact text is
            # code, with its own numbers, and the fact id names a player id.
            return []
        if set(value) == {"roster_id", "reason"}:
            # A fairness side gives what the side gains, in the words of the Advisor, whose guards check its numbers.
            value = {"roster_id": value["roster_id"]}
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
ALL_SOURCES = ["schedules", "depth charts", "id map", "injuries", "expected points", "player weeks", "team stats"]


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


# The find route. The Finder search runs with FakeJev at the Jev port, and the stub Advisor makes the pick, so the
# sheets, the guards, the retry, and the fallback of the pick run with no network.
FIND = {"season": 2026, "asker": 2, "partner": 3}
HEADLINE = "A swap that fits both lineups."


def passing_pick(user: str, **changes) -> dict:
    """A pick that passes every guard: the first offers of the shortlist, up to 3, each Bullet on the week fact."""
    offers = re.findall(r"^Offer (\S+)$", user, re.MULTILINE)[:3]
    bullets = [{"text": "The trade lands in the middle of the season.", "mark": "for", "fact_id": "trade.week"},
               {"text": "The other manager gets help where he needs it.", "mark": "for", "fact_id": "trade.week"}]
    out = {"picks": [{"offer_id": offer, "lean": "Lean yes", "headline": HEADLINE, "bullets": bullets}
                     for offer in offers], "none_line": None}
    return out | changes


class StubPicker:
    """The Claude call of the Finder pick with no network: it answers from a list of builders, one per call.

    Each builder takes the user message and gives the output. The last builder answers every later call.
    """

    def __init__(self, *builders):
        self.builders = list(builders) or [passing_pick]
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system, user, output_model):
        assert output_model is FinderPickOut
        self.calls.append((system, user))
        build = self.builders[min(len(self.calls), len(self.builders)) - 1]
        return FinderPickOut.model_validate(build(user))


def passing_repair(user: str) -> dict:
    """A repaired pick that passes every guard: the one offer of the repair message, each Bullet on the week fact."""
    [pick] = passing_pick(user)["picks"]
    return pick


class StubRepair:
    """The Claude call that repairs one failed pick, with no network. It answers from a list of builders, one per
    call, as StubPicker does. Each builder takes the user message and gives one pick."""

    def __init__(self, *builders):
        self.builders = list(builders) or [passing_repair]
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system, user, output_model):
        assert output_model is PickOut
        self.calls.append((system, user))
        build = self.builders[min(len(self.calls), len(self.builders)) - 1]
        return PickOut.model_validate(build(user))


def _no_partner(key, question, state):
    """A Jev that stops every partner at the partner filter, so the shortlist is empty."""
    return 0.1 if key.startswith(("partner_", "asker_")) else 0.9


def _find_client(settings, sources, picker=None, clock=None, jev=None, news=None, repair=None):
    """A client whose Finder search asks `jev` (FakeJev by default), whose pick makes the call of `picker`, and whose
    repair of a failed pick makes the call of `repair`.

    With a clock, the grade and general limits read it.
    """
    news = news or NewsFeed(fetch=recorded_news, now=lambda: NEWS_RECORDED)
    jev = jev or FakeJev()
    client = TestClient(create_app(
        settings, [CLIENT], sources=_cpc(_here(sources, settings)), analyzer=StubAnalyzer(),
        finder_search=functools.partial(search, jev=jev),
        finder_pick=functools.partial(pick_trades, news=news, jev=jev, call=picker or StubPicker(),
                                      repair_call=repair or StubRepair())))
    if clock is not None:
        client.app.state.served["cpc"].grade_limiter.clock = clock
        client.app.state.limiter.clock = lambda: clock().timestamp()
    return client


def test_the_bullets_of_each_pick_get_the_jev_checks_and_they_only_log(settings, sources, caplog):
    caplog.set_level("INFO", logger="analyzer.read_jev_check")
    jev = FakeJev()
    doc = _find_client(settings, sources, jev=jev).post("/find", json={"season": 2026, "asker": 2},
                                                        headers=HEADERS).json()
    checks = [r for r in jev.requests if r.questions and all(k.startswith(("faithful.", "rumor.")) for k in r.questions)]
    # One request per pick, with one faithfulness question per Bullet of that pick.
    assert [sum(k.startswith("faithful.") for k in r.questions) for r in checks] == [
        len(item["bullets"]) for item in doc["trades"]]
    assert caplog.text.count("Jev checks of the read, log only") == len(doc["trades"])


def test_a_failed_jev_check_of_a_pick_never_blocks_the_picks(settings, sources, caplog):
    def answer(key, question, state):
        if key.startswith(("faithful.", "rumor.")):
            raise JevError("429 Too Many Requests")
        return 0.9

    doc = _find_client(settings, sources, jev=FakeJev(answer=answer)).post(
        "/find", json={"season": 2026, "asker": 2}, headers=HEADERS).json()
    assert doc["fallback"] is False and doc["trades"]
    assert "The Jev checks of the read failed" in caplog.text


def test_find_with_no_partner_gives_up_to_three_picks_each_with_a_headline_and_bullets(settings, sources):
    picker = StubPicker()
    response = _find_client(settings, sources, picker).post("/find", json={"season": 2026, "asker": 2},
                                                            headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert len(picker.calls) == 1
    assert doc["fallback"] is False
    assert doc["empty"] is None
    assert 1 <= len(doc["trades"]) <= 3
    for item in doc["trades"]:
        assert item["headline"] == HEADLINE
        assert 2 <= len(item["bullets"]) <= 3
        # Each Bullet carries the text of its fact, so a tap on the card opens the fact.
        for bullet in item["bullets"]:
            assert set(bullet) == {"text", "mark", "fact_id", "fact_text"}
            assert bullet["fact_text"].startswith("The trade is in week")
        assert item["fact_lines"] == []
        # The asker's side comes first, as in the analyze document.
        assert item["sides"][0]["roster_id"] == 2
    assert doc["as_of"]["chart_week"] == 6


def test_find_with_no_partner_runs_the_partner_filter_on_every_other_team(settings, sources, caplog):
    jev = FakeJev()
    client = _find_client(settings, sources, jev=jev)
    with caplog.at_level("INFO", logger="analyzer"):
        response = client.post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    # Each trade names its own partner in its sides, so the pair has no partner.
    assert doc["trade_pair"]["asker"]["roster_id"] == 2
    assert doc["trade_pair"]["partner"] is None
    filtered = sorted(r.state["teams"]["partner"]["roster_id"] for r in jev.requests if "partner_has" in r.questions)
    assert filtered == [rid for rid in range(1, 13) if rid != 2]
    assert sum("Partner filter of" in record.getMessage() for record in caplog.records) == 11


def test_find_with_a_partner_keeps_every_pick_to_that_partner(settings, sources):
    jev = FakeJev()
    doc = _find_client(settings, sources, jev=jev).post("/find", json=FIND, headers=HEADERS).json()
    assert [r.state["teams"]["partner"]["roster_id"] for r in jev.requests if "partner_has" in r.questions] == [3]
    assert doc["trade_pair"]["partner"]["roster_id"] == 3
    assert doc["trades"]
    assert all([side["roster_id"] for side in item["sides"]] == [2, 3] for item in doc["trades"])


def test_a_find_with_no_partner_and_one_with_a_partner_have_two_cache_keys(settings, sources):
    snapshot = _here(sources, settings).snapshot(2026)
    assert finder_cache_key(2026, 2, None, snapshot) != finder_cache_key(2026, 2, 3, snapshot)


def test_an_empty_shortlist_gives_the_empty_line_and_makes_no_claude_call(settings, sources):
    picker = StubPicker()
    doc = _find_client(settings, sources, picker, jev=FakeJev(answer=_no_partner)).post(
        "/find", json=FIND, headers=HEADERS).json()
    assert doc["trades"] == []
    assert doc["empty"] == NO_OFFER
    assert doc["fallback"] is False
    assert picker.calls == []
    # The finder reads the same bounds and the same known games as the grade.
    assert doc["as_of"]["stats_through"] == 6
    assert doc["as_of"]["completed_through"] == 5
    assert doc["as_of"]["known_games"] == {"week": 6, "games": 14, "in_progress": 0, "pending": {"usage": 8}}


def test_an_empty_find_counts_one_grade_and_a_repeat_is_cached_with_no_claude_call(settings, sources):
    picker = StubPicker()
    client = _find_client(settings, sources, picker, MovingClock(NOW), jev=FakeJev(answer=_no_partner))
    first = client.post("/find", json=FIND, headers=HEADERS).json()
    assert first["trades"] == []
    assert client.post("/find", json=FIND, headers=HEADERS).json() == first
    assert picker.calls == []
    assert json.loads((settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).read_text())["counts"] == {"testclient": 1}


def test_a_find_in_a_week_with_no_chart_answers_and_says_so(settings, fixture_raw_dir):
    response = _find_client(settings, _no_chart_sources(fixture_raw_dir)).post("/find", json=FIND, headers=HEADERS)
    assert response.status_code == 200
    doc = response.json()
    assert doc["trades"]
    assert doc["as_of"]["no_chart"] is True
    assert doc["as_of"]["no_chart_note"] == "This week's player values are not out yet."


def test_find_needs_the_passphrase(settings, sources):
    response = _find_client(settings, sources).post("/find", json=FIND)
    assert response.status_code == 401
    assert response.content == b""


@pytest.mark.parametrize("pair, message", [
    ({"asker": 2, "partner": 2}, "Pick two different teams."),
    ({"asker": 2, "partner": 99}, "Roster 99 is not in the league"),
])
def test_find_with_the_same_roster_twice_or_a_roster_not_in_the_league_is_422(settings, sources, pair, message):
    response = _find_client(settings, sources).post("/find", json={"season": 2026, **pair}, headers=HEADERS)
    assert response.status_code == 422
    assert response.json() == {"detail": {"message": message}}
    assert not (settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).exists()


def test_the_sixth_find_in_a_minute_is_429_with_the_minute_text(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    client = _find_client(settings, sources, clock=MovingClock(NOW))
    # A new partner each time, so no request is a cached repeat and each one counts as one grade.
    for partner in range(3, 3 + GRADES_PER_MINUTE):
        assert client.post("/find", json={**FIND, "partner": partner}, headers=HEADERS).status_code == 200
    response = client.post("/find", json={**FIND, "partner": 3 + GRADES_PER_MINUTE}, headers=HEADERS)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many grades this minute. Try again later."}
    assert 1 <= int(response.headers["Retry-After"]) <= 60


def test_a_find_and_an_analyze_count_against_the_same_grade_limit(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    client = _find_client(settings, sources, clock=MovingClock(NOW))
    client.app.state.analyzer = _uncached()
    _drop_store(client.app)
    for _ in range(GRADES_PER_MINUTE - 1):
        assert client.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
    assert client.post("/find", json=FIND, headers=HEADERS).status_code == 200
    assert client.post("/find", json={**FIND, "partner": 4}, headers=HEADERS).status_code == 429


def test_a_cached_find_repeat_does_not_count_and_makes_no_claude_call(settings, sources):
    from analyzer.tunables import GRADES_PER_MINUTE

    picker = StubPicker()
    client = _find_client(settings, sources, picker, MovingClock(NOW))
    first = client.post("/find", json=FIND, headers=HEADERS).json()
    for _ in range(GRADES_PER_MINUTE):
        assert client.post("/find", json=FIND, headers=HEADERS).json() == first
    assert len(picker.calls) == 1
    assert json.loads((settings.result_cache_dir / "cpc" / GRADE_COUNTS_FILE).read_text())["counts"] == {"testclient": 1}


def _with_as_of(snapshot, **update):
    return snapshot.model_copy(update={"as_of": snapshot.as_of.model_copy(update=update)})


def test_the_find_cache_key_is_the_ordered_pair_and_the_chart_week(settings, sources):
    snapshot = _here(sources, settings).snapshot(2026)
    key = finder_cache_key(2026, 2, 3, snapshot)
    # The rosters fetch time moves on every request, so it is not in the key.
    assert finder_cache_key(2026, 2, 3, _with_as_of(snapshot, rosters_fetched=FETCHED.replace(minute=55))) == key
    # The asker's side comes first, so the other order is another key.
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


def test_the_other_order_of_the_pair_misses_the_cache(settings, sources):
    picker = StubPicker()
    client = _find_client(settings, sources, picker)
    client.post("/find", json=FIND, headers=HEADERS)
    swapped = client.post("/find", json={**FIND, "asker": 3, "partner": 2}, headers=HEADERS).json()
    assert len(picker.calls) == 2
    assert [team["roster_id"] for team in swapped["trade_pair"].values()] == [3, 2]
    assert all(item["sides"][0]["roster_id"] == 3 for item in swapped["trades"])


def _offers_in(user: str) -> dict[str, list[str]]:
    """The fact ids of each offer of a pick message, by offer id."""
    offers, current = {}, None
    for line in user.splitlines():
        if line.startswith("Offer "):
            current = line.removeprefix("Offer ")
            offers[current] = []
        elif current is not None and line.startswith("- "):
            offers[current].append(line[2:].split(": ", 1)[0])
    return offers


def _bad_pick(change):
    """A builder whose first Bullet of the first pick breaks a guard with `change`."""
    def build(user):
        out = passing_pick(user)
        bullets = out["picks"][0]["bullets"]
        out["picks"][0]["bullets"] = [bullets[0] | change, *bullets[1:]]
        return out
    return build


# Plain Bullets on the week fact, each one a separate claim, so a pick of any count passes each other guard.
PLAIN_BULLETS = ["The trade lands in the middle of the season.", "The other manager gets help where he needs it.",
                 "Your bench gets deeper at the spot you need.", "Your lineup keeps its best players.",
                 "The other team gets a starter for the rest of the year."]


def _pick_of_bullets(count):
    """A builder whose first pick holds `count` plain Bullets, each on the week fact."""
    def build(user):
        out = passing_pick(user)
        out["picks"][0]["bullets"] = [{"text": text, "mark": "for", "fact_id": "trade.week"}
                                      for text in PLAIN_BULLETS[:count]]
        return out
    return build


def _news_pick(user):
    """A pick of the first offer with a NEWS fact, whose first Bullet cites that fact and names no report."""
    out = passing_pick(user)
    offer, fid = next((offer, fid) for offer, ids in _offers_in(user).items() for fid in ids if fid.startswith("NEWS."))
    bullets = out["picks"][0]["bullets"]
    out["picks"] = [{"offer_id": offer, "lean": "Lean yes", "headline": HEADLINE,
                     "bullets": [bullets[0] | {"fact_id": fid}, *bullets[1:]]}]
    return out


@pytest.mark.parametrize("builder, failure", [
    (_bad_pick({"fact_id": "NO.such"}), "fact ID NO.such is not on the sheet of offer"),
    (_bad_pick({"text": "The trade lands in week 9."}), "number 9 is not in the cited facts"),
    (_bad_pick({"text": "A rival gets help here."}), "the words 'rival' are not allowed"),
    (_bad_pick({"text": "Josh Jacobs would fit here."}), "the name Josh Jacobs is not in the trade"),
    (lambda user: {"picks": [passing_pick(user)["picks"][0] | {"bullets": passing_pick(user)["picks"][0]["bullets"][:1]}],
                   "none_line": None}, "it has 1 bullets; the range is 2 to 4"),
    (_pick_of_bullets(5), "it has 5 bullets; the range is 2 to 4"),
    (lambda user: passing_pick(user) | {"picks": [passing_pick(user)["picks"][0] | {"headline": "Send it for 12 points."}]},
     "pick 1 headline: number 12 is not in the cited facts"),
    # A pick that the Advisor would read as Lean no alone is no pick, so the analyzer and the Finder agree.
    (lambda user: passing_pick(user) | {"picks": [passing_pick(user)["picks"][0] | {"lean": "Lean no"}]},
     "pick 1: its Lean is Lean no; pick only an offer you would read as Send it, Lean yes, or Gut call"),
])
def test_a_pick_that_fails_a_guard_gets_one_repair_call_and_the_repaired_pick_stands(settings, sources, builder,
                                                                                     failure):
    picker, repair = StubPicker(builder), StubRepair()
    doc = _find_client(settings, sources, picker, repair=repair).post("/find", json={"season": 2026, "asker": 2},
                                                                      headers=HEADERS).json()
    assert len(picker.calls) == 1
    assert len(repair.calls) == 1
    assert failure in repair.calls[0][1]
    assert doc["fallback"] is False
    assert [item["headline"] for item in doc["trades"]] == [HEADLINE] * len(doc["trades"])


@pytest.mark.parametrize("builder, failure", [
    (lambda user: passing_pick(user) | {"picks": [passing_pick(user)["picks"][0] | {"offer_id": "1:2-3:4"}]},
     "offer 1:2-3:4 is not on the shortlist"),
    (lambda user: passing_pick(user) | {"picks": passing_pick(user)["picks"][:1] * 2}, "is picked twice"),
    (lambda user: passing_pick(user) | {"picks": passing_pick(user)["picks"][:1] * 4}, "the response has 4 picks"),
    (lambda user: {"picks": [], "none_line": None}, "a response with no pick needs a none_line"),
])
def test_a_failure_of_the_whole_response_retries_the_whole_call_once(settings, sources, builder, failure):
    picker, repair = StubPicker(builder, passing_pick), StubRepair()
    doc = _find_client(settings, sources, picker, repair=repair).post("/find", json={"season": 2026, "asker": 2},
                                                                      headers=HEADERS).json()
    assert len(picker.calls) == 2
    assert failure in picker.calls[1][1]
    assert repair.calls == []
    assert doc["fallback"] is False
    assert [item["headline"] for item in doc["trades"]] == [HEADLINE] * len(doc["trades"])


def test_one_bad_pick_of_three_gets_one_repair_call_and_the_document_holds_all_three(settings, sources):
    picker, repair = StubPicker(_bad_pick({"text": "The trade lands in week 9."})), StubRepair()
    doc = _find_client(settings, sources, picker, repair=repair).post("/find", json={"season": 2026, "asker": 2},
                                                                      headers=HEADERS).json()
    picked = re.findall(r"^Offer (\S+)$", picker.calls[0][1], re.MULTILINE)[:3]
    assert len(picked) == 3
    assert len(picker.calls) == 1
    # The repair asks for the bad pick only, so the two good picks cost no second call.
    assert [list(_offers_in(user)) for _, user in repair.calls] == [picked[:1]]
    assert [item["offer_id"] for item in doc["trades"]] == picked
    assert doc["fallback"] is False


def test_the_repair_call_sends_the_one_sheet_of_its_offer_only(settings, sources):
    picker, repair = StubPicker(_bad_pick({"fact_id": "NO.such"})), StubRepair()
    _find_client(settings, sources, picker, repair=repair).post("/find", json={"season": 2026, "asker": 2},
                                                                headers=HEADERS)
    pick_offers = _offers_in(picker.calls[0][1])
    [(system, user)] = repair.calls
    [(offer, fids)] = _offers_in(user).items()
    assert offer == next(iter(pick_offers))
    assert fids == pick_offers[offer]
    # The repair sheet gives each fact in full, as it reads alone.
    assert SAME_FACT not in user
    # The failed text and its failures go with it, so the Advisor fixes only what failed.
    assert "fact ID NO.such is not on the sheet of offer" in user
    assert "The trade lands in the middle of the season." in user
    assert "Aim for 3 Bullets, and never write more than 4." in " ".join(system.split())


def test_a_repaired_pick_that_fails_again_is_dropped_when_another_pick_stands(settings, sources, caplog):
    picker = StubPicker(_bad_pick({"text": "The trade lands in week 9."}))
    repair = StubRepair(lambda user: passing_repair(user) | {"headline": "Send it for 12 points."})
    doc = _find_client(settings, sources, picker, repair=repair).post("/find", json={"season": 2026, "asker": 2},
                                                                      headers=HEADERS).json()
    picked = re.findall(r"^Offer (\S+)$", picker.calls[0][1], re.MULTILINE)[:3]
    assert len(picker.calls) == 1 and len(repair.calls) == 1
    assert [item["offer_id"] for item in doc["trades"]] == picked[1:]
    assert doc["fallback"] is False
    assert "finder repair of pick 1 failed" in caplog.text


def _every_pick_bad(user):
    """A builder whose every pick holds a Bullet with a number that no fact holds."""
    out = passing_pick(user)
    for pick in out["picks"]:
        pick["bullets"] = [pick["bullets"][0] | {"text": "The trade lands in week 9."}, *pick["bullets"][1:]]
    return out


def test_when_every_pick_fails_twice_the_shortlist_fallback_holds(settings, sources):
    picker, repair = StubPicker(_every_pick_bad), StubRepair(_every_pick_bad)
    doc = _find_client(settings, sources, picker, repair=repair).post("/find", json={"season": 2026, "asker": 2},
                                                                      headers=HEADERS).json()
    assert len(picker.calls) == 1
    assert len(repair.calls) == len(re.findall(r"^Offer (\S+)$", picker.calls[0][1], re.MULTILINE)[:3])
    _assert_the_shortlist_fallback(doc, picker.calls[0][1])


class MeteredRepair(StubRepair):
    """The stub repair, after one Claude call of a ClaudeWriter over a stub client, so the press meter counts it."""

    def __call__(self, system, user, output_model):
        usage = type("Usage", (), {"input_tokens": 1000, "output_tokens": 100, "cache_read_input_tokens": 0,
                                   "cache_creation_input_tokens": 0})
        response = type("Response", (), {"stop_reason": "end_turn", "parsed_output": "parsed", "usage": usage})()
        messages = type("Messages", (), {"parse": lambda self, **kwargs: response})()
        ClaudeWriter(client=type("Client", (), {"messages": messages})()).parse("user", PickOut, "system",
                                                                                 model=FINDER_PICK_MODEL)
        return super().__call__(system, user, output_model)


def test_the_find_press_line_counts_the_repair_calls_in_its_cost(settings, sources, caplog):
    caplog.set_level("INFO", logger="analyzer.routes")
    picker = StubPicker(_every_pick_bad)
    client = _find_client(settings, sources, picker, repair=MeteredRepair())
    assert client.post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS).status_code == 200
    [line] = _press_lines(caplog, "find")
    # The repairs run in threads of the press. Each one is 1,000 input tokens at $2 per million and 100 output
    # tokens at $10 per million on Sonnet. The stub pick makes no metered call.
    count = len(re.findall(r"^Offer (\S+)$", picker.calls[0][1], re.MULTILINE)[:3])
    assert line.endswith(f"cost=${0.003 * count:.4f} claude_calls={count}")


def test_a_pick_with_4_bullets_passes_the_guard_with_one_call(settings, sources):
    picker = StubPicker(_pick_of_bullets(4))
    doc = _find_client(settings, sources, picker).post("/find", json={"season": 2026, "asker": 2},
                                                       headers=HEADERS).json()
    assert len(picker.calls) == 1
    assert doc["fallback"] is False
    assert len(doc["trades"][0]["bullets"]) == 4


def _taylor_first(key, question, state):
    """A Jev that rates Jonathan Taylor of roster 11 above every other target, so an offer holds him and his news."""
    return 0.99 if key == "11.6813" else 0.9


def test_a_pick_bullet_that_cites_news_and_names_no_report_gets_one_repair_call(settings, sources):
    picker, repair = StubPicker(_news_pick), StubRepair()
    doc = _find_client(settings, sources, picker, jev=FakeJev(answer=_taylor_first), repair=repair).post(
        "/find", json={"season": 2026, "asker": 4, "partner": 11}, headers=HEADERS).json()
    assert len(picker.calls) == 1
    [(_, user)] = repair.calls
    assert "it cites the news fact NEWS.6813." in user
    assert "so it must say 'reported', 'per', or the source" in user
    assert doc["fallback"] is False


def test_no_good_offer_gives_the_plain_line_of_the_advisor(settings, sources):
    line = "No offer on the list helps your lineup enough to send."
    picker = StubPicker(lambda user: {"picks": [], "none_line": line})
    doc = _find_client(settings, sources, picker).post("/find", json=FIND, headers=HEADERS).json()
    assert doc["trades"] == []
    assert doc["empty"] == line
    assert doc["fallback"] is False


def _assert_the_shortlist_fallback(doc, user):
    """The document of a fallback: every offer of the pick message, each with fact lines and no headline."""
    assert doc["fallback"] is True
    assert doc["empty"] is None
    assert [item["offer_id"] for item in doc["trades"]] == list(_offers_in(user))
    for item in doc["trades"]:
        assert item["headline"] is None
        assert item["bullets"] == []
        players = [player["name"] for side in item["sides"] for player in side["gives"]]
        # One plain line per traded player, from his fact on the sheet, in the order of the sides.
        assert len(item["fact_lines"]) == len(players)
        assert all(line.startswith(name) for line, name in zip(item["fact_lines"], players))


def test_two_failed_responses_give_the_shortlist_with_fact_lines_and_the_fallback_flag(settings, sources, caplog):
    picker = StubPicker(lambda user: passing_pick(user) | {"picks": passing_pick(user)["picks"][:1] * 2})
    client = _find_client(settings, sources, picker)
    doc = client.post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS).json()
    assert len(picker.calls) == 2
    assert "finder pick attempt 2 failed" in caplog.text
    _assert_the_shortlist_fallback(doc, picker.calls[0][1])
    # A fallback is not stored, so a repeat tries the Claude call again.
    client.post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS)
    assert len(picker.calls) == 4


def test_an_anthropic_key_that_is_not_valid_gives_the_shortlist_fallback(settings, sources):
    calls = []

    def refused(system, user, output_model):
        calls.append(user)
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        raise anthropic.AuthenticationError("invalid x-api-key", response=httpx.Response(401, request=request),
                                            body=None)

    response = _find_client(settings, sources, refused).post("/find", json={"season": 2026, "asker": 2},
                                                             headers=HEADERS)
    assert response.status_code == 200
    assert len(calls) == 2
    _assert_the_shortlist_fallback(response.json(), calls[0])


def test_the_pick_reads_news_only_of_the_shortlist_players_and_asks_jev_no_new_question(settings, sources):
    fetched, jev, picker = [], FakeJev(), StubPicker()

    def counted(pid):
        fetched.append(pid)
        return recorded_news(pid)

    news = NewsFeed(fetch=counted, now=lambda: NEWS_RECORDED)
    _find_client(settings, sources, picker, jev=jev, news=news).post("/find", json={"season": 2026, "asker": 2},
                                                                     headers=HEADERS)
    user = picker.calls[0][1]
    offers = _offers_in(user)
    players = {pid for offer in offers for side in offer.split("-") for pid in side.partition(":")[2].split("+")}
    assert set(fetched) == players
    # Each player is fetched once, though he is on more than one offer.
    assert len(fetched) == len(players)
    # The sheet holds the Jev answers of the shortlist, so no request asks the accept question of one trade.
    assert all(fids.count("JEV.fair") == 1 for fids in offers.values())
    assert not any(key.startswith("accept.") for request in jev.requests for key in request.questions)


def test_the_pick_message_gives_each_fact_text_once(settings, sources):
    picker = StubPicker()
    _find_client(settings, sources, picker).post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS)
    user = picker.calls[0][1]
    full = [line for line in user.splitlines() if line.startswith("- ") and not line.endswith(SAME_FACT)]
    assert len(full) == len(set(full))
    # A fact that an earlier offer gave in full keeps its id on the later offer, so a Bullet there may cite it.
    repeated = [line for line in user.splitlines() if line.endswith(SAME_FACT)]
    assert repeated
    assert all(f"- {line[2:].split(': ', 1)[0]}: " in user.split(line)[0] for line in repeated)


def test_the_pick_prompt_holds_the_playbook_and_the_pick_rules(settings, sources):
    picker = StubPicker()
    _find_client(settings, sources, picker).post("/find", json=FIND, headers=HEADERS)
    system = " ".join(picker.calls[0][0].split())
    for line in ("picks: up to 3 offers that you would send, best first, each once.",
                 "bullets: 2 to 4 Bullets, one claim each, in plain words.",
                 "Say why the asker sends it and why the other manager says yes.",
                 "Never name the commissioner, and never give a letter grade.",
                 " ".join(CLIENT.voice_dir.joinpath("playbook.md").read_text(encoding="utf-8").split())[:80]):
        assert line in system


def test_a_good_find_returns_the_document_in_the_fixture_shape(settings, sources):
    doc = _find_client(settings, sources).post("/find", json={"season": 2026, "asker": 2}, headers=HEADERS).json()
    fixture = json.loads(FIND_FIXTURE.read_text(encoding="utf-8"))
    assert len(fixture["trades"]) == 3
    assert _same_shape(doc, _shape(fixture))
    # Every trade has the shape of the fixture's first, so no item drops a key.
    for item in doc["trades"]:
        assert _shape(item) == _shape(fixture["trades"][0])
    # The sides and the Bullets of a pick have the shape of the analyze document, so the site renders them once.
    analyze_fixture = json.loads(RESPONSE_FIXTURE.read_text(encoding="utf-8"))
    assert _shape(fixture["trades"][0]["sides"]) == _shape(analyze_fixture["trade"]["sides"])
    assert _shape(fixture["trades"][0]["bullets"]) == _shape(analyze_fixture["sides"][0]["bullets"])
    assert doc["season"] == fixture["season"] == FIND["season"]


def test_the_find_fixture_names_no_letter_and_no_number_outside_ids():
    fixture = json.loads(FIND_FIXTURE.read_text(encoding="utf-8"))
    found = [text for text in _strings(fixture)
             if re.search(r"\b[A-F][+-]?(?![\w'])", text) or re.search(r"\bletters?\b", text, re.IGNORECASE)]
    assert found == []
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


def test_the_document_version_is_22():
    import analyzer.cache as cache_module

    # The position rank enters the facts, so a document stored before it must never serve.
    # The as-of block says when the week has no chart, so a document stored before that must never serve.
    # A bye is no longer a hole, so a grade stored under the old hole rule must never serve.
    # A grade of three or four sides and the zero rule for a player out for the season change the shape and the rules.
    # The bullets and the deal row take the place of the analysis and the chart block, so the shape changes.
    # Each traded player carries his Season rank and his Recent rank, so the shape changes.
    # A silent row hides, and the roster and standing rows read in plain words, so a stored row must never serve.
    # The usage, injury, upside, handcuff, and schedule rows and the fairness reasons read in plain words too.
    # Each side carries its Week lines, so the shape changes.
    # A Week line names each player who steps up, so a stored Week line must never serve.
    # The injury and handcuff rows name no id map, so a stored row must never serve.
    # The read of the Advisor takes the place of the decision and the factor rows, so no old result serves.
    # The Finder pick takes the place of the fairness and the reason of each finder trade, so no old list serves.
    # A fact text names a race group, not an old race word, so no stored fact text of the old words serves.
    # A player who cannot play now fills no slot of the Finder lineup, so no list stored under the old fill serves.
    assert cache_module.DOCUMENT_VERSION == 22


# The API over more than one client: the routes at /clients/<slug>/, the old paths as cpc, the grade limit per
# client, the points key of each client in the cache key, and the start over each folder under clients/.

# The second client of these tests. Its folder lives only in the temp folder of a test, never under clients/.
SECOND = "norcal"
# The second client has its own passphrase, so the passphrase of cpc opens none of its routes.
SECOND_HEADERS = {"X-League-Passphrase": "norcal-test"}


def _two_clients(settings, sources, analyzer=None):
    """An app that serves cpc and a second client on the same fixture league, each with its own sources."""
    cpc = _here(sources, settings)
    # The second client takes no eggs, as norcal takes none, so it needs no commissioner key.
    values = cpc.client.values.model_copy(
        update={"packages": [name for name in cpc.client.values.packages if name != "eggs"]})
    second = dataclasses.replace(cpc, client=cpc.client.model_copy(update={"slug": SECOND, "values": values}))
    settings = dataclasses.replace(settings, passphrases={"cpc": PASSPHRASE, SECOND: SECOND_HEADERS["X-League-Passphrase"]})
    app = create_app(settings, [cpc.client, second.client], sources={"cpc": cpc, SECOND: second}, analyzer=analyzer)
    if analyzer is not None and not getattr(analyzer, "store", True):
        _drop_store(app)
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
    # The app keeps no result, so each repeat is a new grade.
    client = _two_clients(settings, sources, _uncached())
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

