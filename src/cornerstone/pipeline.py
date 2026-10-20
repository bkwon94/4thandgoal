"""
The build and rewrite pipeline for one week of the report.
It fetches, parses, writes, verifies, and renders, and it saves each step under data/.
"""
import json
import logging
import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter

from cornerstone.history import fetch_history, history_dir, history_root, load_history, save_week_to_history
from cornerstone.models import Blurb, BuildRecord, Bundle, History, VerifyFile, VerifyResult
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
_VERSION_1_VERIFY = TypeAdapter(dict[str, list[VerifyResult]])


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


def read_verify(path: Path) -> VerifyFile:
    """Read verify.json. A version 1 file is a plain dict of chapter lists and has no build record."""
    text = path.read_text(encoding="utf-8")
    if "chapters" in json.loads(text):
        return VerifyFile.model_validate_json(text)
    return VerifyFile(chapters=_VERSION_1_VERIFY.validate_json(text))


def _save_blurbs(directory: Path, blurbs: dict[str, Blurb], verify: VerifyFile) -> None:
    (directory / "blurbs.json").write_bytes(_BLURBS.dump_json(blurbs, indent=2))
    (directory / "verify.json").write_bytes(verify.model_dump_json(indent=2).encode("utf-8"))


def _load_history_or_none(root: Path, raw: dict[str, object], week: int) -> History | None:
    # A bad past week never stops a build. The facts that need the history drop out.
    try:
        return load_history(root, raw, week)
    except (OSError, ValueError, KeyError) as err:
        log.warning("history unreadable, build goes on without it: %s", err)
        return None


def make_bundle(
    repo: Path,
    season: int,
    week: int,
    news: NewsFetcher = fetch_news,
    started: datetime | None = None,
) -> tuple[Bundle, BuildRecord]:
    """Load the raw data, run the week gate, load the history, and build the bundle."""
    raw = load_raw(week_dir(repo, season, week) / "raw")
    parsed = parse_week(raw, week=week)
    # The gate runs before any Claude call, so a week that is not final costs nothing.
    message = check_week_is_buildable(week, parsed.last_scored_week)
    if message:
        raise BuildStopped(message)

    history = _load_history_or_none(history_root(repo, season), raw, week)
    bundle = build_bundle(parsed, news=news, history=history)
    record = BuildRecord(
        started=started or datetime.now(ZoneInfo("America/New_York")),
        sources={"history": history is not None and history.complete()},
    )
    return bundle, record


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

    bundle, record = make_bundle(repo, season, week, news)
    write_bundle(bundle, directory / "facts.json")

    blurbs: dict[str, Blurb] = {}
    verify: dict[str, list[VerifyResult]] = {}
    for chapter in bundle.sheet.chapters:
        blurbs[chapter.key], verify[chapter.key] = write_and_verify(chapter, bundle.sheet, call)
        _log_chapter(chapter.key, blurbs[chapter.key])
    _save_blurbs(directory, blurbs, VerifyFile(build=record, chapters=verify))

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    render_index(site_dir)
    # The page is built by now, so a history problem only logs a warning.
    try:
        save_week_to_history(raw_dir, history_dir(history_root(repo, season), week))
    except (OSError, ValueError, KeyError) as err:
        log.warning("week %d not saved to history: %s", week, err)
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
    verify = read_verify(directory / "verify.json")
    blurbs[chapter], verify.chapters[chapter] = write_and_verify(chosen, bundle.sheet, call)
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
