"""
The build and rewrite pipeline for one week of the report.
It fetches, parses, writes, verifies, and renders, and it saves each step under data/.
"""
import json
import logging
import subprocess
from collections.abc import Callable
from pathlib import Path

from pydantic import TypeAdapter

from cornerstone.history import fetch_history, history_root
from cornerstone.models import Blurb, VerifyResult
from cornerstone.parse import parse_week
from cornerstone.render import _download_bytes, render_index, render_week
from cornerstone.sheet import build_bundle, check_week_is_buildable, read_bundle, write_bundle
from cornerstone.sleeper import fetch_news, fetch_state, fetch_week, load_raw
from cornerstone.verifier import write_and_verify
from cornerstone.writer import ClaudeCall

log = logging.getLogger(__name__)

LEAGUE_ID = "1386167364424318976"

NewsFetcher = Callable[[str], list[dict]]
BytesFetcher = Callable[[str], bytes | None]

_BLURBS = TypeAdapter(dict[str, Blurb])
_VERIFY = TypeAdapter(dict[str, list[VerifyResult]])


class BuildStopped(Exception):
    """The build cannot go on. The message tells the reader why."""


def week_dir(repo: Path, season: int, week: int) -> Path:
    return repo / "data" / str(season) / f"week-{week:02d}"


def has_raw(repo: Path, season: int, week: int) -> bool:
    return (week_dir(repo, season, week) / "raw" / "state.json").exists()


def resolve_week(season: int | None, week: int | None) -> tuple[int, int]:
    if season is not None and week is not None:
        return season, week
    state = fetch_state()
    # display_week is the week that people see in the Sleeper app.
    return (season if season is not None else int(state["season"]),
            week if week is not None else int(state["display_week"]))


def _save_blurbs(directory: Path, blurbs: dict[str, Blurb], verify: dict[str, list[VerifyResult]]) -> None:
    (directory / "blurbs.json").write_bytes(_BLURBS.dump_json(blurbs, indent=2))
    (directory / "verify.json").write_bytes(_VERIFY.dump_json(verify, indent=2))


def _log_chapter(key: str, blurb: Blurb) -> None:
    log.info("chapter %s: attempt %d, fallback %s", key, blurb.attempt, blurb.fallback)


def run_build(
    repo: Path,
    season: int,
    week: int,
    call: ClaudeCall,
    fetch: bool = True,
    news: NewsFetcher = fetch_news,
    fetch_bytes: BytesFetcher = _download_bytes,
) -> Path:
    directory = week_dir(repo, season, week)
    raw_dir = directory / "raw"
    if fetch:
        players_cache = repo / "data" / "cache" / "players.json"
        fetch_week(LEAGUE_ID, season, week, raw_dir, players_cache)
    elif not has_raw(repo, season, week):
        raise BuildStopped(f"No raw data for week {week}. Run without --no-fetch.")

    parsed = parse_week(load_raw(raw_dir), week=week)
    # The gate runs before any Claude call, so a week that is not final costs nothing.
    message = check_week_is_buildable(week, parsed.last_scored_week)
    if message:
        raise BuildStopped(message)

    bundle = build_bundle(parsed, news=news)
    write_bundle(bundle, directory / "facts.json")

    blurbs: dict[str, Blurb] = {}
    verify: dict[str, list[VerifyResult]] = {}
    for chapter in bundle.sheet.chapters:
        blurbs[chapter.key], verify[chapter.key] = write_and_verify(chapter, bundle.sheet, call)
        _log_chapter(chapter.key, blurbs[chapter.key])
    _save_blurbs(directory, blurbs, verify)

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    render_index(site_dir)
    return page


def run_rewrite(
    repo: Path,
    season: int,
    week: int,
    chapter: str,
    call: ClaudeCall,
    news: NewsFetcher = fetch_news,
    fetch_bytes: BytesFetcher = _download_bytes,
) -> Path:
    # The news argument keeps the signature the same as run_build. The saved facts need no news.
    directory = week_dir(repo, season, week)
    bundle = read_bundle(directory / "facts.json")
    chosen = next((c for c in bundle.sheet.chapters if c.key == chapter), None)
    if chosen is None:
        keys = ", ".join(c.key for c in bundle.sheet.chapters)
        raise ValueError(f"Unknown chapter '{chapter}'. Valid chapters: {keys}")

    blurbs = _BLURBS.validate_json((directory / "blurbs.json").read_text(encoding="utf-8"))
    verify = _VERIFY.validate_json((directory / "verify.json").read_text(encoding="utf-8"))
    blurbs[chapter], verify[chapter] = write_and_verify(chosen, bundle.sheet, call)
    _log_chapter(chapter, blurbs[chapter])
    _save_blurbs(directory, blurbs, verify)

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    render_index(site_dir)
    return page


def run_history(repo: Path, season: int, through: int, force: bool = False) -> list[int]:
    return fetch_history(LEAGUE_ID, season, through, history_root(repo, season), force=force)


def preview(page: Path) -> None:
    """Open the page and show a notification. A missing tool only logs a warning."""
    week = page.parent.name.removeprefix("week-").lstrip("0")
    script = f'display notification "Week {week} is ready to review" with title "Cornerstone Weekly"'
    for command in (["open", str(page)], ["osascript", "-e", script]):
        try:
            subprocess.run(command, check=False, capture_output=True)
        except OSError as err:
            log.warning("preview step %s failed: %s", command[0], err)
