"""
Tests the Test verdict rule of scripts/verdict.py with a real acceptance file and real comment text.
Each case reads its files from scripts/fixtures/verdict/. See ADR 0020.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

from verdict import judge, latest_verdict_comment

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "verdict"
ACCEPTANCE = (FIXTURES / "ACCEPTANCE.md").read_text()


def comment(name: str) -> str:
    return (FIXTURES / name).read_text()


def rule_ids(result) -> list[str]:
    return [offense.rule_id for offense in result.offenses]


class TheVerdictRule(unittest.TestCase):
    def test_all_pass_passes(self):
        result = judge(ACCEPTANCE, comment("all-pass.md"))
        self.assertTrue(result.passed, result.report())
        self.assertEqual(result.report(), "0 offenses. AT-1 and AT-2 have PASS.")

    def test_one_fail_fails(self):
        result = judge(ACCEPTANCE, comment("one-fail.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/not-pass"])
        self.assertIn("AT-2 has FAIL", result.report())

    def test_one_blocked_fails(self):
        result = judge(ACCEPTANCE, comment("one-blocked.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/not-pass"])
        self.assertIn("AT-1 has BLOCKED", result.report())

    def test_a_missing_test_fails(self):
        result = judge(ACCEPTANCE, comment("missing.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/missing"])
        self.assertIn("AT-2 has no line", result.report())

    def test_an_unknown_test_fails(self):
        result = judge(ACCEPTANCE, comment("unknown.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/unknown"])
        self.assertIn("AT-7", result.report())

    def test_a_comment_with_no_heading_fails(self):
        result = judge(ACCEPTANCE, comment("no-heading.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/no-comment"])

    def test_no_comment_fails(self):
        result = judge(ACCEPTANCE, None)
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/no-comment"])

    def test_a_retired_test_needs_no_line(self):
        # AT-3 of the fixture is retired, and all-pass.md gives it no line.
        self.assertTrue(judge(ACCEPTANCE, comment("all-pass.md")).passed)

    def test_two_lines_for_one_test_fail(self):
        text = "Test verdicts\nAT-1: PASS\nAT-2: PASS\nAT-2: FAIL\n"
        self.assertEqual(rule_ids(judge(ACCEPTANCE, text)), ["verdict/duplicate"])


class TheLatestComment(unittest.TestCase):
    def test_the_latest_owner_comment_with_the_heading_counts(self):
        comments = json.loads((FIXTURES / "comments.json").read_text())
        # Comment 2 has the agent marker, comment 3 is not by the owner, and comment 5 has no heading.
        picked = latest_verdict_comment(comments, "bkwon94")
        self.assertEqual(picked["id"], 4)

    def test_no_owner_comment_gives_none(self):
        comments = json.loads((FIXTURES / "comments.json").read_text())
        self.assertIsNone(latest_verdict_comment(comments, "nobody"))


class TheCommand(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HERE / "verdict.py"), *args], capture_output=True, text=True, check=False
        )

    def test_a_pass_exits_0(self):
        result = self.run_cli(str(FIXTURES / "ACCEPTANCE.md"), "--comment", str(FIXTURES / "all-pass.md"))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_fail_exits_1_and_prints_the_report(self):
        result = self.run_cli(str(FIXTURES / "ACCEPTANCE.md"), "--comment", str(FIXTURES / "one-fail.md"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("verdict/not-pass", result.stdout)

    def test_the_comments_mode_picks_the_latest_and_passes(self):
        result = self.run_cli(
            str(FIXTURES / "ACCEPTANCE.md"), "--comments", str(FIXTURES / "comments.json"), "--owner", "bkwon94"
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
