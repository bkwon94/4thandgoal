"""
Tests for the live eval of the Advisor: the test set, the trade of each entry as of its week, the saved reads, the
Finder presses, and the summary. They feed the week 6 fixtures to the eval with a stub Advisor, a stub Finder pick, and
FakeJev, so no test calls Claude or TypeSafe. The news feed is the recorded feed or no feed, so no test calls Sleeper.
The nflverse download answers from the fixtures or fails, so no test calls nflverse.
The test set of the tests names the teams of the fixtures through the snapshot, so no test file holds a team name.
"""
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import httpx
import pytest
from cpc import cli_root, cpc_client, four_week
from fakes import FakeJev, FakeWriter, no_news, recorded_news
from test_trade_news import NEWS_FACT, TAYLOR, feed, taylor_out

from analyzer.advisor import AdvisorOut
from analyzer.finder_pick import FinderPickOut
from analyzer.trade_news import NewsFeed
from cornerstone import advisor_eval, cli
from cornerstone.advisor_eval import (
    EvalSet,
    EvalTrade,
    FinderAsker,
    Meter,
    TradeNotFound,
    load_test_set,
    named_in_week,
    proposed_trade,
    roster_ids_by_name,
    rosters_before,
    run_eval,
    summary_lines,
)
from facts.writer import FINDER_PICK_MODEL, MODEL, call_cost
from league.jev_port import JevError
from league.paths import nfl_dir, nflverse_cache_dir
from league.provider.sleeper import load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
# Roster 4 gives Collins to roster 12 for Kincaid and Wilson, as the Advisor tests do. Roster 4 asks.
COLLINS, KINCAID, WILSON = "7569", "10236", "8146"


@pytest.fixture(autouse=True)
def no_live_news(monkeypatch):
    """The eval reads the live Sleeper feed by default. A test gives it a recorded feed, or this one with no item."""
    monkeypatch.setattr(advisor_eval, "live_news_feed", lambda: NewsFeed(fetch=no_news))


def no_network(url: str) -> bytes:
    raise httpx.ConnectError(f"no network in a test: {url}")


@pytest.fixture(autouse=True)
def no_nflverse_download(monkeypatch):
    """The command downloads the past season files and the team stats file. A test gives a fetch, or this one fails."""
    monkeypatch.setattr(cli, "http_get", no_network)


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT))


def entry(snap, **changes) -> dict:
    """One entry of the test set, as the file holds it: team names and player names, with fields the eval ignores."""
    names = {pid: snap.players[pid].name for pid in (COLLINS, KINCAID, WILSON)}
    base = {"id": 1, "week": 6, "asker": snap.teams[4].name, "other": snap.teams[12].name,
            "asker_gives": [names[COLLINS]], "asker_gets": [names[KINCAID], names[WILSON]],
            "summary": {"asker_team": "ignored"}, "claude": {"parsed": {"lean": "ignored"}}}
    return base | changes


def write_test_set(path: Path, *entries: dict, finder: list[dict] | None = None) -> Path:
    path.write_text(json.dumps({"meta": {}, "trades": list(entries), "finder": finder or []}))
    return path


def test_the_test_set_loads_each_trade_and_ignores_the_other_fields(snap, tmp_path):
    path = write_test_set(tmp_path / "set.json", entry(snap), entry(snap, id=2))
    trades = load_test_set(path).trades
    assert [t.id for t in trades] == [1, 2]
    assert trades[0] == EvalTrade(id=1, week=6, asker=snap.teams[4].name, other=snap.teams[12].name,
                                  asker_gives=["Nico Collins"], asker_gets=["Dalton Kincaid", "Garrett Wilson"])


