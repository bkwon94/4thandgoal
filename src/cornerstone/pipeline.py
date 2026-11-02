"""
The build and rewrite pipeline for one week of the report.
It fetches, parses, writes, verifies, and renders, and it saves each step under data/.
"""
import contextlib
import json
import logging
import subprocess
from collections.abc import Callable
from datetime import date, datetime
from functools import partial
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter

from cornerstone.chart import match_chart, saved_chart_read
from cornerstone.claude_port import Writer
from cornerstone.config import LeagueConfig
from cornerstone.history import fetch_history, load_history, load_saved_weeks, save_week_to_history, saved_through
from cornerstone.manager_season import saved_awards
from cornerstone.managers import MIN_WEEKS as MANAGERS_MIN_WEEKS
from cornerstone.models import (
    Blurb,
    BuildRecord,
    Bundle,
    Chapter,
    ChartValues,
    History,
    NflverseWeek,
    OddsResult,
    ProjectionsAhead,
    Team,
    Trade,
    VerifyFile,
    VerifyResult,
    Week,
    week_lines,
)
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_trades, parse_week
from cornerstone.paths import (
    history_dir,
    history_root,
    nflverse_cache_dir,
    players_cache,
    raw_dir,
    returns_path,
    week_dir,
    week_from_label,
)
from cornerstone.power_rankings import power_rankings
from cornerstone.provider.base import Provider
from cornerstone.provider.raw import RawState, RawWeek
from cornerstone.provider.sleeper import (
    PROJECTIONS_AHEAD_FILE,
    SLEEPER,
    fetch_news,
    fetch_state,
    load_raw,
    read_fetch_time,
    read_prev_transactions,
)
from cornerstone.render import _download_bytes, render_managers, render_page_json, render_rankings, render_week
from cornerstone.season_inputs import SeasonInputs
from cornerstone.sheet import (
    RANKINGS_CHAPTER,
    build_bundle,
    check_week_is_buildable,
    power_facts,
    rank_why_facts,
    rankings_chapter,
    read_bundle,
    write_bundle,
)
from cornerstone.slow_sources import load_slow_sources
from cornerstone.snapshot import Snapshot, load_returns, week_snapshot
from cornerstone.standings_table import season_records, standings_order
from cornerstone.trades import default_cutoff, trades_for_week
from cornerstone.verifier import page_words, reserved_words, write_and_verify
from cornerstone.waiver import waiver_board
from cornerstone.waiver_price import bid_history
from cornerstone.waiver_research import SearchCall, research_board, search_call
from cornerstone.writer import ClaudeCall

log = logging.getLogger(__name__)

NewsFetcher = Callable[[str], list[dict]]
RawLoader = Callable[[Path], RawWeek]
BytesFetcher = Callable[[str], bytes | None]
# The fetch takes the season, the week, the rostered player IDs, the players file, the Sleeper
# codes of the NFL teams whose started players played, and the league scoring.
NflverseFetcher = Callable[[int, int, list[str], dict, set[str], dict], NflverseWeek]
NFLVERSE_SOURCES = ("nflverse_pbp", "nflverse_ftn", "nflverse_injuries", "ffverse", "nflverse_snaps", "ffopportunity",
                    "nflverse_stats_player")

_BLURBS = TypeAdapter(dict[str, Blurb])
HISTORY_GAP = "The history is missing a week from 1 to {week}. Run cornerstone history --through {week}."
_VERSION_1_VERIFY = TypeAdapter(dict[str, list[VerifyResult]])


class BuildStopped(Exception):
    """The build cannot go on. The message tells the reader why."""


def has_raw(repo: Path, season: int, week: int) -> bool:
    return (raw_dir(repo, season, week) / "state.json").exists()


def resolve_week(
        season: int | None, week: int | None, fetch_state: Callable[[], RawState] = fetch_state,
) -> tuple[int, int]:
    # The state fetch is a parameter, so the CLI passes the one it got.
    if season is not None and week is not None:
        return season, week
    state = fetch_state()
    # display_week is the week that people see in the Sleeper app.
    return (season if season is not None else int(state.season),
            week if week is not None else state.display_week)


