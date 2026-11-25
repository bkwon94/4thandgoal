"""
Makes the changed copies of cpc week-11 sim.json for the variant runs of AT-37 and AT-39.
Each copy changes only the fields its name says; the original file stays as it is.
"""
import copy, json, sys
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src))
def game(doc, winner, loser):
    rows = doc["pages"]["6"]["week_card"]["goals"]["spot"]["root_for"][0]
    return next(r for r in rows if r["winner"] == winner and r["loser"] == loser)
# AT-37: the game "Unsolicited Dak Picks (11) beats Maye d'force B with U (9)" of "Win and beat the median": odds 70, other 68.
half = copy.deepcopy(d); game(half, 11, 9)["odds"] = 68.5
json.dump(half, open(f"{out}/sim-variant-under-1pt-half.json", "w"))
zero = copy.deepcopy(d); game(zero, 11, 9)["odds"] = 68
json.dump(zero, open(f"{out}/sim-variant-under-1pt-zero.json", "w"))
# AT-39: Lil Fridge (3) gets spot "in"; Maye d'force B with U (9) gets spot "in" and seed-1 "in".
cl = copy.deepcopy(d)
board = {b["roster_id"]: b for b in cl["board"]}
board[3]["goals"]["spot"]["status"] = "in"
board[9]["goals"]["spot"]["status"] = "in"
board[9]["goals"]["seed-1"]["status"] = "in"
json.dump(cl, open(f"{out}/sim-variant-clinched.json", "w"))
print("before:", game(d, 11, 9), {k: board_k["goals"]["spot"]["status"] for k, board_k in {b["roster_id"]: b for b in d["board"]}.items() if k in (3, 9)})
