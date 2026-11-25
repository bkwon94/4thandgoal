"""
AT-17 evidence script: it prints the brute-force check of the Clinch lines over every set of week 12 results.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json, sys
from pathlib import Path
from collections import Counter
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
"""A brute-force check over every set of results of week 12, by hand: the winner of each game and the 6 teams above
the median. A loser above the median needs its winner above it too."""
from itertools import combinations, product
def top(rid, wins, reach, k):
    others = [o for o in wins if o != rid]
    if sum(wins[o] + reach >= wins[rid] for o in others) < k:
        return "in"
    if sum(wins[o] > wins[rid] + reach for o in others) >= k:
        return "out"
    return "open"
def hand(rid, wins, reach, goal):
    return top(rid, wins, reach, 6 if goal == "spot" else 2)
def week_sets(pairs, rosters):
    for winners in product(*pairs):
        losers = [b if w == a else a for (a, b), w in zip(pairs, winners)]
        for above in combinations(rosters, len(rosters) // 2):
            up = set(above)
            if all(not (lo in up and wi not in up) for wi, lo in zip(winners, losers)):
                yield frozenset(winners), frozenset(up)
def fits(way, rid, winners, above):
    own = ((way["game"] is None or (rid in winners) == (way["game"] == "win"))
           and (way["median"] is None or (rid in above) == (way["median"] == "above")))
    return own and all(o["winner"] in winners if o["kind"] == "game" else (o["roster_id"] in above) == (o["median"] == "above") for o in way["others"])
rosters = sorted(int(r) for r in sim["records"])
wins = {int(r): rec[0] for r, rec in sim["records"].items()}
first = min(sim["schedule"], key=int)
sets = list(week_sets(sim["schedule"][first], rosters))
print(f"week {first}: {len(sets)} sets of results")
now, after = 2 * len(sim["schedule"]), 2 * (len(sim["schedule"]) - 1)
print("Clinch lines of the board:")
for row in sim["board"]:
    for line in row["clinch"]:
        print(f"  {names[str(row['roster_id'])]}: {json.dumps(line, ensure_ascii=False)}")
missing = wrong = checked = 0
for row in sim["board"]:
    rid = row["roster_id"]
    found = {(l["goal"], l["status"]): l for l in row["clinch"]}
    for goal in ("spot", "bye"):
        for status in ("in", "out"):
            line = found.get((goal, status))
            if hand(rid, wins, now, goal) != "open":
                print(f"{names[str(rid)]:<24} {goal} {status}: status already {hand(rid, wins, now, goal)} now; line {'present' if line else 'none'}")
                continue
            hits = {s for s in sets if hand(rid, {r: wins[r] + (r in s[0]) + (r in s[1]) for r in rosters}, after, goal) == status}
            note = ""
            if hits and line is None:
                missing += 1
                note = "a set exists and no line"
            if line is not None:
                for way in line["ways"]:
                    fit = {s for s in sets if fits(way, rid, *s)}
                    checked += 1
                    if not fit or not fit <= hits:
                        wrong += 1
                        note += f" way does not give the status: {way}"
            print(f"{names[str(rid)]:<24} {goal} {status}: sets that give it {len(hits)}; line {'with ' + str(len(line['ways'])) + ' ways' if line else 'none'} {note}")
print(f"ways checked {checked}; ways with a set that does not give the status {wrong}; teams with a set and no line {missing}")
