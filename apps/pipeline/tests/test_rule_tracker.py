"""
Checks that docs/agents/state.md at the repo root has one row for each feature with an open ticket, and no other row.
It reads the Status line of each tracked ticket under the root .scratch as text. See ADR 0014.
"""
import re
import subprocess
from pathlib import Path, PurePosixPath

from rule_report import Offense, clean_git_env, repo_root, report

ROOT = repo_root()
APPS = {"site", "pipeline"}
ADR = "docs/adr/0014-the-rules-are-checks.md"
STATE = "docs/agents/state.md"
CLOSED = {"done", "wontfix"}
# The nine statuses of a ticket. The first word of a Status line must be one of them.
STATUSES = {
    "needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "in-progress", "in-review", "blocked",
    *CLOSED,
}
# A Status line may be plain or bold. scripts/queue.py and the site rule read it the same way.
STATUS = re.compile(r"^(?:\*\*)?Status:(?:\*\*)?[ \t]*(\S*)")

MISSING_RULE = "each feature with an open ticket has a row in docs/agents/state.md"
STALE_RULE = "each row of docs/agents/state.md names a feature with an open ticket"
MISSING_FIX = "add a row to `docs/agents/state.md`."
STALE_FIX = "remove the row, because the feature is done."
STATUS_RULE = "the first word of the Status line of a ticket is one of the nine statuses"


def _tracked_scratch_files(root: Path) -> list[str]:
    """The paths under .scratch that git tracks, from the repo root.

    A local checkout holds untracked notes under .scratch, and they are not the tracker. Only the tracked
    files count, so the hook and CI read the same set.
    """
    result = subprocess.run(
        ["git", "ls-files", ".scratch"], cwd=root, check=True, capture_output=True, text=True, env=clean_git_env()
    )
    return result.stdout.splitlines()


def _word(match: re.Match) -> str:
    """The first word of a Status line, in lowercase with no trailing punctuation."""
    return match.group(1).lower().rstrip(".,;:")


# A ticket with no Status line has no triage yet, so it counts as open and its feature keeps a row.
def _is_open(ticket: Path) -> bool:
    """A ticket is open when the first word of its Status is not done and not wontfix.

    So "done 2026-10-24" is closed, and "built, waits on the review" is open.
    """
    for line in ticket.read_text().splitlines():
        match = STATUS.match(line)
        if match:
            return _word(match) not in CLOSED
    return True


def _ticket_key(path: str) -> tuple[str, str | None] | None:
    """The feature and the app of a ticket path, or None for a path that is not a ticket.

    A ticket is .scratch/<feature>/issues/<name>.md, with no app. A shared feature keeps a site and a pipeline
    subfolder, so its ticket is .scratch/<feature>/<app>/issues/<name>.md. A PRD does not count.
    """
    parts = PurePosixPath(path).parts
    if not parts or parts[0] != ".scratch" or not parts[-1].endswith(".md"):
        return None
    if len(parts) == 4 and parts[2] == "issues":
        return parts[1], None
    if len(parts) == 5 and parts[2] in APPS and parts[3] == "issues":
        return parts[1], parts[2]
    return None


def _open_features(root: Path, tracked: list[str]) -> set[tuple[str, str | None]]:
    """Each feature and app with an open ticket. The app is None for a feature with no subfolder."""
    features: set[tuple[str, str | None]] = set()
    for path in tracked:
        key = _ticket_key(path)
        if key and _is_open(root / path):
            features.add(key)
    return features


def _covers(row_feature: str, row_app: str, feature: str, app: str | None) -> bool:
    """A row covers an open ticket when it names the feature, and its App names the subfolder or is both.

    A ticket with no subfolder gives the rule no app, so any row of its feature covers it.
    """
    return row_feature == feature and (app is None or row_app in {app, "both"})


