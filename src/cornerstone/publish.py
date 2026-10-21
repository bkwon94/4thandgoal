"""
Publish a built week to the public site repo.
It commits the source repo, copies the site, then commits and pushes the site repo.
"""
import shutil
import subprocess
from pathlib import Path

from cornerstone.render import render_index


SITE_REPO = Path.home() / "repos" / "cpcfantasyfootball"
SITE_URL = "https://cpcfantasy.com/"


class PublishError(Exception):
    """A publish step failed. The message names the step and the cause."""


def _git(cwd: Path, *args: str, ok: tuple[int, ...] = (0,)) -> int:
    result = subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode not in ok:
        raise PublishError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip() or result.stdout.strip()}")
    return result.returncode


def _commit_if_staged(cwd: Path, message: str, *paths: str) -> None:
    # Ask git about staged changes instead of matching its message text. The message differs
    # when other untracked files exist, and a retry of a failed push must not stop here.
    if _git(cwd, "diff", "--cached", "--quiet", "--", *paths, ok=(0, 1)) == 0:
        return
    # The pathspec keeps any other staged change out of this commit.
    _git(cwd, "commit", "-m", message, "--", *paths)


def run_publish(repo: Path, season: int, week: int, site_repo: Path = SITE_REPO, push: bool = True) -> str:
    page = repo / "site" / str(season) / f"week-{week:02d}" / "index.html"
    if not page.exists():
        raise PublishError(f"{page} does not exist. Build the week first.")
    # Check the site repo before the first commit, so a bad path leaves no half-done publish.
    if not (site_repo / ".git").exists():
        raise PublishError(f"{site_repo} is not a git checkout.")

    _git(repo, "add", "site", "data")
    _commit_if_staged(repo, f"Week {week} report", "site", "data")

    # Copy only this week and the static files. A built but unpublished week must stay off
    # the public site, so the home page is rendered again from the weeks in the site repo.
    # The site repo is a Next.js app, and its static export serves public/ at the root.
    site_dir = site_repo / "public"
    week_path = Path(str(season)) / f"week-{week:02d}"
    shutil.copytree(repo / "site" / week_path, site_dir / week_path, dirs_exist_ok=True)
    shutil.copytree(repo / "site" / "static", site_dir / "static", dirs_exist_ok=True)
    render_index(site_dir)
    _git(site_repo, "add", "-A")
    _commit_if_staged(site_repo, f"Week {week}", ".")
    if push:
        _git(site_repo, "push")
    return SITE_URL + f"{season}/week-{week:02d}/"
