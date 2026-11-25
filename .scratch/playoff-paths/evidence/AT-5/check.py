"""
AT-5 evidence script: it prints the hand check of each status against a plain check on wins.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
"""The plain check on wins, by hand: Clinched when fewer than k other teams can reach the wins of the team, Out
when k other teams already hold more wins than the team can reach."""
GOALS = ["spot", "bye"] + [f"seed-{n}" for n in range(1, 7)]
def top(rid, wins, reach, k):
    others = [o for o in wins if o != rid]
    if sum(wins[o] + reach >= wins[rid] for o in others) < k:
        return "in"
    if sum(wins[o] > wins[rid] + reach for o in others) >= k:
        return "out"
    return "open"
def hand(rid, wins, reach, goal):
    if goal == "spot":
        return top(rid, wins, reach, 6)
    if goal == "bye":
        return top(rid, wins, reach, 2)
    k = int(goal.split("-")[1])
    t = top(rid, wins, reach, k)
    above = top(rid, wins, reach, k - 1) if k > 1 else "out"
    if t == "in" and above == "out":
        return "in"
    return "out" if t == "out" or above == "in" else "open"
wins = {int(r): rec[0] for r, rec in sim["records"].items()}
reach = 2 * len(sim["schedule"])
print(f"weeks left {len(sim['schedule'])}, most more wins {reach}")
same = differ = 0
for rid, page in sim["pages"].items():
    for g in GOALS:
        h = hand(int(rid), wins, reach, g)
        f = page["goals"][g]["status"]
        same += h == f
        differ += h != f
        print(f"{names[rid]:<24} wins {wins[int(rid)]:>2} {g:<7} file {f:<5} hand {h:<5} {'same' if h == f else 'DIFFERENT'}")
print(f"statuses: {same} same, {differ} different, of {same + differ}")
