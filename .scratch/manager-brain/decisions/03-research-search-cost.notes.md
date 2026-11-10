# 03: Notes on the cost of the search across all partners

Ticket: `.scratch/manager-brain/decisions/03-research-search-cost.md`. Data: the saved week 8 of season 2026 for cpc and norcal. No TypeSafe call ran. No league data left this machine.

## Summary

1. The plan as written fails both targets when many partners pass. A full search of all 11 partners costs about $0.45 to $0.57 in Jev and needs about 10,000 fact sheets, or about 100 s of code.
2. Jev is cheap per token ($0.042 per Mtok), so the count of candidates sets the cost and the time, not the price.
3. The four-question filter alone is not a dependable cut. A strict code proxy keeps 0 to 2 partners. A loose proxy keeps 0 to 10, median 6.
4. Two small code cuts meet both targets with room to spare. First, a code screen drops each candidate where a side's best lineup loses `FIT_THRESHOLD` (3.0 points per game) or more. Second, a cap keeps the top 50 per partner.
5. Ask Jev per partner with one shared state and one question per candidate. Then a Finder call over all 11 partners costs about $0.012 in Jev and about 15 s end to end, before the final Claude call.

**Recommendation:** keep the filter, and add the screen and the cap of 50 per partner in code. Use one Jev request per partner with a shared state. Brian must read the rate limits of the org at https://console.typesafe.ai/rate-limits before the spec fixes the concurrency. The docs give no number for them.

## How the numbers were made

- The scripts load each snapshot with the real loader of `cornerstone find --week`: `_saved_snapshot` (`apps/pipeline/src/cornerstone/cli.py:253-270`), with `load_client` (`packages/league/python/src/league/client.py:283-297`).
- The worktree has no `data/nfl` cache, because git ignores it. The scripts read the cache of the main checkout, read only.
- The saved chart read was not used as is. The cpc week 8 PNG is 0.6 ms newer than its JSON, so the cache rule drops the read (`packages/league/python/src/league/chart.py:242-247`). With no chart, every listed player is unlisted, so every pool is empty and the Finder finds nothing. The scripts pass the saved read as a `--chart` file.
- norcal has no week 8 chart read. Only `data/nfl/cache/charts/1QB1.0PPR4pt/week-09.json` exists. The norcal numbers use that read with the week 8 rosters.
- The scripts are in `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/cf36e780-3cbf-42a7-b396-30182ea76dfb/scratchpad` (`measure.py` to `measure5.py`, the `report*.json` files, and the sample states).
- Tokens are characters / 4 on compact JSON.

## 1. The tradable pool per roster

The pool rules are no unlisted player, no player out with no return, and no handcuff on the roster (`packages/analyzer/python/src/analyzer/finder.py:49-59`).

| League | Teams | Roster size | Pool per roster, min / median / max |
| - | - | - | - |
| cpc | 12 | 14 to 15 | 6 / 10 / 12 |
| norcal | 12 | 15 to 18 | 7 / 9 / 12 |

Per roster id, cpc: 6, 11, 10, 9, 12, 8, 9, 10, 10, 7, 10, 11. norcal: 12, 9, 11, 8, 10, 9, 7, 10, 9, 9, 9, 9. Source: `report.json`, key `pools`.

## 2. The candidates per partner and per asker

The shapes are 1-for-1, 2-for-1, and 1-for-2, with handcuff trades left out (`finder.py:62-87`). Each count is for one asker and one partner, both directions.

| League | Per pair, min / median / max | Per asker over 11 partners, min / median / max |
| - | - | - |
| cpc | 273 / 855 / 1,518 | 5,109 / 10,135 / 12,990 |
| norcal | 420 / 764 / 1,518 | 6,125 / 8,595 / 12,720 |

The split per asker over all partners, min / median / max:

| League | 1-for-1 | 2-for-1 and 1-for-2 |
| - | - | - |
| cpc | 642 / 1,030 / 1,212 | 4,467 / 9,105 / 11,778 |
| norcal | 735 / 927 / 1,200 | 5,390 / 7,668 / 11,520 |

