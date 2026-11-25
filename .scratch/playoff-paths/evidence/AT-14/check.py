"""
AT-14 evidence script: it prints the Score to beat of Bo Girds.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
page = sim["pages"]["6"]
print(f"{names['6']} week card week {page['week_card']['week']} opponent {page['week_card']['opponent']} ({names[str(page['week_card']['opponent'])]})")
for s in page["score_to_beat"]:
    print(json.dumps(s, ensure_ascii=False), f"opponent name {names[str(s['opponent'])]}")
