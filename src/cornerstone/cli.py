"""
Command line entry point for Cornerstone Weekly.
It defines the build, publish, rewrite, page-json, history, chart, and analyze
subcommands.
"""
import argparse
import logging
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path

import httpx
from pydantic import ValidationError

from cornerstone.adjusters import STEP_WORDS
from cornerstone.analysis import Analysis, analyze
from cornerstone.chart import chart_values, check_chart, match_chart, saved_chart_read
from cornerstone.history import history_root
from cornerstone.live import live_snapshot
from cornerstone.models import ChartValues, PlayerLine, week_lines
from cornerstone.parse import parse_trades, parse_week
from cornerstone.pipeline import (
    BuildStopped, has_raw, nflverse_cache_dir, preview, resolve_week, run_build, run_history, run_page_json,
    run_rewrite, week_dir,
)
from cornerstone.sleeper import fetch_state, load_raw
from cornerstone.publish import PublishError, run_publish, site_page_url
from cornerstone.rubric import ProposedTrade, TradeSide, grade, verdict
from cornerstone.slow_sources import load_slow_sources
from cornerstone.snapshot import Snapshot, load_snapshot
from cornerstone.trades import EASTERN
from cornerstone.writer import analyzer_call, claude_call


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cornerstone", description="Build the weekly Cornerstone report.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="build the report for a week")
    build.add_argument("--week", type=int)
    build.add_argument("--season", type=int)
    build.add_argument("--no-fetch", action="store_true", help="read the saved raw data")
    build.add_argument("--refetch", action="store_true", help="fetch even when raw data is saved")

    publish = sub.add_parser("publish", help="publish the built report")
    publish.add_argument("--week", type=int)
    publish.add_argument("--season", type=int)

    rewrite = sub.add_parser("rewrite", help="rewrite one chapter of the report")
    rewrite.add_argument("--week", type=int)
    rewrite.add_argument("--season", type=int)
    rewrite.add_argument("--chapter", type=str, required=True)

    page_json = sub.add_parser("page-json", help="write page.json for a saved week")
    page_json.add_argument("--week", type=int)
    page_json.add_argument("--season", type=int)

    history = sub.add_parser("history", help="fetch and cache past weeks")
    history.add_argument("--season", type=int)
    history.add_argument("--through", type=int, required=True)
    history.add_argument("--force", action="store_true", help="fetch even when a week is saved")

    chart = sub.add_parser("chart", help="fetch, read, and match the trade value chart of a week")
    chart.add_argument("--week", type=int)
    chart.add_argument("--season", type=int)

    analyze = sub.add_parser(
        "analyze", help="grade a proposed trade from the league now, or from the saved data of a week",
        description="Grade a proposed trade from a snapshot. Without --week, the command fetches the league "
                    "from Sleeper now. With --week, it reads the saved data of that week. "
                    "Give --side twice, once for each roster, as ROSTER:PLAYER,PLAYER. "
                    "Example: --side 4:7569 --side 12:10236,8146 --asker 4 --no-claude")
    analyze.add_argument("--season", type=int, required=True)
    analyze.add_argument("--week", type=int,
                         help="read the saved data of this week; without it, fetch the league now")
    analyze.add_argument("--side", type=_trade_side, action="append", required=True, metavar="ROSTER:PLAYERS",
                         help="a roster id and the comma-separated player ids it gives; give it twice")
    analyze.add_argument("--asker", type=int, required=True, help="the roster id of the side that asked")
    analyze.add_argument("--chart", type=Path,
                         help="a trade values JSON file; the default is the chart of the trade window week")
    analyze.add_argument("--no-claude", action="store_true", help="skip the Claude call and print the breakdown only")

    return parser


def _trade_side(text: str) -> TradeSide:
    """One --side value, ROSTER:PLAYER,PLAYER, as a trade side."""
    roster, _, players = text.partition(":")
    gives = [pid.strip() for pid in players.split(",") if pid.strip()]
    if not roster.strip().isdigit() or not gives:
        raise argparse.ArgumentTypeError(f"{text!r} is not ROSTER:PLAYER,PLAYER")
    return TradeSide(roster_id=int(roster), gives=gives)


def _saved_chart_values(repo: Path, week: int, raw: dict) -> ChartValues | None:
    """The trade values of the saved chart read of the week, or None. It never fetches or reads an image."""
    # The chart module owns the rules for a saved read, so a bad or stale one gives None here too.
    chart = saved_chart_read(repo, week)
    if chart is None:
        return None
    return match_chart(chart, week_lines(parse_week(raw)))


def _given_chart(path: Path) -> ChartValues:
    """The trade values in a --chart JSON file."""
    return ChartValues.model_validate_json(path.read_text(encoding="utf-8"))


