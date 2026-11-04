"""
Checks that no comment in src or tests silences a rule of ruff or pyright, unless the allow list holds its line.
It reads each line as text and imports no pipeline code. See ADR 0014.
"""
import ast
import re
from pathlib import Path

from rule_report import Offense, report

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = ("src", "tests")
ADR = "docs/adr/0014-the-rules-are-checks.md"
RULE = "no comment silences a rule"
FIX = "fix the type or the code, or add the line to the allow list of this test with its reason"

# Each pattern is two parts, so this file holds no match and the rule needs no file exclusion.
MARKER = "no" + "qa"
PATTERNS = [MARKER, "type" + r":\s*ignore", "pyright" + r":\s*ignore"]
SUPPRESSION = re.compile("|".join(PATTERNS), re.IGNORECASE)

# The allow list is the only place a suppression may live. ruff owns BLE001 and RUF009, and we do not
# turn a ruff rule off to clear a marker. ruff 0.17.3 enables both rules by default, so each marker silences a
# real offense. The key is the path from the repo root and the line text with no indent, not the line number.
# So an entry does not go stale when a line above it moves. The value is the reason.
ALLOW: dict[tuple[str, str], str] = {
    ("src/cornerstone/render.py",
     f"except Exception as exc:  # {MARKER}: BLE001 - a build never stops on one avatar"):
        "a build never stops on one avatar",
    ("src/cornerstone/pipeline.py",
     f"except Exception as err:  # {MARKER}: BLE001 - the outer guard: the module catches only HTTP errors"):
        "the outer guard: the module catches only HTTP errors",
}
# The allow list of the league package is in packages/league/python/tests/test_rule_league.py.


def _suppressions(root: Path) -> list[tuple[str, int, str]]:
    """Each line under src and tests that holds a suppression: the path from the root, the line, and the text."""
    found: list[tuple[str, int, str]] = []
    for folder in FOLDERS:
        for path in sorted((root / folder).rglob("*.py")):
            for number, text in enumerate(path.read_text().splitlines(), start=1):
                if SUPPRESSION.search(text):
                    found.append((path.relative_to(root).as_posix(), number, text.strip()))
    return found


def _comment_offenses(root: Path, allow: dict[tuple[str, str], str] = ALLOW) -> list[Offense]:
    return [Offense(
        path=path,
        line=number,
        rule_id="suppression/comment",
        what=f"The line holds a suppression comment: {text}",
        rule=RULE,
        adr=ADR,
        fix=FIX,
    ) for path, number, text in _suppressions(root) if (path, text) not in allow]


def _allow_lines() -> dict[tuple[str, str], int]:
    """The line of each key of ALLOW in this file, so a stale-entry offense names the line to remove."""
    for node in ast.parse(Path(__file__).read_text()).body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "ALLOW":
            assert isinstance(node.value, ast.Dict)
            # The dict keeps the order of its source, so the keys of ALLOW and of the node pair up.
            return {key: node_key.lineno for key, node_key in zip(ALLOW, node.value.keys) if node_key is not None}
    raise AssertionError("tests/test_rule_suppressions.py has no ALLOW dict.")


def _stale_entry_offenses(root: Path, allow: dict[tuple[str, str], str] = ALLOW) -> list[Offense]:
    found = {(path, text) for path, _, text in _suppressions(root)}
    lines = _allow_lines()
    return [Offense(
        # ALLOW is in this file for any root, so the path is from the root of this repo.
        path=Path(__file__).resolve().relative_to(ROOT).as_posix(),
        # A key from a list other than ALLOW has no line in this file, so the offense names line 1.
        line=lines.get(key, 1),
        rule_id="suppression/stale-allow",
        what=f"The allow list names a line of {key[0]} that no file holds: {key[1]}",
        rule=RULE,
        adr=ADR,
        fix="remove the entry from the allow list",
    ) for key in allow if key not in found]


def test_no_comment_silences_a_rule():
    offenses = _comment_offenses(ROOT)
    assert not offenses, report(offenses)


def test_the_allow_list_names_only_lines_that_exist():
    offenses = _stale_entry_offenses(ROOT)
    assert not offenses, report(offenses)


def test_the_rule_finds_a_type_ignore_line(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "models.py").write_text('"""A model module."""\nvalue: int = "one"  # type' + ": ignore\n")
    assert _comment_offenses(tmp_path) == [Offense(
        path="src/models.py",
        line=2,
        rule_id="suppression/comment",
        what='The line holds a suppression comment: value: int = "one"  # type' + ": ignore",
        rule=RULE,
        adr=ADR,
        fix=FIX,
    )]


def test_the_rule_finds_a_stale_entry(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "models.py").write_text('"""A model module."""\nvalue: int = 1\n')
    allow = {("src/models.py", "value: int = 1  # type" + ": ignore"): "a reason"}
    offenses = _stale_entry_offenses(tmp_path, allow)
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("tests/test_rule_suppressions.py", 1, "suppression/stale-allow")]