def read_verify(path: Path) -> VerifyFile:
    """Read verify.json. A version 1 file is a plain dict of chapter lists and has no build record."""
    text = path.read_text(encoding="utf-8")
    if "chapters" in json.loads(text):
        return VerifyFile.model_validate_json(text)
    return VerifyFile(chapters=_VERSION_1_VERIFY.validate_json(text))


def _save_blurbs(directory: Path, blurbs: dict[str, Blurb], verify: VerifyFile) -> None:
    (directory / "blurbs.json").write_bytes(_BLURBS.dump_json(blurbs, indent=2))
    (directory / "verify.json").write_bytes(verify.model_dump_json(indent=2).encode("utf-8"))


def _load_history_or_none(root: Path, raw: RawWeek, week: int) -> History | None:
    # A bad past week never stops a build. The facts that need the history drop out.
    try:
        return load_history(root, raw, week)
    except (OSError, ValueError, KeyError) as err:
        log.warning("history unreadable, build goes on without it: %s", err)
        return None


def _window_trades(
    repo: Path, season: int, week: int, raw: RawWeek, season_start: date, history: History | None,
    tz: ZoneInfo,
) -> list[Trade]:
    # The window is the calendar span between two Tuesday cutoffs, so build time plays no part.
    after = default_cutoff(season_start, week, tz)
    until = default_cutoff(season_start, week + 1, tz)
    # The fresh copy of week N-1 holds the trades made after its build. The history copy does not.
    fresh = read_prev_transactions(raw_dir(repo, season, week))
    if fresh is not None:
        return trades_for_week(parse_trades(raw.transactions), parse_trades(fresh), after, until)
    last = history.weeks.get(week - 1) if history else None
    if last is None and week > 1:
        log.warning("week %d is not in the history: trades of its last hours may be missing", week - 1)
    elif week > 1:
        log.warning("no fresh transactions for week %d: the history copy stands in, "
                    "so a trade made after its build may be missing", week - 1)
    return trades_for_week(parse_trades(raw.transactions), last.trades if last else [], after, until)


def fetch_nflverse(repo: Path) -> NflverseFetcher:
    """Bind the one nflverse cache directory to the fetch. Tests patch this name with a fixture-backed fetcher."""
    cache_dir = nflverse_cache_dir(repo)

    def fetch(season: int, week: int, player_ids: list[str], players: dict, teams: set[str],
              scoring: dict) -> NflverseWeek:
        return nflverse_week(season, week, player_ids, players, cache_dir, teams, scoring=scoring)

    return fetch


def load_nflverse(raw_path: Path) -> NflverseWeek | None:
    path = raw_path / "nflverse.json"
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


def _with_saved(nfl: NflverseWeek, saved: NflverseWeek) -> NflverseWeek:
    """The saved extract, with each key it lacks filled from the refetch.

    A down source can give smaller dicts, not None, so the saved value wins for every key the file holds. The
    flags of the saved file cover its keys, and the fresh flags cover the keys the refetch fills.
    """
    kept = {key: getattr(saved, key) for key in saved.model_fields_set}
    return nfl.model_copy(update={**kept, "sources": {**nfl.sources, **saved.sources}})


