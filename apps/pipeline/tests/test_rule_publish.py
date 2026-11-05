"""
Checks that a publish commit holds only files under the season folders of the client: published/, data/, and build/.
It builds a real git repo in a temp folder and runs the real publish. See ADR 0019.
"""
import subprocess
from pathlib import Path

from rule_report import Offense, clean_git_env, report

from cornerstone.publish import run_publish

ADR = "docs/adr/0019-main-is-the-record-branch.md"
# The three season folders of the client that a publish may stage. The API image seeds from the data folder.
ALLOWED = ("clients/cpc/published/2026/", "clients/cpc/data/2026/", "clients/cpc/build/2026/")
RULE = "a publish commit stages only files under clients/<slug>/published/, data/, or build/ of the season"
FIX = "unstage the file, and commit it on a branch outside the publish."


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=clean_git_env()
    ).stdout


def _commit_paths(root: Path, commit: str) -> list[str]:
    return _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", commit).splitlines()


def _outside_offenses(root: Path, commit: str) -> list[Offense]:
    """Each path of the commit outside the season folders of the client. The line is 1, because a path has no line."""
    return [Offense(
        path=path,
        line=1,
        rule_id="publish/scope",
        what="The publish commit holds a file outside the season folders of the client.",
        rule=RULE,
        adr=ADR,
        fix=FIX,
    ) for path in _commit_paths(root, commit) if not path.startswith(ALLOWED)]


def _publish_offenses(root: Path) -> list[Offense]:
    """The offenses of each commit of the publish: the report commit and the week commit."""
    commits = _git(root, "rev-list", "HEAD").split()
    return [offense for commit in commits for offense in _outside_offenses(root, commit)]


def _built_repo(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """A git repo with the pipeline at apps/pipeline and one built week 8 page in the build folder of cpc.

    The prek hook sets GIT_DIR. The publish calls git with the process env, so the test clears it.
    """
    for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
        monkeypatch.delenv(name, raising=False)
    root = tmp_path / "one"
    pipeline = root / "apps" / "pipeline"
    pipeline.mkdir(parents=True)
    page = root / "clients" / "cpc" / "build" / "2026" / "week-08" / "page.json"
    page.parent.mkdir(parents=True)
    page.write_text("{}")
    raw = root / "clients" / "cpc" / "data" / "2026" / "week-08" / "raw"
    raw.mkdir(parents=True)
    (raw / "league.json").write_text("{}")
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    return root, pipeline


def test_a_publish_stages_only_the_season_folders_of_the_client(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
    offenses = _publish_offenses(root)
    assert not offenses, report(offenses)
    assert _commit_paths(root, "HEAD") == ["clients/cpc/published/2026/week-08/page.json"]
    assert _commit_paths(root, "HEAD~1") == [
        "clients/cpc/build/2026/week-08/page.json", "clients/cpc/data/2026/week-08/raw/league.json",
    ]


def test_a_stray_file_stays_out_of_the_publish(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    (root / "stray.txt").write_text("half-done work\n")
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
    assert _git(root, "status", "--short", "--", "stray.txt").strip() == "?? stray.txt"
    assert _publish_offenses(root) == []


def test_a_change_to_another_season_stays_out_of_the_publish(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    for folder in ("published", "data", "build"):
        old = root / "clients" / "cpc" / folder / "2025" / "rankings.json"
        old.parent.mkdir(parents=True)
        old.write_text("{}")
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
    assert _publish_offenses(root) == []
    for folder in ("published", "data", "build"):
        status = _git(root, "status", "--short", "--", f"clients/cpc/{folder}/2025").strip()
        assert status == f"?? clients/cpc/{folder}/2025/"


def test_a_file_of_the_client_outside_the_season_folders_stays_out_of_the_publish(tmp_path, monkeypatch):
    root, pipeline = _built_repo(tmp_path, monkeypatch)
    (root / "clients" / "cpc" / "data" / "notes.json").write_text("{}")
    run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
    assert _publish_offenses(root) == []
    assert _git(root, "status", "--short", "--", "clients/cpc/data/notes.json").strip() == "?? clients/cpc/data/notes.json"


def test_the_rule_names_a_file_outside_the_season_folders(tmp_path, monkeypatch):
    root, _ = _built_repo(tmp_path, monkeypatch)
    (root / "stray.txt").write_text("half-done work\n")
    (root / "clients" / "cpc" / "client.toml").write_text("")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "Week 8")
    offenses = _outside_offenses(root, "HEAD")
    assert [(offense.path, offense.rule_id) for offense in offenses] == [
        ("clients/cpc/client.toml", "publish/scope"),
        ("stray.txt", "publish/scope"),
    ]
    assert "stray.txt" in report(offenses)
    assert ADR in report(offenses)
