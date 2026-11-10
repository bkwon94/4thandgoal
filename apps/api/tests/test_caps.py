"""
Tests for the caps of the front door: 25 Claude Answers per team per day, and $25 per league per month.
They run at the route seam with FakeJev, a function model of Pydantic AI, and the recorded week 6 Sleeper data.
"""
import logging
from datetime import datetime, timedelta

import test_free_answer
from fakes import FakeJev
from test_free_answer import (
    NOW,
    PASS,
    Checks,
    Script,
    _api,
    _ask,
    _choice,
    _chunks,
    _leader,
)

from cornerstone_api.caps import LEAGUE_LINE, TEAM_LINE, Caps

# The fixture of the free answer tests: a repo with the saved weeks 1 to 5 of the recorded season.
repo = test_free_answer.repo

ASK = "/clients/cpc/ask"
LIL_FRIDGE = 3
BO_GIRDS = 6
QUESTION = "highest scoring team this season"
# The words that cap copy never holds: no manager, and no internal name (the copy rules of the spec).
INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")


def _route(api, question: str = QUESTION, roster_id: int = LIL_FRIDGE):
    return api.post(ASK, json={"question": question, "roster_id": roster_id, "week": 8}, headers=PASS)


def _fill_team(caps: Caps, roster_id: int, count: int, now: datetime = NOW) -> None:
    for _ in range(count):
        caps.record(roster_id, 0.01, now, counts=True)


def _setup(repo, fixture_raw_dir, passes: list[bool] | None = None):
    script = Script("standings", {}, _leader)
    jev = FakeJev(answer=Checks(passes or [True]).answer, choose=_choice)
    api = _api(repo, fixture_raw_dir, jev, script.model())
    return api, script, api.app.state.askers["cpc"].caps


def _names(api) -> list[str]:
    return [name.lower() for name in api.app.state.askers["cpc"].rosters().values()]


def test_at_25_answers_today_the_route_gives_the_team_line_with_3_closest_topics(repo, fixture_raw_dir, caplog):
    # AT-37: the store holds 25 Answers of Lil Fridge today, so the route stops before any Claude call.
    api, script, caps = _setup(repo, fixture_raw_dir)
    _fill_team(caps, LIL_FRIDGE, 25)
    with caplog.at_level(logging.INFO, logger="cornerstone_api"):
        body = _route(api).json()
    assert body["route"] == "cap"
    assert body["line"] == TEAM_LINE == "That's 25 questions today. Ask again tomorrow."
    assert len(body["closest"]) == 3 and body["closest"][0] == "playoff_race"
    assert script.requests == []
    assert "no Claude call" in caplog.text
    # The line names no manager and no internal name.
    assert not any(word in body["line"].lower() for word in (*_names(api), *INNER_NAMES))


def test_the_free_answer_route_refuses_past_the_team_cap_with_no_claude_call(repo, fixture_raw_dir):
    api, script, caps = _setup(repo, fixture_raw_dir)
    _fill_team(caps, LIL_FRIDGE, 25)
    response = _ask(api, QUESTION)
    assert response.status_code == 429
    assert response.json()["detail"] == {"cap": "team", "line": TEAM_LINE}
    assert script.requests == []


def test_24_answers_still_get_a_free_answer_and_it_counts_as_the_25th(repo, fixture_raw_dir):
    api, _, caps = _setup(repo, fixture_raw_dir)
    _fill_team(caps, LIL_FRIDGE, 24)
    assert _route(api).json()["route"] == "free"
    chunks = _chunks(_ask(api, QUESTION))
    assert any(c["type"] == "data-check" and c["data"]["state"] == "checked" for c in chunks)
    assert caps.answers_today(LIL_FRIDGE, NOW) == 25
    assert caps.month_usd(NOW) > 24 * 0.01
    assert _route(api).json()["route"] == "cap"


