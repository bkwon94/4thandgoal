"""
AT-9 evidence script: it prints the repeated Paths of each Finish.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
fin = rep = 0
for rid, page in sim["pages"].items():
    for g, fs in page["finishes"].items():
        for f in fs:
            sets = [frozenset((c["roster_id"], tuple(c["record"])) for c in p["conditions"]) for p in f["paths"]]
            if sets:
                fin += 1
            if len(sets) != len(set(sets)):
                rep += 1
                print(f"repeat: {names[rid]} {g} {f['more_wins']}")
print(f"Finishes with Paths: {fin}; Finishes with a repeated Path: {rep}")
