"""
AT-24 evidence script: it asks the local evidence API for the Suggestions of Bo Girds with the order of Tuesday.
It saves the request and the response beside it, and prints the 3 picks.
"""
import json, sys, urllib.request
from pathlib import Path
base, here = sys.argv[1], Path(__file__).parent
TUESDAY = ["week_recap", "last_matchup", "power_rankings", "playoff_race", "next_matchup", "your_season",
           "leaders_trades", "waiver_targets", "stack_up", "weak_spots", "sell_high", "trade_ideas", "trade_check"]
body = {"roster_id": 6, "order": TUESDAY, "opened": {}}
req = urllib.request.Request(f"{base}/clients/cpc/suggestions", data=json.dumps(body).encode(), method="POST",
                             headers={"Content-Type": "application/json", "X-League-Passphrase": "localtest"})
with urllib.request.urlopen(req, timeout=180) as res:
    raw = res.read()
    print(f"POST {base}/clients/cpc/suggestions {json.dumps(body)} -> {res.status}")
(here / "request.json").write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
(here / "response.json").write_bytes(raw)
r = json.loads(raw)
print("picks:", r["picks"])
print("urgent:", r["urgent"], "head_start:", r["head_start"])
print("fact of playoff_race:", r["facts"].get("playoff_race"))
print("lifts:", json.dumps(r["lifts"]))
