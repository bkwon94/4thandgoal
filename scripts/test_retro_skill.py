"""
Tests the skill text of 4ag:retro, and the end of 4ag:quick and 4ag:implement that names it (AT-17, AT-8, AT-9, AT-19).
Each case reads the real skill files and checks what they name.
"""
import re
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / ".claude" / "plugin" / "skills"
RETRO = SKILLS / "retro" / "SKILL.md"
QUICK = SKILLS / "quick" / "SKILL.md"
IMPLEMENT = SKILLS / "implement"


def section(text: str, heading: str) -> str:
    """The text under one level-two heading, up to the next level-two heading."""
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"no section {heading}"
    return match.group(1)


class RetroSkillTest(unittest.TestCase):
    def setUp(self):
        self.skill = RETRO.read_text()

    def test_retro_starts_with_the_merge_sweep(self):
        queue = section(self.skill, "The queue")
        self.assertIn("python3 scripts/queue.py sweep", queue)

    def test_retro_checks_for_writing_for_agents(self):
        self.assertIn("`writing-for-agents`", section(self.skill, "Before you start"))

    def test_retro_takes_four_inputs_with_the_current_session_as_the_default(self):
        invocation = section(self.skill, "Invocation")
        for command in ("`/4ag:retro`", "`/4ag:retro <PR number>`", "`/4ag:retro <quick file>`",
                        "`/4ag:retro <feature slug>`"):
            self.assertIn(command, invocation)
        self.assertRegex(invocation, r"(?i)no argument[^\n]*current session")

    def test_retro_reads_the_claude_log_and_the_codex_log(self):
        self.assertIn("~/.claude/projects/", self.skill)
        self.assertIn("~/.codex/sessions/", self.skill)
        self.assertRegex(self.skill, r"(?i)no log match")

    def test_retro_prints_the_stage_times(self):
        self.assertIn("<stage>: <minutes> min", self.skill)

    def test_retro_drops_a_candidate_with_no_moment_in_the_log(self):
        self.assertRegex(self.skill, r"(?i)drop each candidate with no moment")

    def test_retro_maps_each_category_to_its_place(self):
        table = section(self.skill, "The categories")
        rows = {
            "A mechanical mistake": "rule test",
            "A judgement mistake": "CODING_STANDARDS.md",
            "A slow search": "pointer",
            "4ag` skill text": "change to that skill",
            "A costly tool call": "cheaper tool",
            "changes nothing": "delete",
            "could not reach": "access",
        }
        for category, place in rows.items():
            row = next((line for line in table.splitlines() if category in line), None)
            self.assertIsNotNone(row, category)
            self.assertIn(place, row, category)
        self.assertRegex(table, r"(?i)exists but is not connected[^\n]*connect")

    def test_retro_proposes_coding_standards_at_the_first_judgement_rule(self):
        self.assertRegex(self.skill, r"(?i)first[^\n]*judgement rule[^\n]*CODING_STANDARDS\.md")

    def test_retro_keeps_rules_out_of_agents_md(self):
        self.assertRegex(self.skill, r"(?i)never[^\n]*rule[^\n]*`AGENTS\.md`")

    def test_retro_files_each_accepted_number_with_queue_add(self):
        self.assertIn("python3 scripts/queue.py add", self.skill)
        for name in ("`Bugs`", "`Quick Wins`", "`Ideas`"):
            self.assertIn(name, self.skill)
        self.assertRegex(self.skill, r"(?i)in order of severity")

    def test_retro_checks_each_task_for_a_manager_name(self):
        self.assertIn("users.json", self.skill)
        self.assertIn("Hits: none.", self.skill)

    def test_retro_changes_no_repo_file(self):
        self.assertRegex(self.skill, r"(?i)writes? no (repo )?file|changes? no repo file")

    def test_retro_copies_the_full_timestamp_of_the_log_line(self):
        find = section(self.skill, "Step 5: find the candidates")
        self.assertIn("`timestamp`", find)
        self.assertRegex(find, r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z")
        self.assertRegex(find, r"(?i)`grep`")

    def test_retro_names_each_record_file_and_each_ci_run_that_it_read(self):
        record = section(self.skill, "Step 2: read the record of the run")
        self.assertRegex(record, r"(?i)name each record file[^\n]*CI run")
        self.assertRegex(section(self.skill, "Step 3: find the session logs"), r"(?i)name each log file[^\n]*full path")

    def test_retro_says_no_log_matched_when_no_log_is_left_in_the_time_window(self):
        logs = section(self.skill, "Step 3: find the session logs")
        self.assertRegex(logs, r"(?i)no log is left after")

    def test_retro_files_an_ideas_task_with_its_draft_outcome_statement(self):
        filing = section(self.skill, "Step 7: file each accepted candidate")
        self.assertRegex(filing, r"(?i)`Ideas`[^\n]*draft outcome statement")

    def test_retro_keeps_each_stage_line_to_its_shape(self):
        stages = section(self.skill, "Step 4: give the stage times")
        self.assertRegex(stages, r"(?i)note on its own line")


class RetroEndLineTest(unittest.TestCase):
    def test_quick_end_names_retro_as_an_option(self):
        end = section(QUICK.read_text(), "The end")
        self.assertIn("/4ag:retro <PR number>", end)

    def test_implement_end_names_retro_as_an_option(self):
        end = section((IMPLEMENT / "SKILL.md").read_text(), "The end")
        self.assertIn("/4ag:retro <PR number>", end)

    def test_no_other_part_of_quick_or_implement_names_retro(self):
        files = [QUICK] + sorted(IMPLEMENT.glob("*.md"))
        for path in files:
            text = path.read_text()
            rest = text.replace(section(text, "The end"), "") if "## The end" in text else text
            self.assertNotIn("retro", rest.lower(), path.name)


if __name__ == "__main__":
    unittest.main()
