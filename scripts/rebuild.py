"""
Rebuild the latest week of each client with the code of the base and with the code of the head.
Diff facts.json, page.json, topics.json, and waiver.json by JSON path.
Check each diff against the approved diffs (ADR 0037).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# The files of a week that the render writes. The diff compares each one.
RENDER_FILES = ("page.json", "topics.json", "waiver.json")
# Every file that the job diffs. The facts-only rebuild adds facts.json to the render files.
DIFFED_FILES = ("facts.json", *RENDER_FILES)
# The saved inputs of a week that the facts-only rebuild reads, by their path in the data folder of the week.
SAVED_INPUTS = ("verify.json", "raw/nflverse.json", "raw/slow_sources.json", "raw/news.json")
# The rebuild makes no Claude call and no TypeSafe call, so a run never gets either key, even from a local shell.
SECRETS = ("ANTHROPIC_API_KEY", "TYPESAFE_API_KEY")
# The command line that runs the pipeline CLI of one checkout.
CORNERSTONE = ["uv", "run", "--quiet", "--exact", "--package", "cornerstone", "cornerstone"]
WEEK_FOLDER = re.compile(r"week-(\d{2})")


@dataclass(frozen=True)
class Week:
    slug: str
    season: int
    week: int

    def __str__(self) -> str:
        return f"{self.slug} {self.season} week {self.week}"


@dataclass(frozen=True, order=True)
class Change:
    """One changed value of the output: the client, the file, and the JSON path in the file."""
    slug: str
    name: str
    path: str

    def __str__(self) -> str:
        return f"{self.slug} {self.name} {self.path}"


@dataclass(frozen=True)
class Result:
    unlisted: list[Change]
    unchanged: list[Change]

    @property
    def passed(self) -> bool:
        return not self.unlisted and not self.unchanged


# One approved diff per list line: "- <client> <file> <JSON path>: <reason>". Backticks around each part are optional.
# The same line shape serves REBUILD.md of a spec and the Rebuild: block of a quick file.
APPROVED_LINE = re.compile(r"^\s*[-*]\s+`?([\w-]+)`?\s+`?(" + "|".join(map(re.escape, DIFFED_FILES)) + r")`?"
                           r"\s+`?(\$[^`\s]*)`?\s*:\s*(.+?)\s*$")


def read_approved(text: str) -> dict[Change, str]:
    """The approved diffs of one list file, each with its reason."""
    return {Change(m.group(1), m.group(2), m.group(3)): m.group(4)
            for line in text.splitlines() if (m := APPROVED_LINE.match(line))}


def check(changed: list[Change], approved: dict[Change, str]) -> Result:
    """The job passes only when the set of changed paths equals the listed set (ADR 0037)."""
    return Result(unlisted=[c for c in changed if c not in approved],
                  unchanged=sorted(c for c in approved if c not in set(changed)))


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


def has_saved_inputs(root: Path, week: Week) -> bool:
    """True when the data folder of the week holds each input of the facts-only rebuild."""
    return all((data_week(root, week) / name).is_file() for name in SAVED_INPUTS)


def base_rebuilds_facts(base: Path) -> bool:
    """True when the CLI of the base has the facts-only rebuild. A base without it gets the render diff only.
    The probe runs the command as the rebuild does, so a rename or a reformat of the CLI source cannot fool it."""
    probe = subprocess.run([*CORNERSTONE, "facts", "--help"], cwd=base, env=clean_env(),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return probe.returncode == 0


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


def clean_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in SECRETS}


def cornerstone(checkout: Path, command: str, week: Week) -> None:
    """Run one command of the pipeline CLI on one week with the code of one checkout. It writes into that checkout:
    facts writes facts.json into the data folder, and page-json writes the build folder."""
    subprocess.run([*CORNERSTONE, command, "--client", week.slug, "--season", str(week.season),
                    "--week", str(week.week)],
                   cwd=checkout, env=clean_env(), check=True, stdout=subprocess.DEVNULL)


def share_inputs(base: Path, head: Path, week: Week) -> None:
    """Copy the saved week of the head into the base, so both codes read the same inputs.
    The base can lag the head, or lack the week, when main got the week after the PR merged main."""
    if base != head:
        shutil.copytree(data_week(head, week), data_week(base, week), dirs_exist_ok=True)


def diff_week(base: Path, head: Path, week: Week, with_facts: bool) -> list[Change]:
    """Rebuild one week with the code of the base and of the head, and give each changed value."""
    share_inputs(base, head, week)
    files = [(name, build_week) for name in RENDER_FILES]
    if with_facts:
        cornerstone(base, "facts", week)
        cornerstone(head, "facts", week)
        files.insert(0, ("facts.json", data_week))
    cornerstone(base, "page-json", week)
    cornerstone(head, "page-json", week)
    return [Change(week.slug, name, path) for name, folder in files
            for path in file_diff(folder(base, week) / name, folder(head, week) / name)]


def report(week: Week, changed: list[Change], approved: dict[Change, str], with_facts: bool) -> None:
    names = (("facts.json",) if with_facts else ()) + RENDER_FILES
    for name in names:
        paths = [c for c in changed if c.name == name]
        print(f"{week} {name}: {len(paths)} diffs")
        for change in paths:
            note = f"approved: {approved[change]}" if change in approved else "not listed"
            print(f"  {change.path}  ({note})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="a checkout of the base, such as main")
    parser.add_argument("--head", type=Path, required=True, help="a checkout of the PR")
    parser.add_argument("--approved", type=Path, action="append", default=[],
                        help="a REBUILD.md or a quick file whose list names the approved diffs; repeat for more")
    args = parser.parse_args()
    base, head = args.base.resolve(), args.head.resolve()

    approved: dict[Change, str] = {}
    for path in args.approved:
        approved.update(read_approved(path.read_text(encoding="utf-8")))
        print(f"approved diffs: {path}")

    base_has_facts = base_rebuilds_facts(base)
    if not base_has_facts:
        print("render only: the base has no facts-only rebuild")

    weeks = latest_weeks(head)
    if not weeks:
        print("No client has a published week with saved facts. Nothing to diff.")
    changed: list[Change] = []
    for week in weeks:
        with_facts = base_has_facts and has_saved_inputs(head, week)
        if base_has_facts and not with_facts:
            print(f"render only: {week} has no saved inputs of the facts")
        week_changed = diff_week(base, head, week, with_facts)
        report(week, week_changed, approved, with_facts)
        changed += week_changed

    result = check(changed, approved)
    for change in result.unlisted:
        print(f"changed but not listed: {change}")
    for change in result.unchanged:
        print(f"listed but not changed: {change}")
    print(f"rebuild diff: {len(changed)} diffs, {len(changed) - len(result.unlisted)} listed, "
          f"{len(result.unlisted)} not listed, {len(result.unchanged)} listed but not changed")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
