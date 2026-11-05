"""
Search the live cpc snapshot for a player who steps up in week 9 or 10, and for the rosters of the Spears trade.
It reads real data only and makes no grade.
"""
import sys
from pathlib import Path
from analyzer.week_line import _steps_up, _out_reason
from cornerstone_api.app import _real_sources, load_clients

client = next(c for c in load_clients(Path(sys.argv[1])) if c.slug == "cpc")
snap = _real_sources(client).snapshot(2026)
print("graded_at", snap.as_of.graded_at, "dt", snap.depth_chart_dt)
for r, ids in sorted(snap.rosters.items()):
    for pid in ids:
        for week in (9, 10):
            if _steps_up(snap, pid, week):
                p, a = snap.players[pid], snap.ahead_on_chart[pid]
                print(f"STEP week {week}: roster {r} {pid} {p.name} {p.position} {p.nfl_team} "
                      f"behind {a.player_id} {a.name} status={a.injury_status} return={snap.returns.get(a.player_id)}")
for r in (4, 12, 8, 2):
    print(r, [(pid, snap.players[pid].name, snap.players[pid].position, snap.players[pid].injury_status) for pid in snap.rosters[r] if snap.players[pid].position in ("RB", "WR")])
for pid in ("9508", "5967"):
    print(pid, snap.players.get(pid), [r for r, ids in snap.rosters.items() if pid in ids], snap.returns.get(pid), snap.ahead_on_chart.get(pid))
