"""
AT-1 and AT-2: the order of the standings table and of the sim draw for each saved week with a Sleeper bracket.
It prints the order of all rosters with W-L, Points For, and Points Against, beside the Sleeper seeds 1 to 6.
"""
import json, sys
from league.history import load_saved_weeks
from league.models import History
from league.paths import client_dir, history_root
from league.provider.raw import RawLeague
from league.provider.sleeper import league_settings
from league.standings_table import season_records, standings_order
from sim.season import season_sim
from pathlib import Path
ROOT = Path.cwd()
weeks = [tuple(a.split(":")) for a in sys.argv[1:]]
for slug, week in weeks:
    week = int(week)
    data = client_dir(ROOT, slug) / "data" / "2026"
    raw = data / f"week-{week:02d}" / "raw"
    settings = league_settings(RawLeague.model_validate_json((raw / "league.json").read_text(encoding="utf-8")))
    history = History(week=week, weeks=load_saved_weeks(history_root(client_dir(ROOT, slug), 2026), week, settings.points_key))
    bracket = json.loads((raw / "bracket.json").read_text(encoding="utf-8"))
    m = {g["m"]: g for g in bracket}
    seeds = [m[3]["t1"], m[4]["t1"], m[2]["t2"], m[1]["t1"], m[1]["t2"], m[2]["t1"]]
    records = season_records(history, week, median_game=settings.median_game)
    table = standings_order(records)
    scores = {rid: [history.weeks[w].scores[rid] for w in range(1, week + 1)] for rid in records}
    run = season_sim(scores, records, {}, season=2026, week=week, settings=settings, runs=1, sample=1).sample[0]
    print(f"== {slug} 2026 week {week} ({raw / 'bracket.json'})")
    print(f"Sleeper seeds 1-6: {seeds}")
    print(f"standings order 1-6: {table[:6]}")
    print(f"sim order 1-6:       {run.table[:6]}")
    print("place  roster  record   PF        PA        Sleeper seed")
    for n, rid in enumerate(table, start=1):
        r = records[rid]
        rec = r if isinstance(r, (list, tuple)) else r
        seed = seeds.index(rid) + 1 if rid in seeds else "-"
        print(f"{n:<6} {rid:<7} {rec}  seed {seed}")