def _nflverse_for_week(
    raw_path: Path, raw: RawWeek, season: int, week: int, nflverse: NflverseFetcher | None,
    teams: set[str],
) -> NflverseWeek | None:
    """The saved extract, or a fresh fetch. A failure of any kind never stops the build.

    A saved extract that lacks a key of NflverseWeek comes from an older build, so the build fetches it again.
    The refetch fills only the keys the file lacks, and every saved key keeps its value. So a source that is
    down now never costs the rebuild a fact it had. The build rewrites the file only when the refetch is complete.
    """
    saved = None
    try:
        saved = load_nflverse(raw_path)
        if nflverse is None:
            return saved
        # A key the file does not hold loads as None, so only the set fields tell an old file from a new one.
        if saved is not None:
            missing = sorted(set(NflverseWeek.model_fields) - saved.model_fields_set)
            if not missing:
                return saved
            log.info("week %d nflverse.json lacks %s, so the build fetches the extract again", week,
                     ", ".join(missing))
        rostered = sorted({pid for entry in raw.matchups for pid in entry.players or [] if pid != "0"})
        nfl = nflverse(season, week, rostered, raw.players, teams, raw.league.scoring_settings)
        # The check reads the fresh flags, not the merged ones. A merged extract has every key, so the build would
        # never fetch a saved one again, though a degraded source cut its rows.
        complete = all(nfl.sources.get(key) for key in NFLVERSE_SOURCES)
        if saved is not None:
            nfl = _with_saved(nfl, saved)
        # A degraded extract is not saved, so the next build tries the sources again.
        if complete:
            _save_nflverse(raw_path / "nflverse.json", nfl)
        return nfl
    except Exception as err:  # noqa: BLE001 - the outer guard: the module catches only HTTP errors
        # The saved file stays as it was, and the build goes on with the facts it holds.
        if saved is not None:
            log.warning("nflverse refetch failed, build goes on with the saved extract: %s", err)
            return saved
        log.warning("nflverse unavailable, build goes on without it: %s", err)
        return None


def _raw_fetch_time(repo: Path, season: int, week: int, tz: ZoneInfo) -> datetime | None:
    """The write time of raw/transactions.json, the closest stand-in for a fetch time that was not saved."""
    # Version 1 saved no fetch time, so this happens for week 6 only. The write time is closer to the
    # real fetch time than the build start is.
    path = raw_dir(repo, season, week) / "transactions.json"
    try:
        written = datetime.fromtimestamp(path.stat().st_mtime, tz)
    except OSError:
        return None
    log.warning(
        "no fetch time for week %d: the fetch time falls back to the write time of %s, %s",
        week, path, written.isoformat(),
    )
    return written


