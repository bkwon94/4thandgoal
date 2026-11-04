"""
Command line entry point for Cornerstone Weekly.
It defines the build, publish, rewrite, page-json, rankings, history, chart, analyze, and find
subcommands.
"""
import argparse
import logging
from collections.abc import Callable, Iterable
from datetime import date, datetime
from functools import partial
from pathlib import Path

import httpx
from pydantic import ValidationError

from analyzer.adjusters import STEP_WORDS
from analyzer.analysis import Analysis, analyze
from analyzer.finder import NO_WIN_WIN, find_win_wins
from analyzer.rubric import (
    MAX_SIDES,
    MIN_SIDES,
    Fairness,
    GivenPlayer,
    ProposedTrade,
    TradeSide,
    fairness,
    grade,
    verdict,
)
from cornerstone.pipeline import (
    BuildStopped,
    has_raw,
    preview,
    resolve_week,
    run_build,
    run_history,
    run_page_json,
    run_rankings,
    run_rewrite,
)
from cornerstone.publish import PublishError, run_publish, site_page_url
from facts.writer import analyzer_call, claude_call, parse_call
from league.chart import chart_values, check_chart, claude_reader, match_chart, saved_chart_read
from league.claude_port import Writer
from league.client import CLIENT_FILE, Client, ClientError, check_schema_file, load_client, read_client_values
from league.live import live_snapshot
from league.models import ChartValues, PlayerLine, week_lines
from league.parse import parse_trades, parse_week
from league.paths import history_root, nfl_dir, nflverse_cache_dir, provider_cache_dir, raw_dir
from league.provider.base import Provider
from league.provider.raw import RawState, RawWeek
from league.provider.sleeper import SleeperProvider, fetch_state, load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import Snapshot, load_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cornerstone", description="Build the weekly Cornerstone report.")
    sub = parser.add_subparsers(dest="command", required=True)
    # Each command that reads a league names its client. The check in main gives the plain line when it is absent.
    named = argparse.ArgumentParser(add_help=False)
    named.add_argument("--client", help="the client slug, the name of its folder under clients/")

    build = sub.add_parser("build", parents=[named], help="build the report for a week")
    build.add_argument("--week", type=int)
    build.add_argument("--season", type=int)
    build.add_argument("--no-fetch", action="store_true", help="read the saved raw data")
    build.add_argument("--refetch", action="store_true", help="fetch even when raw data is saved")

    publish = sub.add_parser("publish", parents=[named], help="publish the built report")
    publish.add_argument("--week", type=int)
    publish.add_argument("--season", type=int)

    rewrite = sub.add_parser("rewrite", parents=[named], help="rewrite one chapter of the report")
    rewrite.add_argument("--week", type=int)
    rewrite.add_argument("--season", type=int)
    rewrite.add_argument("--chapter", type=str, required=True)

    page_json = sub.add_parser("page-json", parents=[named], help="write page.json for a saved week")
    page_json.add_argument("--week", type=int)
    page_json.add_argument("--season", type=int)

    rankings = sub.add_parser("rankings", parents=[named], help="write the rankings blurb and rankings.json for a saved week")
    rankings.add_argument("--week", type=int)
    rankings.add_argument("--season", type=int)

    history = sub.add_parser("history", parents=[named], help="fetch and cache past weeks")
    history.add_argument("--season", type=int)
    history.add_argument("--through", type=int, required=True)
    history.add_argument("--force", action="store_true", help="fetch even when a week is saved")

    chart = sub.add_parser("chart", parents=[named], help="fetch, read, and match the trade value chart of a week")
    chart.add_argument("--week", type=int)
    chart.add_argument("--season", type=int)

    analyze = sub.add_parser(
        "analyze", parents=[named], help="grade a proposed trade from the league now, or from the saved data of a week",
        description="Grade a proposed trade from a snapshot. Without --week, the command fetches the league "
                    "from Sleeper now. With --week, it reads the saved data of that week. "
                    "Give --side two to four times, once for each roster, as ROSTER:PLAYER@TO,PLAYER@TO, where TO "
                    "is the roster that gets the player. A two-side trade may leave out @TO. "
                    "Example: --side 4:7569@12 --side 12:10236@7 --side 7:11628@4 --asker 4 --no-claude")
    analyze.add_argument("--season", type=int, required=True)
    analyze.add_argument("--week", type=int,
                         help="read the saved data of this week; without it, fetch the league now")
    analyze.add_argument("--side", type=_trade_side, action="append", required=True,
                         metavar="ROSTER:PLAYER@TO,PLAYER@TO",
                         help="a roster id and the comma-separated player ids it gives, each with the roster id "
                              "that gets him; give it two to four times")
    analyze.add_argument("--asker", type=int, required=True, help="the roster id of the side that asked")
    analyze.add_argument("--chart", type=Path,
                         help="a trade values JSON file; the default is the chart of the trade window week")
    analyze.add_argument("--no-claude", action="store_true", help="skip the Claude call and print the breakdown only")

    # The finder loads its snapshot the way analyze does, so it takes the same --week and --chart.
    find = sub.add_parser(
        "find", parents=[named], help="list the top trades between two rosters that are good for both",
        description="Grade every one-for-one and two-for-one swap between two rosters and print the top three "
                    "that are good for both. Without --week, the command fetches the league from Sleeper now. "
                    "With --week, it reads the saved data of that week. It makes no Claude call. "
                    "Example: --week 6 --asker 4 --partner 5")
    find.add_argument("--season", type=int, required=True)
    find.add_argument("--week", type=int, help="read the saved data of this week; without it, fetch the league now")
    find.add_argument("--asker", type=int, required=True, help="the roster id of the side that asks")
    find.add_argument("--partner", type=int, required=True, help="the roster id of the partner team")
    find.add_argument("--chart", type=Path,
                      help="a trade values JSON file; the default is the chart of the trade window week")

    settings = sub.add_parser("settings", parents=[named], help="print the League settings and the sizes of a season")
    settings.add_argument("--season", type=int)

    check = sub.add_parser("check-client", help="check the client.toml of a client folder and the exported schema")
    check.add_argument("folder", type=Path, help="the client folder, such as ../../clients/cpc")

    return parser


