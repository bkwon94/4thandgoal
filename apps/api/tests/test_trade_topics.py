"""
Tests for the trade Topics of the front door, the trade check and trade ideas, at the route seam with FakeJev.
The Advisor runs for real with the stub Claude calls of test_api, so the sheet, the guards, and the stages run.
"""
import dataclasses
import functools
import json
import shutil

import pytest
import test_api
from fakes import NEWS_RECORDED, FakeJev, recorded_news
from fastapi.testclient import TestClient
from test_api import CLIENT, HEADERS, StubAdvisor, StubPicker, StubRepair, _cpc, _here

from analyzer.advisor import AdvisorOut, read_trade
from analyzer.finder_pick import pick_trades
from analyzer.finder_search import search
from analyzer.trade_news import NewsFeed
from analyzer.values import AnalyzerValues
from cornerstone_api.app import create_app
from cornerstone_api.caps import TEAM_LINE
from cornerstone_api.trade_wording import GETS_NAMED, GETS_PLAYER, GIVES_NAMED, GIVES_PLAYER
from facts.writer import ClaudeWriter
from league.jev_port import ChoiceQuestion, JevError, NoulQuestion
from league.provider.sleeper import load_raw

# The fixtures of the analyzer tests: the repo with the week 6 history, its settings, and the recorded sources.
repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

CHECK = "/clients/cpc/trade-check"
IDEAS = "/clients/cpc/trade-ideas"
LIL_FRIDGE = 3
BO_GIRDS = 6
SURE_TRADE = "is Khalil Shakir for Zay Flowers fair"
VAGUE_TRADE = "is my RB for their WR fair"
HALF_TRADE = "is Khalil Shakir for their WR fair"
# The words that site copy never holds (decision 08 and the copy rules of the spec).
INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")

