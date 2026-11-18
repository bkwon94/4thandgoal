"""
Tests scripts/scope.py: which heavy checks a diff selects. Each case builds a real git repo in a temp folder,
commits files, and runs the script on the diff of one commit.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOPE = HERE / "scope.py"
# A commit hook sets GIT_INDEX_FILE and GIT_DIR. The test repo drops them, so its commands never touch the real index.
GIT_ENV = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


class TheScope(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.git("init", "-q")
        self.commit({"README.md": "start\n"})

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.repo, env=GIT_ENV, check=True, capture_output=True,
                              text=True).stdout

    def commit(self, files: dict[str, str]) -> None:
        for path, text in files.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "change")

    def scope(self) -> list[str]:
        """The output lines of the script on the last commit."""
        out = subprocess.run(["python3", "-B", str(SCOPE), "HEAD~1", "HEAD"], cwd=self.repo, env=GIT_ENV,
                             check=True, capture_output=True, text=True).stdout
        return out.splitlines()

    def test_a_diff_of_records_selects_no_heavy_check(self):
        self.commit({".scratch/f/MAP.md": "x\n", "docs/adr/0001-a.md": "x\n", "GLOSSARY.md": "x\n"})
        self.assertEqual(self.scope(), ["records only", "selects: none"])

    def test_a_diff_of_the_pipeline_selects_the_rebuild(self):
        self.commit({"apps/pipeline/src/grade.py": "x = 1\n"})
        self.assertEqual(self.scope(), ["change of code", "selects: rebuild rerun"])

    def test_a_diff_of_the_site_selects_the_smoke_run(self):
        self.commit({"apps/site/src/page.tsx": "x\n"})
        self.assertEqual(self.scope(), ["change of code", "selects: smoke rerun"])

    def test_a_diff_of_both_apps_selects_each_check(self):
        self.commit({"apps/site/src/page.tsx": "x\n", "apps/pipeline/src/grade.py": "x = 1\n"})
        self.assertEqual(self.scope(), ["change of code", "selects: smoke rebuild rerun"])

    def test_a_root_file_of_code_selects_each_check(self):
        self.commit({"Makefile": "all:\n"})
        self.assertEqual(self.scope(), ["change of code", "selects: smoke rebuild rerun"])

    def test_a_markdown_file_in_an_app_is_code(self):
        self.commit({"apps/site/README.md": "x\n"})
        self.assertEqual(self.scope()[0], "change of code")


if __name__ == "__main__":
    unittest.main()
