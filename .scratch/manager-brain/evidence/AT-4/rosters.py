"""
Print the RBs and WRs of both sides of eval trade 6, before and after the trade, with each position rank and line.
It loads the saved week 7 snapshot the same way as the advisor eval, so the rosters match the sheet of the eval.
"""
import argparse
from pathlib import Path

from analyzer.measures import _roster_after
from cornerstone.advisor_eval import EvalTrade, named_in_week, proposed_trade, roster_ids_by_name, rosters_before
from cornerstone.cli import VALUE_MODELS, _saved_snapshot, find_root
from league.client import load_client
from league.lineup import above_the_line
from league.paths import nfl_dir, provider_cache_dir
from league.provider.sleeper import SleeperProvider

root = find_root(Path.cwd())
provider = SleeperProvider(provider_cache_dir(nfl_dir(root)))
client = load_client(root, "cpc", 2026, provider.fetch_settings, VALUE_MODELS)
base = _saved_snapshot(argparse.Namespace(season=2026, week=7, chart=None), client)
from league.provider.sleeper import load_raw  # noqa: E402
from league.paths import raw_dir  # noqa: E402
transactions = load_raw(raw_dir(client.folder, 2026, 7)).transactions
known = roster_ids_by_name([base])
trade = EvalTrade(id=6, week=7, asker="behold the lamb", other="Pukancun on 3",  # The week 7 name of the roster that the test set calls NFC Least.
                  asker_gives=["Saquon Barkley", "CeeDee Lamb"], asker_gets=["Omar Cooper Jr.", "Puka Nacua"])
trade = named_in_week(trade, base, known)
rosters, note = rosters_before(trade, base, transactions)
snapshot = base.model_copy(update={"rosters": rosters})
proposed = proposed_trade(trade, snapshot)
print(f"Trade 6, week 7. Roster note: {note}")
lines = client.settings.lines
print(f"Lines of the client: RB {lines.get('RB')}, WR {lines.get('WR')}")
for side in proposed.sides:
    gives = [g.player_id for g in side.gives]
    gets = [g.player_id for s in proposed.sides if s is not side for g in s.gives]
    team = snapshot.teams[side.roster_id].name
    for label, roster in (("before", snapshot.rosters[side.roster_id]),
                          ("after", _roster_after(snapshot, side.roster_id, gives, gets))):
        for position in ("RB", "WR"):
            players = [pid for pid in roster if snapshot.players[pid].position == position]
            rows = sorted(players, key=lambda pid: snapshot.position_rank(pid) or 999)
            count = sum(1 for pid in rows if above_the_line(snapshot, pid))
            text = ", ".join(f"{snapshot.players[pid].name} ({position}{snapshot.position_rank(pid) or '-'})"
                             for pid in rows)
            print(f"{team} (roster {side.roster_id}) {label}, {position}: {count} in the top {lines.get(position)}: {text}")
