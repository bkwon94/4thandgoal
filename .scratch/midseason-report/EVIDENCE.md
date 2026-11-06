# Midseason report: evidence

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests: `.scratch/midseason-report/ACCEPTANCE.md`.
Built from: `d93394b2`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.
Round time: 10 min for 15 site tests.

The pipeline tests ran at `233d3ef0`. The commits after it change only the site, the tests, and the spec text, so the pipeline output is the same. AT-47 ran again at `d93394b2`. The site tests ran at `d93394b2`, with the report data of a real `make midseason CLIENT=cpc WEEK=8` copied into `clients/cpc/published/2026/` for the round and removed after it. No real publish ran: AT-42 and AT-43 ran in a clone whose remote is a local bare repo.

The report applies decisions that Brian made during the build. They change what some Then lines expect: the spread rule is loose, and the opener is not a headline; the report shows the sim's playoff odds; a missed game reads nflverse Out or the Sleeper Out, IR, or PUP fallback; "manager now" reads the live Sleeper rosters; the odds of the sim show below the replay at every width; the champion card shows above the complete bracket.

## AT-1: The build writes the draft

App: pipeline
Then: The build folder of the season holds `midseason.json`, `sim.json`, and the review file. `clients/cpc/published/2026/` does not change.
Files: `evidence/AT-1/output.txt`
Observation: The build ran in 411 s with exit code 0. `clients/cpc/build/2026/` then held `midseason.json`, `sim.json`, `midseason-review.md`, and `midseason-facts.json`, and `git status` of `clients/cpc/published/2026/` showed no change; the build also wrote the untracked `clients/cpc/data/2026/draft/draft.json` and `picks.json`.

## AT-2: NorCal builds the report

App: pipeline
Then: Each week counts one game with no median game, Position top 10 has no DEF list, and the sim's bracket is fixed with no reseed.
Files: `evidence/AT-2/output.txt`
Observation: Each of the 12 NorCal teams has 8 games after 8 weeks, and the positions of Position top 10 are QB, RB, WR, and TE. The `parameters` of `sim.json` show `"median_game":false` and `"reseed":false`; the build ran in 491 s.

## AT-3: A rerun gives the same sim

App: pipeline
Then: The two `sim.json` files are the same, byte for byte.
Files: `evidence/AT-3/output.txt`
Observation: The second run used a second detached worktree at 233d3ef0, because both runs write the same CPC build folder. `diff` of the two `sim.json` files printed nothing with exit code 0, and both files have the SHA-256 `a16b2045…6327`.

## AT-4: Points for is the sum of the weekly scores

App: pipeline
Then: Maye d'force B with U has 900.65 points for, not 901.65. All You Need Is Love is 11-5.
Files: `evidence/AT-4/output.txt`
Observation: The state of the league shows Maye d'force B with U at 9-7 with `points_for` 900.65. All You Need Is Love is rank 1 at 11-5-0.

## AT-5: Arcs

App: pipeline
Then: Return of T Mac has Roller coaster and Turnaround, each with its numbers, and no third arc. Bo Girds has Snakebit and Collapse.
Files: `evidence/AT-5/output.txt`
Observation: Return of T Mac has two arcs: Roller coaster with a 5-game win streak and a 3-game loss streak, and Turnaround from 2-6 in weeks 1 to 4 to 7-1 in weeks 5 to 8. Bo Girds has two arcs: Collapse from 6-2 to 3-5, and Snakebit with schedule luck -2.18.

## AT-6: Schedule luck

App: pipeline
Then: All You Need Is Love has +2.73 with Smoke and mirrors. Bo Girds has -2.18 with Snakebit. Each team shows points against with its rank and its close-game record.
Files: `evidence/AT-6/output.txt`
Observation: All You Need Is Love has `schedule_luck` 2.73 and the arc Smoke and mirrors. Bo Girds has -2.18 and the arc Snakebit, and each of the 12 teams has `points_against`, `points_against_rank`, and close wins, losses, and ties.

## AT-7: Schedule swap

App: pipeline
Then: Each cell of the diagonal equals the team's standings record. Bo Girds with the schedule of Maye d'force B with U is 14-2.
Files: `evidence/AT-7/output.txt`
Observation: For each of the 12 teams, the swap cell with its own schedule shows the same record as the state of the league. The Bo Girds cell with the schedule of roster 9, Maye d'force B with U, is 14-2-0.

