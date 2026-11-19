# 01 notes: the pick method, the speed, and Sleeper on a long injury

Research notes for `01-research-pick-draw-speed.md`. The scripts are throwaway and live in the session scratchpad, not in the repo:
`/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/409057bd-5de1-426c-9e32-0369adf8d9e4/scratchpad/picks.py` and `.../scratchpad/pair_means.py`.

## Summary

- **Method:** use (d), the conditional draw with a weight. Draw each picked pair from the law of the pair given the order. Then weight the run by the chance that the picks hold, given the drawn levels. This is self-normalized importance sampling. It is exact up to sample noise, and it needs no extra draws. Rejection (a) is exact but needs about 4 billion draws for 20 picks. Swap (b) and the plain conditional draw (c) are biased by up to 2.4 points.
- **Mac time** of 10,000 runs, Apple M2 Pro, method (d): 0 picks 0.64 s, 5 picks 0.72 s, 20 picks 0.92 s. `season_sim` itself: 0.69 s.
- **Fly estimate**, not measured: `shared-cpu-1x`, 1 GB. One call takes about 1 to 1.5 s while the burst balance lasts. At the baseline quota of 6.25 %, one call takes about 11 to 15 s. Docker hung on this Mac, so no container number exists.
- **Event loop:** a sync `def` route runs in the thread pool, so the loop does not block. But the sim holds the GIL and the one vCPU, so each other call slows while a sim runs. An `async def` route that calls the sim blocks every caller for the full time.
- **Sleeper:** Sleeper never gives 0. For each week it expects a player out, it gives an entry with no points key, and our fetch drops it. The blank covers each week of the expected absence, not only the next week. The projection comes back at the expected week of return.

## 1. The pick method

### The model of one run

Each run draws a level per roster, `rng.gauss(level_mean, level_se)` (`packages/sim/python/src/sim/season.py:140`). Then each weekly score is `rng.gauss(level, spread) + shift`, rounded to 1 decimal (`season.py:141`). `spread` is pooled over the league (`season.py:121-123`), and the shift is fixed per roster and week (`season.py:128-129`). So, given the levels, the two scores of one game are two independent normals with known means `level + shift` and one common sd `spread`. `_regular` gives no win on an exact tie (`season.py:203-206`). The median game counts a win above the mean of the two middle scores (`season.py:207-210`, `226-230`). Points for is the tiebreak of the table (`season.py:144`).

The key fact: a pick says something about the levels. A team picked to win is likely stronger, so it also does better in its other games and in the bracket. An exact method must carry that update into the rest of the run.

### The methods

| Method | Exact? | Cost | Points for | Median game |
|---|---|---|---|---|
| (a) Rejection | Yes. It is the definition of the exact odds. | Draws grow as 1 over the accept rate: about 2^k for even picks. | Exact. | Exact. |
| (b) Swap | No. No level update, and the wrong split of the pair. | Same as plain. | The pair sum stays. The split is close but off by about 1 point. | The week line stays. The two teams swap their median wins. |
| (c) Conditional draw | No. The pair is exact given the levels, but no level update. | About plain plus a few percent. | Pair right given the levels. | Line right given the levels. |
| (d) Conditional draw with a weight | Yes, up to sample noise. Self-normalized importance sampling has a bias of order 1 over n. | About plain plus 12 % for 5 picks and plus 43 % for 20 picks. The effective count of runs drops. | Exact in law. | Exact in law. |

How (c) and (d) draw a pair. Let the means be `ma` and `mb` and the sd be `s`. With equal sd, `D = xa - xb` and `S = xa + xb` are independent normals with sd `s * sqrt(2)`. Draw `D` from its normal cut at 0, by the inverse CDF. Draw `S` from its free normal. Then `xa = (S + D) / 2` and `xb = (S - D) / 2`. After the rounding, a tie fails the strict order of `_regular`, so redraw it. Code: `_pair_given_order` in `picks.py`.

How (d) weights a run. The weight is the product over the picks of `Phi((ma - mb) / (s * sqrt(2)))`. This is the chance that the picks hold, given the drawn levels. Picks in one week touch distinct teams, so the chances multiply. Each count of the run, such as a playoff spot, a seed, or a title, adds the weight in place of 1. Divide by the sum of the weights. The effective count of runs is `(sum w)^2 / sum w^2`.

Sources for the methods:

