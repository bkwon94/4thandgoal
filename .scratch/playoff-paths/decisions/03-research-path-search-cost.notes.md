# 03 notes: the Path search, the Clinch lines, and their cost

Ticket: `.scratch/playoff-paths/decisions/03-research-path-search-cost.md`. Research date: 2026-11-24.

The scripts are throwaway and live in the session scratchpad, not in the repo:

- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/c788d102-999c-4106-a357-c05493ab68da/scratchpad/paths.py`: the two Path methods, the Week plans, the Clinch lines, the sizes, and a seed check.
- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/c788d102-999c-4106-a357-c05493ab68da/scratchpad/timing.py`: the interleaved times, best of 5.
- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/c788d102-999c-4106-a357-c05493ab68da/scratchpad/sizes.py`: the size variants of `sim.json`.
- `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/c788d102-999c-4106-a357-c05493ab68da/scratchpad/week6.py`: the week file of cpc week 6, to size a week with 8 weeks left.

Run each with `uv run --exact --package cpc-sim python -I <script> ...` from the worktree root. `week6.py` needs `--package cornerstone` from `apps/pipeline`.

## Summary

- **Method:** use a greedy cover (method A). For each Finish, it adds the most decisive condition first, by FOIL gain, and stops at 90 % odds of the Goal. Then it removes the runs that the Path covers and finds the next Path. The odds of each Path are plain counts of runs, so they are exact up to sample noise.
- **Readability:** method A gives short Paths on the teams in the race, such as "Bo Girds wins at most 3 of 6; Omarion Himpton wins at most 4 of 6 → 97 %, happens 33 %". Method B, a count of the most common condition sets (Apriori), finds Paths that happen more often, but it fills them with weak conditions, such as "NFC Least wins at least 2 of 6".
- **Coverage:** a Path at 90 % exists for only 11 % to 34 % of the open Finishes. Most Finishes under about 50 % odds have no Path of 3 teams at 90 %, because many teams race for few spots and Points For breaks many ties. The spec must say what such a Finish shows.
- **Time on the Mac, What-if, one team, all 8 Goals:** the sim takes 0.95 to 1.84 s. The Path add-on adds 0.32 to 0.68 s, or 33 % to 42 % of the sim. 94 % of the add-on is the read of the run records, not the search.
- **Fly:** the measured What-if of cpc week 10 is 1.73 s (AT-22 of `season-sim`). With the add-on, about 2.4 to 2.6 s. With the codes written inside the sim loop, about 2.0 to 2.1 s, an estimate. The machine stays `shared-cpu-1x`, so the cost in money does not change.
- **Size:** the Finish lists, the Paths, the Week plans, the Score to beat, and the League board add 9.7 to 17.5 KB gzip to `sim.json` at week 10 or 11, and 36 KB at week 6. The Week plans hold about 70 % of it.
- **Clinch lines:** an exact enumeration of the results of this week, with the plain check on wins. cpc has 9,024 valid results a week, and NorCal has 64. It takes 1.3 to 1.4 s for cpc in the build and 0.01 s for NorCal. A What-if does not need it.

## 1. What the sim stores, and how a page splits runs today

- `_season_sim` (`packages/sim/python/src/sim/season.py:222`) draws 10,000 runs (`SIM_RUNS`, `tunables.py`). Each run keeps only counters: the playoff spot, the bye, each seed, the final, the title, and each final win total of each team.
- When the call asks for a page, each run also appends a `RunRecord` (`page.py:26`): its weight, the final wins of each team, the playoff teams, the seeds in order, the bracket, the champion, and for each regular week the winners of the head-to-head games and the teams above the median (`season.py`, the `log` list and `_regular`).
- `team_page` (`page.py:184`) reads these records once per team and sums weights into cells: the ladder by more wins, each result of each week, and the root-for rows after a loss. Each number is a split of the runs of one sim (decision 07 of `season-sim`).
- `sim.json` stores 200 runs (`SAMPLE_RUNS`) with their scores, the parameters of the draw, and one page block per team. The What-if (`apps/api/src/cornerstone_api/what_if.py:79`) reruns the sim from the parameters of the latest published week file, with `pages=[you]`.
- So the record that a Path search needs already exists in each What-if: the final wins of each team, the seeds, and the weekly results. The search needs no new draw.

## 2. The inputs

| Label | File | Weeks left | Median game |
| --- | --- | --- | --- |
| cpc 10 | `clients/cpc/published/2026/week-10/sim.json` | 4 (11 to 14) | yes |
| cpc 11 | `clients/cpc/build/2026/week-11/sim.json` of the main checkout. Brian's local build, not published, not in git. | 3 (12 to 14) | yes |
| NorCal 10 | `clients/norcal/published/2026/week-10/sim.json` | 4 (11 to 14) | no |
| cpc 6 | built in the scratchpad by `week6.py` from the saved cpc history of week 6. Names are "Team N". | 8 (7 to 14) | yes |

Each script calls `rerun` on the file, so each run is the run of the build, with the same seed.

The terms of the search:

- A **Finish** of team T is its count of more wins in the weeks left, 0 to 8 in cpc and 0 to 4 in NorCal, with the median game counted.
- A **Goal** is a playoff spot (seeds 1 to 6), a bye (seeds 1 and 2), or one seed. That gives 8 Goals per team.
- A **condition** is "team X wins at most k of N" or "team X wins at least k of N", on the more wins of X in the weeks left.
- A **Path** is a set of conditions on other teams. Its odds are the share of the runs of the Finish and the Path that reach the Goal. Its chance is the share of the runs of the Finish where the Path happens.
- An **open Finish** has at least 100 runs and odds from 1 % to under 90 %. A Finish at 90 % or more needs no Path.

## 3. The Path methods

### Method A: a greedy cover, the most decisive condition first

Each condition and each Finish is a bitset over the 10,000 runs, one Python int. An AND and a popcount (`int.bit_count`) run at C speed.

1. Take the runs of the Finish.
2. Add the condition with the highest FOIL gain: the runs that reach the Goal, times the gain in the log of the odds. Use each team at most once.
3. Stop at 90 % odds, or at 5 conditions. The row shows 3 teams and "and N more results" (MAP, out of scope).
4. Drop each condition that adds less than 2 points of odds.
5. Mark the runs of the Path that reach the Goal as covered. Repeat for up to 5 Paths.
6. A condition true in more than 85 % of the runs of the Finish is skipped, because it says almost nothing.

When no Path reaches 90 %, method A keeps its best Path with its odds, such as "→ 72 %".

Sources: J. R. Quinlan, "Learning logical definitions from relations", Machine Learning 5 (1990), 239 to 266, gives the FOIL gain. W. W. Cohen, "Fast Effective Rule Induction", ICML 1995 (RIPPER), gives the sequential cover. I did not fetch these papers in this session. The method in the script is my own short form.

### Method B: the most common condition sets (Apriori)

1. Take the runs of the Finish that reach the Goal.
2. Keep each condition that holds in at least 100 of them and raises the odds.
3. Join them into sets of 2 and 3 conditions on different teams, Apriori style, and keep the frequent ones.
4. Keep each set with odds of 90 % or more. Rank by chance. Skip a set whose teams include the teams of a set already chosen.

Source: R. Agrawal and R. Srikant, "Fast Algorithms for Mining Association Rules", VLDB 1994. Not fetched in this session.

### The two methods on real data

90 % target, a Path needs 100 runs. "Reach" means a Path at 90 % or more. Method B searches only up to 3 teams.

| Input | Open Finishes | A: reach, any length | A: reach, top Path of 3 teams or fewer | B: reach, 3 teams or fewer | A: median chance of the top Path | B: median chance of the top Path |
| --- | --- | --- | --- | --- | --- | --- |
| NorCal 10 | 145 | 27 | 19 | 21 | 15.4 % | 31.0 % |
| cpc 10 | 249 | 39 | 28 | 29 | 34.8 % | 39.2 % |
| cpc 11 | 203 | 69 | 34 | 36 | 13.9 % | 31.8 % |
| cpc 6 | 396 | 49 | 37 | 42 | 30.6 % | 44.5 % |

The coverage at a lower target, method A, Paths of 3 teams or fewer:

| Input | 90 % | 80 % | 70 % |
| --- | --- | --- | --- |
| NorCal 10 | 19 of 145 | 31 | 38 |
| cpc 10 | 28 of 249 | 40 | 58 |
| cpc 11 | 34 of 203 | 52 | 81 |
| cpc 6 | 37 of 396 | 58 | 78 |

### Readability

Method B finds Paths that happen more often, but it reaches 90 % with filler. cpc 11, Puka Deez... at 13-9, Finish 2 of 6 (86 %):

```
A  Bo Girds wins at most 3 of 6 -> 96%, happens 42.9%
A  💿 🐑 wins at most 2 of 6 -> 97%, happens 33.4%
A  Bengals Buddies wins at most 2 of 6 -> 94%, happens 45%
B  Bo Girds wins at most 4 of 6 -> 91%, happens 71.2%
B  NFC Least wins at least 2 of 6; Immaculate Concepcion wins at least 1 of 6 -> 90%, happens 64.4%
B  Immaculate Concepcion wins at least 1 of 6; Nico Collinsizer wins at least 2 of 6 -> 90%, happens 59.9%
```

The B rows name teams out of the race, and each one only nudges the odds over 90 %. A manager cannot act on "Immaculate Concepcion wins at least 1 of 6". Method A names the rivals for the spot. So method A reads better.

### Exactness up to sample noise

- Both methods read the odds of a Path as a plain count of runs. So each number is exact up to sample noise. At 100 runs and 90 % odds, the standard error is 3 points. At 400 runs, it is 1.5 points.
- The choice of the top Path is less stable than its odds. With a second seed, the top Path of the playoff Goal stays the same in about half of the cases at weeks 10 and 11. The odds move by up to 5 points and the chance by up to 7 points. At cpc week 6 it changes in 20 of 24 cases, with up to 19 points of odds, because each Path holds few runs.
- With a floor of 400 runs per Path (`ABOUT_RUNS`), the odds move by at most 1 point at cpc 11 and cpc 6. A change of the top Path is then a swap of two Paths of near-equal odds. The cost is fewer Paths: cpc 11 has 19 Finishes with a Path of 3 teams at 90 %, against 34 at 100 runs.
- The build has a fixed seed, so one input gives one output. A What-if with no set result gives the same Paths again.
- A What-if has weighted runs. The script resamples them to 10,000 equal runs, which adds a little noise. The product can resample for the search and then sum the exact weights of the 3 to 5 chosen Paths.

### Sample Paths from real data

cpc 11, Bo Girds at 11-11, Goal a playoff spot:

```
Finish 2 of 6: 3% (chance 20%)
Finish 3 of 6: 25% (chance 20%)
  Path  💿 🐑 wins at most 1 of 6; Omarion Himpton wins at most 3 of 6 -> 90%, happens 7.7%
