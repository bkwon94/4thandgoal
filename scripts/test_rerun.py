"""
Tests scripts/rerun.py: the re-run of the Red and Green commands of a quick file. Each case builds a real git repo
in a temp folder, with a red commit, a fix commit, and a commit that adds the quick file, and runs the script on it.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RERUN = HERE / "rerun.py"
# A commit hook sets GIT_INDEX_FILE and GIT_DIR. The test repo drops them, so its commands never touch the real index.
GIT_ENV = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

# The loop of the test repo. The red commit has the bug in calc.py, and the fix commit fixes it.
LOOP = "from calc import add\nassert add(2, 2) == 4, f'add(2, 2) gave {add(2, 2)}'\nprint('loop passed')\n"
BUG = "def add(a, b):\n    return a + b + 1\n"
FIX = "def add(a, b):\n    return a + b\n"
FAILURE_LINE = "AssertionError: add(2, 2) gave 5"
COMMAND = "python3 -B loop.py"


def quick_file(red: str, fix: str, failure_line: str = FAILURE_LINE, command: str = COMMAND,
               red_at: str | None = None) -> str:
    """A quick file in the shape of format.md of 4ag:quick, with one tdd item and one text-only item."""
    red_line = red_at or f"Red: at `{red}`, `{command}`"
    return f"""# Add

Kind: bug
Status: in-progress
Branch: `bug-add`.
Source: the session of 2026-11-18.
Boundary: holds.

## Items

### 1. add gives the sum

Done condition: add(2, 2) gives 4.
Method: tdd
Cause: `add` in `calc.py` adds 1.
{red_line}

```text
Traceback (most recent call last):
{failure_line}
```

Green: at `{fix}`, `{command}`

```text
loop passed
```
Test verdict: pending

### 2. The README names the loop

Done condition: the README names the loop.
Method: text only.
Red: none, text only.
Green: at `{fix}`, the diff of the text.
Test verdict: none

## Comments
"""


class TheRerun(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.git("init", "-q", "-b", "main")
        self.commit({"README.md": "start\n", "calc.py": BUG})
        self.base = self.head_sha()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.repo, env=GIT_ENV, check=True, capture_output=True,
                              text=True).stdout

    def head_sha(self) -> str:
        return self.git("rev-parse", "--short=8", "HEAD").strip()

    def commit(self, files: dict[str, str]) -> str:
        for path, text in files.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "change")
        return self.head_sha()

    def red_and_fix(self) -> tuple[str, str]:
        """A red commit that adds the loop with the bug, and a fix commit that fixes the bug."""
        red = self.commit({"loop.py": LOOP})
        fix = self.commit({"calc.py": FIX, "README.md": "start\nRun loop.py.\n"})
        return red, fix

    def rerun(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(["python3", "-B", str(RERUN), "--repo", str(self.repo), "--base", self.base,
                               "--head", "HEAD", *extra], env=GIT_ENV, capture_output=True, text=True)

    def test_a_true_red_and_fix_passes(self):
        red, fix = self.red_and_fix()
        self.commit({".scratch/bugs/add.md": quick_file(red, fix)})
        result = self.rerun()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("item 1 (add gives the sum): held", result.stdout)
        self.assertIn("item 2 (The README names the loop): text only, skipped", result.stdout)

    def test_a_red_command_that_passes_at_the_red_commit_fails_and_names_the_item(self):
        red, fix = self.red_and_fix()
        # The Red line names the fix commit, where the loop passes, so the loop never went red.
        self.commit({".scratch/bugs/add.md": quick_file(fix, fix)})
        result = self.rerun()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"FAIL item 1 (add gives the sum): the Red command passed at `{fix}`, so the loop never went red",
                      result.stdout)

    def test_a_quoted_failure_line_that_the_command_does_not_print_fails_and_names_the_line(self):
        red, fix = self.red_and_fix()
        self.commit({".scratch/quick-wins/add.md": quick_file(red, fix, "AssertionError: add(2, 2) gave 7 apples")})
        result = self.rerun()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL item 1 (add gives the sum): the Red output has no line "
                      "`AssertionError: add(2, 2) gave 7 apples`", result.stdout)

    def test_a_pr_with_no_quick_file_passes_with_a_note(self):
        self.red_and_fix()
        result = self.rerun()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no quick file", result.stdout)

    def test_a_red_at_the_parent_with_the_loop_file_of_the_fix_commit_passes(self):
        # The hook runs the loop, so the loop and the fix share one commit, and Red runs at its parent.
        parent = self.head_sha()
        fix = self.commit({"loop.py": LOOP, "calc.py": FIX})
        red_at = f"Red: at `{parent}` with `loop.py` of `{fix}`, `{COMMAND}`"
        self.commit({".scratch/bugs/add.md": quick_file(parent, fix, red_at=red_at)})
        result = self.rerun()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("item 1 (add gives the sum): held", result.stdout)

    def test_the_run_puts_back_the_branch_of_the_checkout(self):
        red, fix = self.red_and_fix()
        self.commit({".scratch/bugs/add.md": quick_file(red, fix)})
        self.rerun()
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD").strip(), "main")
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=no"), "")

    def test_the_members_come_from_the_commands(self):
        red, fix = self.red_and_fix()
        site = "cd apps/site && pnpm vitest run src/app/page.test.tsx"
        self.commit({".scratch/bugs/add.md": quick_file(red, fix, command=site)})
        result = self.rerun("--members")
        self.assertEqual(result.stdout.strip(), "members: site", result.stdout + result.stderr)

    def test_a_quoted_line_cut_with_dots_matches_the_full_line(self):
        # A quick file may cut a long line with "...", as pytest does. Each cut part must still show, in order.
        red, fix = self.red_and_fix()
        self.commit({".scratch/bugs/add.md": quick_file(red, fix, "AssertionError: add...gave 5")})
        result = self.rerun()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TheWorkflow(unittest.TestCase):
    """The workflow of the re-run job. The root scripts use only the standard library, so the test reads the text."""

    TEXT = (HERE.parent / ".github" / "workflows" / "rerun.yml").read_text()

    def test_the_script_comes_from_the_default_branch(self):
        self.assertIn("ref: ${{ github.event.repository.default_branch }}\n"
                      "          path: rerun-main\n"
                      "          sparse-checkout: scripts/rerun.py", self.TEXT)
        self.assertIn("python3 -B rerun-main/scripts/rerun.py", self.TEXT)
        self.assertNotIn("python3 -B scripts/rerun.py", self.TEXT)

    def test_the_workflow_names_no_model_key_and_no_secret(self):
        for word in ("ANTHROPIC_API_KEY", "TYPESAFE_API_KEY", "secrets."):
            self.assertNotIn(word, self.TEXT)
