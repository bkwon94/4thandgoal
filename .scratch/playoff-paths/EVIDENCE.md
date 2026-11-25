# The Race: evidence

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests: `.scratch/playoff-paths/ACCEPTANCE.md`.
Built from: `5f26bcb0`, on 2026-11-24. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 23 min for 18 site tests (set A, AT-26 to AT-43) and 8 min for 8 site tests with shots (set B, AT-44 to AT-55).

Smoke run: `Smoke run: 7 flows, 7 passed, 0 failed`. Folder: `evidence/smoke/`.
Rebuild list: `REBUILD.md`, with the output `evidence/rebuild.log`.
Background check: `make check` at `ce601c12`, from 2026-11-25 03:59 to 04:23 UTC, exit 0.

The builds of the evidence: the pipeline tests ran on `ce601c12`. The site tests ran on `ce601c12`, and AT-26, AT-27, AT-37, AT-39, and AT-44 ran again on `5f26bcb0`. The two commits differ only in `packages/league/site/live-names.tsx` and its test, the live-name swap of older weeks. Each site build used cpc week 11 and NorCal week 10 `sim.json` and `topics.json` rebuilt with the code of the branch, from the saved inputs. The instruments: `evidence/site-set/a/` for set A, and `evidence/site-set-b/` for set B, both Playwright WebKit at 390x660 (iPhone 15), 810x980, 1080x740, and 1280x800, light and dark, with an overlap check per shot.

## AT-1: The tiebreak orders tied teams the way Sleeper does

App: pipeline
Then: roster 9 sits above roster 1, as in the Sleeper `bracket.json` of week 8, because roster 9 has more Points Against.
Files: `evidence/AT-1/check.py`, `evidence/AT-1/output.txt`
Observation: The run reads the saved norcal 2026 week 8 data and its `bracket.json`. The standings order and the sim order both read 6, 9, 1, 8, 10, 11 for places 1 to 6, the same as the Sleeper seeds. Roster 9 is at place 2 with (5, 3, 1010.86, 980.3), and roster 1 is at place 3 with (5, 3, 1010.86, 978.84). The tuple is wins, losses, Points For, Points Against, so roster 9 has 1.46 more Points Against. The output lists all 12 rosters in order with their Sleeper seed.

## AT-2: The other stored brackets still match

App: pipeline
Then: the first 6 rosters of each week equal the Sleeper seeds of that week, in order.
Files: `evidence/AT-2/output.txt`, `evidence/AT-1/check.py`
Observation: The run covers cpc weeks 6 to 10 and norcal weeks 8 to 10, 8 weeks in all. For each week the output prints the Sleeper seeds 1 to 6, the standings order 1 to 6, and the sim order 1 to 6, then the table of all rosters. In each of the 8 weeks the three lists hold the same 6 rosters in the same order.

## AT-3: The weekly build writes the Goals of each team

App: pipeline
Then: each of the 12 pages in `week-11/sim.json` holds the odds and the status of the spot Goal, the bye Goal, and seeds 1 to 6.
Files: `evidence/AT-3/check.py`, `evidence/AT-3/output.txt`
Observation: `make sim CLIENT=cpc WEEK=11` writes `clients/cpc/build/2026/week-11/sim.json`. Each of the 12 pages has the goal keys spot, bye, and seed-1 to seed-6, each with `odds` and `status`. The spot odds of each page equal `teams.<id>.playoff`. The output gives the full Goal fields of Bo Girds (spot 48 open, bye 2 open) and The Blue Tent (spot 83 open, bye 18 open).

## AT-4: The open Goal follows the 5% rule

App: pipeline
Then: each page opens on the best Goal with odds of 5% or more, in the order 1 seed, bye, spot, and Lil Fridge at 15-7 opens on the bye or the 1 seed.
Files: `evidence/AT-4/check.py`, `evidence/AT-4/output.txt`
Observation: The table lists the 12 teams with their seed-1, bye, and spot odds and their `open_goal`. Lil Fridge is 15-7 with seed-1 49, bye 75, and spot 99, and opens on seed-1. Bengals Buddies has seed-1 2 and bye 9 and opens on bye. Bo Girds has seed-1 1 and bye 2 and opens on spot. NFC Least and Unsolicited Dak Picks have 0 for each Goal and open on spot.

## AT-5: The status follows the plain check on wins for each Goal

App: pipeline
Then: each status is Clinched, In the hunt, or Out exactly as the hand check says, for the spot, the bye, and each seed.
Files: `evidence/AT-5/check.py`, `evidence/AT-5/output.txt`
Observation: `check.py` holds the hand check, a plain count of wins with 6 more wins at most over 3 weeks. It compares the hand status with the file status for each of the 12 teams and each of the 8 Goals. The last line reads "statuses: 96 same, 0 different, of 96". NFC Least (5 wins) and Unsolicited Dak Picks (6 wins) are out for each Goal in both. Every other status is open in both.

## AT-6: The Finish list sums to 100% with the right final records

App: pipeline
Then: it lists 7 Finishes from 6-0 to 0-6, the chances add to 100% within 1 point, and 4-2 has the final record 15-13.
Files: `evidence/AT-6/check.py`, `evidence/AT-6/output.txt`
Observation: The page of Bo Girds has the record [11, 11]. The spot Finish list has 7 Finishes, 6-0 to 0-6. Their chances are 9.1, 12.9, 25.7, 20.0, 20.0, 8.0, and 4.4, which add to 100.1. The 4-2 Finish has the final record 15-13.

## AT-7: A NorCal Finish list counts head-to-head games only

App: pipeline
Then: each Finish list of `week-10/sim.json` runs 4-0 to 0-4, and no page holds a median result.
Files: `evidence/AT-7/check.py`, `evidence/AT-7/output.txt`
Observation: `make sim CLIENT=norcal WEEK=10` writes `clients/norcal/build/2026/week-10/sim.json` with `median_game` False and 4 weeks left. For each of the 12 pages and each of the 8 Goals, the Finishes run [4, 3, 2, 1, 0] more wins. Each week card holds 2 results with the median None. The output gives the spot Finish list of puurdygood, 4-0 to 0-4.

## AT-8: A Path reaches 90% or names 3 teams

App: pipeline
Then: each Path names 1 to 3 teams, each condition is a final record at most, each Path has 400 runs or more, and each Path that names fewer than 3 teams has odds of 90% or more, unless it is the Best chance Path of its Finish.
Files: `evidence/AT-8/check.py`, `evidence/AT-8/output.txt`
Observation: The file holds 46 Paths: 23 name 1 team, 21 name 2 teams, and 2 name 3 teams. The fewest runs of a Path is 403. Each condition is a roster and a final record, and 0 conditions fail the check of a final record with at most 5 more wins. 21 Paths name fewer than 3 teams with odds under 90, and the Finish of each of the 21 has the case `best`.

