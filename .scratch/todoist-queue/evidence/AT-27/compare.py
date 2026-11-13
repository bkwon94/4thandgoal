"""
Compares each Status line on todoist-queue with its approved line: the audit proposal, changed by the Approved heading.
Run from the repo root: python3 .scratch/todoist-queue/evidence/AT-27/compare.py
"""
import re
from pathlib import Path

STATUS = re.compile(r"^(?:\*\*)?Status:(?:\*\*)?[ \t]*(\S*)", re.MULTILINE)
LINE = re.compile(r"^- `([^`]+)` \(now: ([^)]*)\) → (done|wontfix|open)(?: (\S+?))?,", re.MULTILINE)
# The Approved heading of audit.md: the six kept tickets stay open, each other proposed open closes as wontfix,
# and site-pages 09 stays open as ready-for-agent in place of done.
KEPT = {
    ".scratch/tone/issues/10-remove-names-is-case-sensitive.md",
    ".scratch/week-8-fixes/issues/08-the-scoring-component-fact-names-the-component.md",
    ".scratch/manager-pages/site/issues/11-the-bench-sentence-and-the-odds-change-words.md",
    ".scratch/site-pages/issues/09-home-test-class-name.md",
    ".scratch/manager-pages/pipeline/issues/12-drop-awards-from-managers-entry.md",
    ".scratch/modular/pipeline/issues/20-remove-the-chart-parameter-of-context.md",
}


def approved(path, result, value):
    if path == ".scratch/site-pages/issues/09-home-test-class-name.md":
        return "ready-for-agent"
    if result == "open":
        return value if path in KEPT else "wontfix"
    return result


audit = Path(".scratch/todoist-queue/audit.md").read_text()
rows = LINE.findall(audit)
mismatch = 0
counts = {}
for path, now, result, value in rows:
    want = approved(path, result, value)
    match = STATUS.search(Path(path).read_text())
    line = match.group(0) if match else "(no Status line)"
    got = (match.group(1) if match else "").lower().rstrip(".,;:")
    ok = got == want
    mismatch += not ok
    counts[got] = counts.get(got, 0) + 1
    print(f"{'match' if ok else 'MISMATCH'}  {path}: approved {want}; file has `{line}`")
print(f"\n{len(rows)} tickets, {mismatch} mismatches. Status counts on todoist-queue: {counts}")