def test_the_team_cap_is_per_team_and_starts_again_the_next_day(repo, fixture_raw_dir):
    api, _, caps = _setup(repo, fixture_raw_dir)
    _fill_team(caps, LIL_FRIDGE, 25, NOW - timedelta(days=1))
    _fill_team(caps, BO_GIRDS, 25)
    assert _route(api).json()["route"] == "free"
    assert _route(api, roster_id=BO_GIRDS).json()["route"] == "cap"


def test_an_honest_miss_of_a_free_answer_costs_the_league_but_not_the_team(repo, fixture_raw_dir):
    # The PRD: an honest miss does not count toward the team cap. Its Claude cost still counts toward the league cap.
    api, _, caps = _setup(repo, fixture_raw_dir, passes=[False, False])
    chunks = _chunks(_ask(api, QUESTION))
    assert any(c["type"] == "data-miss" for c in chunks)
    assert caps.answers_today(LIL_FRIDGE, NOW) == 0
    assert caps.month_usd(NOW) > 0


def test_a_route_and_a_topic_count_toward_no_cap(repo, fixture_raw_dir):
    api, _, caps = _setup(repo, fixture_raw_dir)
    for _ in range(30):
        _route(api, "who am i playing sunday")
    assert caps.answers_today(LIL_FRIDGE, NOW) == 0
    assert caps.month_usd(NOW) == 0


def test_cpc_at_25_dollars_gets_the_league_line_and_norcal_at_0_still_answers(repo, fixture_raw_dir, tmp_path):
    # AT-38: each league has its own store, so the budget of one never stops the other.
    api, script, caps = _setup(repo, fixture_raw_dir)
    caps.record(None, 25.00, NOW, counts=False)
    body = _route(api).json()
    assert body["route"] == "cap"
    assert body["line"] == LEAGUE_LINE.format(date="Dec 1")
    assert body["line"] == "The league's question budget is used up for this month. It resets on Dec 1."
    assert len(body["closest"]) == 3
    assert _ask(api, QUESTION).json()["detail"]["cap"] == "league"
    assert script.requests == []
    norcal = Caps(tmp_path / "ask" / "norcal.caps.sqlite", "norcal")
    assert norcal.check(LIL_FRIDGE, NOW) is None


def test_the_league_cap_starts_again_on_the_first_of_the_month(repo, fixture_raw_dir):
    _, _, caps = _setup(repo, fixture_raw_dir)
    caps.record(None, 25.00, NOW, counts=False)
    assert caps.check(LIL_FRIDGE, datetime(2026, 12, 1, 0, 5, tzinfo=NOW.tzinfo)) is None
    december = caps.check(LIL_FRIDGE, datetime(2026, 11, 30, 23, 55, tzinfo=NOW.tzinfo))
    assert december is not None and december.line.endswith("It resets on Dec 1.")


def test_the_pass_of_20_dollars_logs_one_alert_and_a_later_answer_logs_no_second(repo, fixture_raw_dir, caplog):
    # AT-39: $19.90 this month, then a free answer of CPC takes the cost past $20.00. The alert sends no email.
    api, _, caps = _setup(repo, fixture_raw_dir, passes=[True, True])
    caps.record(None, 19.90, NOW, counts=False)
    with caplog.at_level(logging.WARNING, logger="cornerstone_api"):
        caps.record(LIL_FRIDGE, 0.15, NOW, counts=True)
        assert caps.month_usd(NOW) > 20.00
        _chunks(_ask(api, QUESTION))
    alerts = [r for r in caplog.records if "80%" in r.getMessage()]
    assert len(alerts) == 1
    assert "cpc" in alerts[0].getMessage() and "$20.05" in alerts[0].getMessage()


def test_the_alert_holds_across_a_restart(repo, fixture_raw_dir, caplog):
    _, _, caps = _setup(repo, fixture_raw_dir)
    caps.record(None, 20.50, NOW, counts=False)
    # The first pass logs the alert of the month. A new store on the same file, as after a deploy, logs none.
    caplog.clear()
    again = Caps(caps.path, "cpc")
    with caplog.at_level(logging.WARNING, logger="cornerstone_api"):
        again.record(LIL_FRIDGE, 0.10, NOW, counts=True)
    assert not [r for r in caplog.records if "80%" in r.getMessage()]