def _names(snapshot: Snapshot, pids: list[str]) -> str:
    return ", ".join(snapshot.players[pid].name if pid in snapshot.players else pid for pid in pids)


# The plain name of each slow source that the as-of line shows, in print order.
_SOURCE_NAMES = {
    "schedules": "schedules", "depth_charts": "depth charts", "points_allowed": "points allowed", "id_map": "id map",
}


def _sources_line(snapshot: Snapshot) -> str:
    """One line that names the slow sources the grade has, or the ones it lacks."""
    missing = [name for key, name in _SOURCE_NAMES.items() if key in snapshot.missing]
    if not missing:
        return "Sources: schedules, depth charts, points allowed."
    return f"Sources missing: {', '.join(missing)}."


def _saved_snapshot(repo: Path, args: argparse.Namespace) -> Snapshot | None:
    """The snapshot of the saved week, or None after a plain line when the week has no raw data."""
    if not has_raw(repo, args.season, args.week):
        print(f"No raw data is saved for week {args.week} of {args.season}. Build the week first.")
        return None
    raw_dir = week_dir(repo, args.season, args.week) / "raw"
    if args.chart is not None:
        chart = _given_chart(args.chart)
    else:
        chart = _saved_chart_values(repo, args.week, load_raw(raw_dir))
    history = history_root(repo, args.season)
    # A saved week never fetches. A cache that the build did not fill gives missing sources.
    slow = load_slow_sources(nflverse_cache_dir(repo), args.season, args.week, history)
    return load_snapshot(raw_dir, history, chart, slow)


def _live_snapshot(repo: Path, args: argparse.Namespace) -> Snapshot | None:
    """The snapshot of the league now. A given --chart file stands in for the chart read."""
    read_chart = chart_values
    if args.chart is not None:
        given = _given_chart(args.chart)

        # A given file is the chart of the trade, so the reader needs neither the week nor the lines.
        def read_chart(repo: Path, season_start: date, week: int, lines: Iterable[PlayerLine]) -> ChartValues:
            return given
    try:
        return live_snapshot(repo, args.season, now=datetime.now(EASTERN), read_chart=read_chart)
    except ValueError as err:
        print(err)
        return None


def run_analyze(repo: Path, args: argparse.Namespace) -> int:
    """Grade the proposed trade from the live or saved snapshot. Print the breakdown of each side and the verdict.

    Without --no-claude, it also prints Claude's final letter and analysis per side, and Claude's verdict.
    """
    if len(args.side) != 2:
        print("Give --side exactly twice, once for each roster.")
        return 2
    snapshot = _live_snapshot(repo, args) if args.week is None else _saved_snapshot(repo, args)
    if snapshot is None:
        return 2
    try:
        trade = ProposedTrade(season=args.season, sides=tuple(args.side), asker=args.asker)
    except ValidationError as err:
        # One plain line per broken rule, with no pydantic text and no echo of the input.
        for error in err.errors():
            print(error["msg"].removeprefix("Value error, "))
        return 2
    # The Claude call grades the trade itself, so the breakdown and the analysis come from one grade.
    analysis: Analysis | None = None
    if args.no_claude:
        result = grade(trade, snapshot)
        choice = verdict(trade, result)
    else:
        analysis = analyze(trade, snapshot, call=analyzer_call)
        result, choice = analysis.breakdowns, analysis.code_verdict
    stamps = snapshot.as_of
    chart_text = f"Chart week {stamps.chart_week}" if stamps.chart_week is not None else "No chart"
    fetched = stamps.rosters_fetched.isoformat(timespec="minutes") if stamps.rosters_fetched else "unknown"
    print(f"Week {snapshot.week} of {snapshot.season}. {chart_text}. Stats through week {stamps.stats_through}. "
          f"Rosters fetched {fetched}.")
    print(_sources_line(snapshot))
    if snapshot.stale:
        print(f"Refresh failed, so the cache is old or absent: {', '.join(snapshot.stale)}.")
    for index, (side, other, breakdown) in enumerate(
            ((trade.sides[0], trade.sides[1], result[0]), (trade.sides[1], trade.sides[0], result[1]))):
        asked = " (asked)" if side.roster_id == trade.asker else ""
        print()
        print(f"{snapshot.teams[side.roster_id].name}{asked}")
        print(f"  Gives: {_names(snapshot, side.gives)}")
        print(f"  Gets: {_names(snapshot, other.gives)}")
        print(f"  Start letter: {breakdown.start_letter}")
        print(f"  Reason: {breakdown.reason}")
        for adjuster in breakdown.adjusters:
            # The schedule never moves a letter, so its line shows the lean in place of a step.
            words = adjuster.lean if adjuster.lean is not None else STEP_WORDS[adjuster.step]
            print(f"  {adjuster.name.capitalize()}: {words}. {adjuster.reason}")
        if analysis is None:
            print(f"  Final letter: {breakdown.final_letter}")
            continue
        # Claude's letter can differ from the rubric's by one step, so both print, each under its own label.
        final = analysis.sides[index]
        print(f"  Rubric letter: {breakdown.final_letter}")
        print(f"  Final letter: {final.final_letter}" + (f". Reason: {final.reason}" if final.reason else ""))
        print(f"  Analysis: {final.analysis}")
    print()
    if analysis is not None:
        if analysis.fallback:
            print("The Claude call failed twice, so the rubric's letters and verdict stand.")
        choice = analysis.verdict
    flag = " (differs from the rubric's default)" if analysis is not None and analysis.verdict_differs else ""
    print(f"Verdict for {snapshot.teams[trade.asker].name}: {choice.choice}. {choice.reason}{flag}")
    return 0


