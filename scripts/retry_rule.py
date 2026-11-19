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
VITEST_RETRY = re.compile(r"\bretry\s*:(?!\s*0\s*[,}\n])")
RERUNFAILURES = re.compile(r"pytest-rerunfailures|pytest_rerunfailures")

PYTEST_CONFIG_NAMES = {"pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini", "uv.lock"}


def rules_for(name: str):
    """Return the (pattern, message) pairs that apply to a file name."""
    rules = []
    if name.startswith("playwright.config."):
        rules.append((PLAYWRIGHT_RETRIES, "sets a Playwright retries value above 0"))
    if name.startswith("vitest.config."):
        rules.append((VITEST_RETRY, "sets a Vitest retry"))
    if name in PYTEST_CONFIG_NAMES or name == "pnpm-lock.yaml":
        rules.append((RERUNFAILURES, "names pytest-rerunfailures"))
    return rules


def check_retries(root: Path) -> list[str]:
    offenses = []
    for folder, names, files in os.walk(root):
        names[:] = [n for n in names if n not in SKIPPED]
        for name in files:
            rules = rules_for(name)
            if not rules:
                continue
            path = Path(folder) / name
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
