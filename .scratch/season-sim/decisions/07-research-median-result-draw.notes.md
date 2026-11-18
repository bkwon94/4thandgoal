# 07 notes: the median result, the split of the runs, and the response of one call

Research notes for `07-research-median-result-draw.md`. The scripts are throwaway and live in the session scratchpad, not in the repo:

- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/51a21148-e4c9-4264-ad98-6eb237fbf45b/scratchpad/median.py`: the method, the rejection reference, the split, the noise, the time, and the response. Modes: `check`, `ess`, `compare`, `noise`, `jump`, `timing`, `response`.
- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/51a21148-e4c9-4264-ad98-6eb237fbf45b/scratchpad/ceiling.py`: the ceiling of the effective runs.
- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/51a21148-e4c9-4264-ad98-6eb237fbf45b/scratchpad/gameonly.py`: a game result alone.
- The outputs sit beside them: `compare.txt`, `timing.txt`, `noise.txt`, `noise4.txt`, `jump.txt`, `response.txt`, `response-0.json`, `response-4.json`.

Each command runs from the worktree root as `uv run --exact --package cornerstone python <script> <mode>`.

## Summary

- **The key fact:** Your team beats the median exactly when its score is above the k-th highest of the other scores, with k = teams // 2. With R the other 10 scores in a 12-team league, sorted high to low, each tile has a simple form. A win beats the median when Your score is above r6. A loss beats it when Your score is above r5, because the opponent then sits above You. The check found 0 mismatches in 600,000 weeks, ties included.
- **Method:** the conditional draw with a weight, as in decision 01, in the order "Your score first". Draw Your score cut to its side of the line r6 or r5. Then draw the opponent's score cut to its side of Your score. The weight is the product of the two chances. It is exact up to sample noise, and no weight is ever 0. A median result alone draws Your score on its side of the k-th of the other 11. A game result alone uses the pair draw of 01. Set results in other weeks, and the picks of 01, multiply into the weight.
- **Accuracy:** in 4 cases against rejection, the weight is within 0.5 to 1.4 points on each team's playoff odds. The draw with no weight is off by 3.8 to 5.4 points.
- **Mac time,** 10,000 runs, with the split and a sample of 200, on an M2 Pro under a load average of 12: 0 set results 0.90 s, 1 median result 0.93 s, 4 set results 0.98 s, 8 set results 1.05 s, 12 set results 1.10 s. `season_sim` of the same shape takes 0.85 s. The effective runs: 8,330, 2,049, 1,722, and 1,433 of 10,000.
- **Split:** yes. One sim per call gives each page number by a split of its runs: the ladder, the four tiles of each week, the odds after a loss, and the root-for rows. A split is the exact conditional odds, the same as rejection at no cost. Only the set results need the conditional draw. The noise is under 1 point for the common results. It reaches 1.6 to 2 points for a rare tile with no set result, and 2 to 4.4 points for a rare tile after 2 rare tiles are set. The order of the root-for rows is mostly noise: the full top 3 matches in only 2 to 6 of 20 seeds.
- **Response:** one JSON object with the sim.json keys `season`, `week`, `runs`, `teams`, and `sample`, plus `effective_runs`, `you`, `set`, and one `page` block. Raw 161,889 B and gzip 44,314 B with 4 set results. The 200 stored runs hold 96 % of the gzip bytes. With no sample it is 6,238 B raw and 1,613 B gzip. sim.json needs the same `page` block for each of the 12 teams: 36,193 B raw and 3,697 B gzip.

## 1. The median method

### The model of one week

Each run draws a level per roster, then each weekly score as `round(gauss(level, spread) + shift, 1)` (`packages/sim/python/src/sim/season.py:140-141`). Given the levels, the 12 scores of a week are independent normals with one common sd. The head-to-head game gives no win on an exact tie (`season.py:203-206`). The median game counts a win for a score strictly above the line (`season.py:207-210`). The line is the mean of the two middle scores (`season.py:226-230`). The test replays the same rule (`packages/sim/python/tests/test_season.py:93-106`).

So "lose" in this note means "no win": the opponent scores the same or more. "Below" means "no median win": the score is at or under the line. Each pair of words splits the runs in two, with no gap.

### The threshold rule

Let o_1 >= o_2 >= ... be the scores of the 11 other teams, and k = 12 // 2 = 6.

- If x > o_6, x is among the top 6 of the 12. The line is the mean of min(x, o_5) and o_6, and both are under x or one equals x while the other is under it. So x is above the line.
- If x <= o_6, the top 6 of the 12 are o_1 to o_6. The line is the mean of o_6 and max(x, o_7), which is at least x. So x is not above the line.

The same proof works for each count of teams, odd or even, because `_median` takes the positions k and k + 1 with k = n // 2. Command `median.py check`:

```
threshold rule: 0 mismatches in 300,000 weeks (10% of scores forced to 100.0 to make ties)
threshold rule, 10 teams: 0 mismatches in 100,000 weeks
threshold rule, 12 teams: 0 mismatches in 100,000 weeks
threshold rule, 14 teams: 0 mismatches in 100,000 weeks
inline regular loop equals _regular on 2,000 runs
```

### The four tiles

Now take the opponent O out of the 11. Let r_1 >= r_2 >= ... be the other 10 scores. The 6th highest of the 11 is clamp(x_O, r6, r5). From that, each tile has a simple form:

| Tile | Exact condition |
|---|---|
| Win, above | x_O < x and x > r6 |
| Win, below | x_O < x and x <= r6 |
| Loss, above | x_O >= x and x > r5 |
| Loss, below | x_O >= x and x <= r5 |

The proof is short. A win puts O under You, so O cannot be the 6th of the 11 from above You. A loss puts O above You, so the line moves up one place to r5. The general form is r_k for a win and r_(k-1) for a loss.

### The methods

| Method | Exact? | Effective runs, 1 tile | Note |
|---|---|---|---|
| (a) Rejection | Yes. It is the definition. | The accept rate: 8 % to 50 % per tile. | 4 rare tiles: accept 0.1 %, 20 million draws. |
| (b) Conditional draw, no weight | No. | All runs. | It misses the update of the levels. Off by 3.8 to 5.4 points. |
| (c1) Weight, free opponent | Yes. | 26 % to 81 %. | Draw Your score on its interval, given all 11 other scores. The weight is 0 when the interval is empty. |
| (c2) Weight, opponent cut | Yes. | 46 % to 81 %. | As (c1), but first draw the opponent's score cut to the range where the tile can hold. |
| (c3) Weight, Your score first | Yes. | 46 % to 89 %. | The recommendation. See below. |

How (c3) draws one tile in week i, given the levels and the other 10 scores:

1. Pick the line: r6 for a win, r5 for a loss.
2. Draw Your score from its normal, cut above or below the line by the inverse CDF. The chance of that side is p1.
3. Draw the opponent's score from its normal, cut under Your score for a win, or at or over it for a loss. The chance is p2.
4. Multiply the weight of the run by p1 times p2.

The rounding to 1 decimal is exact. Each line and each score sits on the 0.1 grid, so x > a after the rounding holds exactly when the raw draw is above a + 0.05. Each cut sits on the edge of a rounding cell, so the draw keeps whole cells and the weight is the exact chance of the rounded event. A raw draw on the exact edge can round across it in floating point, so the script checks the result and redraws. Code: `held_result` with `seq=True` in `median.py`.

The other set results:

- **A median result alone:** draw Your score cut to its side of o_6, the 6th of the 11 others, which are already drawn. The weight is the chance of that side. Code: `held` in `median.py`.
- **A game result alone,** for a league with no median game: the pair draw of decision 01. Command `gameonly.py`: the pair draw gives 9,420 effective runs for a win and 9,670 for a loss. The exact opponent-side draw gives 6,725 and 7,865. The pair draw never gives a tie, so for a loss it leaves out the tie, with a chance of about 0.1 × φ(0) / (22.2 × √2), which is about 0.13 %. Use the opponent-side draw if the spec wants exact, or the pair draw if it accepts that gap.
- **Set results in several weeks:** given the levels, the weeks are independent, so the weights multiply. The draw of each set week runs after the free draw of its other scores.
- **A pick of decision 01 in the same week,** on a game without Your team: draw that pair first, then the tile. The tile reads the pair as part of R, so the product of the two weights is still exact. The page of decision 04 has no such pick, but the method allows it.

Why it is exact. The target is the prior times the indicator of the set results. The proposal draws the levels and the free scores from the prior, then each held score from its law cut to the event. The ratio of the target to the proposal is the product of the chances of the cuts. This is self-normalized importance sampling, with a bias of order 1 over n (A. B. Owen, *Monte Carlo theory, methods and examples*, chapter 9, https://artowen.su.domains/mc/Ch-var-is.pdf). Each step integrates one score out exactly, which is conditioning (chapter 8, section 7, https://artowen.su.domains/mc/Ch-var-basic.pdf).

### The accuracy against rejection

The league is the CPC fixture after week 8 (`packages/sim/site/fixtures/sim.json`): 12 teams, weeks 9 to 14 left, 6 playoff spots, 2 byes, the median game on, and reseed on. Your team is roster 8, at 42 % with no set result. The reference is rejection over 10 cores. Each other method uses 40,000 runs. Command `median.py compare`, output in `compare.txt`.

| Set results | Accept rate | Kept, draws | Reject, you | Weight (c3), you | No weight (b), you | Max gap (c3) | Max gap (b) | Effective runs (c3) |
|---|---|---|---|---|---|---|---|---|
| Above in week 9 | 0.3614 | 40,000 of 110,685 | 62.9 | 62.9 | 58.5 | 0.5 | 4.3 | 33,279 |
| Loss and above in week 9 | 0.0798 | 40,000 of 501,275 | 49.4 | 49.0 | 45.6 | 0.7 | 3.8 | 18,534 |
| 4: win-below wk 9, loss-above wk 10 | 0.0082 | 40,000 of 4,867,351 | 45.7 | 45.8 | 44.7 | 1.4 | 5.4 | 8,430 |
| 8: WA wk 9, LB wk 10, WB wk 11, LA wk 12 | 0.0010 | 20,000 of 19,923,779 | 60.6 | 60.1 | 57.8 | 1.1 | 5.3 | 6,779 |

The gap is the largest over the 12 teams' playoff odds, in points. The free opponent (c1) has gaps of 0.5, 0.8, 1.2, and 2.7 points. The opponent cut (c2) has 0.5, 0.5, 0.7, and 0.8 points. The rejection of the 8 case took 274 s on 10 cores.

Where the method without a weight fails. In the 4 case, team 2, the opponent of week 9, has 63.0 under rejection, 62.6 under (c3), and 68.5 under (b). In the 8 case, team 12, the opponent of week 11, has 30.5, 29.6, and 35.8. Method (b) keeps the levels of the prior, so it overrates a team that Your team beat.

The noise. One sample error of a 50 % number is 0.25 points for the reference at 40,000 kept and about 0.55 points for (c3) at 8,430 effective runs. The gap of 1.4 points in the 4 case is team 12, at about 2.4 combined errors. That is normal for the largest of 12 gaps.

The ladder matches too. The 8 case, as chance and playoff odds, rejection then (c3):

```
   4:  14.3   2.1 |  14.6   2.0
   5:  17.9  22.6 |  19.1  23.7
   6:  33.7  67.9 |  33.0  68.6
   7:  18.9  96.5 |  18.1  96.4
   8:  15.2 100.0 |  15.2 100.0
