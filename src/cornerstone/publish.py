"""
Publish a built week to the public site repo.
It commits the source repo, copies the site, then commits and pushes the site repo.
"""
import shutil
import subprocess
from pathlib import Path

SITE_REPO = Path.home() / "repos" / "cpcfantasyfootball"
SITE_URL = "https://bkwon94.github.io/cpcfantasyfootball/"


class PublishError(Exception):
    """A publish step failed. The message names the step and the cause."""


def _git(cwd: Path, *args: str, allow_nothing_to_commit: bool = False) -> None:
    result = subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode == 0:
        return
    if allow_nothing_to_commit and "nothing to commit" in result.stdout + result.stderr:
        return
    raise PublishError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip() or result.stdout.strip()}")


def run_publish(repo: Path, season: int, week: int, site_repo: Path = SITE_REPO, push: bool = True) -> str:
    page = repo / "site" / str(season) / f"week-{week:02d}" / "index.html"
    if not page.exists():
        raise PublishError(f"{page} does not exist. Build the week first.")
    # Check the site repo before the first commit, so a bad path leaves no half-done publish.
    if not (site_repo / ".git").exists():
        raise PublishError(f"{site_repo} is not a git checkout.")

    _git(repo, "add", "site", "data")
    _git(repo, "commit", "-m", f"Week {week} report", allow_nothing_to_commit=True)

    shutil.copytree(repo / "site", site_repo, dirs_exist_ok=True)
    _git(site_repo, "add", "-A")
    _git(site_repo, "commit", "-m", f"Week {week}", allow_nothing_to_commit=True)
    if push:
        _git(site_repo, "push")
    return SITE_URL + f"{season}/week-{week:02d}/"
