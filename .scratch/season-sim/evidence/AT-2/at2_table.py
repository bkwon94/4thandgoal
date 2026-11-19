"""Print the playoff odds of each team in week 10 of rankings.json beside its playoff odds in week-10/sim.json."""
import json
import sys

rankings, sim = (json.load(open(p)) for p in sys.argv[1:3])
rows = {r["roster_id"]: r for r in next(w for w in rankings["weeks"] if w["week"] == 10)["rows"]}
print(f"| roster | team | rankings.json week 10 playoff | sim.json playoff | rankings.json bye | sim.json bye | equal |")
print("| --- | --- | --- | --- | --- | --- | --- |")
same = 0
for rid in sorted(rows):
    r, t = rows[rid]["odds"], sim["teams"][str(rid)]
    eq = r["playoff"] == t["playoff"] and r["bye"] == t["bye"]
    same += eq
    print(f"| {rid} | {rows[rid]['name']} | {r['playoff']} | {t['playoff']} | {r['bye']} | {t['bye']} | {eq} |")
print(f"\nteams in week 10 of rankings.json: {len(rows)}; teams with equal playoff and bye odds: {same}")
