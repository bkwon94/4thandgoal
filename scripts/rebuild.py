"""
Runs the base and head rebuild of the latest week of each client: page-json with the code of the base and of the head,
then a diff of page.json, topics.json, and waiver.json by JSON path. Any diff fails the run (ADR 0037).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# The files of a week that the render writes. The diff compares each one.
RENDER_FILES = ("page.json", "topics.json", "waiver.json")
PIPELINE_CLI = Path("apps/pipeline/src/cornerstone/cli.py")
# The rebuild makes no Claude call and no TypeSafe call, so a run never gets either key, even from a local shell.
SECRETS = ("ANTHROPIC_API_KEY", "TYPESAFE_API_KEY")
WEEK_FOLDER = re.compile(r"week-(\d{2})")


@dataclass(frozen=True)
class Week:
    slug: str
    season: int
    week: int

    def __str__(self) -> str:
        return f"{self.slug} {self.season} week {self.week}"


def data_week(root: Path, week: Week) -> Path:
    return root / "clients" / week.slug / "data" / str(week.season) / f"week-{week.week:02d}"


def build_week(root: Path, week: Week) -> Path:
    return root / "clients" / week.slug / "build" / str(week.season) / f"week-{week.week:02d}"


def latest_weeks(root: Path) -> list[Week]:
    """The latest published week of each client whose saved facts and blurbs let page-json render it again."""
    weeks = []
    for client in sorted((root / "clients").iterdir()):
        if not (client / "client.toml").is_file():
            continue
        seasons = sorted((int(p.name) for p in (client / "published").glob("[0-9]*") if p.is_dir()), reverse=True)
        for season in seasons:
            numbers = sorted((int(m.group(1)) for p in (client / "published" / str(season)).iterdir()
                              if (m := WEEK_FOLDER.fullmatch(p.name))), reverse=True)
            found = next((Week(client.name, season, n) for n in numbers
                          if all((data_week(root, Week(client.name, season, n)) / name).is_file()
                                 for name in ("facts.json", "blurbs.json"))), None)
            if found:
                weeks.append(found)
                break
    return weeks


def base_rebuilds_facts(base: Path) -> bool:
    """True when the CLI of the base has the facts-only rebuild. Until then the job can diff the render only."""
    cli = base / PIPELINE_CLI
    return cli.is_file() and 'add_parser("facts"' in cli.read_text(encoding="utf-8")


def json_diff(before, after, path: str = "$") -> list[str]:
    """The JSON path of each value that differs, in the order of the keys and the items."""
    if isinstance(before, dict) and isinstance(after, dict):
        keys = list(before) + [key for key in after if key not in before]
        return [p for key in keys for p in (json_diff(before[key], after[key], f"{path}.{key}")
                                            if key in before and key in after else [f"{path}.{key}"])]
    if isinstance(before, list) and isinstance(after, list):
        common = [p for i, (a, b) in enumerate(zip(before, after)) for p in json_diff(a, b, f"{path}[{i}]")]
        return common + [f"{path}[{i}]" for i in range(min(len(before), len(after)), max(len(before), len(after)))]
    return [] if before == after and type(before) is type(after) else [path]


def file_diff(before: Path, after: Path) -> list[str]:
    """The diff of two JSON files. A file that one side lacks is one diff at the root."""
    if not before.is_file() and not after.is_file():
        return []
    if not before.is_file() or not after.is_file():
        return ["$"]
    return json_diff(json.loads(before.read_text(encoding="utf-8")), json.loads(after.read_text(encoding="utf-8")))


def render(checkout: Path, week: Week) -> None:
    """Run page-json of one week with the code of one checkout. It writes into the build folder of that checkout."""
    env = {key: value for key, value in os.environ.items() if key not in SECRETS}
    subprocess.run(["uv", "run", "--quiet", "--exact", "--package", "cornerstone", "cornerstone", "page-json",
                    "--client", week.slug, "--season", str(week.season), "--week", str(week.week)],
                   cwd=checkout, env=env, check=True, stdout=subprocess.DEVNULL)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="a checkout of the base, such as main")
    parser.add_argument("--head", type=Path, required=True, help="a checkout of the PR")
    args = parser.parse_args()
    base, head = args.base.resolve(), args.head.resolve()

    if not base_rebuilds_facts(base):
        print("render only: the base has no facts-only rebuild")
    else:
        print("render only: the job has no facts diff")

    weeks = latest_weeks(head)
    if not weeks:
        print("No client has a published week with saved facts. Nothing to diff.")
        return 0
    total = 0
    for week in weeks:
        render(base, week)
        render(head, week)
        for name in RENDER_FILES:
            paths = file_diff(build_week(base, week) / name, build_week(head, week) / name)
            total += len(paths)
            print(f"{week} {name}: {len(paths)} diffs")
            for path in paths:
                print(f"  {path}")
    print(f"render diff: {total} diffs")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
