"""
Tests the skill text of 4ag:implement and 4ag:quick for the smoke run (AT-12, AT-13).
Each case reads the real skill files and checks that they name the smoke run, its folder, the stop, and the blocks.
"""
import re
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / ".claude" / "plugin" / "skills"
IMPLEMENT = SKILLS / "implement"
QUICK = SKILLS / "quick"


def text(path: Path) -> str:
    return path.read_text()


class ImplementSmokeTest(unittest.TestCase):
    def test_skill_names_the_smoke_run_in_the_evidence_stage_before_the_judge(self):
        skill = text(IMPLEMENT / "SKILL.md")
        stage_3 = re.search(r"^3\. \*\*The evidence\.\*\*(.+)$", skill, re.M).group(1)
        self.assertRegex(stage_3, r"(?i)smoke run")
        self.assertRegex(skill, r"(?i)red smoke run[^\n]*Judge")

    def test_evidence_names_the_smoke_folder(self):
        evidence = text(IMPLEMENT / "evidence.md")
        self.assertIn("smoke/", evidence)
        self.assertIn("smoke.log", evidence)
        self.assertIn("pnpm --dir apps/site smoke --out", evidence)

    def test_a_red_run_stops_before_the_judge(self):
        evidence = text(IMPLEMENT / "evidence.md")
        self.assertRegex(evidence, r"(?i)red smoke run")
        self.assertRegex(evidence, r"(?i)stop[^\n]*before the Judge|before the Judge[^\n]*stop")


class QuickSmokeTest(unittest.TestCase):
    def test_format_names_the_smoke_block_and_the_rebuild_block(self):
        fmt = text(QUICK / "format.md")
        self.assertRegex(fmt, r"(?m)^Smoke:")
        self.assertRegex(fmt, r"(?m)^Rebuild:")

    def test_rebuild_block_lines_have_the_shape_that_the_rebuild_check_reads(self):
        fmt = text(QUICK / "format.md")
        self.assertIn("- <client> <file> <JSON path>: <reason>", fmt)

    def test_judge_brief_asks_the_third_question(self):
        judge = text(QUICK / "judge.md")
        self.assertIn("Does the smoke run show the changed flow at work?", judge)

    def test_skill_runs_the_smoke_run_before_the_quick_judge(self):
        skill = text(QUICK / "SKILL.md")
        self.assertLess(skill.index("## Step 7: the smoke run"), skill.index("## Step 8: the quick Judge"))


if __name__ == "__main__":
    unittest.main()
