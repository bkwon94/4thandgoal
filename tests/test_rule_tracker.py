"""
Checks that docs/agents/state.md has one row for each feature with an open ticket, and no other row.
It reads the Status line of each tracked ticket under .scratch as text. See ADR 0009.
"""
import re
import subprocess
from pathlib import Path, PurePosixPath

from rule_report import Offense, report

ROOT = Path(__file__).resolve().parent.parent
ADR = "docs/adr/0009-the-rules-are-checks.md"
STATE = "docs/agents/state.md"
CLOSED = {"done", "wontfix"}
STATUS = re.compile(r"^\*\*Status:\*\*\s*(\S*)")

MISSING_RULE = "each feature with an open ticket has a row in docs/agents/state.md"
STALE_RULE = "each row of docs/agents/state.md names a feature with an open ticket"
MISSING_FIX = "add a row to `docs/agents/state.md`."
STALE_FIX = "remove the row, because the feature is done."


def _tracked_scratch_files(root: Path) -> list[str]:
    """The paths under .scratch that git tracks, from the repo root.

    A local checkout holds untracked notes under .scratch, and they are not the tracker. Only the tracked
    files count, so the hook and CI read the same set.
    """
    result = subprocess.run(["git", "ls-files", ".scratch"], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.splitlines()


# A ticket with no Status line has no triage yet, so it counts as open and its feature keeps a row.
def _is_open(ticket: Path) -> bool:
    """A ticket is open when the first word of its Status is not done and not wontfix.

    So "done 2026-10-24" is closed, and "built, waits on the review" is open.
    """
    for line in ticket.read_text().splitlines():
        match = STATUS.match(line)
        if match:
            return match.group(1).lower().rstrip(".,") not in CLOSED
    return True


def _open_features(root: Path, tracked: list[str]) -> set[str]:
    """Each feature with an open ticket. A ticket is .scratch/<feature>/issues/<name>.md. A PRD does not count."""
    features: set[str] = set()
    for path in tracked:
        parts = PurePosixPath(path).parts
        is_ticket = len(parts) == 4 and parts[0] == ".scratch" and parts[2] == "issues" and parts[3].endswith(".md")
        if is_ticket and _is_open(root / path):
            features.add(parts[1])
    return features


def _rows(state_path: Path) -> dict[str, int]:
    """The feature in the first cell of each table row, and its line. The header and the rule line do not count."""
    rows: dict[str, int] = {}
    for number, text in enumerate(state_path.read_text().splitlines(), start=1):
        if not text.startswith("|"):
            continue
        feature = text.strip("|").split("|")[0].strip().strip("`")
        if feature not in {"Feature", ""} and not set(feature) <= {"-", ":"}:
            rows[feature] = number
    return rows


def _repo_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _missing_row_offenses(root: Path, tracked: list[str], state_path: Path) -> list[Offense]:
    # The row does not exist, so the offense names line 1 of the state file.
    rows = _rows(state_path)
    return [Offense(
        path=_repo_path(state_path, root),
        line=1,
        rule_id="tracker/state-file",
        what=f"The feature {feature} has an open ticket and no row.",
        rule=MISSING_RULE,
        adr=ADR,
        fix=MISSING_FIX,
    ) for feature in sorted(_open_features(root, tracked)) if feature not in rows]


def _stale_row_offenses(root: Path, tracked: list[str], state_path: Path) -> list[Offense]:
    features = _open_features(root, tracked)
    return [Offense(
        path=_repo_path(state_path, root),
        line=line,
        rule_id="tracker/state-file",
        what=f"The row names {feature}, and {feature} has no open ticket.",
        rule=STALE_RULE,
        adr=ADR,
        fix=STALE_FIX,
    ) for feature, line in _rows(state_path).items() if feature not in features]


def test_each_open_feature_has_a_row():
    offenses = _missing_row_offenses(ROOT, _tracked_scratch_files(ROOT), ROOT / STATE)
    assert not offenses, report(offenses)


def test_each_row_names_an_open_feature():
    offenses = _stale_row_offenses(ROOT, _tracked_scratch_files(ROOT), ROOT / STATE)
    assert not offenses, report(offenses)


def test_the_rule_finds_an_open_feature_with_no_row(tmp_path):
    issues = tmp_path / ".scratch" / "odds" / "issues"
    issues.mkdir(parents=True)
    (issues / "01-the-draw.md").write_text("# 01: The draw\n\n**Status:** ready-for-agent\n")
    state_path = tmp_path / "docs" / "agents" / "state.md"
    state_path.parent.mkdir(parents=True)
    state_path.write_text("")
    tracked = [".scratch/odds/issues/01-the-draw.md"]
    offenses = _missing_row_offenses(tmp_path, tracked, state_path) + _stale_row_offenses(tmp_path, tracked, state_path)
    assert offenses == [Offense(
        path="docs/agents/state.md",
        line=1,
        rule_id="tracker/state-file",
        what="The feature odds has an open ticket and no row.",
        rule=MISSING_RULE,
        adr=ADR,
        fix=MISSING_FIX,
    )]


def test_the_rule_finds_a_row_with_no_open_ticket(tmp_path):
    issues = tmp_path / ".scratch" / "odds" / "issues"
    issues.mkdir(parents=True)
    (issues / "01-the-draw.md").write_text("# 01: The draw\n\n**Status:** done 2026-10-24\n")
    state_path = tmp_path / "state.md"
    state_path.write_text("| Feature | Next ticket | Blocked by | Hold |\n| --- | --- | --- | --- |\n| odds | 02 | | |\n")
    offenses = _stale_row_offenses(tmp_path, [".scratch/odds/issues/01-the-draw.md"], state_path)
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("state.md", 3, "tracker/state-file")]