## AT-8: The All-play record is explained

App: site
Then: One plain sentence beside the All-play wins explains the All-play record.
Files: `evidence/AT-8/steps.json`, `evidence/AT-8/375-light.png`, `evidence/AT-8/375-dark.png`, `evidence/AT-8/768-light.png`, `evidence/AT-8/768-dark.png`, `evidence/AT-8/1280-light.png`, `evidence/AT-8/1280-dark.png`
Observation: Each shot shows one sentence directly above the Schedule luck table: "All-play wins count each week as a game against every other team, so they show the wins your scores earned with an average schedule." A second sentence follows it: "Schedule luck is the real wins minus the All-play wins." At 375 px the table scrolls sideways inside its card with the team column fixed, and the shot shows it at the start, with the CLOSE column cut at the card edge.

## AT-9: Injury toll

App: pipeline
Then: behold the lamb lost 9 starter games, the most in the league.
Files: `evidence/AT-9/output.txt`
Observation: behold the lamb is rank 1 with 9 games: Kyle Monangai 4, Emeka Egbuka 2, Saquon Barkley 2, and Quinshon Judkins 1. The next team, The Blue Tent, has 5 games, and its list holds Jadarian Price with 1 game, in line with the decision of Brian on a missed game.

## AT-10: Position top 10

App: pipeline
Then: The QB #1 is Josh Allen with 189.32. The DEF #3 is the Buccaneers with the tag "Free agent".
Files: `evidence/AT-10/output.txt`
Observation: QB rank 1 is Josh Allen with 189.32 points. DEF rank 3 is the Tampa Bay Buccaneers with 77.75 points, manager `null`, and the tag "Free agent"; the tag reads the live Sleeper rosters, per the decision of Brian on "Manager now".

## AT-11: The position switch

App: site
Then: The chapter shows the RB list only, with a switch for QB, RB, WR, TE, and DEF.
Files: `evidence/AT-11/steps.json`, `evidence/AT-11/375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/1280-dark.png`
Observation: Position top 10 shows one switch row of QB, RB, WR, TE, and DEF, with RB marked, and one list of 10 running backs, Jahmyr Gibbs 178.8 first. No other position list shows in the chapter.

## AT-12: Draft value in the auction

App: pipeline
Then: A steal is Matthew Golden, $2. A bust is A.J. Brown, $39, with the tag "just bad".
Files: `evidence/AT-12/output.txt`
Observation: The draft type is "auction". The first steal is Matthew Golden of Bo Girds at cost 2, and the first bust is A.J. Brown of Unsolicited Dak Picks at cost 39 with the tag "just bad".

## AT-13: Draft value in the snake

App: pipeline
Then: Each pick's cost is its pick number, and no pick shows a dollar amount.
Files: `evidence/AT-13/output.txt`
Observation: The NorCal draft type is "snake", and the cost of each of the 10 steals and busts equals its `pick_no` in `clients/norcal/data/2026/draft/picks.json`. The draft blurb has no `$` sign, with a count of 0.

## AT-14: The one that got away

App: pipeline
Then: Tyler Allgeier, drafted by Bo Girds for $2 and dropped before his rise, carries the "the one that got away" line.
Files: `evidence/AT-14/output.txt`
Observation: The steal Tyler Allgeier, team Bo Girds, cost 2, 73.6 points, has `line` "the one that got away". Jalen Coker and Stefon Diggs carry the same line, and the steal record has no field for the drop week.

## AT-15: Waiver hits, misses, and the outbid

App: pipeline
Then: The top hit is Ollie Gordon II, $40 to Unsolicited Dak Picks. The top miss is Joe Mixon, $40. The outbid list has The Blue Tent's $36 bid on Ollie Gordon II.
Files: `evidence/AT-15/output.txt`
Observation: The first hit is Ollie Gordon II, bid 40, to Unsolicited Dak Picks. The first miss is Joe Mixon, bid 40, and the outbid list has The Blue Tent with bid 36 on Ollie Gordon II.

## AT-16: Trade results

App: pipeline
Then: It lists 20 trades. The week 1 trade of Maye d'force B with U and NFC Least is a Robbery. The week 8 trade is Too soon.
Files: `evidence/AT-16/output.txt`
Observation: The trade list has a length of 20. The week 1 trade of NFC Least and Maye d'force B with U has result "Robbery", and the one week 8 trade has result "Too soon".

## AT-17: Trade cards

