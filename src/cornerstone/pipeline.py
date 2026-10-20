"""
The build and rewrite pipeline for one week of the report.
It fetches, parses, writes, verifies, and renders, and it saves each step under data/.
"""
import json
import logging
import subprocess
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter

from cornerstone.history import fetch_history, history_dir, history_root, load_history, save_week_to_history
from cornerstone.models import Blurb, BuildRecord, Bundle, History, NflverseWeek, Trade, VerifyFile, VerifyResult, Week
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_trades, parse_week
from cornerstone.render import _download_bytes, render_index, render_week
from cornerstone.sheet import build_bundle, check_week_is_buildable, read_bundle, write_bundle
from cornerstone.sleeper import fetch_news, fetch_state, fetch_week, load_raw, read_fetch_time, read_prev_transactions
from cornerstone.trades import default_cutoff, previous_fetch_time, trades_for_week
from cornerstone.verifier import write_and_verify
from cornerstone.writer import ClaudeCall

log = logging.getLogger(__name__)

LEAGUE_ID = "1386167364424318976"

NewsFetcher = Callable[[str], list[dict]]
BytesFetcher = Callable[[str], bytes | None]
# The fetch takes the season, the week, the rostered player IDs, the players file, and the Sleeper
# codes of the NFL teams whose started players played.
NflverseFetcher = Callable[[int, int, list[str], dict, set[str]], NflverseWeek]
NFLVERSE_SOURCES = ("nflverse_pbp", "nflverse_ftn", "nflverse_injuries", "ffverse")

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


def _window_trades(
    repo: Path, season: int, week: int, raw: dict[str, object], season_start: date, history: History | None,
    until: datetime,
) -> list[Trade]:
    # The window starts at the fetch of the build before. Without it, the Tuesday cut-off stands in.
    after = previous_fetch_time(repo, season, week) or default_cutoff(season_start, week)
    # The fresh copy of week N-1 holds the trades made after its build. The history copy does not.
    fresh = read_prev_transactions(week_dir(repo, season, week) / "raw")
    if fresh is not None:
        return trades_for_week(parse_trades(raw["transactions"]), parse_trades(fresh), after, until)
    last = history.weeks.get(week - 1) if history else None
    if last is None and week > 1:
        log.warning("week %d is not in the history: trades of its last hours may be missing", week - 1)
    elif week > 1:
        log.warning("no fresh transactions for week %d: the history copy stands in, "
                    "so a trade made after its build may be missing", week - 1)
    return trades_for_week(parse_trades(raw["transactions"]), last.trades if last else [], after, until)


def fetch_nflverse(repo: Path) -> NflverseFetcher:
    """Bind the one nflverse cache directory to the fetch. Tests patch this name with a fixture-backed fetcher."""
    cache_dir = repo / "data" / "cache" / "nflverse"

    def fetch(season: int, week: int, player_ids: list[str], players: dict, teams: set[str]) -> NflverseWeek:
        return nflverse_week(season, week, player_ids, players, cache_dir, teams)

    return fetch


def load_nflverse(raw_dir: Path) -> NflverseWeek | None:
    path = raw_dir / "nflverse.json"
    if not path.exists():
        return None
    return NflverseWeek.model_validate_json(path.read_text(encoding="utf-8"))


def _played_teams(week: Week) -> set[str]:
    """The NFL teams of the started players with a Sleeper gp above 0. Each one must have a game in nflverse."""
    return {
        line.nfl_team
        for m in week.matchups for side in (m.a, m.b) for line in side.lines
        if line.started and line.nfl_team and week.stats.get(line.player_id, {}).get("gp", 0) > 0
    }


def _nflverse_for_week(
    raw_dir: Path, raw: dict[str, object], season: int, week: int, nflverse: NflverseFetcher | None,
    teams: set[str],
) -> NflverseWeek | None:
    """The saved extract, or a fresh fetch. A failure of any kind never stops the build."""
    try:
        saved = load_nflverse(raw_dir)
        if saved is not None or nflverse is None:
            return saved
        rostered = sorted({pid for entry in raw["matchups"] for pid in entry["players"] if pid != "0"})
        nfl = nflverse(season, week, rostered, raw["players"], teams)
        # A degraded extract is not saved, so the next build tries the sources again.
        if all(nfl.sources.get(key) for key in NFLVERSE_SOURCES):
            (raw_dir / "nflverse.json").write_text(nfl.model_dump_json(indent=2), encoding="utf-8")
        return nfl
    except Exception as err:  # noqa: BLE001 - the outer guard: the module catches only HTTP errors
        log.warning("nflverse unavailable, build goes on without it: %s", err)
        return None


