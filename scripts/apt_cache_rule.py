"""
Fails on each workflow step that installs the system packages of Playwright with no earlier restore of the apt cache.
Run `python3 scripts/apt_cache_rule.py [root]`. The exit code is 1 when a step breaks the rule.
"""
import re
import sys
from pathlib import Path

# The workflows copy the .deb files of apt to this folder, and actions/cache keeps it, so a slow Ubuntu mirror cannot stall a job.
APT_CACHE = "~/.cache/apt-archives"

# Both commands download the system packages of the browsers from the Ubuntu mirror.
INSTALL_DEPS = re.compile(r"\binstall-deps\b|--with-deps\b")

JOB = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
STEPS = re.compile(r"^(\s+)steps:\s*$")
STEP_ITEM = re.compile(r"^(\s*)- ")


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def is_content(line: str) -> bool:
    """Return True for a line that YAML reads, so a blank line or a comment does not end a block."""
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#")


def steps_by_job(text: str):
    """Return {job: [step, ...]}, where a step is a list of (line number, line) pairs, in file order."""
    jobs: dict[str, list[list[tuple[int, str]]]] = {}
    in_jobs = False
    job = None
    steps_indent = None
    item_indent = None
    for number, line in enumerate(text.splitlines(), start=1):
        if not is_content(line):
            continue
        if indent_of(line) == 0:
            in_jobs = line.rstrip() == "jobs:"
            job = None
            continue
        if not in_jobs:
            continue
        match = JOB.match(line)
        if match:
            job = match.group(1)
            jobs[job] = []
            steps_indent = item_indent = None
            continue
        if job is None:
            continue
        match = STEPS.match(line)
        if match:
            steps_indent = len(match.group(1))
            item_indent = None
            continue
        if steps_indent is None:
            continue
        if indent_of(line) <= steps_indent and not STEP_ITEM.match(line):
            # A key at the level of steps: ends the list of steps.
            steps_indent = item_indent = None
            continue
        match = STEP_ITEM.match(line)
        if match and (item_indent is None or len(match.group(1)) == item_indent):
            item_indent = len(match.group(1))
            jobs[job].append([(number, line)])
        elif jobs[job]:
            jobs[job][-1].append((number, line))
    return jobs


def restores_apt_cache(step: list[tuple[int, str]]) -> bool:
    text = "\n".join(line for _, line in step)
    return "actions/cache" in text and APT_CACHE in text


def check_apt_cache(root: Path) -> list[str]:
    offenses = []
    folder = root / ".github" / "workflows"
    paths = sorted(folder.glob("*.yml")) + sorted(folder.glob("*.yaml")) if folder.is_dir() else []
    for path in paths:
        for job, steps in steps_by_job(path.read_text(errors="replace")).items():
            restored = False
            for step in steps:
                if restores_apt_cache(step):
                    restored = True
                    continue
                for number, line in step:
                    if INSTALL_DEPS.search(line) and not restored:
                        offenses.append(
                            f"{path.relative_to(root)}:{number} job {job} installs system packages"
                            f" with no earlier step that restores {APT_CACHE}: {line.strip()}"
                        )
    return offenses


if __name__ == "__main__":
    offenses = check_apt_cache(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    for offense in offenses:
        print(offense)
    # The re-run check of a quick file looks for a failure mark such as FAILED in the quoted output.
    if offenses:
        print(f"FAILED: {len(offenses)} steps install system packages with no apt cache.")
    sys.exit(1 if offenses else 0)
