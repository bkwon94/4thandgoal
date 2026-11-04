"""
Checks that a publish commit holds only files under clients/<slug>/published/<season>/, the published data of the client.
It builds a real git repo in a temp folder and runs the real publish. See ADR 0019.
"""
import subprocess
from pathlib import Path

from rule_report import Offense, clean_git_env, report

from cornerstone.publish import run_publish

ADR = "docs/adr/0019-main-is-the-record-branch.md"
PUBLISHED = "clients/cpc/published/2026/"
RULE = "a publish commit stages only files under clients/<slug>/published/<season>/"
FIX = "unstage the file, and commit it on a branch outside the publish."


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=clean_git_env()
    ).stdout


def _commit_paths(root: Path, commit: str) -> list[str]:
    return _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", commit).splitlines()


def _outside_offenses(root: Path, commit: str) -> list[Offense]:
    """Each path of the commit outside the published folder. The line is 1, because a path has no line."""
    return [Offense(
        path=path,
        line=1,
        rule_id="publish/scope",
        what="The publish commit holds a file outside the published data.",
        rule=RULE,
        adr=ADR,
        fix=FIX,
    ) for path in _commit_paths(root, commit) if not path.startswith(PUBLISHED)]


def _built_repo(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """A git repo with the pipeline at apps/pipeline and one built week 8 page.

    The prek hook sets GIT_DIR. The publish calls git with the process env, so the test clears it.
    """
    for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
        monkeypatch.delenv(name, raising=False)
    root = tmp_path / "one"
    pipeline = root / "apps" / "pipeline"
    page = pipeline / "site" / "2026" / "week-08" / "page.json"
    page.parent.mkdir(parents=True)
    page.write_text("{}")
    (root / "clients" / "cpc" / "data").mkdir(parents=True)
    (root / "clients" / "cpc" / "data" / "history.json").write_text("{}")
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    return root, pipeline


def test_a_publish_of_only_published_data_passes(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc" / "data", push=False)
    offenses = _outside_offenses(root, "HEAD")
    assert not offenses, report(offenses)
    assert _commit_paths(root, "HEAD") == ["clients/cpc/published/2026/week-08/page.json"]


def test_a_stray_file_stays_out_of_the_publish(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    (root / "stray.txt").write_text("half-done work\n")
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc" / "data", push=False)
    assert _git(root, "status", "--short", "--", "stray.txt").strip() == "?? stray.txt"
    assert _outside_offenses(root, "HEAD") == []


def test_a_change_to_another_season_stays_out_of_the_publish(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    old = root / "clients" / "cpc" / "published" / "2025" / "rankings.json"
    old.parent.mkdir(parents=True)
    old.write_text("{}")
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc" / "data", push=False)
    assert _commit_paths(root, "HEAD") == ["clients/cpc/published/2026/week-08/page.json"]
    assert _git(root, "status", "--short", "--", "clients/cpc/published/2025").strip() == "?? clients/cpc/published/2025/"


def test_the_rule_names_a_file_outside_the_published_data(tmp_path, monkeypatch):
    root, _ = _built_repo(tmp_path, monkeypatch)
    (root / "stray.txt").write_text("half-done work\n")
    published = root / "clients" / "cpc" / "published" / "2026" / "week-08" / "page.json"
    published.parent.mkdir(parents=True)
    published.write_text("{}")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "Week 8")
    offenses = _outside_offenses(root, "HEAD")
    assert [(offense.path, offense.rule_id) for offense in offenses] == [
        ("apps/pipeline/site/2026/week-08/page.json", "publish/scope"),
        ("clients/cpc/data/history.json", "publish/scope"),
        ("stray.txt", "publish/scope"),
    ]
    assert "stray.txt" in report(offenses)
    assert ADR in report(offenses)
