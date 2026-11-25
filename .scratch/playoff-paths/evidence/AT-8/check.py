"""
AT-8 evidence script: it prints the counts of the Paths of the cpc week 11 sim file.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
def paths():
    for rid, page in sim["pages"].items():
        for goal, fs in page["finishes"].items():
            for f in fs:
                for p in f["paths"]:
                    yield rid, goal, f, p
ps = list(paths())
print(f"Paths: {len(ps)}")
print(f"teams per Path: {dict(sorted(Counter(len(p['conditions']) for *_, p in ps).items()))}")
print(f"fewest runs of a Path: {min(p['runs'] for *_, p in ps)}")
bad_size = [p for rid, _, f, p in ps if not 1 <= len(p["conditions"]) <= 3]
under = [(rid, g, f["more_wins"], p["odds"], len(p["conditions"]), f["case"]) for rid, g, f, p in ps if p["odds"] < 90 and len(p["conditions"]) < 3]
print(f"Paths outside 1 to 3 teams: {len(bad_size)}")
print(f"Paths with fewer than 3 teams and odds under 90: {len(under)}; their Finish cases: {dict(Counter(u[5] for u in under))}")
notrec = 0
for rid, g, f, p in ps:
    for c in p["conditions"]:
        w, l = sim["records"][str(c["roster_id"])][:2]
        more = c["record"][0] - w
        if not (c["record"][0] - w + c["record"][1] - l == 6 and more < 6):
            notrec += 1
print(f"conditions that are not a final record with at most 5 more wins: {notrec}")
print("condition keys:", sorted({k for *_, p in ps for c in p["conditions"] for k in c}))
print("example Path:", json.dumps(ps[0][3])[:600])