Finish 4 of 6: 80% (chance 25.7%)
  Path  💿 🐑 wins at most 2 of 6 -> 94%, happens 44.2%
  Path  Bengals Buddies wins at most 2 of 6 -> 93%, happens 45.8%
  Path  The Blue Tent wins at most 2 of 6 -> 91%, happens 30.1%
Finish 5 of 6: 99%
```

cpc 11, The Blue Tent at 13-9, Goal a bye:

```
Finish 4 of 6: 9% (chance 26%)
  Path (best, below 90%)  Maye d'force B with U wins at most 2 of 6; Puka Deez... wins at most 3 of 6;
                          💿 🐑 wins at most 3 of 6 and 1 more results -> 83%, happens 4.2%
Finish 5 of 6: 45% (chance 14%)
  Path  Maye d'force B with U wins at most 3 of 6; Puka Deez... wins at most 4 of 6 -> 93%, happens 30.6%
  Path  Lil Fridge wins at most 2 of 6; Puka Deez... wins at most 4 of 6 -> 96%, happens 18.6%
Finish 6 of 6: 83% (chance 10.7%)
  Path  Maye d'force B with U wins at most 4 of 6 -> 96%, happens 69.3%
```

NorCal 10, Skol Daddy at 5-5, Goal a playoff spot:

```
Finish 1 of 4: 1% (chance 23.5%)
Finish 2 of 4: 72% (chance 37%)
  Path  Bo Girds wins at most 2 of 4; Breece Mode wins at most 2 of 4 -> 91%, happens 41.3%
  Path  Davlionman wins at most 1 of 4; kaiedmonds wins at most 2 of 4 -> 95%, happens 19.1%
  Path  BobBuckstein wins at most 2 of 4; kaiedmonds wins at most 2 of 4 -> 93%, happens 24.3%