- Importance sampling, self-normalized importance sampling, and its comparison with acceptance-rejection: A. B. Owen, *Monte Carlo theory, methods and examples*, chapter 9, https://artowen.su.domains/mc/Ch-var-is.pdf. The book index is https://artowen.su.domains/mc/.
- Acceptance-rejection: the same book, chapter 4, section 7, https://artowen.su.domains/mc/Ch-nonunifrng.pdf.
- Conditioning as a method: the same book, chapter 8, section 7, https://artowen.su.domains/mc/Ch-var-basic.pdf.
- Gibbs sampling is one more honest method. It is exact in the limit, but it is slower and harder to make deterministic. Chapter 12 of the same book covers it. I do not recommend it here.
- Public fantasy tools: I found no primary source that states how a pick tool draws scores. The FiveThirtyEight NFL method page now redirects to `abcnews.com/politics`, so I could not read it. Do not rely on a claim about it.

### The accept rate of rejection

Command: `uv run --exact --package cornerstone python picks.py compare`. The picks are random games with a random winner, so a set with more underdogs has a lower rate. That is why 5 picks has a lower rate than 8 picks here. The second column is the mean over 20,000 runs of the weight of (d), which is the exact accept rate.

```
accept k=1: counted 0.56760  E[P(picks|levels)] 0.568  draws for 10,000 kept ~ 17,612
accept k=3: counted 0.14160  E[P(picks|levels)] 0.139  draws for 10,000 kept ~ 72,146
accept k=5: counted 0.00320  E[P(picks|levels)] 0.00357  draws for 10,000 kept ~ 2,801,555
accept k=8: counted 0.01085  E[P(picks|levels)] 0.0108  draws for 10,000 kept ~ 921,941
accept k=20: counted 0.00000  E[P(picks|levels)] 2.45e-06  draws for 10,000 kept ~ 4,083,810,291
```

At about 64 µs per run on the Mac, 2.8 million draws take about 3 minutes. 4 billion draws take about 3 days. Rejection is not a live method past 2 or 3 picks.

### The side-by-side odds

The synthetic league has 12 teams, 10 weeks played, 4 weeks left, 6 playoff spots, 2 byes, the median game on, and reseed on. It uses `LeagueSettings` as in `packages/sim/python/tests/test_season.py:16-20`. The reference is rejection over 10 cores: 40,000 kept runs for 3 picks and 20,000 for 8 picks. Swap, cond, and weight each use 40,000 runs. The playoff odds are raw percent, with no clamp. One sample error is about 0.25 to 0.35 points.

3 picks `[(2, 10, 6), (2, 12, 1), (2, 2, 9)]`, as (column, winner, loser). The reference kept 40,000 of 290,522 draws in 2.9 s on 10 cores. The effective runs of (d): 35,532 of 40,000.

```
team    plain   reject     swap     cond   weight
   3     26.3     28.9     27.9     28.2     29.0
   5     17.0     18.1     17.7     17.4     17.7
   6     54.7     39.0     41.2     41.4     39.7
   7     21.0     22.6     22.2     22.3     22.3
   8     97.4     97.6     97.6     97.6     97.6
  10     84.9     94.2     93.9     93.6     94.2
  12     98.8     99.6     99.5     99.5     99.6
max gap swap vs reject: 2.2 pts
max gap cond vs reject: 2.4 pts
max gap weight vs reject: 0.7 pts
```

8 picks `[(2, 10, 6), (2, 12, 1), (3, 5, 9), (3, 8, 12), (2, 9, 2), (3, 11, 7), (1, 6, 2), (0, 11, 6)]`. The reference kept 20,000 of 1,866,827 draws in 17.6 s on 10 cores. The effective runs of (d): 32,182 of 40,000.

```
team    plain   reject     swap     cond   weight
   3     26.3     27.8     28.0     28.3     28.5
   5     17.0     35.1     33.9     33.5     35.1
   6     54.7     32.0     33.2     33.7     31.9
   7     21.0     12.0     12.3     11.9     11.4
   8     97.4     99.8     99.7     99.7     99.8
  10     84.9     94.1     93.7     93.6     94.1
  12     98.8     99.2     99.2     99.3     99.2
max gap swap vs reject: 1.3 pts
max gap cond vs reject: 1.7 pts
max gap weight vs reject: 0.6 pts
```

Teams 1, 2, 4, 9, and 11 show 0.0 or 100.0 in each method and are left out. The gap of (d) is within about 1.5 sample errors. The gap of (b) and (c) is about 6 sample errors on team 6, the picked loser. Both methods keep its level as if it had no loss, so they overrate it.

### Swap and points for, and the median game

Command: `uv run --exact --package cornerstone python pair_means.py <scratchpad>`. It runs 200,000 runs of the one game where roster 10 is picked over roster 6.

```
method   winner_mean  loser_mean  winner_median_win%  loser_median_win%
plain 126.85 120.78 58.12 48.23
reject 139.03 108.58 81.69 24.43
swap 138.06 109.58 80.70 25.66
cond 138.67 108.82 81.29 24.68
weight 138.97 108.51 81.59 24.33
```

