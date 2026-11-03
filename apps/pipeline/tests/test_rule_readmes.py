"""
Checks that each package folder under src holds a README.md with the headings Knows, Ports, and Does not do.
Each README is under 25 lines, and the only CLAUDE.md is the one at the repo root. See ADR 0009.
"""
import subprocess
from pathlib import Path

from rule_report import Offense, clean_git_env, report

ROOT = Path(__file__).resolve().parent.parent
ADR = "docs/adr/0009-the-rules-are-checks.md"
HEADINGS = ["## Knows", "## Ports", "## Does not do"]
# An agent reads the README to decide whether to open the folder. A short README means an agent reads little.
MAX_LINES = 24

MISSING_RULE = "each folder under src that holds an __init__.py holds a README.md"
HEADINGS_RULE = "a package README has a one-line title, then the headings Knows, Ports, and Does not do, in that order"
HEADINGS_FIX = "give the README a title on line 1, then exactly ## Knows, ## Ports, and ## Does not do, in that order."
LENGTH_RULE = "a package README is under 25 lines"
CLAUDE_MD_RULE = "the only CLAUDE.md is the one at the repo root"


def _package_folders(root: Path) -> list[Path]:
    """Each folder under src that holds an __init__.py."""
    return sorted(path.parent for path in (root / "src").rglob("__init__.py"))


def _readmes(root: Path) -> list[Path]:
    return [folder / "README.md" for folder in _package_folders(root) if (folder / "README.md").is_file()]


def _repo_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _missing_offenses(root: Path) -> list[Offense]:
    # The README does not exist, so the offense names line 1 of the __init__.py that makes the folder a package.
    return [Offense(
        path=_repo_path(folder / "__init__.py", root),
        line=1,
        rule_id="readme/missing",
        what=f"{_repo_path(folder, root)} holds an __init__.py and no README.md.",
        rule=MISSING_RULE,
        adr=ADR,
        fix=f"add {_repo_path(folder, root)}/README.md with a title and the headings Knows, Ports, and Does not do.",
    ) for folder in _package_folders(root) if not (folder / "README.md").is_file()]


def _heading_offenses(root: Path) -> list[Offense]:
    offenses: list[Offense] = []
    for readme in _readmes(root):
        lines = readme.read_text().splitlines()
        headings = [line for line in lines if line.startswith("#")]
        has_title = bool(lines) and lines[0].startswith("# ")
        if not has_title or headings[1:] != HEADINGS:
            offenses.append(Offense(
                path=_repo_path(readme, root),
                line=1,
                rule_id="readme/headings",
                what=f"The headings are: {', '.join(headings) or 'none'}.",
                rule=HEADINGS_RULE,
                adr=ADR,
                fix=HEADINGS_FIX,
            ))
    return offenses


def _length_offenses(root: Path) -> list[Offense]:
    offenses: list[Offense] = []
    for readme in _readmes(root):
        count = len(readme.read_text().splitlines())
        if count > MAX_LINES:
            offenses.append(Offense(
                path=_repo_path(readme, root),
                line=MAX_LINES + 1,
                rule_id="readme/length",
                what=f"The README has {count} lines.",
                rule=LENGTH_RULE,
                adr=ADR,
                fix=f"cut the README to {MAX_LINES} lines, and move each detail to the docstring of its module.",
            ))
    return offenses


def _tracked_files(root: Path) -> list[str]:
    """The paths that git tracks, from the repo root. A staged file counts, so the hook sees a new one."""
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True, env=clean_git_env()
    )
    return result.stdout.splitlines()


def _claude_md_offenses(tracked: list[str]) -> list[Offense]:
    # A nested CLAUDE.md loads by itself. The agent must choose to read the next level, so the folder holds a README.
    return [Offense(
        path=path,
        line=1,
        rule_id="readme/no-claude-md",
        what=f"{path} is a CLAUDE.md below the repo root.",
        rule=CLAUDE_MD_RULE,
        adr=ADR,
        fix="move the text to the README.md of the folder, and remove the CLAUDE.md.",
    ) for path in tracked if Path(path).name == "CLAUDE.md" and path != "CLAUDE.md"]


def test_each_package_folder_has_a_readme():
    offenses = _missing_offenses(ROOT)
    assert not offenses, report(offenses)


def test_each_readme_has_the_three_headings():
    offenses = _heading_offenses(ROOT)
    assert not offenses, report(offenses)


def test_each_readme_is_under_25_lines():
    offenses = _length_offenses(ROOT)
    assert not offenses, report(offenses)


def test_no_claude_md_below_the_root():
    offenses = _claude_md_offenses(_tracked_files(ROOT))
    assert not offenses, report(offenses)


def test_the_rule_finds_a_package_folder_with_no_readme(tmp_path):
    package = tmp_path / "src" / "cornerstone"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""A package."""\n')
    assert _missing_offenses(tmp_path) == [Offense(
        path="src/cornerstone/__init__.py",
        line=1,
        rule_id="readme/missing",
        what="src/cornerstone holds an __init__.py and no README.md.",
        rule=MISSING_RULE,
        adr=ADR,
        fix="add src/cornerstone/README.md with a title and the headings Knows, Ports, and Does not do.",
    )]


def test_the_rule_finds_a_readme_of_25_lines(tmp_path):
    package = tmp_path / "src" / "cornerstone"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""A package."""\n')
    (package / "README.md").write_text("# cornerstone\n" + "\n" * 24)
    offenses = _length_offenses(tmp_path)
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("src/cornerstone/README.md", 25, "readme/length")]


def test_the_rule_finds_a_claude_md_below_the_root():
    offenses = _claude_md_offenses(["CLAUDE.md", "src/cornerstone/CLAUDE.md"])
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("src/cornerstone/CLAUDE.md", 1, "readme/no-claude-md")]


def test_the_rule_finds_a_readme_with_no_ports_heading(tmp_path):
    package = tmp_path / "src" / "cornerstone"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""A package."""\n')
    (package / "README.md").write_text("# cornerstone\n\n## Knows\n\nThe facts.\n\n## Does not do\n\nNo prose.\n")
    assert _heading_offenses(tmp_path) == [Offense(
        path="src/cornerstone/README.md",
        line=1,
        rule_id="readme/headings",
        what="The headings are: # cornerstone, ## Knows, ## Does not do.",
        rule=HEADINGS_RULE,
        adr=ADR,
        fix=HEADINGS_FIX,
    )]
