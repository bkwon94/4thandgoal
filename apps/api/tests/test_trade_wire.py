"""
Tests for the Trade Wire route at the route seam: the FastAPI test client over the recorded Sleeper answer of the
transactions of leg 9 of cpc, with the live week 10 rosters of cpc for the names. The recorded answer is a fixed input.
"""
import dataclasses
import json
from datetime import datetime
from functools import partial
from pathlib import Path

import httpx
import test_api
import test_start_sit
from fakes import FakeJev
from fastapi.testclient import TestClient
from test_api import HEADERS, _here

from cornerstone_api.app import create_app
from league.provider.raw import RawTransaction
from league.provider.sleeper import fetch_current_transactions

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

TRADE_WIRE = "/clients/{slug}/deadline/trades"
RECORDED = Path(__file__).parent / "fixtures" / "trade-wire" / "cpc-week-9-transactions.json"
# The trade in which roster 4 sends $5 of FAAB to roster 8, and the roster ids of the other trade of leg 9.
TRADE_W = "1424578776058155008"
OTHER_TRADE = "1425209111854747648"


class Wire:
    """The Sleeper read of the transactions of the current leg: the answer it gives, and the count of its reads."""

    def __init__(self, leg: int = 9, answer: list[dict] | None = None):
        self.leg = leg
        self.answer = answer if answer is not None else json.loads(RECORDED.read_text())
        self.reads = 0
        self.until: datetime | None = None

    def __call__(self, league_id: str, *, until: datetime | None = None):
        self.reads += 1
        self.until = until
        return self.leg, [RawTransaction.model_validate(each) for each in self.answer]


def _api(settings, sources, wire) -> TestClient:
    """An app over cpc on its recorded week 10, with `wire` as the Sleeper read of the transactions."""
    cpc = dataclasses.replace(test_start_sit._sources(_here(sources, settings), "cpc", test_start_sit.BEFORE_KICKOFF),
                              fetch_transactions=wire)
    return TestClient(create_app(settings, [cpc.client], sources={"cpc": cpc}, jev=FakeJev()))


def _trades(api, headers=HEADERS) -> list[dict]:
    response = api.get(TRADE_WIRE.format(slug="cpc"), headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["trades"]


def _trade(trades: list[dict], transaction_id: str) -> dict:
    [trade] = [each for each in trades if each["transaction_id"] == transaction_id]
    return trade


def test_trade_w_shows_both_teams_with_their_players_their_positions_and_the_faab(settings, sources):
    # AT-13: the teams with name and avatar, the players each team gets with positions, $5 of FAAB to roster 8.
    trade = _trade(_trades(_api(settings, sources, Wire())), TRADE_W)
    four, eight = sorted(trade["teams"], key=lambda team: team["roster_id"])
    assert (four["roster_id"], eight["roster_id"]) == (4, 8)
    assert four["team"] and eight["team"] and "avatar" in four and "avatar" in eight
    assert [(p["name"], p["position"]) for p in four["players"]] == [
        ("Tetairoa McMillan", "WR"), ("Makai Lemon", "WR"), ("Seth McGowan", "RB"), ("Chase Brown", "RB")]
    assert [(p["name"], p["position"]) for p in eight["players"]] == [
        ("Rome Odunze", "WR"), ("CeeDee Lamb", "WR"), ("Jordan Mason", "RB")]
    assert (four["faab"], eight["faab"]) == (0, 5)
    assert "draft_picks" not in trade and all("picks" not in team for team in trade["teams"])


def _answer_with_odd_trades() -> list[dict]:
    """The recorded answer with a pending trade, a vetoed trade, and a trade of another leg added, each a copy of
    trade W that differs in one field, so the list must drop them."""
    answer = json.loads(RECORDED.read_text())
    [w] = [each for each in answer if each["transaction_id"] == TRADE_W]
    return answer + [
        {**w, "transaction_id": "pending", "status": "pending"},
        {**w, "transaction_id": "vetoed", "status": "failed"},
        {**w, "transaction_id": "last-leg", "leg": 8},
    ]


def test_the_list_has_only_the_complete_trades_of_the_leg_newest_first(settings, sources):
    # AT-14: no waiver, no pending or vetoed trade, no trade of another leg, in descending order of the accept time.
    trades = _trades(_api(settings, sources, Wire(answer=_answer_with_odd_trades())))
    assert [trade["transaction_id"] for trade in trades] == [OTHER_TRADE, TRADE_W]
    times = [trade["accepted_at"] for trade in trades]
    assert times == sorted(times, reverse=True)


def test_the_list_sorts_by_the_accept_time_and_not_by_the_proposal_time(settings, sources):
    # Trade W was proposed before the other trade and accepted after it, so the sort by the accept time puts it first.
    answer = json.loads(RECORDED.read_text())
    for each in answer:
        if each["transaction_id"] == TRADE_W:
            each["status_updated"] = 1794200000000
    trades = _trades(_api(settings, sources, Wire(answer=answer)))
    assert [trade["transaction_id"] for trade in trades] == [TRADE_W, OTHER_TRADE]


def test_two_calls_within_5_s_make_one_sleeper_read_and_a_call_after_5_s_makes_a_second(settings, sources):
    # AT-15: the cache window is 5 s.
    wire, now = Wire(), [1000.0]
    api = _api(settings, sources, wire)
    api.app.state.trade_wires["cpc"].clock = lambda: now[0]
    _trades(api)
    now[0] += 2
    _trades(api)
    assert wire.reads == 1
    now[0] += 4
    _trades(api)
    assert wire.reads == 2


def test_a_call_with_no_passphrase_answers_401_and_40_calls_from_one_address_all_answer_200(settings, sources):
    # AT-16 and AT-17: the route checks the passphrase and counts none of the 30 requests per minute of the address.
    api = _api(settings, sources, Wire())
    refused = api.get(TRADE_WIRE.format(slug="cpc"))
    assert refused.status_code == 401 and refused.content == b""
    assert [api.get(TRADE_WIRE.format(slug="cpc"), headers=HEADERS).status_code for _ in range(40)] == [200] * 40


def test_the_route_reads_the_leg_of_the_week_of_the_lock_after_sleeper_moves_to_leg_12(settings, sources):
    # The Lock of cpc is in week 11. Sleeper is in leg 12, one day after the Lock, so the route reads leg 11.
    paths: list[str] = []
    week_11 = [{**each, "leg": 11} for each in json.loads(RECORDED.read_text())]

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path.endswith("/state/nfl"):
            return httpx.Response(200, json={"leg": 12, "season_start_date": "2026-09-10"})
        return httpx.Response(200, json=week_11 if request.url.path.endswith("/transactions/11") else [])

    api = _api(settings, sources, partial(fetch_current_transactions, transport=httpx.MockTransport(handler)))
    response = api.get(TRADE_WIRE.format(slug="cpc"), headers=HEADERS)
    assert response.status_code == 200, response.text
    assert response.json()["leg"] == 11 and paths[1].endswith("/transactions/11")
    assert {trade["transaction_id"] for trade in response.json()["trades"]} == {TRADE_W, OTHER_TRADE}


def test_the_route_gives_the_lock_of_the_client_config_to_the_sleeper_read(settings, sources):
    wire = Wire()
    _trades(_api(settings, sources, wire))
    assert wire.until == datetime.fromisoformat("2026-11-24T00:00:00-05:00")
