"""
AT-21 evidence script: it reads the first What-if response of AT-20 and prints its board block.
It also lists each key named clinch anywhere in the response.
"""
import json
from pathlib import Path
path = Path(__file__).parent.parent / "AT-20" / "response-1.json"
r = json.loads(path.read_text(encoding="utf-8"))
print(f"file: {path}")
print(f"board rows {len(r['board'])}; keys of each row {sorted({k for row in r['board'] for k in row})}")
print("board:", json.dumps(r["board"], ensure_ascii=False))
def keys(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items():
            yield f"{path}.{k}", k
            yield from keys(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from keys(v, f"{path}[{i}]")
hits = [p for p, k in keys(r) if "clinch" in k.lower()]
print(f"keys with clinch in the name anywhere in the response: {len(hits)}", hits[:10])
