"""
AT-52 evidence script: it prints the count of teams of each Path.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
c = Counter()
for page in sim["pages"].values():
    for fs in page["finishes"].values():
        for f in fs:
            for p in f["paths"]:
                c[len(p["conditions"])] += 1
print(f"Paths by count of teams named: {dict(sorted(c.items()))}")
print(f"Paths that name more than 3 teams: {sum(v for k, v in c.items() if k > 3)}")