- Swap keeps the sum of the pair, so the week line of the median game does not move. But it gives the winner about 1 point too little and the loser about 1 point too much. Its median wins are off by about 1 point too. The error grows when the picked team is a big underdog.
- The exact pair sum also stays at its plain mean: 247.61 under rejection and 247.63 plain. This follows from the independence of `S` and `D`. So the true cost of a pick to points for is a split, not a loss.
- The bigger error of swap and of (c) is in the later weeks and the bracket, from the missed level update. The odds tables above show it.

### Recommendation

Use (d). It is exact, it is cheap, and it treats points for and the median game the same as the plain sim. Show the effective count of runs, or raise the runs when it falls below a floor such as 5,000. A pick of a big underdog drops the effective count faster than a pick of a favorite. The weight also needs the stored sample of runs to be a weighted sample, or a draw of 200 runs with a chance in proportion to the weight.

## 2. The speed

### Mac, measured

Apple M2 Pro, 10 cores (`sysctl -n machdep.cpu.brand_string hw.ncpu`). Command: `uv run --exact --package cornerstone python picks.py timing`. The best of 3 runs is shown for (d).

```
season_sim 10,000 runs, no picks: 0.698 s
season_sim 10,000 runs, no picks: 0.688 s
weight method 10,000 runs, 0 picks: min 0.642 s (of 3), ESS 10,000
weight method 10,000 runs, 5 picks: min 0.718 s (of 3), ESS 6,796
weight method 10,000 runs, 20 picks: min 0.919 s (of 3), ESS 4,845
weight method 5,000 runs, 5 picks: 0.364 s
```

The pick loop in `picks.py` skips the seed counters and the result model of `season_sim`, so it runs about 0.05 s faster. Add that back for a real number: about 0.69 s, 0.77 s, and 0.97 s for 0, 5, and 20 picks.

### Fly machine

`apps/api/fly.toml:39-41`: `size = "shared-cpu-1x"`, `memory = "1gb"`. One machine always runs (`fly.toml:28-30`). Region `ewr` (`fly.toml:6`). The Dockerfile starts one uvicorn process with no `--workers` flag (`apps/api/Dockerfile:66`).

Fly docs, https://docs.fly.io/machines/cpu-performance: a shared vCPU has a baseline of "5ms (6.25%)" per 80 ms. Unused time builds a burst balance that starts at 5 s and can grow to 500 s. While the balance lasts, the vCPU runs at up to 100 %. The page names no CPU model.

### Fly estimate

Docker did not work. `docker info` answered (10 CPUs, 8 GB), but `docker run --cpus=1 ... python:3.12-slim` and then `docker images` hung for more than 3 minutes with no output. I stopped both. The numbers below are an estimate, not a measure.

- The sim is pure Python on one thread, so 1 vCPU at 100 % is the right model. A server core runs Python about 1.3 to 2 times slower than an M2 Pro core. This ratio is my estimate, not a measured number.
- With burst: 0 picks about 0.9 to 1.4 s, 5 picks about 1.0 to 1.5 s, 20 picks about 1.3 to 1.9 s.
- At the baseline of 6.25 %: one call needs about 0.7 to 1.4 s of CPU, so it takes about 11 to 22 s of wall time.
- A full 500 s balance covers about 350 to 550 calls in a row. The idle machine refills it at 6.25 % of real time. A normal league rate of What-if calls stays on the burst.
- Memory is no issue. The sim keeps only counters and 200 stored runs.

### The event loop

