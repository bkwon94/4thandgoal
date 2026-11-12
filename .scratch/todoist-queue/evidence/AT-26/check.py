"""
Compares audit.md with the open tickets of main at the start of the spec (17f45a15), and checks each named commit.
Run from the repo root: python3 .scratch/todoist-queue/evidence/AT-26/check.py
"""
import re
import subprocess
from collections import Counter

START = "17f45a15"
STATUS = re.compile(r"^(?:\*\*)?Status:(?:\*\*)?[ \t]*(\S*)", re.MULTILINE)
LINE = re.compile(r"^- `([^`]+)` \(now: ([^)]*)\) → (done|wontfix|open)(?: (\S+?))?,", re.MULTILINE)
HEX = re.compile(r"\b(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


files = git("ls-tree", "-r", "--name-only", START, ".scratch").stdout.split()
tickets = [f for f in files if re.search(r"/issues/\d+-[^/.]+\.md$", f)]
open_tickets = []
for path in tickets:
    match = STATUS.search(git("show", f"{START}:{path}").stdout)
    word = (match.group(1) if match else "").lower().rstrip(".,;:")
    if word not in ("done", "wontfix"):
        open_tickets.append(path)
print(f"Open tickets of main at {START}: {len(open_tickets)}")
for path in open_tickets:
    print(f"  {path}")

audit = open(".scratch/todoist-queue/audit.md").read()
# Each line sits under the heading of its feature.
lines = []
feature = None
for row in audit.splitlines():
    if row.startswith("## "):
        feature = row[3:].strip()
    match = LINE.match(row)
    if match:
        lines.append((feature, *match.groups(), row))
print(f"\nAudit lines: {len(lines)}")
count = Counter(path for _, path, *_ in lines)
missing = [p for p in open_tickets if count[p] == 0]
twice = [p for p, n in count.items() if n > 1]
extra = [p for p in count if p not in open_tickets]
wrong_feature = [path for feat, path, *_ in lines if path.split("/")[1] != feat]
no_value = [path for _, path, now, result, value, _ in lines if result != "wontfix" and not value]
print(f"Open tickets with no audit line: {missing}")
print(f"Tickets with more than one audit line: {twice}")
print(f"Audit lines for a ticket that is not open on main: {extra}")
print(f"Audit lines under the wrong feature heading: {wrong_feature}")
print(f"done or open lines with no commit or label: {no_value}")
print(f"Results: {dict(Counter(result for _, _, _, result, _, _ in lines))}")
wontfix_no_reason = [path for _, path, _, result, _, row in lines if result == "wontfix" and len(row.split("→", 1)[1].split(",", 1)[1].strip()) < 20]
print(f"wontfix lines with no reason: {wontfix_no_reason}")

done_commits = sorted({value for _, _, _, result, value, _ in lines if result == "done"})
named = sorted(set(HEX.findall(audit)) | set(done_commits))
print(f"\ngit cat-file -e on each commit of a done line ({len(done_commits)}) and each other named hash ({len(named)} in all):")
bad = []
for sha in named:
    ok = git("cat-file", "-e", f"{sha}^{{commit}}").returncode == 0
    print(f"  {sha} {'exists' if ok else 'MISSING'}{' (done line)' if sha in done_commits else ''}")
    if not ok:
        bad.append(sha)
print(f"Missing commits: {bad}")
