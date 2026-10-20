"""
Tests for the cornerstone command line.
They run the real console script.
"""
import subprocess


def test_help_lists_commands():
    out = subprocess.run(["uv", "run", "cornerstone", "--help"], capture_output=True, text=True)
    assert out.returncode == 0
    for cmd in ("build", "publish", "rewrite"):
        assert cmd in out.stdout