The 2-for-1 shapes are about 90 percent of the candidates. Source: `report.json` and `report2.json`.

### How many partners the filter keeps

Jev gives the real answer, so this is a code proxy only. Two readings bound it.

| Proxy | Need | Spare | Partners kept per asker, min / median / max |
| - | - | - | - |
| Strict | a position with a hole slot | a pool player above the line who does not start | cpc 0 / 0 / 0, norcal 0 / 0 / 2 |
| Loose | a hole slot, or depth at or below the starter count | a pool player whose loss makes no new hole | cpc 0 / 6.5 / 10, norcal 0 / 6 / 10 |

With the loose proxy, the kept partners hold a median of 4,623 (cpc) and 5,246 (norcal) candidates per asker. So the filter alone can leave about half of the full search. Source: `report2.json`, `report3.json`. Depth is the count at or above the line (`packages/analyzer/python/src/analyzer/adjusters.py:156-166`). Code must count it, because "Jev does not count reliably" (https://docs.typesafe.ai/model-jaggedness.md, line 37).

### The code screen

The screen keeps a candidate only when no side's best lineup loses 3.0 points per game or more. The value is `FIT_THRESHOLD` (`packages/analyzer/python/src/analyzer/tunables.py:45`). It reads `Side.lineup_change` from `build_sides` (`packages/analyzer/python/src/analyzer/rubric.py:339-349`).

| League | Kept per pair, min / median / max | Kept per asker, min / median / max | Code time per asker, all partners |
| - | - | - | - |
| cpc | 52 / 224 / 559 | 1,074 / 2,607 / 3,865 | 2.5 / 4.1 / 7.4 s |
| norcal | 52 / 198 / 502 | 1,048 / 2,295 / 3,828 | 2.9 / 3.9 / 5.4 s |

The screen drops about 75 percent of the candidates. Only a median of 1 to 1.5 candidates per pair raise both lineups. Source: `report4.json`.

## 3. The tokens of the state per Jev request

### (a) One partner-filter request

The state holds both rosters: each player at QB, RB, WR, or TE with position, rank, Season rank, line flag, starter flag, and status. It also holds the depth per position, the lines, and the hole slots of each roster.

- cpc: 4,440 characters, about 1,110 tokens. norcal: 5,171 characters, about 1,290 tokens.
- The four questions add about 40 tokens each. One request per partner is about 1,300 to 1,450 tokens.
- One request with all 12 rosters and 44 questions is about 8,500 tokens. Per-partner states are better, because "accuracy falls as the state grows with content unrelated to the decision" (https://docs.typesafe.ai/model-jaggedness.md, line 92).

A sample, with the team names removed (full file: `cpc-filter-state.json` in the scratchpad):

```json
{"asker": {"team": "<team A>", "depth_at_or_above_line": {"QB": 2, "RB": 2, "WR": 3, "TE": 2},
  "lines": {"QB": 24, "RB": 36, "WR": 36, "TE": 24}, "holes": ["RB2", "WR2", "FLEX1"],
  "players": [
   {"name": "Bucky Irving", "pos": "RB", "nfl": "TB", "rank": 15, "season_rank": "RB13", "above_line": true, "starter": true, "status": null},
   {"name": "RJ Harvey", "pos": "RB", "nfl": "DEN", "rank": 47, "season_rank": "RB28", "above_line": false, "starter": false, "status": "IR"}]},
 "partner": {"...": "the same shape"},
 "questions": ["Does the partner have a player at a position the asker needs?", "Can the partner spare him?",
               "Does the asker have a player at a position the partner needs?", "Can the asker spare him?"]}
```

### (b) One candidate trade

The state is the trade and its fact sheet from `trade_fact_sheet` (`packages/analyzer/python/src/analyzer/trade_facts.py:251-285`). It has the player facts, the team, the need, the Week line, the holes, the depth, and the strength of each side.

- cpc: 2,380 / 4,075 / 4,946 characters, min / median / max over 40 candidates. That is about 1,020 tokens at the median.
- norcal: 2,750 / 3,880 / 4,592 characters, about 970 tokens at the median.

A sample, cut short (full file: `cpc-trade-state.json` in the scratchpad):

```json
{"trade": {"1": ["Rashee Rice", "Bucky Irving"], "2": ["Tre Tucker"]},
 "facts": {"trade.week": "The trade is in week 8 of the 2026 season. Every stat runs through week 7.",
  "11584.ppg": "Bucky Irving (RB, TB) scored 14.2 points per game over 7 games before the trade. His Season rank is RB13, by total points this season.",
  "11584.value": "Bucky Irving's trade value is 30.5 in the week of the trade.",
  "1.team": "<team A> was 7-7, 6th of 12, before the trade: a contender in a playoff spot.",
  "...": "about 25 facts in all"}}
```

### (c) A shared state per partner

Most facts of a candidate repeat across the candidates of one pair: the player facts, the team facts, and the week. Put them in the state once, and put only the facts of one trade in its question. These are the need, the depth, the holes, the strength, and the Week line.

- The shared state per pair is 10,892 to 16,888 characters, about 2,700 to 4,200 tokens.
- The facts of one trade are 1,320 to 1,651 characters at the median, about 330 to 410 tokens. With the question text, use about 400 tokens per candidate.
- A request must fit 64k tokens, and the state plus one question must fit 32k (https://docs.typesafe.ai/models.md, line 15). So about 140 candidates fit in one request.

Source: `report2.json`, keys `shared_state_chars_3pairs` and `question_trade_facts_chars_median_3pairs`.

## 4. The cost and the time of one Finder call

### The facts from the docs

- The price of Jev 1.14 is $0.042 per Mtok of input. Output tokens are free (https://docs.typesafe.ai/models.md, lines 14 and 21).
- The context limit is 64k tokens per request and 32k per question (https://docs.typesafe.ai/models.md, line 15). Long context goes to 262k, but it is slower and less accurate (https://docs.typesafe.ai/models.md, lines 39 and 58).
- Bundled questions pay for the state once. "Jev ingests the `state` once and evaluates every question against it in parallel" (https://docs.typesafe.ai/models.md, line 28). "Reads the state once, so you pay for the state once" (https://docs.typesafe.ai/patterns/noul-screen.md, line 15). Extra questions cost only their own tokens (https://docs.typesafe.ai/primitives.md, line 135).
- No limit applies to the count of questions, only to the size of the request (https://docs.typesafe.ai/models.md, line 33).
- The rate limits are set per organization, in tokens per second and in requests per second. The docs give no number. Each org reads its own at https://console.typesafe.ai/rate-limits (https://docs.typesafe.ai/models.md, lines 62 and 64). The SDK retries a `429` with backoff (same page, line 64).
- Latency: one request with about 11,800 input tokens and 13 questions took 0.24 s. Thirteen calls of one question each took 2.81 s in sequence, about 0.22 s each (https://docs.typesafe.ai/cookbooks/parallel_questions.md, lines 323 to 326). Ten parallel requests and one more finish "in about a second" (https://docs.typesafe.ai/demos/airbnb-listing-search.md, line 34).
- The default SDK client opens at most 100 connections (https://docs.typesafe.ai/sdk/python/usage/advanced.md, line 102).

### The code time, measured on this machine

- The saved snapshot loads in about 3.0 s for cpc and 3.1 s for norcal (`report.json`, `load_s`). A live snapshot also calls Sleeper, so it can take longer.
- The candidates of all 132 pairs take 2.6 s per league (`candidates_code_s_all_pairs`).
- Today's code Finder over all 11 partners for one asker takes 5.3 s for cpc asker 1 (5,109 candidates) and 14.1 s for norcal asker 1 (12,720 candidates). That is about 1 ms per candidate.
- One `trade_fact_sheet` takes 6 to 15 ms (`measure5.py`, 300 candidates per league). This is the largest code cost. The 10,135 sheets of a median full search take about 100 s.

### The cost of Jev

The filter is 11 requests of about 1,400 tokens, so about 15,400 tokens. That costs $0.0006 and takes about 0.3 s with the requests in parallel. The table adds the filter to the full search. It uses 850 candidates per pair (the median) and 10,135 to 12,990 per asker when all partners pass.

| Plan | 1 partner passes | 3 partners pass | All 11 pass (median to max asker) |
| - | - | - | - |
| A. One request per candidate, 1,050 tokens each | $0.038 | $0.113 | $0.45 to $0.57 |
| B. A shared state per partner, 400 tokens per candidate | $0.016 | $0.046 | $0.18 to $0.23 |
| A with the screen | $0.010 | $0.028 | $0.12 to $0.17 |
| B with the screen | $0.004 | $0.011 | $0.05 to $0.07 |
| B with the screen and a cap of 50 per partner | $0.001 | $0.003 | $0.012 |

The math: tokens × $0.042 / 1,000,000. Plan B adds one state of about 3,500 tokens for each request of about 140 candidates.

### The time

| Plan, all 11 partners pass | Code | Jev | Total before Claude |
| - | - | - | - |
| A, no cut | 3 s load + 100 s of fact sheets | 10,135 requests: 26 s at 100 connections and 0.25 s each, if the rate limit allows about 400 requests per second | over 120 s |
| B with the screen | 3 s load + 4 to 7 s screen + 26 to 39 s of fact sheets | about 25 requests in one parallel round, about 1 s | 34 to 50 s |
| B with the screen and a cap of 50 | 3 s load + 4 to 7 s screen + 3 to 8 s of fact sheets | 11 requests of about 24,000 tokens in one round, about 1 s | about 11 to 19 s |

With 1 or 3 partners passing, the screen runs on fewer pairs and the times drop. The final Claude call that writes the shortlist is not in these numbers. This ticket did not measure it.

## 5. The targets and the cut

The targets are about 30 s and about 10 cents for each Finder call.

| Plan | Under 10 cents? | Under 30 s? |
| - | - | - |
| The map's plan, plan A, no cut | No when 3 or more partners pass | No when many partners pass |
| Plan B, no cut | No when about 7 or more partners pass | No: the fact sheets alone take over 30 s |
| Plan B with the screen | Yes, $0.05 to $0.07 at worst | No at worst: 34 to 50 s |
| **Plan B with the screen and a cap of 50 per partner** | **Yes, about $0.012 at worst** | **Yes, about 11 to 19 s plus Claude** |

### The proposed cut

1. Keep the four-question filter. It costs less than one tenth of a cent, and it stops the search when nothing fits.
2. Add a code screen in `finder.candidates` or just after it. Drop each candidate where a side's best lineup loses `FIT_THRESHOLD` or more. It reuses `build_sides` and drops about 75 percent of the candidates.
3. Cap the screened candidates at 50 per partner. Rank them in code by the smaller of the two lineup changes, with the player ids as the last tie-break. The cap goes in `tunables.py`.
4. Build the fact sheets only for the capped candidates. Put the player and team facts in one shared state per partner. Put the facts of one trade in its question.
5. Send one Jev request per passing partner, all in parallel.

The screen and the cap keep all three shapes of trade, so they do not break the out-of-scope rule on candidate shapes in `MAP.md`.

A smaller cut, "2-for-1 only at a need position", gives too little alone. On the strict proxy it keeps 1,323 of 1,710 candidates, a cut of 23 percent (`report2.json`). Dropping the 2-for-1 shapes cuts 90 percent but breaks the shape rule in `MAP.md`.

### Open points for the spec

- Brian reads the tokens per second and the requests per second of the org at https://console.typesafe.ai/rate-limits. Plan B with the cap sends about 11 requests and 260,000 tokens at once. Check that one burst fits.
- The fact sheet takes 6 to 15 ms. A profile of it, or a cache of the player facts per snapshot, can cut the code time further.
- Fix the chart cache rule for the case where the PNG and the JSON have almost the same time. Today a saved week can lose its chart read, and then the Finder finds nothing. This is out of scope here, so it needs its own issue.
- norcal needs a week 8 chart read to repeat these numbers exactly.
