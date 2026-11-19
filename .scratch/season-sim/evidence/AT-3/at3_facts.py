"""Put each playoff odds number of the week 10 facts beside the number of that team in week-10/sim.json."""
import json
import re
import sys

facts, sim = (json.load(open(p)) for p in sys.argv[1:3])
names = sim["names"]
swings = {(s["a"], s["b"]): s for s in sim["swings"]}
checked = equal = 0
for fid, text in facts["facts"].items():
    if fid.startswith("ODDS.") and not fid.endswith(".why"):
        rid = fid.split(".")[1]
        t = sim["teams"][rid]
        m = re.search(r"in about (\d+)% of runs, with a bye in (\d+)%", text)
        pairs = [("playoff", int(m.group(1)), t["playoff"]), ("bye", int(m.group(2)), t["bye"])] if m else []
        print(f"{fid}: {text}")
        for label, in_fact, in_file in pairs:
            checked += 1
            equal += in_fact == in_file
            print(f"    {label}: fact {in_fact}, sim.json teams.{rid}.{label} {in_file}")
    elif fid.startswith("SW."):
        a, b = (int(x) for x in fid[3:].split("v"))
        s = swings[(a, b)]
        print(f"{fid}: {text}")
        for rid, win, loss in ((a, s["a_win"], s["a_loss"]), (b, s["b_win"], s["b_loss"])):
            m = re.search(re.escape(names[str(rid)]) + r" at (\d+)%, a loss at (\d+)%", text)
            if m:
                for label, in_fact, in_file in (("win", int(m.group(1)), win), ("loss", int(m.group(2)), loss)):
                    checked += 1
                    equal += in_fact == in_file
                    print(f"    {names[str(rid)]} after a {label}: fact {in_fact}, sim.json swings {a}v{b} {in_file}")
            else:
                print(f"    {names[str(rid)]}: no number in the fact (sim.json swings win {win}, loss {loss})")
print(f"\nodds numbers in the facts: {checked}; equal to the file: {equal}")
