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

import pytest

from cornerstone.history import HISTORY_FILES, history_dir, history_root
from pathlib import Path

from cornerstone.models import BuildRecord, NflverseWeek, Sentence, Verdict, VerifyFile, VerifyOut
from cornerstone.nflverse import nflverse_week
from cornerstone.pipeline import (
    BuildStopped, _write_rankings, make_bundle, read_verify, run_build, run_page_json, run_rankings, run_rewrite,
    week_dir,
)
from cornerstone.publish import PublishError, run_publish
from cornerstone.render import RANKINGS_ODDS_KEYS
from cornerstone.sheet import read_bundle

ET = ZoneInfo("America/New_York")


def _fake(system, user, model):
    if model.__name__ == "VerifyOut":
        return VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.M).group(1)
    return model(sentences=[Sentence(text="Fact sentence.", fact_ids=[fid])] * 2)


def _no_news(player_id):
    return []


def _no_bytes(url):
    return None


NFLVERSE_FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"
NFLVERSE_KEYS = ("nflverse_pbp", "nflverse_ftn", "nflverse_injuries", "ffverse")


def _no_network(url):
    raise AssertionError(f"network call to {url}")


def _fixture_nflverse(season, week, player_ids, players, teams):
    """The recorded nflverse files, read through the real parser from a fresh cache."""
    cache = Path(tempfile.mkdtemp())
    for f in NFLVERSE_FIXTURES.iterdir():
        shutil.copy(f, cache / f.name)
    return nflverse_week(season, week, player_ids, players, cache, teams, fetch=_no_network)


def _down_nflverse(season, week, player_ids, players, teams):
    return NflverseWeek(sources={k: False for k in NFLVERSE_KEYS}, gsis={}, drops=None, injuries=None)


def _forbidden_nflverse(season, week, player_ids, players, teams):
    raise AssertionError("the saved extract must not be fetched again")


OFFLINE = {"news": _no_news, "fetch_bytes": _no_bytes, "nflverse": _fixture_nflverse}


def _repo(tmp_path, fixture_raw_dir):
    raw = week_dir(tmp_path, 2026, 6) / "raw"
    shutil.copytree(fixture_raw_dir, raw)
    return tmp_path


