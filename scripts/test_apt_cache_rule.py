"""
Tests the apt cache rule of scripts/apt_cache_rule.py with real workflow files in a scratch folder, and with the workflows of the repo.
A step that installs the system packages of Playwright must restore the apt cache first, so a slow mirror cannot stall it.
"""
import tempfile
import unittest
from pathlib import Path

from apt_cache_rule import check_apt_cache

ROOT = Path(__file__).resolve().parent.parent

RESTORE = """      - name: Restore the apt packages
        uses: actions/cache@v6
        with:
          path: ~/.cache/apt-archives
          key: apt
"""

INSTALL_DEPS = """      - name: Install the system packages
        run: pnpm exec playwright install-deps chromium
"""

WITH_DEPS = """      - name: Install the browsers
        run: |
          set -e
          pnpm exec playwright install --with-deps chromium webkit
"""


def workflow(*jobs: tuple[str, str]) -> str:
    text = "name: Check\non:\n  push:\njobs:\n"
    for name, steps in jobs:
        text += f"  {name}:\n    runs-on: ubuntu-latest\n    steps:\n{steps}"
    return text


class TheAptCacheRule(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def write(self, name: str, text: str) -> Path:
        path = self.root / ".github" / "workflows" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_install_deps_with_no_restore_fails_and_names_the_file_and_the_line(self):
        self.write("check.yml", workflow(("site", INSTALL_DEPS)))
        offenses = check_apt_cache(self.root)
        self.assertEqual(len(offenses), 1)
        self.assertIn(".github/workflows/check.yml:9 job site", offenses[0])
        self.assertIn("install-deps", offenses[0])

    def test_with_deps_in_a_block_with_no_restore_fails(self):
        self.write("rerun.yaml", workflow(("rerun", WITH_DEPS)))
        offenses = check_apt_cache(self.root)
        self.assertEqual(len(offenses), 1)
        self.assertIn(".github/workflows/rerun.yaml:11", offenses[0])

    def test_an_earlier_restore_in_the_same_job_passes(self):
        self.write("check.yml", workflow(("site", RESTORE + INSTALL_DEPS + WITH_DEPS)))
        self.assertEqual(check_apt_cache(self.root), [])

    def test_a_restore_after_the_install_fails(self):
        self.write("check.yml", workflow(("site", INSTALL_DEPS + RESTORE)))
        self.assertEqual(len(check_apt_cache(self.root)), 1)

    def test_a_restore_in_another_job_fails(self):
        self.write("check.yml", workflow(("unit", RESTORE), ("browser", INSTALL_DEPS)))
        offenses = check_apt_cache(self.root)
        self.assertEqual(len(offenses), 1)
        self.assertIn("job browser", offenses[0])

    def test_a_cache_of_another_path_does_not_count(self):
        other = RESTORE.replace("~/.cache/apt-archives", "~/.cache/ms-playwright")
        self.write("check.yml", workflow(("site", other + INSTALL_DEPS)))
        self.assertEqual(len(check_apt_cache(self.root)), 1)

    def test_a_comment_that_names_install_deps_passes(self):
        step = "      # The cache holds the browsers, so install-deps adds the system packages.\n      - run: make check\n"
        self.write("check.yml", workflow(("site", step)))
        self.assertEqual(check_apt_cache(self.root), [])

    def test_the_workflows_of_the_repo_pass(self):
        self.assertEqual(check_apt_cache(ROOT), [])


if __name__ == "__main__":
    unittest.main()