def _rows(state_path: Path) -> list[tuple[str, str, int]]:
    """The feature and the App of each table row, and its line. The header and the rule line do not count."""
    rows: list[tuple[str, str, int]] = []
    for number, text in enumerate(state_path.read_text().splitlines(), start=1):
        if not text.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in text.strip("|").split("|")]
        feature = cells[0]
        app = cells[1] if len(cells) > 1 else ""
        if feature not in {"Feature", ""} and not set(feature) <= {"-", ":"}:
            rows.append((feature, app, number))
    return rows


def _repo_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _missing_row_offenses(root: Path, tracked: list[str], state_path: Path) -> list[Offense]:
    # The row does not exist, so the offense names line 1 of the state file.
    rows = _rows(state_path)
    open_features = sorted(_open_features(root, tracked), key=lambda key: (key[0], key[1] or ""))
    return [Offense(
        path=_repo_path(state_path, root),
        line=1,
        rule_id="tracker/state-file",
        what=f"The feature {feature} has an open ticket and no row." if app is None
        else f"The feature {feature} has an open ticket in {app}/ and no row with the App {app}.",
        rule=MISSING_RULE,
        adr=ADR,
        fix=MISSING_FIX,
    ) for feature, app in open_features
        if not any(_covers(row_feature, row_app, feature, app) for row_feature, row_app, _ in rows)]


def _stale_row_offenses(root: Path, tracked: list[str], state_path: Path) -> list[Offense]:
    features = _open_features(root, tracked)
    return [Offense(
        path=_repo_path(state_path, root),
        line=line,
        rule_id="tracker/state-file",
        what=f"The row names {feature} with the App {row_app}, and {feature} has no open ticket there.",
        rule=STALE_RULE,
        adr=ADR,
        fix=STALE_FIX,
    ) for feature, row_app, line in _rows(state_path)
        if not any(_covers(feature, row_app, open_feature, app) for open_feature, app in features)]


def _odd_status_offenses(root: Path, tracked: list[str]) -> list[Offense]:
    """One offense for each ticket whose Status has a first word outside the nine statuses.

    A ticket with no Status line has no triage yet, so it is legal and open.
    """
    offenses: list[Offense] = []
    for path in tracked:
        if not _ticket_key(path):
            continue
        for number, text in enumerate((root / path).read_text().splitlines(), start=1):
            match = STATUS.match(text)
            if not match:
                continue
            word = _word(match)
            if word not in STATUSES:
                offenses.append(Offense(
                    path=path,
                    line=number,
                    rule_id="tracker/status",
                    what=f"The ticket has the status {word or 'none'}, and it is not one of the nine statuses.",
                    rule=STATUS_RULE,
                    adr=ADR,
                    fix="set the first word of the Status line to one of: " + ", ".join(sorted(STATUSES)) + ".",
                ))
            break
    return offenses


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


def test_an_open_quick_file_needs_no_row(tmp_path):
    for folder in ("bugs", "quick-wins"):
        quick = tmp_path / ".scratch" / folder
        quick.mkdir(parents=True)
        (quick / "fix-the-draw.md").write_text("# Fix the draw\n\nKind: bug\nStatus: in-progress\n")
    state_path = tmp_path / "state.md"
    state_path.write_text("| Feature | Next ticket | Blocked by | Hold |\n| --- | --- | --- | --- |\n")
    tracked = [".scratch/bugs/fix-the-draw.md", ".scratch/quick-wins/fix-the-draw.md"]
    assert _missing_row_offenses(tmp_path, tracked, state_path) == []
    assert _stale_row_offenses(tmp_path, tracked, state_path) == []
    assert _odd_status_offenses(tmp_path, tracked) == []


def test_the_rule_finds_a_row_with_no_open_ticket(tmp_path):
    issues = tmp_path / ".scratch" / "odds" / "issues"
    issues.mkdir(parents=True)
    (issues / "01-the-draw.md").write_text("# 01: The draw\n\n**Status:** done 2026-10-24\n")
    state_path = tmp_path / "state.md"
    state_path.write_text("| Feature | Next ticket | Blocked by | Hold |\n| --- | --- | --- | --- |\n| odds | 02 | | |\n")
    offenses = _stale_row_offenses(tmp_path, [".scratch/odds/issues/01-the-draw.md"], state_path)
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("state.md", 3, "tracker/state-file")]


