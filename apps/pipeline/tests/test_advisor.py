"""
Tests for the read of one trade: the sheet the Advisor reads, its guards, the retry, and the honest failure.
They feed the week 6 snapshot to read_trade with a stub Advisor and FakeJev, so no test calls Claude or TypeSafe.
"""
import re
import shutil

import pytest
from cpc import cpc_client, four_week
from fakes import FakeJev, no_news

from analyzer.advisor import AdvisorFailed, AdvisorOut, read_trade
from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.trade_news import NewsFeed
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
# Roster 4 gives Nico Collins to roster 12 for Dalton Kincaid and Garrett Wilson. Roster 4 asks.
COLLINS, KINCAID, WILSON = "7569", "10236", "8146"
CASE = ("If you believe Garrett Wilson keeps his role, this is worth it. You give up the best player in the deal. "
        "The other manager gets a clear upgrade. Push for it only if your receivers need the help.")


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT))


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": COLLINS, "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": KINCAID, "to": 4}, {"player_id": WILSON, "to": 4}])))


def sheet_facts(user: str) -> dict[str, str]:
    """The facts in the user message of the Advisor, by id."""
    return dict(re.findall(r"^- (\S+): (.+)$", user, re.MULTILINE))


def good_out(facts: dict[str, str], **changes) -> dict:
    """A read that passes every guard: each Bullet cites a player fact and says no number."""
    bullet = {"text": "Garrett Wilson has a steady role.", "mark": "for", "fact_id": f"{WILSON}.ppg"}
    against = {"text": "Nico Collins leaves the roster.", "mark": "against", "fact_id": f"{COLLINS}.ppg"}
    even = {"text": "Dalton Kincaid adds depth.", "mark": "even", "fact_id": f"{KINCAID}.ppg"}
    out = {"lean": "Gut call", "case": CASE, "fairness": "fair", "gives_more": None,
           "sides": [{"roster_id": 4, "gains": "It gets more depth at receiver.", "bullets": [bullet, against, even]},
                     {"roster_id": 12, "gains": "It gets the best player in the deal.",
                      "bullets": [against | {"mark": "for"}, bullet | {"mark": "against"}, even]}]}
    return out | changes


class StubAdvisor:
    """The Claude call of the Advisor: it answers from a list of builders, one per call, and keeps each prompt."""

    def __init__(self, *builders):
        self.builders = list(builders)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system, user, output_model):
        assert output_model is AdvisorOut
        self.calls.append((system, user))
        return AdvisorOut.model_validate(self.builders[len(self.calls) - 1](sheet_facts(user)))


def test_a_good_read_carries_the_lean_the_case_the_fairness_and_the_bullets_with_their_fact_text(snap, trade):
    read = read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=StubAdvisor(good_out))
    assert read.lean == "Gut call"
    assert read.case == CASE
    assert read.fairness.state == "fair" and read.fairness.gives_more is None
    assert [s.roster_id for s in read.fairness.sides] == [4, 12]
    assert [side.roster_id for side in read.sides] == [4, 12]
    first = read.sides[0].bullets[0]
    assert first.fact_id == f"{WILSON}.ppg"
    assert first.fact_text.startswith("Garrett Wilson")
    assert first.mark == "for"


def test_the_advisor_reads_the_jev_answers_beside_the_facts_of_the_trade(snap, trade):
    advisor = StubAdvisor(good_out)
    read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    _, user = advisor.calls[0]
    facts = sheet_facts(user)
    assert {"JEV.fair", "JEV.need.4", "JEV.need.12", "JEV.accept.12"} <= set(facts)
    assert f"{COLLINS}.ppg" in facts


def test_a_lopsided_read_names_the_side_that_gives_more(snap, trade):
    read = read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=StubAdvisor(
        lambda facts: good_out(facts, lean="Pass", fairness="lopsided", gives_more=4)))
    assert read.lean == "Pass"
    assert read.fairness.state == "lopsided" and read.fairness.gives_more == 4


@pytest.mark.parametrize("bad, rule", [
    (lambda out: out["sides"][0]["bullets"][0] | {"fact_id": "NO.such"}, "is not on the sheet"),
    (lambda out: out["sides"][0]["bullets"][0] | {"text": "Garrett Wilson scored 99.9 points a game."},
     "number 99.9"),
    (lambda out: out["sides"][0]["bullets"][0] | {"text": "Garrett Wilson has more trade value."}, "trade value"),
    (lambda out: out["sides"][0]["bullets"][0] | {"text": "Garrett Wilson is no rival to anyone."}, "rival"),
    (lambda out: out["sides"][0]["bullets"][0] | {"text": "Josh Jacobs would fit here."}, "Josh Jacobs"),
])
def test_a_bullet_that_breaks_a_guard_retries_once_with_the_failure_as_feedback(snap, trade, bad, rule):
    def broken(facts):
        out = good_out(facts)
        out["sides"][0]["bullets"][0] = bad(out)
        return out

    advisor = StubAdvisor(broken, good_out)
    read = read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 2
    assert rule in advisor.calls[1][1]
    assert read.sides[0].bullets[0].fact_id == f"{WILSON}.ppg"


