"""
Fails on each retry setting of a test config, because a flaky test gets a fix of its cause or a delete, never a rerun.
Run `python3 scripts/retry_rule.py [root]`. The exit code is 1 when a file breaks the rule.
"""
import os
import re
import sys
from pathlib import Path

# Folders of dependencies, builds, and notes hold no config of ours.
SKIPPED = {"node_modules", ".git", ".venv", ".next", ".scratch", ".pnpm-store", ".claude", "dist", "build"}

# A retries value that is not a plain 0 counts as a retry, so a computed value fails too.
PLAYWRIGHT_RETRIES = re.compile(r"\bretries\s*:(?!\s*0\s*[,}\n])")
# Bun reads a retry from bunfig.toml (`retry = 2`), from a flag (`--retry=2`), and from a per-test option (`{ retry: 2 }`).
BUNFIG_RETRY = re.compile(r"^\s*retry\s*=(?!\s*0\s*(?:#.*)?$)", re.MULTILINE)
BUN_RETRY_FLAG = re.compile(r"--retry\b(?!=0\b)(?!\s+0\b)")
# Only a number counts here, because a site test can pass `retry: false` to its own app code.
BUN_TEST_RETRY_OPTION = re.compile(r"\bretry\s*:\s*(?!0\b)\d")
RERUNFAILURES = re.compile(r"pytest-rerunfailures|pytest_rerunfailures")

# The scripts that start `bun test` and the site test files, which sit in the site app and in the site side of a package.
BUN_SCRIPT_NAMES = {"package.json", "bun-test.mjs"}
SITE_TEST_NAME = re.compile(r"\.(test|spec)\.(ts|tsx|js|jsx|mjs|mts)$")

PYTEST_CONFIG_NAMES = {"pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini", "uv.lock"}


def is_site_path(relative: Path) -> bool:
    parts = relative.parts
    return parts[:2] == ("apps", "site") or (parts[:1] == ("packages",) and "site" in parts[2:-1])


def rules_for(name: str, relative: Path):
    """Return the (pattern, message) pairs that apply to a file."""
    rules = []
    if name.startswith("playwright.config."):
        rules.append((PLAYWRIGHT_RETRIES, "sets a Playwright retries value above 0"))
    if name == "bunfig.toml":
        rules.append((BUNFIG_RETRY, "sets a Bun retry above 0"))
    if name in BUN_SCRIPT_NAMES:
        rules.append((BUN_RETRY_FLAG, "passes a Bun --retry flag"))
    if SITE_TEST_NAME.search(name) and is_site_path(relative):
        rules.append((BUN_TEST_RETRY_OPTION, "sets a per-test retry option"))
    if name in PYTEST_CONFIG_NAMES or name == "pnpm-lock.yaml":
        rules.append((RERUNFAILURES, "names pytest-rerunfailures"))
    return rules


def check_retries(root: Path) -> list[str]:
    offenses = []
    for folder, names, files in os.walk(root):
        names[:] = [n for n in names if n not in SKIPPED]
        for name in files:
            path = Path(folder) / name
            rules = rules_for(name, path.relative_to(root))
            if not rules:
                continue
            text = path.read_text(errors="replace")
            for pattern, message in rules:
                if pattern.search(text):
                    offenses.append(f"{path.relative_to(root)} {message}")
    return sorted(offenses)


if __name__ == "__main__":
    offenses = check_retries(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    for offense in offenses:
        print(offense)
    sys.exit(1 if offenses else 0)
