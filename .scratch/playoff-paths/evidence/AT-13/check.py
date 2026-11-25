"""
AT-13 evidence script: it prints the What-if odds of the Week plan beside its Try it odds.
Run it from the root of a checkout of the branch, after the sim step of the week.
"""
import json
from pathlib import Path
from sim.season import SetResult, SimResult, rerun
SIM = Path("clients/cpc/build/2026/week-11/sim.json")
sim = json.loads(SIM.read_text(encoding="utf-8"))
rid = next(r for r, n in sim["names"].items() if n == "Bo Girds")
plan = next(f for f in sim["pages"][rid]["finishes"]["spot"] if f["more_wins"] == 4)["paths"][0]["plan"]
held = [SetResult(week=w["week"], game=w["game"], median=w["median"]) for w in plan["weeks"]]
print(f"file: {SIM}")
print(f"rerun(week-11/sim.json, you={rid}, set={[r.model_dump() for r in held]})")
result = rerun(SimResult.model_validate(sim), you=int(rid), set_results=held, pages=[int(rid)])
odds = result.pages[int(rid)].goals["spot"].odds
print(f"Try it odds of the plan: {plan['odds']}")
print(f"What-if odds of the spot Goal: {odds} (runs {result.runs}, effective runs {result.effective_runs})")
print(f"difference: {round(abs(odds - plan['odds']), 2)} points")
