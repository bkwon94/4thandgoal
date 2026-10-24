"""
The build and rewrite pipeline for one week of the report.
It fetches, parses, writes, verifies, and renders, and it saves each step under data/.
"""
import contextlib
import json
import logging
import subprocess
from collections.abc import Callable, Iterable
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter

from cornerstone.facts_league import season_records, standings_order
from cornerstone.history import (
    fetch_history, history_dir, history_root, load_history, load_saved_weeks, returns_path, save_week_to_history,
    saved_through,
)
from cornerstone.models import (
    Blurb, BuildRecord, Bundle, Chapter, History, NflverseWeek, Team, Trade, VerifyFile, VerifyResult, Week,
)
from cornerstone.nflverse import nflverse_week
from cornerstone.odds import OddsResult
from cornerstone.parse import parse_trades, parse_week
from cornerstone.power_rankings import power_rankings
from cornerstone.render import _download_bytes, render_page_json, render_rankings, render_week
from cornerstone.sheet import (
    RANKINGS_CHAPTER, build_bundle, check_week_is_buildable, power_facts, rank_why_facts, rankings_chapter, read_bundle,
    required_why_ids, write_bundle,
)
from cornerstone.sleeper import fetch_news, fetch_state, fetch_week, load_raw, read_fetch_time, read_prev_transactions
from cornerstone.slow_sources import load_slow_sources
from cornerstone.snapshot import load_returns
from cornerstone.trades import default_cutoff, trades_for_week
from cornerstone.verifier import write_and_verify
from cornerstone.waiver import waiver_board
from cornerstone.waiver_price import bid_history
from cornerstone.waiver_research import SearchCall, research_board, search_call
from cornerstone.writer import ClaudeCall

log = logging.getLogger(__name__)

LEAGUE_ID = "1386167364424318976"

NewsFetcher = Callable[[str], list[dict]]
BytesFetcher = Callable[[str], bytes | None]
# The fetch takes the season, the week, the rostered player IDs, the players file, the Sleeper
# codes of the NFL teams whose started players played, and the league scoring.
NflverseFetcher = Callable[[int, int, list[str], dict, set[str], dict], NflverseWeek]
NFLVERSE_SOURCES = ("nflverse_pbp", "nflverse_ftn", "nflverse_injuries", "ffverse", "nflverse_snaps", "ffopportunity")

_BLURBS = TypeAdapter(dict[str, Blurb])
HISTORY_GAP = "The history is missing a week from 1 to {week}. Run cornerstone history --through {week}."
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
) -> list[Trade]:
    # The window is the calendar span between two Tuesday cutoffs, so build time plays no part.
    after = default_cutoff(season_start, week)
    until = default_cutoff(season_start, week + 1)
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


def nflverse_cache_dir(repo: Path) -> Path:
    """The one nflverse cache directory. The fetch fills it and the analyze command reads it."""
    return repo / "data" / "cache" / "nflverse"


def fetch_nflverse(repo: Path) -> NflverseFetcher:
    """Bind the one nflverse cache directory to the fetch. Tests patch this name with a fixture-backed fetcher."""
    cache_dir = nflverse_cache_dir(repo)

    def fetch(season: int, week: int, player_ids: list[str], players: dict, teams: set[str],
              scoring: dict) -> NflverseWeek:
        return nflverse_week(season, week, player_ids, players, cache_dir, teams, scoring=scoring)

    return fetch


def load_nflverse(raw_dir: Path) -> NflverseWeek | None:
    path = raw_dir / "nflverse.json"
    if not path.exists():
        return None
    return NflverseWeek.model_validate_json(path.read_text(encoding="utf-8"))


def _save_nflverse(path: Path, nfl: NflverseWeek) -> None:
    # The fetch is good, so a failed write must not cost this build its drops. The next build fetches again.
    try:
        path.write_text(nfl.model_dump_json(indent=2), encoding="utf-8")
    except OSError as err:
        log.warning("nflverse extract not saved to %s, build goes on with it: %s", path, err)
        # A half-written file would load as a broken extract and block the next fetch.
        with contextlib.suppress(OSError):
            path.unlink(missing_ok=True)


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
        nfl = nflverse(season, week, rostered, raw["players"], teams, raw["league"]["scoring_settings"])
        # A degraded extract is not saved, so the next build tries the sources again.
        if all(nfl.sources.get(key) for key in NFLVERSE_SOURCES):
            _save_nflverse(raw_dir / "nflverse.json", nfl)
        return nfl
    except Exception as err:  # noqa: BLE001 - the outer guard: the module catches only HTTP errors
        log.warning("nflverse unavailable, build goes on without it: %s", err)
        return None


