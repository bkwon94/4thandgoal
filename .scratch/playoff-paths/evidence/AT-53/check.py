"""
AT-53 evidence script: it prints the board and the page keys of each playoff fixture file.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
for name in sorted(p.name for p in out.glob("week-sim-*.json")):
    sim = json.loads((out / name).read_text(encoding="utf-8"))
    pages = sim["pages"]
    fin = sum(bool(p.get("finishes")) for p in pages.values())
    goals = sum(bool(p.get("goals")) for p in pages.values())
    paths = sum(len(f.get("paths", [])) for p in pages.values() for fs in (p.get("finishes") or {}).values() for f in fs)
    print(f"{name}: week {sim['week']}, board {sim.get('board')}, pages with a Finish list {fin}, pages with goals {goals}, Paths {paths}")
    print(f"  keys of page 1: {sorted(pages['1'])}")
    print(f"  finishes of page 1: {pages['1'].get('finishes')}")
