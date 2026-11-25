"""
AT-20 and AT-21 evidence script: it calls the What-if route of the local evidence API twice for Bo Girds.
It saves each request and response beside it, cuts each response to the new fields, and diffs the two.
"""
import json, sys, time, urllib.request
from pathlib import Path
base, here = sys.argv[1], Path(__file__).parent
body = {"you": 6, "set": [{"week": 12, "game": "win", "median": "above"}]}
def call(n):
    req = urllib.request.Request(f"{base}/clients/cpc/sim/what-if", data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    started = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as res:
        raw = res.read()
        status = res.status
    print(f"call {n}: POST {base}/clients/cpc/sim/what-if {json.dumps(body)} -> {status}, {len(raw)} bytes, {time.monotonic() - started:.2f} s")
    (here / f"request-{n}.json").write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    (here / f"response-{n}.json").write_bytes(raw)
    return json.loads(raw)
a, b = call(1), call(2)
def cut(r):
    page = r["page"]
    return {"page": {"finishes": page["finishes"], "week_card": page["week_card"], "goals": page["goals"]},
            "board": r["board"]}
for n, r in ((1, a), (2, b)):
    (here / f"response-{n}-cut.json").write_text(json.dumps(cut(r), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("top keys:", sorted(a))
print("page keys:", sorted(a["page"]))
fin = a["page"]["finishes"]
paths = [p for fs in fin.values() for f in fs for p in f["paths"]]
plans = [p["plan"] for p in paths if p.get("plan")]
print(f"Finish list goals: {list(fin)}; spot Finishes {len(fin.get('spot', []))}; Paths {len(paths)}; Week plans {len(plans)}")
print("spot Finishes:", [(f["more_wins"], f["chance"], f["odds"], f["case"], len(f["paths"])) for f in fin["spot"]])
print("example Week plan:", json.dumps(plans[0]) if plans else None)
print("week card:", json.dumps(a["page"]["week_card"])[:800])
print(f"board rows {len(a['board'])}; keys of a row {sorted(a['board'][0])}")
print("board odds:", [(r["roster_id"], r["goals"]["spot"]["odds"], r["goals"]["bye"]["odds"]) for r in a["board"]])
print("set:", a["set"], "runs", a["runs"], "effective_runs", a["effective_runs"])
print("the two responses are byte-equal:", (here / "response-1.json").read_bytes() == (here / "response-2.json").read_bytes())
print("the two responses are JSON-equal:", a == b)