def test_a_trade_resolves_to_roster_ids_and_player_ids_by_name(snap):
    trade = proposed_trade(EvalTrade(**{k: v for k, v in entry(snap).items() if k in EvalTrade.model_fields}), snap)
    assert trade.asker == 4
    assert [(side.roster_id, [p.player_id for p in side.gives]) for side in trade.sides] == [
        (4, [COLLINS]), (12, [KINCAID, WILSON])]
    assert all(p.to == (12 if side.roster_id == 4 else 4) for side in trade.sides for p in side.gives)


def test_a_player_name_matches_with_or_without_a_suffix_and_a_period(snap):
    # The test set holds "Brian Robinson Jr." where the saved raw data of an earlier week holds "Brian Robinson".
    trade = EvalTrade(**{k: v for k, v in entry(snap, asker_gives=["Nico Collins Jr."],
                                                asker_gets=["Dalton  Kincaid", "garrett wilson"]).items()
                         if k in EvalTrade.model_fields})
    assert [p.player_id for p in proposed_trade(trade, snap).sides[0].gives] == [COLLINS]
    assert [p.player_id for p in proposed_trade(trade, snap).sides[1].gives] == [KINCAID, WILSON]


def test_a_team_renamed_after_the_week_is_found_by_its_roster_id_from_the_latest_name(snap):
    # The test set holds the name a team has now. The saved week holds the name it had then.
    trade = EvalTrade(**{k: v for k, v in entry(snap, asker="Renamed Since").items() if k in EvalTrade.model_fields})
    with pytest.raises(TradeNotFound, match="Renamed Since"):
        proposed_trade(trade, snap)
    known = roster_ids_by_name([snap.model_copy(update={"teams": {
        **snap.teams, 4: snap.teams[4].model_copy(update={"name": "Renamed Since"})}})])
    assert known["Renamed Since"] == 4
    named = named_in_week(trade, snap, known)
    assert named.asker == snap.teams[4].name and named.other == trade.other
    assert proposed_trade(named, snap).asker == 4


@pytest.mark.parametrize("change, words", [
    ({"asker": "No Such Team"}, "No Such Team"),
    ({"asker_gives": ["Nobody Atall"]}, "Nobody Atall"),
])
def test_a_trade_with_an_unknown_team_or_player_names_it_in_the_error(snap, change, words):
    trade = EvalTrade(**{k: v for k, v in entry(snap, **change).items() if k in EvalTrade.model_fields})
    with pytest.raises(TradeNotFound, match=words):
        proposed_trade(trade, snap)


def test_rosters_of_a_trade_already_done_go_back_through_the_trades_of_the_week_newest_first(snap, fixture_raw_dir):
    # In week 6, roster 11 sent Wilson to roster 12, and roster 12 holds Kincaid after a later move. The newest trade of
    # the week is between rosters 7 and 8, so the walk back reverses two trades before the players sit with their givers.
    trade = EvalTrade(id=1, week=6, asker=snap.teams[11].name, other=snap.teams[12].name,
                      asker_gives=["Garrett Wilson"], asker_gets=["Dalton Kincaid"])
    with pytest.raises(TradeNotFound):
        proposed_trade(trade, snap)
    rosters, note = rosters_before(trade, snap, load_raw(fixture_raw_dir).transactions)
    assert note == "reversed 2 trade(s) of week 6 on file, newest first"
    assert WILSON in rosters[11] and WILSON not in rosters[12]
    before = snap.model_copy(update={"rosters": rosters})
    assert proposed_trade(trade, before).asker == 11


def test_rosters_before_a_trade_that_is_still_open_stay_as_they_are(snap, fixture_raw_dir):
    trade = EvalTrade(**{k: v for k, v in entry(snap).items() if k in EvalTrade.model_fields})
    rosters, note = rosters_before(trade, snap, load_raw(fixture_raw_dir).transactions)
    assert rosters == snap.rosters
    assert note is None


