"""
Tests that CI runs the site unit suite in a matrix of shards, and that only a PR runs the tests the diff can reach.
Each case reads the real workflow. scripts/bun-test.mjs of the site reads BUN_TEST_SHARD and BUN_TEST_BASE.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = (REPO / ".github/workflows/check.yml").read_text()


def job_text(name: str) -> str:
    match = re.search(rf"^  {re.escape(name)}:\n(.*?)(?=^  \S|\Z)", WORKFLOW, re.M | re.S)
    assert match, f"The workflow has no job {name}"
    return match.group(1)


def env_value(job: str, name: str) -> str:
    match = re.search(rf"^      {re.escape(name)}: (.+)$", job_text(job), re.M)
    assert match, f"The job {job} sets no {name}"
    return match.group(1)


class TheUnitShards(unittest.TestCase):
    def test_the_unit_job_runs_in_a_matrix_of_one_shard(self):
        # With the 4 workers of bun test --parallel, a second shard saves 13 s and one more job costs about 42 s of setup.
        self.assertIn("matrix:\n        shard: [1]\n", job_text("site-unit"))

    def test_each_shard_takes_its_count_from_the_matrix(self):
        self.assertEqual(env_value("site-unit", "BUN_TEST_SHARD"), "${{ matrix.shard }}/${{ strategy.job-total }}")

    def test_only_a_pull_request_sets_a_base_so_a_push_to_main_runs_the_full_suite(self):
        self.assertEqual(
            env_value("site-unit", "BUN_TEST_BASE"),
            "${{ github.event_name == 'pull_request' && 'HEAD^1' || '' }}",
        )

    def test_a_pull_request_checks_out_the_base_commit_for_the_diff(self):
        self.assertIn(
            "fetch-depth: ${{ github.event_name == 'pull_request' && 2 || 1 }}", job_text("site-unit")
        )

    def test_the_gate_waits_for_the_unit_job(self):
        needs = re.search(r"needs: \[(.*)\]", WORKFLOW).group(1)
        self.assertIn("site-unit", needs)


if __name__ == "__main__":
    unittest.main()
