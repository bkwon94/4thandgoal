"""
Prints the apps and packages to check for staged files or for changes since the merge base of a ref and HEAD.
It selects a changed workspace member and each member that needs it, in both languages.
"""
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

# A change to one of these files, or to .github/, can change any member, so it selects every app.
ROOT_FILES = ["pyproject.toml", "uv.lock", "pnpm-workspace.yaml", "pnpm-lock.yaml", "Makefile"]
# The members whose tests read a root path, by the start of the path. The longest start wins, and a path with no start
# here selects every member. The tracker rule of the site and of the pipeline reads .scratch/ and docs/agents/state.md.
# No test reads the other files under docs/, such as the ADRs.
ROOT_READERS = {
    ".scratch/": ("apps/site", "apps/pipeline"),
    "docs/": (),
    "docs/agents/state.md": ("apps/site", "apps/pipeline"),
}
# The rule that allows a rules file only at the repo root reads these names in every folder, so the site and the
# pipeline read them under .scratch/ and docs/ too.
RULES_FILES = ("CLAUDE.md", "AGENTS.md")
# The order of the apps on the line, which is the order the root Makefile runs them in. The site runs first.
APP_ORDER = ["site", "pipeline", "api"]

PNPM_GLOB = re.compile(r"""^\s*-\s*["']?([^"'#\s]+)["']?""")


def _python_members(root: Path) -> dict[str, tuple[Path, set[str]]]:
    """Each uv member by name: its folder, and the names of the workspace members it lists."""
    globs = tomllib.loads((root / "pyproject.toml").read_text())["tool"]["uv"]["workspace"]["members"]
    members: dict[str, tuple[Path, set[str]]] = {}
    for pattern in globs:
        for folder in sorted(root.glob(pattern)):
            project = tomllib.loads((folder / "pyproject.toml").read_text())
            sources = project.get("tool", {}).get("uv", {}).get("sources", {})
            needs = {name for name, source in sources.items() if source.get("workspace")}
            members[project["project"]["name"]] = (folder.relative_to(root), needs)
    return members


def _site_members(root: Path) -> dict[str, tuple[Path, set[str]]]:
    """Each pnpm member by name: its folder, and the names of the workspace members it lists."""
    lines = (root / "pnpm-workspace.yaml").read_text().splitlines()
    globs = [match.group(1) for line in lines if (match := PNPM_GLOB.match(line))]
    members: dict[str, tuple[Path, set[str]]] = {}
    for pattern in globs:
        for folder in sorted(root.glob(pattern)):
            package = json.loads((folder / "package.json").read_text())
            listed = {**package.get("dependencies", {}), **package.get("devDependencies", {}),
                      **package.get("peerDependencies", {})}
            needs = {name for name, spec in listed.items() if str(spec).startswith("workspace:")}
            members[package["name"]] = (folder.relative_to(root), needs)
    return members


def _owner(path: str) -> str | None:
    """The folder that owns a path, such as apps/site or packages/league. None for a path outside both."""
    parts = Path(path).parts
    if len(parts) > 2 and parts[0] in ("apps", "packages"):
        return f"{parts[0]}/{parts[1]}"
    return None


def _readers(path: str) -> tuple[str, ...] | None:
    """The folders of the members whose tests read a path outside apps/ and packages/. None means every member."""
    if Path(path).name in RULES_FILES and any(path.startswith(start) for start in ROOT_READERS):
        return ("apps/site", "apps/pipeline")
    starts = [start for start in ROOT_READERS if path.startswith(start)]
    return ROOT_READERS[max(starts, key=len)] if starts else None


def _selected_owners(root: Path, files: list[str]) -> set[str]:
    """The folders, such as apps/site or packages/league, of each member that the changed files select.

    A path outside apps/ and packages/ selects every member, so a root file is never under-tested. The exception is
    a path under a start of ROOT_READERS: it selects only the members whose tests read it, with no member that needs them.
    A path in a package selects both of its languages, because the published file joins them (ADR 0011).
    """
    if not files:
        return set()
    members = {**_python_members(root), **_site_members(root)}
    owner_of = {name: str(_owner(f"{folder}/x")) for name, (folder, _) in members.items()}
    readers = {path: _readers(path) for path in files if _owner(path) is None}
    if None in readers.values():
        return set(owner_of.values())
    owners = {_owner(path) for path in files} - {None}
    selected = {name for name, owner in owner_of.items() if owner in owners}
    # Add each member that needs a selected member, until no member is left to add.
    while True:
        more = {name for name, (_, needs) in members.items() if needs & selected} - selected
        if not more:
            break
        selected |= more
    return {owner_of[name] for name in selected} | {folder for found in readers.values() for folder in found}


def select_apps(root: Path, files: list[str]) -> list[str]:
    """The apps to check for the changed files, in APP_ORDER. A root file selects every app, except a path of ROOT_READERS."""
    apps = {owner.removeprefix("apps/") for owner in _selected_owners(root, files) if owner.startswith("apps/")}
    return [app for app in APP_ORDER if app in apps]


def select_packages(root: Path, files: list[str]) -> list[str]:
    """The packages to check for the changed files, by name in sorted order, such as league. Each package check runs
    both languages of the package. A root file selects every package, except a path of ROOT_READERS."""
    owners = _selected_owners(root, files)
    return sorted(owner.removeprefix("packages/") for owner in owners if owner.startswith("packages/"))


def _changed_files(ref: str) -> list[str]:
    """Committed, staged, unstaged, and new files since the merge base of the ref and HEAD."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout

    base = git("merge-base", ref, "HEAD").strip()
    files = git("diff", "--name-only", base).splitlines() + git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted(set(files))


def _staged_files() -> list[str]:
    """Read the commit index, with both paths of a rename and literal path bytes."""
    output = subprocess.check_output(["git", "diff", "--cached", "--name-only", "--no-renames", "-z"])
    return [os.fsdecode(path) for path in output.split(b"\0") if path]


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    files = _staged_files() if sys.argv[1] == "--staged" else _changed_files(sys.argv[1])
    # The apps come first, then the packages. The root Makefile tells them apart by the app names.
    checks = select_apps(root, files) + select_packages(root, files)
    if checks:
        print(" ".join(checks))


if __name__ == "__main__":
    main()