# The Jev answers of each trade question: the two Nouls, and the player that each Choice puts its weight on.
PICKS = {
    SURE_TRADE: {GIVES_NAMED: 0.97, GETS_NAMED: 0.96, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
    VAGUE_TRADE: {GIVES_NAMED: 0.08, GETS_NAMED: 0.06, GIVES_PLAYER: "Derrick Henry", GETS_PLAYER: "Zay Flowers"},
    HALF_TRADE: {GIVES_NAMED: 0.95, GETS_NAMED: 0.12, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
}


def _answer(key: str, question: NoulQuestion, state: dict) -> float:
    """The Noul answers of a pick request by its question, and a yes for each Noul of the Advisor and the Finder."""
    picks = PICKS.get(state.get("manager_question", ""))
    return picks[key] if picks is not None and key in picks else 0.9


def _choose(key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
    """Each Choice of a pick request puts its weight on the player of PICKS, by the name in its option text."""
    name = PICKS[state["manager_question"]][key]
    return {option: (0.95 if text.startswith(name + " ") else 0.0) for option, text in question.options.items()}


@pytest.fixture
def jev():
    return FakeJev(answer=_answer, choose=_choose)


@pytest.fixture
def advisor():
    return StubAdvisor()


def _api(settings, sources, jev, advisor) -> TestClient:
    news = NewsFeed(fetch=recorded_news, now=lambda: NEWS_RECORDED)
    app = create_app(
        settings, [CLIENT], sources=_cpc(_here(sources, settings)), jev=jev,
        analyzer=functools.partial(read_trade, jev=jev, news=news, call=advisor),
        finder_search=functools.partial(search, jev=jev),
        finder_pick=functools.partial(pick_trades, news=news, jev=jev, call=StubPicker(), repair_call=StubRepair()))
    return TestClient(app)


@pytest.fixture
def api(settings, sources, jev, advisor):
    return _api(settings, sources, jev, advisor)


def _parts(response) -> list[dict]:
    """The parts of a stream, in order: each `data:` line of the event stream, with the end mark left out."""
    lines = [line.removeprefix("data: ") for line in response.text.split("\n\n") if line.startswith("data: ")]
    return [json.loads(line) for line in lines if line != "[DONE]"]


def _check(api, question: str):
    return api.post(CHECK, json={"question": question, "roster_id": LIL_FRIDGE}, headers=HEADERS)


def _of(parts: list[dict], kind: str) -> list[dict]:
    return [part["data"] for part in parts if part["type"] == kind]


def test_a_typed_trade_of_two_sure_players_gives_the_lean_the_case_and_the_bullets(api, advisor):
    # AT-24.
    response = _check(api, SURE_TRADE)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    [answer] = _of(_parts(response), "data-answer")
    assert answer["kind"] == "check"
    document = answer["document"]
    assert document["lean"] == "Lean yes" and document["case"].startswith("If you believe")
    assert [side["roster_id"] for side in document["sides"]] == [LIL_FRIDGE, BO_GIRDS]
    assert all(len(side["bullets"]) >= 3 for side in document["sides"])
    assert document["fairness"]["state"] == "fair"
    # The one Advisor call reads the trade of the two picks.
    [(_, user)] = advisor.calls
    assert "Khalil Shakir to Bo Girds" in user and "Zay Flowers from Bo Girds" in user


def test_the_stream_holds_each_player_pick_with_its_jev_answers(api):
    # AT-24 evidence: the route response with each player pick.
    [picks] = _of(_parts(_check(api, SURE_TRADE)), "data-picks")
    assert picks["gives"] == {"named": 0.97, "player_id": "8134", "name": "Khalil Shakir", "probability": 0.95,
                              "sure": True, "roster_id": LIL_FRIDGE}
    assert picks["gets"]["player_id"] == "9997" and picks["gets"]["roster_id"] == BO_GIRDS and picks["gets"]["sure"]


def test_one_jev_request_picks_each_side_from_the_real_rosters(api, jev):
    _check(api, VAGUE_TRADE)
    [request] = [r for r in jev.requests if "manager_question" in r.state]
    assert set(request.questions) == {GIVES_NAMED, GIVES_PLAYER, GETS_NAMED, GETS_PLAYER}
    gives = request.questions[GIVES_PLAYER].options.values()
    gets = request.questions[GETS_PLAYER].options.values()
    # Your team gives from its own roster, and gets from each roster of the 11 other teams.
    assert any(text.startswith("Khalil Shakir (WR") for text in gives)
    assert not any(text.startswith("Zay Flowers ") for text in gives)
    assert any(text.startswith("Zay Flowers (WR") and text.endswith("on Bo Girds") for text in gets)
    assert not any(text.startswith("Khalil Shakir ") for text in gets)
    assert request.state["your_team"]["name"] == "Lil Fridge"
    assert len(request.state["other_teams"]) == 11


def test_a_trade_with_no_named_player_opens_the_trade_page_and_fills_no_player(api, advisor):
    # AT-58.
    parts = _parts(_check(api, VAGUE_TRADE))
    [answer] = _of(parts, "data-answer")
    assert answer == {"kind": "form", "form": {"asker": LIL_FRIDGE, "partner": None, "gives": [], "gets": []}}
    [picks] = _of(parts, "data-picks")
    assert not picks["gives"]["sure"] and not picks["gets"]["sure"]
    assert advisor.calls == []


def test_an_unsure_pick_on_one_side_fills_only_the_sure_player(api, advisor):
    [answer] = _of(_parts(_check(api, HALF_TRADE)), "data-answer")
    assert answer == {"kind": "form", "form": {"asker": LIL_FRIDGE, "partner": None, "gives": ["8134"], "gets": []}}
    assert advisor.calls == []


def test_the_steps_of_a_trade_check_come_one_by_one_before_the_whole_answer(api):
    # AT-28 at the route seam: each stage is a part of its own, and the Answer is the last data part.
    parts = _parts(_check(api, SURE_TRADE))
    kinds = [part["type"] for part in parts]
    assert kinds[0] == "start" and kinds[-1] == "finish"
    steps = _of(parts, "data-step")
    assert len(steps) >= 3
    assert kinds.index("data-answer") > max(i for i, kind in enumerate(kinds) if kind == "data-step")
    assert "Checked the players on each side" in [step["line"] for step in steps]


def test_no_step_line_names_an_inner_tool(api):
    lines = [step["line"] for step in _of(_parts(_check(api, SURE_TRADE)), "data-step")]
    lines += [step["line"] for step in _of(_parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE}, headers=HEADERS)),
                                           "data-step")]
    assert lines
    assert not [line for line in lines if any(word in line.lower() for word in INNER_NAMES)]


def test_a_repeat_of_a_trade_check_comes_from_the_cache_with_no_claude_call(api, advisor):
    first = _of(_parts(_check(api, SURE_TRADE)), "data-answer")
    second = _of(_parts(_check(api, SURE_TRADE)), "data-answer")
    assert first == second
    assert len(advisor.calls) == 1


def test_a_failed_jev_pick_is_an_error_and_never_a_form(settings, sources, advisor):
    failing = FakeJev(error=JevError("timeout"))
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), jev=failing,
                     analyzer=functools.partial(read_trade, jev=failing, news=NewsFeed(fetch=recorded_news,
                                                                                       now=lambda: NEWS_RECORDED),
                                                call=advisor))
    parts = _parts(_check(TestClient(app), SURE_TRADE))
    assert _of(parts, "data-answer") == []
    [error] = _of(parts, "data-error")
    assert error["status"] == 503
    assert advisor.calls == []