def _raw_fetch_time(repo: Path, season: int, week: int) -> datetime | None:
    """The write time of raw/transactions.json, the closest stand-in for a fetch time that was not saved."""
    # Version 1 saved no fetch time, so this happens for week 6 only. The write time is closer to the
    # real fetch time than the build start is.
    path = week_dir(repo, season, week) / "raw" / "transactions.json"
    try:
        written = datetime.fromtimestamp(path.stat().st_mtime, ZoneInfo("America/New_York"))
    except OSError:
        return None
    log.warning("no fetch time for week %d: the fetch time falls back to the write time of %s, %s", week, path, written.isoformat())
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
    """Load the raw data, run the week gate, load the history, and build the bundle and the waiver board."""
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
        log.warning("no fetch time for week %d: the fetch time falls back to the build start", week)
        until = started
    trades = _window_trades(repo, season, week, raw, parsed.season_start, history)
    nfl = _nflverse_for_week(week_dir(repo, season, week) / "raw", raw, season, week, nflverse, _played_teams(parsed))
    bundle = build_bundle(parsed, news=news, history=history, trades=trades, nfl=nfl)
    # The board reaches the saved facts, so a rewrite writes the waiver file and never runs the engine.
    # The board runs after week N, as the trade analyzer runs in trade week N + 1, so the slow sources read
    # with week + 1. They read the cache the nflverse fetch fills, with no network call.
    slow = load_slow_sources(nflverse_cache_dir(repo), season, week + 1, history_root(repo, season))
    bundle.waiver = waiver_board(raw, week, started, nfl, claims=bid_history(history_root(repo, season), raw, week),
                                 slow=slow, returns=load_returns(returns_path(repo, season)))
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
    research: SearchCall | None = None,
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
    # The research runs once here, after the engine. The claims save with the facts, so a rewrite reads them.
    # No argument means the real search. A test passes a fake one.
    if bundle.waiver is not None:
        bundle.waiver = research_board(bundle.waiver, research or search_call)
    write_bundle(bundle, directory / "facts.json")

    blurbs: dict[str, Blurb] = {}
    verify: dict[str, list[VerifyResult]] = {}
    for chapter in bundle.sheet.chapters:
        blurbs[chapter.key], verify[chapter.key] = write_and_verify(chapter, bundle.sheet, call)
        _log_chapter(chapter.key, blurbs[chapter.key])
    _save_blurbs(directory, blurbs, VerifyFile(build=record, chapters=verify))

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    # The page is built by now, so a history problem only logs a warning.
    try:
        save_week_to_history(raw_dir, history_dir(history_root(repo, season), week))
    except (OSError, ValueError, KeyError) as err:
        log.warning("week %d not saved to history: %s", week, err)
    # The season file reads the saved history, so it comes after the save. A missing past week never blocks the page.
    try:
        rankings = _write_rankings(repo, season, week, bundle.data.teams, blurbs.get(RANKINGS_CHAPTER), bundle.odds)
        if rankings is None:
            log.warning("history incomplete through week %d: rankings.json not written", week)
    except (OSError, ValueError, KeyError) as err:
        log.warning("rankings.json not written for week %d: %s", week, err)
    return page


def _write_rankings(
    repo: Path, season: int, week: int, teams: dict[int, Team], blurb: Blurb | None = None,
    odds: OddsResult | None = None,
) -> Path | None:
    """Write rankings.json from the saved history of weeks 1 to the latest complete week, never less than `week`.
    The rankings blurb and the `odds` go into the rows of `week`. None when a week from 1 to `week` is missing."""
    # A fallback blurb has no roster tags, so it would write an empty blurb for every team. With no blurb, the
    # week keeps the blurbs of the last file.
    if blurb is not None and blurb.fallback:
        blurb = None
    root = history_root(repo, season)
    # The file holds every week to date. A rebuild of an older week must not cut the later weeks from it.
    through = saved_through(root, week)
    history = History(week=through, weeks=load_saved_weeks(root, through))
    # A gap would shift every rank after it, so the file waits for a complete history.
    if not history.complete():
        return None
    if through > week:
        log.info("rankings.json covers weeks 1 to %d, past the built week %d", through, week)
    return render_rankings(history, season, teams, repo / "site", week, blurb, odds)


def _load_saved_week(repo: Path, season: int, week: int) -> tuple[Bundle, dict[str, Blurb]]:
    """Read the saved facts and blurbs of a week."""
    directory = week_dir(repo, season, week)
    bundle = read_bundle(directory / "facts.json")
    blurbs = _BLURBS.validate_json((directory / "blurbs.json").read_text(encoding="utf-8"))
    return bundle, blurbs


