"""
Tests scripts/parallel.py with real shell commands: the jobs run at the same time, each output prints as one block with
its name and its time, and the exit code is 1 when one job fails.
"""
import subprocess
import time
import unittest
from pathlib import Path

PARALLEL = Path(__file__).resolve().parent / "parallel.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["python3", "-B", str(PARALLEL), *args], capture_output=True, text=True)


class TheParallelRunner(unittest.TestCase):
    def test_two_jobs_run_at_the_same_time(self):
        start = time.monotonic()
        result = run("one", "sleep 1", "two", "sleep 1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        # In sequence the two jobs take 2 s. At the same time they take about 1 s.
        self.assertLess(time.monotonic() - start, 1.9)

    def test_each_output_prints_as_one_block_with_its_name(self):
        result = run("slow", "echo a1; sleep 0.4; echo a2", "fast", "echo b1; sleep 0.1; echo b2")
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        # The fast job ends first, so its block prints first, and no line of the slow job sits inside it.
        fast = next(i for i, line in enumerate(lines) if line.startswith("==> fast: ok"))
        slow = next(i for i, line in enumerate(lines) if line.startswith("==> slow: ok"))
        self.assertLess(fast, slow)
        self.assertEqual(lines[fast - 2:fast], ["b1", "b2"])
        self.assertEqual(lines[slow - 2:slow], ["a1", "a2"])

    def test_one_failed_job_gives_exit_code_1_and_the_other_job_still_ends(self):
        result = run("bad", "echo broken >&2; exit 3", "good", "sleep 0.2; echo done")
        self.assertEqual(result.returncode, 1)
        self.assertIn("broken", result.stdout)
        self.assertIn("==> bad: FAILED with exit code 3", result.stdout)
        self.assertIn("done", result.stdout)
        self.assertIn("==> good: ok", result.stdout)

    def test_an_odd_count_of_arguments_is_a_usage_error(self):
        result = run("lonely")
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr)


if __name__ == "__main__":
    unittest.main()
