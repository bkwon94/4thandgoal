"""
Tests that CI runs the pipeline in two jobs, one for the parallel tests in 2 shards and one for the serial tests.
Each case reads the real workflow and asks the real Makefile what each job runs.
"""
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = (REPO / ".github/workflows/check.yml").read_text()


def job_text(name: str) -> str:
    match = re.search(rf"^  {re.escape(name)}:\n(.*?)(?=^  \S|\Z)", WORKFLOW, re.M | re.S)
    assert match, f"The workflow has no job {name}"
    return match.group(1)


def dry_run(target: str) -> str:
    """Prints the commands of a target of the pipeline Makefile, and runs none."""
    # In CI an outer make runs this test, so the child make gets MAKELEVEL and prints "Entering directory" lines.
    # --no-print-directory keeps those lines out, so the output holds only the commands.
    command = ["make", "--no-print-directory", "-n", target]
    return subprocess.run(command, cwd=REPO / "apps/pipeline", capture_output=True, text=True, check=True).stdout


class ThePipelineJobs(unittest.TestCase):
    def test_the_parallel_job_runs_the_parallel_tests_and_no_serial_test(self):
        commands = dry_run("check-parallel")
        self.assertIn("-n auto -m 'not live and not serial'", commands)
        self.assertNotIn("'serial and not live'", commands)
        self.assertIn("make check-pipeline-parallel", job_text("pipeline-parallel"))

    def test_the_parallel_job_runs_one_target_per_shard_of_its_matrix(self):
        job = job_text("pipeline-parallel")
        shards = re.search(r"shard: \[(.*)\]", job).group(1).split(", ")
        self.assertEqual(shards, ["1", "2"])
        self.assertIn("make check-pipeline-parallel-${{ matrix.shard }}", job)
        for shard in shards:
            commands = dry_run(f"check-parallel-{shard}")
            self.assertIn(f"PYTEST_SHARD={shard}/{len(shards)} ", commands)

    def test_the_shards_run_the_parallel_half_once_and_lint_and_typecheck_only_in_shard_1(self):
        def unsharded(target):
            return [re.sub(r"PYTEST_SHARD=\S+ ", "", line) for line in dry_run(target).splitlines()]

        whole = unsharded("check-parallel")
        first, second = unsharded("check-parallel-1"), unsharded("check-parallel-2")
        self.assertEqual(first, whole)
        self.assertEqual(second, [line for line in whole if "pytest" in line])

    def test_the_serial_job_runs_the_serial_tests_and_no_parallel_test(self):
        commands = dry_run("check-serial")
        self.assertIn("-p no:xdist -m 'serial and not live'", commands)
        self.assertNotIn("-n auto", commands)
        self.assertIn("make check-pipeline-serial", job_text("pipeline-serial"))

    def test_the_two_jobs_together_run_each_command_of_the_full_pipeline_check(self):
        full = {line.strip() for line in dry_run("check").splitlines() if "pytest" in line}
        halves = {
            line.strip()
            for target in ("check-parallel", "check-serial")
            for line in dry_run(target).splitlines()
            if "pytest" in line
        }
        self.assertEqual(full, halves)

    def test_the_old_single_pipeline_job_is_gone(self):
        self.assertNotRegex(WORKFLOW, r"^  pipeline:\n")

    def test_the_gate_waits_for_both_pipeline_jobs(self):
        needs = re.search(r"needs: \[(.*)\]", WORKFLOW).group(1)
        self.assertIn("pipeline-parallel", needs)
        self.assertIn("pipeline-serial", needs)


if __name__ == "__main__":
    unittest.main()