def test_a_number_joined_to_a_word_by_a_hyphen_is_not_a_negative_number(snap, trade):
    """A model writes "top-36" for the top 36. The hyphen is a joiner, so the number is 36 and not -36."""
    def hyphenated(facts):
        number = re.search(r"(?<![\d.])\d+(?![\d.])", facts[f"{WILSON}.ppg"]).group()
        out = good_out(facts)
        out["sides"][0]["bullets"][0] = out["sides"][0]["bullets"][0] | {
            "text": f"Garrett Wilson sits in the top-{number} at his spot."}
        return out

    advisor = StubAdvisor(hyphenated)
    read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 1


def test_a_negative_number_that_is_not_in_the_cited_fact_still_fails(snap, trade):
    def negative(facts):
        out = good_out(facts)
        out["sides"][0]["bullets"][0] = out["sides"][0]["bullets"][0] | {
            "text": "Garrett Wilson scored -97 points a game."}
        return out

    advisor = StubAdvisor(negative, good_out)
    read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 2 and "number -97" in advisor.calls[1][1]


@pytest.mark.parametrize("change, rule", [
    ({"case": "You give up the best player. If you believe in Wilson, send it."}, "condition"),
    ({"fairness": "lopsided", "gives_more": None}, "gives_more"),
])
def test_a_case_with_no_condition_first_or_a_lopsided_read_with_no_side_retries(snap, trade, change, rule):
    advisor = StubAdvisor(lambda facts: good_out(facts, **change), good_out)
    read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 2
    assert rule in advisor.calls[1][1]


def test_a_side_with_two_bullets_retries(snap, trade):
    def short(facts):
        out = good_out(facts)
        out["sides"][1]["bullets"] = out["sides"][1]["bullets"][:2]
        return out

    advisor = StubAdvisor(short, good_out)
    read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert "3 to 5" in advisor.calls[1][1]


def test_two_failed_calls_raise_advisor_failed(snap, trade, caplog):
    def broken(facts):
        return good_out(facts, case="Send it now.")

    advisor = StubAdvisor(broken, broken)
    with pytest.raises(AdvisorFailed):
        read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 2
    assert "advisor attempt 2 failed" in caplog.text


def test_a_failed_jev_call_still_gives_a_read_with_no_jev_fact(snap, trade):
    from league.jev_port import JevError
    advisor = StubAdvisor(good_out)
    read = read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(error=JevError("timeout")), call=advisor)
    assert read.lean == "Gut call"
    assert not any(fid.startswith("JEV.") for fid in sheet_facts(advisor.calls[0][1]))


@pytest.fixture
def snap_no_chart(fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return four_week(load_snapshot(fixture_raw_dir, fixture_history_root, None, slow, client=CLIENT))


def test_a_week_with_no_chart_still_gives_a_read_when_the_case_says_the_chart_is_missing(snap_no_chart, trade):
    case = ("If you believe Garrett Wilson keeps his role, this is worth it. The chart of this week is missing, "
            "so the call rests on the facts of the players. Push for it only if your receivers need the help.")
    advisor = StubAdvisor(lambda facts: good_out(facts, case=case))
    read = read_trade(trade, snap_no_chart, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 1
    assert "trade.chart" in sheet_facts(advisor.calls[0][1])
    assert read.case == case


def test_a_case_that_does_not_say_the_chart_is_missing_retries_with_the_failure_as_feedback(snap_no_chart, trade):
    advisor = StubAdvisor(good_out, lambda facts: good_out(
        facts, case=CASE.replace("this is worth it.", "this is worth it. The chart is missing this week.")))
    read_trade(trade, snap_no_chart, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert len(advisor.calls) == 2
    assert "chart is missing" in advisor.calls[1][1]


def test_the_prompt_says_the_playbook_wins_over_the_chart(snap, trade):
    advisor = StubAdvisor(good_out)
    read_trade(trade, snap, news=NewsFeed(fetch=no_news), jev=FakeJev(), call=advisor)
    assert "the playbook wins over the chart" in advisor.calls[0][0].lower()
    assert "trade.chart" not in sheet_facts(advisor.calls[0][1])
