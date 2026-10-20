"""
Command line entry point for Cornerstone Weekly.
It defines the build, publish, rewrite, and history subcommands.
"""
import argparse
import logging
from pathlib import Path

import httpx


from cornerstone.pipeline import BuildStopped, has_raw, preview, resolve_week, run_build, run_history, run_rewrite
from cornerstone.sleeper import fetch_state
from cornerstone.publish import PublishError, run_publish
from cornerstone.writer import claude_call


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

    history = sub.add_parser("history", help="fetch and cache past weeks")
    history.add_argument("--season", type=int)
    history.add_argument("--through", type=int, required=True)
    history.add_argument("--force", action="store_true", help="fetch even when a week is saved")

    return parser


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
            print("Fetched weeks: " + ", ".join(str(w) for w in weeks) if weeks else "Nothing to fetch")
            return 0
        # resolve_week can call Sleeper, so a network failure gets the same plain exit.
        season, week = resolve_week(args.season, args.week)
        if args.command == "build":
            # A named week with saved raw data rebuilds from disk, so a rebuild sees the same data.
            fetch = not args.no_fetch and (
                args.refetch or args.week is None or not has_raw(repo, season, week)
            )
            page = run_build(repo, season, week, claude_call, fetch=fetch)
            print(page)
            preview(page)
        elif args.command == "rewrite":
            page = run_rewrite(repo, season, week, args.chapter, claude_call)
            print(page)
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