def run_rewrite(
    repo: Path,
    season: int,
    week: int,
    chapter: str,
    call: ClaudeCall,
    news: NewsFetcher = fetch_news,
    fetch_bytes: BytesFetcher = _download_bytes,
    nflverse: NflverseFetcher | None = None,
    research: SearchCall | None = None,
) -> Path:
    # The news, nflverse, and research arguments keep the signature the same as run_build.
    # A rewrite reads the saved facts and the saved claims, so it needs no news, no fetch, and no search.
    directory = week_dir(repo, season, week)
    bundle, blurbs = _load_saved_week(repo, season, week)
    chosen = next((c for c in bundle.sheet.chapters if c.key == chapter), None)
    if chosen is None:
        keys = ", ".join(c.key for c in bundle.sheet.chapters)
        raise ValueError(f"Unknown chapter '{chapter}'. Valid chapters: {keys}")

    verify = read_verify(directory / "verify.json")
    blurbs[chapter], verify.chapters[chapter] = write_and_verify(chosen, bundle.sheet, call)
    _log_chapter(chapter, blurbs[chapter])
    _save_blurbs(directory, blurbs, verify)

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    # The season file holds the rankings blurb, so a rewrite of the chapter must reach the file too.
    if chapter == RANKINGS_CHAPTER:
        try:
            if _write_rankings(repo, season, week, bundle.data.teams, blurbs[chapter], bundle.odds) is None:
                log.warning("history incomplete through week %d: rankings.json not written", week)
        except (OSError, ValueError, KeyError) as err:
            log.warning("rankings.json not written for week %d: %s", week, err)
    return page


def run_page_json(repo: Path, season: int, week: int) -> Path:
    """Write page.json for a saved week from its facts and blurbs. It calls no writer and no network."""
    bundle, blurbs = _load_saved_week(repo, season, week)
    return render_page_json(bundle, blurbs, repo / "site")


def _rankings_chapter(bundle: Bundle, history: History) -> tuple[Chapter, bool]:
    """The rankings chapter of a saved week, and True when the bundle had to take it in.

    A saved week with no rankings chapter has no PR facts, so they come from the saved history.
    A saved chapter that lacks a why family is built again, so the blurb can cite the rank why and the odds why.
    Week 1 of the rankings has no rank why. The odds why comes only from the saved facts, never from the raw week.
    """
    chapter = next((c for c in bundle.sheet.chapters if c.key == RANKINGS_CHAPTER), None)
    rows = power_rankings(history, history.week)[history.week]

    def has_why(prefix: str, ids: Iterable[str]) -> bool:
        return any(fid.startswith(prefix) and fid.endswith(".why") for fid in ids)

    if chapter is not None:
        rank_why_ok = history.week < 2 or has_why("PR.", chapter.fact_ids)
        odds_why_ok = not has_why("ODDS.", bundle.sheet.facts) or has_why("ODDS.", chapter.fact_ids)
        if rank_why_ok and odds_why_ok:
            # A saved chapter can predate the required list, so the list comes from the rows each time.
            chapter.required = required_why_ids(bundle.sheet.facts, rows, bundle.data.table, bundle.odds)
            return chapter, False

    def team(roster_id: int) -> str:
        return bundle.data.teams[roster_id].name

    # A saved week has no Week for ranks_before. With a complete history, ranks_before ranks the records
    # through week N-1 in standings order, the same as here.
    before = (
        {rid: i + 1 for i, rid in enumerate(standings_order(season_records(history, history.week - 1)))}
        if history.week > 1 else {}
    )
    bundle.sheet.facts.update({f.id: f for f in power_facts(rows, team)})
    bundle.sheet.facts.update({f.id: f for f in rank_why_facts(history, rows, before, team)})
    built = rankings_chapter(bundle.sheet.facts, rows, team, bundle.data.table, bundle.odds)
    bundle.sheet.chapters = [c for c in bundle.sheet.chapters if c.key != RANKINGS_CHAPTER] + [built]
    return built, True


def run_rankings(repo: Path, season: int, week: int, call: ClaudeCall) -> Path:
    """Write the rankings blurb of a saved week with one writer call, then rankings.json from the saved history.
    The writer runs for this week only. The other weeks keep the blurbs of the last file."""
    directory = week_dir(repo, season, week)
    bundle, blurbs = _load_saved_week(repo, season, week)
    history = History(week=week, weeks=load_saved_weeks(history_root(repo, season), week))
    # The check comes before the writer call, so a missing week costs no Claude call.
    if not history.complete():
        raise BuildStopped(HISTORY_GAP.format(week=week))
    chapter, added = _rankings_chapter(bundle, history)
    if added:
        # The saved facts must hold the PR facts the blurb cites, so a later rewrite finds them.
        write_bundle(bundle, directory / "facts.json")
    verify = read_verify(directory / "verify.json")
    blurbs[chapter.key], verify.chapters[chapter.key] = write_and_verify(chapter, bundle.sheet, call)
    _log_chapter(chapter.key, blurbs[chapter.key])
    _save_blurbs(directory, blurbs, verify)
    out = _write_rankings(repo, season, week, bundle.data.teams, blurbs[chapter.key], bundle.odds)
    if out is None:
        raise BuildStopped(HISTORY_GAP.format(week=week))
    return out


def run_history(repo: Path, season: int, through: int, force: bool = False) -> list[int]:
    return fetch_history(LEAGUE_ID, season, through, history_root(repo, season), force=force)


def preview(page: Path) -> None:
    """Show a notification that the week is built. A missing tool only logs a warning."""
    week = page.parent.name.removeprefix("week-").lstrip("0")
    script = f'display notification "Week {week} is ready to review" with title "Cornerstone Weekly"'
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except OSError as err:
        log.warning("preview step osascript failed: %s", err)
