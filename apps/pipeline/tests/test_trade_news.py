"""
Tests for the news of the trade players: the NEWS facts on the sheet, the cache of 1 hour, the failed fetch, the
attribution guard, and the log-only Jev checks of a read. The feed is the real feed of Jonathan Taylor, recorded.
"""
import shutil
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from cpc import cpc_client, four_week
from fakes import NEWS_RECORDED, FakeJev, recorded_news
from test_advisor import COLLINS, StubAdvisor, sheet_facts

from analyzer.advisor import advisor_sheet, read_trade
from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.trade_news import NewsFeed
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

TAYLOR = "6813"
URL = "https://"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot of cpc, where roster 11 holds Jonathan Taylor."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=cpc_client()))


@pytest.fixture
def trade():
    """Roster 4 gives Nico Collins to roster 11 for Jonathan Taylor. Roster 4 asks."""
    return ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": COLLINS, "to": 11}]),
        TradeSide(roster_id=11, gives=[{"player_id": TAYLOR, "to": 4}])))


def feed(now=NEWS_RECORDED, fetch=recorded_news, clock=None) -> NewsFeed:
    return NewsFeed(fetch=fetch, now=lambda: now, **({"clock": clock} if clock else {}))


def taylor_out(facts: dict[str, str], news_bullet: dict | None = None) -> dict:
    """A read of the Taylor trade that passes every guard. With `news_bullet`, it is the first Bullet of the asker."""
    collins = {"text": "Nico Collins leaves the roster.", "mark": "against", "fact_id": f"{COLLINS}.ppg"}
    taylor = {"text": "Jonathan Taylor joins a new backfield.", "mark": "for", "fact_id": f"{TAYLOR}.ppg"}
    even = {"text": "The deal swaps one starter for another.", "mark": "even", "fact_id": f"{TAYLOR}.ppg"}
    asker = [news_bullet or taylor, collins, even]
    case = ("If you believe Jonathan Taylor stays the lead back, this is worth it. You give up a steady receiver. "
            "The other manager gets help at receiver.")
    return {"lean": "Gut call", "case": case, "fairness": "fair", "gives_more": None,
            "sides": [{"roster_id": 4, "gains": "It gets a lead back.", "bullets": asker},
                      {"roster_id": 11, "gains": "It gets a receiver.",
                       "bullets": [collins | {"mark": "for"}, taylor | {"mark": "against"}, even]}]}


def news_of(facts, pid=TAYLOR):
    return {fid: f for fid, f in facts.items() if fid.startswith(f"NEWS.{pid}.")}


def test_the_sheet_holds_the_newest_2_reports_of_a_trade_player_from_the_last_7_days(snap, trade):
    news = news_of(advisor_sheet(trade, snap, FakeJev(), feed()))
    assert list(news) == [f"NEWS.{TAYLOR}.1", f"NEWS.{TAYLOR}.2"]
    first, second = news.values()
    assert first.text.startswith("Reported on 2026-11-09 by Rotoballer: The Denver Broncos enter their Week 10 bye")
    assert second.text.startswith("Reported on 2026-11-09 by Rotoballer: According to ESPN's Jordan Raanan")
    for f in news.values():
        description = f.text.split(": ", 1)[1]
        assert len(description) <= 300
        assert not any(URL in n for n in f.numbers)
        assert "2026" in f.numbers and "Jonathan Taylor" in f.players


def test_a_report_older_than_7_days_leaves_the_sheet(snap, trade):
    # The second item came at 09:46 UTC and the newest at 15:50 UTC, so 7 days and 1 hour after the second keeps one.
    later = datetime(2026, 11, 9, 9, 46, tzinfo=UTC) + timedelta(days=7, hours=1)
    news = news_of(advisor_sheet(trade, snap, FakeJev(), feed(now=later)))
    assert list(news) == [f"NEWS.{TAYLOR}.1"]
    assert "Denver Broncos" in news[f"NEWS.{TAYLOR}.1"].text


def test_an_item_with_no_description_drops(snap, trade):
    def no_description(pid):
        return [item | {"metadata": {"title": item["metadata"]["title"]}} for item in recorded_news(pid)]

    assert news_of(advisor_sheet(trade, snap, FakeJev(), feed(fetch=no_description))) == {}


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_a_second_sheet_within_1_hour_fetches_no_news_for_the_same_player(snap, trade, caplog):
    fetched = []

    def counted(pid):
        fetched.append(pid)
        return recorded_news(pid)

    clock = Clock()
    news = feed(fetch=counted, clock=clock)
    caplog.set_level("INFO", logger="analyzer.trade_news")
    first = advisor_sheet(trade, snap, FakeJev(), news)
    clock.t = 59 * 60
    second = advisor_sheet(trade, snap, FakeJev(), news)
    assert sorted(fetched) == sorted([COLLINS, TAYLOR])
    assert news_of(first) == news_of(second)
    assert f"News of player {TAYLOR} from the cache" in caplog.text
    clock.t = 61 * 60
    advisor_sheet(trade, snap, FakeJev(), news)
    assert fetched.count(TAYLOR) == 2


