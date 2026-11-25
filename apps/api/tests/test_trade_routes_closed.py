"""
Tests for the closed reply of the trade routes: after the Lock each route answers 410 and costs nothing, the fair
warm-up skips the client, and the Suggestions hold no trade fact. NorCal answers until its own Lock.
"""
import dataclasses
import functools
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import test_api
from fakes import NEWS_RECORDED, FakeJev, recorded_news
from fastapi.testclient import TestClient
from test_api import CLIENT, HEADERS, TRADE, StubAdvisor, StubPicker, StubRepair, _here
from test_personal_topics import Writer
from test_suggestions import WEDNESDAY, _publish_topics, _suggest
from test_suggestions import _api as suggestions_api
from test_trade_topics import LIL_FRIDGE, SURE_TRADE, _answer, _choose, _parts

from analyzer.advisor import read_trade
from analyzer.finder_pick import pick_trades
from analyzer.finder_search import search
from analyzer.trade_news import NewsFeed
from cornerstone_api import trades_closed
from cornerstone_api.app import create_app
from cornerstone_api.fair_warm import FairWarmer
from cornerstone_api.trades_closed import CLOSED_BODY
from cornerstone_api.value_models import VALUE_MODELS
from league.client import read_client_values

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

EASTERN = ZoneInfo("America/New_York")
AFTER_CPC_LOCK = datetime(2026, 11, 24, 12, 0, tzinfo=EASTERN)
CLIENTS = Path(__file__).resolve().parents[3] / "clients"
FIND = {"season": 2026, "asker": 4, "partner": 5}
ROSTER = {"roster_id": LIL_FRIDGE}
# Each trade route with its method and a valid body, as AT-14 lists them.
ROUTES = [
    ("POST", "analyze", TRADE),
    ("POST", "find", FIND),
    ("POST", "trade-check", {"question": SURE_TRADE, **ROSTER}),
    ("POST", "trade-ideas", ROSTER),
    ("POST", "find-stream", FIND),
    ("POST", "sell-high", ROSTER),
    ("GET", "deadline/trades", None),
]
SECOND_HEADERS = {"X-League-Passphrase": "norcal-test"}


@pytest.fixture
def jev():
    return FakeJev(answer=_answer, choose=_choose)


def _set_clock(monkeypatch, now: datetime) -> None:
    monkeypatch.setattr(trades_closed, "wall_clock", lambda: now)


class Counts:
    """The Claude calls of the three trade presses, counted from the stub calls."""

    def __init__(self):
        self.advisor, self.picker, self.repair = StubAdvisor(), StubPicker(), StubRepair()
        self.sells = 0

    def sell_high(self, *args, **kwargs):
        self.sells += 1
        raise AssertionError("A closed client never asks for a sell pick.")

    def claude(self) -> int:
        return len(self.advisor.calls) + len(self.picker.calls) + len(self.repair.calls) + self.sells


def _api(settings, sources, jev, counts: Counts, slug: str = "cpc") -> TestClient:
    news = NewsFeed(fetch=recorded_news, now=lambda: NEWS_RECORDED)
    cpc = _here(sources, settings)
    client = CLIENT
    if slug != "cpc":
        # NorCal reads its real client.toml, so it has its real Lock, on the fixture league of cpc.
        client = cpc.client.model_copy(update={"slug": slug, "values": read_client_values(CLIENTS / slug, VALUE_MODELS)})
        cpc = dataclasses.replace(cpc, client=client)
        settings = dataclasses.replace(settings, passphrases={slug: SECOND_HEADERS["X-League-Passphrase"]})
    app = create_app(
        settings, [client], sources={slug: cpc}, jev=jev,
        analyzer=functools.partial(read_trade, jev=jev, news=news, call=counts.advisor),
        finder_search=functools.partial(search, jev=jev),
        finder_pick=functools.partial(pick_trades, news=news, jev=jev, call=counts.picker, repair_call=counts.repair),
        sell_high=counts.sell_high)
    return TestClient(app)


def _call(api: TestClient, route: str, method: str, body, slug: str = "cpc", headers=HEADERS):
    return api.request(method, f"/clients/{slug}/{route}", json=body, headers=headers)


@pytest.mark.parametrize(("method", "route", "body"), ROUTES)
def test_each_trade_route_of_cpc_answers_410_with_the_closed_body_after_its_lock(settings, sources, jev, monkeypatch,
                                                                                method, route, body):
    # AT-14.
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    response = _call(_api(settings, sources, jev, Counts()), route, method, body)
    assert response.status_code == 410
    assert response.json() == {"closed": True, "line": "The trade deadline has passed. Trades open again next season."}
    assert response.json() == CLOSED_BODY


