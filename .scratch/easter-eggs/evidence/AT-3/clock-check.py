"""
AT-3 of easter-eggs: the real API app with the real CPC client, a temp egg store, and the clock of the hunt set by hand.
The real clock is outside the window 23:00-00:00 ET, so the script sets the clock of the app and sends each check over HTTP.
"""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from cornerstone_api.app import create_app, load_clients
from cornerstone_api.settings import Settings

ET = ZoneInfo("America/New_York")
REPO = Path(__file__).resolve().parents[4]
T2 = {"page": "/2026/week-08/", "target": "number-median", "action": "tap2", "conditions": {"clock": "23:00-00:00"}}
CHECK = {"page": "/2026/week-08/", "target": "number-median", "action": "tap2", "conditions": {"theme": "dark"}}

with tempfile.TemporaryDirectory() as eggs:
    clients = load_clients(REPO)
    settings = Settings(passphrases={c.slug: "localtest" for c in clients}, repo=REPO, result_cache_dir=Path(eggs) / "results",
                        commissioner_keys={c.slug: "localkey" for c in clients if "eggs" in c.values.packages},
                        eggs_dir=Path(eggs), rate_limit_per_minute=600)
    api = TestClient(create_app(settings, clients))
    print(f"The app: the real clients {[c.slug for c in clients]}, the temp egg store {eggs}/cpc.sqlite.")
    drop = {"week": 9, "eggs": [T2]}
    answer = api.post("/clients/cpc/eggs/drop", json=drop, headers={"X-Commissioner-Key": "localkey"})
    print(f"POST /clients/cpc/eggs/drop {json.dumps(drop)}")
    print(f"  -> HTTP {answer.status_code} {answer.text}")
    hunt = api.app.state.hunts["cpc"]
    for at in (datetime(2026, 11, 10, 22, 59, tzinfo=ET), datetime(2026, 11, 10, 23, 30, tzinfo=ET),
               datetime(2026, 11, 11, 0, 0, tzinfo=ET)):
        hunt.clock = lambda at=at: at
        answer = api.post("/clients/cpc/eggs/check", json=CHECK)
        print(f"clock of the hunt set to {at.isoformat()} ({at.strftime('%H:%M %Z')})")
        print(f"  POST /clients/cpc/eggs/check {json.dumps(CHECK)}")
        print(f"  -> HTTP {answer.status_code} {answer.text}")