def test_a_trade_check_needs_the_passphrase(api):
    response = api.post(CHECK, json={"question": SURE_TRADE, "roster_id": LIL_FRIDGE})
    assert response.status_code == 401


def test_a_team_that_is_not_in_the_league_is_422(api):
    response = api.post(CHECK, json={"question": SURE_TRADE, "roster_id": 99}, headers=HEADERS)
    assert response.status_code == 422


def test_trade_ideas_run_in_a_client_with_the_finder_off_and_give_the_find_document(api):
    # AT-26: CPC has finder = false, and the trade ideas Topic calls the Finder anyway.
    assert CLIENT.values.package(AnalyzerValues).finder is False
    parts = _parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE}, headers=HEADERS))
    [answer] = _of(parts, "data-answer")
    assert answer["kind"] == "ideas"
    document = answer["document"]
    assert document["trade_pair"]["asker"]["roster_id"] == LIL_FRIDGE
    assert 1 <= len(document["trades"]) <= 3
    assert all(trade["sides"][0]["roster_id"] == LIL_FRIDGE for trade in document["trades"])


def test_the_steps_of_trade_ideas_count_the_offers_before_the_whole_answer(api):
    # AT-28: plain steps such as "Weighed 6 offers" show before the Answer.
    parts = _parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE}, headers=HEADERS))
    lines = [step["line"] for step in _of(parts, "data-step")]
    assert any(line.startswith("Checked 11 teams") for line in lines)
    assert any(line.startswith("Weighed ") and line.endswith(" offers") for line in lines)
    kinds = [part["type"] for part in parts]
    assert kinds.index("data-answer") > max(i for i, kind in enumerate(kinds) if kind == "data-step")


def test_trade_ideas_with_a_named_partner_keep_each_offer_to_that_partner(api):
    parts = _parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE, "partner": BO_GIRDS}, headers=HEADERS))
    [answer] = _of(parts, "data-answer")
    assert answer["document"]["trade_pair"]["partner"]["roster_id"] == BO_GIRDS
    assert all(trade["sides"][1]["roster_id"] == BO_GIRDS for trade in answer["document"]["trades"])


class MeteredAdvisor(StubAdvisor):
    """The stub Advisor, after one Claude call of a ClaudeWriter over a stub client, so the press meter counts it:
    1,000 input tokens at $4 per million and 100 output tokens at $20 per million on Opus, $0.0060 a call."""

    def __call__(self, system, user, output_model):
        usage = type("Usage", (), {"input_tokens": 1000, "output_tokens": 100, "cache_read_input_tokens": 0,
                                   "cache_creation_input_tokens": 0})
        response = type("Response", (), {"stop_reason": "end_turn", "parsed_output": "parsed", "usage": usage})()
        messages = type("Messages", (), {"parse": lambda self, **kwargs: response})()
        ClaudeWriter(client=type("Client", (), {"messages": messages})()).parse("user", AdvisorOut, "system")
        return super().__call__(system, user, output_model)


def _caps(api):
    asker = api.app.state.askers["cpc"]
    return asker.caps, asker.clock()


def test_a_trade_check_records_its_claude_cost_and_counts_as_one_answer(settings, sources, jev):
    advisor = MeteredAdvisor()
    news = NewsFeed(fetch=recorded_news, now=lambda: NEWS_RECORDED)
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), jev=jev,
                     analyzer=functools.partial(read_trade, jev=jev, news=news, call=advisor))
    api = TestClient(app)
    caps, now = _caps(api)
    assert _of(_parts(_check(api, SURE_TRADE)), "data-answer")
    assert caps.answers_today(LIL_FRIDGE, now) == 1
    assert caps.month_usd(now) == pytest.approx(0.0060 * len(advisor.calls))
    # A cached repeat is a kept Answer: no Claude call, no cost, and no count.
    assert _of(_parts(_check(api, SURE_TRADE)), "data-answer")
    assert caps.answers_today(LIL_FRIDGE, now) == 1


def test_a_trade_form_counts_toward_no_cap(api):
    caps, now = _caps(api)
    _parts(_check(api, VAGUE_TRADE))
    assert caps.answers_today(LIL_FRIDGE, now) == 0


def test_past_the_team_cap_a_sure_trade_check_gives_the_cap_line_and_no_claude_call(api, advisor):
    caps, now = _caps(api)
    for _ in range(25):
        caps.record(LIL_FRIDGE, 0.01, now, counts=True)
    parts = _parts(_check(api, SURE_TRADE))
    assert _of(parts, "data-cap") == [{"cap": "team", "line": TEAM_LINE}]
    assert _of(parts, "data-answer") == []
    assert advisor.calls == []
    # The form of an unsure pick costs nothing, so it still opens past the cap.
    [answer] = _of(_parts(_check(api, VAGUE_TRADE)), "data-answer")
    assert answer["kind"] == "form"


