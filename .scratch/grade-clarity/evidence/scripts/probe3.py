"""
Grade trade A with no Claude call on the saved week 8 data of cpc, as `cornerstone analyze --week 8` loads it.
Print the as-of block, the Week lines, and the week of the snapshot.
"""
import argparse
import json
import sys
from pathlib import Path
from analyzer.analysis import code_only
from analyzer.routes import result_document
from analyzer.rubric import GivenPlayer, ProposedTrade, TradeSide
from cornerstone.cli import _saved_snapshot
from cornerstone_api.app import load_clients

client = next(c for c in load_clients(Path(sys.argv[1])) if c.slug == "cpc")
snap = _saved_snapshot(argparse.Namespace(season=2026, week=8, chart=None), client)
A = ProposedTrade(season=2026, asker=10, sides=[TradeSide(roster_id=10, gives=[GivenPlayer(player_id="13276", to=6)]),
                                                TradeSide(roster_id=6, gives=[GivenPlayer(player_id="9487", to=10)])])
doc = result_document(A, snap, code_only(A, snap))
print(f"snapshot week {snap.week}, graded_at {snap.as_of.graded_at}, chart is None: {snap.chart is None}")
print(json.dumps({"as_of": doc["as_of"], "week_lines": {s["roster_id"]: s["week_lines"] for s in doc["sides"]},
                  "deal_rows": {s["roster_id"]: s["factors"][0] for s in doc["sides"]}}, indent=2))
