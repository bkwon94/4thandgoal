"""
The evidence-flags-eval command: it runs every Evidence flag question on each labeled past test at its round commit,
read through `git show`, and prints the hits, misses, and false flags of each question with its bar result.
"""
import json
import os
import subprocess
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from cornerstone.evidence_flags import WORKERS, Result, acceptance_tests, ask_test, evidence_entries, gets_request
from cornerstone.evidence_questions import BAR_FALSE_FLAG_RATE, BAR_HIT_RATE, QUESTIONS, Question
from league.jev_port import Jev

DEFAULT_LABELS = Path(__file__).parent / "evidence_labels.json"


@dataclass(frozen=True)
class Label:
    """One labeled past test: its spec, its round commit, its id, and `gap` with its kind, `defect`, or `pass`."""
    spec: str
    commit: str
    test: str
    label: str
    kind: str | None


class EvalError(Exception):
    """The eval cannot read a labeled test at its commit."""


def load_labels(path: Path) -> list[Label]:
    return [Label(each["spec"], each["commit"], each["test"], each["label"], each.get("kind"))
            for each in json.loads(path.read_text(encoding="utf-8"))["tests"]]


def _git_show(repo: Path, commit: str, path: str) -> bytes | None:
    """The bytes of `path` at `commit`, or None when the commit has no such file.

    Under the prek hook git sets GIT_DIR, which would point the call at the repo of the hook, so the call clears it.
    """
    env = {name: value for name, value in os.environ.items()
           if name not in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE")}
    shown = subprocess.run(["git", "show", f"{commit}:{path}"], check=False, cwd=repo, capture_output=True, env=env)
    return shown.stdout if shown.returncode == 0 else None


def _ask_label(repo: Path, label: Label, jev: Jev) -> Result:
    """Copy the test and its files at the commit into a temp folder, then ask every question of the module.

    A file that the commit lacks stays out, and the state names it as missing, as in a live run.
    """
    feature = f".scratch/{label.spec}"
    acceptance = _git_show(repo, label.commit, f"{feature}/ACCEPTANCE.md")
    evidence = _git_show(repo, label.commit, f"{feature}/EVIDENCE.md")
    if acceptance is None or evidence is None:
        raise EvalError(f"{label.spec} has no ACCEPTANCE.md and EVIDENCE.md at {label.commit}.")
    entries = evidence_entries(evidence.decode("utf-8"))
    if label.test not in entries or not gets_request(entries[label.test]):
        raise EvalError(f"{label.spec} {label.test} at {label.commit} has no entry with files in EVIDENCE.md.")
    entry = entries[label.test]
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        for path in entry.files:
            data = _git_show(repo, label.commit, f"{feature}/{path}")
            if data is not None:
                (folder / path).parent.mkdir(parents=True, exist_ok=True)
                (folder / path).write_bytes(data)
        accepted = acceptance_tests(acceptance.decode("utf-8")).get(label.test, {})
        return ask_test(label.test, accepted, entry, folder, jev, QUESTIONS)


@dataclass
class Row:
    """The counts of one question over the labeled tests."""
    question: Question
    hits: int = 0
    misses: int = 0
    gaps: int = 0
    false_flags: int = 0
    passes: int = 0
    errors: int = 0

    def meets_bar(self) -> bool:
        """At least half of the gaps of its kind flagged, and 10% or fewer of the PASS tests.

        With no gap of its kind or no answered PASS test, the eval cannot show the rate, so the question misses the bar.
        """
        return (self.gaps > 0 and self.passes > 0 and self.hits / self.gaps >= BAR_HIT_RATE
                and self.false_flags / self.passes <= BAR_FALSE_FLAG_RATE)

    def line(self) -> str:
        return (f"({self.question.key}) {self.question.name}, cut {self.question.cut:.2f}, kind {self.question.kind}: "
                f"{self.hits} hits, {self.misses} misses of {self.gaps} gaps, "
                f"{self.false_flags} false flags of {self.passes} pass tests, {self.errors} errors, "
                f"meets the bar: {'yes' if self.meets_bar() else 'no'}")


def score(labels: list[Label], results: list[Result]) -> list[Row]:
    """A row per question. A gap of the kind of the question is a hit with a flag and a miss with none. A flag on a
    PASS test is a false flag. A Jev error is an error only: never a hit, a miss, a false flag, or a pass. The gap
    of a test with an error still counts, so an error can never raise the hit rate.
    """
    rows = []
    for question in QUESTIONS:
        row = Row(question)
        for label, result in zip(labels, results, strict=True):
            target = label.label == "gap" and label.kind == question.kind
            row.gaps += target
            if result.error is not None:
                row.errors += 1
                continue
            flagged = any(flag.question.key == question.key for flag in result.flags)
            if target:
                row.hits += flagged
                row.misses += not flagged
            elif label.label == "pass":
                row.passes += 1
                row.false_flags += flagged
        rows.append(row)
    return rows


def run_evidence_eval(repo: Path, labels_path: Path, jev: Jev, echo: Callable[[str], None] = print) -> int:
    """Ask Jev about each labeled test, print each flag, a row per question, and one log line. It exits 2 when a
    labeled test cannot be read at its commit, and 0 otherwise, a Jev error too.
    """
    labels = load_labels(labels_path)
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            results = list(pool.map(lambda label: _ask_label(repo, label, jev), labels))
    except EvalError as err:
        echo(str(err))
        return 2
    for label, result in zip(labels, results, strict=True):
        name = f"{label.spec} {label.test} at {label.commit} ({label.label}{f', {label.kind}' if label.kind else ''})"
        if result.error is not None:
            echo(f"{name}: Jev error: {result.error}")
            continue
        flags = ", ".join(f"({flag.question.key}) {flag.probability:.2f}" for flag in result.flags) or "no flags"
        echo(f"{name}: {flags}{', cut' if result.cut else ''}")
    for row in score(labels, results):
        echo(row.line())
    echo(f"Evidence flags eval: {len(results)} tests, {sum(1 for r in results if r.error is not None)} errors, "
         f"{sum(r.tokens for r in results)} input tokens, {sum(1 for r in results if r.cut)} cut")
    return 0