Finish 3 of 4: 100%
```

### The Week plan

The script builds one Week plan for each Finish and each Path. Each row of a week holds:

- the results of Your team in the most common order over the runs of the Path that reach the Goal;
- an "any order" flag, true when the odds of the Goal move by 5 points or less over the orders with 100 runs or more;
- the 1 or 2 winners of other games in that week that lift the odds most, by 1 point or more;
- the Score to beat at 50 % and 80 %, against the opponent and the median. It comes from the parameters of the draw: the opponent score is normal with the mean `level_mean + shift` and the sd `sqrt(spread² + level_se²)`. The median line comes from 10,000 draws of the week. It depends on the team and the week, not on the Path, so it is stored once per team and week.

cpc 11, The Blue Tent, bye, Finish 5 of 6, Week plan:

```
wk 12 vs 💿 🐑: win, above median; score to beat 107.8/126.4, median 107.9/114.3; root for NFC Least (-> 96%)
wk 13 vs Nico Collinsizer: 1 of 2; score to beat 104.3/122.9, median 106.7/113.3;
                           root for Maye d'force B with U (-> 97%), Unsolicited Dak Picks (-> 97%)
wk 14 vs Bengals Buddies: win, above median; score to beat 103.4/122, median 107.1/113.3;
                          root for Puka Deez... (-> 99%), Omarion Himpton (-> 94%)
