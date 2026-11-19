"""Check the "about" flag of each result of each page of a week sim file.
A result is "about" when its chance times effective_runs is under 400."""
import json, sys
body = json.load(open(sys.argv[1]))
eff = body["effective_runs"]
counts = {"under 400, about true": 0, "under 400, about false": 0, "400 or more, about false": 0, "400 or more, about true": 0}
print(f"effective_runs {eff}")
for rid, page in sorted(body["pages"].items(), key=lambda kv: int(kv[0])):
    n = 0
    for week in page["weeks"]:
        for r in week["results"]:
            small = r["chance"] / 100 * eff < 400
            key = ("under 400" if small else "400 or more") + (", about true" if r["about"] else ", about false")
            counts[key] += 1
            n += 1
            print(f"page {rid} week {week['week']} {r['game']} {r['median']}: chance {r['chance']} % x {eff} = "
                  f"{r['chance'] / 100 * eff:.0f} runs, about {r['about']}")
    print(f"page {rid}: {n} results")
for key, value in counts.items():
    print(f"{key}: {value}")

# The ladder rows of each page carry a chance and an "about" flag too, so the same rule is checked on them.
ladder = {"under 400, about true": 0, "under 400, about false": 0, "400 or more, about false": 0, "400 or more, about true": 0}
print("ladder rows:")
for rid, page in sorted(body["pages"].items(), key=lambda kv: int(kv[0])):
    for row in page["ladder"] or []:
        small = row["chance"] / 100 * eff < 400
        key = ("under 400" if small else "400 or more") + (", about true" if row["about"] else ", about false")
        ladder[key] += 1
        print(f"page {rid} ladder {row['more_wins']} more wins: chance {row['chance']} % x {eff} = "
              f"{row['chance'] / 100 * eff:.0f} runs, about {row['about']}")
for key, value in ladder.items():
    print(f"ladder {key}: {value}")
