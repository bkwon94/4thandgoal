"""
Tests for the trade Topics of the front door, the trade check and trade ideas, at the route seam with FakeJev.
The Advisor runs for real with the stub Claude calls of test_api, so the sheet, the guards, and the stages run.
"""
import dataclasses
import functools
import json
import shutil
from pathlib import Path

import pytest
import test_api
from fakes import NEWS_RECORDED, FakeJev, recorded_news
from fastapi.testclient import TestClient
from test_api import CLIENT, HEADERS, StubAdvisor, StubPicker, StubRepair, _cpc, _here

from analyzer.advisor import AdvisorOut, read_trade
from analyzer.cache import finder_cache_key
from analyzer.finder_pick import pick_trades
from analyzer.finder_search import Anchor, Limit, search
from analyzer.trade_news import NewsFeed
from analyzer.values import AnalyzerValues
from cornerstone_api.app import create_app
from cornerstone_api.caps import TEAM_LINE
from cornerstone_api.trade_topics import NO_ONE_PLAYER
from cornerstone_api.trade_wording import (
    AIM_POSITION,
    AIMS_POSITION,
    GETS_ALSO_NAMED,
    GETS_ALSO_PLAYER,
    GETS_NAMED,
    GETS_PLAYER,
    GIVES_NAMED,
    GIVES_PLAYER,
    KEEPS_NAMED,
    KEEPS_POSITION,
    KEPT_PLAYER,
)
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
GIVE_IDEAS = "trade ideas for khalil shakir"
GET_IDEAS = "trade ideas to get zay flowers"
VAGUE_IDEAS = "any trade ideas for my team"
NO_TE = "id rather not trade a TE"
KEEP_SHAKIR = "keep shakir"
FOR_A_TE = "what about for a TE"
ONE_FOR_TWO = "trade Kyren Williams for Chase Brown and Devonta Smith"
# The rosters of the week 9 build of cpc, where Chase Brown and DeVonta Smith are both on NFC Least.
WEEK_9_RAW = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "data" / "2026" / "week-09" / "raw"
NFC_LEAST = 4
SHAKIR = "8134"
FLOWERS = "9997"
# The words that site copy never holds (decision 08 and the copy rules of the spec).
INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")