def test_rosters_before_name_the_trade_when_no_walk_back_puts_a_player_with_his_giver(snap, fixture_raw_dir):
    trade = EvalTrade(**{k: v for k, v in entry(snap, asker_gives=["Garrett Wilson"]).items()
                         if k in EvalTrade.model_fields})
    with pytest.raises(TradeNotFound, match="Garrett Wilson"):
        rosters_before(trade, snap, load_raw(fixture_raw_dir).transactions)


# The saved week of the fixture has no chart, so the Case says the chart is missing, as the guard needs.
CASE = ("If you believe Garrett Wilson keeps his role, this is worth it. You give up the best player in the deal. "
        "The other manager gets a clear upgrade. The chart of this week is missing. "
        "Push for it only if your receivers need the help.")


def good_out(facts, **changes) -> dict:
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
    """The Claude call of the Advisor: it answers each call with `build(facts)` and counts the calls it got."""

    def __init__(self, build=good_out):
        self.build = build
        self.calls = 0

    def __call__(self, system, user, output_model):
        self.calls += 1
        facts = dict(re.findall(r"^- (\S+): (.+)$", user, re.MULTILINE))
        return AdvisorOut.model_validate(self.build(facts))


class Weeks:
    """The snapshot of a week as the eval asks for it, with the count of asks per week."""

    def __init__(self, snap, fixture_raw_dir):
        self.snap, self.raw = snap, load_raw(fixture_raw_dir)
        self.asked: list[int] = []

    def __call__(self, week):
        self.asked.append(week)
        return self.snap, self.raw.transactions


@pytest.fixture
def weeks(snap, fixture_raw_dir):
    return Weeks(snap, fixture_raw_dir)


def trades_of(snap, *changes, finder: list[FinderAsker] | None = None) -> EvalSet:
    return EvalSet(trades=[EvalTrade(**{k: v for k, v in entry(snap, id=number, **change).items()
                                        if k in EvalTrade.model_fields})
                           for number, change in enumerate(changes, start=1)], finder=finder or [])


def read_file(out_dir: Path, number: int) -> dict:
    return json.loads((out_dir / f"trade-{number}.json").read_text())


def test_the_eval_saves_the_sheet_and_the_read_of_each_trade_and_a_summary(snap, weeks, tmp_path):
    out = tmp_path / "out"
    summary = run_eval(trades_of(snap, {}, {}), weeks, jev=FakeJev(), call=StubAdvisor(), out_dir=out, meter=Meter())
    saved = read_file(out, 1)
    assert saved["lean"] == "Gut call" and saved["case"] == CASE
    assert {"JEV.fair", "JEV.need.4", f"{COLLINS}.ppg"} <= set(saved["sheet"])
    first = saved["sides"][0]["bullets"][0]
    assert first["fact_id"] == f"{WILSON}.ppg" and first["fact_text"] == saved["sheet"][f"{WILSON}.ppg"]
    assert saved["check_failures"] == [] and saved["error"] is None
    assert json.loads((out / "summary.json").read_text()) == summary
    assert summary["leans"] == {"1": "Gut call", "2": "Gut call"}
    assert summary["errors"] == {} and summary["check_failures"] == 0 and summary["inner_word_hits"] == 0
    assert summary["seconds"] >= 0


def _usage(**tokens: int) -> Any:
    """A stand-in for the usage of a Claude response, with only the token counts that the cost reads."""
    return type("Usage", (), tokens)


def test_the_cost_adds_the_claude_usage_and_the_jev_tokens(snap, weeks, tmp_path):
    meter = Meter()
    # The usage of a real call of the prototype: it cost $0.0673.
    usage = _usage(input_tokens=8189, cache_read_input_tokens=1999, cache_creation_input_tokens=0, output_tokens=1707)
    meter.add_claude(usage)
    summary = run_eval(trades_of(snap, {}), weeks, jev=FakeJev(), call=StubAdvisor(), out_dir=tmp_path, meter=meter)
    assert call_cost(MODEL, usage) == pytest.approx(0.0673, abs=0.00005)
    assert summary["cost"]["claude"] == pytest.approx(0.0673, abs=0.00005)
    # The fake Jev reads 100 tokens per question at $0.042 per million: the 4 questions of the trade, then the
    # log-only faithfulness check of each of the 6 Bullets. No Bullet cites news, so no rumor check runs.
    assert summary["cost"]["jev"] == pytest.approx((4 + 6) * 100 * 0.042 / 1_000_000)
    assert summary["cost"]["total"] == pytest.approx(summary["cost"]["claude"] + summary["cost"]["jev"])


