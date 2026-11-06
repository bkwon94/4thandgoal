"""
Tests for the publish of the midseason report: it checks each blurb of the draft again, refuses on a failure, and
commits only midseason.json and sim.json of the season. Each test builds a real git repo in a temp folder.
"""
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from cpc import cli_root, cpc_client
from fakes import FakeWriter
from rule_report import clean_git_env, report
from test_midseason import (
    CPC_DATA,
    CPC_PROVIDER,
    DRAFT_BLURB,
    DRAFT_ROAST,
    ROAST_BLURB,
    STATE_BLURB,
    _call,
    _clean_call,
    _passed,
    prime_nflverse,
)
from test_rule_publish import _outside_offenses

from cornerstone.pipeline import run_midseason
from cornerstone.publish import PublishError, run_midseason_publish
from league.models import Verdict, VerifyOut
from league.paths import build_dir, history_root, nfl_dir, week_dir


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=clean_git_env()
    ).stdout


def _drafted_repo(tmp_path: Path, monkeypatch):
    """A git repo with the pipeline at apps/pipeline and a clean draft of the CPC week 8 report in the build folder,
    with a sim.json beside it. The prek hook sets GIT_DIR, and the publish calls git with the process env, so the test
    clears it."""
    for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
        monkeypatch.delenv(name, raising=False)
    root = tmp_path / "one"
    pipeline = root / "apps" / "pipeline"
    pipeline.mkdir(parents=True)
    client = cpc_client(at=root / "clients" / "cpc")
    shutil.copytree(CPC_DATA / "history", history_root(client.folder, 2026))
    week_dir(client.folder, 2026, 8).mkdir(parents=True)
    shutil.copy(CPC_DATA / "week-08" / "facts.json", week_dir(client.folder, 2026, 8) / "facts.json")
    prime_nflverse(client.nfl_dir)
    run_midseason(2026, 8, _clean_call(), client=client, provider=CPC_PROVIDER)
    # Ticket 03 writes the real sim.json. The publish copies the bytes as they are.
    (build_dir(client.folder) / "2026" / "sim.json").write_text('{"week": 8}\n', encoding="utf-8")
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    (root / "README.md").write_text("one\n")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "Start")
    return root, pipeline, client


def _published(root: Path) -> Path:
    return root / "clients" / "cpc" / "published" / "2026"


def test_a_clean_publish_commits_midseason_json_and_sim_json_and_no_other_path(tmp_path, monkeypatch):
    # AT-43.
    root, pipeline, client = _drafted_repo(tmp_path, monkeypatch)
    run_midseason_publish(pipeline, 2026, 8, _call(_passed(3), _passed(2), _passed(2), _passed(2)), client=client)
    assert _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").split() == [
        "clients/cpc/published/2026/midseason.json", "clients/cpc/published/2026/sim.json"]
    offenses = _outside_offenses(root, "HEAD")
    assert not offenses, report(offenses)
    assert _git(root, "log", "-1", "--format=%s").strip() == "Midseason report week 8"
    build = build_dir(client.folder) / "2026"
    assert (_published(root) / "midseason.json").read_bytes() == (build / "midseason.json").read_bytes()
    assert (_published(root) / "sim.json").read_bytes() == (build / "sim.json").read_bytes()
    # The review file and the saved facts stay in the build folder, and the build folder stays out of the commit.
    assert not (_published(root) / "midseason-review.md").exists()
    assert _git(root, "status", "--short", "--", "clients/cpc/build").strip() == "?? clients/cpc/build/"


