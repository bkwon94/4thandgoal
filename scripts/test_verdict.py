"""
Tests the Test verdict rule of scripts/verdict.py with real acceptance, evidence, verdicts, and comment files.
Each case reads its files from scripts/fixtures/verdict/. See ADR 0026.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verdict import blob_sha, check_verdicts, latest_verdict_comment

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "verdict"
ACCEPTANCE = (FIXTURES / "ACCEPTANCE.md").read_text()
# The files of a spec that the Judge read: ACCEPTANCE.md, EVIDENCE.md, and the VERDICTS.md it wrote.
JUDGE = FIXTURES / "judge"


def comment(name: str) -> str:
    return (FIXTURES / name).read_text()


def rule_ids(result) -> list[str]:
    return [offense.rule_id for offense in result.offenses]


class TheVerdictRule(unittest.TestCase):
    """The lines under `Test verdicts` in VERDICTS.md. The fixtures hold the same lines that the Judge writes."""

    def test_all_pass_passes(self):
        result = check_verdicts(ACCEPTANCE, comment("all-pass.md"))
        self.assertTrue(result.passed, result.report())
        self.assertEqual(result.report(), "0 offenses. AT-1 and AT-2 have PASS.")

    def test_one_fail_fails(self):
        result = check_verdicts(ACCEPTANCE, comment("one-fail.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/not-pass"])
        self.assertIn("AT-2 has FAIL", result.report())

    def test_one_blocked_fails(self):
        result = check_verdicts(ACCEPTANCE, comment("one-blocked.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/not-pass"])
        self.assertIn("AT-1 has BLOCKED", result.report())

    def test_a_missing_test_fails(self):
        result = check_verdicts(ACCEPTANCE, comment("missing.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/missing"])
        self.assertIn("AT-2 has no line", result.report())

    def test_an_unknown_test_fails(self):
        result = check_verdicts(ACCEPTANCE, comment("unknown.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/unknown"])
        self.assertIn("AT-7", result.report())

    def test_verdicts_with_no_heading_fail(self):
        result = check_verdicts(ACCEPTANCE, comment("no-heading.md"))
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/no-verdicts"])

    def test_no_verdicts_file_fails(self):
        result = check_verdicts(ACCEPTANCE, None)
        self.assertFalse(result.passed)
        self.assertEqual(rule_ids(result), ["verdict/no-verdicts"])

    def test_a_retired_test_needs_no_line(self):
        # AT-3 of the fixture is retired, and all-pass.md gives it no line.
        self.assertTrue(check_verdicts(ACCEPTANCE, comment("all-pass.md")).passed)

    def test_two_lines_for_one_test_fail(self):
        text = "Test verdicts\nAT-1: PASS\nAT-2: PASS\nAT-2: FAIL\n"
        self.assertEqual(rule_ids(check_verdicts(ACCEPTANCE, text)), ["verdict/duplicate"])


class TheLatestComment(unittest.TestCase):
    def test_the_latest_owner_comment_with_the_heading_counts(self):
        comments = json.loads((FIXTURES / "comments.json").read_text())
        # Comment 2 has the agent marker, comment 3 is not by the owner, and comment 5 has no heading.
        picked = latest_verdict_comment(comments, "bkwon94")
        self.assertEqual(picked["id"], 4)

    def test_no_owner_comment_gives_none(self):
        comments = json.loads((FIXTURES / "comments.json").read_text())
        self.assertIsNone(latest_verdict_comment(comments, "nobody"))


class TheJudgeRecord(unittest.TestCase):
    """The check reads VERDICTS.md of the Judge, the blob SHAs it names, and a FAIL of Brian (ADR 0026)."""

    def run_check(self, folder: Path = JUDGE, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HERE / "verdict.py"), str(folder / "ACCEPTANCE.md"),
             "--verdicts", str(folder / "VERDICTS.md"), "--evidence", str(folder / "EVIDENCE.md"), *args],
            capture_output=True, text=True, check=False,
        )

    def test_at_10_a_full_pass_of_the_judge_exits_0(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.strip(), "0 offenses. AT-1, AT-2, and AT-3 have PASS.")

    def copy(self) -> Path:
        """A copy of the files of the Judge, so a test can change one line of one file."""
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder)
        shutil.copytree(JUDGE, folder, dirs_exist_ok=True)
        return folder

    def change_a_line(self, path: Path, old: str, new: str) -> None:
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new))

    def test_at_11_a_changed_evidence_file_is_stale(self):
        folder = self.copy()
        self.change_a_line(folder / "EVIDENCE.md", "reads \"Bye 10\" on one line", "reads \"Bye 10\" on two lines")
        result = self.run_check(folder)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("verdict/stale-evidence", result.stdout)
        self.assertIn("EVIDENCE.md", result.stdout)
        self.assertNotIn("verdict/stale-acceptance", result.stdout)

    def test_at_11_a_changed_acceptance_file_is_stale(self):
        folder = self.copy()
        self.change_a_line(folder / "ACCEPTANCE.md", "at 1280 px.", "at 768 and 1280 px.")
        result = self.run_check(folder)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("verdict/stale-acceptance", result.stdout)
        self.assertNotIn("verdict/stale-evidence", result.stdout)

    def test_a_fail_of_the_judge_exits_1(self):
        folder = self.copy()
        self.change_a_line(folder / "VERDICTS.md", "AT-3: PASS", "AT-3: FAIL the image shows 11 rows, not 12")
        result = self.run_check(folder)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("verdict/not-pass", result.stdout)
        self.assertIn("AT-3 has FAIL", result.stdout)

    def test_at_12_a_fail_of_brian_overrides_a_pass_of_the_judge(self):
        # Comment 12 has PASS and the agent marker, so it does not clear the FAIL of comment 11.
        result = self.run_check(JUDGE, "--comments", str(JUDGE / "comments-fail.json"), "--owner", "bkwon94")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("verdict/brian-fail", result.stdout)
        self.assertIn("AT-2 has FAIL from Brian", result.stdout)
        self.assertIn("comment 11", result.stdout)

    def test_at_13_a_newer_comment_of_brian_with_no_fail_clears_it(self):
        result = self.run_check(JUDGE, "--comments", str(JUDGE / "comments-cleared.json"), "--owner", "bkwon94")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.strip(), "0 offenses. AT-1, AT-2, and AT-3 have PASS.")

    def test_a_blocked_line_of_brian_fails_too(self):
        result = self.run_check(JUDGE, "--comment", str(FIXTURES / "one-blocked.md"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("AT-1 has BLOCKED from Brian", result.stdout)

    def test_a_pass_of_brian_does_not_cover_a_fail_of_the_judge(self):
        folder = self.copy()
        self.change_a_line(folder / "VERDICTS.md", "AT-1: PASS", "AT-1: FAIL the page-json run printed no bye_week")
        result = self.run_check(folder, "--comment", str(FIXTURES / "all-pass.md"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("AT-1 has FAIL", result.stdout)

    def test_the_blob_sha_is_the_sha_of_git(self):
        data = (JUDGE / "EVIDENCE.md").read_bytes()
        git = subprocess.run(["git", "hash-object", "--stdin"], input=data, capture_output=True, check=True)
        self.assertEqual(blob_sha(data), git.stdout.decode().strip())

    def test_the_sha_of_the_api_counts_over_the_file(self):
        # verdict.yml gives the blob SHAs that the contents API returns. They name the file at the PR head.
        result = self.run_check(JUDGE, "--evidence-sha", "0" * 40)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("verdict/stale-evidence", result.stdout)


if __name__ == "__main__":
    unittest.main()