def test_the_eval_asks_for_the_snapshot_of_each_week_once(snap, weeks, tmp_path):
    run_eval(trades_of(snap, {}, {}, {}), weeks, jev=FakeJev(), call=StubAdvisor(), out_dir=tmp_path, meter=Meter(),
             workers=2)
    assert weeks.asked == [6]


def test_a_read_that_fails_its_guards_twice_is_an_error_and_the_other_trades_go_on(snap, weeks, tmp_path):
    def build(facts):
        out = good_out(facts)
        # The first trade uses the first two calls, so both of its attempts cite a fact that is not on the sheet.
        if advisor.calls <= 2:
            out["sides"][0]["bullets"][0]["fact_id"] = "NO.such"
        return out

    advisor = StubAdvisor(build)
    summary = run_eval(trades_of(snap, {}, {}), weeks, jev=FakeJev(), call=advisor, out_dir=tmp_path, meter=Meter())
    assert list(summary["errors"]) == ["1"]
    assert "no read that passed the guards" in summary["errors"]["1"]
    assert read_file(tmp_path, 1)["error"] == summary["errors"]["1"]
    assert read_file(tmp_path, 2)["error"] is None
    assert summary["leans"] == {"2": "Gut call"}


def test_a_trade_with_an_unknown_player_is_an_error_that_names_him(snap, weeks, tmp_path):
    summary = run_eval(trades_of(snap, {"asker_gives": ["Nobody Atall"]}, {}), weeks, jev=FakeJev(),
                       call=StubAdvisor(), out_dir=tmp_path, meter=Meter())
    assert "Nobody Atall" in summary["errors"]["1"]
    assert list(summary["leans"]) == ["2"]


def test_a_failed_jev_request_still_gives_a_read_with_no_jev_fact(snap, weeks, tmp_path):
    run_eval(trades_of(snap, {}), weeks, jev=FakeJev(error=JevError("down")), call=StubAdvisor(), out_dir=tmp_path,
             meter=Meter())
    assert not any(fid.startswith("JEV.") for fid in read_file(tmp_path, 1)["sheet"])


def test_the_summary_lines_give_the_leans_the_cost_and_the_time(snap, weeks, tmp_path):
    summary = run_eval(trades_of(snap, {}, {"asker_gives": ["Nobody Atall"]}), weeks, jev=FakeJev(),
                       call=StubAdvisor(), out_dir=tmp_path, meter=Meter())
    lines = summary_lines(summary)
    assert lines[0] == "2 trades: 1 read, 1 error."
    assert "Leans: Gut call 1." in lines
    assert any(line.startswith("Cost: $") and "Claude $" in line and "Jev $" in line for line in lines)
    assert any(line.startswith("Time: ") and line.endswith(" s.") for line in lines)
    assert any(line.startswith("trade 2: ") and "Nobody Atall" in line for line in lines)


def test_the_test_set_loads_each_finder_asker_and_ignores_the_saved_run(snap, tmp_path):
    path = write_test_set(tmp_path / "set.json", entry(snap),
                          finder=[{"asker": snap.teams[4].name, "weak": {}, "pick": {"parsed": None}}])
    assert load_test_set(path).finder == [FinderAsker(asker=snap.teams[4].name)]


