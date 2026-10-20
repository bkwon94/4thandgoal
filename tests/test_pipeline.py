"""
Tests for the build, rewrite, and publish pipeline.
They use recorded fixtures, a fake writer, and a fake avatar downloader, so no network call runs.
"""
import json
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
from cornerstone.pipeline import BuildStopped, make_bundle, read_verify, run_build, run_rewrite, week_dir
from cornerstone.publish import PublishError, run_publish
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


def _fixture_nflverse(season, week, player_ids, players):
    """The recorded nflverse files, read through the real parser from a fresh cache."""
    cache = Path(tempfile.mkdtemp())
    for f in NFLVERSE_FIXTURES.iterdir():
        shutil.copy(f, cache / f.name)
    return nflverse_week(season, week, player_ids, players, cache, fetch=_no_network)


def _down_nflverse(season, week, player_ids, players):
    return NflverseWeek(sources={k: False for k in NFLVERSE_KEYS}, gsis={}, drops=None, injuries=None)


def _forbidden_nflverse(season, week, player_ids, players):
    raise AssertionError("the saved extract must not be fetched again")


OFFLINE = {"news": _no_news, "fetch_bytes": _no_bytes, "nflverse": _fixture_nflverse}


def _repo(tmp_path, fixture_raw_dir):
    raw = week_dir(tmp_path, 2026, 6) / "raw"
    shutil.copytree(fixture_raw_dir, raw)
    return tmp_path


def test_build_from_disk_writes_everything(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert page == repo / "site" / "2026" / "week-06" / "index.html"
    for f in ("facts.json", "blurbs.json", "verify.json"):
        assert (week_dir(repo, 2026, 6) / f).exists()
    assert (repo / "site" / "index.html").exists()


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


def test_publish_copies_site_only(tmp_path, fixture_raw_dir):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, 6) / "raw")
    (repo / "src").mkdir()
    (repo / "src" / "code.py").write_text("x = 1\n")
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)

    url = run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    assert url.endswith("2026/week-06/")
    files = _git(site_repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert "2026/week-06/index.html" in files
    assert not any(f.startswith("src/") for f in files)
    assert _git(repo, "log", "-1", "--format=%s").strip() == "Week 6 report"


def test_publish_leaves_unpublished_weeks_out(tmp_path, fixture_raw_dir, monkeypatch):
    repo, site_repo = tmp_path / "source", tmp_path / "site"
    _init(repo)
    _init(site_repo)
    # The fixture is scored through week 6, so week 7 builds only with the gate open.
    monkeypatch.setattr("cornerstone.pipeline.check_week_is_buildable", lambda *args: None)
    for week in (6, 7):
        shutil.copytree(fixture_raw_dir, week_dir(repo, 2026, week) / "raw")
        run_build(repo, 2026, week, _fake, fetch=False, **OFFLINE)
    assert "week-07/" in (repo / "site" / "index.html").read_text()

    run_publish(repo, 2026, 6, site_repo=site_repo, push=False)

    files = _git(site_repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert "2026/week-06/index.html" in files
    assert not any(f.startswith("2026/week-07/") for f in files)
    home = (site_repo / "index.html").read_text()
    assert "week-06/" in home and "week-07/" not in home


def test_publish_requires_built_page(tmp_path):
    with pytest.raises(PublishError, match="index.html"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "site", push=False)


def test_publish_requires_git_checkout(tmp_path):
    page = tmp_path / "site" / "2026" / "week-06" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<html></html>")
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


def test_window_ends_at_the_saved_fetch_time(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    bundle = read_bundle(week_dir(repo, 2026, 6) / "facts.json")
    assert len(bundle.data.trades) == 5
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 20, 8, 0, tzinfo=ET)


def test_rebuild_keeps_the_first_fetch_time(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    _fetched(repo, datetime(2026, 10, 21, 9, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 20, 12, 0, tzinfo=ET)


def test_window_starts_at_the_fetch_before(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    previous = week_dir(repo, 2026, 5)
    previous.mkdir(parents=True)
    record = BuildRecord(started=datetime(2026, 10, 16, 18, 0, tzinfo=ET), sources={},
                         fetched=datetime(2026, 10, 16, 18, 0, tzinfo=ET))
    (previous / "verify.json").write_text(VerifyFile(build=record, chapters={}).model_dump_json())
    bundle, _ = make_bundle(repo, 2026, 6, news=_no_news, fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert [x.roster_ids for x in bundle.data.trades] == [[11, 12], [7, 8]]


def test_window_without_a_fetch_time_ends_at_the_raw_fetch(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    # The week 6 raw files were fetched before 11:55 on Tuesday, when the late trade of rosters 7 and 8 was made.
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    fetched = datetime(2026, 10, 20, 8, 0, tzinfo=ET)
    os.utime(week_dir(repo, 2026, 6) / "raw" / "transactions.json", (fetched.timestamp(), fetched.timestamp()))
    bundle, record = make_bundle(repo, 2026, 6, news=_no_news, started=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
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
    assert "count only this week" in page.read_text()


def test_degraded_extract_is_not_saved_and_the_next_build_fetches(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **{**OFFLINE, "nflverse": _down_nflverse})
    assert not _nflverse_path(repo).exists()
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    saved = NflverseWeek.model_validate_json(_nflverse_path(repo).read_text())
    assert all(saved.sources.values())


def test_a_crashing_fetcher_never_stops_the_build(tmp_path, fixture_raw_dir, caplog):
    def crash(season, week, player_ids, players):
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
    assert len(bundle.data.trades) == 7


def test_window_without_fresh_transactions_reads_the_history_copy(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    bundle, _ = make_bundle(repo, 2026, 6, news=_no_news, fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert len(bundle.data.trades) == 6
    assert "no fresh transactions for week 5" in caplog.text