## AT-9: No Path repeats

App: pipeline
Then: no two Paths of one Finish hold the same set of conditions.
Files: `evidence/AT-9/check.py`, `evidence/AT-9/output.txt`
Observation: The script compares the condition sets of the Paths of each Finish. 33 Finishes hold Paths. 0 Finishes hold a repeated Path.

## AT-10: A sure or hopeless Finish has no Path

App: pipeline
Then: none of those Finishes holds a Path.
Files: `evidence/AT-10/check.py`, `evidence/AT-10/output.txt`
Observation: The `odds` field is a whole number, and its top value is 99. 0 Finishes have an `odds` field of 99.5 or more, and 112 Finishes have odds under 0.5, all at 0. None of those 112 holds a Path. By case, 29 `sure` Finishes, all at odds 99, and 407 `none` Finishes, at odds 0 or 1, each hold no Path.

## AT-11: A Finish under 90% keeps its best chance

App: pipeline
Then: that Finish holds exactly 1 Path, marked as the best chance.
Files: `evidence/AT-11/check.py`, `evidence/AT-11/output.txt`
Observation: 21 Finishes have a best Path under 90%. Each of the 21 holds exactly 1 Path and has the case `best`. The output prints 2 examples in full, both of The Blue Tent: the spot Finish of 1 more win, with Path odds 20, and the bye Finish of 4 more wins, with Path odds 40.

## AT-12: A Week plan has one row per week left

App: pipeline
Then: it holds 3 rows, weeks 12 to 13 to 14, each with a result, the Score to beat, and 1 or 2 games to root for, and a loss row holds no score against the opponent.
Files: `evidence/AT-12/check.py`, `evidence/AT-12/output.txt`
Observation: The first Path of the 4-2 Finish of Bo Girds names roster 8 at 15-13, with odds 94. Its plan has 3 rows, weeks 12, 13, and 14. Week 12 against roster 5 is a win above the median with 2 root-for games. Week 13 against roster 4 is a win above with 2 games. Week 14 against roster 3 is a loss below with 1 game. Each plan row has the keys week, opponent, game, median, and root_for, and no score. The scores are in the `score_to_beat` list of the page, one entry for each week: week 12 is win 109, win_sure 127, median 107, median_sure 114. Week 14, the loss row, also has an entry there, with win 113.

## AT-13: "Try it" odds equal a What-if of the plan

App: pipeline
Then: the odds of the Goal equal the "Try it" odds of the plan within 1 point.
Files: `evidence/AT-13/check.py`, `evidence/AT-13/output.txt`
Observation: The script reruns the sim on `week-11/sim.json` for roster 6 with the 3 results of the plan held: week 12 win above, week 13 win above, week 14 loss below. The Try it odds of the plan are 81. The What-if odds of the spot Goal are 81, with 10000 runs and 7582 effective runs. The difference is 0 points.

## AT-14: The Score to beat gives a 50% score and an 80% score

App: pipeline
Then: it holds 2 scores against Teez Nuts and 2 against the median, and each 80% score is higher than its 50% score.
Files: `evidence/AT-14/check.py`, `evidence/AT-14/output.txt`
Observation: The week card of Bo Girds is week 12 against roster 5, Teez Nuts. The week 12 Score to beat reads win 109, win_sure 127, median 107, median_sure 114. The output also shows weeks 13 and 14, against NFC Least and Lil Fridge.

## AT-15: The root-for list holds every other game for each result

App: pipeline
Then: each of the 4 results holds 5 rows, one per other head-to-head game, each with the odds after each side wins, and a row with a lift under 1 point is marked doesn't matter.
Files: `evidence/AT-15/check.py`, `evidence/AT-15/output.txt`, `evidence/AT-15/reading.py`, `evidence/AT-15/reading.txt`
Observation: The run is again on head `5f26bcb0`. The new `sim.json` is byte-equal to the published copy in the Spec worktree. The week card of Bo Girds holds 4 results: win above, win below, loss above, and loss below, at 68, 39, 40, and 15 spot odds. Each result holds 5 rows, one for each of the 5 other week 12 games. Each row holds `odds`, the odds after the winner wins, and `other`, the odds after the other side wins. `reading.txt` lists each row with its lift and its mark. 4 rows have a lift of 0, under ROOT_FOR_LIFT = 1, and get "Doesn't matter". Two of them are NFC Least against Lil Fridge at 68 and 68, and Unsolicited Dak Picks against Maye d'force B with U at 39 and 39. The file holds no flag field for the mark. `reading.txt` quotes the source: `week_card.py` line 19 says "the page reads that from the two odds, so the file holds no flag for it". `week-card.tsx` line 254 shows the gray "Doesn't matter" tag when `row.odds - row.other < FLAT`, with `FLAT = 1` on line 33.

## AT-16: Median rooting names at most 2 teams

App: pipeline
Then: it holds 1 or 2 other teams, each with the odds after that team misses the median.
Files: `evidence/AT-16/check.py`, `evidence/AT-16/output.txt`
Observation: Each of the 4 week 12 results of Bo Girds holds 2 teams in `median_root`, each with its odds. For example, win above lists Omarion Himpton at 73 and Bengals Buddies at 71, and loss below lists 💿 🐑 at 19 and Omarion Himpton at 19.

## AT-17: The Clinch lines agree with a brute-force check

App: pipeline
Then: each Clinch line of the board names a set that makes its team Clinched or Out for its Goal, and the check finds no team with such a set and no line.
Files: `evidence/AT-17/check.py`, `evidence/AT-17/output.txt`
Observation: `check.py` holds the brute-force check, which lists 9024 sets of results of week 12. The board holds 7 Clinch lines: Lil Fridge spot in, Maye d'force B with U spot in, Bo Girds bye out, Immaculate Concepcion spot out and bye out, and Nico Collinsizer and Omarion Himpton bye out. The last line reads "ways checked 33; ways with a set that does not give the status 0; teams with a set and no line 0". Each team and Goal with 0 sets has no line, and each team already in or out has no line.

## AT-18: The tiebreak gap shows only when close

App: pipeline
Then: a page holds a gap only when another team is within 1 win and 50 points of it at the edge of the Goal.
Files: `evidence/AT-18/check.py`, `evidence/AT-18/output.txt`
Observation: The script orders the teams by wins, then Points For, then Points Against. It prints each page and Goal that holds a tiebreak gap, beside the close teams that a hand check finds. 12 gaps show, all on open Goals, and each names a team from the hand list. The other 84 Goals hold no gap. The output has no line "no gap but close by hand".

