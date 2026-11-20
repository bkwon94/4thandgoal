"""
Tests that CI runs the pipeline in two jobs, one for the parallel tests and one for the serial tests.
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
    return subprocess.run(["make", "-n", target], cwd=REPO / "apps/pipeline", capture_output=True, text=True, check=True).stdout


class ThePipelineJobs(unittest.TestCase):
    def test_the_parallel_job_runs_the_parallel_tests_and_no_serial_test(self):
        commands = dry_run("check-parallel")
        self.assertIn("-n auto -m 'not live and not serial'", commands)
        self.assertNotIn("'serial and not live'", commands)
        self.assertIn("make check-pipeline-parallel", job_text("pipeline-parallel"))

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
