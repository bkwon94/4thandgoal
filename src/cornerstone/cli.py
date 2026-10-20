"""
Command line entry point for Cornerstone Weekly.
It defines the build, publish, and rewrite subcommands.
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cornerstone", description="Build the weekly Cornerstone report.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="build the report for a week")
    build.add_argument("--week", type=int)
    build.add_argument("--season", type=int)

    publish = sub.add_parser("publish", help="publish the built report")
    publish.add_argument("--week", type=int)

    rewrite = sub.add_parser("rewrite", help="rewrite one chapter of the report")
    rewrite.add_argument("--week", type=int)
    rewrite.add_argument("--chapter", type=str, required=True)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(f"{args.command}: not implemented")
    return 1