App: site
Then: The top 3 trades are full cards, each with the record of each team since the trade, such as "5-3 since". A player who was out in the first week after his trade has the tag "hurt on arrival".
Files: `evidence/AT-17/steps.json`, `evidence/AT-17/375-light.png`, `evidence/AT-17/375-dark.png`, `evidence/AT-17/768-light.png`, `evidence/AT-17/768-dark.png`, `evidence/AT-17/1280-light.png`, `evidence/AT-17/1280-dark.png`
Observation: The chapter shows 3 full cards (week 1 Robbery, week 3 Robbery, week 4 Clear win), each with a record per team, such as "3-13 since" and "9-7 since", then compact rows and a "Show all 17" button. The tag "HURT ON ARRIVAL" shows only in the compact rows, after Breece Hall, Brian Robinson Jr., DJ Moore, Jacory Croskey-Merritt, David Montgomery, and Lamar Jackson; no player in the 3 full cards has the tag.

## AT-18: Lineup choices

App: pipeline
Then: London Cooking in week 2 lost by 1.67 with 27.54 points on the bench, and its best lineup would have won.
Files: `evidence/AT-18/output.txt`
Observation: London Cooking in week 2 scored 112.14, lost by 1.67 to Unsolicited Dak Picks, and had `bench_points` 27.54. Its `best` lineup is 139.68, against the opponent score of 113.81 that the jq filter adds up from score plus margin.

## AT-19: Record book

App: pipeline
Then: The high is 158.96 by Maye d'force B with U in week 5. The closest game is 0.4, All You Need Is Love over The Blue Tent in week 3.
Files: `evidence/AT-19/output.txt`
Observation: The high is 158.96 by Maye d'force B with U in week 5. The closest game is week 3, All You Need Is Love 114.33 over The Blue Tent 113.93, margin 0.4.

## AT-20: Awards

App: pipeline
Then: The MVP is Jahmyr Gibbs. Most active is Bo Girds with 42 moves. Set and forget is London Cooking with 3 moves. All seven awards have a winner and a fact.
Files: `evidence/AT-20/output.txt`
Observation: The award list has 7 entries, each with a team and a `fact` sentence. MVP is Jahmyr Gibbs, Most active is Bo Girds with value 42, and Set and forget is London Cooking with value 3.

## AT-21: Each game shows once

App: site
Then: Heartbreak of the year and Beatdown of the year each show once, inside the record book, and not again among the awards.
Files: `evidence/AT-21/steps.json`, `evidence/AT-21/375-light.png`, `evidence/AT-21/375-dark.png`, `evidence/AT-21/768-light.png`, `evidence/AT-21/768-dark.png`, `evidence/AT-21/1280-light.png`, `evidence/AT-21/1280-dark.png`
Observation: "BEATDOWN OF THE YEAR" shows as a tag on Biggest margin (92.14) and "HEARTBREAK OF THE YEAR" as a tag on Closest game (0.4) in the record book. The awards list below holds 5 cards: MVP, Streaming king, Bench crime of the year, Most active, and Set and forget, with no Heartbreak or Beatdown card.

## AT-22: The spread rule

App: pipeline
Then: Each team has 1 to 3 headlines. Bo Girds keeps its 2 arcs and Most active, and both swap callouts name another team.
Files: `evidence/AT-22/output.txt`
Observation: Each of the 12 teams has 1 to 3 headlines, and Bo Girds has `arc.collapse`, `arc.snakebit`, and `award.most-active`. The swap callouts name Teehee and behold the lamb, and the fact sheet says Bo Girds is not their headline; the spread rule is loose, per the decision of Brian.

## AT-23: Players to watch

App: pipeline
Then: Due to fall has Jaxon Smith-Njigba. Grab him now has Kyler Murray. Each list has 3 players.
Files: `evidence/AT-23/output.txt`
Observation: Due to fall lists Jaxon Smith-Njigba, Caleb Douglas, and Mike Gesicki. Grab him now lists Kyler Murray, J.J. McCarthy, and Justin Herbert, and Due to rise also has 3 players.

## AT-24: Look ahead

App: pipeline
Then: Maye d'force B with U has the softest schedule, at a .44 win rate of its opponents. behold the lamb has the hardest, at .56.
Files: `evidence/AT-24/output.txt`
Observation: `softest` is roster 9 and `hardest` is roster 10. Maye d'force B with U has `opponents_rate` 0.44, and behold the lamb has 0.56.