## AT-19: The sim file stays small

App: pipeline
Then: the file of the latest week is 50 KB gzip or less. The size of week 10 is in the record, with no bar, because a past week loads rarely.
Files: `evidence/AT-19/output.txt`
Observation: The command measures the 3 rebuilt `sim.json` files with `gzip.compress`. cpc 2026 week 11 is 337076 bytes raw and 44959 bytes gzip. cpc 2026 week 10 is 401537 bytes raw and 52300 bytes gzip. norcal 2026 week 10 is 306656 bytes raw and 47875 bytes gzip.

## AT-20: A What-if returns the Paths and the board odds

App: pipeline
Then: each response holds the Finish list, the Paths, the Week plans, the week card, and the board odds, and the two responses are equal.
Files: `evidence/AT-20/check.py`, `evidence/AT-20/output.txt`, `evidence/AT-20/request-1.json`, `evidence/AT-20/request-2.json`, `evidence/AT-20/response-1-cut.json`, `evidence/AT-20/response-1.json`, `evidence/AT-20/response-2-cut.json`, `evidence/AT-20/response-2.json`
Observation: The local evidence API of pp-head runs on port 8093 with the rebuilt cpc week 11 `sim.json`. Each of the 2 calls returns 200 with 142299 bytes, in 1.23 s and 1.26 s. The response holds `page.finishes` for each of the 8 Goals, with 6 Paths, each with a Week plan. It also holds `page.week_card` and a board of 12 rows with the odds of each Goal. The two responses are byte-equal. The `-cut.json` files hold the page Finish list, the week card, the Goals, and the board.

## AT-21: A What-if holds no Clinch lines

App: pipeline
Then: it holds no Clinch line.
Files: `evidence/AT-21/check.py`, `evidence/AT-21/output.txt`, `evidence/AT-20/response-1.json`
Observation: The script reads `AT-20/response-1.json`. The board block has 12 rows, and each row holds only the keys `goals` and `roster_id`. The response holds 0 keys with "clinch" in the name.

## AT-22: A What-if with no set result equals the file

App: pipeline
Then: the page block equals the page of Bo Girds in `week-11/sim.json`.
Files: `evidence/AT-22/check.py`, `evidence/AT-22/output.txt`, `evidence/AT-22/page.diff`, `evidence/AT-22/request.json`, `evidence/AT-22/response.json`
Observation: The call with `{"you": 6, "set": []}` returns 200 with 142385 bytes. The script compares the response page with `pages.6` of `clients/cpc/published/2026/week-11/sim.json` of pp-head. That file is the same rebuilt file as in the Spec worktree. The page keys are the same, and 0 JSON paths differ. `page.diff` is empty.

## AT-23: A What-if on Fly stays under 2.5 s

App: pipeline
Then: the median time is 2.5 s or less.
Files: none
Observation: Not recorded. Its Given line needs the merged branch deployed to Fly, and its Evidence line says it runs after the merge. No unmerged branch deploys to Fly.

## AT-24: The race Topic is the first Suggestion in a regular week

App: pipeline
Then: the first of the 3 Suggestions is the playoff race Topic.
Files: `evidence/AT-24/api-log.txt`, `evidence/AT-24/check.py`, `evidence/AT-24/output.txt`, `evidence/AT-24/request.json`, `evidence/AT-24/response.json`
Observation: The local evidence API of pp-head runs with the real Jev and live Sleeper data, with no Claude key. The live league is past week 11. The request asks for the Suggestions of Bo Girds, roster 6, with the order of Tuesday. The response is 200 with the picks ["playoff_race", "weak_spots", "stack_up"], and the fact of playoff_race is "48% playoff odds". Jev lists 4 urgent Topics: weak_spots 0.95, stack_up 0.93, week_recap 0.77, and playoff_race 0.73. `api-log.txt` shows the head start of weak_spots, which ended as an error with 0 tokens because the run had no Claude key.

## AT-25: The race Topic ranks as usual after week 14

App: pipeline
Then: the playoff race Topic is not pinned first; its place follows the usual rank.
Files: `evidence/AT-25/check.py`, `evidence/AT-25/output.txt`
Observation: The test runs the Suggestions route on the recorded week 6 Sleeper data of the API suite, with the FakeJev of the suite and every lift at 0.1. It runs as week 14 and as week 15, for Bo Girds with the order of Tuesday. As week 14 the picks are ["playoff_race", "week_recap", "last_matchup"]. As week 15 the picks are ["week_recap", "last_matchup", "power_rankings"], and playoff_race keeps rank 4 of the order of the day, out of the 3 picks. The two suite tests of AT-24 and AT-25 also run, and the line reads "3 passed".

## AT-26: The race Answer adds the Finish list and the link

App: both (pipeline part)
Then: the Answer shows the odds, the top 3 Finishes for a playoff spot, no pill for a team In the hunt, and the link "Open The Race" to `/sim/2026/`.
Files: `evidence/AT-26/check.py`, `evidence/AT-26/output.txt`
Observation: This entry is the pipeline part only. The race Answer of Bo Girds in `clients/cpc/build/2026/week-11/topics.json` has the fact "48% playoff odds" and the stat "Playoff odds" 48%. It has `block.finishes` with 3 Finishes: 4-2 ending 15-13 at 25.7% and odds 80, 3-3 ending 14-14 at 20.0% and odds 25, and 2-4 ending 13-15 at 20.0% and odds 3. These are the 3 highest chances of the 7 Finishes in AT-6. `block.pill` is null. The file holds no link, so the link "Open The Race" is the part of the site. The stat "Seed" reads "None" and the row note reads "Seed None". The published file on main shows the same text.

