"""
AT-16 evidence script: it prints the median rooting of the 4 week 12 results of Bo Girds.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
card = sim["pages"]["6"]["week_card"]
spot = card["goals"]["spot"]
for result, rows in zip(card["results"], spot["median_root"]):
    print(f"{result['game']} {result['median']}: {len(rows)} teams: " + "; ".join(f"{names[str(m['roster_id'])]} misses the median -> {m['odds']}%" for m in rows))
    print("  fields:", json.dumps(rows))