def test_an_edited_blurb_with_an_uncited_number_makes_the_publish_refuse_and_name_the_blurb(tmp_path, monkeypatch):
    # AT-42. The code check fails the edit, so the publish makes no Claude call.
    root, pipeline, client = _drafted_repo(tmp_path, monkeypatch)
    draft = build_dir(client.folder) / "2026" / "midseason.json"
    data = json.loads(draft.read_text(encoding="utf-8"))
    data["acts"][0]["chapters"][0]["roast"]["sentences"][0]["text"] = "NFC Least is 3-13 with 999 regrets."
    draft.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(PublishError) as err:
        run_midseason_publish(pipeline, 2026, 8, _call(_passed(3)), client=client)
    assert "The blurb state.roast fails the verifier" in str(err.value)
    assert "number 999 is not in the cited facts" in str(err.value)
    assert not _published(root).exists()
    assert _git(root, "log", "--format=%s").split("\n")[0] == "Start"


def test_a_blurb_that_the_claude_check_rejects_makes_the_publish_refuse(tmp_path, monkeypatch):
    root, pipeline, client = _drafted_repo(tmp_path, monkeypatch)
    rejected = VerifyOut(verdicts=[*_passed(2).verdicts, Verdict(index=2, supported=False, reason="No fact.")])
    with pytest.raises(PublishError, match=r"The blurb state fails the verifier: \[2\] No fact\."):
        run_midseason_publish(pipeline, 2026, 8, _call(rejected, _passed(2)), client=client)
    assert not _published(root).exists()


def test_the_publish_refuses_a_draft_with_no_sim_json(tmp_path, monkeypatch):
    root, pipeline, client = _drafted_repo(tmp_path, monkeypatch)
    (build_dir(client.folder) / "2026" / "sim.json").unlink()
    with pytest.raises(PublishError, match="sim.json"):
        run_midseason_publish(pipeline, 2026, 8, _call(_passed(3), _passed(2), _passed(2), _passed(2)), client=client)
    assert not _published(root).exists()


def test_the_publish_refuses_a_draft_of_another_week(tmp_path, monkeypatch):
    root, pipeline, client = _drafted_repo(tmp_path, monkeypatch)
    with pytest.raises(PublishError, match="week 8"):
        run_midseason_publish(pipeline, 2026, 9, _call(), client=client)
    assert not _published(root).exists()


def test_the_midseason_publish_command_prints_the_refusal_and_names_the_blurb(tmp_path, monkeypatch, capsys):
    # AT-42 through the command of make midseason-publish.
    from cornerstone import cli

    for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
        monkeypatch.delenv(name, raising=False)
    cli_root(tmp_path)
    season = tmp_path / "clients" / "cpc" / "data" / "2026"
    shutil.copytree(CPC_DATA / "history", season / "history")
    (season / "week-08").mkdir()
    shutil.copy(CPC_DATA / "week-08" / "facts.json", season / "week-08" / "facts.json")
    monkeypatch.chdir(tmp_path)
    prime_nflverse(nfl_dir(tmp_path))
    clean = FakeWriter([STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2), DRAFT_BLURB, _passed(2), DRAFT_ROAST,
                        _passed(2)])
    assert cli.main(["midseason", "--client", "cpc", "--season", "2026", "--week", "8"], writer=clean,
                    provider=CPC_PROVIDER) == 0
    build = tmp_path / "clients" / "cpc" / "build" / "2026"
    (build / "sim.json").write_text("{}\n", encoding="utf-8")
    draft = json.loads((build / "midseason.json").read_text(encoding="utf-8"))
    draft["acts"][0]["chapters"][0]["blurb"]["sentences"][0]["text"] = "All You Need Is Love sits at 999."
    (build / "midseason.json").write_text(json.dumps(draft), encoding="utf-8")
    _git(tmp_path, "init", "-b", "main")
    capsys.readouterr()
    monkeypatch.setattr("sys.stdin", io.StringIO("y\n"))

    args = ["midseason-publish", "--client", "cpc", "--season", "2026", "--week", "8"]
    assert cli.main(args, writer=FakeWriter()) == 2
    out = capsys.readouterr().out
    assert "The blurb state fails the verifier" in out and "number 999" in out
    # The empty fake writer fails the Claude check of the clean roast, and a failed check is no pass.
    assert "The blurb state.roast has no verdict" in out
    assert not (tmp_path / "clients" / "cpc" / "published").exists()