def _trade_side(text: str) -> tuple[int, list[tuple[str, int | None]]]:
    """One --side value, ROSTER:PLAYER@TO,PLAYER@TO, as the roster id and each player it gives with his destination.

    The destination is None when the value leaves out @TO, which only a two-side trade allows.
    """
    # "@" needs no quotes in a shell, where ">" would redirect the output.
    roster, _, players = text.partition(":")
    gives = []
    for entry in (item.strip() for item in players.split(",") if item.strip()):
        pid, at, to = entry.partition("@")
        if not pid or (at and not to.strip().isdigit()):
            raise argparse.ArgumentTypeError(f"{text!r} is not ROSTER:PLAYER@TO,PLAYER@TO")
        gives.append((pid.strip(), int(to) if at else None))
    if not roster.strip().isdigit() or not gives:
        raise argparse.ArgumentTypeError(f"{text!r} is not ROSTER:PLAYER@TO,PLAYER@TO")
    return int(roster), gives


def _proposed_sides(sides: list[tuple[int, list[tuple[str, int | None]]]]) -> list[TradeSide] | None:
    """The trade sides of the --side values, or None when a player in a trade of three or more has no destination."""
    rosters = [roster for roster, _ in sides]
    built = []
    for index, (roster, gives) in enumerate(sides):
        # A two-side trade may leave out `@TO`, because the other side is the destination.
        default = rosters[1 - index] if len(rosters) == 2 else None
        if any(to is None for _, to in gives) and default is None:
            return None
        built.append(TradeSide(roster_id=roster, gives=[GivenPlayer(player_id=pid, to=default if to is None else to)
                                                        for pid, to in gives]))
    return built


