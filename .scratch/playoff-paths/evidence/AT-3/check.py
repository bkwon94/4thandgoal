"""
AT-3 evidence script: it prints the Goal fields of each page of the cpc week 11 sim file.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
for rid in ("6", "1"):
    print(f"{names[rid]} (roster {rid}) goals: {json.dumps(sim['pages'][rid]['goals'])}")
print("pages:", len(sim["pages"]))
for rid, page in sim["pages"].items():
    print(f"roster {rid:>2} {names[rid]:<24} goal keys {list(page['goals'])} spot odds {page['goals']['spot']['odds']} teams.playoff {sim['teams'][rid]['playoff']}")
