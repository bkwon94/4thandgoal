"""
Tests the retry rule of scripts/retry_rule.py with real config files in a scratch folder, and with the configs of the repo.
A flaky test gets a fix or a delete, never a retry setting.
"""
import tempfile
import unittest
from pathlib import Path

from retry_rule import check_retries

ROOT = Path(__file__).resolve().parent.parent


class TheRetryRule(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_a_playwright_retries_value_above_zero_fails_and_names_the_file(self):
        self.write("apps/site/playwright.config.ts", "export default { retries: 1 };\n")
        offenses = check_retries(self.root)
        self.assertEqual(len(offenses), 1)
        self.assertIn("apps/site/playwright.config.ts", offenses[0])

    def test_a_computed_retries_value_fails(self):
        self.write("playwright.config.ts", "export default { retries: process.env.CI ? 2 : 0 };\n")
        self.assertEqual(len(check_retries(self.root)), 1)

    def test_a_playwright_retries_value_of_zero_passes(self):
        self.write("apps/site/playwright.config.ts", "export default { retries: 0 };\n")
        self.assertEqual(check_retries(self.root), [])

    def test_pytest_rerunfailures_in_a_lock_file_fails(self):
        self.write("uv.lock", '[[package]]\nname = "pytest-rerunfailures"\nversion = "14.0"\n')
        offenses = check_retries(self.root)
        self.assertEqual(len(offenses), 1)
        self.assertIn("uv.lock", offenses[0])

    def test_pytest_rerunfailures_in_a_config_fails(self):
        self.write("apps/pipeline/pyproject.toml", 'dev = ["pytest-rerunfailures>=14"]\n')
        self.assertEqual(len(check_retries(self.root)), 1)

    def test_a_vitest_retry_fails(self):
        self.write("apps/site/vitest.config.mts", "export default { test: { retry: 2 } };\n")
        offenses = check_retries(self.root)
        self.assertEqual(len(offenses), 1)
        self.assertIn("vitest.config.mts", offenses[0])

    def test_a_vitest_retry_of_zero_passes(self):
        self.write("apps/site/vitest.config.mts", "export default { test: { retry: 0 } };\n")
        self.assertEqual(check_retries(self.root), [])

    def test_a_folder_of_dependencies_is_skipped(self):
        self.write("node_modules/x/playwright.config.ts", "export default { retries: 3 };\n")
        self.assertEqual(check_retries(self.root), [])

    def test_the_configs_of_the_repo_pass(self):
        self.assertEqual(check_retries(ROOT), [])


if __name__ == "__main__":
    unittest.main()