## AT-25: The opener is the title race

App: pipeline
Then: The opener is the title race. It names the title odds of the leaders and of All You Need Is Love, the record leader at 11-5.
Files: `evidence/AT-25/output.txt`
Observation: The opener has the title "The title race" and names London Cooking 16.8%, Bo Girds 16.3%, Maye d'force B with U 14.5%, and All You Need Is Love 11-5 with 9.7%, 6th. The odds are the sim odds, and no headline has the chapter "opener", per the decisions of Brian.

## AT-26: Three acts

App: site
Then: The report has three acts in this order: How we got here, The moves, What comes next. Each act opens with a dark title page.
Files: `evidence/AT-26/steps.json`, `evidence/AT-26/375-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/1280-dark.png`
Observation: Each full-page shot shows, from top to end, the title pages "Act I How we got here", "Act II The moves", and "Act III What comes next". Each title page has a near-black surface in the light theme and in the dark theme. Each test has one full-page shot per width and theme that holds all three title pages, not one shot per title page.

## AT-27: The chapter rail

App: site
Then: The rail stays at the top, and the page moves to Act III.
Files: `evidence/AT-27/steps.json`, `evidence/AT-27/before-375-light.png`, `evidence/AT-27/before-375-dark.png`, `evidence/AT-27/before-768-light.png`, `evidence/AT-27/before-768-dark.png`, `evidence/AT-27/before-1280-light.png`, `evidence/AT-27/before-1280-dark.png`, `evidence/AT-27/after-375-light.png`, `evidence/AT-27/after-375-dark.png`, `evidence/AT-27/after-768-light.png`, `evidence/AT-27/after-768-dark.png`, `evidence/AT-27/after-1280-light.png`, `evidence/AT-27/after-1280-dark.png`, `evidence/AT-27/url-375-light.txt`, `evidence/AT-27/url-375-dark.txt`, `evidence/AT-27/url-768-light.txt`, `evidence/AT-27/url-768-dark.txt`, `evidence/AT-27/url-1280-light.txt`, `evidence/AT-27/url-1280-dark.txt`
Observation: In each full-page shot the top band and the rail sit at the scroll position: mid Act II, at the trade report card, before the tap, and directly above the "Act III What comes next" title page after it, with "WHAT COMES NEXT" in the accent color. Each url file holds `/midseason/2026/#what-comes-next`.

## AT-28: The look at each width

App: site
Then: The report renders in the redesign look with no clipped text and no sideways scroll.
Files: `evidence/AT-28/steps.json`, `evidence/AT-28/start-375-light.png`, `evidence/AT-28/start-375-dark.png`, `evidence/AT-28/start-768-light.png`, `evidence/AT-28/start-768-dark.png`, `evidence/AT-28/start-1280-light.png`, `evidence/AT-28/start-1280-dark.png`, `evidence/AT-28/end-375-light.png`, `evidence/AT-28/end-375-dark.png`, `evidence/AT-28/end-768-light.png`, `evidence/AT-28/end-768-dark.png`, `evidence/AT-28/end-1280-light.png`, `evidence/AT-28/end-1280-dark.png`
Observation: Each shot is exactly the viewport width (375, 768, 1280 px), so the page has no sideways scroll, and it shows the redesign top band, cards, mono labels, and dark hero surfaces. At 375 px the start shots show The state of the league and Schedule luck at the left of their tables, with STREAK and CLOSE cut at the card edge. The end shots, after a scroll to the PLAYOFF and CLOSE headers, show both tables at their right end with the team column, place number included, still in place. In the end shots the fixed team column covers the left part of the next column, for example PF "850.17" shows as "0.17".

## AT-29: The sim is the finale

App: site
Then: The sim is the last chapter of the report.
Files: `evidence/AT-29/steps.json`, `evidence/AT-29/375-light.png`, `evidence/AT-29/375-dark.png`, `evidence/AT-29/768-light.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/1280-light.png`, `evidence/AT-29/1280-dark.png`
Observation: The end of each page shows Players to watch, then "Sim the rest of the season" with the "Sim the season" button, the replay stage, and the table "The odds of all 10,000 runs". Nothing follows the odds table but the page end.

## AT-30: The replay: the regular season and the split

