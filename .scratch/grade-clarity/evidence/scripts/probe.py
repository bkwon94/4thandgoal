"""
Print the real values of the grade-clarity acceptance tests from the live snapshot of cpc, with a set grade time.
It reads the real Sleeper and nflverse data through the API Sources, and makes no Claude call except the chart read.
"""
import json
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analyzer.analysis import code_only
from analyzer.cache import cache_key
from analyzer.finder import find_win_wins
from analyzer.finder_reasons import trade_facts
from analyzer.routes import result_document
from analyzer.rubric import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_facts import shown_ranks, trade_fact_sheet
from analyzer.week_line import chart_is_fresh, last_game_status, week_lines
from cornerstone_api.app import _real_sources, load_clients
from league.ranks import recent_points_per_game, recent_rank, season_points_per_game, lineup_value, due_back_week

REPO = Path(sys.argv[1])
OUT = Path(sys.argv[2])
MODE = sys.argv[3]  # "now" or an ISO grade time
client = next(c for c in load_clients(REPO) if c.slug == "cpc")
sources = _real_sources(client)
if MODE != "now":
    fixed = datetime.fromisoformat(MODE)
    sources = replace(sources, clock=lambda: fixed)
snap = sources.snapshot(2026)


def trade(asker: int, *sides: tuple[int, str, int]) -> ProposedTrade:
    return ProposedTrade(season=2026, asker=asker, sides=[
        TradeSide(roster_id=r, gives=[GivenPlayer(player_id=p, to=t)]) for r, p, t in sides])


def name(pid: str) -> str:
    p = snap.players.get(pid)
    return p.name if p else pid


def roster_of(pid: str) -> int | None:
    return next((r for r, ids in snap.rosters.items() if pid in ids), None)


def find_id(full: str) -> str:
    return next(pid for pid, p in snap.players.items() if p.name == full)


def write(fname: str, lines: list[str]) -> None:
    (OUT / fname).write_text("\n".join(lines) + "\n")


def lines_of(t: ProposedTrade) -> list[str]:
    return [f"  roster {r}: {line.text}" for r, ls in week_lines(t, snap).items() for line in ls]


head = [f"grade time (as_of.graded_at): {snap.as_of.graded_at.isoformat() if snap.as_of.graded_at else None}",
        f"depth_chart_dt: {snap.depth_chart_dt.isoformat() if snap.depth_chart_dt else None}",
        f"age of the chart at the grade time: {snap.as_of.graded_at - snap.depth_chart_dt}",
        f"chart_is_fresh: {chart_is_fresh(snap)}", f"last_game_status (Tue or Wed): {last_game_status(snap)}",
        f"trade week: {snap.week}, stats_through: {snap.as_of.stats_through}, chart_week: {snap.as_of.chart_week}"]
A = trade(10, (10, "13276", 6), (6, "9487", 10))

# Steps up: the SF WR rows of the depth chart, Tate and Robinson, the trade of Samuel.
evans = find_id("Mike Evans")
sf = [f"{pid} {name(pid)} status={snap.players[pid].injury_status} roster={roster_of(pid)} "
      f"ahead={snap.ahead_on_chart[pid].name if pid in snap.ahead_on_chart else None}"
      for pid, p in snap.players.items() if p.nfl_team == "SF" and p.position == "WR" and pid in snap.ahead_on_chart
      or pid == evans]
gsis = snap.depth_charts.get("SF", {}).get("WR", []) if snap.depth_charts else []
tate, robinson = find_id("Carnell Tate"), find_id("Wan'Dale Robinson")
samuel = find_id("Deebo Samuel Sr.")
step = head + ["", f"SF WR depth chart gsis order: {gsis}", "SF WRs with a player ahead on the chart (Sleeper file):", *sf,
               "", f"Trade S: roster {roster_of(samuel)} gives {samuel} {name(samuel)} to roster 6 for 9487 Parker Washington.",
               *lines_of(trade(roster_of(samuel), (roster_of(samuel), samuel, 6), (6, "9487", roster_of(samuel)))),
               "", f"Trade T: roster {roster_of(tate)} gives {tate} {name(tate)} to roster {roster_of(robinson)} "
               f"for {robinson} {name(robinson)}. Roster {roster_of(tate)} asks.",
               *lines_of(trade(roster_of(tate), (roster_of(tate), tate, roster_of(robinson)),
                               (roster_of(robinson), robinson, roster_of(tate))))]
for full in ("Carnell Tate", "Wan'Dale Robinson", "Malik Lemon", "Chris Godwin", "Emeka Egbuka", "Dontayvion Wicks",
             "Jordan Watkins"):
    try:
        pid = find_id(full)
    except StopIteration:
        step.append(f"{full}: not in the players file of the snapshot")
        continue
    a = snap.ahead_on_chart.get(pid)
    step.append(f"{pid} {full} team={snap.players[pid].nfl_team} status={snap.players[pid].injury_status} "
                f"roster={roster_of(pid)} ahead={a.player_id + ' ' + a.name + ' status=' + str(a.injury_status) if a else None}")
from analyzer.week_line import _steps_up
step += ["", "Every rostered player who steps up in week 9 or 10 at this grade time:"]
for r, ids in sorted(snap.rosters.items()):
    for pid in ids:
        for w in (9, 10):
            if _steps_up(snap, pid, w):
                step.append(f"  week {w}: roster {r} {pid} {name(pid)} behind {snap.ahead_on_chart[pid].name}")