def make_bundle(
    repo: Path,
    season: int,
    week: int,
    news: NewsFetcher = fetch_news,
    started: datetime | None = None,
    fetched: datetime | None = None,
    nflverse: NflverseFetcher | None = None,
    *,
    config: LeagueConfig,
    raw: dict | None = None,
) -> tuple[Bundle, BuildRecord]:
    """Load the raw data, run the week gate, load the history, and build the bundle and the waiver board.
    The build passes the `raw` week it loaded, so the week loads once. None loads it here."""
    if raw is None:
        raw = load_raw(raw_dir(repo, season, week))
    parsed = parse_week(raw, config.owner_username, week=week, team_count=config.team_count)
    # The gate runs before any Claude call, so a week that is not final costs nothing.
    message = check_week_is_buildable(week, parsed.last_scored_week, config)
    if message:
        raise BuildStopped(message)

    history = _load_history_or_none(history_root(repo, season), raw, week)
    started = started or datetime.now(config.tz)
    until = (fetched or read_fetch_time(raw_dir(repo, season, week))
             or _raw_fetch_time(repo, season, week, config.tz))
    if until is None:
        log.warning("no fetch time for week %d: the fetch time falls back to the build start", week)
        until = started
    trades = _window_trades(repo, season, week, raw, parsed.season_start, history, config.tz)
    nfl = _nflverse_for_week(raw_dir(repo, season, week), raw, season, week, nflverse, _played_teams(parsed))
    # The bye facts read the position rank and the bye cover from the analyzer's snapshot of the league after week N.
    snapshot = week_snapshot(raw, history_root(repo, season), week, config=config)
    bundle = build_bundle(parsed, news=news, history=history, trades=trades, nfl=nfl, snapshot=snapshot,
                          today=started.date(), config=config)
    # The board reaches the saved facts, so a rewrite writes the waiver file and never runs the engine.
    # The board runs after week N, as the trade analyzer runs in trade week N + 1, so the slow sources read
    # with week + 1. They read the cache the nflverse fetch fills, with no network call.
    slow = load_slow_sources(nflverse_cache_dir(repo), season, week + 1, history_root(repo, season))
    bundle.waiver = waiver_board(raw, week, started, nfl, claims=bid_history(history_root(repo, season), raw, week),
                                 slow=slow, returns=load_returns(returns_path(repo, season)), config=config)
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
    # The clock is a parameter so a build is reproducible.
    started: datetime | None = None,
    *,
    config: LeagueConfig,
    # The loader is a seam: a test passes a counted one to prove the raw week loads once per build.
    raw_loader: RawLoader = load_raw,
    # The provider is a seam too. The config gives it the league id and the timezone of the fetch.
    provider: Provider = SLEEPER,
    # The writer of the research call when `research` is None. A writer of None is the one ClaudeWriter of the process.
    writer: Writer | None = None,
) -> Path:
    directory = week_dir(repo, season, week)
    raw_path = raw_dir(repo, season, week)
    # A rebuild keeps the first window, also after a refetch, so a trade never moves to another page.
    saved = directory / "verify.json"
    first_fetch = _first_build(saved)
    # The page and the season files read this one load of the raw week.
    # A fetch gives back the week it saved, so a fetched week loads once too.
    if fetch:
        raw = provider.fetch_week(config.league_id(season), season, week, raw_path, players_cache(repo), config.tz,
                                  config.last_regular_week, config.last_season_week)
    elif not has_raw(repo, season, week):
        raise BuildStopped(f"No raw data for week {week}. Run without --no-fetch.")
    else:
        raw = raw_loader(raw_path)
    # No argument means the real fetch. A test passes a fixture-backed one.
    bundle, record = make_bundle(
        repo, season, week, news, started=started, fetched=first_fetch.fetched if first_fetch else None,
        nflverse=nflverse or fetch_nflverse(repo), config=config, raw=raw)
    # The research runs once here, after the engine. The claims save with the facts, so a rewrite reads them.
    # No argument means the real search through `writer`. A test passes a fake search or a fake writer.
    if bundle.waiver is not None:
        search = research or partial(search_call, writer=writer)
        bundle.waiver = research_board(bundle.waiver, search, config.prompts_dir)
    write_bundle(bundle, directory / "facts.json")

    blurbs: dict[str, Blurb] = {}
    verify: dict[str, list[VerifyResult]] = {}
    # "lucky" and "unlucky" each appear at most once per page, so each chapter gets the words that earlier chapters
    # used and the award words it does not own.
    used: set[str] = set()
    for chapter in bundle.sheet.chapters:
        reserved = reserved_words(chapter.key, bundle.sheet)
        blurbs[chapter.key], verify[chapter.key] = write_and_verify(
            chapter, bundle.sheet, call, used | reserved, prompts_dir=config.prompts_dir)
        used |= page_words(blurbs[chapter.key], chapter)
        _log_chapter(chapter.key, blurbs[chapter.key])
    _save_blurbs(directory, blurbs, VerifyFile(build=record, chapters=verify))

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    # The page is built by now, so a history problem only logs a warning.
    try:
        save_week_to_history(raw_path, history_dir(repo, season, week))
    except (OSError, ValueError, KeyError) as err:
        log.warning("week %d not saved to history: %s", week, err)
    # The season file reads the saved history, so it comes after the save. A missing past week never blocks the page.
    # Both season files read the one history load, so a failed load skips both files.
    try:
        history = _season_history(repo, season, week)
    except (OSError, ValueError, KeyError) as err:
        log.warning("rankings.json not written for week %d: %s", week, err)
        log.warning("managers.json not written for week %d: %s", week, err)
        return page
    try:
        rankings = _write_rankings(repo, season, week, bundle.data.teams, SeasonInputs(history=history),
                                   blurbs.get(RANKINGS_CHAPTER), bundle.odds)
        if rankings is None:
            log.warning("history incomplete through week %d: rankings.json not written", week)
    except (OSError, ValueError, KeyError) as err:
        log.warning("rankings.json not written for week %d: %s", week, err)
    # The managers file reads the same saved history, so it comes right after the rankings file.
    # The snapshot, the projections ahead, and the chart load inside this try, so their failure skips only this file.
    try:
        _write_managers(repo, season, week, bundle.data.teams,
                        _season_inputs(repo, season, week, raw, history, config))
    except (OSError, ValueError, KeyError) as err:
        log.warning("managers.json not written for week %d: %s", week, err)
    return page


