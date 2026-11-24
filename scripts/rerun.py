"""
Runs the Red and Green commands of the quick file of a PR again: Red at the red commit must fail, Green at the fix
commit must pass, and the output of Red must hold each failure line that the Red block quotes (ADR 0037).
"""
import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# The folders of the quick files of 4ag:quick. See format.md of the skill.
QUICK_FOLDERS = (".scratch/bugs", ".scratch/quick-wins")
ITEM_HEADING = re.compile(r"^### (\d+)\. (.+)$", re.MULTILINE)
# The two forms of a Red line in format.md: at one commit, or at the parent with the loop file of the fix commit.
# The command may end with " in `<folder>`", the folder to run it in.
RUN_LINE = re.compile(
    r"^(?P<kind>Red|Green): at `(?P<sha>[0-9a-f]{7,40})`"
    r"(?: with `(?P<loop_file>[^`]+)` of `(?P<loop_sha>[0-9a-f]{7,40})`)?"
    r", (?:`(?P<command>[^`]+)`(?: in `(?P<folder>[^`]+)`)?|(?P<same>the same command))",
    re.MULTILINE)
TEXT_BLOCK = re.compile(r"^```text\n(.*?)^```", re.MULTILINE | re.DOTALL)
# A quoted line with one of these marks is a failure line, such as "AssertionError: ...", "FAILED ...", or "✘ 1 ...".
# Bun marks a failure with "(fail) <test name>", "error: expect(...)", and a summary such as " 1 fail".
FAILURE_MARK = re.compile(r"FAIL|Error|✘|×|\bfailed\b|^E\s|\(fail\)|^error:|^[1-9]\d* fail$")
# A number changes from run to run, such as a time, so the compare treats each number as the same.
NUMBER = re.compile(r"\d+(?:\.\d+)?")
# A quick file may cut a long line with "...", as pytest does, so a cut matches any text.
CUT = re.compile(r"\.\.\.|…")
# A tool such as Vitest on GitHub Actions colors its output with ANSI codes, so the compare drops each code.
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
# The site client build that a site loop needs at each commit, as the site job of Check does before its tests.
CLIENT_BUILD = "CLIENT=cpc node scripts/client-build.mjs"
# A loop that runs longer than this counts as a failure, so a hung command cannot hold the job.
TIMEOUT_SECONDS = 1800


@dataclass
class Run:
    sha: str
    command: str
    folder: str
    loop_file: str | None = None
    loop_sha: str | None = None


@dataclass
class Item:
    number: str
    title: str
    text_only: bool
    red: Run | None = None
    green: Run | None = None
    failure_lines: list[str] | None = None
    problem: str | None = None

    @property
    def name(self) -> str:
        return f"item {self.number} ({self.title})"

    def members(self) -> set[str]:
        """The members that the commands of the item need, read from the commands and their folders."""
        needs = set()
        for run in (self.red, self.green):
            if run is None:
                continue
            words = f"{run.command} {run.folder}"
            if "apps/site" in words or "pnpm" in words:
                needs.add("site")
            if re.search(r"\buv\b|pytest|apps/api|apps/pipeline|packages/[^/\s]+/python", words):
                needs.add("python")
        return needs


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, env=clean_env(), check=True, capture_output=True,
                          text=True).stdout


def clean_env() -> dict[str, str]:
    """The environment with no GIT_ variable. A git hook sets GIT_DIR and GIT_INDEX_FILE, which would point the git
    calls and the loops at the index of the hook."""
    return {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}


def quick_files(repo: Path, base: str, head: str) -> list[str]:
    """The quick files that the PR adds: Markdown files directly under a quick folder."""
    added = git(repo, "diff", "--name-only", "--diff-filter=A", f"{base}...{head}").splitlines()
    return [path for path in added
            if str(PurePosixPath(path).parent) in QUICK_FOLDERS and path.endswith(".md")]


def parse_items(text: str) -> list[Item]:
    headings = list(ITEM_HEADING.finditer(text))
    items = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else text.find("\n## ", heading.end())
        body = text[heading.end():end if end != -1 else len(text)]
        method = re.search(r"^Method: (.+)$", body, re.MULTILINE)
        item = Item(heading.group(1), heading.group(2).strip(),
                    text_only=bool(method and "text only" in method.group(1)))
        if not item.text_only:
            read_runs(item, body)
        items.append(item)
    return items


