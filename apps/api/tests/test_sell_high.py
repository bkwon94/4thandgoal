"""
Tests for the sell high Topic of the front door at the route seam, with FakeJev and a stub Claude call.
The sheet, the guards, the retry, and the Jev checks of the Advisor run for real on the week 6 fixtures of cpc.
"""
import functools
import json
import re

import pytest
import test_api
from fakes import NEWS_RECORDED, FakeJev, recorded_news
from fastapi.testclient import TestClient
from test_api import CLIENT, HEADERS, _cpc, _here

from analyzer.sell_high import SellHighOut, pick_sells
from analyzer.trade_news import NewsFeed
from cornerstone_api.app import create_app

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

SELL = "/clients/cpc/sell-high"
LIL_FRIDGE = 3
HEADLINE = "Sell him while his last month reads well."
# The words that site copy never holds (decision 08 and the copy rules of the spec).
INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")


def passing_sells(user: str, **changes) -> dict:
    """Picks that pass every guard: the first player of the sheet, with two Bullets on his trend fact."""
    first = re.search(r"^Player (\S+):", user, re.MULTILINE).group(1)
    bullets = [{"text": "His last month is his best stretch of the season.", "mark": "for", "fact_id": f"{first}.trend"},
               {"text": "Another manager pays for that kind of run.", "mark": "for", "fact_id": f"{first}.trend"}]
    out = {"picks": [{"player_id": first, "headline": HEADLINE, "bullets": bullets}], "none_line": None}
    return out | changes


class StubSeller:
    """The Claude call of the sell high pick with no network: it answers from a list of builders, one per call.

    Each builder takes the user message and gives the output. The last builder answers every later call.
    """

    def __init__(self, *builders):
        self.builders = list(builders) or [passing_sells]
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system, user, output_model):
        assert output_model is SellHighOut
        self.calls.append((system, user))
        build = self.builders[min(len(self.calls), len(self.builders)) - 1]
        return SellHighOut.model_validate(build(user))


@pytest.fixture
def jev():
    return FakeJev()


@pytest.fixture
def seller():
    return StubSeller()


def _app(settings, sources, jev, seller):
    news = NewsFeed(fetch=recorded_news, now=lambda: NEWS_RECORDED)
    return TestClient(create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), jev=jev,
                                 sell_high=functools.partial(pick_sells, jev=jev, news=news, call=seller)))


@pytest.fixture
def api(settings, sources, jev, seller):
    return _app(settings, sources, jev, seller)


def _parts(response) -> list[dict]:
    lines = [line.removeprefix("data: ") for line in response.text.split("\n\n") if line.startswith("data: ")]
    return [json.loads(line) for line in lines if line != "[DONE]"]


def _of(parts: list[dict], kind: str) -> list[dict]:
    return [part["data"] for part in parts if part["type"] == kind]


def _sell(api, roster_id: int = LIL_FRIDGE):
    return api.post(SELL, json={"roster_id": roster_id}, headers=HEADERS)


def _roster(api, roster_id: int = LIL_FRIDGE) -> list[dict]:
    """The players of a roster, from the teams route of the analyzer."""
    teams = api.get("/clients/cpc/teams", params={"season": 2026}, headers=HEADERS).json()["teams"]
    return next(team["players"] for team in teams if team["roster_id"] == roster_id)


def test_the_answer_names_a_player_of_lil_fridge_to_sell_with_the_reason(api):
    # AT-27 at the route seam.
    response = _sell(api)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    [answer] = _of(_parts(response), "data-answer")
    assert answer["kind"] == "sell"
    document = answer["document"]
    assert document["team"] == {"roster_id": LIL_FRIDGE, "team": "Lil Fridge"}
    [pick] = document["picks"]
    assert pick["player"]["player_id"] in {player["player_id"] for player in _roster(api)}
    assert pick["headline"] == HEADLINE
    assert len(pick["bullets"]) == 2
    assert all(bullet["fact_text"] for bullet in pick["bullets"])


def test_the_sheet_puts_the_four_reads_of_each_player_side_by_side_and_drops_no_player(api, seller):
    # Code gives facts and the Advisor picks, so every QB, RB, WR, and TE of the roster reaches the call.
    _sell(api)
    [(system, user)] = seller.calls
    listed = re.findall(r"^Player (\S+):", user, re.MULTILINE)
    ranked = [p["player_id"] for p in _roster(api) if p["position"] in ("QB", "RB", "WR", "TE")]
    assert listed == ranked
    for pid in listed:
        block = user.split(f"Player {pid}:")[1].split("\nPlayer ")[0]
        for read in ("value", "lineup", "trend", "schedule"):
            assert f"- {pid}.{read}: " in block
    assert "Playbook" in system or "playbook" in system.lower()


