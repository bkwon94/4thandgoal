# 09 notes: Jev rank of the facts of a Finder trade

Research for `09-research-finder-fact-rank.md`. Written 2026-11-09. This file measures and shows. Brian decides.

The scratchpad is `S` = `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/dca6fb71-05df-45b3-a975-9d25fe459bf6/scratchpad/jev-09/`.
The side-by-side cards are at `S/cards.html`. That file holds real names, because the scratchpad is not tracked.

## Answers in short

1. **Do the top 2 facts read well beside the Claude sentence?** Partly. About half of the cards read well. The other half show a bookkeeping fact, such as "Team B has 5 RB after the trade and 0 open roster spots". A code filter on the fact kind fixes most of that. Jev cannot surface the best line of most Claude sentences, "gets more work while Smith is out", because that line is in the grade lines, not in the fact sheet.
2. **Latency of one request for 10 trades:** 0.31 s to 0.51 s, median 0.39 s, for 289 to 333 Score questions. Ten requests of one trade each, sent at once, take 0.15 s to 0.23 s of wall time. One `write_reasons` call takes 21 s to 27 s.
3. **Does the order change the answer?** Not the order of the questions. The order of the trades in the state does. With all trades in one state, a reversed trade order changes the top 2 of 48% of sides. The same request sent twice changes 15% to 24% of sides. One request per trade removes the order effect, but the 15% to 24% noise stays.

## Method

1. **The Finder.** `S/find.py` runs the repo's own code with `uv run --exact --package cornerstone`. It loads the saved week 8 of 2026 for `cpc` with `_saved_snapshot` (`apps/pipeline/src/cornerstone/cli.py:252`). It calls `find_win_wins` (`packages/analyzer/python/src/analyzer/finder.py:128`) for the asker against each of the 11 other rosters, then ranks the pool with `rank` (`finder.py:104`).
2. **The list.** The script keeps up to 10 trades, with one player in 3 trades at most. This copies decision 02 of your-league as the handoff states it. The jev branch has no league-wide list, so this step is my approximation, not repo code.
3. **The askers.** Three askers: the 1st, the 7th, and the 12th of the standings. The askers are asker 1, asker 2, and asker 3 below. They got 8, 9, and 10 trades: 27 trades and 54 sides in total (`S/trades.json`).
4. **The Claude sentence.** One `write_reasons` call per asker (`packages/analyzer/python/src/analyzer/finder_reasons.py:97`). That made 3 Claude calls. Each passed its check on the first attempt, with no fallback (`S/trades.json`, keys `claude_seconds` and `fallback`).
5. **The facts.** The fact sheet of each trade is `trade_facts` of `finder_reasons.py`, which wraps `trade_fact_sheet` (`packages/analyzer/python/src/analyzer/trade_facts.py:251`). For each side, the script drops three kinds of fact:
   - each `.value` fact, because the prose never shows a trade value (`packages/analyzer/python/src/analyzer/analysis.py:232`);
   - the `trade.week` fact, because it is the same for every trade;
   - each fact about the other roster alone, such as its record and its need.

   The rest is 17.4 facts per side on average (`S/order-test.json`).
6. **The state.** Each trade sits in the state as `trades.trade_<n>`, with `team_a` and `team_b`. Each team has `gives`, `gets`, and `what_it_gains`, the code's fairness reason of the side. Team names are swapped for "Team A" and "Team B" before the send. A scan of every payload found no team name (`S/rank.py`, the `label` function).
7. **The question.** One Score per fact per side, all trades of one asker in one request, model `jev-1.14.0`. The text sits in one module, `S/questions.py`:
   - Instructions: "How much does this fact matter to {team}'s decision to accept `trades.{trade}`? Fact: {fact}"
   - Level 0: "A routine detail that would not change this team's mind."
   - Level 1: "A minor point this team would notice but not weigh much."
   - Level 2: "A real reason for or against the trade, but not the main one."
   - Level 3: "A main reason this team would accept or turn down the trade."

   The card takes the 2 facts with the highest Score position. A tie keeps the order of the fact sheet.