App: site
Then: Each week of 9 to 14 shows a lower third with the scores, and the standings reorder. After week 14 a red PLAYOFFS wipe plays, then the final standings with the cut under seed 6 and BYE on seeds 1 and 2.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/replay-375-dark.webm`, `evidence/AT-30/week-375-dark.png`, `evidence/AT-30/week-1280-dark.png`, `evidence/AT-30/wipe-375-dark.png`, `evidence/AT-30/wipe-1280-dark.png`, `evidence/AT-30/final-375-dark.png`, `evidence/AT-30/final-1280-dark.png`
Observation: The week shots show "WEEK 10 FINAL" with the median and a line of team scores under the standings, with up and down arrows beside the teams that moved. The wipe shots show a red band with "PLAYOFFS" over the standings at week 14, and the final shots show a red line under seed 6 and BYE tags on seeds 1 and 2. The shots and the video come from a Playwright script, not the runner, because a beat of 1 to 2 s is shorter than the runner's shot (see `steps.txt`).

## AT-31: The replay: the bracket

App: site
Then: The bracket draws in. Each winner slides along its line to its next slot. In the semifinal, seed 1 meets the lowest seed left.
Files: `evidence/AT-31/steps.txt`, `evidence/AT-31/bracket-375-dark.webm`, `evidence/AT-31/semifinal-375-dark.png`, `evidence/AT-31/semifinal-1280-dark.png`
Observation: At 375 px the Semifinal pairs seed 1 with seed 6 and seed 2 with seed 4, after Round 1 winners of seeds 6 and 4. At 1280 px it pairs seed 1 with seed 6 and seed 2 with seed 5, after Round 1 winners of seeds 6 and 5. In the video each round draws in under the last one, a red marker moves down the line from a winner, and the seed badges of the next round move into their slots. The run ends with the champion card above the bracket.

## AT-32: The champion card

App: site
Then: A full champion card shows the team and "Wins the title in N% of all 10,000 runs", where N is the team's title odds in `sim.json`.
Files: `evidence/AT-32/steps.json`, `evidence/AT-32/375-light.png`, `evidence/AT-32/375-dark.png`, `evidence/AT-32/768-light.png`, `evidence/AT-32/768-dark.png`, `evidence/AT-32/1280-light.png`, `evidence/AT-32/1280-dark.png`
Observation: The card sits at the top of the replay stage, above the complete bracket, with the team and the line "Wins the title in N% of all 10,000 runs": Lil Fridge 14.4 (375 light and 1280 dark), The Blue Tent 13.4 (375 dark), and London Cooking 16.8 (1280 light). Each N matches `teams.<id>.title` in `sim.json` (14.4, 13.4, 16.8). At 768 px the fixed dock covers the team name and most of the line: the avatar shows Bo Girds with "16.3%" in part (light) and Lil Fridge with "14.4%" in part (dark); at 375 px the dock covers the lower part of the avatar and the top of the name, but not the line.

## AT-33: The odds of all runs

App: site
Then: The playoff, bye, and title odds of all 10,000 runs show below the replay at every width.
Files: `evidence/AT-33/steps.json`, `evidence/AT-33/375-light.png`, `evidence/AT-33/375-dark.png`, `evidence/AT-33/768-light.png`, `evidence/AT-33/768-dark.png`, `evidence/AT-33/1280-light.png`, `evidence/AT-33/1280-dark.png`
Observation: At each width the table "The odds of all 10,000 runs" sits below the replay stage, with the columns PLAYOFF, BYE, TITLE, and SEED for all 12 teams. Before a press the SEED column shows a dash for each team.

## AT-34: Skip to the end

App: site
Then: The final state shows at once: the bracket complete and the champion card.
Files: `evidence/AT-34/steps.json`, `evidence/AT-34/before-375-dark.png`, `evidence/AT-34/before-1280-dark.png`, `evidence/AT-34/after-375-dark.png`, `evidence/AT-34/after-1280-dark.png`
Observation: The before shots show week 11 of the run with the "Skip to the end" button. The after shots show no "Skip to the end" button, and the stage shows the champion card above the complete bracket: Round 1, Semifinal, and Final, each game with both scores. At 375 px The Blue Tent wins; at 1280 px London Cooking wins, with the three rounds side by side.

## AT-35: A fresh run

App: site
Then: A new run starts at week 9, with no part of the old run left on the screen.
Files: `evidence/AT-35/steps.txt`, `evidence/AT-35/fresh-run-375-dark.webm`
Observation: The video shows weeks 9, 10, and 11 of a run, then the second press at week 11. The strip goes back to week 9, and the standings change to a new order, Lil Fridge first. No lower third or standings row of the old run shows after the press.

## AT-36: Reduced motion

App: site
Then: Each beat changes with a fade or at once, with no movement, and the same facts show.
Files: `evidence/AT-36/steps.txt`, `evidence/AT-36/reduced-motion-375-dark.webm`
Observation: With reduced motion on, the PLAYOFFS band shows at full width and fades out, with no wipe from the side. The weeks, the final standings with BYE tags, the bracket rounds, and the champion card above the bracket all show. Each new bracket round and the champion card fade in. In each bracket result the scores count up from a low number to the final score over about 1 s.

## AT-37: The sim file

App: pipeline
Then: It holds 200 sim runs, the odds of 10,000 runs per team, and the seed odds. Its gzip size is 50 KB or less.
Files: `evidence/AT-37/output.txt`
Observation: `sim.json` has `runs` 10000 and a `sample` of 200 runs. Each of the 12 teams has playoff, bye, final, title, and seed odds, and the file is 161,014 bytes, or 46,463 bytes with gzip.

## AT-38: Sim parity

App: pipeline
Then: For each team of each client, the sim's playoff odds are within 2 points of the published week 8 odds.
Files: `evidence/AT-38/output.txt`
Observation: The test `test_the_playoff_odds_of_the_sim_are_within_2_points_of_the_published_week_8_odds` ran for both clients, and pytest reported 2 passed. The largest gap is 2 points for CPC, roster 6, and 1 point for NorCal, roster 3.

## AT-39: The review file

App: pipeline
Then: Each blurb shows its prose block, the facts it cites, and the verifier result.
Files: `evidence/AT-39/output.txt`
Observation: The first 40 lines hold the full `opener` entry: a "Prose block" line, a numbered blurb with fact ids, a "Cited facts" list, and "Verifier: passed on attempt 1.". The `opener.roast` entry follows in the same shape, and its verifier line is line 42, just past the 40-line cut.

## AT-40: A roast cites a fact

App: pipeline
Then: Each roast blurb cites at least one fact, and the verifier passes it.
Files: `evidence/AT-40/output.txt`
Observation: The file holds the review entries of `opener.roast`, `state.roast`, and `arcs.roast`. Each of the 13 roast blurbs cites 1 to 6 facts, and each verifier line says "passed", 12 on attempt 1 and `waivers.roast` on attempt 2.

## AT-41: The roast setting off

App: pipeline
Then: The draft has no roast lines.
Files: `evidence/AT-41/output.txt`
Observation: In a second detached worktree, `client.toml` got `roast = "off"`; the build ran in 244 s, and the file was put back. The review file says "Roast: off" and has no `.roast` section, and each `roast` in `midseason.json` is `null`; 4 main blurbs still each hold one sentence marked `[reaction]`.

## AT-42: An edit that adds an uncited number

App: pipeline
Then: The publish refuses and names the blurb. `clients/cpc/published/2026/` does not change.
Files: `evidence/AT-42/output.txt`
Observation: The publish ran in a clone whose `origin` is a local bare repo, so nothing reached GitHub. It printed "The blurb opener fails the verifier: [3] number 999 is not in the cited facts OP.record" and "Nothing is published", with exit code 2; `git status` of `clients/cpc/` shows only untracked build files, and HEAD stays at 233d3ef0.

## AT-43: The publish

App: pipeline
Then: The commit holds `midseason.json` and `sim.json` in `clients/cpc/published/2026/` and no file outside the client's season folders.
Files: `evidence/AT-43/output.txt`
Observation: The publish ran in a clone whose `origin` is a local bare repo, so nothing reached GitHub. It printed "Committed and pushed", and `git show --stat` of commit eb6f8a22 "Midseason report week 8" lists only `clients/cpc/published/2026/midseason.json` and `clients/cpc/published/2026/sim.json`.

## AT-44: The takeover

App: site
Then: The top of the home page shows the takeover: the opener and a link to the report.
Files: `evidence/AT-44/steps.json`, `evidence/AT-44/375-light.png`, `evidence/AT-44/375-dark.png`, `evidence/AT-44/768-light.png`, `evidence/AT-44/768-dark.png`, `evidence/AT-44/1280-light.png`, `evidence/AT-44/1280-dark.png`
Observation: Under the league title, the top of the home page shows a dark hero "2026 Midseason Report // Week 8, The title race" with the title odds of London Cooking 16.8%, Bo Girds 16.3%, Maye d'force B with U 14.5%, and the record leader All You Need Is Love 9.7%. The hero ends in the button "Read the Midseason Report", and Power Rankings follows it. The hero holds the opener title and odds, but not the opener prose.

## AT-45: The report tile

App: site
Then: The home page shows its usual top and the report tile with one big fact and a link to the report.
Files: `evidence/AT-45/steps.json`, `evidence/AT-45/steps.txt`, `evidence/AT-45/375-light.png`, `evidence/AT-45/375-dark.png`, `evidence/AT-45/768-light.png`, `evidence/AT-45/768-dark.png`, `evidence/AT-45/1280-light.png`, `evidence/AT-45/1280-dark.png`
Observation: No week 10 data exists, so these shots come from a copy of the published `midseason.json` with `takeover_end_week` set to 7, not 9, and week 8 as the latest week. The home page shows its usual top, the week 8 Matchup of the week hero and "Week 8 in four numbers", then the tile "2026 Midseason Report, Title favorite, 16.8%, London Cooking" with an arrow, above Power Rankings.

## AT-46: The menu

App: site
Then: The dock and the menu have the same items as before the report.
Files: `evidence/AT-46/steps.json`, `evidence/AT-46/375-light.png`, `evidence/AT-46/375-dark.png`, `evidence/AT-46/768-light.png`, `evidence/AT-46/768-dark.png`, `evidence/AT-46/1280-light.png`, `evidence/AT-46/1280-dark.png`
Observation: At 375 and 768 px the dock holds Home, Week 8, Rankings, Managers, and Trade. At 1280 px the pill bar holds Home, Week 8, Power Rankings, Managers, and Trade Analyzer. The dock is the same as in `.scratch/site-redesign/evidence/AT-3/cpc/375-light.png`, from before the report. The site has no menu to open, so the shots show the dock and the pill bar as they are.

## AT-47: The layers

App: pipeline
Then: `test_layers.py` passes, and `midseason` and `sim` import only `league` and `facts`.
Files: `evidence/AT-47/output.txt`
Observation: At `d93394b2`, `test_layers.py`, `test_client.py`, and `test_golden.py` give 40 passed, and the `test_imports.py` of `sim` and of `midseason` give 4 and 21 passed. An earlier `make check` at `233d3ef0` had 5 failures in `test_client.py`, `test_cli.py`, and `test_golden.py`; commits `5769cfcd` and `1301edcc` changed those tests.

## AT-48: The config check

App: pipeline
Then: The check fails and names the missing package `sim`.
Files: `evidence/AT-48/output.txt`
Observation: On a copy of `client.toml` in the scratchpad, with `sim` removed from the package list, `cornerstone check-client` exits 2. It prints "The midseason package needs the sim package. Add sim to the package list."; the real file never changed.

## AT-49: No weekly rebuild

App: pipeline
Then: `midseason.json` and `sim.json` in `published/` do not change.
Files: `evidence/AT-49/output.txt`
Observation: The build ran in a second detached worktree, with the `midseason.json` and `sim.json` of the AT-43 publish put in `clients/cpc/published/2026/` first. Both files have the same SHA-256 before and after the 770 s build; the build changed only week 8 files under `build/` and `data/`.

## AT-50: No picks in the replay

App: site
Then: The sim chapter has no control to pick the winner of a game.
Files: `evidence/AT-50/steps.json`, `evidence/AT-50/375-light.png`, `evidence/AT-50/375-dark.png`, `evidence/AT-50/768-light.png`, `evidence/AT-50/768-dark.png`, `evidence/AT-50/1280-light.png`, `evidence/AT-50/1280-dark.png`
Observation: The sim chapter shows one control, the "Sim the season" button, then the stage with the standings after week 8 and the odds table. It shows no control per game or per team. The AT-30, AT-31, and AT-34 shots of a running replay show only "Sim the season" and "Skip to the end".

## AT-51: The weekly odds do not change

App: pipeline
Then: `clients/cpc/published/2026/rankings.json` does not change.
Files: `evidence/AT-51/output.txt`
Observation: `git status` of `rankings.json` is empty before and after `make midseason CLIENT=cpc WEEK=8`. Its MD5 is `4a80c07457cf7adc6a184d9404dbf4f1` both times.
