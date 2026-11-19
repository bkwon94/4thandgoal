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

    def test_evidence_tells_the_builder_to_write_the_rebuild_list(self):
        evidence = text(IMPLEMENT / "evidence.md")
        self.assertIn(".scratch/<slug>/REBUILD.md", evidence)
        self.assertIn("- <client> <file> <JSON path>: <reason>", evidence)
        self.assertIn("evidence/rebuild.log", evidence)

    def test_implement_judge_reads_the_rebuild_list(self):
        judge = text(IMPLEMENT / "judge.md")
        self.assertIn("REBUILD.md", judge)
        self.assertIn("evidence/rebuild.log", judge)

    def test_implement_judge_may_open_the_smoke_run(self):
        judge = text(IMPLEMENT / "judge.md")
        self.assertIn("evidence/smoke/", judge)
        self.assertIn("smoke.log", judge)


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

    def test_quick_judge_gets_the_rebuild_block_and_output(self):
        judge = text(QUICK / "judge.md")
        self.assertIn("`Rebuild:` block", judge)
        self.assertIn("output of the rebuild run", judge)

    def test_quick_judge_gets_the_paths_of_the_smoke_files(self):
        judge = text(QUICK / "judge.md")
        self.assertIn("the path of `smoke.log` and the path of each shot", judge)
        self.assertIn("Also open the `smoke.log` file", judge)

    def test_skill_runs_the_smoke_run_before_the_quick_judge(self):
        skill = text(QUICK / "SKILL.md")
        self.assertLess(skill.index("## Step 7: the smoke run"), skill.index("## Step 8: the quick Judge"))


if __name__ == "__main__":
    unittest.main()