step += ["  (end of list)", "", "Trade A at this grade time:", *lines_of(A)]
write(f"stepup-{MODE[:13]}.txt", step)
if MODE != "now":
    sys.exit(0)

# Position rank and season and recent ranks.
wr = snap.rank_table()["WR"]
rank = [f"position_rank(13276) = WR{snap.position_rank('13276')}", "WR rank table, places 20 to 30:"]
for i, pid in enumerate(wr[19:30], start=20):
    rank.append(f"  WR{i} {pid} {name(pid)} season_ppg={season_points_per_game(snap, pid):.2f} "
                f"lineup_value={lineup_value(snap, pid):.2f} due_back_week={due_back_week(snap, pid)}")
for pid in ("13276", "9487"):
    rank.append(f"{pid} {name(pid)}: shown_ranks={shown_ranks(snap, pid)} raw recent_rank={recent_rank(snap, pid)} "
                f"recent_ppg={recent_points_per_game(snap, pid):.2f} season_ppg={season_points_per_game(snap, pid):.2f}")
write("ranks.txt", head + [""] + rank)

# Week 8 points allowed to WRs, the byes and statuses of the WRs of rosters 6 and 10.
pa = snap.points_allowed or {}
table = sorted(((v["WR"].rank, team, v["WR"].points, v["WR"].games) for team, v in pa.items() if "WR" in v))
wk = ["Points allowed to WRs, rank 1 the most:"] + [f"  {r:2d} {t} points={p:.1f} games={g}" for r, t, p, g in table]
wk += ["", "WRs of rosters 6 and 10: bye week, Sleeper injury_status, return week"]
for r in (10, 6):
    for pid in snap.rosters[r]:
        p = snap.players[pid]
        if p.position == "WR":
            sched = snap.schedules.get(p.nfl_team) if snap.schedules and p.nfl_team else None
            wk.append(f"  roster {r}: {pid} {p.name} {p.nfl_team} bye={sched.bye_week if sched else None} "
                      f"status={p.injury_status} return={snap.returns.get(pid)}")
wk += ["", "Week lines of trade A at this grade time:", *lines_of(A)]
write("week.txt", head + [""] + wk)

# The fact sheet of trade A.
facts = trade_fact_sheet(A, snap)
write("facts.txt", head + ["", "Fact ids:", *[f"  {k}" for k in facts],
                           "", "Week line facts:", *[f"  {k}: {f.text}" for k, f in facts.items() if "week_line" in k]])

# The cache key of trade A, after a new chart dt, after a new status.
k1 = cache_key(A, snap)
moved = snap.model_copy(update={"depth_chart_dt": snap.depth_chart_dt + timedelta(hours=1)})
k2 = cache_key(A, moved)
target = next(pid for pid in snap.rosters[10] if snap.players[pid].position == "WR" and snap.players[pid].injury_status is None)
players = dict(moved.players)
players[target] = players[target].model_copy(update={"injury_status": "Out"})
k3 = cache_key(A, moved.model_copy(update={"players": players}))
write("cache.txt", head + ["", f"1. key of trade A on the live snapshot: {k1}",
                           f"2. depth_chart_dt {snap.depth_chart_dt.isoformat()} -> {moved.depth_chart_dt.isoformat()}: {k2}",
                           f"3. then {target} {name(target)} (roster 10 WR) injury_status None -> Out: {k3}",
                           f"key 1 != key 2: {k1 != k2}; key 2 != key 3: {k2 != k3}; key 1 != key 3: {k1 != k3}"])

# The finder facts of the pair 10 and 6.
found = find_win_wins(10, 6, snap)
fin = [f"finder trades of asker 10 and partner 6: {len(found)}"]
for n, item in enumerate(found, start=1):
    fin.append(f"t{n}: " + "; ".join(f"roster {s.roster_id} gives {[name(p) for p in s.player_ids]}" for s in item.trade.sides))
if found:
    sheet = trade_facts(1, found[0], snap)
    fin += ["", "Fact sheet of finder trade t1:", *[f"  {k}: {f.text}" for k, f in sheet.items()]]
write("finder.txt", head + [""] + fin)

# Code-only documents of the Spears trade and the Tate trade, plus a no-chart grade of trade A.
spears = trade(4, (4, "9508", 12), (12, "7567", 4))
(OUT / "spears.json").write_text(json.dumps(result_document(spears, snap, code_only(spears, snap)), indent=2))
tt = trade(8, (8, "13279", 2), (2, "8126", 8))
(OUT / "tate.json").write_text(json.dumps(result_document(tt, snap, code_only(tt, snap)), indent=2))
nochart = snap.model_copy(update={"chart": None, "as_of": snap.as_of.model_copy(update={"chart_week": None})})
(OUT / "nochart.json").write_text(json.dumps(result_document(A, nochart, code_only(A, nochart)), indent=2))
write("rosters.txt", [f"9508 {name('9508')} roster={roster_of('9508')}", f"5967 {name('5967')} roster={roster_of('5967')}",
                      f"7567 {name('7567')} roster={roster_of('7567')}",
                      f"returns 9508: {snap.returns.get('9508')}, status 9508: {snap.players['9508'].injury_status}",
                      f"ahead of 9508: {snap.ahead_on_chart.get('9508')}"])
print("done")