order share 0.42, any order false
```

## 4. The Clinch lines

Method: an exact enumeration of the results of this week, with the plain check on wins (`roster_status`, `packages/league/python/src/league/standings_table.py:140`).

1. List each valid result of this week as the more wins of each team. In a game, the winner gets 1 plus 1 above the median, and the loser gets 1 above the median only if the winner is above it too. With a median game, exactly half the league is above the line. cpc has 9,024 valid results. NorCal has no median game, so it has 2^6 = 64.
2. For each result, apply `roster_status` with one week fewer to each team, at 6 spots, 2 spots, and each seed. A seed n is Clinched when the team is in the top n and is out of the top n-1. It is Out when the team is out of the top n, or in the top n-1.
3. For each team and Goal, find up to 3 Clinch lines that each surely give Clinched, or Out. A line is a set of up to 4 conditions on the wins of this week, such as "wins 2 of 2" or "Bo Girds wins at most 1 of 2". The greedy step adds the condition with the best share of Clinched results. A line counts only when each result that fits it is Clinched, so a line is never wrong.
4. The chance of each line is the share of the runs of the sim where the week fits it.

The plain check counts a tie on wins as not sure, as GLOSSARY.md says. A tie on wins that Points For breaks never gives Clinched.

Sample Clinch lines from real data:

```
cpc 11  Lil Fridge (15-7), playoff spot: Clinched if Lil Fridge wins 2 of 2 and Bo Girds wins at most 1 of 2 (happens 24.2%)
cpc 11  Maye d'force B with U (14-8), playoff spot: Clinched if it wins 2 of 2, Bo Girds wins 0 of 2,
        Nico Collinsizer wins at most 1 of 2, and Omarion Himpton wins at most 1 of 2 (happens 2.5%)
cpc 11  Bo Girds (11-11), bye: Out if Bo Girds wins 0 of 2, Maye d'force B with U wins 2 of 2,
        and Lil Fridge wins at least 1 of 2 (happens 10.5%)
cpc 11  NFC Least and Unsolicited Dak Picks: already Out of a playoff spot
cpc 10  NFC Least (3-17), playoff spot: Out if NFC Least wins at most 1 of 2 (happens 59%),
        or if Bo Girds wins at least 1 of 2 (happens 49%)
