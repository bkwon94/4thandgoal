"""
Checks that the Claude Code skills and the Codex skills share one source: each skill has a 4ag symlink, each CLAUDE.md holds
only @AGENTS.md, and no skill file names a tool that only Claude Code has. See ADR 0014.
"""
from pathlib import Path

from rule_report import Offense, repo_root, report, tracked_files

ROOT = repo_root()
ADR = "docs/adr/0014-the-rules-are-checks.md"
SKILLS = ".claude/plugin/skills"
LINKS = ".agents/skills"

CLAUDE_MD_RULE = "each CLAUDE.md holds the one line @AGENTS.md"
CLAUDE_MD_FIX = "make the file hold only the line @AGENTS.md, and move the rest to the AGENTS.md of the same folder."
TOOL_RULE = "a skill file does not name the Skill tool or the Agent tool, because Codex has neither"
# The skills use neutral words, and AGENTS.md maps each word to the tool of each harness.
TOOL_FIX = "write the neutral word from the table in AGENTS.md, such as load the skill or start a fresh subagent."
CLAUDE_ONLY_TOOLS = ("Skill tool", "Agent tool")

SYMLINK_RULE = "each skill under .claude/plugin/skills has a tracked symlink .agents/skills/4ag-<name> that resolves to it"


def _skill_names(tracked: list[str]) -> list[str]:
    """The name of each skill folder that holds a tracked SKILL.md."""
    parts = [path.split("/") for path in tracked if path.startswith(f"{SKILLS}/")]
    return sorted(part[-2] for part in parts if len(part) == 5 and part[-1] == "SKILL.md")


def _symlink_offenses(root: Path, tracked: list[str]) -> list[Offense]:
    offenses: list[Offense] = []
    for name in _skill_names(tracked):
        link = f"{LINKS}/4ag-{name}"
        folder = root / SKILLS / name
        resolves = link in tracked and (root / link).is_symlink() and (root / link).resolve() == folder.resolve()
        if not resolves:
            offenses.append(Offense(
                path=f"{SKILLS}/{name}/SKILL.md",
                line=1,
                rule_id="harness/symlink",
                what=f"The skill {name} has no tracked symlink {link} that resolves to it.",
                rule=SYMLINK_RULE,
                adr=ADR,
                fix=f"run ln -s ../../{SKILLS}/{name} {link}, then stage the symlink.",
            ))
    return offenses


def _import_line_offenses(root: Path, tracked: list[str]) -> list[Offense]:
    # Codex reads AGENTS.md. A CLAUDE.md that holds only the import keeps one source for both harnesses.
    offenses: list[Offense] = []
    for path in tracked:
        if Path(path).name != "CLAUDE.md":
            continue
        lines = (root / path).read_text().splitlines()
        if [line.strip() for line in lines] != ["@AGENTS.md"]:
            offenses.append(Offense(
                path=path,
                line=1,
                rule_id="harness/claude-md",
                what=f"{path} holds {len(lines)} lines, and not only @AGENTS.md.",
                rule=CLAUDE_MD_RULE,
                adr=ADR,
                fix=CLAUDE_MD_FIX,
            ))
    return offenses


def _tool_word_offenses(root: Path, tracked: list[str]) -> list[Offense]:
    offenses: list[Offense] = []
    for path in tracked:
        if not path.startswith(f"{SKILLS}/") or not (root / path).is_file():
            continue
        try:
            lines = (root / path).read_text().splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            for word in CLAUDE_ONLY_TOOLS:
                if word in line:
                    offenses.append(Offense(
                        path=path,
                        line=number,
                        rule_id="harness/tool-word",
                        what=f'The line holds "{word}".',
                        rule=TOOL_RULE,
                        adr=ADR,
                        fix=TOOL_FIX,
                    ))
    return offenses


def test_each_skill_has_a_symlink_that_resolves_to_it():
    offenses = _symlink_offenses(ROOT, tracked_files(ROOT))
    assert not offenses, report(offenses)


def test_the_rule_finds_a_skill_with_no_symlink(tmp_path):
    (tmp_path / SKILLS / "review").mkdir(parents=True)
    (tmp_path / SKILLS / "plan").mkdir(parents=True)
    (tmp_path / LINKS).mkdir(parents=True)
    (tmp_path / LINKS / "4ag-plan").symlink_to(f"../../{SKILLS}/plan")
    tracked = [f"{SKILLS}/review/SKILL.md", f"{SKILLS}/plan/SKILL.md", f"{LINKS}/4ag-plan"]
    offenses = _symlink_offenses(tmp_path, tracked)
    assert [(offense.path, offense.rule_id) for offense in offenses] == [
        (f"{SKILLS}/review/SKILL.md", "harness/symlink")]
    assert "4ag-review" in offenses[0].what


def test_the_rule_finds_a_symlink_that_resolves_to_another_skill(tmp_path):
    (tmp_path / SKILLS / "review").mkdir(parents=True)
    (tmp_path / SKILLS / "plan").mkdir(parents=True)
    (tmp_path / LINKS).mkdir(parents=True)
    (tmp_path / LINKS / "4ag-review").symlink_to(f"../../{SKILLS}/plan")
    tracked = [f"{SKILLS}/review/SKILL.md", f"{LINKS}/4ag-review"]
    assert [offense.rule_id for offense in _symlink_offenses(tmp_path, tracked)] == ["harness/symlink"]


def test_each_claude_md_holds_only_the_agents_import():
    offenses = _import_line_offenses(ROOT, tracked_files(ROOT))
    assert not offenses, report(offenses)


def test_the_rule_finds_a_claude_md_with_an_extra_line(tmp_path):
    (tmp_path / "apps" / "site").mkdir(parents=True)
    (tmp_path / "CLAUDE.md").write_text("@AGENTS.md\n")
    (tmp_path / "apps" / "site" / "CLAUDE.md").write_text("@AGENTS.md\nExtra rule.\n")
    offenses = _import_line_offenses(tmp_path, ["CLAUDE.md", "apps/site/CLAUDE.md", "AGENTS.md"])
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("apps/site/CLAUDE.md", 1, "harness/claude-md")]


def test_the_rule_finds_a_claude_md_with_no_import(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("Rules of the repo.\n")
    assert [offense.rule_id for offense in _import_line_offenses(tmp_path, ["CLAUDE.md"])] == ["harness/claude-md"]


def test_no_skill_file_names_a_claude_only_tool():
    offenses = _tool_word_offenses(ROOT, tracked_files(ROOT))
    assert not offenses, report(offenses)


def test_the_rule_finds_a_tool_word_in_a_skill_file(tmp_path):
    folder = tmp_path / SKILLS / "to-spec"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("Start.\nCall the Skill tool for to-spec.\nUse the Agent tool.\n")
    (tmp_path / "AGENTS.md").write_text("The Skill tool maps to a Codex word.\n")
    offenses = _tool_word_offenses(tmp_path, [f"{SKILLS}/to-spec/SKILL.md", "AGENTS.md"])
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        (f"{SKILLS}/to-spec/SKILL.md", 2, "harness/tool-word"),
        (f"{SKILLS}/to-spec/SKILL.md", 3, "harness/tool-word")]
