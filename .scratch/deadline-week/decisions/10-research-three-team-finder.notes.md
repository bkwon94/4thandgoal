# 10 notes: how the Finder can find a three-team trade, and at what cost and speed

Ticket: `10-research-three-team-finder.md`. Map: `../MAP.md`. Next: `11-grill-three-team-finder.md`.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`. Each source is a file of this repo, read on 2026-11-19.
Each line number is the line in that file now. Each team is its roster id. The notes name no manager and no team name.
The player names are only those of the Backtest marks: Walker, Mahomes, Flowers, and Goff.

## Summary

- **The shape is a ring:** the asker gives to B, B gives to C, and C gives to the asker. Only a ring makes a trade that no pair of teams can do alone. The request shape already fits it, and the form already defaults to it.
- **The steps change in four places:** the Spares tree must run on all 132 ordered pairs, not on 22. Code joins three Spares edges into a ring. The offer build and two hard-rule checks must read N sides. The pick prompt must speak of two other managers.
- **The cut that decides everything is the code list of the Spares tree.** Under the reading of decision 09 ("a bench player above the line"), only 29 of 132 ordered pairs list any player. Then no asker has one ring. Under the literal reading of decision 05 ("a backup above the line behind him"), 117 of 132 pairs list a player. Then each asker has 55 to 95 rings and 1,767 to 6,431 one-for-one-for-one offers.
- **A cut with no score:** the aim position of the manager, plus an "unlock" rule. The unlock rule keeps a ring only when the asker has no two-team trade with C, the team that sends him the player. That is the reason for a three-team trade. With RB as the aim, it leaves 8 to 22 rings for 5 askers and none for 7 askers.
- **One replayed press** (asker 8, aim RB, unlock rule, at most 2 players per edge) built 172 offers. The Jev steps took 3.3 s. The pick call took 26.0 s. The press cost $0.108. A two-team press is about 25 s and $0.07 after the cuts of decision 02.
- **The replay shows the bugs of decisions 01 and 09 again, and worse.** All 10 Shortlist offers gave the same player of the asker. 8 of the 10 lowered the lineup of the asker. The Advisor picked one that loses 2.2 points a week, and its Bullets spoke of one other manager only.
- **Build:** about 3 to 4 days on top of the two-team Finder of this spec. **Can it ship before the Lock without risk to the event? No.**
- Spend: **$0.148** of the $0.50 cap. $0.086 was Claude, one pick call. $0.062 was Jev, 4 runs.

## 1. How each step of the Finder changes for three sides

The path of one press now: `POST /find` (`packages/analyzer/python/src/analyzer/routes.py:356`) calls `find_trades` (`routes.py:365`). `find_trades` calls `_find` (`routes.py:375`), and `_find` calls `finder_search` then `finder_pick`. The search is `search` (`packages/analyzer/python/src/analyzer/finder_search.py:386-499`). The pick is `pick_trades` (`packages/analyzer/python/src/analyzer/finder_pick.py:322-367`).

| Step | Two teams now | Three teams | Change |
| --- | --- | --- | --- |
| Partner filter, then the Spares tree of decision 05 | One request per partner: 11 pairs, with both ways in one state (`finder_search.py:421-432`). Decision 05 swaps the four questions for the Spares tree. | A ring needs the edge "B can spare a player to C" between two teams that are not the asker. So the tree runs on every ordered pair: 132, with 110 more than now. | Run the same tree over all pairs. Code joins three edges into a ring. The Deadline board already runs the tree for the spares of each team (decision 05), so one run per roster change can feed both. |
| Targets | One Jev target question per pool player of both sides (`finder_search.py:202-224`, `:437-459`). At most `TARGET_MAX` 4 per side, by probability (`:71-72`, `:227-231`). | The Spares Nouls already name each player who would start for the team that gets him. So the edge list is the target list, and the target step folds into the tree. | A cap per edge, by the order of the Jev answer, as `_pick_targets` does now. Brian must say if this order counts as a score screen (section 3). |
| Offer build | `build_offers` makes 1-for-1, 2-for-1, and 1-for-2 between two rosters, with `to` set to the other side (`finder_search.py:247-270`). | A new ring builder: side A gives p1 `to` B, B gives p2 `to` C, C gives p3 `to` A. Start with 1-for-1-for-1 only. `ProposedTrade` takes 2 to 4 sides (`packages/analyzer/python/src/analyzer/trade.py:43-87`), and `trade_handcuffs` already reads N sides (`packages/analyzer/python/src/analyzer/measures.py:235-247`). | `_within` (`finder_search.py:191-199`) and `_holds` (`:242-244`) read `sides[0]` and `sides[1]`. They must read "what the asker gives" and "what the asker gets" by roster id. `wider_offers` (`:307-347`) stays two-team. |
| Shortlist | One request per partner with `fair` and `need.<side>` per offer. The 10 best by the product stay (`finder_search.py:478-495`). The offers group by `trade.sides[1].roster_id` (`:468`). | `trade_jev_questions` already asks for N sides: paths `partner_1` and `partner_2`, and "every team" in `fair` (`packages/analyzer/python/src/analyzer/trade_jev.py:98-103`, `:126-146`). | Group by the pair (B, C), with three team states. The gain Noul of decision 09 runs once per side, so 3 per offer. That makes 7 Nouls per offer, against 5 for two teams. The variety rule of decision 01 must count each player of the asker and each ring pair. |
| Pick | One Advisor call over at most 10 offers (`finder_pick.py:337-342`). `side_lines` (`packages/analyzer/python/src/analyzer/advisor.py:144-155`) and `_echoed_sides` (`routes.py:175-190`) already write N sides with `to` and `from`. | The same one call. In the replay, each pick guard passed on a three-side offer. | The prompt says "the other manager would take" and "why the other manager says yes" (`packages/analyzer/python/src/analyzer/prompts/finder_pick.md:32`, `:39`). For a ring it must say "each other manager". In the replay, the pick named one other manager only. A label `A` to `J` (decision 02) also covers the longer three-part id (`finder_search.py:350-352`). |
| Route and cache | `FindRequest` holds `partner: int \| None` (`routes.py:293-305`). `trade_pair` names one partner (`routes.py:344`). | It needs a field for three teams, such as `teams: 2 \| 3`. | `finder_cache_key` must hold that field (`packages/analyzer/python/src/analyzer/cache.py:172-197`), or a three-team press can serve the two-team list. |
| Site | The finder hides at three sides (`packages/analyzer/site/form/trade-form.tsx:199`, `:449`). A card fills two sides (`trade-form.tsx:282-298`). | The `SwapCard` already shows a row per side past two sides (`packages/analyzer/site/form/analyze-result.tsx:138`). | `openTrade` must fill three sides with each destination. The Finder of decision 07 needs the "2 teams · 3 teams" choice. The front door builds `FindRequest` at `apps/api/src/cornerstone_api/trade_topics.py:438`, so a typed "three-team" needs one more read of the question. |

## 2. The shape of a three-team offer

The request shape: each given player names the roster he goes to (`trade.py:23-28`, ADR 0008). Each side must give one player and get one player (`trade.py:66-82`).

1. **A ring: A to B, B to C, C to A.** Each side gives one and gets one. No pair can do it alone, because C does not want what A has. B does. That is the only case where a third team adds a trade. The form already defaults to a ring: "the default destination is the next side in order, and the first side for the last" (`.scratch/analyzer-multi-team/PRD.md:63`, `:199`). So a ring opens in the analyzer with no change of destination.
2. **A hub: A gives to B and to C, and gets from both.** The request shape takes it. But it is two two-team trades side by side. The two-team Finder already finds each half. A hub with B as the center has the same fault.

The ring fits the request shape best. Each of the two directions of one pair of teams is its own ring: A to B to C, or A to C to B. So 11 other teams give 110 directed rings, the 55 pairs times 2.

## 3. How to keep the search small

### Method

- Data: the saved CPC week 10 raw folder, `clients/cpc/data/2026/week-10/raw/`. Its rosters are from 2026-11-17, so they are the rosters of week 11, as in decision 09. It loaded with `_saved_snapshot` of `apps/pipeline/src/cornerstone/cli.py:166`. No fetch ran.
- Code: a throwaway script in the session scratchpad. It ran the Spares Nouls of decision 05 on all 132 ordered pairs, through `JevWaves`. Each Noul read "Would {player} start over {weak starter} of {team} for the rest of the season?". A fact gave the lineup points a week of both players, as the S1 state of decision 09 did. The saved week has no chart read, so no chart value was in the state.
- An edge "T can spare p to U" stands when the answer is not a clear no (0.3 or more), as decision 05 sets. A count with "yes" only (above 0.7) cut the rings by 15% or less for 11 askers, and by 43% for one.
- The `Meter` and `MeteredJev` of `apps/pipeline/src/cornerstone/advisor_eval.py:215`, `:242` counted the cost. The script changed no product code. It and its output are deleted.

### The code list of the Spares tree decides the size

Decision 05 says code lists each player of a team at the position of a weak slot of the other team, "with a backup above the line behind him". The script tried both readings.

| Reading of the code list | Ordered pairs that list a player | Rings per asker | 1-for-1-for-1 offers per asker | Two-team partners per asker |
| --- | --- | --- | --- | --- |
| Surplus: the team has more players above the line who can play now at that position than it starts there. This is how decision 09 reads it: "no bench WR is above the line, so Flowers ... are not listed". | 29 of 132 | 0 for each of 12 | 0 | 0 to 3 |
| Depth 2: the team has 2 or more players above the line who can play now at that position. | 117 of 132 | 55 to 95 | 1,767 to 6,431 | 6 to 11 |

So, under the reading of decision 09, a three-team Finder finds nothing on this week. That reading also leaves the two-team Finder few partners. The spec of the Spares tree must fix this reading first. It is a decision of the main spec, not of this ticket.

### Cuts that use only hard rules and Jev answers

Each cut below uses only hard rules and Jev answers. None ranks a trade by a score.

1. **The aim position.** The manager says "I want an RB". That is `Limit.aim_position`, his own hard rule (`finder_search.py:85-91`). C must send a player at that position. With RB, the offers fall to 1,069 to 3,141 per asker, under the depth 2 reading. 4 askers have no ring with an RB at all.
2. **The unlock rule.** Keep a ring only when the asker has no Spares edge to C. That is, no player of the asker would start for C. This is a join of Jev answers by code, the same kind of logic as the gate of decision 05. It keeps only the trades that a two-team trade cannot do.
3. **At most 2 players per edge, by the order of the Jev answer.** `_pick_targets` keeps the top 4 by probability now (`finder_search.py:227-231`). A cap of 2 makes at most 8 offers per ring. **Brian decides** if an order by Jev answer is allowed here. It is the same rule as the targets now, but it is an order, not a judgment of each offer.
4. **The gain Noul of decision 09 on each side.** A clear no drops the offer.

With the depth 2 reading and RB as the aim:

| Asker | Rings | Rings after the unlock rule | Offers after the unlock rule, no cap |
| --- | --- | --- | --- |
| 1 | 70 | 18 | 379 |
| 2 | 86 | 8 | 98 |
| 4 | 86 | 8 | 135 |
| 7 | 55 | 20 | 360 |
| 8 | 61 | 22 | 464 |
| 6, 10, 12 | 95, 95, 68 | 0 | 0 |
| 3, 5, 9, 11 | 0: no RB fits | 0 | 0 |

- 7 of 12 askers get no three-team idea for an RB. For each of them, every team with an RB to spare also takes a two-team trade. So the Finder can say so plainly and show the two-team ideas.
- With any position, the unlock rule leaves 0 to 22 rings. 6 of 12 askers get none.

## 4. The time and the cost of one press

### The replayed press

Asker 8, aim RB, depth 2 reading, unlock rule, 2 players per edge. One pick call, with no news, as `_find_one` runs (`advisor_eval.py:322-351`).

| Step | Requests | Nouls | Offers | Time | Cost |
| --- | --- | --- | --- | --- | --- |
| Spares tree, all ordered pairs | 121, in 2 waves, because 80 a second is the limit (`packages/analyzer/python/src/analyzer/jev_waves.py:18-19`) | 1,224 | | 2.19 s | $0.016 |
| Rings, code | | | 22 rings, 172 offers | about 0 s | |
| Shortlist: fair and 3 needs, no gain Noul | 22, 1 wave | 688 | 172 rated, 10 kept | 1.09 s | $0.005 |
| Pick call, Sonnet 5.5 at medium effort | 1 | | 1 pick, 3 near ideas | 26.0 s: 22,526 in, 2,646 out | $0.086 |
| Jev checks, log only | 4 | | | | under $0.001 |
| Press in all | about 147 | | | **about 31 to 33 s** on the Mac | **$0.108** |

The time in all adds the 10 offer sheets, at 1.0 to 1.8 s one after the other (decision 02). The API keeps the snapshot in memory, so the 1.6 s load of the script does not count.

### Against the two-team press

| | Two teams now, decision 02 | Two teams after the cuts of decisions 01 and 02 | Three teams, measured | Three teams, uncut, estimate |
| --- | --- | --- | --- | --- |
| Jev requests | 23 to 27 | about 37: 11 more targets (decision 01) | about 147 | about 230 |
| Offers built | 11 to 130; 526 over 12 runs | about the same | 172 | 1,000 to 6,400 |
| Jev time | 2 to 3 s, with the wave waits | about 2 s | 3.3 s | 10 to 40 s: the token limit of 100,000 a second sets the pace |
| Pick call | 17 to 21 s, twice with the id retry | 17 to 21 s, once | 26.0 s, once, no retry | same |
| Press in all | 42 to 43 s | about 25 s | about 31 to 33 s | 45 to 75 s |
| Cost | $0.143 to $0.147 | about $0.07 to $0.08 | $0.108 | about $0.15 to $0.25 |

- The estimate for the uncut column: 688 Nouls cost 122,600 Jev tokens in the replay, so about 180 tokens each. 2,340 offers with 4 to 7 Nouls each is 1.6 to 2.9 million tokens. That is 17 to 30 waves at 100,000 tokens a second, and $0.07 to $0.12 of Jev.
- The pick input stays near 23k tokens, as in the two-team press, because the prompt drops repeat facts (`finder_pick.py:147-154`). The output was 2,646 tokens, the top of the two-team range. So the pick costs a few seconds more, not double.
- The Spares run over all pairs costs $0.016 and 2.2 s. It changes with each roster move, as the cache key of decision 02 does. A run per roster move costs cents, not the $0.85 to $1.70 of a Claude prewarm.
- The press stays under the limit of 35 s for a Finder press (manager-brain PRD) only with the label fix of decision 02. One id retry adds 18 to 26 s, so a press would take about 55 s.
- The press was not timed on Fly.

### What the replay picked

- All 10 Shortlist offers gave the same player of the asker, an RB. The top 10 had 5 ring pairs. The variety rule of decision 01 is not built yet, so this repeats the cause of decision 01.
- The Jev `fair` answer had a median of 0.26 over 172 offers. 104 offers were a clear no on `fair`. No offer got a clear no on a need.
- A code count of the lineup points a week, before and after: 8 of the 10 Shortlist offers lower the lineup of the asker, by 0.4 to 2.8 points. One offer lowers the lineup of C by 7.3 points.
- The Advisor picked one offer. It gives that RB of the asker for another RB, at a loss of 2.2 points a week for the asker. Its Bullets said "the other manager can say yes" and named one other team only. This is the bad trade of decision 06 again, with Walker for Mahomes and Flowers for Goff as the marks. The gain Noul of decision 09 is built to stop it. It was not in this replay.

## 5. Days of build, and the Lock

Each estimate counts only the three-team part. It starts after the two-team Finder of this spec, the Spares tree, and the gain Noul are built.

| Part | Days |
| --- | --- |
| Search: the Spares tree on all pairs with a cache per roster move, the ring builder, the unlock rule, the cap per edge, N-side `_within` and `_holds`, the group by ring pair, the gain Noul per side, variety by ring | 1 to 1.5 |
| Pick: the prompt for two other managers, a Backtest mark from the replay, guard tests on a three-side Shortlist | 0.5 |
| Route, cache key, `FindRequest`, and the read of "three-team" in a typed question of the front door | 0.5 |
| Site: the "2 teams · 3 teams" choice in the Finder of decision 07, the three-side card, and `openTrade` for three sides | 0.5 to 1 |
| Evidence, the Judge, and a phone check by Brian | 0.5 |
| **In all** | **3 to 4 days** |

**Can it ship before the Lock (00:00 Eastern Tue 2026-11-24) without risk to the event? No.**

1. The event goes live Fri 2026-11-20 night. The two-team Finder, the Spares tree, and the gain Noul must land first, and they are not built yet.
2. After Friday, about 3 days are left. A three-team build of 3 to 4 days changes `finder_search.py` and `finder_pick.py`, the same code as the live two-team Finder. A new bug there breaks the event Finder.
3. The best case is a ship on Mon 2026-11-23. Sleeper locks trades after the Monday game, so managers get a few hours of use.
4. The code list of the Spares tree has two readings, and one of them finds no ring at all (section 3). That fix must come first, in the main spec.

## 6. Options for Brian

| Option | What it is | Cost per press | Speed | Build days |
| --- | --- | --- | --- | --- |
| **A. A pointer now, a ring search after the deadline** | For the event: when the Finder shows its results, one line says "For a three-team trade, add a team in the analyzer". The analyzer already grades 3 and 4 sides. The Deadline board shows the spares of each team, so a manager can see a ring himself. The ring search becomes its own spec after the Lock, for next season. | $0 more | no change, about 25 s | about 0.25 now, 3 to 4 later |
| **B. A ring search behind its own flag, after the event goes live** | A separate spec from Sat 2026-11-21, with the flag off until Brian checks it on the phone. It ships Mon 2026-11-23 at best. | about $0.11 | about 31 to 33 s, about 55 s with an id retry | 3 to 4, in the 3 days before the Lock |
| **C. A ring search in this spec** | The ring search goes into the deadline-week spec now, with the two-team Finder. | about $0.11 | about 31 to 33 s | 3 to 4 more in this spec, which then misses Fri 2026-11-20 night |

**Recommendation: option A.** The event and the two-team Finder ship on time. No live code changes for three teams in deadline week. The replay shows that a ring search today repeats the faults of decisions 01 and 09 until the variety rule and the gain Noul are built and backtested. The Lock leaves no time for that loop. One fix belongs in this spec under any option: the code list of the Spares tree. Under the reading of decision 09, only 29 of 132 pairs list a player. Brian decides in ticket 11.

## 7. Spend

| Run | Jev | Claude | In all |
| --- | --- | --- | --- |
| 1. Spares tree, surplus reading, all pairs | $0.003 | | $0.003 |
| 2. Spares tree, depth 2 reading, all pairs | $0.016 | | $0.016 |
| 3. Spares tree and the ring Shortlist of asker 8 | $0.021 | | $0.021 |
| 4. The full press of asker 8, with one pick call | $0.021 | $0.086 | $0.108 |
| **Total** | **$0.062** | **$0.086** | **$0.148** of the $0.50 cap |

The `Meter` of `advisor_eval.py` counted each cost, at the prices of `facts/writer.py` and `JEV_INPUT` (`advisor_eval.py:51`). The pick call ran once, with no retry and no repair.