def _season_history(repo: Path, season: int, week: int) -> History:
    """The saved history of weeks 1 to the latest saved week, never less than `week`. It can have a gap."""
    root = history_root(repo, season)
    # The file holds every week to date. A rebuild of an older week must not cut the later weeks from it.
    through = saved_through(root, week)
    return History(week=through, weeks=load_saved_weeks(root, through))


def _season_inputs(
        repo: Path, season: int, week: int, raw: dict | None, history: History, config: LeagueConfig) -> SeasonInputs:
    """The inputs of the season files, from one load of the `raw` week and the saved `history`. None for `raw` means
    the week has no raw data, so the managers file goes out with no grade."""
    raw_path = raw_dir(repo, season, week)
    return SeasonInputs(
        history=history, snapshot=_managers_snapshot(repo, season, week, raw, config),
        projections_ahead=_projections_ahead(raw_path), chart=_managers_chart(repo, week, raw),
    )


def _write_rankings(
    repo: Path, season: int, week: int, teams: dict[int, Team], inputs: SeasonInputs, blurb: Blurb | None = None,
    odds: OddsResult | None = None,
) -> Path | None:
    """Write rankings.json from the history of the `inputs`: weeks 1 to the latest complete week, never less than
    `week`. The rankings blurb and the `odds` go into the rows of `week`. None when a week from 1 to `week` is
    missing."""
    # A fallback blurb has no roster tags, so it would write an empty blurb for every team. With no blurb, the
    # week keeps the blurbs of the last file.
    if blurb is not None and blurb.fallback:
        blurb = None
    history = inputs.history
    # A gap would shift every rank after it, so the file waits for a complete history.
    if not history.complete():
        return None
    if history.week > week:
        log.info("rankings.json covers weeks 1 to %d, past the built week %d", history.week, week)
    return render_rankings(history, season, teams, repo / "site", week, blurb, odds)


def _write_managers(
    repo: Path, season: int, week: int, teams: dict[int, Team], inputs: SeasonInputs,
) -> Path | None:
    """Write managers.json from the history of the `inputs`: weeks 1 to the latest complete week, never less than
    `week`. None, with one log line, when a week from 1 to `week` is missing or the history is under two weeks."""
    # The same history as the rankings file, so the record of an entry matches the record of its rankings row.
    through = inputs.history.week
    if not inputs.history.complete():
        log.warning("history incomplete through week %d: managers.json not written", week)
        return None
    if through < MANAGERS_MIN_WEEKS:
        log.info(
            "history holds %d of the %d weeks the file needs: managers.json not written", through, MANAGERS_MIN_WEEKS,
        )
        return None
    raw_path = raw_dir(repo, season, week)
    slots, players = _season_raw(raw_path)
    week_awards = saved_awards({n: week_dir(repo, season, n) / "facts.json" for n in range(1, through + 1)})
    return render_managers(
        inputs, season, teams, repo / "site", players=players, roster_slots=slots, week_awards=week_awards,
    )


def _managers_chart(repo: Path, week: int, raw: dict | None) -> ChartValues | None:
    """The trade values of the saved chart read of the week for the roster grade. None, with one log line, when no
    read is saved or the week has no raw data. It never fetches or reads an image."""
    chart = saved_chart_read(repo, week) if raw is not None else None
    if chart is None:
        # The grade still goes out. Its trade value part is 0 for every roster.
        log.info("no saved chart read for week %d: the roster grade has no trade value", week)
        return None
    return match_chart(chart, week_lines(parse_week(raw)))


