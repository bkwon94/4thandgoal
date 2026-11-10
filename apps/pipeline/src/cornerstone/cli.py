"""
Command line entry point for Cornerstone Weekly.
It defines the build, publish, rewrite, page-json, rankings, midseason, midseason-publish, history, chart,
advisor-eval, egg-draft, egg-drop, check-client, and evidence-flags subcommands.
"""
import argparse
import logging
import subprocess
from collections.abc import Callable
from datetime import date
from functools import partial
from pathlib import Path

import httpx

from cornerstone.advisor_eval import Meter, fetch_press_sources, load_test_set, run_eval, summary_lines
from cornerstone.egg_draft import run_egg_draft
from cornerstone.egg_drop import drop_after_publish, drop_from_env
from cornerstone.evidence_flags import run_evidence_flags
from cornerstone.pipeline import (
    BuildStopped,
    has_raw,
    preview,
    resolve_week,
    run_build,
    run_history,
    run_midseason,
    run_page_json,
    run_rankings,
    run_rewrite,
)
from cornerstone.publish import PublishError, run_midseason_publish, run_publish, site_page_url
from cornerstone.value_models import VALUE_MODELS
from eggs.draft import DraftError
from eggs.eggfile import default_egg_file
from facts.writer import ClaudeWriter, analyzer_call, claude_call, parse_call
from league.chart import check_chart, claude_reader, match_chart, saved_chart_read
from league.claude_port import Writer
from league.client import CLIENT_FILE, Client, ClientError, check_schema_files, load_client, read_client_values
from league.jev import JEV
from league.jev_port import Jev
from league.models import ChartValues, week_lines
from league.nflverse import http_get
from league.parse import parse_trades, parse_week
from league.paths import history_root, nfl_dir, nflverse_cache_dir, provider_cache_dir, raw_dir
from league.provider.base import Provider
from league.provider.raw import RawState, RawWeek
from league.provider.sleeper import SleeperProvider, fetch_state, load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import Snapshot, load_snapshot, saved_chart_before


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

    midseason = sub.add_parser("midseason", parents=[named],
                               help="write the midseason report of a saved week into the build folder of the season")
    midseason.add_argument("--week", type=int)
    midseason.add_argument("--season", type=int)

    midseason_publish = sub.add_parser(
        "midseason-publish", parents=[named],
        help="check each blurb of the midseason draft again, then commit and push midseason.json and sim.json")
    midseason_publish.add_argument("--week", type=int)
    midseason_publish.add_argument("--season", type=int)

    history = sub.add_parser("history", parents=[named], help="fetch and cache past weeks")
    history.add_argument("--season", type=int)
    history.add_argument("--through", type=int, required=True)
    history.add_argument("--force", action="store_true", help="fetch even when a week is saved")

    chart = sub.add_parser("chart", parents=[named], help="fetch, read, and match the trade value chart of a week")
    chart.add_argument("--week", type=int)
    chart.add_argument("--season", type=int)

    advisor_eval = sub.add_parser(
        "advisor-eval", parents=[named], help="read each trade of a test set with the real Advisor and the real Jev",
        description="Read each trade of a test set file as of its week, from the saved data of that week. Save the "
                    "fact sheet and the read of each trade, and print the Leans, the cost, and the time. The test set "
                    "and the output name league managers, so keep both outside the repo or in a folder that git "
                    "ignores. Example: --season 2026 --test-set ~/results.json --out ~/eval-out")
    advisor_eval.add_argument("--season", type=int, required=True)
    advisor_eval.add_argument("--test-set", type=Path, required=True, help="the JSON file with the trades to read")
    advisor_eval.add_argument("--out", type=Path, required=True, help="the folder for the saved sheets and reads")
    advisor_eval.add_argument("--workers", type=int, default=4, help="how many trades to read at one time")

    settings = sub.add_parser("settings", parents=[named], help="print the League settings and the sizes of a season")
    settings.add_argument("--season", type=int)

    # The egg file sits outside the repo, so the repo never names a spot. A test names a temp file.
    eggs_file = argparse.ArgumentParser(add_help=False)
    eggs_file.add_argument("--eggs-file", type=Path, help="the egg file; the default is ~/cpc-eggs/<season>.toml")

    egg_draft = sub.add_parser("egg-draft", parents=[named, eggs_file],
                               help="propose the spots of the egg drop of a week with an agent, marked not confirmed")
    egg_draft.add_argument("--week", type=int)
    egg_draft.add_argument("--season", type=int)

    egg_drop = sub.add_parser("egg-drop", parents=[named, eggs_file],
                              help="send the confirmed eggs of a week to the API; a failed drop warns and exits 0")
    egg_drop.add_argument("--week", type=int)
    egg_drop.add_argument("--season", type=int)
    # The publish runs the egg drop as its last step, so it takes the egg file too.
    publish.add_argument("--eggs-file", type=Path, help="the egg file; the default is ~/cpc-eggs/<season>.toml")

    check = sub.add_parser("check-client", help="check the client.toml of a client folder and the exported schema")
    check.add_argument("folder", type=Path, help="the client folder, such as ../../clients/cpc")

    flags = sub.add_parser("evidence-flags",
                           help="ask Jev about the evidence of each acceptance test and add each flag to FLAGS.md")
    flags.add_argument("slug", help="the feature folder under .scratch/")
    flags.add_argument("tests", nargs="*", metavar="AT-<n>", help="the tests to read; the default is every test in EVIDENCE.md")
    flags.add_argument("--root", type=Path, help="the folder that holds .scratch/; the default is the current worktree")

    return parser