def _saved_chart_values(nfl: Path, week: int, raw: RawWeek) -> ChartValues | None:
    """The trade values of the saved chart read of the week, or None. It never fetches or reads an image."""
    # The chart module owns the rules for a saved read, so a bad or stale one gives None here too.
    chart = saved_chart_read(nfl, week)
    if chart is None:
        return None
    return match_chart(chart, week_lines(parse_week(raw)))


def _given_chart(path: Path) -> ChartValues:
    """The trade values in a --chart JSON file."""
    return ChartValues.model_validate_json(path.read_text(encoding="utf-8"))


def _names(snapshot: Snapshot, pids: list[str]) -> str:
    return ", ".join(snapshot.players[pid].name if pid in snapshot.players else pid for pid in pids)


def _routed(snapshot: Snapshot, trade: ProposedTrade, roster_id: int, gives: bool) -> str:
    """The players a side gives, each with the team he goes to, or the players it gets, each with his source team."""
    givers = trade.givers
    if gives:
        side = next(side for side in trade.sides if side.roster_id == roster_id)
        pairs = [(player.player_id, f"to {snapshot.teams[player.to].name}") for player in side.gives]
    else:
        pairs = [(pid, f"from {snapshot.teams[givers[pid]].name}") for pid in trade.gets(roster_id)]
    return ", ".join(f"{_names(snapshot, [pid])} {where}" for pid, where in pairs)


# The plain name of each slow source that the as-of line shows, by its key in Snapshot.missing, in print order.
# The refreshed nflverse files use the names of REFRESHED_SOURCES. A cli test fails when the two lists differ.
_SOURCE_NAMES = {
    "schedules": "schedules", "depth_charts": "depth charts", "points_allowed": "points allowed", "id_map": "id map",
    "injuries": "injuries", "expected_points": "expected points", "player_weeks": "player weeks",
}
# The id map only joins the ids of the other files. So the line names it only when it is missing.
_JOIN_ONLY = "id_map"


def _sources_line(snapshot: Snapshot) -> str:
    """One line that names the slow sources the grade has, or the ones it lacks."""
    missing = [name for key, name in _SOURCE_NAMES.items() if key in snapshot.missing]
    if not missing:
        present = [name for key, name in _SOURCE_NAMES.items() if key != _JOIN_ONLY]
        return f"Sources: {', '.join(present)}."
    return f"Sources missing: {', '.join(missing)}."


def _saved_snapshot(args: argparse.Namespace, client: Client) -> Snapshot | None:
    """The snapshot of the saved week, or None after a plain line when the week has no raw data."""
    if not has_raw(client.folder, args.season, args.week):
        print(f"No raw data is saved for week {args.week} of {args.season}. Build the week first.")
        return None
    raw_path = raw_dir(client.folder, args.season, args.week)
    raw = load_raw(raw_path)
    if args.chart is not None:
        chart = _given_chart(args.chart)
    else:
        # A client with no chart reads no saved chart read either: each of its chart values is 0.
        chart = _saved_chart_values(client.nfl_dir, args.week, raw) if client.chart is not None else None
    history = history_root(client.folder, args.season)
    # A saved week never fetches. A cache that the build did not fill gives missing sources.
    slow = load_slow_sources(nflverse_cache_dir(client.nfl_dir), args.season, args.week, history,
                             raw.league.scoring_settings, client.settings.points_key)
    return load_snapshot(raw_path, history, chart, slow, client=client)


def _live_snapshot(
        args: argparse.Namespace, client: Client, writer: Writer | None, provider: Provider,
) -> Snapshot | None:
    """The snapshot of the league now. A given --chart file stands in for the chart read."""
    read_chart = partial(chart_values, read=claude_reader(partial(parse_call, writer=writer)))
    if args.chart is not None:
        given = _given_chart(args.chart)

        # A given file is the chart of the trade, so the reader needs neither the week nor the lines.
        def read_chart(nfl: Path, season_start: date, week: int, lines: Iterable[PlayerLine], *,
                       chart: str) -> ChartValues:
            return given
    try:
        return live_snapshot(args.season, client=client, now=datetime.now(client.tz), read_chart=read_chart,
                             fetch_sleeper=provider.fetch_live, fetch_history_week=provider.fetch_past_leg,
                             fetch_projections=provider.fetch_projections)
    except ValueError as err:
        print(err)
        return None