```

### The effective runs

Command `median.py ess`, 10,000 runs, seed 3. A one-tile row also shows what rejection keeps from 10,000 draws.

```
  WA: chance 27.8 %, rejection keeps  2778, free ESS   7012, cut ESS   7012, weight ESS   8162
  WB: chance 14.6 %, rejection keeps  1463, free ESS   3519, cut ESS   5463, weight ESS   5324
  LA: chance  8.0 %, rejection keeps   798, free ESS   2636, cut ESS   4575, weight ESS   4614
  LB: chance 49.6 %, rejection keeps  4961, free ESS   8106, cut ESS   8106, weight ESS   8866
1 game result only (W wk 9): free ESS   9420, cut ESS   9420, weight ESS   9420
likely path, 4 tiles: free ESS   2648, cut ESS   2648, weight ESS   5286
rare path, 4 tiles (scenario 8): free ESS    440, cut ESS   1289, weight ESS   1621
all 6 weeks (scenario 12): free ESS    250, cut ESS    753, weight ESS   1115
2 rare tiles (scenario 4): free ESS    619, cut ESS   2262, weight ESS   2121
```

The likely path is win-above in weeks 9 and 11 and loss-below in weeks 10 and 12. The effective runs fall about as the product of the share of each tile. Rare tiles fall fastest. The count from one seed is itself noisy: the 12 case gave 1,115 here and 1,433 in the timing, with the same seed but another use of the stream.

The ceiling. Command `ceiling.py` finds the share of effective runs of a perfect weight for one tile. C1 integrates the opponent's score and Your score exactly, given the levels and the other 10 scores. C2 integrates all 12 scores, given the levels only.

```
WA: mean chance 27.9 %, ceiling ESS per run: C1 0.858, C2 0.904
WB: mean chance 14.5 %, ceiling ESS per run: C1 0.745, C2 0.900
LA: mean chance  8.2 %, ceiling ESS per run: C1 0.585, C2 0.853
LB: mean chance 50.2 %, ceiling ESS per run: C1 0.950, C2 0.963
```

Method (c3) gets 0.82, 0.53, 0.46, and 0.89. That is close to C1 for the common tiles, and about 70 % of C1 for the rare ones. An exact integral over the opponent's score needs a quadrature in each run, at about 32 calls of the normal CDF per tile. That costs about 1 s more at 6 tiles, so I do not recommend it.

A draw of the levels from a pilot estimate gave no gain. I drew the levels of Your team and of each set opponent from the weighted mean and sd of a pilot of 2,000 runs, 1.2 times wider, with the ratio to the prior in the weight. This is a form of adaptive importance sampling. The effective runs were 6,795 for WA (no cut: 7,012) and 1,176 for the rare 4-tile path (cut: 1,289). So the levels are not the main source of the weight variance. The other 10 scores of the week are. I took the code out of the timing.

## 2. The time

Apple M2 Pro, 10 cores. The Mac ran other work: `uptime` gave the load averages `12.07 20.83 16.17` right after the run. So these times are high, but they compare with each other. Command `median.py timing`, best of 3, output in `timing.txt`:

```
season_sim, same shape, 10,000 runs: min 0.847 s (of 3)
               0 set results, 10,000 runs, split and sample of 200: min 0.899 s (of 3), ESS 10,000
 1 median result set results, 10,000 runs, split and sample of 200: min 0.931 s (of 3), ESS 8,330
   1 game result set results, 10,000 runs, split and sample of 200: min 0.961 s (of 3), ESS 9,429
     4 (2 tiles) set results, 10,000 runs, split and sample of 200: min 0.978 s (of 3), ESS 2,049
     8 (4 tiles) set results, 10,000 runs, split and sample of 200: min 1.050 s (of 3), ESS 1,722
    12 (6 tiles) set results, 10,000 runs, split and sample of 200: min 1.095 s (of 3), ESS 1,433
               0 set results, no sample: 0.885 s