8. **The fit.** The first wording had longer levels with examples (`S/v1/questions.py`). With it, the request of 10 trades failed with `400 {"detail":{"error_type":"max_tokens_exceeded"}}`. The levels go with each question, and the limit is 64k per request (https://docs.typesafe.ai/models.md). The short levels bring the largest request to 49,099 input tokens.
9. **The order test.** Each asker ran 8 times as one request: the given order, the same request twice more, the questions reversed, the trades of the state reversed, both reversed, and two shuffles of both. Each asker also ran 3 times as 10 parallel requests of one trade each (`S/pertrade.py`). One more variant added the grade lines of each side to the state (`S/rank-*-breakdown.json`).
10. **A code filter.** `S/no-need.txt` drops the need facts and the Week line facts in code, then takes the top 2 from the same answers. It sends no new request.

## Limits of the method

- The rosters are the saved week 8 data, not a live fetch. The ticket names week 8, and a live fetch can start a chart read with Claude.
- The worktree has no NFL cache, because the cache is not tracked. The script reads the cache of the main checkout, `data/nfl/`, and changes no file there.
- The saved chart PNG of week 8 is a fraction of a second newer than its JSON read. So `saved_chart_read` returns None (`packages/league/python/src/league/chart.py:242`), and the CLI would read the image again with Claude. The script matches the saved JSON read itself and passes it as `--chart` (`S/chart-week-08.json`).

## Cost

- Jev: 118 requests, $0.092 in total (sum of `cost_usd` in `S/rank-*.json`). One request of 10 trades costs about $0.002. The price is $0.042 per million input tokens (https://docs.typesafe.ai/models.md).
- Claude: 3 calls, one per asker. They took 21.3 s, 21.3 s, and 26.6 s (`S/trades.json`).

## Latency

| Form | Questions | Input tokens | Time |
|---|---|---|---|
| One request, 8 to 10 trades | 289 to 333 | 42,361 to 49,099 | 0.31 s to 0.51 s, median 0.39 s |
| One request, plus the grade lines in the state | 289 to 333 | 48,401 to 56,345 | 0.37 s to 0.51 s |
| One request per trade, 8 to 10 sent at once | 289 to 333 in total | 44,216 to 51,484 in total | 0.15 s to 0.23 s wall |
| `write_reasons`, one Claude call | 8 to 10 sentences | n/a | 21.3 s to 26.6 s |

The times are client wall time around `system_one` (`S/rank-*.json`, key `seconds`). The Finder search itself took 9 s to 14 s on this laptop (`S/trades.json`, key `find_seconds`).

## Order test

Each count is the number of sides, out of 54, whose top 2 set differs from the given run (`S/order-test.json`, `S/compare.json`, and the inline counts of the session).

| Run against the given run | Sides changed | Share |
|---|---|---|
| The same request again, first time | 8 | 15% |
| The same request again, second time | 13 | 24% |
| The questions reversed, the state as given | 10 | 19% |
| The trades of the state reversed, the questions as given | 31 | 57% |
| Both reversed | 26 | 48% |
| Both shuffled, seed 1 | 21 | 39% |
| Both shuffled, seed 2 | 21 | 39% |
| One request per trade, against its own repeat | 13 | 24% |
| One request per trade, its questions reversed, against its given run | 14 | 26% |
| The grade lines in the state, the same request again | 6 | 11% |
| The grade lines in the state, both reversed | 16 | 30% |

What the counts show:

1. The order of the questions has no effect beyond the noise. A reversed question order changes 19%, inside the 15% to 24% of a plain repeat.
2. The place of a trade in a long state has an effect. A reversed trade order changes 57%. The jaggedness page names the first-option bias for a Choice only. It also names accuracy loss in a large state (https://docs.typesafe.ai/model-jaggedness.md). This test fits the second item better than the first.
3. One request per trade removes the trade-order effect. Its repeat changes 24%, the same as the noise of one request.
4. The noise is near ties. The median gap between the 2nd and the 3rd fact of a side is 0.12 on the 0 to 3 scale. 37% of sides have a gap under 0.1.
5. The mean of two orders does not help. Mean of the given and the reversed runs, against the mean of the repeat and a shuffle, changes 7 of 54 sides (13%).
6. Of the 108 facts the cards show, 60 stay in the top 2 in all 8 one-request runs. 81 stay in 6 or more (`S/cards.md`, the `n/8` marks).

## Which facts win

Fact kinds in the top 2 of the given run, out of 108 slots (`S/order-test.json`, `S/no-need.txt`):

| Kind | As sent | With need and Week line dropped in code |
|---|---|---|
| need ("has 5 RB after the trade and 0 open roster spots") | 34 | dropped |
| ppg (points per game and rank) | 33 | 48 |
| usage (snap share) | 10 | 17 |
| week_line (two weeks of lines, 50 to 80 words) | 9 | dropped |
| depth ("the WRs in the top 36 go from 2 to 3") | 8 | 14 |
| team (record and race) | 7 | 9 |
| injury | 3 | 8 |
| hole | 3 | 3 |
| strength | 1 | 4 |
| targets | 0 | 5 |

With the filter, the repeat noise stays at 9 to 12 of 54. The trade-order effect stays at 25 of 54.
The grade lines in the state did not lower the need facts. They rose from 34 to 41 slots (`S/compare.json`).

## A sample of the cards

The askers are asker 1, 2, and 3. Within a trade, Team A is the asker and Team B is the partner. Each Jev fact shows its Score position and its `n/8` count. The full set of 27 cards is in `S/cards.md`, and with real names in `S/cards.html`.

| Asker, trade | Side | Gives, gets | Jev top 2 facts | Claude sentence |
|---|---|---|---|---|
| 2, trade 7 | A | gives Bijan Robinson; gets Jonathan Taylor, George Pickens | 2.14 (8/8): Jonathan Taylor (RB, IND) scored 18.4 points per game over 7 games before the trade. His Season rank is RB4, by total points this season.<br>2.11 (5/8): Team A has 5 RB and 6 WR after the trade and 0 open roster spots. | Team A adds Jonathan Taylor and George Pickens and its lineup scores more, while Team B gets the better player in Bijan Robinson, who gets more work while Brian Robinson Jr. is out, though WR2 becomes a hole with A.J. Brown out and no return week on file. |
| 2, trade 7 | B | gives Jonathan Taylor, George Pickens; gets Bijan Robinson | 2.67 (8/8): For Team B, the trade leaves WR2 short: A.J. Brown is out with no return week on file. George Pickens held WR2 before the trade. The best free agent at WR is Devaughn Vele, WR31.<br>2.07 (2/8): Bijan Robinson's snap share was 79 percent over the last 2 weeks before the trade, up from the 2 weeks before that. | |
| 3, trade 2 | A | gives CeeDee Lamb; gets Ja'Marr Chase | 2.81 (8/8): Team A was 3-11, 12th of 12, before the trade: a seller out of the playoff race.<br>1.94 (8/8): Team A has 5 WR after the trade and 0 open roster spots. | Team A, out of the playoff race, gets Ja'Marr Chase as the better player for the rest of the season, while Team B, in a playoff spot, gets CeeDee Lamb at 18.4 points per game so its lineup scores more now. |
| 3, trade 2 | B | gives Ja'Marr Chase; gets CeeDee Lamb | 2.26 (8/8): Team B has 5 WR after the trade and 0 open roster spots.<br>2.09 (8/8): CeeDee Lamb (WR, DAL) scored 18.4 points per game over 7 games before the trade. His Season rank is WR2, by total points this season. | |
| 1, trade 4 | A | gives Travis Kelce; gets Wan'Dale Robinson, Brenton Strange | 2.05: Travis Kelce (TE, KC) scored 9.7 points per game over 6 games before the trade. His Season rank is TE6, by total points this season. His Recent rank is TE29, by points per game over the last 4 weeks.<br>1.79: Wan'Dale Robinson has no injury status now. | Team A adds Wan'Dale Robinson, whose target share rose to 25 percent and who gets more work while Tate is out, plus Brenton Strange, while Team B gets the better player in Travis Kelce. |
| 1, trade 6 | A | gives Jaxon Smith-Njigba; gets Bijan Robinson | 2.5 (8/8): For Team A, the trade leaves WR2 short: Jakobi Meyers is WR39. Jaxon Smith-Njigba held WR1 before the trade. The best free agent at WR is Devaughn Vele, WR31.<br>2.15 (4/8): Jaxon Smith-Njigba (WR, SEA) scored 23.9 points per game over 7 games before the trade. His Season rank is WR1, by total points this season. | Team A gets Bijan Robinson, a top 8 player this week who gets more work while Brian Robinson Jr. is out, and Team B gets Jaxon Smith-Njigba, the WR1 by total points this season. |

## My read

Where the Jev cards are stronger:

1. **Speed and cost.** One request takes under half a second and costs about $0.002. The Claude call takes 21 s to 27 s. The Jev card adds almost nothing to the 4 s to 6 s search of the handoff.
2. **No failure of the whole list.** Each fact is its own question, so no sentence check and no retry of all 10 apply. The code still treats a failed call as an error, never as a low score.
3. **No new numbers.** The card shows the code's own fact text, so the number check of `trade_prose_failures` has nothing to catch.
4. **The holes.** Three trades open a hole. In each, Jev puts the hole fact first, in 7 or 8 of 8 runs. Claude names the hole in 1 of the 3 sentences (`S/trades.json`, `S/cards.md`).
5. **Both sides.** The card gives two facts to each side. The Claude sentence gives most of its words to the asker, and often gives the partner only "gets the better player".

Where the Jev cards are weaker:

1. **The best reason is not a fact.** 17 of the 27 Claude sentences use the Upside adjuster, such as "gets more work while Smith is out". That line comes from the grade lines that the Claude prompt shows (`analysis.py:152` to `analysis.py:155`, `finder_reasons.py:72`), not from the fact sheet. Jev can only rank the facts it gets.
2. **Bookkeeping facts win.** The need fact took 34 of 108 slots. It tells a manager little. A filter in code on the fact kind removes it. That is a decision for code, not a question for Jev.
3. **No direction.** The level "a real reason for or against" does not say which. The card for the side that gets Kelce shows "His Recent rank is TE29", a reason against, with no mark. A second question per fact, "Does this fact favor the trade for this team?", can give the direction, as the skill advises: ask direction and magnitude separately.
4. **Some odd picks.** "Wan'Dale Robinson has no injury status now" scored 1.79 and took second place. Level 0 names this case. Only some runs pick it.
5. **Noise near ties.** 15% to 24% of sides change their top 2 between two identical requests. A card can show a different second fact on reload, unless the result cache holds the answer.
6. **Length.** A Week line fact runs 50 to 80 words. That is too long for a card line.
7. **It is two facts, not a sentence.** The Claude sentence ties the two sides together in one line that a manager can paste into the group chat (`finder_reasons.py:21`). Two facts per side do not do that.

## What this means for your-league ticket 04

These are facts for the choice. They do not make it.

1. **A fourth option is real.** Jev can rank the facts of 10 trades in one request, under 0.5 s, for about $0.002, with no Claude call. It fits only with short levels, at 49k of the 64k tokens of one request.
2. **It sits next to option 3.** Option 3 shows the code's reason of each side. A Jev card adds two facts per side under that reason. The "Analyze" button of option 3 still gives the full Claude read.
3. **It needs code around it.** A build needs these parts:
   - a filter on the fact kind, at least the need fact and the Week line fact;
   - one request per trade, or a fixed trade order with the effect accepted;
   - a direction question for each fact, if a card must say for or against;
   - the result cache of decision 03, so a card holds still between loads.
4. **It does not replace the Claude sentence.** It cannot say "gets more work while Smith is out", unless the code turns the Upside line into a fact.
5. **The test is small.** It used one week, one league, 27 trades, and my own rank of "reads well". No manager saw the cards.