def test_past_the_league_cap_trade_ideas_give_the_league_line_and_no_claude_call(api, advisor):
    caps, now = _caps(api)
    caps.record(None, 25.00, now, counts=False)
    parts = _parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE}, headers=HEADERS))
    [cap] = _of(parts, "data-cap")
    assert cap["cap"] == "league" and cap["line"].startswith("The league's question budget is used up")
    assert _of(parts, "data-answer") == []


CURRENT = "/clients/cpc/personal/current"


def dropped(sources, fixture_raw_dir, tmp_path, roster_id: int):
    """The sources after the roster of `roster_id` drops its last player, as a waiver drop does. No other roster
    changes."""
    raw = tmp_path / f"raw-after-a-drop-{roster_id}"
    shutil.copytree(fixture_raw_dir, raw)
    rosters = json.loads((raw / "rosters.json").read_text())
    roster = next(each for each in rosters if each["roster_id"] == roster_id)
    roster["players"] = roster["players"][:-1]
    (raw / "rosters.json").write_text(json.dumps(rosters))
    return dataclasses.replace(sources, fetch_sleeper=lambda league_id: (load_raw(raw), test_api.FETCHED))


def current(api, topic: str, key: str, team: int | None = None) -> bool:
    item = {"topic": topic, "roster_id": LIL_FRIDGE, "team": team, "key": key}
    [state] = api.post(CURRENT, json={"answers": [item]}, headers=HEADERS).json()["answers"]
    assert state["key"] == key and state["kept_at"] is None
    return state["current"]


def test_a_trade_check_sends_the_key_of_the_rosters_it_read_before_its_answer(api):
    parts = _parts(_check(api, SURE_TRADE))
    kinds = [part["type"] for part in parts]
    assert kinds.index("data-key") < kinds.index("data-answer")
    [key] = _of(parts, "data-key")
    assert key["at"].startswith("2026-")
    assert current(api, "trade_check", key["key"], BO_GIRDS)


def test_a_trade_check_goes_stale_when_a_roster_of_its_trade_changes_and_no_other(settings, sources, jev, advisor,
                                                                                  fixture_raw_dir, tmp_path):
    # Story 42: the trade check read Lil Fridge and Bo Girds, so only a change to one of them makes it stale.
    [key] = _of(_parts(_check(_api(settings, sources, jev, advisor), SURE_TRADE)), "data-key")
    other = _api(settings, dropped(sources, fixture_raw_dir, tmp_path, 1), jev, advisor)
    assert current(other, "trade_check", key["key"], BO_GIRDS)
    partner = _api(settings, dropped(sources, fixture_raw_dir, tmp_path, BO_GIRDS), jev, advisor)
    assert not current(partner, "trade_check", key["key"], BO_GIRDS)
    mine = _api(settings, dropped(sources, fixture_raw_dir, tmp_path, LIL_FRIDGE), jev, advisor)
    assert not current(mine, "trade_check", key["key"], BO_GIRDS)


def test_the_form_of_an_unsure_pick_sends_no_key(api):
    assert _of(_parts(_check(api, VAGUE_TRADE)), "data-key") == []


def test_trade_ideas_with_no_partner_read_each_roster_so_any_change_makes_them_stale(settings, sources, jev, advisor,
                                                                                     fixture_raw_dir, tmp_path):
    api = _api(settings, sources, jev, advisor)
    [key] = _of(_parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE}, headers=HEADERS)), "data-key")
    assert current(api, "trade_ideas", key["key"])
    other = _api(settings, dropped(sources, fixture_raw_dir, tmp_path, 1), jev, advisor)
    assert not current(other, "trade_ideas", key["key"])


def test_trade_ideas_with_a_partner_read_only_the_two_rosters(settings, sources, jev, advisor, fixture_raw_dir,
                                                              tmp_path):
    api = _api(settings, sources, jev, advisor)
    body = {"roster_id": LIL_FRIDGE, "partner": BO_GIRDS}
    [key] = _of(_parts(api.post(IDEAS, json=body, headers=HEADERS)), "data-key")
    other = _api(settings, dropped(sources, fixture_raw_dir, tmp_path, 1), jev, advisor)
    assert current(other, "trade_ideas", key["key"], BO_GIRDS)
    partner = _api(settings, dropped(sources, fixture_raw_dir, tmp_path, BO_GIRDS), jev, advisor)
    assert not current(partner, "trade_ideas", key["key"], BO_GIRDS)