def _saved_chart_values(nfl: Path, week: int, raw: RawWeek, chart_name: str) -> ChartValues | None:
    """The trade values of the saved chart read of the week, or None. It never fetches or reads an image."""
    # The chart module owns the rules for a saved read, so a bad or stale one gives None here too.
    chart = saved_chart_read(nfl, week, chart=chart_name)
    if chart is None:
        return None
    return match_chart(chart, week_lines(parse_week(raw)))


def _given_chart(path: Path) -> ChartValues:
    """The trade values in a --chart JSON file."""
    return ChartValues.model_validate_json(path.read_text(encoding="utf-8"))


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
        chart = _saved_chart_values(client.nfl_dir, args.week, raw, client.chart) if client.chart is not None else None
    # With no chart of the week, the superstar check reads the newest saved read of the weeks before.
    before = saved_chart_before(client, args.week, raw, chart)
    history = history_root(client.folder, args.season)
    # A saved week never fetches. A cache that the build did not fill gives missing sources.
    slow = load_slow_sources(nflverse_cache_dir(client.nfl_dir), args.season, args.week, history,
                             raw.league.scoring_settings, client.settings.points_key)
    return load_snapshot(raw_path, history, chart, slow, client=client, chart_before=before)


def _out_is_safe(out: Path, root: Path) -> bool:
    """True when `out` is outside the repo, or inside it and ignored by git, so no output file can reach a commit."""
    resolved = out.resolve()
    if not resolved.is_relative_to(root.resolve()):
        return True
    # A folder that does not exist yet has no ignore state of its own, so ask about a file in it.
    probe = resolved / "summary.json"
    return subprocess.run(["git", "check-ignore", "-q", str(probe)], cwd=root, check=False).returncode == 0


def run_advisor_eval(
        args: argparse.Namespace, client: Client, writer: Writer | None, jev: Jev | None, root: Path,
        fetch: Callable[[str], bytes],
) -> int:
    """Read the trades of the test set as of their weeks, save each sheet and read, and print the summary.

    Before the reads, `fetch` downloads the sources that a press downloads, so the sheet is the sheet of a press.
    The exit code is 1 when a trade has no read, and 2 when the output folder is in the repo and not ignored.
    """
    if not _out_is_safe(args.out, root):
        print(f"{args.out} is in the repo and git does not ignore it. The output names league managers, "
              "so use a folder outside the repo or a folder in .gitignore.")
        return 2
    for line in fetch_press_sources(client, args.season, fetch):
        print(line)
    meter = Meter()
    # The writer of the run counts each response, so the summary has the real cost. A test passes its own writer.
    writer = writer or ClaudeWriter(on_usage=meter.add_claude)

    def snapshot_of(week: int):
        snapshot = _saved_snapshot(argparse.Namespace(season=args.season, week=week, chart=None), client)
        if snapshot is None:
            raise ValueError(f"The test set has trades of week {week}, and that week has no saved raw data.")
        return snapshot, load_raw(raw_dir(client.folder, args.season, week)).transactions

    summary = run_eval(load_test_set(args.test_set), snapshot_of, jev=JEV if jev is None else jev,
                       call=partial(analyzer_call, writer=writer), out_dir=args.out, meter=meter,
                       workers=args.workers)
    print("\n".join(summary_lines(summary)))
    return 1 if summary["errors"] else 0


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
    print(f"Read {len(check.chart.rows)} chart rows")
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
    """Check the client folder `folder` and each exported schema. Print OK, or each broken rule and exit 2."""
    try:
        read_client_values(folder, VALUE_MODELS)
        check_schema_files(VALUE_MODELS)
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


