"""
Tests scripts/rebuild.py: the pick of the latest week, the mode of the run, and the diff of two rendered files.
Each case reads the real saved weeks of this repo, or a real folder that it writes in a temp folder.
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import rebuild  # noqa: E402

CPC_WEEK = ROOT / "clients" / "cpc" / "build" / "2026" / "week-10"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class TheLatestWeek(unittest.TestCase):
    def test_each_client_gets_its_latest_published_week_with_saved_facts(self):
        weeks = rebuild.latest_weeks(ROOT)
        slugs = [week.slug for week in weeks]
        self.assertEqual(slugs, sorted(slugs))
        self.assertIn("cpc", slugs)
        self.assertIn("norcal", slugs)
        for week in weeks:
            folder = ROOT / "clients" / week.slug / "published" / str(week.season) / f"week-{week.week:02d}"
            self.assertTrue(folder.is_dir(), folder)
            self.assertTrue((rebuild.data_week(ROOT, week) / "facts.json").is_file())

    def test_a_published_week_with_no_saved_facts_is_skipped(self):
        root = Path(tempfile.mkdtemp())
        client = root / "clients" / "x"
        (client / "published" / "2026" / "week-03").mkdir(parents=True)
        (client / "published" / "2026" / "week-04").mkdir(parents=True)
        for week in ("week-03",):
            data = client / "data" / "2026" / week
            data.mkdir(parents=True)
            (data / "facts.json").write_text("{}")
            (data / "blurbs.json").write_text("{}")
        (client / "client.toml").write_text("")
        self.assertEqual(rebuild.latest_weeks(root), [rebuild.Week("x", 2026, 3)])


class TheMode(unittest.TestCase):
    def tree(self, cli_text: str) -> Path:
        root = Path(tempfile.mkdtemp())
        cli = root / rebuild.PIPELINE_CLI
        cli.parent.mkdir(parents=True)
        cli.write_text(cli_text)
        return root

    def test_a_base_with_no_facts_command_gets_the_render_diff_only(self):
        base = self.tree('sub.add_parser("page-json", parents=[named])\n')
        self.assertFalse(rebuild.base_rebuilds_facts(base))

    def test_a_base_with_the_facts_command_can_rebuild_the_facts(self):
        base = self.tree('sub.add_parser("facts", parents=[named],\n')
        self.assertTrue(rebuild.base_rebuilds_facts(base))


class TheDiff(unittest.TestCase):
    def test_a_rendered_file_against_itself_has_no_diff(self):
        page = read(CPC_WEEK / "page.json")
        self.assertEqual(rebuild.json_diff(page, copy.deepcopy(page)), [])

    def test_one_changed_waiver_score_names_its_json_path(self):
        board = read(CPC_WEEK / "waiver.json")
        bucket = next(name for name, rows in board["buckets"].items() if rows)
        changed = copy.deepcopy(board)
        changed["buckets"][bucket][0]["board_score"] = changed["buckets"][bucket][0]["board_score"] + 1
        self.assertEqual(rebuild.json_diff(board, changed), [f"$.buckets.{bucket}[0].board_score"])

    def test_an_added_key_and_a_shorter_list_each_name_a_path(self):
        self.assertEqual(rebuild.json_diff({"a": [1, 2]}, {"a": [1], "b": 0}), ["$.a[1]", "$.b"])

    def test_a_file_that_one_side_lacks_is_one_diff_at_the_root(self):
        folder = Path(tempfile.mkdtemp())
        shutil.copy(CPC_WEEK / "topics.json", folder / "topics.json")
        self.assertEqual(rebuild.file_diff(folder / "topics.json", folder / "absent.json"), ["$"])


class TheWorkflow(unittest.TestCase):
    workflow = (ROOT / ".github" / "workflows" / "rebuild.yml").read_text(encoding="utf-8")

    def test_the_workflow_runs_the_scripts_of_the_default_branch(self):
        self.assertIn("ref: ${{ github.event.repository.default_branch }}\n          path: base", self.workflow)
        self.assertIn("python3 -B base/scripts/rebuild.py --base base --head head", self.workflow)
        self.assertIn("../base/scripts/scope.py", self.workflow)

    def test_the_workflow_names_no_secret_of_claude_or_typesafe(self):
        for secret in rebuild.SECRETS:
            self.assertNotIn(secret, self.workflow)


if __name__ == "__main__":
    unittest.main()
