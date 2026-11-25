"""
AT-15 evidence script: it prints the root-for rows of the 4 week 12 results of Bo Girds.
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
print(f"Bo Girds week {card['week']} results {[(r['game'], r['median']) for r in card['results']]}")
print(f"other games of week 12: {[p for p in sim['schedule']['12'] if 6 not in p]}")
spot = card["goals"]["spot"]
for result, value, rows in zip(card["results"], spot["odds"], spot["root_for"]):
    print(f"== {result['game']} {result['median']} -> {value}%: {len(rows)} rows")
    for r in rows:
        lift = round(r["odds"] - r["other"], 2)
        print(f"  {names[str(r['winner'])]} beats {names[str(r['loser'])]} -> {r['odds']}%; other result -> {r['other']}%; lift {lift}; fields {json.dumps(r)}")
