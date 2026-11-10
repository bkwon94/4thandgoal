# Manager brain: evidence

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests: `.scratch/manager-brain/ACCEPTANCE.md`, with the revisions of 2026-11-10 to AT-26, AT-33, AT-34, AT-47, and AT-50.
Built from: `6ba706cf`, on 2026-11-10. Each Observation names the commit it was taken at. A test taken at an earlier commit (`26dbed1b` or `b056a29f`) stayed as it was, because no later change touched its code or files. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: about 16 min for 9 site tests with a `steps.json`, in three runner rounds. The runner printed per-test times for the first round and totals of 186.6 s (AT-45) and 220.1 s (AT-47 and AT-48) for the others. AT-44, AT-49, and AT-51 used `agent-browser`.
The full `make check` ran green on 2026-11-09 from 22:56:54 to 23:05:02 at `26dbed1b`. Each later merge ran `make check-fast` and the full pipeline and API suites.

## AT-1: The chart cache trusts the hash of the PNG

App: pipeline
Then: the first run reads nothing again. The second run reads the chart again.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/onebyte.py`
Observation: Before run 1 the saved read held png_sha256 b28ead45... of a read of the same PNG, and the PNG was 10 s newer than the JSON after the touch. Run 1 made no POST to api.anthropic.com and left the JSON time and hash as they were. Run 2, after one byte at offset 42 changed (cmp shows 1 byte), made one POST to api.anthropic.com with a ChartRead call, and the saved hash changed to 6115bf40..., the hash of the changed PNG.

## AT-2: The build log says when a week has no chart

App: pipeline
Then: the build log has one plain line that says the week has no chart.
Files: `evidence/AT-2/output.txt`
Observation: The cache held chart PNGs of weeks 6 to 9 only. The build of week 5 ended with exit 0, and the log has one line with the word chart: "Week 5 has no chart, so the roster grade has no trade value."

## AT-3: The manual chart step reads a placed chart

App: pipeline
Then: the command reads the PNG and prints the count of chart rows it read.
Files: `evidence/AT-3/output.txt`
Observation: With the week 8 PNG in the cache and no saved read, the command made one ChartRead call to Claude and printed "Read 131 chart rows", each guard as pass, and "Matched 128 of 131 chart rows".

## AT-4: The sheet states the RB depth after the trade for each side

App: pipeline
Then: each side has a fact in the shape "RBs in the top 36 go from N to M", and N and M match the rosters before and after the trade. The sheet also states the depth of the other team at the positions of the trade.
Files: `evidence/AT-4/output.txt`, `evidence/AT-4/rosters.txt`, `evidence/AT-4/rosters.py`
Observation: At 6ba706cf, the eval sheet of trade 6 has "the RBs in the top 36 go from 1 to 1" for behold the lamb and "from 2 to 2" for Pukancun on 3, plus WR depth facts for both sides (2 to 3, and 4 to 3). rosters.txt, from the same week 7 snapshot at 6ba706cf, counts 1 then 1 and 2 then 2 RBs at or above RB36, and 2 then 3 and 4 then 3 WRs at or above WR36.

## AT-5: The sheet gives the past-season splits with their game counts

App: pipeline
Then: for each of 2023, 2024, and 2025, the sheet gives his half-PPR points per game in weeks 1 to 8 and in weeks 9 to 17, and in cold games, each with its game count.
Files: `evidence/AT-5/output.txt`
Observation: At 6ba706cf, the eval sheet of trade 12 has 3198.history for Derrick Henry. It gives 2023, 2024, and 2025, each with points per game in weeks 1 to 8, in weeks 9 to 17, and in cold games, and a game count for each.

## AT-6: A player with no past season gets no number

App: pipeline
Then: the sheet has no split fact for him, and no Bullet and no sentence of the Case gives him a number from a past season.
Files: `evidence/AT-6/output.txt`
Observation: At 6ba706cf, the eval sheet of trade 6 has .history facts for Barkley, Lamb, and Nacua, and none for Omar Cooper Jr. No Bullet and no sentence of the Case names a past season, so none gives Cooper a past-season number.

## AT-7: A past-season file downloads once

App: pipeline
Then: the log shows no download of a past-season file.
Files: `evidence/AT-7/output.txt`, `evidence/AT-7/cache-times.txt`, `evidence/AT-7/api_run.py`
Observation: The start of the local API at 26dbed1b downloaded each 2023 to 2025 file one time, on 2026-11-09 at 23:14:21 to 23:14:22. The eval at 6ba706cf, about 10:31 to 10:35 on 2026-11-10, logs no download, its 28 sheets each hold a .history fact, and the file times stay at 23:14:22. The reused press log at 26dbed1b also shows no download.

## AT-8: The sheet holds the quality of the NFL team

App: pipeline
Then: the sheet has a fact on the quality of his NFL team.
Files: `evidence/AT-8/output.txt`
Observation: At 6ba706cf, the eval sheet of trade 24 has 12507.nfl_team: "Omarion Hampton's NFL team, the Chargers, ranks 32nd of 32 on offense: -20.16 expected points added per 100 plays over 6 games before the trade."

## AT-9: The sheet holds the race group, the odds, and the bye of each side

App: pipeline
Then: each side has its race group (In, Bubble, or Out) and its playoff odds. The side with the bye has a bye fact.
Files: `evidence/AT-9/output.txt`, `evidence/AT-9/response.json`
Observation: The press of week 9 returned HTTP 200. The sheet has 9.team (race group In, 77% playoff odds) and 8.team (race group Bubble, 42% playoff odds), and 8.bye says Carnell Tate, Pittsburgh Steelers, and Jaylen Warren start after the trade and have a bye in week 9.

## AT-10: A week with no chart still grades

App: pipeline
Then: the response is a read with a Lean, and the Case says the chart is missing.
Files: `evidence/AT-10/output.txt`, `evidence/AT-10/response.json`, `evidence/AT-10/api_run.py`
Observation: With the chart site blocked for the API process and the PNG and JSON of weeks 7, 8, and 9 moved out, the log says "no chart of the 2 weeks before week 9 is cached", and the sheet has trade.chart: "The chart of week 9 is missing". POST /analyze returned HTTP 200 with lean Lean no, and the Case says "This week's chart is missing". The chart files went back, and their hashes match the originals.

## AT-11: A player who is not on the chart stays in play

App: pipeline
Then: his fact says he is not on the chart, and the target step of the Finder log lists him among the players it asks about.
Files: `evidence/AT-11/output.txt`
Observation: DeMario Douglas has no row in the week 9 chart read, and the sheet of a press with him has "DeMario Douglas is not on the chart of week 9." The Find press for Return of T Mac with no partner returned HTTP 200, and each of the 5 target step lines lists DeMario Douglas with a Jev answer (0.31 to 0.57).

## AT-12: The sheet holds the news of a trade player

App: pipeline
Then: there are at most 2, newest first. Each text starts "Reported on <YYYY-MM-DD> by <Source>:", each date is in the last 7 days, and no URL is in the numbers.
Files: `evidence/AT-12/output.txt`, `evidence/AT-12/numbers.txt`, `evidence/AT-12/news_numbers.py`
Observation: At 6ba706cf, the eval sheet of trade 30 has 2 facts NEWS.6813.1 and NEWS.6813.2, both "Reported on 2026-11-09 by Rotoballer:", and the eval wrote the file at 2026-11-10T10:34:47-05:00. The record holds no numbers, so numbers.txt builds the same 2 facts again from the live feed at 6ba706cf: their numbers are date parts and counts, with no URL.

## AT-13: A Bullet that cites news names the report

App: pipeline
Then: each one holds "reported", "report", "per", "according to", "rumor", or the source name.
Files: `evidence/AT-13/output.txt`
Observation: At 6ba706cf, the 28 reads hold 2 Bullets that cite a NEWS. fact, in trades 21 and 30. Both start "Per Rotowire", the source name of the cited fact.

## AT-14: A failed news fetch never stops a grade

App: pipeline
Then: the response is 200 with a read, and the sheet has no `NEWS.` fact.
Files: `evidence/AT-14/output.txt`, `evidence/AT-14/response.json`, `evidence/AT-14/api_run.py`
Observation: With the Sleeper host of the API process set to a closed local port, the news fetch of 9221 and 9509 logged "Connection refused" and 0 items, and POST /analyze returned HTTP 200 with lean Pass, a Case, and 10 Bullets. The sheet log has no NEWS. fact; the block also cut the Sleeper stats endpoints, so the response lists stale ["stats"].

## AT-15: The news of a player is cached for 1 hour

App: pipeline
Then: the log shows no news fetch for that player on the second press.
Files: `evidence/AT-15/output.txt`, `evidence/AT-15/api_run.py`
Observation: Press 1 logged "News fetch of player 9221: 5 items". Press 2, a different trade with Jahmyr Gibbs 27 s later in the same process, logged "News of player 9221 from the cache" and no fetch for 9221.

## AT-16: The analyze document holds the Lean, the Case, and the Bullets

App: pipeline
Then: the document has a `lean` of Send it, Lean yes, Gut call, Lean no, or Pass, a `case`, and a fairness block. Each side has 3 to 5 Bullets, each with `text`, `mark`, `fact_id`, and `fact_text`. No key holds a letter, a factor, a decision, or an answer.
Files: `evidence/AT-16/output.txt`, `evidence/AT-16/request.json`, `evidence/AT-16/response.json`, `evidence/AT-16/keys.txt`, `evidence/AT-16/log.txt`
Observation: The shared API on port 8080 answered 200 in 24.4 s with `lean` "Lean no", a `case`, and a fairness block of state lopsided with `gives_more` 9. Each side has 5 Bullets with the keys `fact_id`, `fact_text`, `mark`, and `text`, and the key scan finds no key with letter, factor, decision, or answer. The shared API sets no app log handler, so its log holds only the access line.

## AT-17: A clear loss reads as a loss

App: pipeline
Then: the Lean is Pass or Lean no, and the fairness is lopsided with All You Need Is Love as the side that gives more.
Files: `evidence/AT-17/output.txt`, `evidence/AT-17/request.json`, `evidence/AT-17/response.json`, `evidence/AT-17/log.txt`
Observation: The shared API answered 200 with `lean` "Pass". The fairness block has state lopsided and `gives_more` 2, the roster id of All You Need Is Love.

## AT-18: The Case leads with its condition

App: pipeline
Then: it holds a condition, with "if" or "as long as".
Files: `evidence/AT-18/case.txt`
Observation: The first sentence of the Case of AT-16 is "If you believe Bijan's growing role in the passing game will outrun a weak Falcons offense, this can work, but I'd lean against it." It holds "if" and does not hold "as long as".

## AT-19: Every number, name, and fact id comes from the sheet

App: pipeline
Then: each cited fact id is on its sheet, and each number and each player name in a Bullet or a Case is in a cited fact.
Files: `evidence/AT-19/output.txt`, `evidence/AT-19/check_reads.py`
Observation: At 6ba706cf, over the 28 new eval reads, 276 of 276 cited fact ids are on their sheets. The strict check finds 0 numbers outside the cited facts. It finds 29 player names outside the text of a cited fact, 2 full and 27 last names, and each one names a player of the trade itself, such as "Patrick Mahomes" (trade 3).

## AT-20: No inner word reaches a read

App: pipeline
Then: no read holds "trade value" or "return bet".
Files: `evidence/AT-20/output.txt`, `evidence/AT-20/inner_words.py`
Observation: At 6ba706cf, the search covers 304 texts, the Case and the Bullets of the 28 new eval reads. It finds 0 hits of "trade value" and 0 hits of "return bet".

## AT-21: A failed Advisor gives an honest error that costs no grade

App: pipeline
Then: the response is a plain error with no read, the log shows two Advisor calls, and the grade count of the passphrase does not change.
Files: `evidence/AT-21/output.txt`, `evidence/AT-21/request.json`, `evidence/AT-21/response.json`, `evidence/AT-21/log.txt`, `evidence/AT-21/grades.txt`, `evidence/AT-21/server.txt`
Observation: My API on port 8081 with ANTHROPIC_API_KEY=sk-ant-not-a-valid-key answered 503 with only a `detail.message`: "The read of this trade did not come through. Try again in a minute. This try does not count toward your grades." The log shows "advisor attempt 1 failed" and "advisor attempt 2 failed", each with authentication_error, and the grade count stays at 6 before and after.

## AT-22: A repeat press gives the same read

App: pipeline
Then: the second document is the same as the first, and the log shows a cache hit.
Files: `evidence/AT-22/output.txt`, `evidence/AT-22/first.json`, `evidence/AT-22/second.json`, `evidence/AT-22/server.txt`
Observation: On my API on port 8081, `cmp` prints SAME for the two documents of the trade of AT-16. The first press logs time=27.0s cost=$0.0579 claude_calls=1, and the second logs time=1.7s cost=$0.0000 claude_calls=0. The cache writes no line of its own, so the zero-call press line is the sign of the hit.

## AT-23: The document version changes

App: pipeline
Then: the two versions differ.
Files: `evidence/AT-23/output.txt`
Observation: `DOCUMENT_VERSION` is 18 on `main` (47b1dc6d) and 21 on `manager-brain` (26dbed1b).

## AT-24: The Jev checks log and never block

App: pipeline
Then: the log has the result of the Jev faithfulness check and of the Jev rumor check for the Bullets, and each of the 28 trades still has a read.
Files: `evidence/AT-24/output.txt`
Observation: The eval log at 6ba706cf has 29 lines "Jev checks of the read, log only": one per read of the 28 trades and one for the 1 Finder pick. It shows 2 `rumor.*` results, both "no", and no line says the Jev checks failed. All 28 trades list a Lean, and `summary.json` shows trades 28, reads 28, and no error.

## AT-25: Jev requests stay under the rate limit

App: pipeline
Then: the log shows the Jev requests in waves and no 429 response.
Files: `evidence/AT-25/output.txt`, `evidence/AT-25/server.txt`, `evidence/AT-25/find/output.txt`, `evidence/AT-25/find/request.json`, `evidence/AT-25/find/response.json`, `evidence/AT-25/find/log.txt`
Observation: At b056a29f, the Find press ran on a plain API with no `--log-config`, and the app lines print through `configure_logging`. The log shows Jev wave 1 (partner filter) with 11 requests, wave 2 (targets) with 4, and wave 3 (shortlist) with 4. All 21 TypeSafe responses are 200, and the log holds no 429. The press ran on port 8081 with a cold cache, because the shared cache on port 8080 already held results.

## AT-26: Find with no partner searches the whole league

App: pipeline
Then: the log shows the partner filter on all 11 other teams. The document has 1 to 3 picks, each with a headline and 2 to 4 Bullets, or a plain empty line.
Files: `evidence/AT-26/output.txt`, `evidence/AT-26/request.json`, `evidence/AT-26/response.json`, `evidence/AT-26/log.txt`, `evidence/AT-26/server.txt`, `evidence/AT-26/picks.txt`
Observation: At 6ba706cf, on a cold plain API, the log shows a "Partner filter" line for each of the 11 other teams. The document has 1 pick, D'Andre Swift for Christian Watson with The Blue Tent, with a headline and 3 Bullets.

## AT-27: Find with one partner keeps to that partner

App: pipeline
Then: every pick is a trade with The Blue Tent.
Files: `evidence/AT-27/output.txt`, `evidence/AT-27/request.json`, `evidence/AT-27/response.json`, `evidence/AT-27/log.txt`, `evidence/AT-27/server.txt`
Observation: At 6ba706cf, the document has 1 pick, D'Andre Swift for Christian Watson, with 4 Bullets. Its sides are Maye d'force B with U and The Blue Tent, and `trade_pair.partner` is The Blue Tent.

## AT-28: No offer breaks a hard rule

App: pipeline
Then: no offer holds a kicker, a defense, a player out with no return week, or a handcuff.
Files: `evidence/AT-28/offers.txt`, `evidence/AT-26/log.txt`
Observation: At 6ba706cf, the log lists 95 offers that hold 15 players, all of position QB, RB, WR, or TE. Each of the 15 has no `injury_status` in the cached Sleeper players file of 2026-11-09 22:59, Puka Nacua included. The only RBs are Jahmyr Gibbs and D'Andre Swift, each at `depth_chart_order` 1.

## AT-29: Every offer is a small trade

App: pipeline
Then: every offer is 1-for-1, 2-for-1, or 1-for-2.
Files: `evidence/AT-29/offers.txt`
Observation: At 6ba706cf, the 95 offers count 33 of 1-for-1, 41 of 2-for-1, and 21 of 1-for-2.

## AT-30: A failed Advisor in the Finder gives the shortlist

App: pipeline
Then: the document has the fallback flag true and the shortlist offers, each with plain fact lines.
Files: `evidence/AT-30/output.txt`, `evidence/AT-30/request.json`, `evidence/AT-30/response.json`, `evidence/AT-30/log.txt`, `evidence/AT-30/server.txt`
Observation: At 6ba706cf, with ANTHROPIC_API_KEY=sk-ant-not-a-valid-key, the log shows "finder pick attempt 1 failed" and "attempt 2 failed" with authentication_error. The Find press answered 200 with `fallback` true and 10 shortlist trades. Each trade has `headline` null, no Bullets, and 2 or 3 `fact_lines` of plain facts, such as "Jahmyr Gibbs (RB, DET) scored 24 points per game over 8 games before the trade."

## AT-31: The Finder no longer offers Gibbs for Bijan

App: pipeline
Then: no pick sends Jahmyr Gibbs for Bijan Robinson.
Files: `evidence/AT-31/output.txt`, `evidence/AT-31/request.json`, `evidence/AT-31/response.json`, `evidence/AT-31/log.txt`, `evidence/AT-31/server.txt`
Observation: At 6ba706cf, the partner filter passed Return of T Mac, and the log lists 6 offers, each with CeeDee Lamb as the only player from Return of T Mac. No offer sends Jahmyr Gibbs for Bijan Robinson. The document has no pick and `empty` "No offer on the list both helps your lineup and gives the other manager a reason to say yes."

## AT-32: The analyzer agrees with a Finder pick

App: pipeline
Then: each read has a Lean of Send it, Lean yes, or Gut call.
Files: `evidence/AT-32/output.txt`, `evidence/AT-32/request.json`, `evidence/AT-32/response.json`, `evidence/AT-32/log.txt`, `evidence/AT-32/server.txt`, `evidence/AT-32/leans.txt`
Observation: At 6ba706cf, the one pick of AT-26, D'Andre Swift for Christian Watson, reads as "Lean yes". Its press logs time=23.2s cost=$0.0574 claude_calls=1.

## AT-33: A press stays in time and in cost

App: pipeline
Then: at least 4 of the 5 analyze presses take 30 s or less, and all 5 cost $0.15 or less. At least 4 of the 5 Finder presses take 35 s or less, and all 5 cost $0.15 or less.
Files: `evidence/AT-33/table.md`, `evidence/AT-33/server.txt`, `evidence/AT-33/analyze/output.txt`, `evidence/AT-33/analyze/log.txt`, `evidence/AT-33/analyze-2/output.txt`, `evidence/AT-33/analyze-2/log.txt`, `evidence/AT-33/analyze-3/output.txt`, `evidence/AT-33/analyze-3/log.txt`, `evidence/AT-33/analyze-4/output.txt`, `evidence/AT-33/analyze-4/log.txt`, `evidence/AT-33/analyze-5/output.txt`, `evidence/AT-33/analyze-5/log.txt`, `evidence/AT-33/find-1/output.txt`, `evidence/AT-33/find-1/log.txt`, `evidence/AT-33/find-2/output.txt`, `evidence/AT-33/find-2/log.txt`, `evidence/AT-33/find-3/output.txt`, `evidence/AT-33/find-3/log.txt`, `evidence/AT-33/find-4/output.txt`, `evidence/AT-33/find-4/log.txt`, `evidence/AT-33/find-5/output.txt`, `evidence/AT-33/find-5/log.txt`
Observation: At 6ba706cf, on plain APIs on port 8081, each with a cold result cache, the 5 analyze presses log 30.9 s, 25.8 s, 25.7 s, 20.7 s, and 22.3 s. Their costs run from $0.0524 to $0.0685. The 5 Find presses log 20.2 s, 25.9 s, 32.3 s, 24.1 s, and 25.6 s, with costs from $0.0739 to $0.0910. The 32.3 s Find made 2 Claude calls after a repair of pick 1.

## AT-34: The live eval reads all 28 trades

App: pipeline
Then: each trade has a Lean, a Case, and 3 to 5 Bullets per side, with no check failure after the retry. The Leans cover at least 3 of the 5 steps of the scale. The output has the cost and the time of the run.
Files: `evidence/AT-34/output.txt`
Observation: At 6ba706cf, run.txt and the 28 trade files show 28 reads, 0 errors, each with a Lean and a Case, 5 Bullets per side in 24 trades and 5 and 4 in 4, and 0 check failures after the retry. The Leans are Send it 5, Lean yes 11, Gut call 0, Lean no 5, and Pass 7, so 4 of the 5 steps have a Lean. The summary prints "Cost: $2.17" and "Time: 237 s."

## AT-35: Each client has a Playbook

App: pipeline
Then: cpc has a Playbook with its tips: RBs first in half PPR, contenders firm up, bubble teams take risks, a top 3 to 5 player beats two good ones, and managers here chase recent points. NorCal has a Playbook with general tips and no league-specific claim.
Files: `evidence/AT-35/output.txt`
Observation: The cpc Playbook has tips on RBs in half PPR, playoff teams that firm up, bubble or out teams that take risk, one consensus top 3 to 5 player over two good ones, and managers who look at recent points. The NorCal Playbook says the tips are general and that no tip makes a claim about its format or its managers.

## AT-36: The rubric and its words are gone

App: pipeline
Then: no code or copy holds a rubric, a start letter, a breakdown, an adjuster step, a verdict, a factor row, or a letter of a side. Each old adjuster writes facts as a Measure.
Files: `evidence/AT-36/search-pipeline.txt`
Observation: Pipeline half, at 6ba706cf: the searches of `packages/analyzer/python/src` and `apps/api/src` find no rubric, start letter, breakdown, adjuster, factor row, side letter, or verdict, and no old document key. The only hits are three prompt rules "never give a letter grade", in `advisor.md`, `finder_pick.md`, and the new `finder_pick_repair.md`. The old rubric files are gone, and `MEASURE_IDS` names 10 Measures that write facts, such as fit, standing, trend, injury, upside, superstar, and handcuff.

## AT-36 (site half)

App: site
Then: no code or copy holds a rubric, a start letter, a breakdown, an adjuster step, a verdict, a factor row, or a letter of a side. Each old adjuster writes facts as a Measure.
Files: `evidence/AT-36/search-site.txt`
Observation: The search of `packages/analyzer/site` and `apps/site/src` finds no rubric, start letter, breakdown, adjuster, or factor row. The four hits are test names and one comment that say "no letter grade". The word "verdict" appears only as the stable id `verdict-word` in `analyze-result.tsx`, in the egg tests, and in a tracker-rule test comment.

## AT-37: ADR 0030 is accepted

App: pipeline
Then: the ADR status reads accepted, and the glossary holds no term that the ADR drops.
Files: `evidence/AT-37/output.txt`
Observation: At 6ba706cf, ADR 0030 reads "Status: accepted." No dropped word is a term of GLOSSARY.md, and each of the 11 term greps exits 1. The dropped words show only in _Avoid_ lines, in the workflow terms Test verdict and Decision ticket, in the term Jev answer, and in plain sentences such as line 67, "The decision is for the asker."

## AT-38: The hero shows the Lean on its scale

App: site
Then: the hero shows the Lean word, and under it the 5-step scale from Pass to Send it with the step of that Lean lit.
Files: `evidence/AT-38/steps.json`, `evidence/AT-38/375-light.png`, `evidence/AT-38/375-dark.png`, `evidence/AT-38/768-light.png`, `evidence/AT-38/768-dark.png`, `evidence/AT-38/1280-light.png`, `evidence/AT-38/1280-dark.png`
Observation: Each shot shows the hero with the word "Lean no" and a 5-step scale (Pass, Lean no, Gut call, Lean yes, Send it) with the "Lean no" step lit in red. The trade is Maye d'force B with U giving Jahmyr Gibbs to Return of T Mac for Bijan Robinson. The fixed nav dock covers part of the Fairness card in the 375 and 768 full-page shots.

## AT-39: The Case is clamped on the phone

App: site
Then: before the tap the Case shows 3 lines. After the tap it shows in full.
Files: `evidence/AT-39/steps.json`, `evidence/AT-39/before-375-light.png`, `evidence/AT-39/before-375-dark.png`, `evidence/AT-39/after-375-light.png`, `evidence/AT-39/after-375-dark.png`
Observation: Before the tap the Case shows 3 lines that end in an ellipsis, with "Read the full case" under them. After the tap the Case shows the whole paragraph (about 14 lines) and the link is gone.

## AT-40: The hero shows the fairness line

App: site
Then: the hero shows "Lopsided: All You Need Is Love gives more."
Files: `evidence/AT-40/steps.json`, `evidence/AT-40/375-light.png`, `evidence/AT-40/375-dark.png`, `evidence/AT-40/768-light.png`, `evidence/AT-40/768-dark.png`, `evidence/AT-40/1280-light.png`, `evidence/AT-40/1280-dark.png`
Observation: The hero of the trade of Ja'Marr Chase to NFC Least for Xavier Worthy shows "Pass" with the Pass step lit. The Fairness card in the hero holds the pill "Lopsided: All You Need Is Love gives more." and the line "It gives more than it gets." Unchanged at 6ba706cf: the analyzer page code between 26dbed1b and 6ba706cf differs only in a comment of `lib/schemas/api.ts`, so I did not retake the shots.

## AT-41: One tab per team, the asker first

App: site
Then: before the tap, the tab of Maye d'force B with U is open. After the tap, the Bullets of Return of T Mac show.
Files: `evidence/AT-41/steps.json`, `evidence/AT-41/before-375-light.png`, `evidence/AT-41/before-375-dark.png`, `evidence/AT-41/before-768-light.png`, `evidence/AT-41/before-768-dark.png`, `evidence/AT-41/before-1280-light.png`, `evidence/AT-41/before-1280-dark.png`, `evidence/AT-41/after-375-light.png`, `evidence/AT-41/after-375-dark.png`, `evidence/AT-41/after-768-light.png`, `evidence/AT-41/after-768-dark.png`, `evidence/AT-41/after-1280-light.png`, `evidence/AT-41/after-1280-dark.png`
Observation: In the before shots the switcher has two tabs with "Maye d'force B with U" filled and its Bullets (For and Against) below. In the after shots "Return of T Mac" is filled and the lists show "Gets Jahmyr Gibbs", "Gives Bijan Robinson", and its own For and Against Bullets.

## AT-42: The Bullets sit in bands with their Marks

App: site
Then: the Bullets sit in For, then Against, then Even bands, with ▲, ▼, and – Marks. A band with no Bullet does not show.
Files: `evidence/AT-42/steps.json`, `evidence/AT-42/375-light.png`, `evidence/AT-42/375-dark.png`, `evidence/AT-42/768-light.png`, `evidence/AT-42/768-dark.png`, `evidence/AT-42/1280-light.png`, `evidence/AT-42/1280-dark.png`
Observation: The open tab shows a FOR band with ▲ rows, then an AGAINST band with ▼ rows. This read has no Even Bullet on the open tab, and no EVEN band shows. The – Mark and the EVEN band show in `evidence/AT-40/1280-light.png` and `evidence/AT-44/rows.txt`. Unchanged at 6ba706cf: the analyzer page code between 26dbed1b and 6ba706cf differs only in a comment of `lib/schemas/api.ts`, so I did not retake the shots.

## AT-43: A tap on a Bullet shows its fact

App: site
Then: its fact text opens under the row.
Files: `evidence/AT-43/steps.json`, `evidence/AT-43/375-light.png`, `evidence/AT-43/375-dark.png`, `evidence/AT-43/768-light.png`, `evidence/AT-43/768-dark.png`, `evidence/AT-43/1280-light.png`, `evidence/AT-43/1280-dark.png`
Observation: In each shot the first Bullet row ("Robinson's target share ...") is open with a flipped chevron. A smaller grey fact line shows under it, and the other rows stay closed.

## AT-44: A screen reader hears the Mark as a word

App: site
Then: the row reads "for", "against", or "even", and the glyph is hidden.
Files: `evidence/AT-44/steps.txt`, `evidence/AT-44/rows.txt`, `evidence/AT-44/snapshot-full.txt`
Observation: The accessibility tree of the Return of T Mac tab names each row button with its Mark word first: "for Gibbs's Lions rank 6th ...", "against Gibbs's snap share ...", and "even Gibbs faces MIN ...". Each button holds a StaticText "for", "against", or "even". The tree has no ▲, ▼, or – glyph (0 matches).

## AT-45: A 3-team trade shows three tabs

App: site
Then: the switcher shows one tab per team, three in all.
Files: `evidence/AT-45/steps.json`, `evidence/AT-45/375-light.png`, `evidence/AT-45/375-dark.png`, `evidence/AT-45/768-light.png`, `evidence/AT-45/768-dark.png`, `evidence/AT-45/1280-light.png`, `evidence/AT-45/1280-dark.png`
Observation: The trade I picked was Maye d'force B with U gives Jahmyr Gibbs to Return of T Mac, Return of T Mac gives CeeDee Lamb to Lil Fridge, and Lil Fridge gives Derrick Henry to Maye d'force B with U. The Sides switcher shows three tabs: Maye d'force B with U, Return of T Mac, and Lil Fridge. The hero shows "Pass", and the swap card lists three teams.

## AT-46: No letter shows

App: site
Then: no letter grade shows on either page.
Files: `evidence/AT-46/finder-text.txt`, `evidence/AT-46/analyzer-text.txt`, `evidence/AT-46/search.txt`, plus the shots of `evidence/AT-38/` and `evidence/AT-47/`
Observation: The rendered text of the Finder cards and of the analyzer read has no "letter", "grade", or "GPA" word. A search for a lone letter A to F finds only the team name "Maye d'force B with U", "A cold game ...", and "40 degrees F". The shots of AT-38 and AT-47 show a Lean word, Bullets, and no letter badge.

## AT-47: The Finder card uses the same rows

App: site
Then: the card shows a headline, the swap, and 2 to 4 Bullet rows with the same Marks and tap as the analyzer. The tap opens the analyzer read of that trade.
Files: `evidence/AT-47/steps.json`, `evidence/AT-47/build-note.txt`, `evidence/AT-47/card-375-light.png`, `evidence/AT-47/card-375-dark.png`, `evidence/AT-47/card-768-light.png`, `evidence/AT-47/card-768-dark.png`, `evidence/AT-47/card-1280-light.png`, `evidence/AT-47/card-1280-dark.png`, `evidence/AT-47/read-375-light.png`, `evidence/AT-47/read-375-dark.png`, `evidence/AT-47/read-768-light.png`, `evidence/AT-47/read-768-dark.png`, `evidence/AT-47/read-1280-light.png`, `evidence/AT-47/read-1280-dark.png`
Observation: At commit 6ba706cf, on a build with the Finder on (see `build-note.txt`), Find with no partner shows "Trade 1 of 1". The card has a headline, a swap card (Christian Watson for D'Andre Swift), 3 Bullet rows with ▲, ▲, and – Marks and a chevron, and a "See the Full Result" button. The headline is partly under the fixed "Grade the Trade" bar. The tap opens the analyzer read of that trade: "Lean yes", the 5-step scale, the Fairness card "Fair", and For, Against, and Even bands.

## AT-48: Find works with no partner picked

App: site
Then: the button is on, and the press shows picks or the plain empty line.
Files: `evidence/AT-48/steps.json`, `evidence/AT-48/build-note.txt`, `evidence/AT-48/before-375-light.png`, `evidence/AT-48/before-375-dark.png`, `evidence/AT-48/before-768-light.png`, `evidence/AT-48/before-768-dark.png`, `evidence/AT-48/before-1280-light.png`, `evidence/AT-48/before-1280-dark.png`, `evidence/AT-48/after-375-light.png`, `evidence/AT-48/after-375-dark.png`, `evidence/AT-48/after-768-light.png`, `evidence/AT-48/after-768-dark.png`, `evidence/AT-48/after-1280-light.png`, `evidence/AT-48/after-1280-dark.png`
Observation: At commit 6ba706cf, with Your Team picked and no partner chosen, the "Find a Trade" button shows as a filled button under the unselected partner list. After the press one pick shows ("Trade 1 of 1": Christian Watson for D'Andre Swift). In the after shots the "Find a Trade" button looks grey.

## AT-49: The page shows the honest error

App: site
Then: the page shows a plain error and Try Again, and no Lean.
Files: `evidence/AT-49/steps.txt`, `evidence/AT-49/375-light.png`, `evidence/AT-49/375-dark.png`, `evidence/AT-49/768-light.png`, `evidence/AT-49/768-dark.png`, `evidence/AT-49/1280-light.png`, `evidence/AT-49/1280-dark.png`
Observation: Each shot shows the form with the picked trade and an error box: "The read of this trade did not come through. Try again in a minute. This try does not count toward your grades." A "Try Again" button sits under it. No hero, no Lean word, and no scale show.

## AT-50 (pipeline half): The copy says no "rival" and no name of the commissioner

App: pipeline
Then: neither appears. A player whose name holds "Brian", such as Brian Robinson, does not count.
Files: `evidence/AT-50/search-pipeline.txt`, `evidence/AT-50/copy_words.py`
Observation: At 6ba706cf, the search covers 360 texts of the 28 new eval reads: each Case, fairness reason, gains line, and Bullet. It finds 0 hits of "rival". All 6 hits of "brian" are the NFL player Brian Robinson or Brian Robinson Jr., so after the search removes those player names, 0 hits remain.

## AT-50 (site half)

App: site
Then: neither word appears.
Files: `evidence/AT-50/search-site.txt`
Observation: At commit 6ba706cf, the search for "rival" and "brian" finds no hit in `packages/analyzer/site`, in `clients/cpc` copy, brand, and client files, or in `clients/norcal/copy.toml`. In `apps/site/src` the only hit is one comment in `globals.css` that names Brian (the commissioner). It is not page copy.

## AT-51: Reduced motion shows the page at rest

App: site
Then: the Lean word and the Bullets show at once, with no rise.
Files: `evidence/AT-51/steps.txt`, `evidence/AT-51/375-light.png`, `evidence/AT-51/375-dark.png`, `evidence/AT-51/768-light.png`, `evidence/AT-51/768-dark.png`, `evidence/AT-51/1280-light.png`, `evidence/AT-51/1280-dark.png`
Observation: Each shot was taken 300 ms after the Lean scale appeared, with reduced motion on. It shows the Lean word "Lean no", the lit scale step, the Case, and all For and Against Bullets fully drawn, with no faded or offset element.

## AT-52: The Finder builds no 2-for-2 trade

App: pipeline
Then: no offer is 2-for-2 or larger.
Files: `evidence/AT-52/offers.txt`
Observation: At 6ba706cf, the 95 offers count 33 of 1-for-1, 41 of 2-for-1, and 21 of 1-for-2. No offer has 2 or more players on each side.

## AT-53: A press makes no web search

App: pipeline
Then: neither press makes a web search call.
Files: `evidence/AT-53/output.txt`, `evidence/AT-53/server.txt`, `evidence/AT-53/analyze/log.txt`, `evidence/AT-53/find/log.txt`
Observation: At 6ba706cf, the cold plain logs of the analyze press of the AT-16 trade and the Find press of AT-26 have 0 lines with web_search, web search, or server_tool_use. Calls go only to api.sleeper.app, api.typesafe.ai, api.anthropic.com, and the chart list of peakedinhighskool.com from `league/chart.py`. Each press made 1 Claude call.
