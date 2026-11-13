import json, pathlib, re, sys
pr = json.loads(pathlib.Path(sys.argv[1]).read_text())
text = (pr["title"] + "\n" + pr["body"]).lower()
names = set()
for path in pathlib.Path("clients").glob("*/data/**/users.json"):
    for user in json.loads(path.read_text()):
        names.add(user.get("display_name") or "")
        names.add((user.get("metadata") or {}).get("team_name") or "")
names.discard("")
clients = sorted({p.parts[1] for p in pathlib.Path("clients").glob("*/data/**/users.json")})
hits = sorted(name for name in names if re.search(rf"\b{re.escape(name.lower())}\b", text))
print(f"Clients: {', '.join(clients)}. Checked {len(names)} names. Hits: {', '.join(hits) or 'none'}.")