def find_scratch_root(start: Path) -> Path | None:
    """The nearest folder at or above `start` that holds .scratch/, or None."""
    for folder in (start, *start.parents):
        if (folder / ".scratch").is_dir():
            return folder
    return None


def main(
        argv: list[str] | None = None, *, writer: Writer | None = None, provider: Provider | None = None,
        fetch_state: Callable[[], RawState] = fetch_state, jev: Jev | None = None,
) -> int:
    """Run one command. The writer, the provider, the state fetch, and the Jev are seams, so a test passes the fakes.

    A provider of None is the Sleeper adapter with the shared NFL cache dir under the repo root.

    A writer of None is the one ClaudeWriter of the process, so a run makes one Claude client.
    A Jev of None is the one TypeSafeJev of the process. Only the build runs a Jev check.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    if args.command == "check-client":
        return run_check_client(args.folder)
    if args.command == "evidence-flags":
        # The command reads the tracker of a worktree, not a league, so it needs no client and no pipeline folder.
        root = args.root or find_scratch_root(Path.cwd())
        if root is None:
            print(f"No .scratch folder in {Path.cwd()} or above it. Run the command inside a worktree, or pass --root.")
            return 2
        return run_evidence_flags(root, args.slug, args.tests, JEV if jev is None else jev)
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
        return load_client(root, args.client, season, provider.fetch_settings, VALUE_MODELS)

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
        if args.command == "advisor-eval":
            # The eval reads the week of each trade of its test set, so it skips resolve_week too.
            # The download is read at call time, so a test swaps http_get of this module and makes no network call.
            return run_advisor_eval(args, load(args.season), writer, jev, root, http_get)
        # resolve_week can call Sleeper, so a network failure gets the same plain exit.
        season, week = resolve_week(args.season, args.week, fetch_state)
        client = load(season)
        if args.command == "build":
            # A named week with saved raw data rebuilds from disk, so a rebuild sees the same data.
            fetch = not args.no_fetch and (
                args.refetch or args.week is None or not has_raw(client.folder, season, week)
            )
            page = run_build(repo, season, week, call, fetch=fetch, client=client, provider=provider, writer=writer,
                             jev=jev)
            print(page)
            print(f"Site page after publish: {site_page_url(client.slug, season, week)}")
            preview(page)
        elif args.command == "chart":
            return run_chart(client, season, week, writer, fetch_state)
        elif args.command == "page-json":
            print(run_page_json(repo, season, week, client=client))
        elif args.command == "rankings":
            print(run_rankings(repo, season, week, call, client=client))
        elif args.command == "midseason":
            print(run_midseason(season, week, call, client=client, provider=provider))
        elif args.command == "midseason-publish":
            answer = input(f"Publish the midseason report of week {week} of {client.slug}? [y/N] ")
            if answer not in ("y", "Y"):
                print("Not published.")
                return 0
            print(run_midseason_publish(repo, season, week, call, client=client))
            print("Committed and pushed. The report is live after the site deploys.")
        elif args.command == "egg-draft":
            egg_file = args.eggs_file or default_egg_file(season)
            spots = run_egg_draft(client, season, week, egg_file, root)
            print(f"Wrote {len(spots)} spots of week {week} to {egg_file}, each marked not confirmed.")
            print("Keep, change, or reject each spot. Set confirmed = true on each spot to drop.")
        elif args.command == "egg-drop":
            print(drop_from_env(client, week, args.eggs_file or default_egg_file(season)))
        elif args.command == "rewrite":
            page = run_rewrite(repo, season, week, args.chapter, call, client=client)
            print(page)
            print(f"Site page after publish: {site_page_url(client.slug, season, week)}")
            preview(page)
        else:
            answer = input(f"Publish week {week} of {client.slug}? [y/N] ")
            if answer not in ("y", "Y"):
                print("Not published.")
                return 0
            print(run_publish(repo, season, week, client.slug, client.folder))
            # The last step of the publish: a failed drop warns and keeps the exit 0, and "make egg-drop" retries.
            print(drop_after_publish(client, week, args.eggs_file or default_egg_file(season)))
    except (BuildStopped, PublishError, DraftError, ValueError) as err:
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
