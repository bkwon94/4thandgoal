"""Search each Case, fairness reason, gains line, and Bullet of the live eval reads for "rival" and for "Brian".
Usage: copy_words.py <eval out dir> <players.json>. The names of NFL players that hold "Brian" go out first."""
import glob, json, re, sys
players = json.load(open(sys.argv[2]))
# Each name also goes out without a suffix such as "Jr.", because a read may write "Brian Robinson".
SUFFIX = re.compile(r"\s+(Jr\.?|Sr\.?|II|III|IV|V)$")
full = {p["full_name"] for p in players.values() if p.get("full_name") and "brian" in p["full_name"].lower()}
brian_players = sorted(full | {SUFFIX.sub("", n) for n in full}, key=len, reverse=True)
reads = texts = raw = hits = 0
for path in sorted(glob.glob(f"{sys.argv[1]}/trade-*.json"), key=lambda p: int(re.search(r"(\d+)", p.split("/")[-1]).group(1))):
    d = json.load(open(path)); reads += 1
    items = [("case", d["case"] or "")]
    items += [(f"fairness {s.get('roster_id')}", s.get("reason", "")) for s in (d.get("fairness") or {}).get("sides", [])]
    items += [(f"gains {s['roster_id']}", s.get("gains") or "") for s in d["sides"]]
    items += [(f"bullet {s['roster_id']}.{i}", b["text"]) for s in d["sides"] for i, b in enumerate(s["bullets"], 1)]
    found = []; players_named = []
    for label, text in items:
        raw += len(re.findall(r"brian", text, re.I))
        stripped = text
        for name in brian_players:
            if name in stripped: players_named.append((label, name)); stripped = stripped.replace(name, "")
        found += [(label, w) for w in ("rival", "brian") if w in stripped.lower()]
    texts += len(items); hits += len(found)
    print(f"trade {d['id']}: {len(items)} texts, hits={len(found)} {found if found else ''}"
          f"{' player names removed: ' + str(players_named) if players_named else ''}")
print(f"TOTAL reads={reads} texts={texts} raw_brian={raw} hits_after_player_names={hits}")