class StubPick:
    """The Claude call of the Finder pick: it picks the first offer of the message with two Bullets that cite the first
    two facts of that offer and say no name and no number. It counts the calls it got."""

    def __init__(self):
        self.calls = 0

    def __call__(self, system, user, output_model):
        self.calls += 1
        first = user.split("\nOffer ")[1]
        offer_id = first.split("\n", 1)[0].strip()
        fact_ids = re.findall(r"^- (\S+): ", first, re.MULTILINE)
        bullets = [{"text": "This trade helps the asker.", "mark": "for", "fact_id": fact_ids[0]},
                   {"text": "The other side gets depth.", "mark": "even", "fact_id": fact_ids[1]}]
        return FinderPickOut.model_validate({"picks": [{"offer_id": offer_id, "lean": "Gut call",
                                                        "headline": "A swap that fits both teams.",
                                                        "bullets": bullets}], "none_line": None})


def test_the_eval_runs_the_finder_of_each_asker_on_the_newest_week_and_saves_the_picks(snap, weeks, tmp_path):
    picker = StubPick()
    summary = run_eval(trades_of(snap, {}, finder=[FinderAsker(asker=snap.teams[4].name)]), weeks, jev=FakeJev(),
                       call=StubAdvisor(), out_dir=tmp_path, meter=Meter(), finder_call=picker)
    saved = json.loads((tmp_path / "finder-1.json").read_text())
    assert saved["error"] is None and saved["week"] == 6 and saved["asker"] == snap.teams[4].name
    assert saved["offers"] > 0 and 0 < len(saved["shortlist"]) <= 10
    assert len(saved["picks"]) == 1 and saved["picks"][0]["offer_id"] == saved["shortlist"][0]["offer_id"]
    assert saved["picks"][0]["headline"] == "A swap that fits both teams."
    assert all(b["fact_text"] for b in saved["picks"][0]["bullets"])
    assert picker.calls == 1 and saved["claude_calls"] == 1
    # FakeJev reads 100 tokens per question, so the press has a Jev cost and no Claude cost from the stub.
    assert saved["cost"] > 0
    assert summary["finder"] == {"1": {"asker": snap.teams[4].name, "week": 6, "picks": 1, "fallback": False,
                                       "error": None, "cost": saved["cost"], "seconds": saved["seconds"]}}
    assert weeks.asked == [6]
    assert any(line.startswith("finder 1: 1 pick, $") for line in summary_lines(summary))


class ShortFirstPick(StubPick):
    """A Finder pick call whose first answer holds one Bullet, so the pick fails the count guard."""

    def __call__(self, system, user, output_model):
        out = super().__call__(system, user, output_model)
        if self.calls == 1:
            out.picks[0].bullets = out.picks[0].bullets[:1]
        return out


def test_the_eval_meters_the_repair_call_of_a_finder_pick(snap, weeks, tmp_path, monkeypatch):
    usage = _usage(input_tokens=1_000_000, cache_read_input_tokens=1_000_000, cache_creation_input_tokens=1_000_000,
                   output_tokens=1_000_000)
    repairs = []

    class UsageWriter:
        """A writer that keeps its usage hook, so the stub repair call reports its usage as the real writer does."""

        def __init__(self, on_usage):
            self.on_usage = on_usage

    def repair_call(system, user, output_model, *, writer):
        repairs.append(user)
        writer.on_usage(usage)
        return StubPick()(system, user, FinderPickOut).picks[0]

    monkeypatch.setattr(advisor_eval, "ClaudeWriter", UsageWriter)
    monkeypatch.setattr(advisor_eval, "finder_repair_call", repair_call)
    meter = Meter()
    run_eval(trades_of(snap, {}, finder=[FinderAsker(asker=snap.teams[4].name)]), weeks, jev=FakeJev(),
             call=StubAdvisor(), out_dir=tmp_path, meter=meter, finder_call=ShortFirstPick())
    saved = json.loads((tmp_path / "finder-1.json").read_text())
    assert len(repairs) == 1 and len(saved["picks"]) == 1 and saved["fallback"] is False
    # The pick call and the repair call are 2 Claude calls, and the repair costs the Sonnet prices.
    assert saved["claude_calls"] == 2
    assert meter.claude_usd == pytest.approx(call_cost(FINDER_PICK_MODEL, usage))
    assert saved["cost"] >= meter.claude_usd