def _raw_fetch_time(repo: Path, season: int, week: int) -> datetime | None:
    """The write time of raw/transactions.json, the closest stand-in for a fetch time that was not saved."""
    # Version 1 saved no fetch time, so this happens for week 6 only. The build start would end the
    # window too late, so a trade made between the fetch and the rebuild would land on this page.
    path = week_dir(repo, season, week) / "raw" / "transactions.json"
    try:
        written = datetime.fromtimestamp(path.stat().st_mtime, ZoneInfo("America/New_York"))
    except OSError:
        return None
    log.warning("no fetch time for week %d: window ends at the write time of %s, %s", week, path, written.isoformat())
    return written


def make_bundle(
    repo: Path,
    season: int,
    week: int,
    news: NewsFetcher = fetch_news,
    started: datetime | None = None,
    fetched: datetime | None = None,
    nflverse: NflverseFetcher | None = None,
) -> tuple[Bundle, BuildRecord]:
    """Load the raw data, run the week gate, load the history, and build the bundle."""
    raw = load_raw(week_dir(repo, season, week) / "raw")
    parsed = parse_week(raw, week=week)
    # The gate runs before any Claude call, so a week that is not final costs nothing.
    message = check_week_is_buildable(week, parsed.last_scored_week)
    if message:
        raise BuildStopped(message)

    history = _load_history_or_none(history_root(repo, season), raw, week)
    started = started or datetime.now(ZoneInfo("America/New_York"))
    until = fetched or read_fetch_time(week_dir(repo, season, week) / "raw") or _raw_fetch_time(repo, season, week)
    if until is None:
        log.warning("no fetch time for week %d: window ends at the build start", week)
        until = started
    trades = _window_trades(repo, season, week, raw, parsed.season_start, history, until)
    nfl = _nflverse_for_week(week_dir(repo, season, week) / "raw", raw, season, week, nflverse, _played_teams(parsed))
    bundle = build_bundle(parsed, news=news, history=history, trades=trades, nfl=nfl)
    record = BuildRecord(
        started=started,
        sources={"history": history is not None and history.complete(),
                 **{key: nfl is not None and nfl.sources.get(key, False) for key in NFLVERSE_SOURCES}},
        fetched=until,
    )
    return bundle, record


def _first_build(saved: Path) -> BuildRecord | None:
    """The build record of an earlier build of this week. None when there is none or it is unreadable."""
    if not saved.exists():
        return None
    # A corrupt file must not stop a rebuild. The fetch time then comes from the raw directory.
    try:
        return read_verify(saved).build
    except (OSError, ValueError, KeyError, TypeError) as err:
        log.warning("%s is unreadable, so the rebuild takes a new window end: %s", saved, err)
        return None


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
    nflverse: NflverseFetcher | None = None,
) -> Path:
    directory = week_dir(repo, season, week)
    raw_dir = directory / "raw"
    # A rebuild keeps the first window, also after a refetch, so a trade never moves to another page.
    saved = directory / "verify.json"
    first_fetch = _first_build(saved)
    if fetch:
        players_cache = repo / "data" / "cache" / "players.json"
        fetch_week(LEAGUE_ID, season, week, raw_dir, players_cache)
    elif not has_raw(repo, season, week):
        raise BuildStopped(f"No raw data for week {week}. Run without --no-fetch.")

    # No argument means the real fetch. A test passes a fixture-backed one.
    bundle, record = make_bundle(
        repo, season, week, news, fetched=first_fetch.fetched if first_fetch else None,
        nflverse=nflverse or fetch_nflverse(repo))
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
    nflverse: NflverseFetcher | None = None,
) -> Path:
    # The news and nflverse arguments keep the signature the same as run_build.
    # A rewrite reads the saved facts, so it needs neither news nor a fetch.
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
