"""
AT-12 evidence script: it prints the Week plan of the first Path of the 4-2 Finish of Bo Girds, one line per row.
Each line names the week, the opponent, the result, the Score to beat of the row, and the games to root for.
"""
import json
from pathlib import Path
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
print(f"file: {SIM} (week {sim['week']}, {sim['runs']} runs)")
rid = next(r for r, n in names.items() if n == "Bo Girds")
page = sim["pages"][rid]
finish = next(f for f in page["finishes"]["spot"] if f["more_wins"] == 4)
path = finish["paths"][0]
plan = path["plan"]
print(f"Bo Girds roster {rid}; 4-2 Finish ends {finish['record']}; first Path {path['conditions']} odds {path['odds']}")
print(f"plan: {len(plan['weeks'])} rows; any_order {plan['any_order']}; Try it odds {plan['odds']}")
for row in plan["weeks"]:
    roots = "; ".join(f"{names[str(g['winner'])]} beats {names[str(g['loser'])]} -> {g['odds']}%" for g in row["root_for"])
    print(f"week {row['week']} vs {names[str(row['opponent'])]} (roster {row['opponent']}): {row['game']}, {row['median']} the median; "
          f"win {row.get('win')}, win_sure {row.get('win_sure')}, median_score {row.get('median_score')}, "
          f"median_sure {row.get('median_sure')}; root for {len(row['root_for'])}: {roots}")
    print(f"  keys of the row: {sorted(row)}")
print("plan JSON:", json.dumps(plan, ensure_ascii=False))