# The page words of the fairness states. The lopsided line adds the team that gives more.
FAIRNESS_WORDS = {"win_win": "Good for both", "fair": "Fair", "lopsided": "Lopsided"}


def _fairness_lines(snapshot: Snapshot, fairness_result: Fairness) -> list[str]:
    """The fairness line in page words, then one reason per side, as the site shows them."""
    words = FAIRNESS_WORDS[fairness_result.state]
    if fairness_result.gives_more is not None:
        words += f": {snapshot.teams[fairness_result.gives_more].name} gives more."
    reasons = (f"  {snapshot.teams[side.roster_id].name}: {side.reason}" for side in fairness_result.sides)
    return [f"Fairness: {words}", *reasons]


def _print_as_of(snapshot: Snapshot) -> None:
    """Print the as-of line, the sources line, and any failed refresh, so a manager knows the data week."""
    # Analyze and find both print these lines, so the two commands show the stamps the same way.
    stamps = snapshot.as_of
    chart_text = f"Chart week {stamps.chart_week}" if stamps.chart_week is not None else "No chart"
    fetched = stamps.rosters_fetched.isoformat(timespec="minutes") if stamps.rosters_fetched else "unknown"
    known = stamps.known_games
    # With known games the next line counts week N, so this line names the completed week to count it once.
    through = stamps.completed_through if known is not None and known.games else stamps.stats_through
    print(f"Week {snapshot.week} of {snapshot.season}. {chart_text}. Stats through week {through}. "
          f"Rosters fetched {fetched}.")
    if known is not None:
        pending = ", ".join(f"{name} {count} game{'' if count == 1 else 's'}" for name, count in known.pending.items())
        print(f"Known games of week {known.week}: {known.games} read, {known.in_progress} in progress"
              f"{', pending: ' + pending if pending else ''}.")
    print(_sources_line(snapshot))
    if snapshot.stale:
        print(f"Refresh failed, so the cache is old or absent: {', '.join(snapshot.stale)}.")


def run_analyze(
        args: argparse.Namespace, client: Client, writer: Writer | None, provider: Provider,
) -> int:
    """Grade the proposed trade from the live or saved snapshot. Print the breakdowns, the verdict, and the fairness.

    Without --no-claude, it also prints Claude's final letter and analysis per side, and Claude's verdict.
    """
    if not MIN_SIDES <= len(args.side) <= MAX_SIDES:
        print("Give --side two to four times, once for each roster.")
        return 2
    sides = _proposed_sides(args.side)
    if sides is None:
        print("Give each player a destination, as PLAYER@ROSTER, in a trade of three or more sides.")
        return 2
    snapshot = (_live_snapshot(args, client, writer, provider) if args.week is None
                else _saved_snapshot(args, client))
    if snapshot is None:
        return 2
    try:
        trade = ProposedTrade(season=args.season, sides=sides, asker=args.asker)
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
        analysis = analyze(trade, snapshot, call=partial(analyzer_call, writer=writer))
        result, choice = analysis.breakdowns, analysis.code_verdict
    _print_as_of(snapshot)
    for index, (side, breakdown) in enumerate(zip(trade.sides, result)):
        asked = " (asked)" if side.roster_id == trade.asker else ""
        print()
        print(f"{snapshot.teams[side.roster_id].name}{asked}")
        if len(trade.sides) == 2:
            print(f"  Gives: {_names(snapshot, side.player_ids)}")
            print(f"  Gets: {_names(snapshot, trade.gets(side.roster_id))}")
        else:
            # With three or more sides each player names the team he goes to or comes from.
            print(f"  Gives: {_routed(snapshot, trade, side.roster_id, gives=True)}")
            print(f"  Gets: {_routed(snapshot, trade, side.roster_id, gives=False)}")
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
    # The fairness reads the letters that stand: Claude's when the call ran, the rubric's without it.
    letters = analysis.standing_letters if analysis is not None else tuple(b.final_letter for b in result)
    for line in _fairness_lines(snapshot, fairness(letters, result)):
        print(line)
    return 0