def test_a_finder_asker_with_an_unknown_team_is_an_error_and_the_trades_still_read(snap, weeks, tmp_path):
    summary = run_eval(trades_of(snap, {}, finder=[FinderAsker(asker="No Such Team")]), weeks, jev=FakeJev(),
                       call=StubAdvisor(), out_dir=tmp_path, meter=Meter(), finder_call=StubPick())
    assert "No Such Team" in summary["finder"]["1"]["error"]
    assert summary["leans"] == {"1": "Gut call"}
    assert any(line.startswith("finder 1: error, ") for line in summary_lines(summary))


def test_the_finder_pick_costs_the_sonnet_prices():
    usage = _usage(input_tokens=1_000_000, cache_read_input_tokens=1_000_000, cache_creation_input_tokens=1_000_000,
                   output_tokens=1_000_000)
    meter = Meter()
    meter.add_claude(usage, model=FINDER_PICK_MODEL)
    assert call_cost(FINDER_PICK_MODEL, usage) == pytest.approx(2.0 + 0.10 + 4.0 + 10.0)
    assert meter.claude_usd == pytest.approx(16.10) and meter.claude_calls == 1
    assert call_cost(MODEL, usage) == pytest.approx(4.0 + 0.20 + 8.0 + 20.0)


def taylor_trade(snap) -> dict:
    """The entry of the news tests: roster 4 gives Nico Collins to roster 11 for Jonathan Taylor."""
    return entry(snap, other=snap.teams[11].name, asker_gives=["Nico Collins"], asker_gets=[snap.players[TAYLOR].name])


class CountedFeed:
    """The recorded news feed, with each player id it was asked for."""

    def __init__(self):
        self.asked: list[str] = []
        self.feed = feed(fetch=self.fetch)

    def fetch(self, player_id):
        self.asked.append(player_id)
        return recorded_news(player_id)


def test_a_trade_of_the_current_week_reads_the_live_feed_and_the_summary_lists_its_news_bullets(snap, weeks,
                                                                                                tmp_path):
    bullet = {"text": "Jonathan Taylor is reported as a fit in Denver.", "mark": "for", "fact_id": NEWS_FACT}
    news = CountedFeed()
    summary = run_eval(EvalSet(trades=[EvalTrade.model_validate(taylor_trade(snap))]), weeks, jev=FakeJev(),
                       call=StubAdvisor(lambda facts: taylor_out(facts, bullet)), out_dir=tmp_path, meter=Meter(),
                       news=news.feed)
    saved = read_file(tmp_path, 1)
    assert NEWS_FACT in saved["sheet"] and TAYLOR in news.asked
    assert summary["news_week"] == 6
    assert summary["news_bullets"] == [{"trade": 1, "text": bullet["text"], "fact_id": NEWS_FACT,
                                        "fact_text": saved["sheet"][NEWS_FACT]}]
    assert "News: week 6 reads the live feed, and 1 Bullet cites a NEWS fact." in summary_lines(summary)


def test_a_trade_of_an_older_week_reads_no_news(snap, weeks, tmp_path):
    news = CountedFeed()
    summary = run_eval(EvalSet(trades=[EvalTrade.model_validate(taylor_trade(snap))]), weeks, jev=FakeJev(),
                       call=StubAdvisor(lambda facts: taylor_out(facts)), out_dir=tmp_path, meter=Meter(),
                       news=news.feed, current_week=7)
    assert not any(fid.startswith("NEWS.") for fid in read_file(tmp_path, 1)["sheet"])
    assert news.asked == [] and summary["news_bullets"] == []