```

- A set result here is one condition: a game result or a median result. One tile sets two.
- The shape is 12 teams, 6 regular weeks left, and 3 bracket weeks. Decision 01 measured 0.69 s for `season_sim` with 4 weeks left. The cost falls as the season goes on.
- The split and the weighted sample of 200 add about 0.05 s over `season_sim`. Each set tile adds about 0.04 s.
- Fly, an estimate and not a measure: decision 01 puts a Fly vCPU at 1.3 to 2 times slower than the Mac. That gives about 1.2 to 2.2 s per call at 6 weeks left while the burst lasts. It is over the budget of about 1 s early in the second half. 5,000 runs halve it (decision 01 notes, section 2).

The weighted sample. The replay needs runs that follow the set results. Each run of (c3) holds them, but a run with a high weight is more typical. The script keeps 200 runs by the weighted reservoir of Efraimidis and Spirakis: the key of a run is u^(1/w), and the 200 top keys stay (https://doi.org/10.1016/j.ipl.2005.11.003). It holds 200 runs in memory, not 10,000. It draws without replacement, so a low effective count spreads the sample a little wider than the exact law. A replay does not need more.

## 3. The split of one sim

### What the page needs, and what the split gives

| Page number (decision 04) | The split | Exact? |
|---|---|---|
| Playoff odds of Your team | All runs, weighted. | Yes. |
| The ladder: each count of more wins, its chance, and its playoff odds | The runs by the more wins of Your team, the median wins included. | Yes. A split is the conditional odds by count, the same as rejection with no extra draws. |
| The four tiles of each week: the chance and the playoff odds | The runs by the tile of Your team that week. | Yes. |
| The odds after a loss in a week | The runs where Your team has no win that week. | Yes. |
| The root-for rows: the odds after a loss and "<winner> beats <loser>" | The runs of a loss, by the winner of each other game of that week. | Yes, but see the noise. |

Only the set results need the conditional draw. With set results, each split is over the weighted runs, so each cell has an effective count of about its chance times the effective runs. Its sample error is about sqrt(p (1 - p) / (chance × ESS)). The measures below match that.

Two facts for the spec:

- With set results, the ladder counts the wins of the set weeks too. The 4 case sets one win and one median win, so its ladder starts at 2 more wins.
- In a set week, the set tile has chance 100 and the other three have no runs. With a set win, the root-for list of that week is empty.

### The noise with no set result

Command `median.py noise 0`: 20 seeds of 10,000 runs, the sd over the seeds in points, output in `noise.txt`.

- Playoff odds of Your team: mean 42.4, sd 0.49.
- The ladder: sd 0.49 to 1.05 for the counts in the open race (4 to 7 more wins). The counts at 0 or 100 have sd 0. Each count from 0 to 12 shows in each seed. The rarest, 12 more wins, has a chance of 0.26 %, about 26 runs. Its odds are 100 in each run, so it has no noise, but a count with odds in the open race and so few runs would be noisy.
- The four tiles. The common tiles have sd 0.48 to 0.97. The rare tiles, with a chance of 6 % to 15 %, have sd 1.07 to 2.00. Week 13 win-below, chance 5.9 %, has sd 2.00.
- The odds after a loss: sd 0.54 to 0.84.
- The root-for rows. Each row's number has sd 0.45 to 1.15. But the candidates sit within about 1 point of each other, so the order is mostly noise:

```
week 9:  root-for top 3 (4, 10, 5): same set and order in 3 of 20; same first row in 17 of 20
week 10: root-for top 3 (4, 11, 10): same set and order in 4 of 20; same first row in 11 of 20
week 11: root-for top 3 (11, 4, 10): same set and order in 6 of 20; same first row in 9 of 20
week 13: root-for top 3 (4, 11, 10): same set and order in 3 of 20; same first row in 11 of 20
```

### The noise with 2 rare tiles set

Command `median.py noise 4`, set: win-below in week 9 and loss-above in week 10, about 2,100 effective runs, output in `noise4.txt`.

- Playoff odds of Your team: mean 45.8, sd 0.81.
- The ladder: sd up to 1.75 (6 more wins, odds 69).
- The tiles of the later weeks. The common tiles have sd 1.03 to 1.69. The rare tiles have sd 2.11 to 4.38. Week 13 win-below, chance 5.8 %, has sd 4.38.
- The root-for rows: sd 0.99 to 2.00 per row. The full top 3 matches in 2 of 20 seeds.

### The jump after a tap

The tile shows odds from the split of the call before. After the tap, the next call gives the headline with that tile set. Both are exact, so they differ only by noise. Command `median.py jump`, 20 seeds each, output in `jump.txt`:

```
WA: tile from split mean  67.0 sd 0.89 | headline with tile set mean  66.8 sd 0.77 | jump mean +0.25, mean abs 0.95, max abs 2
WB: tile from split mean  45.2 sd 1.21 | headline with tile set mean  44.9 sd 0.73 | jump mean +0.35, mean abs 1.15, max abs 3
LA: tile from split mean  49.5 sd 1.63 | headline with tile set mean  49.5 sd 0.59 | jump mean +0.00, mean abs 1.00, max abs 3
LB: tile from split mean  26.6 sd 0.48 | headline with tile set mean  26.8 sd 0.54 | jump mean -0.10, mean abs 0.60, max abs 1
```

So a tap moves the number by about 1 point on average and by 3 points at most. The page animates the odds to the new value anyway (decision 04).

### What to do about the noise

- Keep the fixed seed of `season_sim` (`season.py:114-115`). The same set results then give the same numbers and the same rows on each call, so a reload never shuffles them.
- Rank the root-for rows with a tolerance. For example, keep the rows that lift the odds by 1 point or more, round the lift to whole points, and break a tie by the reason (the closest team in the standings first). The rows are all real help, so their order matters little.
- Return `effective_runs`. A spec can raise the runs, or show a tile's number as "about", when chance × ESS falls under a floor such as 400 runs. A floor of 400 keeps the sample error of a 50 % number under 2.5 points.

## 4. The response of one call

### The shape

The page reads `sim.json` first and calls the API only for a What-if (MAP, decisions so far). So the response holds only what changes with the set results: the odds of each team, the page numbers of Your team, and the runs for the replay. It leaves out `records`, `schedule`, `parameters`, `names`, `weeks`, and `bracket_weeks`, because sim.json already has them and they do not change.

The example below is cut from `response-4.json`: one team of 12, two weeks of 6, and one run of 200.

```json
{
  "schema_version": 1,
  "season": 2026,
  "week": 8,
  "runs": 10000,
  "effective_runs": 2049,
  "you": 8,
  "set": [
    {"week": 9, "game": "win", "median": "below"},
    {"week": 10, "game": "loss", "median": "above"}
  ],
  "teams": {
    "8": {"roster_id": 8, "playoff": 46, "bye": 5, "final": 12.0, "title": 5.1,
          "seeds": {"1": 1.0, "2": 3.6, "3": 6.3, "4": 9.0, "5": 11.4, "6": 14.7},
          "final_wins": {"11": 4.6, "12": 9.0, "13": 17.8, "14": 18.7, "15": 21.9, "16": 14.5, "17": 9.0, "18": 3.7, "19": 0.9},
          "mean_wins": 14.48}
  },
  "page": {
    "playoff": 46,
    "ladder": [
      {"more_wins": 4, "chance": 17.8, "playoff": 1},
      {"more_wins": 5, "chance": 18.7, "playoff": 17},
      {"more_wins": 6, "chance": 21.9, "playoff": 70},
      {"more_wins": 7, "chance": 14.5, "playoff": 95},
      {"more_wins": 8, "chance": 9.0, "playoff": 100}
    ],
    "weeks": {
      "10": {"opponent": 7,
             "results": [
               {"game": "win", "median": "above", "chance": 0.0, "playoff": null},
               {"game": "win", "median": "below", "chance": 0.0, "playoff": null},
               {"game": "loss", "median": "above", "chance": 100.0, "playoff": 46},
               {"game": "loss", "median": "below", "chance": 0.0, "playoff": null}],
             "after_loss": 46,
             "root_for": [{"winner": 1, "loser": 6, "playoff": 48},
                          {"winner": 4, "loser": 9, "playoff": 48},
                          {"winner": 11, "loser": 12, "playoff": 48}]},
      "11": {"opponent": 12,
             "results": [
               {"game": "win", "median": "above", "chance": 21.4, "playoff": 79},
               {"game": "win", "median": "below", "chance": 9.4, "playoff": 54},
               {"game": "loss", "median": "above", "chance": 9.3, "playoff": 52},
               {"game": "loss", "median": "below", "chance": 59.9, "playoff": 32}],
             "after_loss": 35,
             "root_for": [{"winner": 10, "loser": 7, "playoff": 36},
                          {"winner": 11, "loser": 1, "playoff": 36},
                          {"winner": 6, "loser": 9, "playoff": 36}]}
    }
  },
  "sample": [
    {"scores": {"8": [101.7, 116.8, 77.6, 104.4, 125.3, 84.1, 130.9, 95.3, 90.0], "...": []},
     "table": [1, 5, 3, 6, 10, 8, 11, 2, 12, 9, 7, 4],
     "bracket": [[[3, 8], [6, 10]], [[1, 8], [5, 10]], [[5, 8]]],
     "champion": 5}
  ]
}
```

The page derives the rest itself. The sentence "Win 6 of the 8 left" is the smallest `more_wins` with `playoff` of 90 or more. The wins a tile adds come from the tile (2, 1, 1, or 0). The reason of a root-for row comes from `records` in sim.json.

A league with no median game gives two results per week, with `median` null.

### The size

Command `median.py response <scratchpad>`, compact JSON as `write_sim` writes it (`packages/sim/python/src/sim/published.py:31-39`), gzip level 9:

| Body | Raw | Gzip |
|---|---|---|
| Response, no set result, 200 runs | 162,247 B | 44,549 B |
| Response, 4 set results, 200 runs | 161,889 B | 44,314 B |
| The same with no sample | 6,238 B | 1,613 B |
| The `page` block alone | 2,769 B | 514 B |
| A `pages` block for all 12 teams, for sim.json | 36,193 B | 3,697 B |
| The fixture sim.json today | 161,014 B | 45,132 B |

- One stored run costs about 215 B gzip: (44,549 - 1,641) / 200. A sample of 50 runs gives a response of about 12 KB gzip.
- The API sets no gzip now: `grep -rni "gzip\|GZipMiddleware" apps/api/src apps/api/fly.toml` finds nothing. Starlette's `GZipMiddleware` (https://www.starlette.io/middleware/#gzipmiddleware) cuts the body by about 3.6 times.
- The `pages` block adds about 8 % to the gzip size of sim.json, which stays under the 50 KB gzip cap of the sample (`packages/sim/python/src/sim/tunables.py:8-9`).

### How it relates to sim.json

- `teams` uses the shape of `teamSimSchema` (`packages/sim/site/schema/sim.ts:25-34`), and `sample` uses `simRunSchema` (`sim.ts:14-22`). The page reads both with the parsers it already has.
- `season`, `week`, `runs`, and `schema_version` match `simSchema` (`sim.ts:44-48`).
- The page needs the page numbers before any call, so sim.json must hold them too. Add `pages: record(rosterKey, pageSchema)` to sim.json, with one block per team, because the visitor picks Your team. The response then holds the same `pageSchema` under `page`. The page reads `sim.pages[you]` before a What-if and `response.page` after it, with one parser.
- A Zod sketch, not product code: `whatIfSchema = simSchema.pick({schema_version, season, week, runs, teams, sample}).extend({effective_runs, you, set, page: pageSchema})`. sim.json can carry `effective_runs` equal to `runs`, so a reader never needs a branch.
- `sim/published.py` owns the shape (`packages/sim/site/schema/README.md`, ADR 0013), so the Python side defines `pageSchema` first.

## Sources

- A. B. Owen, *Monte Carlo theory, methods and examples*. Importance sampling and self-normalized importance sampling: chapter 9, https://artowen.su.domains/mc/Ch-var-is.pdf. Conditioning: chapter 8, section 7, https://artowen.su.domains/mc/Ch-var-basic.pdf. Acceptance-rejection: chapter 4, section 7, https://artowen.su.domains/mc/Ch-nonunifrng.pdf. The book index: https://artowen.su.domains/mc/.
- P. S. Efraimidis and P. G. Spirakis, "Weighted random sampling with a reservoir", *Information Processing Letters* 97(5), 2006, https://doi.org/10.1016/j.ipl.2005.11.003.
- Starlette `GZipMiddleware`: https://www.starlette.io/middleware/#gzipmiddleware.
- Decision 01 notes, for the pair draw, the Fly machine, and the event loop: `.scratch/season-sim/decisions/01-research-pick-draw-speed.notes.md`.
