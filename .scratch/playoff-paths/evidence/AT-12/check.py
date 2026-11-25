"""
AT-12 evidence script: it prints the Week plan of the first Path of the 4-2 Finish of Bo Girds.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
rid = next(r for r, n in names.items() if n == "Bo Girds")
page = sim["pages"][rid]
f = next(f for f in page["finishes"]["spot"] if f["more_wins"] == 4)
path = f["paths"][0]
print(f"first Path of the 4-2 Finish of Bo Girds: conditions {path['conditions']} odds {path['odds']}")
plan = path["plan"]
print("plan:", json.dumps(plan, ensure_ascii=False, indent=1))
print("score_to_beat:", json.dumps(page["score_to_beat"], ensure_ascii=False))