App: site (the site part only; the pipeline part has its own files in this folder)
Then: the Answer shows the odds, the top 3 Finishes for a playoff spot, no pill for a team In the hunt, and the link "Open The Race" to `/sim/2026/`.
Files: `evidence/AT-26/site-steps.txt`, `evidence/AT-26/site-answer.txt`, `evidence/AT-26/site-answer-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-26/site-answer-view1-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-26/site-answer-view2-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-26/site-answer-view3-390x660-{light,dark}.png`, `evidence/AT-26/site-api-{390x660,810x980,1080x740,1280x800}-{light,dark}.json`, `evidence/AT-26/site-overlap.txt`, `evidence/AT-26/site-5f26bcb0-answer.txt`, `evidence/AT-26/site-5f26bcb0-answer-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-26/site-5f26bcb0-answer-view1-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-26/site-5f26bcb0-answer-view2-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-26/site-5f26bcb0-answer-view3-390x660-{light,dark}.png`, `evidence/AT-26/site-5f26bcb0-api-{390x660,810x980,1080x740,1280x800}-{light,dark}.json`, `evidence/AT-26/site-5f26bcb0-overlap.txt`, `evidence/AT-26/site-5f26bcb0-tries.txt`, `evidence/AT-26/site-tries.txt`, `evidence/AT-26/site-tap-cause.txt`, `evidence/AT-26/site-tap-probe.mjs.txt`, `evidence/AT-26/site-tap-probe-390x660-dark.log`, `evidence/AT-26/site-tap-probe-390x660-dark-first.log`, `evidence/AT-26/site-tap-probe-810x980-dark.log`, `evidence/AT-26/site-tap-probe-trial1-{before,after}-tap.png`
Observation: On ce601c12 and again on 5f26bcb0 (files `site-5f26bcb0-*`), a tap on the Suggestion "Playoff race" with Your team Bo Girds shows an Answer with "PLAYOFF ODDS 48%" and the Finishes 4-2 (ends 15-13, 80%), 3-3 (ends 14-14, 25%), and 2-4 (ends 13-15, 3%). It also shows a 12-row table where Bo Girds has only a "YOU" tag and no pill, and the link "Open The Race" with href `/sim/2026/`, in all 8 shots of each run, with 0 overlaps and 0 covered text. The second tap of the ce601c12 run came from the script, not the site (`site-tap-cause.txt`): its selector took the quick chip "Playoffs", which has the same aria-label, and a first tap on that chip only opens a strip with "Open →", as designed. With the fixed tap, the 5f26bcb0 run shows the Answer after the first tap in 8 of 8 runs, 2 of them with the "Playoffs" chip in the row (`site-tries.txt`). In the full-page shots the sticky Ask bar draws over table rows 4 to 8, and the viewport shots show those rows.

## AT-27: The page is The Race

App: site
Then: the page title reads "The Race", the menu item reads "The Race", and the short label reads "Race".
Files: `evidence/AT-27/steps.txt`, `evidence/AT-27/page-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-27/menu-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-27/labels.txt`, `evidence/AT-27/short-label.txt`, `evidence/AT-27/overlap.txt`
Observation: The page shows the heading "The Race" and the document title "The Race 2026 · Cornerstone Fantasy Football League". The menu sheet at 390 and 810 and the header pill bar at 1080 and 1280 show the item "The Race", checked as the current page, with 0 overlaps and 0 covered text in all 16 shots. No screen shows the short label "Race" at any size, so I took no extra shot (`short-label.txt`). The label is held in `SHORT.sim` of `apps/site/src/app/shell-props.ts` line 24 and set on each `NavItem.short` (`packages/design/site/shell/nav.ts` line 14). No component reads `.short`: the pill bar and the menu sheet render `.label`. The built export holds `"label":"The Race","short":"Race"`, and the run of the unit test "with the short label Race (AT-50)" prints "1 pass, 0 fail".

## AT-28: The Goal switch changes every part

