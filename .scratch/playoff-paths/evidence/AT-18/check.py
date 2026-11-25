"""
AT-18 evidence script: it prints the tiebreak gap of each page beside a hand check.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
records = {int(r): v for r, v in sim["records"].items()}
order = sorted(records, key=lambda r: (-records[r][0], -records[r][2], -records[r][3], r))
place = {r: n for n, r in enumerate(order, start=1)}
edges = {"spot": 6, "bye": 2, **{f"seed-{n}": n for n in range(1, 7)}}
print("order:", [(r, records[r][0], records[r][2]) for r in order])
shown = no_close = 0
for rid, page in sim["pages"].items():
    you = int(rid)
    for goal, card in page["week_card"]["goals"].items():
        e = edges[goal]
        close = [o for o in order if o != you and (place[o] <= e) != (place[you] <= e) and abs(records[o][0] - records[you][0]) <= 1 and abs(records[o][2] - records[you][2]) <= 50]
        gap = card["tiebreak"]
        st = page["goals"][goal]["status"]
        if gap is not None:
            shown += 1
            print(f"gap: {names[rid]} {goal} status {st}: {json.dumps(gap)}; close teams by hand {close}")
        elif close and st == "open":
            print(f"no gap but close by hand: {names[rid]} {goal} close {close}")
        else:
            no_close += 1
print(f"gaps shown {shown}; Goals with no gap {no_close}")
