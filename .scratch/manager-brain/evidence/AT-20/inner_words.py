"""Search each Bullet and each Case of the live eval reads for the inner words. Usage: inner_words.py <eval out dir>."""
import glob, json, re, sys
WORDS = ("trade value", "return bet")
hits = 0; reads = 0; texts = 0
for path in sorted(glob.glob(f"{sys.argv[1]}/trade-*.json"), key=lambda p: int(re.search(r"(\d+)", p.split("/")[-1]).group(1))):
    d = json.load(open(path)); reads += 1
    items = [("case", d["case"] or "")] + [(f"bullet {s['roster_id']}.{i}", b["text"]) for s in d["sides"] for i, b in enumerate(s["bullets"], 1)]
    found = [(label, w) for label, t in items for w in WORDS if w in t.lower()]
    texts += len(items); hits += len(found)
    print(f"trade {d['id']}: {len(items)} texts searched, hits={len(found)} {found if found else ''}")
print(f"TOTAL reads={reads} texts={texts} hits={hits}")