App: site
Then: the odds of the card, the Finish list, the board bars, and the board order all show the odds of a bye.
Files: `evidence/AT-28/steps.txt`, `evidence/AT-28/before-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-28/after-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-28/state.txt`, `evidence/AT-28/overlap.txt`
Observation: Before the tap the card reads "48% SPOT ODDS"; after the tap on Bye it reads "2% BYE ODDS", the Finish list reads "odds of a bye" (6-0 26%, the rest 1%), and the board reads "Each team's odds of a bye." with rows and bar widths in bye-odds order (Lil Fridge 75%, Maye d'force B with U 62%, Teez Nuts 23%, down to 0%). The rows under the bye Goal show "Out of the bye race with ..." lines; the overlap check found 0 overlaps and 0 covered text in all 16 shots.

## AT-29: The seed picker shows one seed

App: site
Then: the card, the Finish list, and the board show the odds of the 3 seed, and the board shows no Clinch line.
Files: `evidence/AT-29/steps.txt`, `evidence/AT-29/seed-3-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-29/state.txt`, `evidence/AT-29/overlap.txt`
Observation: After Seed, then 3, the seed row 1 to 6 shows 3 as selected, the card reads "6% SEED 3 ODDS", the Finish list reads "Odds of the 3 seed" (6-0 47%, 5-1 12%, the rest 1%), and the board reads "Each team's odds of the 3 seed." in that order (Teez Nuts 22% first). The page holds no line that starts with "Clinches" or "Out with" (`state.txt` clinchLines is empty), the root-for part reads "Pick Spot or Bye to see who to root for.", and the overlap check found 0 overlaps and 0 covered text.

## AT-30: The Your team card opens in place

App: site
Then: the card opens in the page, with no sheet, and shows the Finish list, then the week card.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/loaded-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-30/tap-1-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-30/tap-2-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-30/state.txt`, `evidence/AT-30/overlap.txt`
Observation: The card loads open (aria-expanded "true") with the Finish list above "Week 12 vs Teez Nuts"; the first tap closes it to the header row ("tap-1"), and the second tap opens it again in the page with the same order ("tap-2"). No dialog opens at any step (0 open dialogs in `state.txt`), and the overlap check found 0 overlaps and 0 covered text in all 24 shots.

## AT-31: A Finish shows its Paths with their copy

App: site
Then: the Finish reads "4-2 · ends 15-13" with its chance, and each Path reads "If <team> ends <record> or worse…" and "Happens N% · you're in N%.".
Files: `evidence/AT-31/steps.txt`, `evidence/AT-31/finish-4-2-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-31/paths.txt`, `evidence/AT-31/overlap.txt`, `evidence/AT-31/reading.txt`
Observation: The opened Finish reads "4-2 · ends 15-13 · 26% likely" with 3 Paths: "If 💿 🐑 ends 15-13 or worse." / "Happens 44% · you're in 94%.", "If The Blue Tent ends 15-13 or worse." / "Happens 30% · you're in 91%.", and "If Bengals Buddies ends 15-13 or worse." / "Happens 46% · you're in 93%.". Each Path line ends with a period, not "…"; the overlap check found 0 overlaps and 0 covered text.

## AT-32: A Finish shows the copy of its case

App: site
Then: a Finish at 99.5% or more reads "You're in whatever the others do.", a Finish under 0.5% reads "No way in at this record.", and a Finish under 90% shows "Best chance".
Files: `evidence/AT-32/steps.txt`, `evidence/AT-32/finish-6-0-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-32/finish-0-6-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-32/finish-3-3-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-32/finishes.txt`, `evidence/AT-32/overlap.txt`, `evidence/AT-32/reading.txt`
Observation: The 6-0 Finish (shown 99%, case "sure" in `week-11/sim.json`) reads "You're in whatever the others do."; the 0-6 Finish (shown 1%, case "none") reads "No way in at this record."; the 3-3 Finish (25%) shows "BEST CHANCE" over the Path "If 💿 🐑 ends 15-13 or worse and Omarion Himpton ends 14-14 or worse." / "Happens 28% · you're in 45%.". The page shows the 0-6 odds as "1%"; the overlap check found 0 overlaps and 0 covered text in all 24 shots.

## AT-33: A Path opens its Week plan

App: site
Then: a sheet opens with the header "Your plan to 15-13 · you're in N%", 3 week rows with "Score N to win, N to be sure", and the order line when the order does not matter.
Files: `evidence/AT-33/steps.txt`, `evidence/AT-33/plan-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-33/sheet.txt`, `evidence/AT-33/overlap.txt`
Observation: A sheet opens with the header "Your plan to 15-13 · you're in 81%", the line "Any 4 wins of your 6 work. This is the most common order.", and 3 week rows: weeks 12 and 13 read "Score 109 to win, 127 to be sure." and "Score 102 to win, 120 to be sure." with median scores, and week 14 (vs Lil Fridge, "Lose and miss the median.") has no score line. The button reads "Try it: you're in 81%"; the overlap check found 0 overlaps and 0 covered text in the open sheet.

## AT-34: "Try it" sets the plan as a What-if

App: site
Then: the set line lists the 3 results of the plan with a Reset, and the odds of the card equal the "Try it" odds of the header within 1 point.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/plan-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-34/after-try-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-34/state.txt`, `evidence/AT-34/api-{390x660,810x980,1080x740,1280x800}-{light,dark}.json`, `evidence/AT-34/overlap.txt`, `evidence/AT-34/5f26bcb0-reading.txt`, `evidence/AT-34/5f26bcb0-plan-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-34/5f26bcb0-after-try-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-34/5f26bcb0-overlap.txt`
Observation: On 5f26bcb0, `5f26bcb0-reading.txt` quotes for each of the 8 runs: the sheet header "Your plan to 15-13 · you're in 81%", the button "Try it: you're in 81%", the request "POST /clients/cpc/sim/what-if {"you":6,"set":[{"week":12,"game":"win","median":"above"},{"week":13,"game":"win","median":"above"},{"week":14,"game":"loss","median":"below"}]}", "response status: 200", and "response page.playoff: 81". After the tap it quotes "open dialogs after the tap: 0", the card "YOUR TEAM Bo Girds 11-11 81% SPOT ODDS", and the set line "What-if: Wk 12 win, beat median · Wk 13 win, beat median · Wk 14 lose, miss median Reset", the same in all 8 runs. The ce601c12 recording (`state.txt`, `api-*.json`) holds the same values, and the overlap check found 0 overlaps and 0 covered text in all shots of both recordings.

## AT-35: The week card shows the Score to beat

App: site
Then: it names Teez Nuts and shows "to win" and "to be sure" scores against Teez Nuts and against the median.
Files: `evidence/AT-35/steps.txt`, `evidence/AT-35/week-card-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-35/week-card.txt`, `evidence/AT-35/overlap.txt`
Observation: The week card reads "Week 12 vs Teez Nuts" over a table "SCORE TO BEAT / TO WIN / TO BE SURE" with "Beat Teez Nuts 109 127" and "Beat the median 107 114". The overlap check found 0 overlaps and 0 covered text in all 8 shots.

## AT-36: A result tile sets a What-if

App: site
Then: the set line lists that result, and the Finish list and the board odds change to the numbers of the response.
Files: `evidence/AT-36/steps.txt`, `evidence/AT-36/before-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-36/after-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-36/state.txt`, `evidence/AT-36/api-{390x660,810x980,1080x740,1280x800}-{light,dark}.json`, `evidence/AT-36/overlap.txt`
Observation: The tap sends `{"you":6,"set":[{"week":12,"game":"loss","median":"below"}]}`, the API answers 200, and the set line reads "What-if: Wk 12 lose, miss median" with "Reset". The card changes from 48% to 15%, the Finish list to 4-2 74%, 3-3 22%, 2-4 2%, 1-5 1%, and the board to Teez Nuts 98%, The Blue Tent 86%, 💿 🐑 78%, Bengals Buddies 75%, Omarion Himpton 41%, Bo Girds 15%, the same numbers as `page` and `teams` of the response; the overlap check found 0 overlaps and 0 covered text, and the full-page "after" shots draw the sticky header mid-image because the page had scrolled.

## AT-37: The root-for list shows every game with both results

App: site
Then: the list shows 5 games, each with "<winner> beats <loser> → N%" and the other result below it, a gray "Doesn't matter" tag on a game under 1 point, and 1 or 2 median rows.
Files: `evidence/AT-37/steps.txt`, `evidence/AT-37/root-for-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-37/root-for.txt`, `evidence/AT-37/api-{390x660,810x980,1080x740,1280x800}-{light,dark}.json`, `evidence/AT-37/overlap.txt`, `evidence/AT-37/doesnt-matter-tests.txt`, `evidence/AT-37/variant-under-1pt-diff.txt`, `evidence/AT-37/variant-under-1pt-half-build.txt`, `evidence/AT-37/variant-under-1pt-zero-root-for-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-37/variant-under-1pt-zero-root-for.txt`, `evidence/AT-37/variant-under-1pt-zero-tags.txt`, `evidence/AT-37/variant-under-1pt-zero-overlap.txt`
Observation: On the real data, after the tap (a What-if answer with `page.playoff` 69), the list reads "If you win and beat the median, you sit at 69%. Root for:". It has 5 games, each "<winner> beats <loser> → N%" over "<other> wins → N%", the last one "Lil Fridge beats NFC Least → 69%" over "NFC Least wins → 68%", then 2 median rows. No game has the tag after the tap. Before any tap, the real `week-11/sim.json` already holds one game 0 points apart, "NFC Least vs Lil Fridge" (68 and 68), and it shows a gray "DOESN'T MATTER" tag. The variant run uses a changed copy of `week-11/sim.json`, not the real data, on 5f26bcb0. With a copy that has one game 0.5 point apart, the build exits 1, because the schema takes only whole numbers (`variant-under-1pt-half-build.txt`). A copy with "Unsolicited Dak Picks beats Maye d'force B with U" changed from 70/68 to 68/68 shows "Unsolicited Dak Picks vs Maye d'force B with U" with the gray tag (text rgb(102,102,102) on rgb(235,235,235) in light) in all 8 shots, with 0 overlaps and 0 covered text. The run of the 9 committed tests of `week-card.test.tsx` prints "9 pass, 0 fail"; they include "lists the 5 other games with both results, a gray tag on a game under 1 point, and 1 or 2 median rows" (`doesnt-matter-tests.txt`).

## AT-38: The League board shows every team in odds order

App: site
Then: it shows 12 rows in odds order for a playoff spot, Bo Girds has the accent bar and a "You" tag, and every other bar is ink.
Files: `evidence/AT-38/steps.txt`, `evidence/AT-38/board-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-38/board.txt`, `evidence/AT-38/you-tag.txt`, `evidence/AT-38/overlap.txt`
Observation: The board shows 12 rows from Lil Fridge 99% down to NFC Least 0%, in falling odds order, and the row "Bo Girds YOU 11-11 48%" has a red name and a bar of `rgb(184, 52, 42)`. Every other filled bar is `oklab(0.191251 0 0 / 0.8)` in light and `oklab(1 0 0 / 0.8)` in dark, and the two 0% rows show only the gray track; the overlap check found 0 overlaps and 0 covered text.

## AT-39: The board pills show Clinched and Out only

App: site
Then: a Clinched team shows a green pill naming its best Goal, an Out team shows a red pill, and a team In the hunt shows no pill.
Files: `evidence/AT-39/steps.txt`, `evidence/AT-39/board-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-39/pill-contrast.txt`, `evidence/AT-39/overlap.txt`, `evidence/AT-39/pill-tests.txt`, `evidence/AT-39/variant-clinched-diff.txt`, `evidence/AT-39/variant-clinched-board-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-39/variant-clinched-pill-contrast.txt`, `evidence/AT-39/variant-clinched-overlap.txt`
Observation: On the real data, on the spot Goal, only Unsolicited Dak Picks and NFC Least show a pill, a red "Out", and the 10 other rows show no pill. No team in `week-11/sim.json` has a Clinched status, so no green pill shows there. The "Out" pills measure 5.73 contrast in light and 7.94 in dark. The variant run uses a changed copy of `week-11/sim.json`, not the real data, on 5f26bcb0: Lil Fridge has spot "in", and Maye d'force B with U has spot "in" and seed-1 "in" (`variant-clinched-diff.txt`). It shows a green "Clinched spot" pill on Lil Fridge, a green "Clinched 1 seed" pill on Maye d'force B with U, the two red "Out" pills, and no pill on the 8 other teams, in all 8 shots, with 0 overlaps and 0 covered text. The green pill measures 6.17 contrast in light (text 26,101,50 on 226,243,231) and 8.21 in dark (text 143,212,164 on 22,48,31). The run of the 9 committed pill tests of `race.test.tsx` and `sim-preview.test.tsx` prints "9 pass, 0 fail" (`pill-tests.txt`).

## AT-40: A Clinch line shows under its team

App: site
Then: each Clinch line of the file shows under its team, names the Goal, and names at most 2 other results before "and N more results".
Files: `evidence/AT-40/steps.txt`, `evidence/AT-40/board-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-40/clinch-lines.txt`, `evidence/AT-40/overlap.txt`, `evidence/AT-40/5f26bcb0-reading.txt`, `evidence/AT-40/5f26bcb0-board-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-40/5f26bcb0-overlap.txt`
Observation: On 5f26bcb0, `5f26bcb0-reading.txt` pairs each spot Clinch entry of `week-11/sim.json` with the board row of its team, read from the page. Lil Fridge (status in, 4 ways) has the row "Lil Fridge | 15-7 | 99% | Clinches a spot with a win, a median win, and a Bo Girds loss to Teez Nuts.". Maye d'force B with U (status in, 1 way, 4 other results in its first way) has "... | Clinches a spot with a win, a median win, a Bo Girds loss to Teez Nuts, a Nico Collinsizer median miss, and 2 more results.". Immaculate Concepcion (status out, 2 ways, 3 other results in its first way) has "... | Out with a loss, a median miss, a median win by The Blue Tent, a 💿 🐑 median win, and 1 more result.". Each line names 2 or fewer results of other teams before "and N more result(s)", "rows on the spot Goal with a Clinch line: 3", and all 8 runs read the same; the "Out with ..." copy for a spot is the copy of decision 06 (`.scratch/playoff-paths/decisions/06-grill-path-and-clinch-copy.md` line 47). The bye entries of the file show only under the Bye Goal (AT-28 "after"), and the overlap check found 0 overlaps and 0 covered text.

## AT-41: Another team opens in a sheet

App: site
Then: a sheet opens with the Finish list of Lil Fridge and a button "Make this Your team".
Files: `evidence/AT-41/steps.txt`, `evidence/AT-41/sheet-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-41/sheet-end-{390x660,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-41/sheet.txt`, `evidence/AT-41/overlap.txt`
Observation: A sheet opens with "Lil Fridge", "15-7 · 99% odds of a playoff spot", a "THIS WEEK" list of 4 Clinch ways, and the Finish list 6-0 (ends 21-7) to 0-6 (ends 15-13, "about 75%"). The button "Make this Your team" shows at the end of the sheet (the "sheet-end" shots at 390, 1080, and 1280, and in the "sheet" shot at 810); the overlap check found 0 overlaps and 0 covered text in the open sheet.

## AT-42: The page shows the file when the API is down

App: site
Then: the page shows the numbers of `week-11/sim.json`, and the tap shows a quiet note with no blank part.
Files: `evidence/AT-42/steps.txt`, `evidence/AT-42/loaded-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-42/after-tap-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-42/state.txt`, `evidence/AT-42/api-{390x660,810x980,1080x740,1280x800}-{light,dark}.json`, `evidence/AT-42/overlap.txt`
Observation: With the API process stopped, the page loads with the file numbers (card 48%, the same Finish list and board as AT-28 "before"), and the POST to `/clients/cpc/sim/what-if` ends with "Could not connect to the server.". After the tap on "Lose and miss the median" the card, Finish list, and board keep the file numbers, the root-for list changes to "If you lose and miss the median, you sit at 15%.", and the line "The What-if is not available now." shows under the Sim buttons with no empty block; the overlap check found 0 overlaps and 0 covered text.

## AT-43: NorCal fits a league with no median

App: site
Then: the week card shows 2 result tiles, no median score, a Finish list of 4-0 to 0-4, and no median rooting.
Files: `evidence/AT-43/steps.txt`, `evidence/AT-43/page-{390x660,810x980,1080x740,1280x800}-{light,dark}.png`, `evidence/AT-43/state.txt`, `evidence/AT-43/overlap.txt`
Observation: On the norcal build of week 10 ("After week 10 · 4 weeks left") with Your team Bo Girds (roster 7), the week card reads "Week 11 vs The Mean Machine" with one score row "Beat The Mean Machine 109 130", 2 tiles "Win 10%" and "Lose 1%", and a root-for list of 4 games and one "DOESN'T MATTER" game with no median row. The Finish list runs 4-0 (ends 9-5) to 0-4 (ends 5-9); the card opens on the Bye Goal ("8% BYE ODDS"), and the overlap check found 0 overlaps and 0 covered text.

## AT-44: A renamed team shows its live name

App: site
Then: every name slot and every blurb shows "Teez Nuts", and no page shows "Puka Deez...".
Files: `evidence/AT-44/network.txt`, `evidence/AT-44/overlap.txt`, `evidence/AT-44/race-390x660-dark.png`, `evidence/AT-44/race-390x660-light.png`, `evidence/AT-44/race-810x980-dark.png`, `evidence/AT-44/race-810x980-light.png`, `evidence/AT-44/race-1080x740-dark.png`, `evidence/AT-44/race-1080x740-light.png`, `evidence/AT-44/race-1280x800-dark.png`, `evidence/AT-44/race-1280x800-light.png`, `evidence/AT-44/readings.txt`, `evidence/AT-44/steps.txt`, `evidence/AT-44/week-390x660-dark.png`, `evidence/AT-44/week-390x660-light.png`, `evidence/AT-44/week-810x980-dark.png`, `evidence/AT-44/week-810x980-light.png`, `evidence/AT-44/week-1080x740-dark.png`, `evidence/AT-44/week-1080x740-light.png`, `evidence/AT-44/week-1280x800-dark.png`, `evidence/AT-44/week-1280x800-light.png`, `evidence/AT-44/week10-readings.txt`, `evidence/AT-44/week10-overlap.txt`, `evidence/AT-44/week10-network.txt`, `evidence/AT-44/week10-390x660-light.png`, `evidence/AT-44/week10-390x660-dark.png`, `evidence/AT-44/week10-810x980-light.png`, `evidence/AT-44/week10-810x980-dark.png`, `evidence/AT-44/week10-1080x740-light.png`, `evidence/AT-44/week10-1080x740-dark.png`, `evidence/AT-44/week10-1280x800-light.png`, `evidence/AT-44/week10-1280x800-dark.png`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: These files come from a new build of 5f26bcb0, the Spec head after fix E1, with the same changed client files. In all 8 contexts the browser sent GET /rosters and GET /users to Sleeper once on the week 11 page (both 200), and the cache gives roster 5 the name "Teez Nuts". The week 11 page shows "Teez Nuts" 8 times and The Race 5 times, with 0 "Puka Deez" on either page. The published week 11 files already hold "Teez Nuts", so those two pages show no swap of the name. The week 10 page, whose exported HTML gives roster 5 the published names ["Teez Nuts","Puka Deez...","London Cooking"], sent the same 2 Sleeper calls (both 200) and shows "Teez Nuts" 9 times and "Puka Deez" 0 times in every shot. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll on all 24 pages.

## AT-45: A changed avatar shows from Sleeper

App: site
Then: the avatar of roster 3 shows the new URL, and the local image stays until the new one loads.
Files: `evidence/AT-45/output.txt`
Observation: The command ran 7 tests of packages/league/site/live-names.test.tsx, with 7 pass and 0 fail. The test "shows a changed avatar from Sleeper only after it loads" stubs fetch with a new avatar_url for roster 3, checks that the local image keeps /2026/week-10/avatars/3.jpg before the preload fires load, and checks that it then shows the new URL.

## AT-46: A failed Sleeper call keeps the published names

App: site
Then: the page shows the published names and no error.
Files: `evidence/AT-46/network.txt`, `evidence/AT-46/overlap.txt`, `evidence/AT-46/readings.txt`, `evidence/AT-46/steps.txt`, `evidence/AT-46/week-10-390x660-dark.png`, `evidence/AT-46/week-10-390x660-light.png`, `evidence/AT-46/week-10-810x980-dark.png`, `evidence/AT-46/week-10-810x980-light.png`, `evidence/AT-46/week-10-1080x740-dark.png`, `evidence/AT-46/week-10-1080x740-light.png`, `evidence/AT-46/week-10-1280x800-dark.png`, `evidence/AT-46/week-10-1280x800-light.png`, `evidence/AT-46/week-11-390x660-dark.png`, `evidence/AT-46/week-11-390x660-light.png`, `evidence/AT-46/week-11-810x980-dark.png`, `evidence/AT-46/week-11-810x980-light.png`, `evidence/AT-46/week-11-1080x740-dark.png`, `evidence/AT-46/week-11-1080x740-light.png`, `evidence/AT-46/week-11-1280x800-dark.png`, `evidence/AT-46/week-11-1280x800-light.png`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: With both Sleeper calls aborted, the week 11 page shows "Teez Nuts" 8 times, and the week 10 page shows "Puka Deez" 9 times and "Teez Nuts" 0 times. Both pages show 0 hits for "error", "went wrong", and "try again" in all 8 contexts, and the shots show the full page with no error panel. The log shows both Sleeper requests on each page failed as "Blocked by Web Inspector". The only console errors are 2 lines "Failed to load resource: Could not connect to the server.", one for each call to the empty API port 8291, and no page error. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll on all 16 pages.

## AT-47: A second page reads the cached names

App: site
Then: the page shows "Teez Nuts" at once, and the network log shows no new Sleeper call.
Files: `evidence/AT-47/390x660-dark.png`, `evidence/AT-47/390x660-light.png`, `evidence/AT-47/810x980-dark.png`, `evidence/AT-47/810x980-light.png`, `evidence/AT-47/1080x740-dark.png`, `evidence/AT-47/1080x740-light.png`, `evidence/AT-47/1280x800-dark.png`, `evidence/AT-47/1280x800-light.png`, `evidence/AT-47/network.txt`, `evidence/AT-47/overlap.txt`, `evidence/AT-47/readings.txt`, `evidence/AT-47/steps.txt`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: The rankings page in the same tab shows "Teez Nuts" once at the load event and once 2.3 s later, with 0 "Puka Deez", in all 8 contexts. The log shows 0 new Sleeper requests on the rankings page, and the shots show "Teez Nuts" at rank 03. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll. The published rankings.json also holds "Teez Nuts" 12 times and "Puka Deez" once.

## AT-48: The midseason report keeps its names

App: site
Then: the report makes no Sleeper call, and its names match the published report.
Files: `evidence/AT-48/390x660-dark.png`, `evidence/AT-48/390x660-light.png`, `evidence/AT-48/810x980-dark.png`, `evidence/AT-48/810x980-light.png`, `evidence/AT-48/1080x740-dark.png`, `evidence/AT-48/1080x740-light.png`, `evidence/AT-48/1280x800-dark.png`, `evidence/AT-48/1280x800-light.png`, `evidence/AT-48/network.txt`, `evidence/AT-48/overlap.txt`, `evidence/AT-48/readings.txt`, `evidence/AT-48/steps.txt`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: The report page made 0 Sleeper requests in all 8 contexts. Its visible text is the same with the Sleeper calls open and with them blocked (15490 characters), and each team name has the same count in both. "Teez Nuts" and "Puka Deez..." each show 0 times as visible text, and the exported HTML holds each once. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll.

## AT-49: The Announcement introduces The Race once

App: site
Then: the first load shows "New: The Race", "The Race is on", and "Open The Race", and the second load shows no Announcement.
Files: `evidence/AT-49/first-390x660-dark.png`, `evidence/AT-49/first-390x660-light.png`, `evidence/AT-49/first-810x980-dark.png`, `evidence/AT-49/first-810x980-light.png`, `evidence/AT-49/first-1080x740-dark.png`, `evidence/AT-49/first-1080x740-light.png`, `evidence/AT-49/first-1280x800-dark.png`, `evidence/AT-49/first-1280x800-light.png`, `evidence/AT-49/overlap.txt`, `evidence/AT-49/readings.txt`, `evidence/AT-49/second-390x660-dark.png`, `evidence/AT-49/second-390x660-light.png`, `evidence/AT-49/second-810x980-dark.png`, `evidence/AT-49/second-810x980-light.png`, `evidence/AT-49/second-1080x740-dark.png`, `evidence/AT-49/second-1080x740-light.png`, `evidence/AT-49/second-1280x800-dark.png`, `evidence/AT-49/second-1280x800-light.png`, `evidence/AT-49/steps.txt`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: On the first load the sheet opens in all 8 contexts. Its modal layer holds "New: The Race", "The Race is on", and "Open The Race", and the shots show the eyebrow "NEW: THE RACE" in capitals. After "Not now" the key cpc.announcement.the-race-2026 reads "seen". On the reload the page shows none of the three texts and no modal layer, and the shots show the home page with no sheet. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll in both states.

## AT-50: The Sim tile links to The Race

App: site
Then: the tile after Standings reads "The Race" and links to `/sim/2026/`.
Files: `evidence/AT-50/390x660-dark.png`, `evidence/AT-50/390x660-light.png`, `evidence/AT-50/810x980-dark.png`, `evidence/AT-50/810x980-light.png`, `evidence/AT-50/1080x740-dark.png`, `evidence/AT-50/1080x740-light.png`, `evidence/AT-50/1280x800-dark.png`, `evidence/AT-50/1280x800-light.png`, `evidence/AT-50/overlap.txt`, `evidence/AT-50/readings.txt`, `evidence/AT-50/steps.txt`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: In all 8 contexts the section after #standings is #sim, with the heading "The Race" and one link, to /sim/2026/. Its text reads "The Race AFTER WEEK 11 PLAYOFF ODDS 48% Win 5 of the 6 left and you're in. Open The Race". The shots show the tile below Standings. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll.

## AT-51: The playoff weeks keep the bracket view

App: site
Then: the page shows the bracket view, with no Goal switch and no League board.
Files: `evidence/AT-51/390x660-dark.png`, `evidence/AT-51/390x660-light.png`, `evidence/AT-51/810x980-dark.png`, `evidence/AT-51/810x980-light.png`, `evidence/AT-51/1080x740-dark.png`, `evidence/AT-51/1080x740-light.png`, `evidence/AT-51/1280x800-dark.png`, `evidence/AT-51/1280x800-light.png`, `evidence/AT-51/overlap.txt`, `evidence/AT-51/readings.txt`, `evidence/AT-51/steps.txt`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: On the playoff fixture export, /sim/2026/ has 1 region "Bracket", 0 elements labelled "Goal", and 0 "League board" groups in all 8 contexts. The shots show Bo Girds "Out of the playoffs", Title odds, and the bracket of weeks 15 to 17, with no Goal switch and no League board. The week 11 export gives 0, 1, and 1 for the same three queries, for comparison. The overlap check found 0 overlaps, 0 covered texts, and no sideways scroll.

## AT-52: No Path names 4 or more teams in full

App: pipeline
Then: no Path names more than 3 teams.
Files: `evidence/AT-52/check.py`, `evidence/AT-52/output.txt`
Observation: The script counts the teams of each Path of the cpc week 11 file. 23 Paths name 1 team, 21 name 2 teams, and 2 name 3 teams. 0 Paths name more than 3 teams.

## AT-53: No Paths in the playoff weeks

App: pipeline
Then: no page of the file holds a Finish list, a Path, or a board.
Files: `evidence/AT-53/check.py`, `evidence/AT-53/output.txt`
Observation: The command is `cornerstone sim-fixtures` on the cpc 2026 week 10 inputs. It writes the 3 playoff fixture files to a scratch folder: week 14, week 15, and week 17. The seeds come from stored run 1. Each file has `board` []. Each page has `finishes` {} and `goals` {}, and each file has 0 Paths. The output gives the keys of page 1 of each file.

## AT-54: No live scores

App: site
Then: the site calls only the league rosters and the league users, and no matchup, projection, or player call.
Files: `evidence/AT-54/network.txt`, `evidence/AT-54/steps.txt`, `evidence/site-set-b/run.mjs`, `evidence/site-set-b/lib.mjs`, `evidence/site-set-b/serve.mjs`
Observation: Across the 8 contexts of AT-44 the site called 2 distinct Sleeper API URLs: /v1/league/1386167364424318976/rosters and /users. 0 Sleeper URLs name matchups, projections, players, stats, or state. The only other outside hosts are gc.zgo.at (count.js) and the empty local API port 127.0.0.1:8291 (eggs/board).

## AT-55: No push notifications

App: site
Then: the search finds none.
Files: `evidence/AT-55/output.txt`
Observation: apps/site/test/no-push.test.ts ran with 1 pass and 0 fail. The rg search of apps/site and packages/*/site finds 3 lines, and each one is in apps/site/test/no-push.test.ts itself. An rg search of the cpc export finds nothing (exit 1).
