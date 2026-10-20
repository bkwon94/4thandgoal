"""
Tests for the build, rewrite, and publish pipeline.
They use recorded fixtures, a fake writer, and a fake avatar downloader, so no network call runs.
"""
import json
import re
import shutil
import subprocess

import pytest

from cornerstone.models import Sentence, Verdict, VerifyOut
from cornerstone.pipeline import BuildStopped, run_build, run_rewrite, week_dir
from cornerstone.publish import PublishError, run_publish


def _fake(system, user, model):
    if model.__name__ == "VerifyOut":
        return VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.M).group(1)
    return model(sentences=[Sentence(text="Fact sentence.", fact_ids=[fid])] * 2)


def _no_news(player_id):
    return []


def _no_bytes(url):
    return None


OFFLINE = {"news": _no_news, "fetch_bytes": _no_bytes}


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
    page = run_rewrite(repo, 2026, 6, "median", _fake, **OFFLINE)
    after = json.loads(path.read_text())
    assert set(before) == set(after)
    assert page.exists()


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


def test_publish_requires_built_page(tmp_path):
    with pytest.raises(PublishError, match="index.html"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "site", push=False)


def test_publish_requires_git_checkout(tmp_path):
    page = tmp_path / "site" / "2026" / "week-06" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<html></html>")
    with pytest.raises(PublishError, match="git"):
        run_publish(tmp_path, 2026, 6, site_repo=tmp_path / "missing", push=False)
