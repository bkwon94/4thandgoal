"""Compare the odds of weeks 1 to 9 of two rankings.json files, row by row. The first file is read from git."""
import json
import subprocess
import sys

before = json.loads(subprocess.run(["git", "show", sys.argv[1]], capture_output=True, text=True, check=True).stdout)
after = json.load(open(sys.argv[2]))

def odds(body):
    return {w["week"]: {r["roster_id"]: r.get("odds") for r in w["rows"]} for w in body["weeks"]}

b, a = odds(before), odds(after)
changed = 0
for week in range(1, 10):
    rows = sorted(set(b.get(week, {})) | set(a.get(week, {})))
    diffs = [rid for rid in rows if b.get(week, {}).get(rid) != a.get(week, {}).get(rid)]
    changed += len(diffs)
    with_odds = sum(1 for rid in rows if a.get(week, {}).get(rid) is not None)
    print(f"week {week}: {len(rows)} rows, {with_odds} with odds, {len(diffs)} odds values changed")
    for rid in diffs:
        print(f"    roster {rid}: {b[week].get(rid)} -> {a[week].get(rid)}")
print(f"odds values changed in weeks 1 to 9: {changed}")
