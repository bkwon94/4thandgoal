"""
Prints the apps that the check must run for the changed files since the merge base of a ref and HEAD, on one line.
It selects by workspace member: a changed member, and each member that needs it, through both languages of a package.
"""
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

# A change to one of these files, or to .github/, can change any member, so it selects every app.
ROOT_FILES = ["pyproject.toml", "uv.lock", "pnpm-workspace.yaml", "pnpm-lock.yaml", "Makefile"]
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


def select_apps(root: Path, files: list[str]) -> list[str]:
    """The apps to check for the changed files, in APP_ORDER.

    A path outside apps/ and packages/ selects every app, so a root file is never under-tested.
    A path in a package selects both of its languages, because the published file joins them (ADR 0011).
    """
    if not files:
        return []
    owners = {_owner(path) for path in files}
    if None in owners:
        return list(APP_ORDER)
    members = {**_python_members(root), **_site_members(root)}
    owner_of = {name: _owner(f"{folder}/x") for name, (folder, _) in members.items()}
    selected = {name for name, owner in owner_of.items() if owner in owners}
    # Add each member that needs a selected member, until no member is left to add.
    while True:
        more = {name for name, (_, needs) in members.items() if needs & selected} - selected
        if not more:
            break
        selected |= more
    apps = {str(owner_of[name]).removeprefix("apps/") for name in selected if str(owner_of[name]).startswith("apps/")}
    return [app for app in APP_ORDER if app in apps]


def _changed_files(ref: str) -> list[str]:
    """Committed, staged, unstaged, and new files since the merge base of the ref and HEAD."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout

    base = git("merge-base", ref, "HEAD").strip()
    files = git("diff", "--name-only", base).splitlines() + git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted(set(files))


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    apps = select_apps(root, _changed_files(sys.argv[1]))
    if apps:
        print(" ".join(apps))


if __name__ == "__main__":
    main()