def run_find(
        args: argparse.Namespace, client: Client, writer: Writer | None, provider: Provider,
) -> int:
    """Print the top win-win trades between the asker and the partner, each with its sides and its fairness."""
    # A plain line for the same roster twice, before the snapshot loads, so no load runs for nothing.
    if args.asker == args.partner:
        print("Give two different rosters for --asker and --partner.")
        return 2
    snapshot = (_live_snapshot(args, client, writer, provider) if args.week is None
                else _saved_snapshot(args, client))
    if snapshot is None:
        return 2
    for roster_id in (args.asker, args.partner):
        if roster_id not in snapshot.rosters:
            print(f"Roster {roster_id} is not in the league.")
            return 2
    found = find_win_wins(args.asker, args.partner, snapshot)
    _print_as_of(snapshot)
    print()
    if not found:
        print(NO_WIN_WIN)
        return 0
    for number, item in enumerate(found, start=1):
        mine, theirs = item.trade.sides
        print(f"{number}. {snapshot.teams[mine.roster_id].name} gives: {_names(snapshot, mine.player_ids)}")
        print(f"   {snapshot.teams[theirs.roster_id].name} gives: {_names(snapshot, theirs.player_ids)}")
        # The same fairness lines as analyze, so a trade reads the same in both commands.
        for line in _fairness_lines(snapshot, item.fairness):
            print(line)
    return 0


def run_chart(
        client: Client, season: int, week: int, writer: Writer | None, fetch_state: Callable[[], RawState],
) -> int:
    """Print the parsed chart, every guard, and the match against the saved raw data of the week."""
    if client.chart is None:
        print(f"The client {client.slug} has no chart. Set chart under [values.league] of its client.toml.")
        return 2
    raw = load_raw(raw_dir(client.folder, season, week)) if has_raw(client.folder, season, week) else None
    if raw is not None:
        league = parse_week(raw)
        season_start = league.season_start
    else:
        # Sleeper state, as in resolve_week, gives the start date of the season in progress only.
        state = fetch_state()
        if int(state.season) != season:
            print(f"No raw data is saved for week {week} of {season}. Build the week first.")
            return 2
        season_start = date.fromisoformat(state.season_start_date)
    check = check_chart(client.nfl_dir, season_start, week, read=claude_reader(partial(parse_call, writer=writer)),
                        chart=client.chart)
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
    lines = {line.player_id: line for line in week_lines(league)}
    values = match_chart(check.chart, lines.values()).values
    print(f"Matched {len(values)} of {len(check.chart.rows)} chart rows")
    traded = {pid for t in parse_trades(raw.transactions) for pid in t.adds}
    unmatched = sorted(lines[pid].name if pid in lines else pid for pid in traded - values.keys())
    if unmatched:
        print("Unmatched traded players: " + ", ".join(unmatched))
    return 0


# The plain line when a command names no client, so no build reads the wrong league.
NO_CLIENT = "Name the client slug with --client. Example: --client cpc. Each client is a folder under clients/."


def find_root(start: Path) -> Path | None:
    """The repo root: the first folder from `start` upward that holds clients/. None when no folder does."""
    return next((folder for folder in (start, *start.parents) if (folder / "clients").is_dir()), None)


def run_check_client(folder: Path) -> int:
    """Check the client folder `folder` and the exported schema. Print OK, or each broken rule and exit 2."""
    try:
        read_client_values(folder)
        check_schema_file()
    except ClientError as err:
        print(err)
        return 2
    print(f"{folder / CLIENT_FILE} passes the check.")
    return 0


