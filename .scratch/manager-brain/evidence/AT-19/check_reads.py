"""Check the 28 live eval reads against their saved sheets: fact ids, numbers, and player names.
Usage: check_reads.py <eval out dir> <players.json>. Prints one line per read and each miss."""
import glob, json, re, sys
out, players_path = sys.argv[1], sys.argv[2]
players = json.load(open(players_path))
NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?")
def nums(text):
    return {float(n) for n in NUM.findall(text.replace(",", ""))}
names = {p["full_name"] for p in players.values()
         if p.get("full_name") and p.get("position") in ("QB", "RB", "WR", "TE", "K") and p.get("team")}
def full_names(text):
    return {n for n in names if re.search(rf"(?<!\w){re.escape(n)}(?!\w)", text)}
total = {"reads": 0, "bullets": 0, "id_miss": 0, "num_miss": 0, "name_miss": 0, "last_miss": 0}
for path in sorted(glob.glob(f"{out}/trade-*.json"), key=lambda p: int(re.search(r"(\d+)", p.split("/")[-1]).group(1))):
    d = json.load(open(path)); sheet = d["sheet"]; total["reads"] += 1
    sheet_names = set().union(*(full_names(t) for t in sheet.values()))
    # A fact id that starts with a player id is a fact of a player in the trade.
    in_trade = {players[k.split(".")[0]]["full_name"] for k in sheet if k.split(".")[0] in players}
    lasts = {n.split()[-1]: n for n in sheet_names if len(n.split()[-1]) > 3}
    misses = []; cited = []
    for side in d["sides"]:
        for b in side["bullets"]:
            total["bullets"] += 1; cited.append(b["fact_id"])
            if b["fact_id"] not in sheet:
                misses.append(f"fact id {b['fact_id']} is not on the sheet"); total["id_miss"] += 1; continue
    def check(label, text, facts):
        ftext = " ".join(sheet.get(f, "") for f in facts)
        for n in sorted(nums(text) - nums(ftext)):
            misses.append(f"{label}: number {n:g} is not in its cited facts. Text: {text!r}"); total["num_miss"] += 1
        for n in sorted(full_names(text) - full_names(ftext)):
            tag = "in the trade" if n in in_trade else "not in the trade"
            misses.append(f"{label}: name {n} is not in its cited facts ({tag})"); total["name_miss"] += 1; total[tag] = total.get(tag, 0) + 1
        for last, full in sorted(lasts.items()):
            if re.search(rf"(?<!\w){re.escape(last)}(?!\w)", text) and full not in ftext and last not in ftext:
                tag = "in the trade" if full in in_trade else "not in the trade"
                misses.append(f"{label}: name {last} ({full}) is not in its cited facts ({tag})"); total["last_miss"] += 1; total[tag] = total.get(tag, 0) + 1
    for side in d["sides"]:
        for i, b in enumerate(side["bullets"], 1):
            check(f"bullet {side['roster_id']}.{i}", b["text"], [b["fact_id"]])
    check("case", d["case"] or "", cited)
    print(f"trade {d['id']}: lean={d['lean']} bullets={sum(len(s['bullets']) for s in d['sides'])} "
          f"cited ids on sheet={sum(f in sheet for f in cited)}/{len(cited)} misses={len(misses)}")
    for m in misses: print("   ", m)
print("TOTAL", json.dumps(total))