def run_chart(repo: Path, season: int, week: int) -> int:
    """Print the parsed chart, every guard, and the match against the saved raw data of the week."""
    raw = load_raw(week_dir(repo, season, week) / "raw") if has_raw(repo, season, week) else None
    if raw is not None:
        league = parse_week(raw)
        season_start = league.season_start
    else:
        # Sleeper state, as in resolve_week, gives the start date of the season in progress only.
        state = fetch_state()
        if int(state["season"]) != season:
            print(f"No raw data is saved for week {week} of {season}. Build the week first.")
            return 2
        season_start = date.fromisoformat(state["season_start_date"])
    check = check_chart(repo, season_start, week)
    if check is None:
        print(f"Week {week} has no chart. The log says why.")
        return 1
    print(f"Chart week {check.week}, dated {check.chart.date}")
    for row in check.chart.rows:
        print(f"{row.value}  {row.name}  {row.position}")
    # A saved read passed the guards before the save. A second print of them lets a person see each one.
    for name, ok in check.guards.items():
        print(f"{name}: {'pass' if ok else 'FAIL'}")
    if not all(check.guards.values()):
        print("A guard failed, so no trade values were made.")
        return 1
    if raw is None:
        print(f"No raw data for week {week}, so no player match.")
        return 0
    lines = {l.player_id: l for l in week_lines(league)}
    values = match_chart(check.chart, lines.values()).values
    print(f"Matched {len(values)} of {len(check.chart.rows)} chart rows")
    traded = {pid for t in parse_trades(raw["transactions"]) for pid in t.adds}
    unmatched = sorted(lines[pid].name if pid in lines else pid for pid in traded - values.keys())
    if unmatched:
        print("Unmatched traded players: " + ", ".join(unmatched))
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    repo = Path.cwd()
    if not (repo / "pyproject.toml").exists():
        print("Run cornerstone from the repo root. No pyproject.toml in the current directory.")
        return 2
    try:
        if args.command == "history":
            # History has no --week, so it skips resolve_week.
            season = args.season if args.season is not None else int(fetch_state()["season"])
            weeks = run_history(repo, season, args.through, force=args.force)
            print(("Fetched weeks: " + ", ".join(str(w) for w in weeks)) if weeks else "Nothing to fetch")
            return 0
        if args.command == "analyze":
            # Analyze skips resolve_week. Without --week it reads Sleeper itself, and with --week it reads disk.
            return run_analyze(repo, args)
        # resolve_week can call Sleeper, so a network failure gets the same plain exit.
        season, week = resolve_week(args.season, args.week)
        if args.command == "build":
            # A named week with saved raw data rebuilds from disk, so a rebuild sees the same data.
            fetch = not args.no_fetch and (
                args.refetch or args.week is None or not has_raw(repo, season, week)
            )
            page = run_build(repo, season, week, claude_call, fetch=fetch)
            print(page)
            print(f"Site page after publish: {site_page_url(season, week)}")
            preview(page)
        elif args.command == "chart":
            return run_chart(repo, season, week)
        elif args.command == "page-json":
            print(run_page_json(repo, season, week))
        elif args.command == "rewrite":
            page = run_rewrite(repo, season, week, args.chapter, claude_call)
            print(page)
            print(f"Site page after publish: {site_page_url(season, week)}")
            preview(page)
        else:
            answer = input(f"Publish week {week} to GitHub Pages? [y/N] ")
            if answer not in ("y", "Y"):
                print("Not published.")
                return 0
            print(run_publish(repo, season, week))
    except (BuildStopped, PublishError, ValueError) as err:
        print(err)
        return 2
    except httpx.HTTPError as err:
        print(f"Sleeper request failed: {err}")
        return 2
    except FileNotFoundError as err:
        # On build, a missing file means the saved raw data is incomplete, not an unbuilt week.
        name = f" {err.filename}" if err.filename else ""
        hint = "Run the build with --refetch." if args.command == "build" else "Build the week first."
        print(f"Missing file{name}. {hint}")
        return 2
    return 0
