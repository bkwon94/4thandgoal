"""
Publish a built week into the published data of its client, clients/<slug>/published/, in the same repo.
It commits the built site and the client data, copies the week folder and the season files, then commits the season folder only and pushes.
"""
import logging
import shutil
import subprocess
from pathlib import Path

from league.paths import season_dir, site_week_dir, week_label

# Each client serves at its own subdomain, from the Cloudflare Worker named by its slug.
SITE_DOMAIN = "4thandgoal.app"

log = logging.getLogger(__name__)


def site_page_url(slug: str, season: int, week: int) -> str:
    """The public URL of one week's page of the client `slug`."""
    return f"https://{slug}.{SITE_DOMAIN}/{season}/{week_label(week)}/"


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


def _repo_root(repo: Path) -> Path:
    # Why: the pipeline and the site live in one repo, so the site is the root of the pipeline's own
    # checkout. A fixed path to a second checkout breaks in a worktree and on any other machine.
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=repo, check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise PublishError(f"{repo} is not in a git checkout: {result.stderr.strip()}")
    return Path(result.stdout.strip())


def run_publish(
        repo: Path, season: int, week: int, slug: str, data: Path, site_repo: Path | None = None,
        push: bool = True) -> str:
    """Publish one week of the client `slug`. `data` is the data folder of the client. The site repo is the root of
    the pipeline's checkout, unless a test names another."""
    page = site_week_dir(repo / "site", season, week) / "page.json"
    if not page.exists():
        raise PublishError(f"{page} does not exist. Build the week first.")
    if site_repo is None:
        site_repo = _repo_root(repo)
    # Check the site repo before the first commit, so a bad path leaves no half-done publish.
    if not (site_repo / ".git").exists():
        raise PublishError(f"{site_repo} is not a git checkout.")

    _git(repo, "add", "site", str(data))
    _commit_if_staged(repo, f"Week {week} report", "site", str(data))

    # Copy only this week: its page.json, avatars, and headshots. A built but unpublished week must
    # stay off the public site. The site is a Next.js app. It renders the pages and the home
    # page from these folders.
    # Why: each client keeps its data in its own folder, and the site build copies only that client's published data.
    public_dir = site_repo / "clients" / slug / "published"
    week_path = Path(str(season)) / week_label(week)
    shutil.copytree(
        repo / "site" / week_path, public_dir / week_path, dirs_exist_ok=True
    )
    # The season file holds every week to date, so it goes out with the week in the same commit.
    rankings = season_dir(repo / "site", season) / "rankings.json"
    if rankings.exists():
        shutil.copy2(rankings, public_dir / str(season) / "rankings.json")
    else:
        log.warning("%s missing: the publish goes out without rankings.json", rankings)
    # The managers file is a season file too. A thin history has none, so a missing file only warns.
    managers = season_dir(repo / "site", season) / "managers.json"
    if managers.exists():
        shutil.copy2(managers, public_dir / str(season) / "managers.json")
    else:
        log.warning("%s missing: the publish goes out without managers.json", managers)
    # Why: the repo holds code and notes too. Staging the season folder of the client only keeps a stray change
    # elsewhere in the tree out of the commit. ADR 0019 allows the push to main on this one condition.
    published = str((public_dir / str(season)).relative_to(site_repo))
    _git(site_repo, "add", "--", published)
    _commit_if_staged(site_repo, f"Week {week}", published)
    if push:
        _git(site_repo, "push")
    return site_page_url(slug, season, week)