# The Jev answers of each trade question: the two Nouls, and the player that each Choice puts its weight on.
PICKS = {
    SURE_TRADE: {GIVES_NAMED: 0.97, GETS_NAMED: 0.96, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
    VAGUE_TRADE: {GIVES_NAMED: 0.08, GETS_NAMED: 0.06, GIVES_PLAYER: "Derrick Henry", GETS_PLAYER: "Zay Flowers"},
    HALF_TRADE: {GIVES_NAMED: 0.95, GETS_NAMED: 0.12, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
    GIVE_IDEAS: {GIVES_NAMED: 0.96, GETS_NAMED: 0.05, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
    GET_IDEAS: {GIVES_NAMED: 0.04, GETS_NAMED: 0.95, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
    VAGUE_IDEAS: {GIVES_NAMED: 0.05, GETS_NAMED: 0.06, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers"},
    NO_TE: {GIVES_NAMED: 0.05, GETS_NAMED: 0.04, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers",
            KEEPS_POSITION["TE"]: 0.95},
    KEEP_SHAKIR: {GIVES_NAMED: 0.2, GETS_NAMED: 0.04, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers",
                  KEEPS_NAMED: 0.94, KEPT_PLAYER: "Khalil Shakir"},
    FOR_A_TE: {GIVES_NAMED: 0.05, GETS_NAMED: 0.1, GIVES_PLAYER: "Khalil Shakir", GETS_PLAYER: "Zay Flowers",
               AIMS_POSITION: 0.93, AIM_POSITION: "TE"},
    # Each Choice picks one player, so the second player that the manager gets has a Noul and a Choice of its own.
    ONE_FOR_TWO: {GIVES_NAMED: 0.97, GETS_NAMED: 0.96, GIVES_PLAYER: "Kyren Williams", GETS_PLAYER: "Chase Brown",
                  GETS_ALSO_NAMED: 0.94, GETS_ALSO_PLAYER: "DeVonta Smith"},
}


def _answer(key: str, question: NoulQuestion, state: dict) -> float:
    """The Noul answers of a pick request by its question, and a yes for each Noul of the Advisor and the Finder. A Noul
    of the limit that PICKS does not name is a no, so a question sets no limit unless it says one."""
    picks = PICKS.get(state.get("manager_question", ""))
    if picks is None:
        return 0.9
    return picks.get(key, 0.05)


def _choose(key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
    """Each Choice of a pick request puts its weight on the player of PICKS, by the name in its option text. A Choice
    that PICKS does not name spreads its weight."""
    name = PICKS[state["manager_question"]].get(key)
    if name is None:
        return {option: 1 / len(question.options) for option in question.options}
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
                              "sure": True, "roster_id": LIL_FRIDGE, "also": None}
    assert picks["gets"]["player_id"] == "9997" and picks["gets"]["roster_id"] == BO_GIRDS and picks["gets"]["sure"]


def test_one_jev_request_picks_each_side_from_the_real_rosters(api, jev):
    _check(api, VAGUE_TRADE)
    [request] = [r for r in jev.requests if "manager_question" in r.state]
    assert {GIVES_NAMED, GIVES_PLAYER, GETS_NAMED, GETS_PLAYER} <= set(request.questions)
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


def test_a_typed_one_for_two_trade_weighs_all_three_players(settings, sources, jev, advisor):
    week_9 = dataclasses.replace(sources, fetch_sleeper=lambda league_id: (load_raw(WEEK_9_RAW), test_api.FETCHED))
    response = _api(settings, week_9, jev, advisor).post(
        CHECK, json={"question": ONE_FOR_TWO, "roster_id": BO_GIRDS}, headers=HEADERS)
    [answer] = _of(_parts(response), "data-answer")
    assert answer["kind"] == "check"
    [yours, theirs] = answer["document"]["trade"]["sides"]
    assert [player["name"] for player in yours["gives"]] == ["Kyren Williams"]
    assert [player["name"] for player in yours["gets"]] == ["Chase Brown", "DeVonta Smith"]
    assert theirs["roster_id"] == NFC_LEAST


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


def _ideas(api, question: str | None = None, turns: list[dict] | None = None):
    body = {"roster_id": LIL_FRIDGE} if question is None else {"roster_id": LIL_FRIDGE, "question": question}
    if turns is not None:
        body["turns"] = turns
    return _parts(api.post(IDEAS, json=body, headers=HEADERS))


def _pick_requests(jev) -> list:
    return [r for r in jev.requests if "manager_question" in r.state]


def test_a_typed_question_of_trade_ideas_goes_with_one_jev_pick_over_the_real_rosters(api, jev):
    parts = _ideas(api, GIVE_IDEAS)
    [request] = _pick_requests(jev)
    assert request.state["manager_question"] == GIVE_IDEAS
    assert "trade ideas" in request.state["context"]
    assert {GIVES_NAMED, GIVES_PLAYER, GETS_NAMED, GETS_PLAYER} <= set(request.questions)
    assert any(text.startswith("Khalil Shakir (WR") for text in request.questions[GIVES_PLAYER].options.values())
    assert any(text.startswith("Zay Flowers (WR") for text in request.questions[GETS_PLAYER].options.values())
    [picks] = _of(parts, "data-picks")
    assert picks["gives"]["player_id"] == SHAKIR and picks["gives"]["sure"]


def test_a_tap_of_trade_ideas_sends_no_question_and_asks_no_pick(api, jev):
    _ideas(api)
    assert _pick_requests(jev) == []


def test_ideas_around_a_player_that_the_manager_gives_hold_him_on_the_side_of_your_team(api):
    parts = _ideas(api, GIVE_IDEAS)
    assert "Found Khalil Shakir" in [step["line"] for step in _of(parts, "data-step")]
    [answer] = _of(parts, "data-answer")
    trades = answer["document"]["trades"]
    assert trades
    for trade in trades:
        mine = trade["sides"][0]
        assert mine["roster_id"] == LIL_FRIDGE
        assert SHAKIR in [player["player_id"] for player in mine["gives"]]


def test_ideas_around_a_player_that_the_manager_gets_hold_him_on_the_side_of_his_team(api):
    parts = _ideas(api, GET_IDEAS)
    assert "Found Zay Flowers" in [step["line"] for step in _of(parts, "data-step")]
    [answer] = _of(parts, "data-answer")
    assert answer["document"]["trade_pair"]["partner"]["roster_id"] == BO_GIRDS
    trades = answer["document"]["trades"]
    assert trades
    for trade in trades:
        theirs = trade["sides"][1]
        assert theirs["roster_id"] == BO_GIRDS
        assert FLOWERS in [player["player_id"] for player in theirs["gives"]]


def test_an_unsure_pick_falls_back_to_the_weakest_slot_search_with_a_step_that_says_so(api):
    plain = _of(_ideas(api), "data-answer")
    parts = _ideas(api, VAGUE_IDEAS)
    lines = [step["line"] for step in _of(parts, "data-step")]
    assert lines[0] == NO_ONE_PLAYER
    assert not any(word in NO_ONE_PLAYER.lower() for word in INNER_NAMES)
    # The fallback is the plain search, so it gives the same trades as a tap.
    assert _of(parts, "data-answer") == plain


def test_the_kept_answer_key_holds_the_anchor(settings, sources):
    snapshot = _here(sources, settings).snapshot(2026)
    plain = finder_cache_key(2026, LIL_FRIDGE, None, snapshot)
    gives = finder_cache_key(2026, LIL_FRIDGE, None, snapshot, Anchor(player_id=SHAKIR, side="gives"))
    gets = finder_cache_key(2026, LIL_FRIDGE, None, snapshot, Anchor(player_id=SHAKIR, side="gets"))
    assert len({plain, gives, gets}) == 3


def test_a_player_search_after_a_tap_never_serves_the_plain_list(api):
    _ideas(api)
    [answer] = _of(_ideas(api, GIVE_IDEAS), "data-answer")
    assert all(SHAKIR in [player["player_id"] for player in trade["sides"][0]["gives"]]
               for trade in answer["document"]["trades"])


def live_then_done(steps: list[dict]) -> list[str]:
    """Check the step parts of one stream, and give its done lines. A live step names the stage at work in the present,
    such as "Building offers". Its done line comes next, in the past, such as "Built 56 offers"."""
    for index, step in enumerate(steps):
        first = step["line"].split()[0]
        if step["live"]:
            assert first.endswith("ing"), step
            assert index + 1 < len(steps) and not steps[index + 1]["live"], step
        else:
            assert not first.endswith("ing"), step
    return [step["line"] for step in steps if not step["live"]]


def test_each_stage_of_trade_ideas_sends_a_live_line_then_its_done_line(api):
    steps = _of(_ideas(api), "data-step")
    assert [step["line"] for step in steps if step["live"]] == [
        "Checking 11 teams for a fit", "Building offers", "Weighing the offers", "Picking the best offers"]
    done = live_then_done(steps)
    assert done[0] == "Checked 11 teams for a fit" and done[-1] == "Picked the best 3"


def test_each_stage_of_a_trade_check_sends_a_live_line_then_its_done_line(api):
    steps = _of(_parts(_check(api, SURE_TRADE)), "data-step")
    assert [step["line"] for step in steps if step["live"]] == [
        "Checking the players on each side", "Checking each number of the read"]
    assert live_then_done(steps) == [
        "Found Khalil Shakir and Zay Flowers", "Checked the players on each side", "Checked each number of the read"]


# The trade turn before a follow-up, as the site sends it.
IDEAS_TURN = {"question": "Trade ideas", "answer": "2 offers. Offer 1: Lil Fridge gives Khalil Shakir. Bo Girds gives "
                                                  "Zay Flowers. Offer 2: Lil Fridge gives Derrick Henry. Teehee gives "
                                                  "Jalen Hurts."}


def _positions(side: dict) -> list[str]:
    return [player["position"] for player in side["gives"]]


def test_a_follow_up_reads_its_limit_with_the_pick_in_one_request_over_the_turns(api, jev):
    parts = _ideas(api, NO_TE, [IDEAS_TURN])
    [request] = _pick_requests(jev)
    assert request.state["earlier_turns"] == [IDEAS_TURN]
    assert set(KEEPS_POSITION.values()) | {KEEPS_NAMED, KEPT_PLAYER, AIMS_POSITION, AIM_POSITION} <= set(request.questions)
    [limit] = _of(parts, "data-limit")
    assert limit == {"keep_positions": ["TE"], "keep_players": [], "aim_position": None}


def test_a_follow_up_that_keeps_each_te_gives_no_offer_that_sends_a_te_away(api):
    plain = _of(_ideas(api), "data-answer")[0]["document"]["trades"]
    # The plain list sends a TE away, so the limit has an offer to drop.
    assert any("TE" in _positions(trade["sides"][0]) for trade in plain)
    parts = _ideas(api, NO_TE, [IDEAS_TURN])
    lines = [step["line"] for step in _of(parts, "data-step")]
    assert "Left out each offer that sends away a TE" in lines
    assert NO_ONE_PLAYER not in lines
    trades = _of(parts, "data-answer")[0]["document"]["trades"]
    assert trades
    assert all("TE" not in _positions(trade["sides"][0]) for trade in trades)


def test_a_follow_up_that_keeps_one_player_gives_no_offer_that_sends_him_away(api):
    parts = _ideas(api, KEEP_SHAKIR, [IDEAS_TURN])
    assert "Left out each offer that sends away Khalil Shakir" in [step["line"] for step in _of(parts, "data-step")]
    trades = _of(parts, "data-answer")[0]["document"]["trades"]
    assert trades
    assert all(SHAKIR not in [player["player_id"] for player in trade["sides"][0]["gives"]] for trade in trades)


def test_a_follow_up_that_aims_at_a_position_gives_offers_that_bring_one_back(api):
    parts = _ideas(api, FOR_A_TE, [IDEAS_TURN])
    assert "Looked only for offers that bring back a TE" in [step["line"] for step in _of(parts, "data-step")]
    trades = _of(parts, "data-answer")[0]["document"]["trades"]
    assert trades
    assert all("TE" in _positions(trade["sides"][1]) for trade in trades)


def test_no_limit_line_names_an_inner_tool(api):
    lines = [step["line"] for question in (NO_TE, KEEP_SHAKIR, FOR_A_TE)
             for step in _of(_ideas(api, question, [IDEAS_TURN]), "data-step")]
    assert not any(word in line.lower() for line in lines for word in INNER_NAMES)


def test_the_kept_answer_key_holds_the_limit(settings, sources):
    snapshot = _here(sources, settings).snapshot(2026)
    plain = finder_cache_key(2026, LIL_FRIDGE, None, snapshot)
    no_wr = finder_cache_key(2026, LIL_FRIDGE, None, snapshot, limit=Limit(keep_positions=["WR"]))
    keep = finder_cache_key(2026, LIL_FRIDGE, None, snapshot, limit=Limit(keep_players=[SHAKIR]))
    te = finder_cache_key(2026, LIL_FRIDGE, None, snapshot, limit=Limit(aim_position="TE"))
    assert len({plain, no_wr, keep, te}) == 4


# The projected points of the week 6 fixture from the trade week 6 through week 14, the last week that it holds.
SHAKIR_REST = 57.61
FLOWERS_REST = 126.9


def test_a_trade_check_sends_the_trade_card_with_the_lean_the_case_and_the_points_of_each_side(api):
    # AT-34: the two sides, the projected points for the rest of the season of each player, and the Lean.
    [answer] = _of(_parts(_check(api, SURE_TRADE)), "data-answer")
    block = answer["block"]
    assert block["kind"] == "trade"
    [offer] = block["offers"]
    assert offer["lean"] == answer["document"]["lean"] == "Lean yes"
    assert offer["case"] == answer["document"]["case"]
    assert offer["partner"] == "Bo Girds"
    # Your side comes first, and each side lists the players it gets.
    yours, theirs = offer["sides"]
    assert yours["yours"] and yours["team"] == "Lil Fridge" and not theirs["yours"]
    assert [(p["name"], p["points"]) for p in yours["gets"]] == [("Zay Flowers", FLOWERS_REST)]
    assert [(p["name"], p["points"]) for p in theirs["gets"]] == [("Khalil Shakir", SHAKIR_REST)]
    assert (yours["total"], theirs["total"]) == (FLOWERS_REST, SHAKIR_REST)
    # The top Bullets of Your side open in place. The card adds no grade and no edge in points.
    mine = next(side for side in answer["document"]["sides"] if side["roster_id"] == LIL_FRIDGE)
    assert offer["bullets"] == mine["bullets"][:3]
    assert "edge" not in json.dumps(block).lower()


def test_trade_ideas_send_one_trade_card_with_a_row_per_offer(api):
    # AT-33: one card, one offer per pick, each with its partner, its headline as the gist, and the points of each side.
    [answer] = _of(_parts(api.post(IDEAS, json={"roster_id": LIL_FRIDGE}, headers=HEADERS)), "data-answer")
    document, block = answer["document"], answer["block"]
    assert block["kind"] == "trade"
    assert [offer["id"] for offer in block["offers"]] == [trade["offer_id"] for trade in document["trades"]]
    for offer, trade in zip(block["offers"], document["trades"], strict=True):
        partner = next(side for side in trade["sides"] if side["roster_id"] != LIL_FRIDGE)
        assert offer["partner"] == partner["team"]
        assert offer["gist"] == trade["headline"]
        assert offer["lean"] is None and offer["bullets"] == trade["bullets"][:2]
        assert offer["sides"][0]["yours"] and offer["sides"][0]["roster_id"] == LIL_FRIDGE
        for side in offer["sides"]:
            assert side["gets"] and side["total"] == round(sum(p["points"] for p in side["gets"]), 2)
            assert all(p["points"] > 0 for p in side["gets"])
