"""
AT-7 evidence script: it prints the Finish lists and the week card medians of the norcal week 10 sim file.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json
from pathlib import Path
SIM = Path("clients/norcal/build/2026/week-10/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, median_game {sim['parameters']['median_game']}, weeks left {len(sim['schedule'])})")
for rid, page in sim["pages"].items():
    runs = {g: [f["more_wins"] for f in fs] for g, fs in page["finishes"].items()}
    medians = [r["median"] for r in page["week_card"]["results"]]
    print(f"roster {rid:>2} {names[rid]:<24} more_wins by goal {runs}  week card result medians {medians}")
rid = next(iter(sim["pages"]))
print(f"Finish list of {names[rid]} for the spot:")
for f in sim["pages"][rid]["finishes"]["spot"]:
    print(f"  {f['more_wins']}-{4 - f['more_wins']} final {f['record']} chance {f['chance']} odds {f['odds']} case {f['case']}")
