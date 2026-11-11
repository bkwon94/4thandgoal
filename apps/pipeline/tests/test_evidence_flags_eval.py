"""
Tests for `cornerstone evidence-flags-eval`: it reads the label file, runs each question on each labeled test at its
commit through `git show`, and prints the hits, misses, false flags, and the bar result. FakeJev answers.
"""
import json
import subprocess
from collections import Counter
from pathlib import Path

from fakes import FakeJev
from rule_report import clean_git_env

from cornerstone import cli
from cornerstone.evidence_eval import DEFAULT_LABELS, load_labels
from cornerstone.evidence_questions import QUESTIONS
from league.jev_port import JevError

ACCEPTANCE = """# Demo: acceptance tests

AT-1: A clock window holds
App: pipeline
Given: A test egg with the clock window 11 PM to midnight ET.
When: POST its check at a time inside the window.
Then: The check inside the window matches.
Evidence: the test output of the check, with its time.

AT-2: The count shows
App: pipeline
Given: a week.
When: the build runs.
Then: The log gives the count.
Evidence: the log.
"""

ONE_PASSED = "1 passed in 0.25s\n"
CLOCK = "$ curl -s -X POST http://127.0.0.1:8080/eggs/check --time 23:30ET\n{\"match\":true}\n"


EVIDENCE = ("# Demo: evidence\n\n## AT-1: A clock window holds\n\nApp: pipeline\n"
            "Files: `evidence/AT-1/output.txt`\nObservation: The check matched.\n\n"
            "## AT-2: The count shows\n\nApp: pipeline\nFiles: `evidence/AT-2/output.txt`\nObservation: The count is 4.\n")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True,
                          env=clean_git_env()).stdout.strip()


def _commit(repo: Path, output_of_1: str) -> str:
    folder = repo / ".scratch" / "demo"
    for test in ("AT-1", "AT-2"):
        (folder / "evidence" / test).mkdir(parents=True, exist_ok=True)
    (folder / "ACCEPTANCE.md").write_text(ACCEPTANCE, encoding="utf-8")
    (folder / "EVIDENCE.md").write_text(EVIDENCE, encoding="utf-8")
    (folder / "evidence" / "AT-1" / "output.txt").write_text(output_of_1, encoding="utf-8")
    (folder / "evidence" / "AT-2" / "output.txt").write_text("count 4\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "round")
    return _git(repo, "rev-parse", "--short", "HEAD")


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    """A temp git repo with two rounds of a small feature, and a label file outside it.

    The first round has a fact that no file shows on AT-1. The second round shows it, and both tests pass.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    first = _commit(repo, ONE_PASSED)
    second = _commit(repo, CLOCK)
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({"tests": [
        {"spec": "demo", "commit": first, "test": "AT-1", "label": "gap", "kind": "fact"},
        {"spec": "demo", "commit": first, "test": "AT-2", "label": "defect"},
        {"spec": "demo", "commit": second, "test": "AT-1", "label": "pass"},
        {"spec": "demo", "commit": second, "test": "AT-2", "label": "pass"},
    ]}), encoding="utf-8")
    return repo, labels


def _fact_shown_unless_only_a_pass_line(key, question, state):
    """(a) says no file shows the fact when the only file is a pytest pass line. No other question flags."""
    if key.startswith("a_"):
        return 0.1 if ONE_PASSED in state["evidence"]["text_files"].values() else 0.95
    return 0.95 if key.startswith("d_shown") else 0.05


def test_the_eval_counts_hits_misses_and_false_flags_at_the_cut_and_gives_the_bar(tmp_path, capsys):
    repo, labels = _repo(tmp_path)
    jev = FakeJev(answer=_fact_shown_unless_only_a_pass_line)

    code = cli.main(["evidence-flags-eval", "--labels", str(labels), "--repo", str(repo)], jev=jev)

    out = capsys.readouterr().out
    assert code == 0
    # One request per labeled test, each with every question of the module.
    assert len(jev.requests) == 4
    rows = {line.split(" ", 1)[0]: line for line in out.splitlines() if line.startswith("(")}
    assert set(rows) == {"(a)", "(b)", "(c)", "(d)"}
    assert "1 hits, 0 misses of 1 gaps, 0 false flags of 2 pass tests, 0 errors" in rows["(a)"]
    assert rows["(a)"].endswith("meets the bar: yes")
    # No past gap has the kind of (b), so the eval cannot show that it catches one.
    assert "0 hits, 0 misses of 0 gaps" in rows["(b)"]
    assert rows["(b)"].endswith("meets the bar: no")
    assert out.strip().splitlines()[-1].startswith("Evidence flags eval: 4 tests, 0 errors, ")


def test_a_false_flag_rate_over_the_bar_does_not_meet_it(tmp_path, capsys):
    repo, labels = _repo(tmp_path)
    jev = FakeJev(answer=lambda key, question, state: 0.1 if key.startswith("a_") else 0.05)

    cli.main(["evidence-flags-eval", "--labels", str(labels), "--repo", str(repo)], jev=jev)

    row = next(line for line in capsys.readouterr().out.splitlines() if line.startswith("(a)"))
    assert "1 hits, 0 misses of 1 gaps, 2 false flags of 2 pass tests" in row
    assert row.endswith("meets the bar: no")


def test_a_jev_error_counts_each_test_as_an_error_never_as_a_miss_or_a_pass(tmp_path, capsys):
    repo, labels = _repo(tmp_path)
    jev = FakeJev(error=JevError("TypeSafeError: no API key"))

    code = cli.main(["evidence-flags-eval", "--labels", str(labels), "--repo", str(repo)], jev=jev)

    out = capsys.readouterr().out
    assert code == 0
    rows = [line for line in out.splitlines() if line.startswith("(")]
    assert len(rows) == 4
    for row in rows:
        assert "0 hits, 0 misses of 1 gaps" in row or "0 hits, 0 misses of 0 gaps" in row
        assert "0 false flags of 0 pass tests, 4 errors" in row
        assert row.endswith("meets the bar: no")
    assert out.strip().splitlines()[-1].startswith("Evidence flags eval: 4 tests, 4 errors, 0 input tokens")


def test_the_label_file_holds_the_past_labels_and_each_gap_has_the_kind_of_a_question():
    labels = load_labels(DEFAULT_LABELS)

    assert len(labels) == 56
    assert Counter(label.label for label in labels) == {"gap": 7, "defect": 5, "pass": 44}
    kinds = {question.kind for question in QUESTIONS}
    assert all(label.kind in kinds for label in labels if label.label == "gap")
    assert all(label.kind is None for label in labels if label.label != "gap")
    assert len({(label.spec, label.commit, label.test) for label in labels}) == 56
