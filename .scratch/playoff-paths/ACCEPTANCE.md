# The Race: acceptance tests

Spec: `.scratch/playoff-paths/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

**The site evidence set.** Screenshots in Playwright WebKit at 390x660 (iPhone 15), 810x980 and 1080x740 (iPad), and 1280x800, each in the light theme and the dark theme. Add the output of the overlap check: no text box overlaps another, and no fixed bar covers content.

**The data.** `cpc` 2026 week 11 has the median game, 3 weeks left, and 6 results per team. Your team there is Bo Girds, roster 6, at 11-11, and week 12 is Bo Girds vs Teez Nuts. The week 11 build fetched `users.json` before roster 5 changed its name from "Puka Deez..." to "Teez Nuts". `norcal` 2026 week 10 has no median game and 4 weeks left. `norcal` 2026 week 8 holds the tie of rosters 1 and 9 at 5-3 with 1010.86 Points For.

**The playoff fixture.** The playoff fixture of `season-sim`: the inputs of `cpc` 2026 week 10, with weeks 11 to 14 filled from stored run 1 of `week-10/sim.json`, built as week 14.

**The API.** Each API test runs on the local evidence API of the branch. No unmerged branch deploys to Fly. AT-23 runs on Fly after the merge.

## Tests

AT-1: The tiebreak orders tied teams the way Sleeper does
App: pipeline
Stories: 62
Given: `norcal` 2026 week 8, where rosters 1 and 9 tie at 5-3 with 1010.86 Points For.
When: the sim orders the standings of week 8.
Then: roster 9 sits above roster 1, as in the Sleeper `bracket.json` of week 8, because roster 9 has more Points Against.
Evidence: The command, its output, and the order of the 12 rosters beside the Sleeper seeds.

AT-2: The other stored brackets still match
App: pipeline
Stories: 62
Given: the stored `bracket.json` of `cpc` weeks 6 to 10 and `norcal` weeks 8 to 10.
When: the sim orders the standings of each week.
Then: the first 6 rosters of each week equal the Sleeper seeds of that week, in order.
Evidence: The command and a table of each week with both orders.

AT-3: The weekly build writes the Goals of each team
App: pipeline
Stories: 1, 4, 5
Given: `cpc` 2026 week 11.
When: the sim step of the weekly build runs.
Then: each of the 12 pages in `week-11/sim.json` holds the odds and the status of the spot Goal, the bye Goal, and seeds 1 to 6.
Evidence: The command, its output, and the Goal fields of 2 pages.

AT-4: The open Goal follows the 5% rule
App: pipeline
Stories: 2, 3
Given: `week-11/sim.json` of `cpc`.
When: the reader reads the open Goal of each page.
Then: each page opens on the best Goal with odds of 5% or more, in the order 1 seed, bye, spot, and Lil Fridge at 15-7 opens on the bye or the 1 seed.
Evidence: A table of the 12 teams with the odds of each Goal and the open Goal.

AT-5: The status follows the plain check on wins for each Goal
App: pipeline
Stories: 39, 40, 41
Given: `week-11/sim.json` of `cpc`.
When: the reader compares the status of each team for each Goal with a plain check on wins written by hand.
Then: each status is Clinched, In the hunt, or Out exactly as the hand check says, for the spot, the bye, and each seed.
Evidence: The hand check, its output, and the status fields.

AT-6: The Finish list sums to 100% with the right final records
App: pipeline
Stories: 10, 11, 12
Given: the page of Bo Girds, 11-11, in `week-11/sim.json` of `cpc`.
When: the reader reads its Finish list for a playoff spot.
Then: it lists 7 Finishes from 6-0 to 0-6, the chances add to 100% within 1 point, and 4-2 has the final record 15-13.
Evidence: The Finish list fields.

AT-7: A NorCal Finish list counts head-to-head games only
App: pipeline
Stories: 6, 13
Given: `norcal` 2026 week 10, which has no median game and 4 weeks left.
When: the sim step of the weekly build runs.
Then: each Finish list of `week-10/sim.json` runs 4-0 to 0-4, and no page holds a median result.
Evidence: The command output and the Finish list of 1 page.

AT-8: A Path reaches 90% or names 3 teams
App: pipeline
Stories: 16, 17, 18
Given: `week-11/sim.json` of `cpc`.
When: the reader reads every Path of every page.
Then: each Path names 1 to 3 teams, each condition is a final record at most, each Path has 400 runs or more, and each Path that names fewer than 3 teams has odds of 90% or more.
Evidence: A script over the file and its counts.

AT-9: No Path repeats
App: pipeline
Stories: 20
Given: `week-11/sim.json` of `cpc`.
When: the reader compares the Paths of each Finish.
Then: no two Paths of one Finish hold the same set of conditions.
Evidence: The script and its output.

AT-10: A sure or hopeless Finish has no Path
App: pipeline
Stories: 14, 15
Given: `week-11/sim.json` of `cpc`.
When: the reader reads each Finish with odds of 99.5% or more, and each Finish under 0.5%.
Then: none of those Finishes holds a Path.
Evidence: The script and a count of those Finishes.

AT-11: A Finish under 90% keeps its best chance
App: pipeline
Stories: 19
Given: `week-11/sim.json` of `cpc`.
When: the reader reads each Finish whose best Path stays under 90%.
Then: that Finish holds exactly 1 Path, marked as the best chance.
Evidence: The script and 2 examples.

AT-12: A Week plan has one row per week left
App: pipeline
Stories: 21, 22, 26
Given: the first Path of the 4-2 Finish of Bo Girds in `week-11/sim.json` of `cpc`.
When: the reader reads its Week plan.
Then: it holds 3 rows, weeks 12 to 13 to 14, each with a result, the Score to beat, and 1 or 2 games to root for, and a loss row holds no score against the opponent.
Evidence: The Week plan fields.

AT-13: "Try it" odds equal a What-if of the plan
App: pipeline
Stories: 25
Given: the Week plan of AT-12.
When: the reader runs the sim with the results of the plan set for Bo Girds.
Then: the odds of the Goal equal the "Try it" odds of the plan within 1 point.
Evidence: The command, its output, and both numbers.

AT-14: The Score to beat gives a 50% score and an 80% score
App: pipeline
Stories: 27, 28
Given: the page of Bo Girds in `week-11/sim.json` of `cpc`, week 12 vs Teez Nuts.
When: the reader reads its Score to beat.
Then: it holds 2 scores against Teez Nuts and 2 against the median, and each 80% score is higher than its 50% score.
Evidence: The Score to beat fields.

AT-15: The root-for list holds every other game for each result
App: pipeline
Stories: 31, 32, 34
Given: the page of Bo Girds in `week-11/sim.json` of `cpc`.
When: the reader reads the root-for list of week 12.
Then: each of the 4 results holds 5 rows, one per other head-to-head game, each with the odds after each side wins, and a row with a lift under 1 point is marked doesn't matter.
Evidence: The root-for fields of the 4 results.

AT-16: Median rooting names at most 2 teams
App: pipeline
Stories: 35
Given: the page of AT-15.
When: the reader reads the median rooting of week 12.
Then: it holds 1 or 2 other teams, each with the odds after that team misses the median.
Evidence: The median rooting fields.

AT-17: The Clinch lines agree with a brute-force check
App: pipeline
Stories: 42, 43
Given: `week-11/sim.json` of `cpc`.
When: the reader runs a hand-written check over every set of results of week 12.
Then: each Clinch line of the board names a set that makes its team Clinched or Out for its Goal, and the check finds no team with such a set and no line.
Evidence: The check, its output, and the board lines.

AT-18: The tiebreak gap shows only when close
App: pipeline
Stories: 36
Given: `week-11/sim.json` of `cpc`.
When: the reader reads the tiebreak gap of each page.
Then: a page holds a gap only when another team is within 1 win and 50 points of it at the edge of the Goal.
Evidence: The script and the pages with a gap.

AT-19: The sim file stays small
App: pipeline
Stories: none
Given: `cpc` 2026 week 11 and `cpc` 2026 week 10 rebuilt on the branch.
When: the reader measures `sim.json` with gzip.
Then: each file is 50 KB gzip or less.
Evidence: The command and the sizes.

AT-20: A What-if returns the Paths and the board odds
App: pipeline
Stories: 47, 50
Given: the local evidence API on the branch, with `cpc` 2026 week 11.
When: the reader calls the What-if route for Bo Girds with a win and a median win in week 12, twice.
Then: each response holds the Finish list, the Paths, the Week plans, the week card, and the board odds, and the two responses are equal.
Evidence: The two requests and responses, cut to the new fields, and a diff.

AT-21: A What-if holds no Clinch lines
App: pipeline
Stories: none
Given: the call of AT-20.
When: the reader reads the response.
Then: it holds no Clinch line.
Evidence: The response, cut to the board block.

AT-22: A What-if with no set result equals the file
App: pipeline
Stories: 49
Given: the local evidence API with `cpc` 2026 week 11.
When: the reader calls the What-if route for Bo Girds with no set result.
Then: the page block equals the page of Bo Girds in `week-11/sim.json`.
Evidence: The request, the response, and a diff with the file.

AT-23: A What-if on Fly stays under 2.5 s
App: pipeline
Stories: none
Given: the merged branch deployed to Fly, with `cpc` 2026 week 11.
When: the reader times 10 What-if calls for Bo Girds with one set result.
Then: the median time is 2.5 s or less.
Evidence: The 10 times. This test runs after the merge; the PR records it as the live seam.

AT-24: The race Topic is the first Suggestion in a regular week
App: pipeline
Stories: 59
Given: `cpc` 2026 week 11.
When: the API builds the Suggestions of Bo Girds.
Then: the first of the 3 Suggestions is the playoff race Topic.
Evidence: The request and the response.

AT-25: The race Topic ranks as usual after week 14
App: pipeline
Stories: 59
Given: a fixture of `cpc` 2026 that runs as week 15.
When: the API builds the Suggestions of Bo Girds.
Then: the playoff race Topic is not pinned first; its place follows the usual rank.
Evidence: The request, the response, and the rank.

AT-26: The race Answer adds the Finish list and the link
App: both
Stories: 60
Given: `cpc` 2026 week 11, the front door with Your team Bo Girds.
When: the reader taps the playoff race Suggestion.
Then: the Answer shows the odds, the top 3 Finishes for a playoff spot, no pill for a team In the hunt, and the link "Open The Race" to `/sim/2026/`.
Evidence: The Answer fields and the site evidence set, with the overlap check.

AT-27: The page is The Race
App: site
Stories: 57
Given: `cpc` 2026 week 11.
When: the reader opens `/sim/2026/` and the menu.
Then: the page title reads "The Race", the menu item reads "The Race", and the short label reads "Race".
Evidence: The site evidence set, with the overlap check.

AT-28: The Goal switch changes every part
App: site
Stories: 1, 5
Given: `cpc` 2026 week 11, Your team Bo Girds.
When: the reader taps Bye on the Goal switch.
Then: the odds of the card, the Finish list, the board bars, and the board order all show the odds of a bye.
Evidence: Screenshots before and after the tap, in the site evidence set, with the overlap check.

AT-29: The seed picker shows one seed
App: site
Stories: 4, 46
Given: the page of AT-28.
When: the reader taps Seed, then 3.
Then: the card, the Finish list, and the board show the odds of the 3 seed, and the board shows no Clinch line.
Evidence: The site evidence set, with the overlap check.

AT-30: The Your team card opens in place
App: site
Stories: 7, 8
Given: `cpc` 2026 week 11, Your team Bo Girds.
When: the reader taps the Your team card.
Then: the card opens in the page, with no sheet, and shows the Finish list, then the week card.
Evidence: The site evidence set, with the overlap check.

AT-31: A Finish shows its Paths with their copy
App: site
Stories: 11, 16, 17, 18
Given: the open card of AT-30.
When: the reader taps the 4-2 Finish.
Then: the Finish reads "4-2 · ends 15-13" with its chance, and each Path reads "If <team> ends <record> or worse…" and "Happens N% · you're in N%.".
Evidence: The site evidence set, with the overlap check.

AT-32: A Finish shows the copy of its case
App: site
Stories: 14, 15, 19
Given: the open card of AT-30.
When: the reader reads each Finish.
Then: a Finish at 99.5% or more reads "You're in whatever the others do.", a Finish under 0.5% reads "No way in at this record.", and a Finish under 90% shows "Best chance".
Evidence: The site evidence set, with the overlap check.

AT-33: A Path opens its Week plan
App: site
Stories: 21, 22, 23, 24
Given: the Paths of AT-31.
When: the reader taps the first Path.
Then: a sheet opens with the header "Your plan to 15-13 · you're in N%", 3 week rows with "Score N to win, N to be sure", and the order line when the order does not matter.
Evidence: The site evidence set, with the overlap check.

AT-34: "Try it" sets the plan as a What-if
App: site
Stories: 25, 47, 48
Given: the Week plan of AT-33, with the local evidence API.
When: the reader taps "Try it".
Then: the set line lists the 3 results of the plan with a Reset, and the odds of the card equal the "Try it" odds of the header within 1 point.
Evidence: The site evidence set, with the overlap check. Add the request and the response.

AT-35: The week card shows the Score to beat
App: site
Stories: 27, 28
Given: the open card of AT-30.
When: the reader reads the week card.
Then: it names Teez Nuts and shows "to win" and "to be sure" scores against Teez Nuts and against the median.
Evidence: The site evidence set, with the overlap check.

AT-36: A result tile sets a What-if
App: site
Stories: 29, 30, 47
Given: the open card of AT-30, with the local evidence API.
When: the reader taps "Lose and miss the median".
Then: the set line lists that result, and the Finish list and the board odds change to the numbers of the response.
Evidence: The site evidence set, with the overlap check. Add the request and the response.

AT-37: The root-for list shows every game with both results
App: site
Stories: 31, 32, 33, 34, 35
Given: the open card of AT-30.
When: the reader taps "Win and beat the median".
Then: the list shows 5 games, each with "<winner> beats <loser> → N%" and the other result below it, a gray "Doesn't matter" tag on a game under 1 point, and 1 or 2 median rows.
Evidence: The site evidence set, with the overlap check.

AT-38: The League board shows every team in odds order
App: site
Stories: 37, 38
Given: `cpc` 2026 week 11, Your team Bo Girds.
When: the reader reads the League board.
Then: it shows 12 rows in odds order for a playoff spot, Bo Girds has the accent bar and a "You" tag, and every other bar is ink.
Evidence: The site evidence set, with the overlap check.

AT-39: The board pills show Clinched and Out only
App: site
Stories: 39, 40, 41
Given: `week-11/sim.json` of `cpc`, with the status of each team from AT-5.
When: the reader reads the pills of the board on the spot Goal.
Then: a Clinched team shows a green pill naming its best Goal, an Out team shows a red pill, and a team In the hunt shows no pill.
Evidence: The site evidence set, with the overlap check. Add the measured contrast of each pill.

AT-40: A Clinch line shows under its team
App: site
Stories: 42, 44
Given: `week-11/sim.json` of `cpc`.
When: the reader reads the board on the spot Goal.
Then: each Clinch line of the file shows under its team, names the Goal, and names at most 2 other results before "and N more results".
Evidence: The site evidence set, with the overlap check.

AT-41: Another team opens in a sheet
App: site
Stories: 45, 9
Given: `cpc` 2026 week 11, Your team Bo Girds.
When: the reader taps Lil Fridge on the board.
Then: a sheet opens with the Finish list of Lil Fridge and a button "Make this Your team".
Evidence: The site evidence set, with the overlap check.

AT-42: The page shows the file when the API is down
App: site
Stories: 49
Given: `cpc` 2026 week 11, with the API stopped.
When: the reader opens The Race and taps a result tile.
Then: the page shows the numbers of `week-11/sim.json`, and the tap shows a quiet note with no blank part.
Evidence: The site evidence set, with the overlap check.

AT-43: NorCal fits a league with no median
App: site
Stories: 6, 13
Given: `norcal` 2026 week 10.
When: the reader opens `/sim/2026/` with Your team set.
Then: the week card shows 2 result tiles, no median score, a Finish list of 4-0 to 0-4, and no median rooting.
Evidence: The site evidence set, with the overlap check.

AT-44: A renamed team shows its live name
App: site
Stories: 51, 53, 54
Given: `cpc` 2026 week 11, where the published name of roster 5 is "Puka Deez..." and Sleeper says "Teez Nuts".
When: the reader opens the week page, then The Race.
Then: every name slot and every blurb shows "Teez Nuts", and no page shows "Puka Deez...".
Evidence: The site evidence set, with the overlap check. Add the network log of the 2 Sleeper calls.

AT-45: A changed avatar shows from Sleeper
App: site
Stories: 52
Given: a component test with a stubbed Sleeper answer that changes the `avatar_url` of roster 3.
When: the page renders and the stub answers.
Then: the avatar of roster 3 shows the new URL, and the local image stays until the new one loads.
Evidence: The test output.

AT-46: A failed Sleeper call keeps the published names
App: site
Stories: 55
Given: the site with both Sleeper calls blocked.
When: the reader opens the week page.
Then: the page shows the published names and no error.
Evidence: The site evidence set, with the overlap check. Add the network log.

AT-47: A second page reads the cached names
App: site
Stories: 54
Given: the site after AT-44.
When: the reader opens the rankings page within 5 minutes.
Then: the page shows "Teez Nuts" at once, and the network log shows no new Sleeper call.
Evidence: The site evidence set, with the overlap check. Add the network log.

AT-48: The midseason report keeps its names
App: site
Stories: 56
Given: `cpc` 2026, the midseason report.
When: the reader opens `/midseason/2026/` with the Sleeper calls open.
Then: the report makes no Sleeper call, and its names match the published report.
Evidence: The site evidence set, with the overlap check. Add the network log.

AT-49: The Announcement introduces The Race once
App: site
Stories: 58
Given: `cpc` 2026 week 11, a fresh browser with Your team set.
When: the reader opens the home page, then dismisses the Announcement, then loads the page again.
Then: the first load shows "New: The Race", "The Race is on", and "Open The Race", and the second load shows no Announcement.
Evidence: The site evidence set, with the overlap check.

AT-50: The Sim tile links to The Race
App: site
Stories: 61
Given: `cpc` 2026 week 11.
When: the reader opens the week page.
Then: the tile after Standings reads "The Race" and links to `/sim/2026/`.
Evidence: The site evidence set, with the overlap check.

AT-51: The playoff weeks keep the bracket view
App: site
Stories: 63
Given: the playoff fixture of `season-sim` (cpc week 10 filled through week 14 with stored run 1).
When: the reader opens `/sim/2026/`.
Then: the page shows the bracket view, with no Goal switch and no League board.
Evidence: The site evidence set, with the overlap check.

AT-52: No Path names 4 or more teams in full
App: pipeline
Stories: none
Given: `week-11/sim.json` of `cpc`.
When: the reader counts the teams of each Path.
Then: no Path names more than 3 teams.
Evidence: The script and its output.

AT-53: No Paths in the playoff weeks
App: pipeline
Stories: none
Given: the playoff fixture of AT-51.
When: the sim step of the weekly build runs.
Then: no page of the file holds a Finish list, a Path, or a board.
Evidence: The command output and the keys of 1 page.

AT-54: No live scores
App: site
Stories: none
Given: the network log of AT-44.
When: the reader lists the Sleeper calls of the site.
Then: the site calls only the league rosters and the league users, and no matchup, projection, or player call.
Evidence: The network log.

AT-55: No push notifications
App: site
Stories: none
Given: the branch.
When: the reader searches the site for a service worker, `Notification`, or `PushManager`.
Then: the search finds none.
Evidence: The search command and its output.

## Trace

Story 1: AT-3, AT-28
Story 2: AT-4
Story 3: AT-4
Story 4: AT-3, AT-29
Story 5: AT-3, AT-28
Story 6: AT-7, AT-43
Story 7: AT-30
Story 8: AT-30
Story 9: AT-41
Story 10: AT-6
Story 11: AT-6, AT-31
Story 12: AT-6
Story 13: AT-7, AT-43
Story 14: AT-10, AT-32
Story 15: AT-10, AT-32
Story 16: AT-8, AT-31
Story 17: AT-8, AT-31
Story 18: AT-8, AT-31
Story 19: AT-11, AT-32
Story 20: AT-9
Story 21: AT-12, AT-33
Story 22: AT-12, AT-33
Story 23: AT-33
Story 24: AT-33
Story 25: AT-13, AT-34
Story 26: AT-12
Story 27: AT-14, AT-35
Story 28: AT-14, AT-35
Story 29: AT-36
Story 30: AT-36
Story 31: AT-15, AT-37
Story 32: AT-15, AT-37
Story 33: AT-37
Story 34: AT-15, AT-37
Story 35: AT-16, AT-37
Story 36: AT-18
Story 37: AT-38
Story 38: AT-38
Story 39: AT-5, AT-39
Story 40: AT-5, AT-39
Story 41: AT-5, AT-39
Story 42: AT-17, AT-40
Story 43: AT-17
Story 44: AT-40
Story 45: AT-41
Story 46: AT-29
Story 47: AT-20, AT-34, AT-36
Story 48: AT-34
Story 49: AT-22, AT-42
Story 50: AT-20
Story 51: AT-44
Story 52: AT-45
Story 53: AT-44
Story 54: AT-44, AT-47
Story 55: AT-46
Story 56: AT-48
Story 57: AT-27
Story 58: AT-49
Story 59: AT-24, AT-25
Story 60: AT-26
Story 61: AT-50
Story 62: AT-1, AT-2
Story 63: AT-51
Out of scope "Paths in the playoff weeks": AT-51, AT-53
Out of scope "A Path of 4 or more teams in full": AT-52
Out of scope "Notifications": AT-55
Out of scope "Clinch lines after a What-if": AT-21
Out of scope "Live names in the midseason report": AT-48
Out of scope "Live scores, injuries, or projections": AT-54
Out of scope "The rank of a tied game": no test. Reason: no stored week has a tied game, so no agent builds it by mistake.
Out of scope "A bigger API machine": AT-23 runs on the existing machine. No other test.

## Revisions

None yet.