def read_runs(item: Item, body: str) -> None:
    """Reads the Red and Green runs and the quoted failure lines of one item, or sets the problem of the item."""
    lines = {match.group("kind"): match for match in RUN_LINE.finditer(body)}
    if "Red" not in lines or "Green" not in lines:
        missing = " and ".join(kind for kind in ("Red", "Green") if kind not in lines)
        item.problem = f"the {missing} line does not name a commit and a command in the form of format.md"
        return
    red, green = lines["Red"], lines["Green"]
    if red.group("same"):
        item.problem = "the Red line names no command"
        return
    item.red = Run(red.group("sha"), red.group("command"), red.group("folder") or ".",
                   red.group("loop_file"), red.group("loop_sha"))
    if green.group("same"):
        item.green = Run(green.group("sha"), item.red.command, item.red.folder)
    else:
        item.green = Run(green.group("sha"), green.group("command"), green.group("folder") or ".")
    block = TEXT_BLOCK.search(body, red.end(), green.start())
    quoted = block.group(1).splitlines() if block else []
    item.failure_lines = [line.strip() for line in quoted if FAILURE_MARK.search(line.strip())]
    if not item.failure_lines:
        item.problem = "the Red block quotes no failure line"


def normal(text: str) -> str:
    return " ".join(NUMBER.sub("0", ANSI.sub("", text)).split())


def shows(line: str, printed: str) -> bool:
    """True if the output shows the quoted line: each part between the cuts shows, in order."""
    at = 0
    for part in CUT.split(line):
        part = normal(part)
        found = printed.find(part, at)
        if found == -1:
            return False
        at = found + len(part)
    return True


def run_at(repo: Path, run: Run, site: bool) -> tuple[int, str]:
    """Checks out the commit of the run, and the loop file if the run names one, and runs the command there."""
    git(repo, "checkout", "-q", "--force", "--detach", run.sha)
    if run.loop_file:
        git(repo, "checkout", "-q", run.loop_sha, "--", run.loop_file)
    if site and (repo / "apps/site/scripts/client-build.mjs").exists():
        subprocess.run(CLIENT_BUILD, shell=True, cwd=repo / "apps/site", env=clean_env(), check=True,
                       capture_output=True)
    try:
        done = subprocess.run(["bash", "-c", run.command], cwd=repo / run.folder, env=clean_env(),
                              capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        return 124, f"{error.stdout or ''}{error.stderr or ''}\nThe command ran past {TIMEOUT_SECONDS} s."
    return done.returncode, done.stdout + done.stderr


def show(label: str, code: int, output: str) -> None:
    """Prints the exit code and the last lines of one run, so the log of the job shows what the run printed."""
    tail = output.strip().splitlines()[-40:]
    print(f"  {label}: exit {code}")
    for line in tail:
        print(f"    | {line}")


def check_item(repo: Path, item: Item) -> list[str]:
    """Runs the item and gives each way in which it does not hold. An empty list means the item holds."""
    if item.problem:
        return [f"{item.name}: {item.problem}"]
    site = "site" in item.members()
    problems = []
    code, output = run_at(repo, item.red, site)
    show(f"Red at {item.red.sha}", code, output)
    if code == 0:
        problems.append(f"{item.name}: the Red command passed at `{item.red.sha}`, so the loop never went red")
    else:
        printed = normal(output)
        for line in item.failure_lines:
            if not shows(line, printed):
                problems.append(f"{item.name}: the Red output has no line `{line}`")
    code, output = run_at(repo, item.green, site)
    show(f"Green at {item.green.sha}", code, output)
    if code != 0:
        problems.append(f"{item.name}: the Green command failed at `{item.green.sha}` with exit {code}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."), help="the checkout of the PR, with its full history")
    parser.add_argument("--base", required=True, help="the base commit of the PR")
    parser.add_argument("--head", required=True, help="the head commit of the PR")
    parser.add_argument("--members", action="store_true",
                        help="print the members that the loops need, and run nothing")
    args = parser.parse_args()
    repo = args.repo.resolve()

    paths = quick_files(repo, args.base, args.head)
    if not paths:
        if args.members:
            print("members: none")
        else:
            print("no quick file: the PR adds no file under .scratch/bugs/ or .scratch/quick-wins/, so the job passes.")
        return 0
    files = {path: parse_items(git(repo, "show", f"{args.head}:{path}")) for path in paths}

    if args.members:
        needs = set().union(*(item.members() for items in files.values() for item in items if not item.text_only))
        print("members: " + (" ".join(sorted(needs)) or "none"))
        return 0

    # Each run checks out a commit with --force, so a change in the checkout would be lost. The run needs a clean
    # tree, and it puts back the first commit or branch at the end.
    if git(repo, "status", "--porcelain", "--untracked-files=no").strip():
        print("The checkout has changes to tracked files. Commit or stash them first.")
        return 2
    start = git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if start == "HEAD":
        start = git(repo, "rev-parse", "HEAD").strip()

    problems = []
    try:
        for path, items in files.items():
            print(f"quick file: {path}")
            for item in items:
                if item.text_only:
                    print(f"{item.name}: text only, skipped")
                    continue
                found = check_item(repo, item)
                problems += found
                print(f"{item.name}: " + ("held" if not found else "does not hold"))
    finally:
        git(repo, "checkout", "-q", "--force", start)

    for problem in problems:
        print(f"FAIL {problem}")
    print(f"{len(problems)} problems." if problems else "Each item held.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
