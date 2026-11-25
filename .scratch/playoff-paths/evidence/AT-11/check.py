"""
AT-11 evidence script: it prints each Finish whose best Path stays under 90%.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
rows = []
for rid, page in sim["pages"].items():
    for g, fs in page["finishes"].items():
        for f in fs:
            if f["paths"] and max(p["odds"] for p in f["paths"]) < 90:
                rows.append((rid, g, f))
print(f"Finishes whose best Path is under 90: {len(rows)}")
print("their Path counts:", dict(Counter(len(f["paths"]) for *_, f in rows)), "; their cases:", dict(Counter(f["case"] for *_, f in rows)))
print("path keys:", sorted(rows[0][2]["paths"][0]) if rows else None)
for rid, g, f in rows[:2]:
    print(f"example: {names[rid]} {g} {f['more_wins']} more wins: {json.dumps(f)[:900]}")
