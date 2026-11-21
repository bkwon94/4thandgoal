"""
Tests the selection of scripts/changed_apps.py: which apps and which packages a set of changed files checks.
Each case writes a real workspace of pyproject.toml and package.json files into a temp folder.
"""
import json
import os
import re
import shlex
import shutil
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
    site_member(root, "apps/site", "4thandgoal-site", ["@cpc/league", "@cpc/waiver"])


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


class TheRootFolderSelection(unittest.TestCase):
    """A change only under .scratch/ or docs/ selects the members whose tests read the changed path, and no more."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        workspace(self.root)

    def test_a_tracker_note_selects_the_site_and_the_pipeline_that_read_the_tracker(self):
        files = [".scratch/quick-wins/faster-checks.md"]
        self.assertEqual(select_apps(self.root, files), ["site", "pipeline"])
        self.assertEqual(select_packages(self.root, files), [])

    def test_the_state_file_selects_the_site_and_the_pipeline_that_read_it(self):
        self.assertEqual(select_apps(self.root, ["docs/agents/state.md"]), ["site", "pipeline"])

    def test_an_adr_selects_no_member_because_no_test_reads_it(self):
        self.assertEqual(select_apps(self.root, ["docs/adr/0033-quick-runs.md"]), [])
        self.assertEqual(select_packages(self.root, ["docs/adr/0033-quick-runs.md"]), [])

    def test_a_rules_file_under_a_root_folder_selects_the_members_of_the_rules_file_rule(self):
        for path in ("docs/agents/AGENTS.md", ".scratch/CLAUDE.md"):
            with self.subTest(path=path):
                self.assertEqual(select_apps(self.root, [path]), ["site", "pipeline"])

    def test_a_root_folder_file_with_another_root_file_selects_every_app_and_package(self):
        files = [".scratch/quick-wins/faster-checks.md", "Makefile"]
        self.assertEqual(select_apps(self.root, files), ["site", "pipeline", "api"])
        self.assertEqual(select_packages(self.root, files), ["facts", "league", "waiver"])

    def test_a_root_folder_file_with_an_app_file_selects_the_readers_and_the_app(self):
        self.assertEqual(select_apps(self.root, ["docs/adr/0033-quick-runs.md", "apps/api/src/app.py"]), ["api"])
        self.assertEqual(select_apps(self.root, [".scratch/a.md", "apps/api/src/app.py"]), ["site", "pipeline", "api"])

    def test_the_repo_tracker_selects_the_site_and_the_pipeline_only(self):
        self.assertEqual(select_apps(REPO, [".scratch/quick-wins/faster-checks.md"]), ["site", "pipeline"])
        self.assertEqual(select_packages(REPO, [".scratch/quick-wins/faster-checks.md"]), [])


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
        files = ["packages/analyzer/python/src/analyzer/advisor.py"]
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
        for path in ("packages/rankings/python/src/rankings/chapter.py", "packages/rankings/site/chapters/top-three.tsx"):
            with self.subTest(path=path):
                self.assertEqual(select_apps(REPO, [path]), ["site", "pipeline", "api"])
                self.assertEqual(select_packages(REPO, [path]), ["rankings"])

    def test_the_command_prints_the_apps_on_one_line(self):
        # HEAD against HEAD has no committed change, so only the files of the work tree count.
        out = subprocess.run(["python3", "-B", str(HERE / "changed_apps.py"), "HEAD"], cwd=REPO,
                             check=True, capture_output=True, text=True).stdout
        self.assertEqual(len(out.splitlines()), 1 if out else 0)


class TheStagedCheck(unittest.TestCase):
    def test_only_staged_paths_choose_the_member_checks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            # Git exports its index location to hooks. Use the index of this test repository instead.
            git_vars = subprocess.check_output(["git", "rev-parse", "--local-env-vars"], text=True).splitlines()
            env = {key: value for key, value in os.environ.items() if key not in git_vars}

            def git(*args: str) -> None:
                subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True)

            workspace(root)
            (root / "scripts").mkdir()
            shutil.copyfile(REPO / "Makefile", root / "Makefile")
            shutil.copyfile(HERE / "changed_apps.py", root / "scripts/changed_apps.py")
            write(root, "README.md", "Committed root file\n")
            git("init", "--quiet", "--template=")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.com", "-c", "commit.gpgSign=false",
                "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Create the test workspace")
            write(root, "apps/pipeline/odds.py", "# Staged pipeline change\n")
            git("add", "apps/pipeline/odds.py")
            write(root, "README.md", "Unstaged root change\n")
            write(root, "apps/site/untracked.ts", "// Untracked site file\n")

            # Dry-run the Make command from the hook so this test does not run every member suite.
            config = (REPO / ".pre-commit-config.yaml").read_text()
            entry = next(line.split(":", 1)[1] for line in config.splitlines() if line.lstrip().startswith("entry:"))
            output = subprocess.check_output([*shlex.split(entry), "-n"], cwd=root, env=env, text=True)

            self.assertEqual(re.findall(r'echo "==> (.+?): check-fast"', output), ["scripts", "pipeline", "api"])


class TheSiteTestSelection(unittest.TestCase):
    def site_command(self, *options: str) -> str:
        """The planned command of the site fast check, read from a dry run of the Make command in a real repo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            git_vars = subprocess.check_output(["git", "rev-parse", "--local-env-vars"], text=True).splitlines()
            # A hook run of Make passes STAGED=1 to its children, in MAKEFLAGS and in the environment. This dry run sets
            # its own options.
            skipped = [*git_vars, "MAKEFLAGS", "MFLAGS", "MAKELEVEL", "STAGED", "BASE"]
            env = {key: value for key, value in os.environ.items() if key not in skipped}

            def git(*args: str) -> None:
                subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
                                "-c", "commit.gpgSign=false", "-c", "core.hooksPath=/dev/null", *args],
                               cwd=root, env=env, check=True, capture_output=True)

            workspace(root)
            (root / "scripts").mkdir()
            shutil.copyfile(REPO / "Makefile", root / "Makefile")
            shutil.copyfile(HERE / "changed_apps.py", root / "scripts/changed_apps.py")
            git("init", "--quiet", "--template=")
            git("add", ".")
            git("commit", "--quiet", "-m", "Create the test workspace")
            write(root, "apps/site/page.ts", "// Changed site file\n")
            git("add", "apps/site/page.ts")
            if "BASE=HEAD" in options:
                git("commit", "--quiet", "-m", "Change the site")
                options = ("BASE=HEAD~1",)
            output = subprocess.check_output(["make", "-n", "check-fast", *options], cwd=root, env=env, text=True)
            return next(line for line in output.splitlines() if "check:fast" in line)

    def test_a_staged_run_tests_every_site_file(self):
        self.assertNotIn("--changed", self.site_command("STAGED=1"))

    def test_a_base_run_tests_every_site_file(self):
        self.assertNotIn("--changed", self.site_command("BASE=HEAD"))

    def test_a_run_with_no_selection_tests_every_site_file(self):
        self.assertNotIn("--changed", self.site_command())

    def test_a_hook_run_in_a_work_tree_with_git_dir_set_finds_the_top_of_the_work_tree(self):
        """Run the real prefix of the site command with GIT_DIR set as a git hook sets it, with git as the probe.

        A site test, such as the tracker rule test, runs git from apps/site. A hook sets GIT_DIR and no GIT_WORK_TREE,
        so git takes apps/site as the top of the work tree and sees every file as changed.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skipped = subprocess.check_output(["git", "rev-parse", "--local-env-vars"], text=True).splitlines()
            env = {key: value for key, value in os.environ.items() if key not in skipped}

            def git(*args: str) -> str:
                return subprocess.check_output(["git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
                                                "-c", "commit.gpgSign=false", "-c", "core.hooksPath=/dev/null", *args],
                                               cwd=root, env=env, text=True)

            workspace(root)
            (root / "scripts").mkdir()
            shutil.copyfile(REPO / "Makefile", root / "Makefile")
            shutil.copyfile(HERE / "changed_apps.py", root / "scripts/changed_apps.py")
            git("init", "--quiet", "--template=")
            git("add", ".")
            git("commit", "--quiet", "-m", "Create the test workspace")
            write(root, "apps/site/page.ts", "// Changed site file\n")
            git("add", "apps/site/page.ts")
            make_env = {key: value for key, value in env.items() if key not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
            plan = subprocess.check_output(["make", "-n", "check-fast", "STAGED=1"], cwd=root, env=make_env, text=True)
            line = next(line for line in plan.splitlines() if "check:fast" in line)
            command = line[line.index("LINT_FILES="):]
            probe = command.replace("pnpm --dir apps/site check:fast", "git diff --name-only HEAD")
            self.assertNotEqual(command, probe)
            hook_env = {**env, "GIT_DIR": str(root / ".git"), "GIT_INDEX_FILE": str(root / ".git/index")}
            output = subprocess.check_output(["sh", "-c", probe], cwd=root / "apps/site", env=hook_env, text=True)
            self.assertEqual(output.split(), ["apps/site/page.ts"])


if __name__ == "__main__":
    unittest.main()
