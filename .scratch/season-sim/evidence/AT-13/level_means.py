"""Work out the level mean of each CPC team from the saved scores of 2026 weeks 1 to 10, and compare it with the file.
The level is (own points + 5 x league average) / (own games + 5): the season average shrunk with 5 weeks of weight."""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
sim = json.loads((root / "clients/cpc/published/2026/week-10/sim.json").read_text())
scores: dict[int, list[float]] = {}
for week in range(1, 11):
    for row in json.loads((root / f"clients/cpc/data/2026/history/week-{week:02d}/matchups.json").read_text()):
        scores.setdefault(row["roster_id"], []).append(row["points"])
league = sum(sum(s) for s in scores.values()) / sum(len(s) for s in scores.values())
print(f"source: clients/cpc/data/2026/history/week-01..week-10/matchups.json, field points")
print(f"file: shrink_weeks {sim['parameters']['shrink_weeks']}, league_mean {sim['parameters']['league_mean']:.4f}")
print(f"worked out: league average {league:.4f} over {sum(len(s) for s in scores.values())} scores")
print(f"{'roster':>6} {'name':<24} {'games':>5} {'season avg':>10} {'worked out':>10} {'file':>10} {'gap':>8}")
worst = 0.0
for rid in sorted(scores):
    own = scores[rid]
    expected = (sum(own) + 5 * league) / (len(own) + 5)
    in_file = sim["parameters"]["level_mean"][str(rid)]
    gap = abs(expected - in_file)
    worst = max(worst, gap)
    print(f"{rid:>6} {sim['names'][str(rid)]:<24} {len(own):>5} {sum(own) / len(own):>10.4f} {expected:>10.4f} "
          f"{in_file:>10.4f} {gap:>8.5f}")
print(f"largest gap: {worst:.6f}")
print("parameter keys of the file:", sorted(sim["parameters"]))