NorCal 10  VarsityBlue2 (5-5), bye: Out if VarsityBlue2 loses (happens 53.8%)
```

- The lines of a team can be more than 3. The script marks such a set "incomplete". The spec must decide if the board shows "and other results".
- No team can clinch a playoff spot in NorCal week 11 by the plain check, and only the bye has Out lines. 4 weeks of 1 game leave too much reach.

## 5. The times

Apple M2 Pro, 10 cores (`sysctl -n machdep.cpu.brand_string hw.ncpu`). The Mac was under load from other sessions: the load average was 12 to 44 on 10 cores. So each time is a best of 5, interleaved, and the ratio of the add-on to the sim is the more useful number. Command: `uv run --exact --package cpc-sim python -I timing.py 5 <files>`.

### One What-if: one team, one set result in the first week, all 8 Goals

| Input | Sim (`rerun`, `pages=[you]`) | Read of the runs to bitsets | Path search and Week plans, 8 Goals | Search, playoff Goal only | Add-on over the sim |
| --- | --- | --- | --- | --- | --- |
| cpc 10 | 1.076 s | 0.347 s | 0.100 s | 0.015 s | +42 % |
| cpc 11 | 0.948 s | 0.222 s | 0.093 s | 0.015 s | +33 % |
| NorCal 10 | 0.999 s | 0.266 s | 0.071 s | 0.014 s | +34 % |
| cpc 6 | 1.844 s | 0.590 s | 0.093 s | 0.018 s | +37 % |

A split test (`timing2.py` in the scratchpad) shows that the read of the run records takes 0.285 s of the 0.302 s of the bitsets at cpc 10. The bitset step itself takes about 0.02 s. The read loops over the `RunRecord` objects in Python. If the sim loop writes one byte per team and per week into a buffer as it runs, most of the read goes away. My estimate for that write is 0.05 to 0.1 s per call. I did not measure it.

### The full build: all 12 teams, all 8 Goals

| Input | Sim with all pages | Bitsets | Paths and Week plans, method A | Paths, method A, no plans | Paths, method B, no plans | Clinch lines |
| --- | --- | --- | --- | --- | --- | --- |
| cpc 10 | 1.205 s | 0.336 s | 0.652 s | 0.08 s | 0.52 s | 1.414 s |
| cpc 11 | 1.014 s | 0.253 s | 0.586 s | 0.06 s | 0.35 s | 1.346 s |
| NorCal 10 | 1.095 s | 0.280 s | 0.543 s | 0.04 s | 0.80 s | 0.010 s |
| cpc 6 | 1.908 s | 0.676 s | 0.791 s | 0.15 s | 1.61 s | 1.302 s |

The method B times come from the single run of `paths.py`, not from the best of 5. The build runs on the Mac in the weekly pipeline, not on Fly. So the build adds about 2 to 3 s to the weekly build, at no Fly cost.

## 6. The cost on Fly

The measured ratio. The task says that decision 01 of `season-sim` holds a measured ratio of Fly to the Mac. It does not. Decision 01 gives an estimate of 1.3 to 2 times, because Docker hung. A real measure exists in `.scratch/season-sim/EVIDENCE.md`, AT-22 and AT-23:

- Release v62 on `shared-cpu-1x`, 1 GB, 2026-11-19. 10 What-if calls of cpc, one at a time, after 10 minutes idle: 1.55 to 1.90 s, median 1.73 s (`.scratch/season-sim/evidence/AT-22/idle.txt`). Just after a deploy: median 1.79 s.
- The week file then was cpc week 10, the same file as the cpc 10 input here.
- The Mac time of the same sim is 0.90 s (decision 07) to 1.08 s (this session, under load). So a full Fly call is 1.6 to 1.9 times the Mac sim. The Fly time also holds the network, the JSON, and the gzip, so the true CPU ratio is a little lower.

The estimate for one What-if with the Path add-on:

| Case | Mac add-on | Fly add-on (x 1.6 to 1.9) | Fly call |
| --- | --- | --- | --- |
| cpc 10 shape, as built here | 0.45 s | 0.72 to 0.86 s | about 2.4 to 2.6 s |
| cpc 10 shape, codes written in the sim loop (estimate) | about 0.15 to 0.2 s | about 0.25 to 0.4 s | about 2.0 to 2.1 s |
| cpc 6 shape, 8 weeks left, as built here | 0.68 s | 1.1 to 1.3 s | about 4.0 s (the sim alone is about 2.9 s) |
| Paths of the playoff Goal only, codes in the loop | about 0.1 s | about 0.2 s | about 1.9 to 2.0 s |

These Fly numbers are an estimate from a measured base. I deployed nothing.

The cost in money: none. The machine is one `shared-cpu-1x` that always runs (`apps/api/fly.toml:28-41`), at a fixed price. The add-on uses more of the CPU burst balance (https://docs.fly.io/machines/cpu-performance: a baseline of 6.25 %, a balance of up to 500 s):

- Now, about 1.7 s of CPU per call: a full balance covers about 290 calls in a row, and the refill covers about 130 calls an hour.
- With the add-on as built here, about 2.5 s: about 200 calls in a row and about 90 calls an hour.
- With the codes in the sim loop, about 2.0 s: about 250 calls in a row and about 110 calls an hour.

The two leagues have about 24 managers. So the add-on stays on the burst in normal use. The bar of AT-22 of `season-sim` was a median of 2.5 s. The add-on as built here sits at that bar for week 10, and over it early in a season.

The What-if answer grows by 1.2 to 3.1 KB gzip for the Paths of one team and all 8 Goals (raw 13.5 to 46.6 KB). The answer today is 37,096 bytes (AT-22).

## 7. The size in sim.json

Compact JSON with long keys, as `write_week_sim` writes it. gzip at level 9. All 12 teams.

| Part | cpc 10 | cpc 11 | NorCal 10 | cpc 6 |
| --- | --- | --- | --- | --- |
| Finish lists and Paths, all 8 Goals | 71.8 KB raw, 4.7 KB gzip | 58.5 KB, 3.9 KB | 42.4 KB, 2.9 KB | 108.8 KB, 6.8 KB |
| The same with the Week plans of each Finish and each Path | 264.6 KB, 16.6 KB | 189.4 KB, 12.2 KB | 157.7 KB, 9.7 KB | 589.5 KB, 35.3 KB |
| Score to beat | 4.3 KB, 0.5 KB | 3.2 KB, 0.4 KB | 2.6 KB, 0.4 KB | 8.5 KB, 0.9 KB |
| League board with the Clinch lines | 5.1 KB, 0.4 KB | 8.1 KB, 0.6 KB | 4.6 KB, 0.4 KB | 2.3 KB, 0.1 KB |
| All new parts | 274.1 KB, 17.5 KB | 200.7 KB, 13.0 KB | 164.9 KB, 10.5 KB | 600.3 KB, 36.3 KB |
| sim.json now | 172.9 KB, 38.8 KB | 148.9 KB, 32.9 KB | 164.5 KB, 38.4 KB | 259.1 KB, 60.2 KB |
| sim.json with all new parts | 446.9 KB, 56.6 KB | 349.6 KB, 46.0 KB | 329.4 KB, 49.1 KB | 859.4 KB, 96.5 KB |
| sim.json lean: playoff and bye only, Week plans of each Finish only | 238.8 KB, 43.9 KB | 200.0 KB, 36.9 KB | 203.8 KB, 41.6 KB | 394.7 KB, 69.3 KB |

- The Week plans hold about 70 % of the new bytes, and the 6 seed Goals hold about 65 %.
- `tunables.py` says that 200 stored runs keep `sim.json` under 50 KB gzip. cpc week 6 is already at 60.2 KB gzip today. The full new parts take cpc week 10 to 56.6 KB.
- The page can build a Week plan of a Path from the parts it already has. The sum of the plan rows is the cost of the size, not of the search.

## 8. The fallback if the cost is too high

In order, cheapest loss first:

1. Write the per-run codes inside the sim loop, not from the `RunRecord` list. This keeps every Path after a What-if and cuts most of the add-on. It is a change to `_season_sim`, so it needs a parity test with the current numbers.
2. After a What-if, find the Paths of the Goal on screen only, and leave the other Goals for the next tap. The search of one Goal takes 0.015 s on the Mac.
3. Leave out the Paths after a What-if, as the map says. The Finish list still comes from the split of the runs. The page shows the Paths of the build with a note that they hold no set result.
4. Run 5,000 runs for a What-if with Paths. This halves the sim time (decision 01 of `season-sim`), but it halves the runs of each Path too, so fewer Paths pass the floor.

For the size: store the Week plans of each Finish only, and of the playoff and bye Goals in full. Build the plan of a seed Goal or of a Path in the API on a tap, or leave it out.

## 9. Recommended decision

Use method A, a greedy cover by FOIL gain on conditions "X wins at most or at least k of N", with a 90 % stop, up to 3 teams shown plus "and N more results", and a floor of 400 runs per Path. A Finish with no Path at 90 % shows its best Path with its odds, which is the common case under about 50 %, so decision 06 must give its copy. The Clinch lines come from an exact enumeration of the results of this week with `roster_status`, in the build only. The What-if keeps its Paths on `shared-cpu-1x` at about 2.0 to 2.6 s on Fly and no extra cost in money, best when the sim loop writes the per-run codes; the fallback is the Paths of the Goal on screen only, then no Paths after a What-if. Keep `sim.json` lean: a Week plan for each Finish, and the full Paths and plans for the playoff and bye Goals only.
