"""
AT-26 evidence script, the pipeline part: it prints the race Answer of Bo Girds in the cpc week 11 topics.json.
Run it from the root of a checkout of the branch, after page-json of the week.
"""
import json
from pathlib import Path
TOPICS = Path("clients/cpc/build/2026/week-11/topics.json")
d = json.loads(TOPICS.read_text(encoding="utf-8"))
print(f"file: {TOPICS} (week {d['week']}, schema {d['schema_version']})")
teams = d["teams"]
team = teams["6"] if isinstance(teams, dict) else next(t for t in teams if t.get("roster_id") == 6)
answers = team["answers"] if isinstance(team, dict) and "answers" in team else team
race = next(a for a in answers if a["topic"] == "playoff_race")
print("Bo Girds playoff_race Answer:")
print(json.dumps(race, ensure_ascii=False, indent=1))
block = race["block"]
print(f"fact: {race['fact']}; block kind {block['kind']}; finishes {len(block.get('finishes') or [])}; pill {block.get('pill')}")
for f in block.get("finishes") or []:
    print(f"  Finish {f['name']} ends {f['record']}: chance {f['chance']}%, odds {f['odds']}%")
