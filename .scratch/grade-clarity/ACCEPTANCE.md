# Grade clarity: acceptance tests

Spec: `.scratch/grade-clarity/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

The grade reads the live snapshot, so a value can move after the week 9 games. Each value named below holds through week 8. The evidence agent records the values that the spec does not give: the counts, the opponents, and the byes of trade A, the ranks of Washington, and the trades of AT-15, AT-25, and AT-36.

## Tests

AT-1: Layout A order
App: site
Stories: 1, 2, 3, 4
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: The reader grades trade A on the analyze route.
Then: The page shows the decision with its "why" sentence, then the trade card, then one card for each side, then the as-of line, in one column.
Evidence: Screenshots of the analyze result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-2: The side card before a tap
App: site
Stories: 5, 6, 8, 10, 20
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: The reader grades trade A and taps nothing.
Then: Each side card shows Cooper and Washington with a headshot, the position, the NFL team, and the Season rank, then 2 or 3 bullets, then the "This week and next" box. The fold is closed.
Evidence: Screenshots of each side card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-3: The fold
App: site
Stories: 21, 23
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: The reader taps "How the grade adds up · <n> rows" on the roster 10 card.
Then: The fold opens and shows each row with a mark, up, down, or even. <n> equals the count of rows that show.
Evidence: Screenshots of the open fold at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-4: The players stack on a phone
App: site
Stories: 39, 40
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: The reader grades trade A at each width.
Then: At 375 px the two players of a side stack. At 768 and 1280 px they stand next to each other. The two side cards never stand next to each other.
Evidence: Screenshots of the roster 10 card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-5: Three sides
App: both
Stories: 41
Given: `2026` week 9. Roster 4 gives Rome Odunze (`11620`) to roster 12. Roster 12 gives Garrett Wilson (`8146`) to roster 7. Roster 7 gives Ryan Flournoy (`11783`) to roster 4. Roster 4 asks.
When: The reader grades `SIDES="4:11620@12 12:8146@7 7:11783@4" ASKER=4`.
Then: The document has three sides, each with bullets, Week lines, and factors. The page shows three side cards in the same form.
Evidence: The command output, the document, and screenshots of the result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-6: The Season rank
App: pipeline
Stories: 6
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: Cooper has `season_rank` WR60, the rank by total points through week 8, as Sleeper sorts it.
Evidence: The command and the `trade.sides` players of the document.

AT-7: The Recent rank on a large gap
App: pipeline
Stories: 7, 44
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: Cooper has `recent_rank` WR18. His gap is 42, and `RECENT_RANK_GAP` is 12.
Evidence: The command, the player fields, and the `RECENT_RANK_GAP = 12` line of the analyzer `tunables.py`.

AT-8: No Recent rank on a small gap
App: pipeline
Stories: 7
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: Each traded player whose Recent rank is 11 spots or fewer from his Season rank has `recent_rank` null.
Evidence: The command, and the Season rank and the Recent rank of each traded player.

AT-9: The Position rank by season points per game
App: pipeline
Stories: 37
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The grade reads Cooper as WR26, by season points per game over the games played, not WR18.
Evidence: The command, and the Position rank that the snapshot gives for `13276`.

AT-10: The bullets
App: pipeline
Stories: 8, 9
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: `POST /analyze` of trade A on the local API with the Claude call.
Then: Each side has 2 or 3 `bullets`, and each bullet is one sentence.
Evidence: The request and the `sides[].bullets` of the document.

AT-11: The Week line counts
App: pipeline
Stories: 11
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: Each side has a Week line for week 9 and week 10. Each line gives the count of WRs in the top 36 who play, before and after the trade.
Evidence: The command and the `sides[].week_lines` of the document.

AT-12: The Week line opponent
App: pipeline
Stories: 15
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The line of each week names the opponent of the player the side gets, with its rank in points allowed to WRs, rank 1 the most.
Evidence: The command, the `week_lines`, and the points allowed table of week 8.

AT-13: Byes
App: pipeline
Stories: 12
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks. The evidence agent records each WR of rosters 6 and 10 with a bye in week 9 or 10.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The line of each week names each WR of the side who has a bye that week. A side with no bye names none.
Evidence: The command, the `week_lines`, and the bye week of each WR on the two rosters.

AT-14: Out last week
App: pipeline
Stories: 13, 16
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks. A WR on roster 6 or 10 is Out or on IR in the Sleeper players file.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API on a Tuesday or a Wednesday.
Then: The week 9 line names the Out player as "listed Out last week". The week 10 line names him only when his status is IR, PUP, NA, or Sus.
Evidence: The command, the run date, the `week_lines`, and the status of each named player.

AT-15: Steps up
App: pipeline
Stories: 14
Given: `2026` week 9. Mike Evans, SF WR rank 1 on the newest depth chart, is Out. The evidence agent finds the SF WR directly behind him and a trade of two rosters that moves him.
When: The reader grades that trade.
Then: The week 9 line of the side that holds the SF WR says he steps up. If no roster holds that WR, the test is BLOCKED.
Evidence: The trade, the command, the `week_lines`, and the SF WR rows of the depth chart.

AT-16: A stale depth chart names no step-up
App: pipeline
Stories: 17
Given: The trade of AT-15. The newest depth chart `dt` is 2026-11-03T07:02Z.
When: The reader grades it with the grade time set to 2026-11-05T08:00Z or later, more than 48 hours after `dt`.
Then: No Week line names a step-up.
Evidence: The command, the grade time, the `dt`, and the `week_lines`.

AT-17: The Week line moves no letter
App: pipeline
Stories: 18
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: `factors` has no Week line row, and the breakdown holds the same adjusters as on `main`, with no new one.
Evidence: The command, the breakdown, and the list of adjusters.

AT-18: The verdict can name the Week line
App: pipeline
Stories: 19
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Build the fact sheet of trade A.
Then: The fact sheet holds one Week line fact for each side, with the text of its two lines.
Evidence: The command and the Week line facts.

AT-19: Silent rows hide
App: pipeline
Stories: 22
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: No side has a handcuff row, because no player in trade A is a handcuff.
Evidence: The command and the `sides[].factors` names.

AT-20: No banned word
App: pipeline
Stories: 24, 35, 36
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: `POST /analyze` of trade A with the Claude call.
Then: No bullet, factor reason, or verdict reason holds "trade value", "highest-value", "best lineup", "the line", "hole", "win-now move", "return bet", "star", "opportunity", "one step", "no step", "takes RB", "takes WR", or "sits on the bench".
Evidence: The request, the document, and a scan of its text for each word.

AT-21: The deal row
App: pipeline
Stories: 25
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The first factor of each side is the deal row, in a form such as "You get far more than you give." It names no source. No `chart` block stays on a side.
Evidence: The command and the first factor of each side.

AT-22: The roster row
App: pipeline
Stories: 26
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The roster row of each side counts its WRs in the top 36 before and after, such as "You keep 3 WRs in the top 36, and you get the better player."
Evidence: The command and the roster row text.

AT-23: The standing row
App: pipeline
Stories: 27
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The standing row of each side names its race, its need, and whether the trade meets it, in one sentence.
Evidence: The command and the standing row text.

AT-24: The usage row
App: pipeline
Stories: 28
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The usage row has one clause for Cooper and one for Washington, each with the snap share, the target share, and the air yards per target. It names no week and no route share.
Evidence: The command and the usage row text.

AT-25: The handcuff and upside rows
App: pipeline
Stories: 30, 31
Given: `2026` week 9. The evidence agent finds a trade where one side gets Tyjae Spears (`9508`) and holds Tony Pollard (`5967`).
When: The reader grades that trade.
Then: The handcuff row reads "Spears backs up your RB, Pollard, on the Titans depth chart." An upside row, when it shows, is one plain sentence such as "Spears gets more work while Pollard is out." If no such trade exists, the test is BLOCKED.
Evidence: The trade, the command, and the two rows.

AT-26: The schedule row
App: pipeline
Stories: 32
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: The schedule row names each playoff opponent of weeks 15 to 17 with its rank at the position. It has no sentence "The schedule leans for this side".
Evidence: The command and the schedule row text.

AT-27: The as-of line
App: site
Stories: 33
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: The reader grades trade A.
Then: The as-of line names the stats and the fetch time of the rosters, and no "Chart week".
Evidence: Screenshots of the as-of line at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-28: The no-values note
App: pipeline
Stories: 34
Given: A `2026` trade week with no value chart, so `chart_week` is null.
When: Grade trade A on that snapshot.
Then: `as_of.no_chart_note` reads "This week's player values are not out yet, so both sides start even."
Evidence: The command and the `as_of` block.

AT-29: The fallback
App: pipeline
Stories: 8, 10, 20
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks. The Claude call fails twice.
When: `POST /analyze` of trade A.
Then: `fallback` is true. Each side has no bullets, and still has its Week lines and its factors.
Evidence: The request and the document.

AT-30: The cache key
App: pipeline
Stories: 38
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Compute the cache key of trade A, then change the depth chart `dt`, then change the status of one player that a Week line reads.
Then: Each change gives a new key.
Evidence: The three keys and the change of each step.

AT-31: The finder facts
App: pipeline
Stories: 42
Given: `2026` week 9. The asker is roster 10, and the partner is roster 6.
When: Run the finder for the pair.
Then: The facts of each traded player give the Season rank, such as WR60, and no slot fact.
Evidence: The command and the fact sheet of one finder trade.

AT-32: The weekly report keeps its Position rank
App: pipeline
Stories: 43
Given: `2026` week 8.
When: `make -C apps/pipeline build WEEK=8` on the spec branch and on `main`.
Then: The Position ranks in the two `page.json` files are the same.
Evidence: Both commands and the diff of the rank fields.

AT-33: The finder prompt and view stay
App: site
Stories: none
Given: `2026` week 9, client `norcal`, which turns on the finder.
When: Compare the finder prompt and the finder view with `main`.
Then: The finder prompt file has no change, and the finder cards look the same as on `main`.
Evidence: The diff of the finder prompt, and screenshots of the finder cards at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-34: No Week line past the next week
App: pipeline
Stories: none
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: Each side has Week lines for week 9 and week 10 only.
Evidence: The command and the weeks of `week_lines`.

AT-35: The expected gap row stays off
App: pipeline
Stories: none
Given: `2026` week 9, the trade window after week 8. Trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: Run `make -C apps/pipeline analyze CLIENT=cpc SIDES="10:13276@6 6:9487@10" ASKER=10`, or a `POST /analyze` of the same trade on the local API.
Then: No side has an expected gap row, and `EXPECTED_ADJUSTER_ON` is False.
Evidence: The command, the factor names, and the tunable line.

AT-36: The injury row
App: pipeline
Stories: 29
Given: `2026` week 9. The evidence agent finds a trade that moves a player with a return week in the Returns file or with weeks on the injury report.
When: The reader grades that trade.
Then: The injury row names the return week and the count of weeks on the injury report, such as "Cooper is out until week 11. He was on the injury report in 5 of 8 weeks."
Evidence: The trade, the command, and the injury row.

## Trace

Story 1: AT-1
Story 2: AT-1
Story 3: AT-1
Story 4: AT-1
Story 5: AT-2
Story 6: AT-2, AT-6
Story 7: AT-7, AT-8
Story 8: AT-2, AT-10, AT-29
Story 9: AT-10
Story 10: AT-2, AT-29
Story 11: AT-11
Story 12: AT-13
Story 13: AT-14
Story 14: AT-15
Story 15: AT-12
Story 16: AT-14
Story 17: AT-16
Story 18: AT-17
Story 19: AT-18
Story 20: AT-2, AT-29
Story 21: AT-3
Story 22: AT-19
Story 23: AT-3
Story 24: AT-20
Story 25: AT-21
Story 26: AT-22
Story 27: AT-23
Story 28: AT-24
Story 29: AT-36
Story 30: AT-25
Story 31: AT-25
Story 32: AT-26
Story 33: AT-27
Story 34: AT-28
Story 35: AT-20
Story 36: AT-20
Story 37: AT-9
Story 38: AT-30
Story 39: AT-4
Story 40: AT-4
Story 41: AT-5
Story 42: AT-31
Story 43: AT-32
Story 44: AT-7
Out of scope "The prompt and the view of the trade finder": AT-33
Out of scope "The Position rank of the weekly report and of the manager grade": AT-32
Out of scope "A Week line past the next week": AT-34
Out of scope "Route share in the usage row": AT-24
Out of scope "The expected gap row": AT-35
Out of scope "An audit of the other numbers of a grade": no test. Reason: no agent builds an audit by mistake.
Out of scope "The suggested counters": no test. Reason: no ticket touches the slot.

## Revisions

None yet.
