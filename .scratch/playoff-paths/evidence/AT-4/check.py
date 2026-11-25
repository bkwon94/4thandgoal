"""
AT-4 evidence script: it prints the odds of each Goal and the open Goal of each cpc week 11 page.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
G = ["seed-1", "bye", "spot"]
print(f"{'team':<24} {'W-L':<7} {'seed-1':>6} {'bye':>5} {'spot':>5}  open_goal")
for rid, page in sim["pages"].items():
    o = page["goals"]
    w, l = sim["records"][rid][:2]
    print(f"{names[rid]:<24} {w}-{l:<5} {o['seed-1']['odds']:>6} {o['bye']['odds']:>5} {o['spot']['odds']:>5}  {page['open_goal']}")
