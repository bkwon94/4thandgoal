"""
Prints the scope of a diff: "records only" or "change of code", and the heavy checks that the diff selects.
The heavy checks are the smoke run, the rebuild, and the re-run of the loop (ADR 0037).
"""
import subprocess
import sys
from pathlib import PurePosixPath

# A diff outside these paths changes code. A Markdown file in a folder of code is code, because a rule test may read it.
RECORD_FOLDERS = (".scratch", "docs")
# The order of the checks on the line.
CHECK_ORDER = ["smoke", "rebuild", "rerun"]


def is_record(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return parts[0] in RECORD_FOLDERS or (len(parts) == 1 and path.endswith(".md"))


def _checks_of(path: str) -> set[str]:
    """The checks that one path of code selects. A path of no known owner selects each check, so none is skipped."""
    parts = PurePosixPath(path).parts
    if parts[0] == "apps" and len(parts) > 2:
        if parts[1] == "pipeline":
            return {"rebuild", "rerun"}
        return {"smoke", "rerun"}
    if parts[0] == "packages" and len(parts) > 2:
        # A package holds Python for the pipeline and a site side for the pages.
        if parts[2] == "python":
            return {"rebuild", "rerun"}
        return {"smoke", "rerun"}
    return {"smoke", "rebuild", "rerun"}


def select(files: list[str]) -> tuple[str, list[str]]:
    """The scope line and the checks, in CHECK_ORDER, for the changed files."""
    code = [path for path in files if not is_record(path)]
    if not code:
        return "records only", []
    selected = set().union(*(_checks_of(path) for path in code))
    return "change of code", [check for check in CHECK_ORDER if check in selected]


def main() -> None:
    base, head = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    merge_base = subprocess.run(["git", "merge-base", base, head], check=True, capture_output=True,
                                text=True).stdout.strip()
    files = subprocess.run(["git", "diff", "--name-only", "--no-renames", merge_base, head], check=True,
                           capture_output=True, text=True).stdout.splitlines()
    scope, checks = select(files)
    print(scope)
    print(f"selects: {' '.join(checks) or 'none'}")


if __name__ == "__main__":
    main()