def test_the_rule_counts_a_subfolder_ticket_for_its_app(tmp_path):
    # A shared feature keeps a site and a pipeline subfolder. The row for the site does not cover an open pipeline ticket.
    site = tmp_path / ".scratch" / "waiver" / "site" / "issues"
    pipeline = tmp_path / ".scratch" / "waiver" / "pipeline" / "issues"
    site.mkdir(parents=True)
    pipeline.mkdir(parents=True)
    (site / "01-the-route.md").write_text("# 01: The route\n\n**Status:** done\n")
    (pipeline / "09-usage-floor.md").write_text("# 09: The usage floor\n\n**Status:** needs-triage\n")
    tracked = [".scratch/waiver/site/issues/01-the-route.md", ".scratch/waiver/pipeline/issues/09-usage-floor.md"]
    state_path = tmp_path / "state.md"
    table = "| Feature | App | Next ticket | Blocked by | Hold |\n| --- | --- | --- | --- | --- |\n"
    state_path.write_text(table + "| `waiver` | site | 01 | none | |\n")
    offenses = _missing_row_offenses(tmp_path, tracked, state_path) + _stale_row_offenses(tmp_path, tracked, state_path)
    assert [(offense.line, offense.what) for offense in offenses] == [
        (1, "The feature waiver has an open ticket in pipeline/ and no row with the App pipeline."),
        (3, "The row names waiver with the App site, and waiver has no open ticket there."),
    ]
    state_path.write_text(table + "| `waiver` | pipeline | 09 | none | |\n")
    assert _missing_row_offenses(tmp_path, tracked, state_path) + _stale_row_offenses(tmp_path, tracked, state_path) == []


def test_the_rule_finds_a_ticket_with_an_odd_status(tmp_path):
    issues = tmp_path / ".scratch" / "zz-rule" / "issues"
    issues.mkdir(parents=True)
    (issues / "01-zz.md").write_text("# 01: Zz\n\n**Status:** backlog\n")
    offenses = _odd_status_offenses(tmp_path, [".scratch/zz-rule/issues/01-zz.md"])
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        (".scratch/zz-rule/issues/01-zz.md", 3, "tracker/status")]
    assert "backlog" in offenses[0].what


def test_a_ticket_with_no_status_line_passes(tmp_path):
    issues = tmp_path / ".scratch" / "zz-rule" / "issues"
    issues.mkdir(parents=True)
    (issues / "01-zz.md").write_text("# 01: Zz\n\nNo status yet.\n")
    (issues / "02-zz.md").write_text("# 02: Zz\n\n**Status:** done 2026-10-24\n")
    assert _odd_status_offenses(tmp_path, [".scratch/zz-rule/issues/01-zz.md", ".scratch/zz-rule/issues/02-zz.md"]) == []


def test_a_plain_status_line_and_a_capital_done_read_as_closed(tmp_path):
    issues = tmp_path / ".scratch" / "zz-rule" / "issues"
    issues.mkdir(parents=True)
    (issues / "01-zz.md").write_text("# 01: Zz\n\nStatus: Done\n")
    (issues / "02-zz.md").write_text("# 02: Zz\n\n**Status:** Done;\n")
    (issues / "03-zz.md").write_text("# 03: Zz\n\nStatus: backlog\n")
    tracked = [f".scratch/zz-rule/issues/0{n}-zz.md" for n in (1, 2, 3)]
    assert _open_features(tmp_path, tracked[:2]) == set()
    offenses = _odd_status_offenses(tmp_path, tracked)
    assert [(offense.path, offense.line) for offense in offenses] == [(".scratch/zz-rule/issues/03-zz.md", 3)]


def test_each_ticket_has_one_of_the_nine_statuses():
    offenses = _odd_status_offenses(ROOT, _tracked_scratch_files(ROOT))
    assert not offenses, report(offenses)