def run_settings(client: Client, season: int) -> int:
    """Print the League settings of the season and each size that derives from them."""
    settings = client.settings
    print(f"League settings of {client.slug} for {season}:")
    for name in ("team_count", "playoff_spots", "bye_count", "last_regular_week", "last_season_week",
                 "return_by_week", "lines", "strength_rank", "star_rank_by_position", "grade_spare_rank",
                 "grade_strong_rank", "grade_soft_rank", "reception_points", "points_key", "median_game",
                 "roster_slots"):
        print(f"  {name}: {getattr(settings, name)}")
    return 0


def main(
        argv: list[str] | None = None, *, writer: Writer | None = None, provider: Provider | None = None,
        fetch_state: Callable[[], RawState] = fetch_state,
) -> int:
    """Run one command. The writer, the provider, and the state fetch are seams, so a test passes the fakes.

    A provider of None is the Sleeper adapter with the shared NFL cache dir under the repo root.

    A writer of None is the one ClaudeWriter of the process, so a run makes one Claude client.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    if args.command == "check-client":
        return run_check_client(args.folder)
    repo = Path.cwd()
    if not (repo / "pyproject.toml").exists():
        print("Run cornerstone from the pipeline folder. No pyproject.toml in the current directory.")
        return 2
    if args.client is None:
        print(NO_CLIENT)
        return 2
    root = find_root(repo)
    if root is None:
        print(f"No clients folder in {repo} or above it. Run cornerstone inside the repo.")
        return 2
    # The adapter takes the shared cache dir of the repo, so every league of the repo shares one players file.
    provider = provider or SleeperProvider(provider_cache_dir(nfl_dir(root)))
    # The Claude calls of the CLI. The chart read and the analyzer call get the writer in their commands.
    # The build gets the writer too, for its research call.
    call = partial(claude_call, writer=writer)

    def load(season: int) -> Client:
        # The one client of the run. Every command that needs a league value gets it from here.
        return load_client(root, args.client, season, provider.fetch_settings)

    try:
        if args.command in ("history", "settings"):
            # History and settings have no --week, so they skip resolve_week.
            season = args.season if args.season is not None else int(fetch_state().season)
            client = load(season)
            if args.command == "settings":
                return run_settings(client, season)
            weeks = run_history(season, args.through, force=args.force, client=client)
            print(("Fetched weeks: " + ", ".join(str(w) for w in weeks)) if weeks else "Nothing to fetch")
            return 0
        if args.command == "analyze":
            # Analyze skips resolve_week. Without --week it reads Sleeper itself, and with --week it reads disk.
            return run_analyze(args, load(args.season), writer, provider)
        if args.command == "find":
            # Find skips resolve_week for the same reason as analyze.
            return run_find(args, load(args.season), writer, provider)
        # resolve_week can call Sleeper, so a network failure gets the same plain exit.
        season, week = resolve_week(args.season, args.week, fetch_state)
        client = load(season)
        if args.command == "build":
            # A named week with saved raw data rebuilds from disk, so a rebuild sees the same data.
            fetch = not args.no_fetch and (
                args.refetch or args.week is None or not has_raw(client.folder, season, week)
            )
            page = run_build(repo, season, week, call, fetch=fetch, client=client, provider=provider, writer=writer)
            print(page)
            print(f"Site page after publish: {site_page_url(season, week)}")
            preview(page)
        elif args.command == "chart":
            return run_chart(client, season, week, writer, fetch_state)
        elif args.command == "page-json":
            print(run_page_json(repo, season, week, client=client))
        elif args.command == "rankings":
            print(run_rankings(repo, season, week, call, client=client))
        elif args.command == "rewrite":
            page = run_rewrite(repo, season, week, args.chapter, call, client=client)
            print(page)
            print(f"Site page after publish: {site_page_url(season, week)}")
            preview(page)
        else:
            answer = input(f"Publish week {week} to GitHub Pages? [y/N] ")
            if answer not in ("y", "Y"):
                print("Not published.")
                return 0
            print(run_publish(repo, season, week, client.slug, client.folder / "data"))
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
