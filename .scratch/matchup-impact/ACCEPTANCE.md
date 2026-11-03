# Matchup impact: acceptance tests

Spec: `.scratch/matchup-impact/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

A build runs the odds engine again, so the odds after the week can differ a little from the live week 8 page. Each test that names the odds after the week means the playoff odds that the same build writes in `data/2026/week-08/facts.json` under `odds.teams`. The odds before the week are fixed: they come from `data/2026/week-07/facts.json`.

## Tests

AT-1: The impact fact of a loser
App: pipeline
Stories: 1, 4, 8, 11, 19, 24, 25
Given: `2026` week 8. Lil Fridge lost to Maye d'force B with U 80.11 to 121.16. Its week 7 playoff odds were 99%.
When: `make -C apps/pipeline build WEEK=8`
Then: `M1.impact` says Lil Fridge fell from 1st to 2nd in the standings, its playoff odds went from 99% to its week 8 playoff odds this week, and it missed the median and went 0-2 this week.
Evidence: the command output and the text of `M1.impact` in `data/2026/week-08/facts.json`, beside `odds.teams.3.playoff`.

AT-2: The impact fact of a winner who held its place
App: pipeline
Stories: 5, 8, 11, 19
Given: `2026` week 8. Maye d'force B with U beat Lil Fridge. Its week 7 playoff odds were 49%.
When: `make -C apps/pipeline build WEEK=8`
Then: `M1.impact` says Maye d'force B with U stayed 5th in the standings, its playoff odds went from 49% to its week 8 playoff odds this week, and it beat the median and went 2-0 this week.
Evidence: the command output and the text of `M1.impact` in `data/2026/week-08/facts.json`, beside `odds.teams.9.playoff`.

AT-3: The impact fact of a climb
App: pipeline
Stories: 3, 8
Given: `2026` week 8. To Infinity and Bijan beat Bo Girds. It was 11th after week 7, with 1% playoff odds.
When: `make -C apps/pipeline build WEEK=8`
Then: `M6.impact` says To Infinity and Bijan rose from 11th to 9th in the standings, and its playoff odds went from 1% to its week 8 playoff odds this week.
Evidence: the command output and the text of `M6.impact` in `data/2026/week-08/facts.json`, beside `odds.teams.7.playoff`.

AT-4: A streak that ended and a streak that grew
App: pipeline
Stories: 14, 15
Given: `2026` week 8. To Infinity and Bijan had lost 3 straight head-to-head games. Bo Girds had lost 3 straight.
When: `make -C apps/pipeline build WEEK=8`
Then: `M6.impact` says To Infinity and Bijan ended a 3-game losing streak, and Bo Girds has lost 4 straight.
Evidence: the command output and the text of `M6.impact` in `data/2026/week-08/facts.json`.

AT-5: A streak under 3 is left out
App: pipeline
Stories: 13, 22
Given: `2026` week 8. Lil Fridge has lost 2 straight head-to-head games. Maye d'force B with U has no streak of 3 or more.
When: `make -C apps/pipeline build WEEK=8`
Then: `M1.impact` names no streak.
Evidence: the command output and the text of `M1.impact` in `data/2026/week-08/facts.json`.

AT-6: No cut, no clinch, and no out in week 8
App: pipeline
Stories: 18, 22
Given: `2026` week 8. The six teams in the playoff spots after week 8 are the same six teams as after week 7. Every team has the status `open`.
When: `make -C apps/pipeline build WEEK=8`
Then: no `M<n>.impact` fact of week 8 names the cut, a clinch, or an out.
Evidence: the command output and the text of `M1.impact` to `M6.impact` in `data/2026/week-08/facts.json`.

AT-7: An early week leaves out the odds part
App: pipeline
Stories: 23
Given: `2026` week 6. It is the first week with odds, so no week has saved odds before it.
When: `make -C apps/pipeline build WEEK=6`
Then: each `M<n>.impact` fact of week 6 has the standings place and the median result, and names no playoff odds.
Evidence: the command output and the text of `M1.impact` to `M6.impact` in `data/2026/week-06/facts.json`.

AT-8: The matchup prose blocks have the impact fact in scope
App: pipeline
Stories: 2, 26
Given: `2026` week 8.
When: `make -C apps/pipeline build WEEK=8`
Then: the fact lists of `motw` and of `recap_1` to `recap_6` each hold the `M<n>.impact` fact of their matchup, and the fact lists of `next_week` and `game_changer` hold no impact fact.
Evidence: the command output and the fact list of each of the nine prose blocks in `data/2026/week-08/facts.json`.

AT-9: Each of the seven matchup blurbs says the impact
App: pipeline
Stories: 1, 2, 26, 27
Given: `2026` week 8, with the writer rule for the impact.
When: `make -C apps/pipeline build WEEK=8`
Then: each of the 7 blurbs `motw` and `recap_1` to `recap_6` has at least one sentence that cites its `M<n>.impact` fact. A FAIL starts the ticket for a code check.
Evidence: the command output and the 7 blurbs, each sentence with the fact IDs it cites.

AT-10: An impact odds number is named and dated
App: pipeline
Stories: 9, 10
Given: `2026` week 8, with the blurbs of AT-9.
When: `make -C apps/pipeline build WEEK=8`
Then: each blurb sentence with an odds number from an `M<n>.impact` fact says "playoff odds" and "this week".
Evidence: each such sentence from the 7 blurbs, with the fact IDs it cites.

AT-11: The six recaps say the impact in different ways
App: pipeline
Stories: 21
Given: `2026` week 8, with the blurbs of AT-9.
When: `make -C apps/pipeline build WEEK=8`
Then: no two of the recap sentences that cite an `M<n>.impact` fact start with the same three words.
Evidence: the first sentence that cites `M<n>.impact` in each of `recap_1` to `recap_6`.

AT-12: The Matchup of the Week blurb says the upset once
App: pipeline
Stories: 2
Given: `2026` week 8. The Matchup of the Week is The Blue Tent against London Cooking, an upset.
When: `make -C apps/pipeline build WEEK=8`
Then: the `motw` blurb names the upset in one sentence only.
Evidence: the `motw` blurb, each sentence with the fact IDs it cites.

AT-13: The site and the live page do not change
App: both
Stories: none
Given: the Spec branch `matchup-impact` after its last ticket.
When: `git diff main -- apps/site`
Then: the diff is empty, so `apps/site/public/2026/week-08/page.json` and the site code are the same as on `main`.
Evidence: the command and its empty output.

## Trace

Story 1: AT-1, AT-9
Story 2: AT-8, AT-9, AT-12
Story 3: AT-3
Story 4: AT-1
Story 5: AT-2
Story 6: no test. Reason: the six teams in the playoff spots were the same after weeks 6, 7, and 8, so no real week shows a cross. A unit test of the ticket covers it.
Story 7: no test. Reason: the same as story 6.
Story 8: AT-1, AT-2, AT-3
Story 9: AT-10
Story 10: AT-10
Story 11: AT-1, AT-2
Story 12: no test. Reason: each loser of week 8 missed the median. A unit test of the ticket covers it.
Story 13: AT-5
Story 14: AT-4
Story 15: AT-4
Story 16: no test. Reason: no team has clinched yet. AT-6 covers the case with no clinch. A unit test of the ticket covers a clinch.
Story 17: no test. Reason: no team is out yet. AT-6 covers the case with no out. A unit test of the ticket covers an out.
Story 18: AT-6
Story 19: AT-1, AT-2
Story 20: no test. Reason: the choice of the parts is the writer's judgment by design. AT-9 checks the result.
Story 21: AT-11
Story 22: AT-5, AT-6
Story 23: AT-7
Story 24: AT-1
Story 25: AT-1
Story 26: AT-8, AT-9
Story 27: AT-9
Story 28: no test. Reason: it is the absence of a code check, which the diff shows. AT-9 decides if a later ticket adds one.
Story 29: no test. Reason: the spec does not change the odds engine, which the diff shows.
Out of scope "The Next Week blurb": AT-8
Out of scope "Any change to the site": AT-13

## Revisions

None yet.
