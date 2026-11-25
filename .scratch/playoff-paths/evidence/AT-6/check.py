"""
AT-6 evidence script: it prints the Finish list of Bo Girds for a playoff spot.
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
print(f"Bo Girds roster {rid} record {page['record']}")
fs = page["finishes"]["spot"]
for f in fs:
    print(f"{f['more_wins']}-{6 - f['more_wins']}  final {f['record'][0]}-{f['record'][1]}  chance {f['chance']}  odds {f['odds']}  case {f['case']}  paths {len(f['paths'])}")
print(f"Finishes: {len(fs)}, sum of chances {round(sum(f['chance'] for f in fs), 2)}")
