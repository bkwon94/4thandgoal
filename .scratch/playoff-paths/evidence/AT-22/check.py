"""
AT-22 evidence script: it calls the What-if route of the local evidence API for Bo Girds with no set result.
It saves the request and the response, and diffs the page block with the page of Bo Girds in week-11/sim.json.
"""
import json, sys, urllib.request
from pathlib import Path
base, sim_path, here = sys.argv[1], Path(sys.argv[2]), Path(__file__).parent
body = {"you": 6, "set": []}
req = urllib.request.Request(f"{base}/clients/cpc/sim/what-if", data=json.dumps(body).encode(), method="POST",
                             headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=120) as res:
    raw = res.read()
    print(f"POST {base}/clients/cpc/sim/what-if {json.dumps(body)} -> {res.status}, {len(raw)} bytes")
(here / "request.json").write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
(here / "response.json").write_bytes(raw)
page = json.loads(raw)["page"]
sim = json.loads(sim_path.read_text(encoding="utf-8"))
filed = sim["pages"]["6"]
print(f"file: {sim_path} (week {sim['week']})")
def diff(a, b, path="$"):
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in dict.fromkeys([*a, *b]) for p in (diff(a[k], b[k], f"{path}.{k}") if k in a and k in b else [f"{path}.{k}"])]
    if isinstance(a, list) and isinstance(b, list):
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in diff(x, y, f"{path}[{i}]")] + [f"{path}[{i}]" for i in range(min(len(a), len(b)), max(len(a), len(b)))]
    return [] if a == b else [path]
d = diff(filed, page)
(here / "page.diff").write_text("\n".join(d) + ("\n" if d else ""), encoding="utf-8")
print(f"page keys: response {sorted(page)}; file {sorted(filed)}")
print(f"JSON paths that differ between the response page and the file page: {len(d)}")
for p in d[:40]:
    print("  ", p)
