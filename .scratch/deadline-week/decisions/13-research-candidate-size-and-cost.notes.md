# 13 notes: the candidate count of each shape, and the cost of the Jev calls

Ticket: `13-research-candidate-size-and-cost.md`. Map: `../MAP.md`. Rulings: `.handoff/deadline-week-fair-finder.md`.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`, head `0c6a9127`. Each repo source is a file of this branch, read on 2026-11-19.
Each team is its roster id. Roster 6 is the team of Brian's preview press. The notes name no manager and no team name.
These notes give facts only. Decisions 14 and 15 decide.

## Summary

- With no screen, the four shapes give 95,092 candidates for roster 6, 198,770 for roster 7, and 242,158 for roster 12, over 11 partners. The 3-player shapes are 90% or more of each count.
- A band of 5% of the larger sum still leaves 4,166, 7,730, and 9,957 candidates. A band of 20% leaves 17,585, 32,529, and 42,553. No band of 5% or more leaves zero for a team.
- The 1-for-1 shape stays small: 33 to 42 candidates per asker at 5%, and 112 to 184 at 20%.
- One fair Noul per candidate at the 5% band costs about $0.02 to $0.05 of Jev per press. It sends 13 to 22 requests and about 0.46 to 1.09 million input tokens. That is about 5 to 11 times the per-second token limit of the account. Today's press uses less than one time the limit.
- Today's Spares tree offers of roster 6 mostly fail every band: 2 of 66 pass at 5%, and 5 of 66 pass at 20%. Their median gap is 73% to 80% of the larger sum.
- Two real Jev calls (the only calls of this research, $0.0014) gave no "yes" to the fair question for any of 41 candidates inside the 10% band. Jev said a clear "no" to 12 to 22 of them.

## Method

- Snapshot: the live snapshot of CPC, built the way the API builds it, through `_live_snapshot` (`apps/pipeline/src/cornerstone/cli.py:264-273`) and `live_snapshot` (`apps/api/src/cornerstone_api/sources.py:66-72`). The script printed `week 11 chart_week 11 chart values 126`, `stats_through=11`, `rosters_fetched=2026-11-19 21:45:36 ET`.
- Chart: CPC reads the chart `1QB0.5PPR4pt` (`clients/cpc/client.toml:17`). The week 11 read is the saved file `data/nfl/cache/charts/1QB0.5PPR4pt/week-11.json`, dated 2026-11-17. `check_chart` uses a saved read first (`packages/league/python/src/league/chart.py:320-330`). The script gave a chart reader that raises, so no Claude call ran. 126 chart rows match a Sleeper player. Values go from 0.5 to 68.
- No saved week 11 raw folder exists (`clients/cpc/data/2026/` ends at `week-10`). So these notes use the live rosters, not the saved week 10 folder of decisions 01, 02, and 09.
- Code: throwaway scripts in the session scratchpad. They import the product code and change none. `git status --short` is empty after each run.
- Askers: roster 6, roster 7 (low chart total, 153.5), and roster 12 (the highest chart total, 284.0, and 12 tradeable players).
- Shapes: each shape counts in both directions. "2-for-1" means the asker gives 2 and gets 1. "1-for-2" means the asker gives 1 and gets 2. So the four shapes of ruling 2 are seven rows.
- Gap: `|sum of the asker side - sum of the partner side| / the larger sum`, on the week 11 chart values.
- "Dir" columns add ruling 3: the team that gets more players gets the larger total. A 1-for-1 always passes it.

## 1. The count with no screen

### Which players count as tradeable

A player counts when both rules hold:

1. `in_pool` (`packages/analyzer/python/src/analyzer/finder_search.py:152-156`): a QB, RB, WR, or TE, not Out with no return week, and not a handcuff on his own roster. Today's Finder uses this same rule for its targets (`finder_search.py:203`) and for the Spares tree (`packages/analyzer/python/src/analyzer/spares_tree.py:103`).
2. A week 11 chart value. The value screen sums chart values, so a player with no value cannot have a sum. 29 of the 148 pool players of the league have no chart value. Examples: Justin Herbert, Cam Ward, Mark Andrews, Courtland Sutton, and 5 of the 13 pool players of roster 6.

A candidate also drops when it makes a handcuff on the roster that gets the player. This is the hard rule of `build_offers` (`finder_search.py:252`). The real `trade_handcuffs` dropped 0 of 34,651 1-for-1, 2-for-1, and 1-for-2 trades of the three askers. The fast form of the same rule in the script dropped 0 of all candidates.

"Legal rosters" here means the Sleeper rosters of now. A CPC lineup has 14 slots: 8 starters, a DEF, and 5 BN (`clients/cpc/data/2026/week-10/raw/league.json`, `roster_positions`). Rosters hold 14 or 15 players with IR. No code today checks the roster size after a trade. An uneven shape makes the team that gets more players drop a player in Sleeper. The counts do not remove those trades.

Tradeable players per roster: 1: 10, 2: 9, 3: 10, 4: 10, 5: 7, 6: 8, 7: 11, 8: 10, 9: 10, 10: 12, 11: 10, 12: 12.

### Per shape, summed over 11 partners

| Shape | Roster 6 | Roster 7 | Roster 12 |
| --- | --- | --- | --- |
| 1-for-1 | 888 | 1,188 | 1,284 |
| 2-for-1 | 3,108 | 5,940 | 7,062 |
| 1-for-2 | 4,112 | 5,357 | 5,712 |
| 3-for-1 | 6,216 | 17,820 | 23,540 |
| 1-for-3 | 11,552 | 14,685 | 15,360 |
| 3-for-2 | 28,784 | 80,355 | 104,720 |
| 2-for-3 | 40,432 | 73,425 | 84,480 |
| **All** | **95,092** | **198,770** | **242,158** |

### Per partner, all shapes

| Partner | Roster 6: all | Roster 6: 1-for-1 | Roster 7: all | Roster 7: 1-for-1 | Roster 12: all | Roster 12: 1-for-1 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 8,120 | 80 | 18,150 | 110 | 22,780 | 120 |
| 2 | 6,156 | 72 | 13,959 | 99 | 17,586 | 108 |
| 3 | 8,120 | 80 | 18,150 | 110 | 22,780 | 120 |
| 4 | 8,120 | 80 | 18,150 | 110 | 22,780 | 120 |
| 5 | 3,248 | 56 | 7,623 | 77 | 9,688 | 84 |
| 6 | | | 10,472 | 88 | 13,248 | 96 |
| 7 | 10,472 | 88 | | | 28,908 | 132 |
| 8 | 8,120 | 80 | 18,150 | 110 | 22,780 | 120 |
| 9 | 8,120 | 80 | 18,150 | 110 | 22,780 | 120 |
| 10 | 13,248 | 96 | 28,908 | 132 | 36,048 | 144 |
| 11 | 8,120 | 80 | 18,150 | 110 | 22,780 | 120 |
| 12 | 13,248 | 96 | 28,908 | 132 | | |

The count follows the tradeable count of each side: a 3-for-2 grows with C(n, 3) x C(m, 2).

## 2. The count left at each band

Columns: the relative gap at 5%, 10%, 15%, and 20% of the larger sum; the absolute gap at 3 and 5 chart points; and the 10% and 20% bands with ruling 3 ("dir").

### Roster 6

| Shape | All | 5% | 10% | 15% | 20% | abs 3 | abs 5 | 10% dir | 20% dir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1-for-1 | 888 | 33 | 61 | 83 | 112 | 89 | 132 | 61 | 112 |
| 2-for-1 | 3,108 | 68 | 143 | 216 | 289 | 122 | 192 | 88 | 172 |
| 1-for-2 | 4,112 | 177 | 404 | 592 | 796 | 423 | 696 | 238 | 444 |
| 3-for-1 | 6,216 | 56 | 115 | 178 | 245 | 66 | 109 | 68 | 164 |
| 1-for-3 | 11,552 | 381 | 819 | 1,247 | 1,705 | 735 | 1,185 | 520 | 1,073 |
| 3-for-2 | 28,784 | 887 | 1,824 | 2,799 | 3,868 | 895 | 1,449 | 1,018 | 2,371 |
| 2-for-3 | 40,432 | 2,564 | 5,132 | 7,773 | 10,570 | 3,132 | 4,992 | 2,674 | 5,441 |
| **All** | **95,092** | **4,166** | **8,498** | **12,888** | **17,585** | **5,462** | **8,755** | **4,667** | **9,777** |

### Roster 7

| Shape | All | 5% | 10% | 15% | 20% | abs 3 | abs 5 | 10% dir | 20% dir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1-for-1 | 1,188 | 42 | 90 | 142 | 184 | 246 | 374 | 90 | 184 |
| 2-for-1 | 5,940 | 222 | 482 | 734 | 997 | 664 | 1,092 | 282 | 555 |
| 1-for-2 | 5,357 | 94 | 219 | 323 | 431 | 388 | 611 | 138 | 265 |
| 3-for-1 | 17,820 | 589 | 1,168 | 1,689 | 2,254 | 1,105 | 1,740 | 732 | 1,406 |
| 1-for-3 | 14,685 | 135 | 287 | 406 | 570 | 271 | 434 | 161 | 344 |
| 3-for-2 | 80,355 | 4,516 | 9,298 | 14,000 | 18,813 | 7,821 | 12,473 | 4,933 | 9,731 |
| 2-for-3 | 73,425 | 2,132 | 4,354 | 6,678 | 9,280 | 3,976 | 6,301 | 2,421 | 5,389 |
| **All** | **198,770** | **7,730** | **15,898** | **23,972** | **32,529** | **14,471** | **23,025** | **8,757** | **17,874** |

### Roster 12

| Shape | All | 5% | 10% | 15% | 20% | abs 3 | abs 5 | 10% dir | 20% dir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1-for-1 | 1,284 | 39 | 80 | 123 | 181 | 181 | 284 | 80 | 181 |
| 2-for-1 | 7,062 | 195 | 384 | 555 | 753 | 393 | 628 | 222 | 449 |
| 1-for-2 | 5,712 | 211 | 452 | 687 | 902 | 535 | 872 | 245 | 478 |
| 3-for-1 | 23,540 | 287 | 600 | 965 | 1,383 | 397 | 668 | 358 | 864 |
| 1-for-3 | 15,360 | 428 | 890 | 1,406 | 1,934 | 808 | 1,318 | 511 | 1,148 |
| 3-for-2 | 104,720 | 3,914 | 8,082 | 12,315 | 16,943 | 4,713 | 7,548 | 4,490 | 9,933 |
| 2-for-3 | 84,480 | 4,883 | 10,000 | 15,217 | 20,457 | 6,745 | 10,746 | 5,380 | 10,844 |
| **All** | **242,158** | **9,957** | **20,488** | **31,268** | **42,553** | **13,772** | **22,064** | **11,286** | **23,897** |

### Per partner at the 10% band, all shapes

| Partner | Roster 6 | Roster 7 | Roster 12 |
| --- | --- | --- | --- |
| 1 | 816 | 1,494 | 2,162 |
| 2 | 538 | 1,105 | 1,496 |
| 3 | 684 | 1,270 | 1,825 |
| 4 | 712 | 1,935 | 1,822 |
| 5 | 314 | 603 | 991 |
| 6 | | 853 | 1,304 |
| 7 | 853 | | 2,235 |
| 8 | 732 | 1,413 | 1,971 |
| 9 | 716 | 1,277 | 1,990 |
| 10 | 1,189 | 2,136 | 2,966 |
| 11 | 640 | 1,577 | 1,726 |
| 12 | 1,304 | 2,235 | |

### The absolute band

The chart runs from 0.5 to 68, and 15 of the 119 tradeable players sit under 5. A gap of 3 points is 5% of a 60-point side but 30% of a 10-point side. So the absolute band lets in more trades of low-value players and fewer trades of stars. For roster 7, whose players are mostly between 7.5 and 13.5, `abs 3` keeps 246 1-for-1 candidates against 42 at 5%.

## 3. The Jev calls per press

### The calls of today, with file and line

A press with no partner and no anchor sends these requests. Each request holds many Nouls.

| Step | Requests | Nouls per request | Source |
| --- | --- | --- | --- |
| Spares tree | One per partner that lists a player: 11 | One per listed player of both sides | `finder_search.py:504-511`, `spares_tree.py:140-158` |
| Targets | One per partner that passes | One per pool player of both sides | `finder_search.py:534-536`, `finder_search.py:186-208` |
| Shortlist | One per partner with offers | 5 per offer: `fair`, `need` x2, `gain` x2 | `finder_search.py:576-577`, `finder_search.py:410-427` |
| Pick checks, log only | One per pick and per near idea, after the Answer | 1 to 4 | `packages/analyzer/python/src/analyzer/finder_pick.py:382-389`, `:427`; `read_jev_check.py:81` |

Code caps the offers of today: at most 4 targets per side (`finder_search.py:49-50`), so at most 16 + 24 + 24 = 64 offers per partner (`build_offers`, `finder_search.py:231-254`).

Today's presses of roster 6 in the preview API log (`<old session scratchpad>/preview-api.log`):

| Press | Spares tree | Targets | Offers | Shortlist | Checks | Claude |
| --- | --- | --- | --- | --- | --- | --- |
| Line 102 to 341 | 11 requests, about 12,632 tokens | 4 requests, about 9,636 tokens | 66 | 4 requests, about 45,689 tokens | 5 requests, 3,266 tokens | 3 calls, cost $0.0961 (`:341`) |
| Line 659 to 898 | 11 requests, about 12,632 tokens | 4 requests, about 12,665 tokens | 78 | 4 requests, about 52,711 tokens | 5 requests, 3,199 tokens | 1 call, cost $0.0731 (`:898`) |

So a press of today sends about 24 Jev requests and about 70,000 to 80,000 input tokens. The other logs of the old session show 62 to 96 offers and shortlist waves of about 43,000 to 64,000 tokens (`.scratch/deadline-week/evidence/AT-49/api-run-1.log`: 96 offers, about 63,894 tokens).

For rosters 7 and 12, no log exists. Code alone gives the Spares tree wave: roster 7 lists 150 players (about 23,701 tokens), roster 12 lists 66 (about 10,190 tokens), and roster 6 lists 77 (about 11,865 tokens). With every partner passed, the targets wave would hold 278 Nouls in 11 requests, about 33,000 to 36,000 tokens, for each asker.

### The token size of one candidate

`estimated_tokens` of `jev_waves.py:33-37` measured three request forms on 41 candidates of roster 6 with roster 7 at the 10% band. Two real calls checked the estimate.

| Form | What each candidate adds | Estimate per candidate | Base per request | Real check |
| --- | --- | --- | --- | --- |
| A, lean | One `fair` Noul. The state is the pair state of today (`finder_search.py:148-149`). | 95 | 1,255 | 41 candidates: estimate 5,156, real 5,755 |
| B, fair with lineup lines | One `fair` Noul, plus the trade and the lineup lines of today's shortlist state (`finder_search.py:393-401`) | 228 | 1,258 | not called |
| C, today's set | The 5 shortlist Nouls and the lineup lines: `shortlist_request` (`finder_search.py:404-407`) | 687 | 1,257 | 41 candidates: estimate 29,434, real 28,734 |

The real counts are within 12% of the estimate. The tables below use about 106 tokens per candidate for A, 228 for B, and 671 for C.

### The calls of the new candidates, per press

Each row adds the candidates to today's press. One request per partner holds its candidates, split where a request passes the 64k context of Jev (section 4). "x limit" is the input tokens divided by the 100,000 tokens per second of the account.

| Asker | Band | Candidates | A: requests | A: tokens | A: x limit | B: requests | B: tokens | C: requests | C: tokens | C: x limit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 5% | 4,166 | 13 | 0.46 M | 4.6 | 22 | 0.98 M | 49 | 2.89 M | 28.9 |
| 6 | 10% | 8,498 | 22 | 0.93 M | 9.3 | 36 | 1.99 M | 96 | 5.89 M | 58.9 |
| 6 | 15% | 12,888 | 26 | 1.40 M | 14.0 | 53 | 3.02 M | 146 | 8.93 M | 89.3 |
| 6 | 20% | 17,585 | 35 | 1.91 M | 19.1 | 72 | 4.12 M | 196 | 12.18 M | 121.8 |
| 6 | 10% dir | 4,667 | 13 | 0.51 M | 5.1 | 23 | 1.10 M | 57 | 3.24 M | 32.4 |
| 6 | abs 3 | 5,462 | 14 | 0.60 M | 6.0 | 25 | 1.28 M | 65 | 3.79 M | 37.9 |
| 7 | 5% | 7,730 | 19 | 0.85 M | 8.5 | 34 | 1.81 M | 89 | 5.36 M | 53.6 |
| 7 | 10% | 15,898 | 33 | 1.73 M | 17.3 | 65 | 3.72 M | 180 | 11.02 M | 110.2 |
| 7 | 15% | 23,972 | 46 | 2.60 M | 26.0 | 93 | 5.60 M | 265 | 16.60 M | 166.0 |
| 7 | 20% | 32,529 | 61 | 3.53 M | 35.3 | 124 | 7.60 M | 361 | 22.53 M | 225.3 |
| 7 | 10% dir | 8,757 | 22 | 0.96 M | 9.6 | 37 | 2.05 M | 100 | 6.07 M | 60.7 |
| 7 | abs 3 | 14,471 | 31 | 1.58 M | 15.8 | 57 | 3.38 M | 163 | 10.03 M | 100.3 |
| 12 | 5% | 9,957 | 22 | 1.09 M | 10.9 | 42 | 2.33 M | 114 | 6.90 M | 69.0 |
| 12 | 10% | 20,488 | 41 | 2.23 M | 22.3 | 80 | 4.79 M | 228 | 14.19 M | 141.9 |
| 12 | 15% | 31,268 | 58 | 3.39 M | 33.9 | 122 | 7.31 M | 344 | 21.65 M | 216.5 |
| 12 | 20% | 42,553 | 79 | 4.62 M | 46.2 | 162 | 9.94 M | 470 | 29.47 M | 294.7 |
| 12 | 10% dir | 11,286 | 24 | 1.23 M | 12.3 | 47 | 2.64 M | 128 | 7.82 M | 78.2 |
| 12 | abs 3 | 13,772 | 30 | 1.50 M | 15.0 | 55 | 3.22 M | 155 | 9.54 M | 95.4 |

Add today's press to each row: about 24 requests and 0.07 to 0.08 M tokens.

The 1-for-1 shape alone at 20% is 112 to 184 candidates: about 12,000 to 20,000 tokens in form A, less than today's shortlist wave.

## 4. The cost and the rate limit

### The sources

- Price: "$42 / $0.042" per Btok and per Mtok for Jev 1.14 (`jev-1.14.0`). "You pay per input token. Output tokens are free." Source: https://docs.typesafe.ai/models.md, read 2026-11-19. The repo uses the same price: `JEV_INPUT = 0.042` (`apps/pipeline/src/cornerstone/advisor_eval.py:49-51`).
- The model: `jev-latest` maps to `jev-1.14.0` (same doc). The client asks for `jev-latest` (`packages/league/python/src/league/jev.py:12`). Both real calls answered with `model jev-1.14.0`.
- Rate limits: "Limits are measured in tokens per second and requests per second." The doc gives no numbers: the values are in the developer console. The repo sets 80 requests per second and 100,000 tokens per second "from its dashboard" (`packages/analyzer/python/src/analyzer/jev_waves.py:18-20`).
- Context: "64k per-request / 32k per-question" for Jev 1.14. The per-request count is the state plus all questions. A header `TypeSafe-Danger-Zone-Long-Context: true` raises both to 262k. "There is no separate limit on the number of questions in a request." Source: https://docs.typesafe.ai/models.md.
- The client keeps the default retry of a 429 and a 529 (`jev.py:47`).

### The cost per press

| Asker | Band | A, lean | B, with lineup lines | C, today's 5 Nouls |
| --- | --- | --- | --- | --- |
| 6 | 5% | $0.019 | $0.041 | $0.121 |
| 6 | 10% | $0.039 | $0.084 | $0.247 |
| 6 | 20% | $0.080 | $0.173 | $0.512 |
| 7 | 5% | $0.036 | $0.076 | $0.225 |
| 7 | 10% | $0.073 | $0.156 | $0.463 |
| 7 | 20% | $0.148 | $0.319 | $0.946 |
| 12 | 5% | $0.046 | $0.098 | $0.290 |
| 12 | 10% | $0.094 | $0.201 | $0.596 |
| 12 | 20% | $0.194 | $0.418 | $1.238 |
| Any | no screen | $0.43 to $1.10 | $0.93 to $2.37 | $2.76 to $7.04 |

For scale: today's Jev part of a press is about 75,000 tokens, about $0.003. The Claude pick of today costs $0.07 to $0.10 per press (`preview-api.log:341`, `:898`). The Claude part does not change with the candidate count while the pick still reads 10 offers.

### The rate limit

- Requests: the worst row above sends 470 requests in one press. Today's pacer puts at most 80 requests in one wave (`jev_waves.py:47`).
- Tokens: every banded row passes the 100,000 tokens of one second. The pacer then splits the requests into waves that each fit the second (`jev_waves.py:40-54`, `:74-83`). The "x limit" column is the least count of such waves for one press.
- The limits belong to the account, not to the press. Two managers who press at once share the same 80 requests and 100,000 tokens.
- One request per partner breaks the 64k context at about 590 candidates in form A, 274 in B, and 92 in C. At the 10% band, each of the 11 partners of roster 12 passes 590 candidates. The table counts the split requests.

## 5. Today's Spares tree candidates against the bands

The offers of today's Finder come from the Spares tree, the targets, and `build_offers`. They depend on Jev answers, so no code count can rebuild them. These rows take the logged offers of roster 6 and score them on the week 11 chart of now. Offers that hold a player with no chart value have no gap.

| Press | Offers | No chart value | 5% | 10% | 15% | 20% | Median gap | Shapes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `preview-api.log` line 153 | 66 | 9 | 2 | 2 | 2 | 5 | 80% | 24 1-for-1, 30 2-for-1, 12 1-for-2 |
| `preview-api.log` line 710 | 78 | 7 | 2 | 2 | 2 | 5 | 73% | 28 1-for-1, 30 2-for-1, 20 1-for-2 |
| `evidence/AT-49/api-run-1.log` | 96 | 18 | 3 | 4 | 5 | 10 | 73% | 31 1-for-1, 42 2-for-1, 23 1-for-2 |

The closest offers of the press at line 153:

| Gap | Roster 6 gives | Roster 6 gets |
| --- | --- | --- |
| 0.0% | Trey McBride 18.5 | Jared Goff 9.0 + Patrick Mahomes 9.5 |
| 2.6% | Trey McBride 18.5 | Dak Prescott 11.0 + C.J. Stroud 8.0 |
| 17.4% | Zay Flowers 23.0 | Dak Prescott 11.0 + C.J. Stroud 8.0 |
| 18.9% | Trey McBride 18.5 | Caleb Williams 13.0 + Bryce Young 2.0 |
| 19.6% | Zay Flowers 23.0 | Jared Goff 9.0 + Patrick Mahomes 9.5 |

The offers of today are need-first. They give QBs, and QBs are low on a 1QB chart: the top 14 QBs run from 41.0 to 2.0. So most of them sit far outside any band. Justin Herbert has no chart value, and 7 to 18 offers per press hold him or another player with no value.

For rosters 7 and 12 no log exists, so this section has no row for them.

## What surprised me

1. **The 3-player shapes explode.** 3-for-2 and 2-for-3 are 73% to 78% of the candidates with no screen, and 82% to 88% at the 10% band. A 10% band still leaves 6,956 to 18,082 of them per asker.
2. **The sum screen keeps filler.** At the 10% band, 40% to 45% of the candidates hold a player with a chart value under 5. A low-value player changes a big sum by little, so he rides along in a "fair" 3-player side.
3. **Jev reads fair differently from the chart.** Two real calls asked `fair` of 41 candidates inside the 10% band. No answer was a "yes" (max 0.47). 22 of 41 (form C) and 12 of 41 (form A) were a clear "no". The state of today holds no chart value: the pair state has the Season rank only (`finder_search.py:127-131`). The FAIR "yes" text still names "trade value" (`packages/analyzer/python/src/analyzer/trade_jev.py:20-23`).
4. **A failed request passes its candidates.** A failed shortlist request lets each offer go on as "unsure" (`finder_search.py:583-586`). A request over the 64k context fails. So an oversized request would pass every candidate in it with no judgment.
5. **The Spares tree and the value pairs barely meet.** 2 to 4 of 66 to 96 offers of today fall in a 5% to 10% band.
6. **The chart misses some starters.** Justin Herbert, Cam Ward, Mark Andrews, and Courtland Sutton have no week 11 chart value. 29 of 148 pool players drop from the value pairs for this cause, 5 of them on roster 6.
7. **No band of 5% or more leaves a team with zero.** Some single cells are empty. Roster 6 has no 3-for-1 with partner 4 at 5% or 10%. Roster 12 has no 1-for-1 with partner 3 at 5%. Roster 6 has one 1-for-1 with partner 7 at 10%.

## What this means for decisions 14 and 15

These are options, with no pick.

### Decision 14, the value screen

1. **A relative band on the sums, the same for each shape.** 5% keeps about 4,200 to 10,000 per asker. 20% keeps about 17,600 to 42,600.
2. **A band per shape.** For example, a wide band for 1-for-1 (112 to 184 at 20%), and a narrow band or a count cap for the 3-player shapes.
3. **Ruling 3 as a code rule.** The team that gets more players gets the larger sum. This cuts each band by about 45%.
4. **A floor per player.** Each player in a candidate has a chart value at or above a floor. This removes the filler of surprise 2. It is a second screen on top of the band.
5. **An absolute band.** It treats low-value and high-value trades differently. Section 2 shows the effect.
6. **A cap on the count per partner or per shape after the band.** For example, the N closest per shape per partner. This fixes the Jev cost whatever the band.
7. **Players with no chart value.** Leave them out, as these counts do, or give them a stand-in value. Herbert is the test case.

### Decision 15, the Jev questions

1. **One `fair` Noul per candidate in a lean state (form A).** It is the cheapest form: about $0.02 to $0.05 per press at 5%.
2. **Today's five Nouls per candidate (form C).** It costs about 6 times form A, and about 29 to 69 times the per-second token limit at 5%.
3. **Two steps.** Ask `fair` of every banded candidate first. Then ask `need` and `gain` only of the candidates that pass. The second step is the size of today's shortlist.
4. **The chart values in the state as facts.** Surprise 3 shows that Jev gives no "yes" to chart-fair trades when the state has no chart value. The Spares tree already puts chart values in its state (`spares_tree.py:123-137`).
5. **The split of requests.** Keep one request per partner and split at the 64k context. Or send the long-context header. Either way, a failed request must not pass its candidates as "unsure" without a decision on that.
6. **The gain check of ticket 09.** It is two of the five Nouls of form C. Keeping it as a clear-no drop on all candidates costs most of the gap between form A and form C.

## Spend

- Jev: 2 requests, 34,489 input tokens, $0.0014. Both were the calibration calls of section 3. No other Jev call ran.
- Claude: none. The chart reader raised if called, and it was not called.
