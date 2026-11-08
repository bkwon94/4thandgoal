"""
Tests the selection of scripts/changed_apps.py: which apps and which packages a set of changed files checks.
Each case writes a real workspace of pyproject.toml and package.json files into a temp folder.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from changed_apps import ROOT_FILES, select_apps, select_packages

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
    """The layout of decision 07: three apps, two packages in both languages, and a package with Python only."""
    write(root, "pyproject.toml",
          '[tool.uv.workspace]\nmembers = ["apps/pipeline", "apps/api", "packages/*/python"]\n')
    write(root, "pnpm-workspace.yaml", 'packages:\n  - "apps/site"\n  - "packages/*/site"\n')
    python_member(root, "packages/league/python", "cpc-league", [])
    site_member(root, "packages/league/site", "@cpc/league", [])
    python_member(root, "packages/facts/python", "cpc-facts", ["cpc-league"])
    python_member(root, "packages/waiver/python", "cpc-waiver", ["cpc-facts", "cpc-league"])
    site_member(root, "packages/waiver/site", "@cpc/waiver", ["@cpc/league"])
    python_member(root, "apps/pipeline", "cornerstone", ["cpc-facts", "cpc-waiver"])
    python_member(root, "apps/api", "cpc-api", ["cornerstone"])
    site_member(root, "apps/site", "cpcfantasyfootball-site", ["@cpc/league", "@cpc/waiver"])


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

    def test_a_change_in_the_python_of_a_core_package_selects_its_dependents_of_both_languages(self):
        self.assertEqual(self.select("packages/waiver/python/src/waiver/board.py"), ["site", "pipeline", "api"])

    def test_a_change_in_a_python_only_package_selects_its_python_dependents(self):
        self.assertEqual(self.select("packages/facts/README.md"), ["pipeline", "api"])

    def test_each_root_file_selects_every_app(self):
        for path in ROOT_FILES + [".github/workflows/check.yml"]:
            with self.subTest(path=path):
                self.assertEqual(self.select(path), ["site", "pipeline", "api"])

    def test_a_file_outside_apps_and_packages_selects_every_app(self):
        self.assertEqual(self.select("GLOSSARY.md"), ["site", "pipeline", "api"])


class ThePackageSelection(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        workspace(self.root)

    def select(self, *files: str) -> list[str]:
        return select_packages(self.root, list(files))

    def test_a_change_in_one_language_of_a_package_selects_it_and_each_package_that_needs_it(self):
        self.assertEqual(self.select("packages/league/site/headshot.tsx"), ["facts", "league", "waiver"])

    def test_a_change_in_a_package_selects_it_and_each_package_above_it(self):
        self.assertEqual(self.select("packages/facts/README.md"), ["facts", "waiver"])

    def test_a_change_in_one_language_of_a_core_package_selects_it_alone(self):
        self.assertEqual(self.select("packages/waiver/python/src/waiver/board.py"), ["waiver"])
        self.assertEqual(self.select("packages/waiver/site/war-chest.tsx"), ["waiver"])

    def test_a_change_in_an_app_selects_no_package(self):
        self.assertEqual(self.select("apps/pipeline/src/cornerstone/odds.py"), [])

    def test_a_root_file_selects_every_package(self):
        self.assertEqual(self.select("Makefile"), ["facts", "league", "waiver"])


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

    def test_a_change_in_the_league_package_of_the_repo_selects_each_app_and_each_package_on_it(self):
        # The facts, the analyzer, the eggs, the managers, the midseason, the rankings, the sim, the waiver, and the
        # week packages list the league package, so a change in league checks each.
        files = ["packages/league/python/src/league/models.py"]
        self.assertEqual(select_apps(REPO, files), ["site", "pipeline", "api"])
        self.assertEqual(select_packages(REPO, files),
                         ["analyzer", "eggs", "facts", "league", "managers", "midseason", "rankings", "sim", "waiver",
                          "week"])

    def test_a_change_in_the_facts_package_of_the_repo_selects_the_apps_that_import_it_and_not_league(self):
        # The analyzer, the managers, the midseason, the rankings, the sim, the waiver, and the week packages list the
        # facts package, so a change in facts checks each too.
        files = ["packages/facts/python/src/facts/writer.py"]
        self.assertEqual(select_apps(REPO, files), ["pipeline", "api"])
        self.assertEqual(select_packages(REPO, files),
                         ["analyzer", "facts", "managers", "midseason", "rankings", "sim", "waiver", "week"])

    def test_a_change_in_the_analyzer_package_of_the_repo_selects_the_apps_that_import_it(self):
        # The analyzer has both languages, so a change on either side selects the site and the two Python apps.
        files = ["packages/analyzer/python/src/analyzer/rubric.py"]
        self.assertEqual(select_apps(REPO, files), ["site", "pipeline", "api"])
        self.assertEqual(select_packages(REPO, files), ["analyzer"])

    def test_a_change_in_the_python_of_the_waiver_package_of_the_repo_selects_both_languages_and_each_dependent(self):
        # AT-32: the package check runs both languages of waiver, and the site, the pipeline, and the API need it.
        files = ["packages/waiver/python/src/waiver/board.py"]
        self.assertEqual(select_apps(REPO, files), ["site", "pipeline", "api"])
        self.assertEqual(select_packages(REPO, files), ["waiver"])

    def test_a_change_in_either_side_of_the_week_package_selects_each_app_and_only_the_week(self):
        # A path in a package selects both of its languages, so the site, the pipeline, and the API each run.
        for path in ("packages/week/python/src/week/sheet/assemble.py", "packages/week/site/chapters/standings.tsx"):
            with self.subTest(path=path):
                self.assertEqual(select_apps(REPO, [path]), ["site", "pipeline", "api"])
                self.assertEqual(select_packages(REPO, [path]), ["week"])

    def test_a_change_in_either_side_of_the_managers_package_selects_each_app_and_only_the_managers(self):
        # The pipeline lists the managers package, and a change in the pipeline selects the API too.
        for path in ("packages/managers/python/src/managers/season.py", "packages/managers/site/page/points-line.tsx"):
            with self.subTest(path=path):
                self.assertEqual(select_apps(REPO, [path]), ["site", "pipeline", "api"])
                self.assertEqual(select_packages(REPO, [path]), ["managers"])

    def test_a_change_in_either_side_of_the_rankings_package_selects_each_app_and_only_the_rankings(self):
        # No other package lists the rankings. The pipeline lists it, and a change in the pipeline selects the API too.
        for path in ("packages/rankings/python/src/rankings/odds.py", "packages/rankings/site/chapters/top-three.tsx"):
            with self.subTest(path=path):
                self.assertEqual(select_apps(REPO, [path]), ["site", "pipeline", "api"])
                self.assertEqual(select_packages(REPO, [path]), ["rankings"])

    def test_the_command_prints_the_apps_on_one_line(self):
        # HEAD against HEAD has no committed change, so only the files of the work tree count.
        out = subprocess.run(["python3", "-B", str(HERE / "changed_apps.py"), "HEAD"], cwd=REPO,
                             check=True, capture_output=True, text=True).stdout
        self.assertEqual(len(out.splitlines()), 1 if out else 0)


if __name__ == "__main__":
    unittest.main()