def test_the_closed_reply_still_needs_the_passphrase(settings, sources, jev, monkeypatch):
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    api = _api(settings, sources, jev, Counts())
    assert api.post("/clients/cpc/analyze", json=TRADE).status_code == 401


def test_the_teams_route_stays_open_after_the_lock(settings, sources, jev, monkeypatch):
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    response = _api(settings, sources, jev, Counts()).get("/clients/cpc/teams", params={"season": 2026},
                                                          headers=HEADERS)
    assert response.status_code == 200


def test_a_refused_call_makes_no_jev_call_and_no_claude_call(settings, sources, jev, monkeypatch):
    # AT-16.
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    counts = Counts()
    api = _api(settings, sources, jev, counts)
    for method, route, body in ROUTES:
        assert _call(api, route, method, body).status_code == 410
    assert jev.requests == []
    assert counts.claude() == 0


def test_the_old_path_with_no_client_answers_closed_as_cpc(settings, sources, jev, monkeypatch):
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    api = _api(settings, sources, jev, Counts())
    assert api.post("/analyze", json=TRADE, headers=HEADERS).status_code == 410
    assert api.post("/find", json=FIND, headers=HEADERS).status_code == 410


def test_the_fair_warm_up_never_warms_a_closed_client(settings, sources, monkeypatch, caplog):
    # AT-17.
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    jev = FakeJev()
    cpc = test_api.with_week_9_chart(_here(sources, settings))
    app = create_app(settings, [cpc.client], sources={"cpc": cpc}, jev=jev)
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    with caplog.at_level(logging.INFO, logger="cornerstone_api.fair_warm"):
        warmer.warm(app.state.served["cpc"])
    assert [r for r in caplog.records if r.name == "cornerstone_api.fair_warm"] == []
    assert jev.requests == [] and len(app.state.fair_cache) == 0


def test_a_press_or_the_trade_wire_never_wakes_the_warm_up_of_a_closed_client(settings, sources, monkeypatch):
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    jev = FakeJev()
    cpc = test_api.with_week_9_chart(_here(sources, settings))
    app = create_app(settings, [cpc.client], sources={"cpc": cpc}, jev=jev)
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    warmer.check(cpc.snapshot(cpc.client.values.latest_season))
    warmer.trades_seen("cpc", ["1"])
    assert not warmer.wake.is_set()


def test_the_suggestions_of_a_closed_client_hold_no_trade_fact_and_ask_no_sell_read(settings, sources, monkeypatch):
    # AT-18.
    _publish_topics(settings)
    _set_clock(monkeypatch, AFTER_CPC_LOCK)
    jev = FakeJev()
    api = suggestions_api(settings, sources, jev, Writer())
    body = _suggest(api, WEDNESDAY).json()
    assert not {"trade_ideas", "sell_high", "trade_check"} & set(body["picks"])
    assert not {"trade_ideas", "sell_high"} & set(body["facts"])
    assert not {"trade_ideas", "sell_high"} & set(body["lifts"])
    assert not [r for r in jev.requests if any(key.startswith("sell") for key in r.questions)]


def test_the_norcal_trade_check_still_grades_the_day_before_its_lock(settings, sources, jev, monkeypatch):
    # AT-21.
    _set_clock(monkeypatch, datetime(2026, 12, 14, 12, 0, tzinfo=EASTERN))
    api = _api(settings, sources, jev, Counts(), "norcal")
    response = _call(api, "trade-check", "POST", {"question": SURE_TRADE, **ROSTER}, "norcal", SECOND_HEADERS)
    assert response.status_code == 200
    answers = [part for part in _parts(response) if part["type"] == "data-answer"]
    assert answers and answers[0]["data"]["kind"] == "check"


def test_the_norcal_trade_check_is_410_one_second_after_its_lock(settings, sources, jev, monkeypatch):
    # AT-22.
    _set_clock(monkeypatch, datetime(2026, 12, 15, 0, 0, 1, tzinfo=EASTERN))
    api = _api(settings, sources, jev, Counts(), "norcal")
    response = _call(api, "trade-check", "POST", {"question": SURE_TRADE, **ROSTER}, "norcal", SECOND_HEADERS)
    assert response.status_code == 410
    assert response.json() == CLOSED_BODY