def _projections_ahead(raw_path: Path) -> ProjectionsAhead | None:
    """The projections ahead of the roster grade, by week and player id, from the raw projections ahead file.
    No file gives None, so the entries carry no grade."""
    path = raw_path / PROJECTIONS_AHEAD_FILE
    if not path.exists():
        return None
    return {entry["week"]: entry["projections"] for entry in json.loads(path.read_text(encoding="utf-8"))}


def _season_raw(raw_path: Path) -> tuple[list[str] | None, dict[str, dict] | None]:
    """The roster slots and the players of the managers file, from the raw league and players files.
    The roster slots do not change in a season, so the raw files of the built week serve every saved week.
    No league file gives no slots, so the entries carry no bench points. No players file reads ids."""
    league, players = raw_path / "league.json", raw_path / "players.json"
    slots = json.loads(league.read_text(encoding="utf-8"))["roster_positions"] if league.exists() else None
    entries = json.loads(players.read_text(encoding="utf-8")) if players.exists() else None
    return slots, entries


def _managers_snapshot(
        repo: Path, season: int, week: int, raw: dict | None, config: LeagueConfig) -> Snapshot | None:
    """The analyzer's snapshot of the week for the roster grade. None, with one log line, when the week has no raw
    data."""
    # A saved week can lack its raw data. The file then goes out with no grade, so the page still ships.
    if raw is None:
        log.info("no raw data for week %d: managers.json has no roster grade", week)
        return None
    return week_snapshot(raw, history_root(repo, season), week, config=config)


def _raw_for_season_files(repo: Path, season: int, week: int) -> dict | None:
    """The raw week of a saved week, or None when the week has no raw data."""
    raw_path = raw_dir(repo, season, week)
    return load_raw(raw_path) if raw_path.exists() else None


def _load_saved_week(repo: Path, season: int, week: int) -> tuple[Bundle, dict[str, Blurb]]:
    """Read the saved facts and blurbs of a week."""
    directory = week_dir(repo, season, week)
    bundle = read_bundle(directory / "facts.json")
    blurbs = _BLURBS.validate_json((directory / "blurbs.json").read_text(encoding="utf-8"))
    return bundle, blurbs


def _other_page_words(bundle: Bundle, blurbs: dict[str, Blurb], key: str) -> set[str]:
    """The once-per-page words that the saved blurbs of the other chapters say, so a rewrite cannot add a second one."""
    chapters = {c.key: c for c in bundle.sheet.chapters}
    said = {word for k, b in blurbs.items() if k != key for word in page_words(b, chapters.get(k))}
    return said | reserved_words(key, bundle.sheet)


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
    *,
    config: LeagueConfig,
) -> Path:
    # The news, nflverse, and research arguments keep the signature the same as run_build.
    # A rewrite reads the saved facts and the saved claims, so it needs no news, no fetch, and no search.
    # The config gives the prompts folder to the writer and the verifier, as in run_build and run_rankings.
    directory = week_dir(repo, season, week)
    bundle, blurbs = _load_saved_week(repo, season, week)
    chosen = next((c for c in bundle.sheet.chapters if c.key == chapter), None)
    if chosen is None:
        keys = ", ".join(c.key for c in bundle.sheet.chapters)
        raise ValueError(f"Unknown chapter '{chapter}'. Valid chapters: {keys}")

    verify = read_verify(directory / "verify.json")
    used = _other_page_words(bundle, blurbs, chapter)
    blurbs[chapter], verify.chapters[chapter] = write_and_verify(
        chosen, bundle.sheet, call, used, prompts_dir=config.prompts_dir)
    _log_chapter(chapter, blurbs[chapter])
    _save_blurbs(directory, blurbs, verify)

    site_dir = repo / "site"
    page = render_week(bundle, blurbs, site_dir, fetch_bytes)
    # The season file holds the rankings blurb, so a rewrite of the chapter must reach the file too.
    if chapter == RANKINGS_CHAPTER:
        try:
            # The rankings file reads only the history, so a rewrite loads no raw week.
            inputs = SeasonInputs(history=_season_history(repo, season, week))
            if _write_rankings(repo, season, week, bundle.data.teams, inputs, blurbs[chapter], bundle.odds) is None:
                log.warning("history incomplete through week %d: rankings.json not written", week)
        except (OSError, ValueError, KeyError) as err:
            log.warning("rankings.json not written for week %d: %s", week, err)
    return page


