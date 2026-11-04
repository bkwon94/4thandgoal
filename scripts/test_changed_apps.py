"""
Tests the selection of scripts/changed_apps.py: which apps a set of changed files checks.
Each case writes a real workspace of pyproject.toml and package.json files into a temp folder.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from changed_apps import ROOT_FILES, select_apps

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def python_member(root: Path, folder: str, name: str, needs: list[str]) -> None:
    sources = "".join(f"{need} = {{ workspace = true }}\n" for need in needs)
    write(root, f"{folder}/pyproject.toml",
          f'[project]\nname = "{name}"\ndependencies = {json.dumps(needs)}\n\n[tool.uv.sources]\n{sources}')


def site_member(root: Path, folder: str, name: str, needs: list[str]) -> None:
    write(root, f"{folder}/package.json",
          json.dumps({"name": name, "dependencies": {need: "workspace:*" for need in needs}}))


def workspace(root: Path) -> None:
    """The layout of decision 07: three apps, a package in both languages, and a package with Python only."""
    write(root, "pyproject.toml",
          '[tool.uv.workspace]\nmembers = ["apps/pipeline", "apps/api", "packages/*/python"]\n')
    write(root, "pnpm-workspace.yaml", 'packages:\n  - "apps/site"\n  - "packages/*/site"\n')
    python_member(root, "packages/league/python", "cpc-league", [])
    site_member(root, "packages/league/site", "@cpc/league", [])
    python_member(root, "packages/facts/python", "cpc-facts", ["cpc-league"])
    python_member(root, "apps/pipeline", "cornerstone", ["cpc-facts"])
    python_member(root, "apps/api", "cpc-api", ["cornerstone"])
    site_member(root, "apps/site", "cpcfantasyfootball-site", ["@cpc/league"])


class TheAppSelection(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        workspace(self.root)

    def select(self, *files: str) -> list[str]:
        return select_apps(self.root, list(files))

    def test_no_change_selects_no_app(self):
        self.assertEqual(self.select(), [])

    def test_a_change_in_the_site_selects_the_site(self):
        self.assertEqual(self.select("apps/site/src/app/page.tsx"), ["site"])

    def test_a_change_in_the_pipeline_selects_the_pipeline_and_the_api_that_needs_it(self):
        self.assertEqual(self.select("apps/pipeline/src/cornerstone/odds.py"), ["pipeline", "api"])

    def test_a_change_in_the_api_selects_the_api_only(self):
        self.assertEqual(self.select("apps/api/src/cornerstone_api/app.py"), ["api"])

    def test_a_change_in_one_language_of_a_package_selects_the_dependents_of_both_languages(self):
        self.assertEqual(self.select("packages/league/python/league/models.py"), ["site", "pipeline", "api"])

    def test_a_change_in_a_python_only_package_selects_its_python_dependents(self):
        self.assertEqual(self.select("packages/facts/README.md"), ["pipeline", "api"])

    def test_each_root_file_selects_every_app(self):
        for path in ROOT_FILES + [".github/workflows/check.yml"]:
            with self.subTest(path=path):
                self.assertEqual(self.select(path), ["site", "pipeline", "api"])

    def test_a_file_outside_apps_and_packages_selects_every_app(self):
        self.assertEqual(self.select("GLOSSARY.md"), ["site", "pipeline", "api"])


class TheRepoWorkspace(unittest.TestCase):
    """The real workspace files of the repo, read by the same code."""

    def test_the_root_files_name_the_workspace_and_the_lock_files(self):
        self.assertEqual(sorted(ROOT_FILES),
                         ["Makefile", "pnpm-lock.yaml", "pnpm-workspace.yaml", "pyproject.toml", "uv.lock"])
        for path in ROOT_FILES:
            with self.subTest(path=path):
                self.assertTrue((REPO / path).is_file(), f"{path} is missing at the repo root")

    def test_a_change_in_the_pipeline_of_the_repo_selects_the_api_too(self):
        self.assertEqual(select_apps(REPO, ["apps/pipeline/src/cornerstone/odds.py"]), ["pipeline", "api"])

    def test_the_command_prints_the_apps_on_one_line(self):
        # HEAD against HEAD has no committed change, so only the files of the work tree count.
        out = subprocess.run(["python3", "-B", str(HERE / "changed_apps.py"), "HEAD"], cwd=REPO,
                             check=True, capture_output=True, text=True).stdout
        self.assertEqual(len(out.splitlines()), 1 if out else 0)


if __name__ == "__main__":
    unittest.main()