FastAPI runs a route declared with plain `def` "in an external threadpool that is then awaited" (https://fastapi.tiangolo.com/async/). The API mixes both kinds: `ask` is a sync `def` (`apps/api/src/cornerstone_api/ask.py:206-207`), and `free` and `next_matchup` are `async def` (`free_answer.py:358`, `next_matchup.py:133`).

- A What-if route as sync `def` does not block the event loop. The loop still accepts calls, and the Claude streams of the ask box still advance.
- But the sim holds the GIL. Python hands the GIL to other threads only at its switch interval, 5 ms by default. On one vCPU, a sim and other work share one core. Each other call is slower while a sim runs, and two sims at once each take about twice as long.
- A What-if route as `async def` that calls the sim directly blocks the whole process for the full time of the sim. Do not do that. If the route must be async, call the sim with `await anyio.to_thread.run_sync(...)` or `starlette.concurrency.run_in_threadpool`.
- The API image does not install the `sim` package now. `apps/api/Dockerfile:24-39` copies only league, facts, analyzer, eggs, and managers. The What-if needs a new line for `packages/sim` there.

### Cheap speedups

- Fewer runs, measured: 5,000 runs with 5 picks take 0.364 s on the Mac, about half of 0.718 s. The sample error of a 50 % odds number goes from 0.5 to 0.7 points. With (d) the effective count falls further, so check it.
- numpy: not tried. numpy is not in the pipeline env (`uv run --exact --package cornerstone python -c "import numpy"` gives `ModuleNotFoundError: No module named 'numpy'`). A vector draw of all scores and the regular weeks is simple. The reseeded bracket per run is harder to vectorize. A numpy port also changes the random stream, so the parity with the weekly odds and the stored sample need a new check.
- A cache by the set of picks: one input gives one output (`season.py:114-115`), so the same picks give the same result. The API already keeps a result cache dir (`fly.toml:15`).

## 3. Sleeper and a long injury

### The fetch

`_projections_ahead` calls `https://api.sleeper.app/projections/nfl/<season>/<week>` for each week from `week + 1` to `last` (`packages/league/python/src/league/provider/sleeper.py:173-185`, `UNOFFICIAL_URL` at line 35). It keeps an item only when `stats` has the points key, such as `pts_half_ppr` (`sleeper.py:182`). So an item with no points key has no entry in `projections_ahead.json`. A zero would stay as `0.0`. The week 10 CPC file has only 0 to 1 zero values per week, so Sleeper does not use zero for an injured player.

The saved files are in git: `git ls-files | grep projections_ahead` lists `clients/cpc/data/2026/week-06` to `week-10` and `clients/norcal/data/2026/week-08` to `week-10`, plus a pipeline test fixture.

### Week 10 of 2026, CPC

The status is from `clients/cpc/data/2026/week-10/raw/players.json`. The projections ahead are from `clients/cpc/data/2026/week-10/raw/projections_ahead.json`, weeks 11 to 17. A dash means no entry.

| Player | Status | Wk 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|
| Puka Nacua, WR LAR | IR, Knee - MCL | - | - | - | - | - | 14.75 | 12.33 | 13.58 |
| Jeremiyah Love, RB ARI | IR, Ankle | - | - | - | - | - | 6.63 | 7.83 | 8.23 |
| De'Von Achane, RB MIA | IR, Knee - ACL | - | - | - | - | - | - | - | - |
| Davante Adams, WR LAR | IR, Hamstring | - | - | 13.48 | 12.91 | 13.36 | 12.89 | 11.01 | 11.98 |
| Kenneth Walker III, RB KC | Out, Groin | - | 17.13 | 18.61 | 17.20 | 21.32 | 20.13 | 17.88 | 20.43 |

The week 10 entries in `projections.json` for Nacua, Achane, Love, and Jackson exist, but `stats` holds one key only and no `pts_half_ppr`.

### The public endpoint

I called the same endpoint read-only, with no league ID: `curl -s "https://api.sleeper.app/projections/nfl/2026/12?season_type=regular&position[]=WR&position[]=RB&position[]=QB"`, and the same for week 15. Each answer holds 2,472 items. Each player out that week has an item with one stat only: `{'adp_dd_ppr': 1000.0}`. For Love in week 12: 4 stats, with `adp_dd_ppr: 999.0`, `gp: 1.0`, and no points. In week 15, Nacua has 24 stats and `pts_half_ppr` 14.75. Love has 29 stats and 6.63. Achane, Jackson, Hurts, and McLaurin still have the one-stat blank in week 15.

### The trace over the saved weeks

The same players in the CPC files of weeks 8, 9, and 10:

- Lamar Jackson: week 8 file, status Out, blank for weeks 9 to 13, then 21.64 from week 14. Week 9 file, IR, blank to week 13, then 19.24 from week 14. Week 10 file, IR, blank in each week 11 to 17. Sleeper moved his return out as the news changed.
- Puka Nacua: week 8 file, healthy, projected in each week except week 11. Week 11 is the LAR bye: the week 10 file projects 0 LAR players in week 11 and 16 in week 12. Week 10 file, IR, blank for weeks 11 to 14, back from week 15.
- Achane, Hurts, McLaurin: blank in each week of each file. Sleeper treats each as out for the season.

### The answer

Sleeper zeroes no player. For each week it expects him out, it gives a blank item with no points key. The blank covers each week of the expected absence, not only the next week. For a player out for the season, it covers each week left. The projection comes back at the expected week of return, and Sleeper moves that week as the news changes. A bye week gives the same blank, so a blank alone does not say "injured".

Our code turns the blank into no entry. `projected_totals` counts a player with no projection as 0, and a healthy bench player or a pool player takes his slot (`packages/week/python/src/week/sheet/base.py:91-95`). So the shift of the season sim already sees a long injury in each week of the absence.
