"""Search the added lines of a git diff for runs of 8 or more lines copied from each Scrolltide prompt file.
Usage: git diff main | python3 -I scrolltide_search.py prompt1.md prompt2.md ..."""
import sys

RUN = 8

def norm(line):
    return " ".join(line.split())

added = [norm(l[1:]) for l in sys.stdin.read().splitlines() if l.startswith("+") and not l.startswith("+++")]
added = [l for l in added if l]
windows = {tuple(added[i:i + RUN]) for i in range(len(added) - RUN + 1)}
print(f"diff: {len(added)} added non-empty lines, {len(windows)} runs of {RUN}")
total = 0
for path in sys.argv[1:]:
    lines = [norm(l) for l in open(path, encoding="utf8").read().splitlines()]
    lines = [l for l in lines if l]
    hits = [i for i in range(len(lines) - RUN + 1) if tuple(lines[i:i + RUN]) in windows]
    total += len(hits)
    print(f"{path}: {len(lines)} non-empty lines, {len(hits)} matching runs of {RUN}")
    for i in hits:
        print("  match at prompt line", i + 1, "|", lines[i][:80])
print(f"total matching runs: {total}")
