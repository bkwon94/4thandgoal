"""
AT-15 reading script: it prints each week 12 root-for row of Bo Girds for the spot Goal, with the mark that each row gets.
The mark follows the rule of the code: a row whose two odds differ by under ROOT_FOR_LIFT points is "Doesn't matter".
"""
import json
from pathlib import Path
from sim.tunables import ROOT_FOR_LIFT
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
names = sim["names"]
card = sim["pages"]["6"]["week_card"]
spot = card["goals"]["spot"]
others = [p for p in sim["schedule"]["12"] if 6 not in p]
print(f"file: {SIM}; ROOT_FOR_LIFT = {ROOT_FOR_LIFT}")
print(f"other head-to-head games of week 12: {len(others)}: " + "; ".join(f"{names[str(a)]} vs {names[str(b)]}" for a, b in others))
marked = 0
for result, value, rows in zip(card["results"], spot["odds"], spot["root_for"]):
    games = {frozenset((r["winner"], r["loser"])) for r in rows}
    print(f"== result {result['game']} {result['median']}: Bo Girds at {value}%; {len(rows)} rows; "
          f"rows cover the {len(others)} other games: {games == {frozenset(p) for p in others}}")
    for r in rows:
        lift = r["odds"] - r["other"]
        mark = "Doesn't matter" if lift < ROOT_FOR_LIFT else "matters"
        marked += mark == "Doesn't matter"
        print(f"  {names[str(r['winner'])]} wins -> {r['odds']}%; {names[str(r['loser'])]} wins -> {r['other']}%; "
              f"lift {lift}; mark: {mark}")
print(f"rows marked Doesn't matter: {marked}")