def blocked(request):
    raise httpx.ConnectError("the host of the news feed is blocked", request=request)


def test_a_failed_news_fetch_gives_a_read_with_no_news_fact(snap, trade):
    from league.provider.sleeper import fetch_news

    advisor = StubAdvisor(taylor_out)
    read = read_trade(trade, snap, jev=FakeJev(), news=feed(fetch=lambda pid: fetch_news(
        pid, transport=httpx.MockTransport(blocked))), call=advisor)
    assert read.lean == "Gut call"
    assert not any(fid.startswith("NEWS.") for fid in sheet_facts(advisor.calls[0][1]))


def test_a_fetch_that_raises_gives_no_news_and_is_tried_again(snap, trade):
    calls = []

    def broken(pid):
        calls.append(pid)
        raise RuntimeError("the feed changed its shape")

    news = feed(fetch=broken)
    assert news_of(advisor_sheet(trade, snap, FakeJev(), news)) == {}
    advisor_sheet(trade, snap, FakeJev(), news)
    assert calls.count(TAYLOR) == 2


NEWS_FACT = f"NEWS.{TAYLOR}.1"


def test_a_bullet_that_cites_news_and_names_no_report_retries_once(snap, trade):
    bare = {"text": "The Colts trade Jonathan Taylor to Denver.", "mark": "for", "fact_id": NEWS_FACT}
    named = bare | {"text": "Jonathan Taylor is reported as a fit in Denver."}
    advisor = StubAdvisor(lambda facts: taylor_out(facts, bare), lambda facts: taylor_out(facts, named))
    read = read_trade(trade, snap, jev=FakeJev(), news=feed(), call=advisor)
    assert len(advisor.calls) == 2
    assert f"roster 4 bullet 1: it cites the news fact {NEWS_FACT}" in advisor.calls[1][1]
    assert read.sides[0].bullets[0].text == named["text"]
    assert read.sides[0].bullets[0].fact_text.startswith("Reported on 2026-11-09 by Rotoballer:")


@pytest.mark.parametrize("text", [
    "Rotoballer says Jonathan Taylor could land in Denver.",
    "Per NFL Network, the Colts hear offers for Jonathan Taylor.",
    "According to one report, Denver wants Jonathan Taylor.",
    "A rumor puts Jonathan Taylor in Denver.",
])
def test_a_bullet_that_names_the_report_or_its_source_passes(snap, trade, text):
    bullet = {"text": text, "mark": "for", "fact_id": NEWS_FACT}
    advisor = StubAdvisor(lambda facts: taylor_out(facts, bullet))
    read_trade(trade, snap, jev=FakeJev(), news=feed(), call=advisor)
    assert len(advisor.calls) == 1


def test_the_jev_checks_ask_faithfulness_of_each_bullet_and_the_rumor_question_of_each_news_bullet(snap, trade,
                                                                                                  caplog):
    bullet = {"text": "Jonathan Taylor is reported as a fit in Denver.", "mark": "for", "fact_id": NEWS_FACT}
    jev = FakeJev(yes=0.2)
    caplog.set_level("INFO", logger="analyzer.read_jev_check")
    read = read_trade(trade, snap, jev=jev, news=feed(), call=StubAdvisor(lambda facts: taylor_out(facts, bullet)))
    assert read.lean == "Gut call"
    assert len(jev.requests) == 2
    questions = jev.requests[1].questions
    assert {f"faithful.4.{n}" for n in (1, 2, 3)} | {f"faithful.11.{n}" for n in (1, 2, 3)} | {"rumor.4.1"} == set(
        questions)
    rumor = questions["rumor.4.1"].instructions
    assert isinstance(rumor, dict) and rumor["bullet"] == bullet["text"]
    assert rumor["fact"].startswith("Reported on 2026-11-09 by Rotoballer:")
    assert "Jev checks of the read, log only" in caplog.text
    assert "rumor.4.1=0.2 no" in caplog.text and "faithful.11.3=0.2 no" in caplog.text


def test_a_failed_jev_check_logs_and_never_blocks_the_read(snap, trade, caplog):
    from league.jev_port import JevError

    read = read_trade(trade, snap, jev=FakeJev(error=JevError("timeout")), news=feed(),
                      call=StubAdvisor(taylor_out))
    assert read.lean == "Gut call"
    assert "The Jev checks of the read failed, so they log no answer: timeout" in caplog.text