def test_the_finder_askers_read_the_live_feed_of_the_current_week(snap, weeks, tmp_path):
    news = CountedFeed()
    run_eval(EvalSet(trades=[], finder=[FinderAsker(asker=snap.teams[4].name)]), weeks, jev=FakeJev(),
             call=StubAdvisor(), out_dir=tmp_path, meter=Meter(), finder_call=StubPick(), news=news.feed,
             current_week=6)
    shortlist = json.loads((tmp_path / "finder-1.json").read_text())["shortlist"]
    assert shortlist and news.asked
    assert weeks.asked == [6]


def _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch) -> Path:
    """A repo folder in tmp_path with the week 6 raw data and history. The folder beside it is outside the repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    cli_root(repo)
    shutil.copytree(fixture_raw_dir, repo / "clients" / "cpc" / "data" / "2026" / "week-06" / "raw")
    shutil.copytree(fixture_history_root, repo / "clients" / "cpc" / "data" / "2026" / "history")
    # The Advisor reads the Playbook of the client, so the repo folder needs one.
    playbook = repo / "clients" / "cpc" / "prompts" / "playbook.md"
    playbook.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(CLIENT.voice_dir / "playbook.md", playbook)
    monkeypatch.chdir(repo)
    return repo


def _eval_args(snap, tmp_path, out: Path) -> list[str]:
    path = write_test_set(tmp_path / "set.json", entry(snap), entry(snap, id=2))
    return ["advisor-eval", "--client", "cpc", "--season", "2026", "--test-set", str(path), "--out", str(out),
            "--workers", "1"]


def test_the_command_reads_the_test_set_from_the_saved_weeks_and_prints_the_summary(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    out = tmp_path / "out"
    writer = FakeWriter([AdvisorOut.model_validate(good_out({})), AdvisorOut.model_validate(good_out({}))])

    code = cli.main(_eval_args(snap, tmp_path, out), writer=writer, jev=FakeJev())

    text = capsys.readouterr().out
    assert code == 0
    assert "2 trades: 2 reads, 0 errors." in text and "Leans: Gut call 2." in text
    assert "Cost: $" in text and "Time: " in text
    assert (out / "trade-1.json").exists() and (out / "summary.json").exists()
    assert len(writer.calls) == 2


def test_the_command_exits_with_one_when_a_trade_fails(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    # No answer is left for the Advisor, so both attempts of each trade fail.
    code = cli.main(_eval_args(snap, tmp_path, tmp_path / "out"), writer=FakeWriter(), jev=FakeJev())
    assert code == 1
    assert "2 trades: 0 reads, 2 errors." in capsys.readouterr().out


def test_the_command_refuses_an_output_folder_in_the_repo_that_git_does_not_ignore(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    repo = _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    writer = FakeWriter()

    code = cli.main(_eval_args(snap, tmp_path, repo / "eval-out"), writer=writer, jev=FakeJev())

    assert code == 2
    assert "names league managers" in capsys.readouterr().out
    assert not (repo / "eval-out").exists() and writer.calls == []


def test_the_command_writes_to_an_output_folder_in_the_repo_that_git_ignores(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    repo = _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / ".gitignore").write_text("eval-out/\n")
    writer = FakeWriter([AdvisorOut.model_validate(good_out({})), AdvisorOut.model_validate(good_out({}))])

    code = cli.main(_eval_args(snap, tmp_path, repo / "eval-out"), writer=writer, jev=FakeJev())

    assert code == 0
    assert (repo / "eval-out" / "summary.json").exists()


def test_the_command_names_a_week_with_no_saved_raw_data(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    path = write_test_set(tmp_path / "set.json", entry(snap, week=9))
    code = cli.main(["advisor-eval", "--client", "cpc", "--season", "2026", "--test-set", str(path), "--out",
                     str(tmp_path / "out")], writer=FakeWriter(), jev=FakeJev())
    assert code == 2
    assert "week 9" in capsys.readouterr().out


PAST = Path(__file__).parent / "fixtures" / "nflverse_past"
COLLINS_GSIS = "00-0036554"


def _fresh_cache(repo: Path, fixture_nflverse_dir: Path) -> Path:
    """The nflverse cache of the repo with the week files of the build and no past season file and no team stats file.

    The id map gets a row for Collins, so his past season rows match him, as the full id map of a real cache does.
    The schedules file holds the games of both fixtures with every column of the past slice, as a real one does.
    """
    cache = nflverse_cache_dir(nfl_dir(repo))
    shutil.copytree(fixture_nflverse_dir, cache)
    (cache / "stats_team_week_2026.csv.gz").unlink()
    with (PAST / "games.csv").open(newline="") as past, (fixture_nflverse_dir / "games.csv").open(newline="") as now:
        past_rows, now_rows = csv.DictReader(past), list(csv.DictReader(now))
        columns = list(past_rows.fieldnames or [])
        rows = [*past_rows, *now_rows]
    with (cache / "games.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, columns, restval="")
        writer.writeheader()
        writer.writerows(rows)
    ids = cache / "db_playerids.csv"
    fields = ids.read_text().splitlines()[0].split(",")
    row = {"gsis_id": COLLINS_GSIS, "sleeper_id": COLLINS, "name": "Nico Collins", "merge_name": "nico collins",
           "position": "WR", "team": "HOU"}
    with ids.open("a") as f:
        f.write(",".join(row.get(field, "NA") for field in fields) + "\n")
    return cache


def _serve_fixtures(fixture_nflverse_dir: Path, asked: list[str]):
    """A download that answers from the past season slice and the week fixtures, and keeps each URL it was asked for."""
    def fetch(url: str) -> bytes:
        asked.append(url)
        name = url.rsplit("/", 1)[-1]
        return ((PAST / name) if (PAST / name).exists() else (fixture_nflverse_dir / name)).read_bytes()
    return fetch


def test_the_command_downloads_the_sources_of_a_press_so_the_sheet_has_history_and_nfl_team_facts(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    repo = _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    _fresh_cache(repo, fixture_nflverse_dir)
    asked: list[str] = []
    monkeypatch.setattr(cli, "http_get", _serve_fixtures(fixture_nflverse_dir, asked))
    writer = FakeWriter([AdvisorOut.model_validate(good_out({})), AdvisorOut.model_validate(good_out({}))])

    code = cli.main(_eval_args(snap, tmp_path, tmp_path / "out"), writer=writer, jev=FakeJev())

    assert code == 0
    sheet = read_file(tmp_path / "out", 1)["sheet"]
    assert f"{COLLINS}.history" in sheet
    assert any(fid.endswith(".nfl_team") for fid in sheet)
    assert sorted(url.rsplit("/", 1)[-1] for url in asked) == [
        "stats_player_week_2023.csv.gz", "stats_player_week_2024.csv.gz", "stats_player_week_2025.csv.gz",
        "stats_team_week_2026.csv.gz"]


def test_a_failed_download_gives_no_history_or_nfl_team_fact_and_a_printed_line(
        snap, tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    repo = _eval_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    _fresh_cache(repo, fixture_nflverse_dir)
    writer = FakeWriter([AdvisorOut.model_validate(good_out({})), AdvisorOut.model_validate(good_out({}))])

    code = cli.main(_eval_args(snap, tmp_path, tmp_path / "out"), writer=writer, jev=FakeJev())

    assert code == 0
    sheet = read_file(tmp_path / "out", 1)["sheet"]
    assert not any(fid.endswith((".history", ".nfl_team")) for fid in sheet)
    text = capsys.readouterr().out
    assert "past season file of 2023" in text and "team stats file of 2026" in text