def run_page_json(repo: Path, season: int, week: int) -> Path:
    """Write page.json for a saved week from its facts and blurbs. It calls no writer and no network."""
    bundle, blurbs = _load_saved_week(repo, season, week)
    return render_page_json(bundle, blurbs, repo / "site")


def _rankings_chapter(bundle: Bundle, history: History, config: LeagueConfig) -> Chapter:
    """The rankings chapter of a saved week, built from the history and the current rules.

    The PR facts and the rank why facts derive from the history and the rules, never from the saved facts.
    A rule change must reach the blurb, so the rows of rankings.json and the facts agree on every rank.
    Week 1 of the rankings has no rank why. The odds why comes only from the saved facts, never from the raw week.
    """
    rows = power_rankings(history, history.week)[history.week]

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
    built = rankings_chapter(bundle.sheet.facts, rows, team, bundle.data.table, bundle.odds, config=config)
    bundle.sheet.chapters = [c for c in bundle.sheet.chapters if c.key != RANKINGS_CHAPTER] + [built]
    return built


def run_rankings(repo: Path, season: int, week: int, call: ClaudeCall, *, config: LeagueConfig) -> Path:
    """Write the rankings blurb of a saved week with one writer call, then rankings.json from the saved history.
    The writer runs for this week only. The other weeks keep the blurbs of the last file."""
    directory = week_dir(repo, season, week)
    bundle, blurbs = _load_saved_week(repo, season, week)
    history = History(week=week, weeks=load_saved_weeks(history_root(repo, season), week))
    # The check comes before the writer call, so a missing week costs no Claude call.
    if not history.complete():
        raise BuildStopped(HISTORY_GAP.format(week=week))
    chapter = _rankings_chapter(bundle, history, config)
    # The saved facts must hold the PR facts the blurb cites, so a later rewrite finds them.
    write_bundle(bundle, directory / "facts.json")
    verify = read_verify(directory / "verify.json")
    used = _other_page_words(bundle, blurbs, chapter.key)
    blurbs[chapter.key], verify.chapters[chapter.key] = write_and_verify(
        chapter, bundle.sheet, call, used, prompts_dir=config.prompts_dir)
    _log_chapter(chapter.key, blurbs[chapter.key])
    _save_blurbs(directory, blurbs, verify)
    season_history = _season_history(repo, season, week)
    out = _write_rankings(repo, season, week, bundle.data.teams, SeasonInputs(history=season_history),
                          blurbs[chapter.key], bundle.odds)
    if out is None:
        raise BuildStopped(HISTORY_GAP.format(week=week))
    # The command rebuilds the season files from the saved history, so the managers file comes along.
    # A thin history only logs: the rankings file is the output of the command.
    # The raw week loads after the rankings file, so a failed load of the grade inputs leaves that file written.
    inputs = _season_inputs(repo, season, week, _raw_for_season_files(repo, season, week), season_history, config)
    _write_managers(repo, season, week, bundle.data.teams, inputs)
    return out


def run_history(repo: Path, season: int, through: int, force: bool = False, *, config: LeagueConfig) -> list[int]:
    return fetch_history(config.league_id(season), season, through, history_root(repo, season), force=force)


def preview(page: Path) -> None:
    """Show a notification that the week is built. A missing tool only logs a warning."""
    week = str(week_from_label(page.parent.name))
    script = f'display notification "Week {week} is ready to review" with title "Cornerstone Weekly"'
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except OSError as err:
        log.warning("preview step osascript failed: %s", err)