def test_the_trend_and_the_schedule_read_the_last_4_weeks_and_the_weeks_ahead(api, seller):
    _sell(api)
    [(_, user)] = seller.calls
    trend = re.search(r"^- \d+\.trend: (.*)$", user, re.MULTILINE).group(1)
    assert trend.startswith("Over the last 4 weeks, ") and " over the season." in trend
    schedule = re.search(r"^- \d+\.schedule: (.*)$", user, re.MULTILINE).group(1)
    assert schedule.startswith("The schedule ahead of ") and "week 6 " in schedule


def _other_player(user: str) -> dict:
    """Picks of a player who is not on the sheet, so the guard fails the response."""
    return passing_sells(user) | {"picks": [{**passing_sells(user)["picks"][0], "player_id": "0000"}]}


def test_a_pick_of_a_player_off_the_roster_retries_with_the_failure_as_feedback(settings, sources, jev):
    seller = StubSeller(_other_player, passing_sells)
    [answer] = _of(_parts(_sell(_app(settings, sources, jev, seller))), "data-answer")
    assert len(answer["document"]["picks"]) == 1
    assert len(seller.calls) == 2
    assert "player 0000 is not a player of the sheet" in seller.calls[1][1]


def test_a_number_that_no_cited_fact_holds_fails_the_guard_of_the_advisor(settings, sources, jev):
    def made_up(user: str) -> dict:
        out = passing_sells(user)
        return out | {"picks": [{**out["picks"][0], "headline": "Sell him before he drops 40 spots."}]}

    seller = StubSeller(made_up, passing_sells)
    _of(_parts(_sell(_app(settings, sources, jev, seller))), "data-answer")
    assert "number 40 is not in the cited facts" in seller.calls[1][1]


def test_two_failed_picks_are_an_honest_error_and_never_a_pick(settings, sources, jev):
    seller = StubSeller(_other_player)
    api = _app(settings, sources, jev, seller)
    parts = _parts(_sell(api))
    assert _of(parts, "data-answer") == []
    [error] = _of(parts, "data-error")
    assert error["status"] == 503 and "does not count toward your grades" in error["line"]
    # A failed pick is not kept, so the next press calls the Advisor again.
    _sell(api)
    assert len(seller.calls) == 4


def test_the_jev_checks_of_the_advisor_read_each_bullet_against_its_fact(api, jev):
    _sell(api)
    checks = [r for r in jev.requests if any(key.startswith("faithful.") for key in r.questions)]
    [request] = checks
    assert set(request.questions) == {f"faithful.{LIL_FRIDGE}.1", f"faithful.{LIL_FRIDGE}.2"}


def test_the_steps_come_one_by_one_before_the_whole_answer_and_name_no_inner_tool(api):
    # The steps show before the whole Answer, as in ticket 09.
    parts = _parts(_sell(api))
    kinds = [part["type"] for part in parts]
    assert kinds[0] == "start" and kinds[-1] == "finish"
    lines = [step["line"] for step in _of(parts, "data-step")]
    ranked = sum(p["position"] in ("QB", "RB", "WR", "TE") for p in _roster(api))
    assert lines == [f"Lined up your {ranked} players", "Checked each number of the picks", "Picked one player to sell"]
    assert kinds.index("data-answer") > max(i for i, kind in enumerate(kinds) if kind == "data-step")
    assert not [line for line in lines if any(word in line.lower() for word in INNER_NAMES)]


def test_a_roster_with_no_clear_sell_gives_the_plain_line(settings, sources, jev):
    line = "No player on your roster is priced above what he gives you."
    seller = StubSeller(lambda user: {"picks": [], "none_line": line})
    [answer] = _of(_parts(_sell(_app(settings, sources, jev, seller))), "data-answer")
    assert answer["document"]["picks"] == [] and answer["document"]["empty"] == line


def test_a_repeat_comes_from_the_cache_with_no_claude_call(api, seller):
    first = _of(_parts(_sell(api)), "data-answer")
    second = _of(_parts(_sell(api)), "data-answer")
    assert first == second
    assert len(seller.calls) == 1


def test_sell_high_needs_the_passphrase(api):
    assert api.post(SELL, json={"roster_id": LIL_FRIDGE}).status_code == 401


def test_a_team_that_is_not_in_the_league_is_422(api):
    assert _sell(api, 99).status_code == 422


def test_past_the_team_cap_sell_high_gives_the_cap_line_and_no_claude_call(api, seller):
    asker = api.app.state.askers["cpc"]
    now = asker.clock()
    for _ in range(25):
        asker.caps.record(LIL_FRIDGE, 0.01, now, counts=True)
    parts = _parts(api.post(SELL, json={"roster_id": LIL_FRIDGE}, headers=HEADERS))
    [cap] = [part["data"] for part in parts if part.get("type") == "data-cap"]
    assert cap["cap"] == "team" and cap["line"] == "That's 25 questions today. Ask again tomorrow."
    assert [part for part in parts if part.get("type") == "data-answer"] == []
    assert seller.calls == []
