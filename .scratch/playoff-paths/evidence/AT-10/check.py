"""
AT-10 evidence script: it prints the Paths of each sure or hopeless Finish.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
n_hi = n_lo = with_paths = 0
for rid, page in sim["pages"].items():
    for g, fs in page["finishes"].items():
        for f in fs:
            if f["odds"] >= 99.5 or f["odds"] < 0.5:
                n_hi += f["odds"] >= 99.5
                n_lo += f["odds"] < 0.5
                with_paths += bool(f["paths"])
print(f"Finishes with odds of 99.5 or more: {n_hi}; under 0.5: {n_lo}; of those, Finishes with a Path: {with_paths}")
by_case = Counter((f["case"], bool(f["paths"])) for p in sim["pages"].values() for fs in p["finishes"].values() for f in fs)
print("Finishes by (case, has a Path):", dict(sorted(by_case.items())))
odds_sure = Counter(f["odds"] for p in sim["pages"].values() for fs in p["finishes"].values() for f in fs if f["case"] == "sure")
odds_none = Counter(f["odds"] for p in sim["pages"].values() for fs in p["finishes"].values() for f in fs if f["case"] == "none")
print("odds field of the sure Finishes:", dict(odds_sure), "; of the none Finishes:", dict(odds_none))
print("Finishes by case:", dict(Counter(f["case"] for p in sim["pages"].values() for fs in p["finishes"].values() for f in fs)))
