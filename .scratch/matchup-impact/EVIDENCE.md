# Matchup impact: evidence

Spec: `.scratch/matchup-impact/PRD.md`. Acceptance tests: `.scratch/matchup-impact/ACCEPTANCE.md`.
Built from: `c052d92`, on 2026-11-03. The agent gives no Test verdict. Brian gives one for each test.

The week 8 build and the week 6 build ran once each. Their full logs are `evidence/build-08/output.txt` and `evidence/build-06/output.txt`. Each exited 0. After each build, `git restore` put back the tracked week files, so the branch holds no week output.

## AT-1: The impact fact of a loser

App: pipeline
Then: `M1.impact` says Lil Fridge fell from 1st to 2nd in the standings, saw its playoff odds go from 99% to its week 8 playoff odds this week, and missed the median to go 0-2 this week.
Files: `evidence/AT-1/output.txt`
Observation: The fact reads "Lil Fridge fell from 1st to 2nd in the standings, saw its playoff odds go from about 99% to 86% this week, and missed the median to go 0-2 this week." `odds.teams.3.playoff` is 86.

## AT-2: The impact fact of a winner who held its place

App: pipeline
Then: `M1.impact` says Maye d'force B with U stayed 5th in the standings, saw its playoff odds go from 49% to its week 8 playoff odds this week, and beat the median to go 2-0 this week.
Files: `evidence/AT-2/output.txt`
Observation: The fact reads "Maye d'force B with U stayed 5th in the standings, saw its playoff odds go from about 49% to 77% this week, and beat the median to go 2-0 this week." `odds.teams.9.playoff` is 77.

## AT-3: The impact fact of a climb

App: pipeline
Then: `M6.impact` says To Infinity and Bijan rose from 11th to 9th in the standings, and its playoff odds went from 1% to its week 8 playoff odds this week.
Files: `evidence/AT-3/output.txt`
Observation: The fact reads "To Infinity and Bijan rose from 11th to 9th in the standings, saw its playoff odds go from about 1% to 7% this week". `odds.teams.7.playoff` is 7.

## AT-4: A streak that ended and a streak that grew

App: pipeline
Then: `M6.impact` says To Infinity and Bijan ended a 3-game losing streak, and Bo Girds has lost 4 straight.
Files: `evidence/AT-4/output.txt`
Observation: The fact says Bo Girds "has now lost 4 straight", and To Infinity and Bijan "ended a 3-game losing streak".

## AT-5: A streak under 3 is left out

App: pipeline
Then: `M1.impact` names no streak.
Files: `evidence/AT-5/output.txt`
Observation: `M1.impact` has the place, the odds, and the median for both teams, and no streak words.

## AT-6: No cut, no clinch, and no out in week 8

App: pipeline
Then: no `M<n>.impact` fact of week 8 names the cut, a clinch, or an out.
Files: `evidence/AT-6/output.txt`
Observation: None of the six facts holds "playoff spots", "clinched", or "out of the playoff race". The status of each team is `open`.

## AT-7: An early week leaves out the odds part

App: pipeline
Then: each `M<n>.impact` fact of week 6 has the standings place and the median result, and names no playoff odds.
Files: `evidence/AT-7/output.txt`
Observation: Each of the six week 6 facts has a place and a median part, and none says "playoff odds". The week 6 file has its own odds, so only the missing week 5 odds leave the part out. `M4.impact` also shows a loser who beat the median: "Bo Girds fell from 2nd to 3rd in the standings and beat the median to go 1-1 this week."

## AT-8: The matchup prose blocks have the impact fact in scope

App: pipeline
Then: the fact lists of `motw` and of `recap_1` to `recap_6` each hold the `M<n>.impact` fact of their matchup, and the fact lists of `next_week` and `game_changer` hold no impact fact.
Files: `evidence/AT-8/output.txt`
Observation: `motw` holds `M3.impact`, and each `recap_<n>` holds `M<n>.impact`. `next_week` and `game_changer` hold no impact fact.

## AT-9: Each of the seven matchup blurbs says the impact

App: pipeline
Then: each of the 7 blurbs `motw` and `recap_1` to `recap_6` has at least one sentence that cites its `M<n>.impact` fact. A FAIL starts the ticket for a code check.
Files: `evidence/AT-9/output.txt`
Observation: Each of the 7 blurbs has at least one sentence that cites its impact fact. `recap_5` cites `M5.impact` in its last sentence only, in "the winners hold their spot and the losers stay dead last". `recap_1` names no number from the impact fact.

## AT-10: An impact odds number is named and dated

App: pipeline
Then: each blurb sentence with an odds number from an `M<n>.impact` fact says "playoff odds" and "this week".
Files: `evidence/AT-10/output.txt`
Observation: Six sentences cite an impact fact and hold a percent. Each says "playoff odds" and "this week". The `motw` sentence gives only the odds after the week: "rose to about 75% this week" and "slid to about 83%".

## AT-11: The six recaps say the impact in different ways

App: pipeline
Then: no two of the recap sentences that cite an `M<n>.impact` fact start with the same three words.
Files: `evidence/AT-11/output.txt`
Observation: The first three words of the first impact sentence of each recap are "The old leader", "Return of T", "The Blue Tent", "Unsolicited Dak Picks", "Hunter Henry is", and "This week dropped". No two are the same.

## AT-12: The Matchup of the Week blurb says the upset once

App: pipeline
Then: the `motw` blurb names the upset in one sentence only.
Files: `evidence/AT-12/output.txt`
Observation: Only sentence 0 of the 6 `motw` sentences says "upset": "The Blue Tent edged London Cooking 100.31 to 98.88 in an upset."

## AT-13: The site and the live page do not change

App: both
Then: the diff is empty, so `apps/site/public/2026/week-08/page.json` and the site code are the same as on `main`.
Files: `evidence/AT-13/output.txt`
Observation: `git diff main -- apps/site` printed 0 lines and exited 0.
