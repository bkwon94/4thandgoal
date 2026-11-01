"""
Tests for the build, rewrite, and publish pipeline.
They use recorded fixtures, a fake writer, and a fake avatar downloader, so no network call runs.
"""
import gzip
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from cornerstone.config import cornerstone_config
from cornerstone.history import HISTORY_FILES, load_saved_weeks
from cornerstone.paths import history_dir, history_root, week_dir
from cornerstone.models import History
from cornerstone.parse import parse_week
from pathlib import Path

from cornerstone.models import (
    Blurb, NflverseWeek, ResearchClaim, ResearchOut, Sentence, Verdict, VerifyOut,
)
from cornerstone.nflverse import nflverse_week
from cornerstone.power_rankings import power_rankings
from cornerstone.pipeline import (
    BuildStopped, _nflverse_for_week, _rankings_chapter, _write_managers, _write_rankings, make_bundle, read_verify,
    run_build, run_page_json, run_rankings, run_rewrite,
)
from cornerstone.publish import PublishError, run_publish
from cornerstone.render import RANKINGS_ODDS_KEYS
from cornerstone.sleeper import load_raw
from cornerstone.sheet import read_bundle
from cornerstone.writer import WriterError
from fakes import fixture_nflverse, no_claims, no_network, no_news

ET = ZoneInfo("America/New_York")
# The league config the builds and fetches of these tests read.
CONFIG = cornerstone_config()


def _fake(system, user, model):
    if model.__name__ == "VerifyOut":
        return VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.M).group(1)
    return model(sentences=[Sentence(text="Fact sentence.", fact_ids=[fid])] * 2)


def _no_bytes(url):
    return None


NFLVERSE_FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"
NFLVERSE_KEYS = ("nflverse_pbp", "nflverse_ftn", "nflverse_injuries", "ffverse", "nflverse_snaps", "ffopportunity",
                 "nflverse_stats_player")


def _no_bytes_nflverse(url):
    raise httpx.ConnectError("down")


def _down_nflverse(season, week, player_ids, players, teams, scoring):
    return NflverseWeek(sources={k: False for k in NFLVERSE_KEYS}, gsis={}, drops=None, injuries=None)


def _forbidden_nflverse(season, week, player_ids, players, teams, scoring):
    raise AssertionError("the saved extract must not be fetched again")


@pytest.fixture
def offline(tmp_path_factory):
    """The build inputs with no network call. The nflverse cache sits outside the test repo, so no build reads it."""
    return {"news": no_news, "fetch_bytes": _no_bytes,
            "nflverse": fixture_nflverse(tmp_path_factory.mktemp("nflverse")), "research": no_claims}


def _ordinal(n):
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _repo(tmp_path, fixture_raw_dir):
    raw = week_dir(tmp_path, 2026, 6) / "raw"
    shutil.copytree(fixture_raw_dir, raw)
    return tmp_path