def test_build_from_disk_writes_everything(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
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


def test_build_records_the_history_source(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    record = read_verify(week_dir(repo, 2026, 6) / "verify.json").build
    assert record.sources["history"] is True


def test_build_without_history_degrades(tmp_path, fixture_raw_dir, caplog):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources["history"] is False
    assert "history incomplete" in caplog.text


def test_build_saves_the_week_to_history(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    out = history_dir(history_root(repo, 2026), 6)
    assert {p.stem for p in out.glob("*.json")} == {*HISTORY_FILES, "injuries"}
    injuries = json.loads((out / "injuries.json").read_text())
    assert injuries["2216"] == "Out"  # Mike Evans
    assert injuries["5859"] == "Questionable"  # A.J. Brown


def _rankings(repo):
    return repo / "site" / "2026" / "rankings.json"


def test_build_writes_the_rankings_file_after_the_page(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert page.exists()
    built = _rankings(repo).read_text(encoding="utf-8")
    data = json.loads(built)
    assert [w["week"] for w in data["weeks"]] == [1, 2, 3, 4, 5, 6]
    # The plain fake gives the rankings chapter no roster tags, so it falls back. The fallback leaves the
    # blurbs empty on purpose, so both files match.
    # The rankings command writes the same file from the same saved history.
    assert run_rankings(repo, 2026, 6, _fake).read_text(encoding="utf-8") == built


def test_build_puts_the_odds_of_the_week_in_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    # The odds come from the saved facts of the build, so the file and the facts agree.
    odds = read_bundle(week_dir(repo, 2026, 6) / "facts.json").odds
    for row in data["weeks"][-1]["rows"]:
        t = odds.teams[row["roster_id"]]
        assert row["odds"] == {k: getattr(t, k) for k in RANKINGS_ODDS_KEYS}
    assert all("odds" not in row for w in data["weeks"][:-1] for row in w["rows"])


def test_a_rewrite_puts_the_saved_odds_in_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    # With no rankings file, the odds can come only from the saved facts.
    _rankings(repo).unlink()
    run_rewrite(repo, 2026, 6, "rankings", _fake)
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    odds = read_bundle(week_dir(repo, 2026, 6) / "facts.json").odds
    assert odds is not None
    for row in data["weeks"][-1]["rows"]:
        assert row["odds"] == {k: getattr(odds.teams[row["roster_id"]], k) for k in RANKINGS_ODDS_KEYS}


def test_an_older_week_never_shrinks_the_rankings_file(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    # The build saves week 6, so the history runs through week 6.
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    teams = read_bundle(week_dir(repo, 2026, 6) / "facts.json").data.teams
    caplog.set_level(logging.INFO, logger="cornerstone.pipeline")
    out = _write_rankings(repo, 2026, 5, teams)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [w["week"] for w in data["weeks"]] == [1, 2, 3, 4, 5, 6]
    assert "covers weeks 1 to 6, past the built week 5" in caplog.text


def test_incomplete_history_skips_the_rankings_file_and_the_page_builds(tmp_path, fixture_raw_dir, caplog):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert page.exists()
    assert not _rankings(repo).exists()
    assert "history incomplete" in caplog.text


def test_rankings_command_writes_the_file_for_a_saved_week(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
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


def test_rankings_command_writes_twelve_blurbs_with_one_call(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
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
    tmp_path, fixture_raw_dir, fixture_history_root,
):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
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
    tmp_path, fixture_raw_dir, fixture_history_root,
):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
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


def test_build_writes_the_rankings_blurb_into_the_file(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)

    def call(system, user, model):
        # The rankings chapter gets tagged sentences. Every other chapter gets the plain fake.
        fake = _RankingsWriter() if "Chapter: Power rankings" in user else _fake
        return fake(system, user, model)

    run_build(repo, 2026, 6, call, fetch=False, **OFFLINE)
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    week6 = next(w for w in data["weeks"] if w["week"] == 6)
    assert all(len(row["blurb"]) == 1 for row in week6["rows"])


def _week6_blurbs(repo):
    data = json.loads(_rankings(repo).read_text(encoding="utf-8"))
    return {row["roster_id"]: row["blurb"] for w in data["weeks"] if w["week"] == 6 for row in w["rows"]}


def test_a_fallback_rankings_blurb_keeps_the_saved_blurbs(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    run_rankings(repo, 2026, 6, _RankingsWriter())
    saved = _week6_blurbs(repo)
    assert all(len(b) == 1 for b in saved.values())
    # The plain fake gives no roster tags, so the blurb falls back and must not wipe the saved blurbs.
    run_rankings(repo, 2026, 6, _fake)
    blurbs = json.loads((week_dir(repo, 2026, 6) / "blurbs.json").read_text(encoding="utf-8"))
    assert blurbs["rankings"]["fallback"] is True
    assert _week6_blurbs(repo) == saved


def test_a_rankings_rewrite_reaches_the_season_file(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    # The plain fake falls back, so the build leaves the blurbs empty.
    assert all(b == [] for b in _week6_blurbs(repo).values())
    run_rewrite(repo, 2026, 6, "rankings", _RankingsWriter(), **OFFLINE)
    blurbs = _week6_blurbs(repo)
    assert len(blurbs) == 12
    chapter = next(c for c in read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.chapters if c.key == "rankings")
    for rid, sentences in blurbs.items():
        required = [fid for fid in chapter.required if fid.split(".")[1] == str(rid)]
        assert [s["fact_ids"] for s in sentences] == [[f"PR.{rid}", *required]]


def test_a_rewrite_reads_the_saved_odds_and_never_runs_the_engine(tmp_path, fixture_raw_dir, fixture_history_root,
                                                                  monkeypatch):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    saved = read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.facts
    odds = {fid: f for fid, f in saved.items() if fid.startswith(("ODDS.", "SW."))}
    # 12 odds facts, 12 odds why facts, and 2 swing facts.
    assert len(odds) == 26

    def no_engine(*args, **kwargs):
        raise AssertionError("a rewrite ran the odds engine")

    monkeypatch.setattr("cornerstone.sheet.playoff_odds", no_engine)
    run_rewrite(repo, 2026, 6, "next_week", _fake, **OFFLINE)
    after = read_bundle(week_dir(repo, 2026, 6) / "facts.json").sheet.facts
    assert {fid: after[fid] for fid in odds} == odds


def _waiver(repo):
    return json.loads((repo / "site" / "2026" / "week-06" / "waiver.json").read_text())


def test_build_writes_the_waiver_file_beside_the_page(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    body = _waiver(repo)
    assert body["schema_version"] == 1
    assert body["week"] == 6
    assert datetime.fromisoformat(body["built"]).tzinfo is not None
    # The fixture rosters every player in its players file, so the pool is empty. It has no trending file.
    assert body["buckets"] == {"best_adds": [], "trending": []}
    assert len(body["budgets"]) == 12
    assert body["budgets"][0] == {"roster_id": 1, "budget_left": 69, "waiver_order": 1}


def test_a_rewrite_reads_the_saved_board_and_never_runs_the_waiver_engine(tmp_path, fixture_raw_dir, monkeypatch):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    built = _waiver(repo)
    (repo / "site" / "2026" / "week-06" / "waiver.json").unlink()

    def no_engine(*args, **kwargs):
        raise AssertionError("a rewrite ran the waiver engine")

    monkeypatch.setattr("cornerstone.pipeline.waiver_board", no_engine)
    run_rewrite(repo, 2026, 6, "next_week", _fake, **OFFLINE)
    assert _waiver(repo) == built


def test_rankings_command_stops_on_an_incomplete_history(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    with pytest.raises(BuildStopped, match="history"):
        run_rankings(repo, 2026, 6, _fake)


def test_build_survives_a_history_save_failure(tmp_path, fixture_raw_dir, caplog):
    repo = _repo(tmp_path, fixture_raw_dir)
    # A file in place of the history directory makes the save fail.
    root = history_root(repo, 2026)
    root.parent.mkdir(parents=True, exist_ok=True)
    root.write_text("not a directory")
    page = run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert page.exists()
    assert "week 6 not saved to history" in caplog.text


def test_rewrite_reads_the_version_1_verify_shape(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    path = week_dir(repo, 2026, 6) / "verify.json"
    chapters = json.loads(path.read_text())["chapters"]
    path.write_text(json.dumps(chapters))
    assert read_verify(path).build is None

    run_rewrite(repo, 2026, 6, "median", _fake, **OFFLINE)

    assert read_verify(path).build is None
    assert set(read_verify(path).chapters) == set(chapters)


def test_rewrite_keeps_the_build_record(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    path = week_dir(repo, 2026, 6) / "verify.json"
    before = read_verify(path).build
    run_rewrite(repo, 2026, 6, "median", _fake, **OFFLINE)
    assert read_verify(path).build == before


def test_build_stops_on_unscored_week(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    shutil.copytree(week_dir(repo, 2026, 6) / "raw", week_dir(repo, 2026, 7) / "raw")
    with pytest.raises(BuildStopped, match="not final"):
        run_build(repo, 2026, 7, _fake, fetch=False, **OFFLINE)


def test_build_stops_without_raw_data(tmp_path):
    with pytest.raises(BuildStopped, match="No raw data for week 6"):
        run_build(tmp_path, 2026, 6, _fake, fetch=False, **OFFLINE)


def test_rewrite_one_chapter(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    path = week_dir(repo, 2026, 6) / "blurbs.json"
    before = json.loads(path.read_text())

    # The build fake gives one verdict for two sentences, so every built blurb is the template.
    # This fake passes both sentences, so the rewrite keeps the text it wrote.
    def rewrite_fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(2)])
        fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.M).group(1)
        return model(sentences=[Sentence(text="Rewritten median sentence.", fact_ids=[fid])] * 2)

    page = run_rewrite(repo, 2026, 6, "median", rewrite_fake, **OFFLINE)
    after = json.loads(path.read_text())
    assert set(before) == set(after)
    text = [s["text"] for s in after["median"]["sentences"]]
    assert text != [s["text"] for s in before["median"]["sentences"]]
    assert text == ["Rewritten median sentence."] * 2
    assert after["recap_4"] == before["recap_4"]
    assert "Rewritten median sentence." in page.read_text()


def test_rewrite_unknown_chapter_lists_valid_keys(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    with pytest.raises(ValueError, match="median"):
        run_rewrite(repo, 2026, 6, "nope", _fake, **OFFLINE)


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def _init(path):
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")


def test_publish_copies_site_only(tmp_path, fixture_raw_dir, fixture_history_root):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    shutil.copytree(fixture_history_root, history_root(repo, 2026))
    (repo / "src").mkdir()
    (repo / "src" / "code.py").write_text("x = 1\n")
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)

    url = run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    assert url.endswith("2026/week-06/")
    files = _git(site_repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert "public/2026/week-06/page.json" in files
    assert "public/2026/rankings.json" in files
    assert "public/2026/week-06/waiver.json" in files
    assert "public/2026/week-06/index.html" not in files
    assert not any(f.startswith("src/") for f in files)
    assert not any(f.startswith("public/static/") for f in files)
    assert "public/index.html" not in files
    assert not (site_repo / "2026").exists()
    assert not (site_repo / "index.html").exists()
    assert not (site_repo / "static").exists()
    assert _git(repo, "log", "-1", "--format=%s").strip() == "Week 6 report"


def test_publish_leaves_unpublished_weeks_out(tmp_path, fixture_raw_dir, monkeypatch, caplog):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    # The fixture is scored through week 6, so week 7 builds only with the gate open.
    monkeypatch.setattr("cornerstone.pipeline.check_week_is_buildable", lambda *args: None)
    for week in (6, 7):
        shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, week) / "raw")
        run_build(repo, 2026, week, _fake, fetch=False, **OFFLINE)
    assert (repo / "site" / "2026" / "week-07" / "page.json").exists()

    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    files = _git(site_repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert "public/2026/week-06/page.json" in files
    assert not any(f.startswith("public/2026/week-07/") for f in files)
    # No history means no season file, so the publish warns and goes out without it.
    assert "the publish goes out without rankings.json" in caplog.text
    assert "public/2026/rankings.json" not in files
    assert not (site_repo / "public" / "2026" / "rankings.json").exists()


def test_publish_requires_built_page(tmp_path):
    with pytest.raises(PublishError, match="page.json"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "site", push=False)


def test_publish_requires_git_checkout(tmp_path):
    page = tmp_path / "site" / "2026" / "week-06" / "page.json"
    page.parent.mkdir(parents=True)
    page.write_text("{}")
    with pytest.raises(PublishError, match="git"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "missing", push=False)


def test_publish_retry_with_untracked_file_succeeds(tmp_path, fixture_raw_dir):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)
    (repo / "notes.txt").write_text("untracked\n")

    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    assert not (_git(repo, "ls-tree", "-r", "--name-only", "HEAD").count("notes.txt"))


def _fetched(repo, when):
    (week_dir(repo, 2026, 6) / "raw" / "fetched.json").write_text(json.dumps({"transactions": when.isoformat()}))


def test_window_holds_the_five_trades_before_the_cutoff_whatever_the_fetch_time(
        tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 21, 9, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    bundle = read_bundle(week_dir(repo, 2026, 6) / "facts.json")
    assert len(bundle.data.trades) == 5
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 21, 9, 0, tzinfo=ET)


def test_rebuild_keeps_the_first_fetch_time(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    _fetched(repo, datetime(2026, 10, 21, 9, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 20, 12, 0, tzinfo=ET)


def test_fetch_time_without_a_saved_one_comes_from_the_raw_write_time(
        tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    fetched = datetime(2026, 10, 20, 8, 0, tzinfo=ET)
    os.utime(week_dir(repo, 2026, 6) / "raw" / "transactions.json", (fetched.timestamp(), fetched.timestamp()))
    bundle, record = make_bundle(repo, 2026, 6, news=_no_news, started=datetime(2026, 10, 22, 12, 0, tzinfo=ET))
    assert len(bundle.data.trades) == 5 and record.fetched == fetched
    assert record.fetched.tzinfo == ET
    assert "transactions.json" in caplog.text


def _nflverse_path(repo):
    return week_dir(repo, 2026, 6) / "raw" / "nflverse.json"


def test_build_writes_the_nflverse_extract_and_sources(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert _nflverse_path(repo).exists()
    sources = read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources
    assert sources == {"history": True, "nflverse_pbp": True, "nflverse_ftn": True,
                       "nflverse_injuries": True, "ffverse": True}


def test_saved_extract_is_not_fetched_again(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    run_build(repo, 2026, 6, _fake, fetch=False, **{**OFFLINE, "nflverse": _forbidden_nflverse})


def test_nflverse_down_still_builds(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **{**OFFLINE, "nflverse": _down_nflverse})
    assert page.exists() and "count only this week" not in page.read_text()


def test_degraded_extract_is_not_saved_and_the_next_build_fetches(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **{**OFFLINE, "nflverse": _down_nflverse})
    assert not _nflverse_path(repo).exists()
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    saved = NflverseWeek.model_validate_json(_nflverse_path(repo).read_text())
    assert all(saved.sources.values())


def test_a_crashing_fetcher_never_stops_the_build(tmp_path, fixture_raw_dir, caplog):
    def crash(season, week, player_ids, players, teams):
        raise OSError("disk gone")

    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **{**OFFLINE, "nflverse": crash})
    assert page.exists()
    assert not _nflverse_path(repo).exists()
    assert "nflverse unavailable" in caplog.text


def test_no_fetcher_and_no_file_builds_without_nflverse(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    _, record = make_bundle(repo, 2026, 6, news=_no_news)
    assert not any(record.sources.get(k) for k in NFLVERSE_KEYS)


def test_rewrite_takes_the_nflverse_argument(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    run_rewrite(repo, 2026, 6, "median", _fake, **{**OFFLINE, "nflverse": _forbidden_nflverse})


def _late_week_5_trade(repo):
    """A week 5 leg trade made after the build of week 5, so the history copy of week 5 lacks it."""
    copy = history_dir(history_root(repo, 2026), 5) / "transactions.json"
    trade = {**next(t for t in json.loads(copy.read_text()) if t["roster_ids"] == [2, 6]),
             "transaction_id": "late-week-5",
             "created": int(datetime(2026, 10, 14, 12, 0, tzinfo=ET).timestamp() * 1000)}
    return json.loads(copy.read_text()) + [trade]


def test_window_reads_the_fresh_transactions_of_the_week_before(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    (week_dir(repo, 2026, 6) / "raw" / "transactions_prev.json").write_text(json.dumps(_late_week_5_trade(repo)))
    bundle, _ = make_bundle(repo, 2026, 6, news=_no_news, fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert [t.transaction_id for t in bundle.data.trades].count("late-week-5") == 1
    assert len(bundle.data.trades) == 6


def test_window_without_fresh_transactions_reads_the_history_copy(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    bundle, _ = make_bundle(repo, 2026, 6, news=_no_news, fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert len(bundle.data.trades) == 5
    assert "no fresh transactions for week 5" in caplog.text


def test_build_gives_the_fetch_the_teams_that_played(tmp_path, fixture_raw_dir):
    seen = []

    def record(season, week, player_ids, players, teams):
        seen.append(teams)
        return _fixture_nflverse(season, week, player_ids, players, teams)

    _, record_ = make_bundle(_repo(tmp_path, fixture_raw_dir), 2026, 6, news=_no_news, nflverse=record)
    # 28 NFL teams in 14 games had a started player with a Sleeper gp above 0.
    assert len(seen[0]) == 28 and "LAR" in seen[0]
    assert record_.sources["nflverse_pbp"] is True


def test_partial_week_is_not_saved(tmp_path, fixture_raw_dir):
    # Both files lack the ARI and LA game, so the started players of ARI and LAR have no game in them.
    def partial(season, week, player_ids, players, teams):
        cache = Path(tempfile.mkdtemp())
        for f in NFLVERSE_FIXTURES.iterdir():
            shutil.copy(f, cache / f.name)
        for name in ("play_by_play_2026.csv.gz", "ftn_charting_2026.csv"):
            opener = gzip.open if name.endswith(".gz") else open
            with opener(cache / name, "rt", encoding="utf-8", newline="") as f:
                rows = [line for line in f if "2026_06_ARI_LA" not in line]
            with opener(cache / name, "wt", encoding="utf-8", newline="") as f:
                f.writelines(rows)
        return nflverse_week(season, week, player_ids, players, cache, teams, fetch=_no_network)

    repo = _repo(tmp_path, fixture_raw_dir)
    _, record = make_bundle(repo, 2026, 6, news=_no_news, nflverse=partial)
    assert record.sources["nflverse_pbp"] is False
    assert not _nflverse_path(repo).exists()


def test_corrupt_fetch_files_fall_back_with_a_warning(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    (week_dir(repo, 2026, 6) / "raw" / "fetched.json").write_text('{"transactions": "not a ti')
    (week_dir(repo, 2026, 6) / "verify.json").write_text('{"chapters": {')
    page = run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert page.exists()
    for name in ("fetched.json", "week-06/verify.json"):
        assert name in caplog.text


def test_a_failed_save_keeps_the_fetched_extract(tmp_path, fixture_raw_dir, caplog):
    repo = _repo(tmp_path, fixture_raw_dir)
    raw = week_dir(repo, 2026, 6) / "raw"
    # A read-only raw directory makes the write of nflverse.json fail after a good fetch.
    raw.chmod(0o555)
    try:
        bundle, record = make_bundle(repo, 2026, 6, news=_no_news, nflverse=_fixture_nflverse)
    finally:
        raw.chmod(0o755)
    assert record.sources["nflverse_pbp"] is True and bundle.data.drop_source == "nflverse"
    assert not _nflverse_path(repo).exists()
    assert "nflverse.json" in caplog.text


def test_page_json_command_writes_a_saved_week_with_no_writer_call(tmp_path, fixture_raw_dir, monkeypatch):
    from cornerstone import cli

    def no_claude(*args, **kwargs):
        raise AssertionError("page-json must not call the writer")

    repo = tmp_path / "source"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    page_json = repo / "site" / "2026" / "week-06" / "page.json"
    page_json.unlink()
    monkeypatch.setattr(cli, "claude_call", no_claude)
    monkeypatch.chdir(repo)

    assert cli.main(["page-json", "--season", "2026", "--week", "6"]) == 0

    data = json.loads(page_json.read_text(encoding="utf-8"))
    assert data["schema_version"] == 2
    assert data["week"] == 6
    assert len(data["matchups"]) == 6