def test_build_from_disk_writes_everything(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert page == repo / "site" / "2026" / "week-06" / "page.json"
    for f in ("facts.json", "blurbs.json", "verify.json"):
        assert (week_dir(repo, 2026, 6) / f).exists()
    assert not (repo / "site" / "index.html").exists()
    assert not (repo / "site" / "static").exists()
    sources = read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources
    assert "chart" not in sources


def test_an_old_verify_file_with_a_chart_flag_still_reads(tmp_path):
    path = tmp_path / "verify.json"
    path.write_text('{"build": {"started": "2026-10-20T11:58:00-04:00", "sources": {"history": true, "chart": true},'
                    ' "fetched": "2026-10-20T11:56:00-04:00"}, "chapters": {"median": []}}')
    verify = read_verify(path)
    assert verify.build.sources == {"history": True, "chart": True}
    assert verify.chapters == {"median": []}


def _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo(tmp_path, fixture_raw_dir)
    shutil.copytree(fixture_history_root, history_root(repo, 2026))
    return repo


def test_build_records_the_history_source(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    record = read_verify(week_dir(repo, 2026, 6) / "verify.json").build
    assert record.sources["history"] is True


def test_build_without_history_degrades(tmp_path, fixture_raw_dir, caplog, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources["history"] is False
    assert "history incomplete" in caplog.text


def test_build_saves_the_week_to_history(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    out = history_dir(repo, 2026, 6)
    assert {p.stem for p in out.glob("*.json")} == {*HISTORY_FILES, "injuries"}
    injuries = json.loads((out / "injuries.json").read_text())
    assert injuries["2216"] == "Out"  # Mike Evans
    assert injuries["5859"] == "Questionable"  # A.J. Brown


def _rankings(repo):
    return repo / "site" / "2026" / "rankings.json"


def test_build_writes_the_rankings_file_after_the_page(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert page.exists()
    built = _rankings(repo).read_text(encoding="utf-8")
    data = json.loads(built)
    assert [w["week"] for w in data["weeks"]] == [1, 2, 3, 4, 5, 6]
    # The plain fake gives the rankings chapter no roster tags, so it falls back. The fallback leaves the
    # blurbs empty on purpose, so both files match.
    # The rankings command writes the same file from the same saved history.
    assert run_rankings(repo, 2026, 6, _fake).read_text(encoding="utf-8") == built


def _managers(repo):
    return repo / "site" / "2026" / "managers.json"


def test_build_writes_the_managers_file_after_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root,
                                                               offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    built = _managers(repo).read_text(encoding="utf-8")
    data = json.loads(built)
    assert data["schema_version"] == 1
    assert data["season"] == 2026
    assert data["through"] == 6
    assert [m["roster_id"] for m in data["managers"]] == list(range(1, 13))
    # The moves hold every week, newest first, and the raw players file names the players.
    assert all([w["week"] for w in m["moves"]["weeks"]] == [6, 5, 4, 3, 2, 1] for m in data["managers"])
    adds = [a for m in data["managers"] for w in m["moves"]["weeks"] for a in w["adds"]]
    assert adds
    assert any(a["name"] != a["player_id"] for a in adds)
    # The raw league file of the week gives the roster slots, so every entry carries bench points.
    assert all(m["bench"] is not None and len(m["weeks"]) == 6 for m in data["managers"])
    # Only week 6 has a report, so the shelf counts the shelf awards of its facts file.
    facts = json.loads((repo / "data" / "2026" / "week-06" / "facts.json").read_text(encoding="utf-8"))
    shelf = [a for a in facts["data"]["awards"] if a["key"] != "overachiever"]
    assert sum(sum(m["awards"].values()) for m in data["managers"]) == len(shelf)
    # The rankings command writes the same file from the same saved history.
    _managers(repo).unlink()
    run_rankings(repo, 2026, 6, _fake)
    assert _managers(repo).read_text(encoding="utf-8") == built


def test_a_thin_history_writes_no_managers_file(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo(tmp_path, fixture_raw_dir)
    # One saved week is under the two the file needs.
    shutil.copytree(fixture_history_root / "week-01", history_root(repo, 2026) / "week-01")
    teams = parse_week(load_raw(fixture_raw_dir)).teams
    caplog.set_level(logging.INFO, logger="cornerstone.pipeline")
    assert _write_managers(repo, 2026, 1, teams) is None
    assert not _managers(repo).exists()
    lines = [r for r in caplog.records if r.name == "cornerstone.pipeline" and "managers.json" in r.getMessage()]
    assert len(lines) == 1


def test_build_puts_the_odds_of_the_week_in_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    # The odds come from the saved facts of the build, so the file and the facts agree.
    odds = read_bundle(week_dir(repo, 2026, 6) / "facts.json").odds
    for row in data["weeks"][-1]["rows"]:
        t = odds.teams[row["roster_id"]]
        assert row["odds"] == {k: getattr(t, k) for k in RANKINGS_ODDS_KEYS}
    assert all("odds" not in row for w in data["weeks"][:-1] for row in w["rows"])


def test_a_rewrite_puts_the_saved_odds_in_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    # With no rankings file, the odds can come only from the saved facts.
    _rankings(repo).unlink()
    run_rewrite(repo, 2026, 6, "rankings", _fake)
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    odds = read_bundle(week_dir(repo, 2026, 6) / "facts.json").odds
    assert odds is not None
    for row in data["weeks"][-1]["rows"]:
        assert row["odds"] == {k: getattr(odds.teams[row["roster_id"]], k) for k in RANKINGS_ODDS_KEYS}


def test_an_older_week_never_shrinks_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root, caplog,
                                                       offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    # The build saves week 6, so the history runs through week 6.
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    teams = read_bundle(week_dir(repo, 2026, 6) / "facts.json").data.teams
    caplog.set_level(logging.INFO, logger="cornerstone.pipeline")
    out = _write_rankings(repo, 2026, 5, teams)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [w["week"] for w in data["weeks"]] == [1, 2, 3, 4, 5, 6]
    assert "covers weeks 1 to 6, past the built week 5" in caplog.text


def test_incomplete_history_skips_the_rankings_file_and_the_page_builds(tmp_path, fixture_raw_dir, caplog, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert page.exists()
    assert not _rankings(repo).exists()
    assert not _managers(repo).exists()
    assert "history incomplete" in caplog.text


def test_rankings_command_writes_the_file_for_a_saved_week(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    _rankings(repo).unlink()
    run_page_json(repo, 2026, 6)
    # The page-json command leaves the season file alone.
    assert not _rankings(repo).exists()
    out = run_rankings(repo, 2026, 6, _fake)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [w["week"] for w in data["weeks"]] == [1, 2, 3, 4, 5, 6]
    # The plain fake falls back on the rankings chapter. The fallback leaves the blurbs empty on purpose.
    assert all(row["blurb"] == [] for w in data["weeks"] for row in w["rows"])


class _RankingsWriter:
    """A fake Claude that writes one tagged sentence per PR fact, and counts the writer calls.
    Each sentence also cites its team's required facts, so the code check passes."""

    def __init__(self):
        self.writer_calls = 0

    def __call__(self, system, user, model):
        if model.__name__ == "VerifyOut":
            count = len(re.findall(r"^\d+\. ", user, re.M))
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(count)])
        self.writer_calls += 1
        found = re.findall(r"^- (PR\.(\d+)): (.*)$", user, re.M)
        listed = re.search(r"^Cite each of these facts in its team's sentences: (.*)\.$", user, re.MULTILINE)
        required = listed.group(1).split(", ") if listed else []
        return model(sentences=[
            Sentence(text=text, fact_ids=[fid, *(r for r in required if r.split(".")[1] == rid)], roster_id=int(rid))
            for fid, rid, text in found
        ])


def test_rankings_command_writes_twelve_blurbs_with_one_call(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    # A saved week with no rankings chapter has no PR facts.
    facts = week_dir(repo, 2026, 6) / "facts.json"
    bundle = read_bundle(facts)
    bundle.sheet.facts = {fid: f for fid, f in bundle.sheet.facts.items() if not fid.startswith("PR.")}
    bundle.sheet.chapters = [c for c in bundle.sheet.chapters if c.key != "rankings"]
    facts.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")

    call = _RankingsWriter()
    data = json.loads(run_rankings(repo, 2026, 6, call).read_text(encoding="utf-8"))
    assert call.writer_calls == 1
    week6 = next(w for w in data["weeks"] if w["week"] == 6)
    assert all(len(row["blurb"]) == 1 for row in week6["rows"])
    assert all(row["blurb"] == [] for w in data["weeks"] if w["week"] != 6 for row in w["rows"])
    blurbs = json.loads((week_dir(repo, 2026, 6) / "blurbs.json").read_text(encoding="utf-8"))
    assert blurbs["rankings"]["fallback"] is False
    assert "rankings" in read_verify(week_dir(repo, 2026, 6) / "verify.json").chapters
    # The saved facts take in the PR facts the blurb cites.
    assert "rankings" in [c.key for c in read_bundle(facts).sheet.chapters]


def test_rankings_command_adds_the_rank_why_facts_to_an_older_saved_chapter(
    tmp_path, fixture_raw_dir, fixture_history_root, offline,
):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    # A week saved before the rank why facts has a rankings chapter with no .why ids.
    facts = week_dir(repo, 2026, 6) / "facts.json"
    bundle = read_bundle(facts)
    bundle.sheet.facts = {fid: f for fid, f in bundle.sheet.facts.items() if not fid.endswith(".why")}
    for c in bundle.sheet.chapters:
        c.fact_ids = [fid for fid in c.fact_ids if not fid.endswith(".why")]
    facts.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")

    run_rankings(repo, 2026, 6, _fake)
    saved = read_bundle(facts)
    chapter = next(c for c in saved.sheet.chapters if c.key == "rankings")
    assert [c.key for c in saved.sheet.chapters].count("rankings") == 1
    for rid in saved.data.teams:
        assert f"PR.{rid}.why" in chapter.fact_ids
        assert f"PR.{rid}.why" in saved.sheet.facts
    # The saved facts hold no odds why, and the raw week is not read, so the chapter lists none.
    assert not any(fid.startswith("ODDS.") and fid.endswith(".why") for fid in chapter.fact_ids)


def test_rankings_command_lists_the_saved_odds_why_facts_in_an_older_saved_chapter(
    tmp_path, fixture_raw_dir, fixture_history_root, offline,
):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    # The saved facts hold the odds why, but the saved chapter lists only the rank why.
    facts = week_dir(repo, 2026, 6) / "facts.json"
    bundle = read_bundle(facts)
    for c in bundle.sheet.chapters:
        c.fact_ids = [fid for fid in c.fact_ids if not (fid.startswith("ODDS.") and fid.endswith(".why"))]
    facts.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")

    run_rankings(repo, 2026, 6, _fake)
    chapter = next(c for c in read_bundle(facts).sheet.chapters if c.key == "rankings")
    for rid in bundle.data.teams:
        assert f"ODDS.{rid}.why" in chapter.fact_ids
        assert f"PR.{rid}.why" in chapter.fact_ids


def test_a_saved_pr_fact_with_an_old_rank_is_rebuilt_from_the_history_and_the_rules(
    tmp_path, fixture_raw_dir, fixture_history_root, offline,
):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    bundle = read_bundle(week_dir(repo, 2026, 6) / "facts.json")
    history = History(week=6, weeks=load_saved_weeks(history_root(repo, 2026), 6))
    rows = power_rankings(history, 6)[6]
    row = rows[0]
    fresh = bundle.sheet.facts[f"PR.{row.roster_id}"]
    # An earlier build ranked the team under other rules, so the saved fact names another rank.
    old_rank = "99th"
    current = f"is {_ordinal(row.power_rank)} in"
    stale = fresh.model_copy(update={"text": fresh.text.replace(current, f"is {old_rank} in")})
    assert stale.text != fresh.text
    bundle.sheet.facts[stale.id] = stale

    _rankings_chapter(bundle, history)
    assert bundle.sheet.facts[stale.id].text == fresh.text
    assert f"is {_ordinal(row.power_rank)} in the power rankings" in bundle.sheet.facts[stale.id].text


def test_build_writes_the_rankings_blurb_into_the_file(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)

    def call(system, user, model):
        # The rankings chapter gets tagged sentences. Every other chapter gets the plain fake.
        fake = _RankingsWriter() if "Chapter: Power rankings" in user else _fake
        return fake(system, user, model)

    run_build(repo, 2026, 6, call, fetch=False, **offline, config=CONFIG)
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    week6 = next(w for w in data["weeks"] if w["week"] == 6)
    assert all(len(row["blurb"]) == 1 for row in week6["rows"])


def _week6_blurbs(repo):
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    return {row["roster_id"]: row["blurb"] for w in data["weeks"] if w["week"] == 6 for row in w["rows"]}


def test_a_fallback_rankings_blurb_keeps_the_saved_blurbs(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    run_rankings(repo, 2026, 6, _RankingsWriter())
    saved = _week6_blurbs(repo)
    assert all(len(b) == 1 for b in saved.values())
    # The plain fake gives no roster tags, so the blurb falls back and must not wipe the saved blurbs.
    run_rankings(repo, 2026, 6, _fake)
    blurbs = json.loads((week_dir(repo, 2026, 6) / "blurbs.json").read_text(encoding="utf-8"))
    assert blurbs["rankings"]["fallback"] is True
    assert _week6_blurbs(repo) == saved


def test_a_rankings_rewrite_reaches_the_season_file(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    # The plain fake falls back, so the build leaves the blurbs empty.
    assert all(b == [] for b in _week6_blurbs(repo).values())
    run_rewrite(repo, 2026, 6, "rankings", _RankingsWriter(), **offline)
    blurbs = _week6_blurbs(repo)
    assert len(blurbs) == 12
    chapter = next(c for c in read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.chapters if c.key == "rankings")
    for rid, sentences in blurbs.items():
        required = [fid for fid in chapter.required if fid.split(".")[1] == str(rid)]
        assert [s["fact_ids"] for s in sentences] == [[f"PR.{rid}", *required]]


def test_a_rewrite_reads_the_saved_odds_and_never_runs_the_engine(tmp_path, fixture_raw_dir, fixture_history_root,
                                                                  monkeypatch, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    saved = read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.facts
    odds = {fid: f for fid, f in saved.items() if fid.startswith(("ODDS.", "SW."))}
    # 12 odds facts, 12 odds why facts, and 2 swing facts.
    assert len(odds) == 26

    def no_engine(*args, **kwargs):
        raise AssertionError("a rewrite ran the odds engine")

    monkeypatch.setattr("cornerstone.sheet.playoff_odds", no_engine)
    run_rewrite(repo, 2026, 6, "next_week", _fake, **offline)
    after = read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.facts
    assert {fid: after[fid] for fid in odds} == odds


def _waiver(repo):
    return json.loads((repo / "site" / "2026" / "week-06" / "waiver.json").read_text())


def test_build_writes_the_waiver_file_beside_the_page(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    body = _waiver(repo)
    assert body["schema_version"] == 1
    assert body["week"] == 6
    assert datetime.fromisoformat(body["built"]).tzinfo is not None
    # The fixture rosters every player in its players file, so the pool is empty and no drop has a better pool
    # player. It has no trending file.
    assert body["buckets"] == {"best_adds": [], "trending": [], "sneaky": [], "stashes": [], "drops": []}
    assert len(body["budgets"]) == 12
    assert body["budgets"][0] == {"roster_id": 1, "budget_left": 69, "waiver_order": 1}


def test_a_rewrite_reads_the_saved_board_and_never_runs_the_waiver_engine(tmp_path, fixture_raw_dir, monkeypatch,
                                                                          offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    built = _waiver(repo)
    (repo / "site" / "2026" / "week-06" / "waiver.json").unlink()

    def no_engine(*args, **kwargs):
        raise AssertionError("a rewrite ran the waiver engine")

    monkeypatch.setattr("cornerstone.pipeline.waiver_board", no_engine)
    run_rewrite(repo, 2026, 6, "next_week", _fake, **offline)
    assert _waiver(repo) == built


def _repo_with_free_agent(tmp_path, fixture_raw_dir):
    """The week 6 repo with one free agent WR, so the pool and the best adds bucket hold one player."""
    repo = _repo(tmp_path, fixture_raw_dir)
    raw = week_dir(repo, 2026, 6) / "raw"
    players = json.loads((raw / "players.json").read_text())
    players["80001"] = {"position": "WR", "team": "LV", "status": "Active", "active": True, "full_name": "Free Agent"}
    (raw / "players.json").write_text(json.dumps(players))
    ahead = json.loads((raw / "projections_ahead.json").read_text())
    for entry in ahead:
        entry["projections"]["80001"] = 8.0
    (raw / "projections_ahead.json").write_text(json.dumps(ahead))
    return repo


def _one_claim(asked):
    def call(system, user):
        asked.append(user)
        return ResearchOut(claims=[ResearchClaim(
            text="He is the WR2 now.", url="https://sports.yahoo.com/fantasy/article/x-141451458.html",
            source="Yahoo Fantasy", date="2026-10-20", stance="news")])
    return call


def test_the_build_researches_once_and_a_rewrite_reads_the_saved_claims(tmp_path, fixture_raw_dir, offline):
    repo = _repo_with_free_agent(tmp_path, fixture_raw_dir)
    asked = []
    run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "research": _one_claim(asked)}, config=CONFIG)
    assert len(asked) == 1 and "Free Agent" in asked[0]
    player = _waiver(repo)["buckets"]["best_adds"][0]
    assert [c["text"] for c in player["research"]] == ["He is the WR2 now."]
    saved = read_bundle(week_dir(repo, 2026, 6) / "facts.json").waiver.buckets["best_adds"][0]
    assert "WV.research.80001.1" in {f.id for f in saved.facts}
    built = _waiver(repo)

    def no_search(system, user):
        raise AssertionError("a rewrite ran the search")

    run_rewrite(repo, 2026, 6, "next_week", _fake, **{**offline, "research": no_search})
    assert _waiver(repo) == built


def test_a_search_failure_for_every_player_flags_the_missing_experts_and_the_build_completes(
        tmp_path, fixture_raw_dir, offline):
    repo = _repo_with_free_agent(tmp_path, fixture_raw_dir)

    def down(system, user):
        raise WriterError("no parsed output")

    page = run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "research": down}, config=CONFIG)
    assert page.exists()
    body = _waiver(repo)
    assert body["experts_missing"] is True
    assert body["buckets"]["best_adds"][0]["research"] == []


def test_rankings_command_stops_on_an_incomplete_history(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    with pytest.raises(BuildStopped, match="history"):
        run_rankings(repo, 2026, 6, _fake)


def test_build_survives_a_history_save_failure(tmp_path, fixture_raw_dir, caplog, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    # A file in place of the history directory makes the save fail.
    root = history_root(repo, 2026)
    root.parent.mkdir(parents=True, exist_ok=True)
    root.write_text("not a directory")
    page = run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert page.exists()
    assert "week 6 not saved to history" in caplog.text


def test_rewrite_reads_the_version_1_verify_shape(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    path = week_dir(repo, 2026, 6) / "verify.json"
    chapters = json.loads(path.read_text())["chapters"]
    path.write_text(json.dumps(chapters))
    assert read_verify(path).build is None

    run_rewrite(repo, 2026, 6, "median", _fake, **offline)

    assert read_verify(path).build is None
    assert set(read_verify(path).chapters) == set(chapters)


def test_rewrite_keeps_the_build_record(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    path = week_dir(repo, 2026, 6) / "verify.json"
    before = read_verify(path).build
    run_rewrite(repo, 2026, 6, "median", _fake, **offline)
    assert read_verify(path).build == before


def test_build_stops_on_unscored_week(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    shutil.copytree(week_dir(repo, 2026, 6) / "raw", week_dir(repo, 2026, 7) / "raw")
    with pytest.raises(BuildStopped, match="not final"):
        run_build(repo, 2026, 7, _fake, fetch=False, **offline, config=CONFIG)


def test_build_stops_without_raw_data(tmp_path, offline):
    with pytest.raises(BuildStopped, match="No raw data for week 6"):
        run_build(tmp_path, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)


def test_rewrite_one_chapter(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    path = week_dir(repo, 2026, 6) / "blurbs.json"
    before = json.loads(path.read_text())

    # The build fake gives one verdict for two sentences, so every built blurb is the template.
    # This fake passes both sentences, so the rewrite keeps the text it wrote.
    def rewrite_fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(2)])
        fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.M).group(1)
        return model(sentences=[Sentence(text="Rewritten median sentence.", fact_ids=[fid])] * 2)

    page = run_rewrite(repo, 2026, 6, "median", rewrite_fake, **offline)
    after = json.loads(path.read_text())
    assert set(before) == set(after)
    text = [s["text"] for s in after["median"]["sentences"]]
    assert text != [s["text"] for s in before["median"]["sentences"]]
    assert text == ["Rewritten median sentence."] * 2
    assert after["recap_4"] == before["recap_4"]
    assert "Rewritten median sentence." in page.read_text()


def test_rewrite_unknown_chapter_lists_valid_keys(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    with pytest.raises(ValueError, match="median"):
        run_rewrite(repo, 2026, 6, "nope", _fake, **offline)


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def _init(path):
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")


def test_publish_copies_site_only(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    shutil.copytree(fixture_history_root, history_root(repo, 2026))
    (repo / "src").mkdir()
    (repo / "src" / "code.py").write_text("x = 1\n")
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)

    url = run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    assert url.endswith("2026/week-06/")
    files = _git(site_repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert "public/2026/week-06/page.json" in files
    assert "public/2026/rankings.json" in files
    assert "public/2026/managers.json" in files
    assert "public/2026/week-06/waiver.json" in files
    assert "public/2026/week-06/index.html" not in files
    assert not any(f.startswith("src/") for f in files)
    assert not any(f.startswith("public/static/") for f in files)
    assert "public/index.html" not in files
    assert not (site_repo / "2026").exists()
    assert not (site_repo / "index.html").exists()
    assert not (site_repo / "static").exists()
    assert _git(repo, "log", "-1", "--format=%s").strip() == "Week 6 report"


def test_publish_leaves_unpublished_weeks_out(tmp_path, fixture_raw_dir, monkeypatch, caplog, offline):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    # The fixture is scored through week 6, so week 7 builds only with the gate open.
    monkeypatch.setattr("cornerstone.pipeline.check_week_is_buildable", lambda *args: None)
    for week in (6, 7):
        shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, week) / "raw")
        run_build(repo, 2026, week, _fake, fetch=False, **offline, config=CONFIG)
    assert (repo / "site" / "2026" / "week-07" / "page.json").exists()

    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    files = _git(site_repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert "public/2026/week-06/page.json" in files
    assert not any(f.startswith("public/2026/week-07/") for f in files)
    # No history means no season file, so the publish warns and goes out without it.
    assert "the publish goes out without rankings.json" in caplog.text
    assert "public/2026/rankings.json" not in files
    assert not (site_repo / "public" / "2026" / "rankings.json").exists()
    assert "the publish goes out without managers.json" in caplog.text
    assert not (site_repo / "public" / "2026" / "managers.json").exists()


def test_publish_requires_built_page(tmp_path):
    with pytest.raises(PublishError, match="page.json"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "site", push=False)


def test_publish_requires_git_checkout(tmp_path):
    page = tmp_path / "site" / "2026" / "week-06" / "page.json"
    page.parent.mkdir(parents=True)
    page.write_text("{}")
    with pytest.raises(PublishError, match="git"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "missing", push=False)


def test_publish_retry_with_untracked_file_succeeds(tmp_path, fixture_raw_dir, offline):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)
    (repo / "notes.txt").write_text("untracked\n")

    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    assert not (_git(repo, "ls-tree", "-r", "--name-only", "HEAD").count("notes.txt"))


def _fetched(repo, when):
    (week_dir(repo, 2026, 6) / "raw" / "fetched.json").write_text(json.dumps({"transactions": when.isoformat()}))


def test_window_holds_the_five_trades_before_the_cutoff_whatever_the_fetch_time(
        tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 21, 9, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    bundle = read_bundle(week_dir(repo, 2026, 6) / "facts.json")
    assert len(bundle.data.trades) == 5
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 21, 9, 0, tzinfo=ET)


def test_rebuild_keeps_the_first_fetch_time(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    _fetched(repo, datetime(2026, 10, 21, 9, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(
        2026, 10, 20, 12, 0, tzinfo=ET
    )


def test_fetch_time_without_a_saved_one_comes_from_the_raw_write_time(
        tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    fetched = datetime(2026, 10, 20, 8, 0, tzinfo=ET)
    os.utime(week_dir(repo, 2026, 6) / "raw" / "transactions.json", (fetched.timestamp(), fetched.timestamp()))
    bundle, record = make_bundle(repo, 2026, 6, news=no_news, started=datetime(2026, 10, 22, 12, 0, tzinfo=ET),
                                 config=CONFIG)
    assert len(bundle.data.trades) == 5 and record.fetched == fetched
    assert record.fetched.tzinfo == ET
    assert "transactions.json" in caplog.text


def _nflverse_path(repo):
    return week_dir(repo, 2026, 6) / "raw" / "nflverse.json"


def test_build_writes_the_nflverse_extract_and_sources(tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert _nflverse_path(repo).exists()
    sources = read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources
    assert sources == {"history": True, "nflverse_pbp": True, "nflverse_ftn": True,
                       "nflverse_injuries": True, "ffverse": True, "nflverse_snaps": True, "ffopportunity": True,
                       "nflverse_stats_player": True}


def test_saved_extract_is_not_fetched_again(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "nflverse": _forbidden_nflverse}, config=CONFIG)


def test_nflverse_down_still_builds(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "nflverse": _down_nflverse}, config=CONFIG)
    assert page.exists() and "count only this week" not in page.read_text()


def test_degraded_extract_is_not_saved_and_the_next_build_fetches(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "nflverse": _down_nflverse}, config=CONFIG)
    assert not _nflverse_path(repo).exists()
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    saved = NflverseWeek.model_validate_json(_nflverse_path(repo).read_text())
    assert all(saved.sources.values())


def test_a_crashing_fetcher_never_stops_the_build(tmp_path, fixture_raw_dir, caplog, offline):
    def crash(season, week, player_ids, players, teams, scoring):
        raise OSError("disk gone")

    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "nflverse": crash}, config=CONFIG)
    assert page.exists()
    assert not _nflverse_path(repo).exists()
    assert "nflverse unavailable" in caplog.text


def test_no_fetcher_and_no_file_builds_without_nflverse(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    _, record = make_bundle(repo, 2026, 6, news=no_news, config=CONFIG)
    assert not any(record.sources.get(k) for k in NFLVERSE_KEYS)


def test_rewrite_takes_the_nflverse_argument(tmp_path, fixture_raw_dir, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    run_rewrite(repo, 2026, 6, "median", _fake, **{**offline, "nflverse": _forbidden_nflverse})


def _late_week_5_trade(repo):
    """A week 5 leg trade made after the build of week 5, so the history copy of week 5 lacks it."""
    copy = history_dir(repo, 2026, 5) / "transactions.json"
    trade = {**next(t for t in json.loads(copy.read_text()) if t["roster_ids"] == [2, 6]),
             "transaction_id": "late-week-5",
             "created": int(datetime(2026, 10, 14, 12, 0, tzinfo=ET).timestamp() * 1000)}
    return json.loads(copy.read_text()) + [trade]


def test_window_reads_the_fresh_transactions_of_the_week_before(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    (week_dir(repo, 2026, 6) / "raw" / "transactions_prev.json").write_text(json.dumps(_late_week_5_trade(repo)))
    bundle, _ = make_bundle(repo, 2026, 6, news=no_news, fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET),
                            config=CONFIG)
    assert [t.transaction_id for t in bundle.data.trades].count("late-week-5") == 1
    assert len(bundle.data.trades) == 6


def test_window_without_fresh_transactions_reads_the_history_copy(
    tmp_path, fixture_raw_dir, fixture_history_root, caplog
):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    bundle, _ = make_bundle(repo, 2026, 6, news=no_news, fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET),
                            config=CONFIG)
    assert len(bundle.data.trades) == 5
    assert "no fresh transactions for week 5" in caplog.text


def test_build_gives_the_fetch_the_teams_that_played(tmp_path, fixture_raw_dir, offline):
    seen = []

    def record(season, week, player_ids, players, teams, scoring):
        seen.append(teams)
        return offline["nflverse"](season, week, player_ids, players, teams, scoring)

    _, record_ = make_bundle(_repo(tmp_path, fixture_raw_dir), 2026, 6, news=no_news, nflverse=record, config=CONFIG)
    # 28 NFL teams in 14 games had a started player with a Sleeper gp above 0.
    assert len(seen[0]) == 28 and "LAR" in seen[0]
    assert record_.sources["nflverse_pbp"] is True


def test_partial_week_is_not_saved(tmp_path, fixture_raw_dir):
    # Both files lack the ARI and LA game, so the started players of ARI and LAR have no game in them.
    def partial(season, week, player_ids, players, teams, scoring):
        cache = Path(tempfile.mkdtemp())
        for f in NFLVERSE_FIXTURES.iterdir():
            shutil.copy(f, cache / f.name)
        for name in ("play_by_play_2026.csv.gz", "ftn_charting_2026.csv"):
            opener = gzip.open if name.endswith(".gz") else open
            with opener(cache / name, "rt", encoding="utf-8", newline="") as f:
                rows = [line for line in f if "2026_06_ARI_LA" not in line]
            with opener(cache / name, "wt", encoding="utf-8", newline="") as f:
                f.writelines(rows)
        return nflverse_week(season, week, player_ids, players, cache, teams, fetch=no_network, scoring=scoring)

    repo = _repo(tmp_path, fixture_raw_dir)
    _, record = make_bundle(repo, 2026, 6, news=no_news, nflverse=partial, config=CONFIG)
    assert record.sources["nflverse_pbp"] is False
    assert not _nflverse_path(repo).exists()


def test_a_file_without_the_monday_night_game_is_not_saved(tmp_path, fixture_raw_dir):
    # The expected points file lacks the WAS and SF game, so it reads through week 5 and the build goes on.
    def lagged(season, week, player_ids, players, teams, scoring):
        cache = Path(tempfile.mkdtemp())
        for f in NFLVERSE_FIXTURES.iterdir():
            shutil.copy(f, cache / f.name)
        lines = (cache / "ep_weekly_2026.csv").read_text().splitlines(keepends=True)
        (cache / "ep_weekly_2026.csv").write_text("".join(line for line in lines if "2026_06_WAS_SF" not in line))
        return nflverse_week(season, week, player_ids, players, cache, teams, fetch=no_network, scoring=scoring)

    repo = _repo(tmp_path, fixture_raw_dir)
    _, record = make_bundle(repo, 2026, 6, news=no_news, nflverse=lagged, config=CONFIG)
    assert record.sources["ffopportunity"] is False and record.sources["nflverse_pbp"] is True
    assert not _nflverse_path(repo).exists()


def test_a_missing_player_file_sets_its_flag_false_and_is_not_saved(tmp_path, fixture_raw_dir):
    def no_player_file(season, week, player_ids, players, teams, scoring):
        cache = Path(tempfile.mkdtemp())
        for f in NFLVERSE_FIXTURES.iterdir():
            if f.name != "stats_player_week_2026.csv.gz":
                shutil.copy(f, cache / f.name)
        return nflverse_week(season, week, player_ids, players, cache, teams, fetch=_no_bytes_nflverse,
                             scoring=scoring)

    repo = _repo(tmp_path, fixture_raw_dir)
    _, record = make_bundle(repo, 2026, 6, news=no_news, nflverse=no_player_file, config=CONFIG)
    assert record.sources["nflverse_stats_player"] is False and record.sources["nflverse_pbp"] is True
    assert not _nflverse_path(repo).exists()


def test_corrupt_fetch_files_fall_back_with_a_warning(tmp_path, fixture_raw_dir, fixture_history_root, caplog, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    (week_dir(repo, 2026, 6) / "raw" / "fetched.json").write_text('{"transactions": "not a ti')
    (week_dir(repo, 2026, 6) / "verify.json").write_text('{"chapters": {')
    page = run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert page.exists()
    for name in ("fetched.json", "week-06/verify.json"):
        assert name in caplog.text


def test_a_failed_save_keeps_the_fetched_extract(tmp_path, fixture_raw_dir, caplog, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    raw = week_dir(repo, 2026, 6) / "raw"
    # A read-only raw directory makes the write of nflverse.json fail after a good fetch.
    raw.chmod(0o555)
    try:
        bundle, record = make_bundle(repo, 2026, 6, news=no_news, nflverse=offline["nflverse"], config=CONFIG)
    finally:
        raw.chmod(0o755)
    assert record.sources["nflverse_pbp"] is True and bundle.data.drop_source == "nflverse"
    assert not _nflverse_path(repo).exists()
    assert "nflverse.json" in caplog.text


def _old_extract(repo):
    """Cut the saved extract down to the four keys of the first version, as in the saved week 6 file."""
    path = _nflverse_path(repo)
    saved = json.loads(path.read_text())
    path.write_text(json.dumps({key: saved[key] for key in ("sources", "gsis", "drops", "injuries")}))
    return path


def test_a_saved_extract_without_usage_is_fetched_again_and_rewritten(tmp_path, fixture_raw_dir, caplog, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    path = _old_extract(repo)
    with caplog.at_level(logging.INFO, logger="cornerstone.pipeline"):
        _, record = make_bundle(repo, 2026, 6, news=no_news, nflverse=offline["nflverse"], config=CONFIG)
    saved = json.loads(path.read_text())
    assert saved["usage"] and saved["expected"] and saved["next_games"] and saved["bye_weeks"]
    assert record.sources["nflverse_stats_player"] is True
    assert ("week 6 nflverse.json lacks bye_weeks, environment, expected, next_games, usage, "
            "so the build fetches the extract again") in caplog.text


def test_a_refetch_with_a_source_down_keeps_the_saved_drops(tmp_path, fixture_raw_dir, offline):
    # With no FTN file the fresh extract has no drops, but the play by play still gives the usage.
    def no_ftn(season, week, player_ids, players, teams, scoring):
        cache = Path(tempfile.mkdtemp())
        for f in NFLVERSE_FIXTURES.iterdir():
            if f.name != "ftn_charting_2026.csv":
                shutil.copy(f, cache / f.name)
        return nflverse_week(season, week, player_ids, players, cache, teams, fetch=_no_bytes_nflverse,
                             scoring=scoring)

    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    before = _old_extract(repo).read_text()
    bundle, record = make_bundle(repo, 2026, 6, news=no_news, nflverse=no_ftn, config=CONFIG)
    assert bundle.data.drop_source == "nflverse" and record.sources["nflverse_ftn"] is True
    assert record.sources["nflverse_snaps"] is True
    # The fresh extract is degraded, so the file keeps the old content and the next build fetches again.
    assert _nflverse_path(repo).read_text() == before


def test_a_refetch_without_ffverse_keeps_the_saved_keys(tmp_path, fixture_raw_dir, offline):
    # With no ID map the refetch still runs, but it matches fewer players, so its dicts are smaller, not None.
    def no_ffverse(season, week, player_ids, players, teams, scoring):
        cache = Path(tempfile.mkdtemp())
        for f in NFLVERSE_FIXTURES.iterdir():
            if f.name != "db_playerids.csv":
                shutil.copy(f, cache / f.name)
        return nflverse_week(season, week, player_ids, players, cache, teams, fetch=_no_bytes_nflverse,
                             scoring=scoring)

    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    full = NflverseWeek.model_validate_json(_nflverse_path(repo).read_text())
    before = _old_extract(repo).read_text()
    raw_dir = week_dir(repo, 2026, 6) / "raw"
    nfl = _nflverse_for_week(raw_dir, load_raw(raw_dir), 2026, 6, no_ffverse, set())
    assert nfl.gsis == full.gsis and nfl.drops == full.drops and nfl.sources["ffverse"] is True
    # Without the ID map, the fixture usage maps no player. The fresh keys still arrive.
    assert nfl.usage == {} and nfl.environment and nfl.sources["nflverse_snaps"] is True
    assert _nflverse_path(repo).read_text() == before


def test_a_failed_refetch_keeps_the_saved_extract(tmp_path, fixture_raw_dir, caplog, offline):
    def crash(season, week, player_ids, players, teams, scoring):
        raise OSError("disk gone")

    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    path = _old_extract(repo)
    before = path.read_bytes()
    page = run_build(repo, 2026, 6, _fake, fetch=False, **{**offline, "nflverse": crash}, config=CONFIG)
    assert page.exists() and path.read_bytes() == before
    # The build goes on with the drops of the saved extract.
    bundle = read_bundle(week_dir(repo, 2026, 6) / "facts.json")
    assert bundle.data.drop_source == "nflverse"
    assert "nflverse refetch failed" in caplog.text


def test_page_json_command_writes_a_saved_week_with_no_writer_call(tmp_path, fixture_raw_dir, monkeypatch, offline):
    from cornerstone import cli

    def no_claude(*args, **kwargs):
        raise AssertionError("page-json must not call the writer")

    repo = tmp_path / "source"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    page_json = repo / "site" / "2026" / "week-06" / "page.json"
    page_json.unlink()
    monkeypatch.setattr(cli, "claude_call", no_claude)
    monkeypatch.chdir(repo)

    assert cli.main(["page-json", "--season", "2026", "--week", "6"]) == 0

    data = json.loads(page_json.read_text(encoding="utf-8"))
    assert data["schema_version"] == 2
    assert data["week"] == 6
    assert len(data["matchups"]) == 6


def _spy_write_and_verify(seen, lucky_key=None):
    """A stand-in for write_and_verify: it records the page words each chapter gets, and one chapter says "lucky"."""
    def spy(chapter, sheet, call, used_words=frozenset()):
        seen[chapter.key] = set(used_words)
        text = "That was lucky." if chapter.key == lucky_key else "Fact sentence."
        sentences = [Sentence(text=text, fact_ids=[chapter.fact_ids[0]])] if chapter.fact_ids else []
        return Blurb(chapter=chapter.key, attempt=1, fallback=False, sentences=sentences), []

    return spy


def _saved_lucky(repo, key):
    """Put "lucky" into the saved blurb of one chapter."""
    path = week_dir(repo, 2026, 6) / "blurbs.json"
    saved = json.loads(path.read_text(encoding="utf-8"))
    saved[key]["sentences"][0]["text"] = "That was lucky."
    path.write_text(json.dumps(saved), encoding="utf-8")


def test_build_reserves_the_award_words_and_carries_lucky(tmp_path, fixture_raw_dir, monkeypatch, offline):
    # The fixture week has both awards, so every chapter but awards starts with both words used.
    repo = _repo(tmp_path, fixture_raw_dir)
    seen = {}
    monkeypatch.setattr("cornerstone.pipeline.write_and_verify", _spy_write_and_verify(seen))
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    facts = read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.facts
    assert "AW.lucky" in facts and "AW.unlucky" in facts
    assert seen["awards"] == set()
    assert all(seen[k] == {"lucky", "unlucky"} for k in seen if k != "awards")
    # A "lucky" in an earlier chapter reaches the awards chapter.
    seen.clear()
    monkeypatch.setattr("cornerstone.pipeline.write_and_verify", _spy_write_and_verify(seen, "game_changer"))
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    assert seen["awards"] == {"lucky"}


def test_a_rewrite_sees_lucky_from_an_earlier_saved_blurb(tmp_path, fixture_raw_dir, monkeypatch, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    _saved_lucky(repo, "motw")
    seen = {}
    monkeypatch.setattr("cornerstone.pipeline.write_and_verify", _spy_write_and_verify(seen))
    run_rewrite(repo, 2026, 6, "awards", _fake, **offline)
    assert seen["awards"] == {"lucky"}


def test_a_rewrite_of_an_earlier_chapter_sees_a_later_lucky(tmp_path, fixture_raw_dir, monkeypatch, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    _saved_lucky(repo, "median")
    seen = {}
    monkeypatch.setattr("cornerstone.pipeline.write_and_verify", _spy_write_and_verify(seen))
    run_rewrite(repo, 2026, 6, "awards", _fake, **offline)
    assert seen["awards"] == {"lucky"}


def test_a_rewrite_does_not_count_the_chapter_against_itself(tmp_path, fixture_raw_dir, monkeypatch, offline):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **offline, config=CONFIG)
    _saved_lucky(repo, "awards")
    seen = {}
    monkeypatch.setattr("cornerstone.pipeline.write_and_verify", _spy_write_and_verify(seen))
    run_rewrite(repo, 2026, 6, "awards", _fake, **offline)
    assert seen["awards"] == set()


def test_the_bundle_reads_the_position_rank_and_the_bye_cover_from_the_week_snapshot(
        tmp_path, fixture_raw_dir, fixture_history_root, offline):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    bundle, _ = make_bundle(repo, 2026, 6, news=no_news, nflverse=offline["nflverse"], config=CONFIG)
    assert bundle.sheet.facts["NX.bye.12.7523"].text.startswith("Trevor Lawrence, QB10, is on bye in week 7")
    assert "NX.bye.5.8138.cover" in bundle.sheet.facts
