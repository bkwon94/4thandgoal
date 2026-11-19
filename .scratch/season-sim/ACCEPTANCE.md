# Season sim: acceptance tests

Spec: `.scratch/season-sim/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

**The site evidence set.** Screenshots in Playwright WebKit at 390x660 (iPhone 15), 810x980 and 1080x740 (iPad), and 1280x800, each in the light theme and the dark theme. Add the output of the overlap check: no text box overlaps another, and no fixed bar covers content (decision 04).

**The data.** `cpc` 2026 week 10 has the median game. Your team there is Bo Girds, 6th at 11-9, and week 11 is Bo Girds vs Maye d'force B with U. `norcal` 2026 week 10 has no median game. Your team there is Bo Girds, 7th at 5-5, and week 11 is The Mean Machine vs Bo Girds.

**The playoff fixture.** No real playoff week exists before the merge. The fixture takes the inputs of `cpc` 2026 week 10 and fills weeks 11 to 14 with the scores of stored run 1 of `week-10/sim.json`. The build then runs as week 14, so the bracket of week 15 is set. **The round-two fixture** fills weeks 11 to 15 the same way and runs as week 15, so round 1 is played and the top seed has its semifinal. In `cpc`, the top seed has a bye in week 15, so only this fixture gives it a game with a set opponent. **The season-end fixture** fills weeks 11 to 17 the same way. The evidence names the seeds and the champion of each fixture.

## Tests

AT-1: The weekly build writes a sim file in the week folder
App: pipeline
Stories: 24, 55
Given: `cpc` 2026 week 10.
When: the sim step of the weekly build runs.
Then: `clients/cpc/published/2026/week-10/sim.json` exists with `runs` 10000, 12 `teams`, 200 runs in `sample`, and 12 entries in `pages`.
Evidence: the command, its output, and the top-level keys and counts of the file.

AT-2: The rankings odds come from the sim
App: pipeline
Stories: 54, 57
Given: `cpc` 2026 week 10, after AT-1.
When: the rankings step of the weekly build runs.
Then: the playoff odds of each of the 12 teams in `rankings.json` for week 10 equal the playoff odds of that team in `week-10/sim.json`.
Evidence: the command output and a table of the 12 teams with both numbers.

AT-3: The facts quote the odds of the sim
App: pipeline
Stories: 55
Given: `cpc` 2026 week 10, after AT-1.
When: the facts step of the weekly build runs.
Then: each playoff odds number in the facts of week 10 equals the number of that team in `week-10/sim.json`.
Evidence: the command output and each odds fact with the number of the file beside it.

AT-4: The odds of past weeks stay
App: pipeline
Stories: 56
Given: the branch after AT-2.
When: the reader runs `git diff main -- clients/cpc/published/2026/rankings.json` and reads weeks 1 to 9.
Then: no odds value of weeks 1 to 9 changes.
Evidence: the diff, filtered to the odds of weeks 1 to 9.

AT-5: The old odds engine is gone
App: pipeline
Stories: 57
Given: the branch.
When: the reader searches the repo for `rankings.odds` and `odds.py`.
Then: `packages/rankings/python/src/rankings/odds.py` and its parity test do not exist, and no module imports `rankings.odds`.
Evidence: the search command and its output.

AT-6: The ladder names the wins Your team needs
App: pipeline
Stories: 3, 4, 5
Given: `week-10/sim.json` of `cpc`, the page of Bo Girds.
When: the reader reads the ladder of the page.
Then: the ladder lists each count of more wins with its playoff odds and its chance, and the sentence names the smallest count with odds of 90 % or more.
Evidence: the ladder and the sentence from the file.

AT-7: Week 11 has four results with the median game
App: pipeline
Stories: 7, 8, 9
Given: `week-10/sim.json` of `cpc`, the page of Bo Girds.
When: the reader reads the block of week 11.
Then: the opponent is Maye d'force B with U, and four results each give odds after, a chance, and wins added of 2, 1, 1, and 0.
Evidence: the block of week 11 from the file.

AT-8: Week 11 has two results with no median game
App: pipeline
Stories: 10
Given: `week-10/sim.json` of `norcal`, the page of Bo Girds.
When: the reader reads the block of week 11.
Then: the opponent is The Mean Machine, and two results give odds after a win and after a loss.
Evidence: the block of week 11 from the file.

AT-9: The root-for rows follow the rules of the spec
App: pipeline
Stories: 11, 12, 13
Given: `week-10/sim.json` of `cpc`, the page of Bo Girds, week 11.
When: the reader reads the odds after a loss and the root-for rows.
Then: there are at most 3 rows, each lifts the odds after a loss by 1 point or more, each number is whole, the rows rank by the lift, and each reason is one of the five reasons of the spec.
Evidence: the block, and the lift of each row worked out from its two numbers.

AT-10: A small sample shows "about"
App: pipeline
Stories: 15
Given: `week-10/sim.json` of `cpc`.
When: the reader reads each result of each page.
Then: each result whose chance times `effective_runs` is under 400 has the "about" flag, and each other result does not.
Evidence: a script output that checks each result of the 12 pages, with the count of each case.

AT-11: A set result agrees with an exact reference
App: pipeline
Stories: 16, 17
Given: the inputs of `cpc` 2026 week 10.
When: the sim runs with Bo Girds set to lose week 11 and miss the median.
Then: the playoff odds of Bo Girds are within 1.5 points of an exact rejection reference on the same inputs.
Evidence: the test command, both numbers, and the gap.

AT-12: The same set results give the same numbers
App: pipeline
Stories: 21
Given: the inputs of `cpc` 2026 week 10.
When: the sim runs twice with Bo Girds set to win week 11 and beat the median.
Then: the two page blocks are equal byte for byte.
Evidence: the test command and the hash of each output.

AT-13: An injury does not change the level of a team
App: pipeline
Stories: none
Given: the inputs of `cpc` 2026 week 10.
When: the reader reads the level of each team in `week-10/sim.json`.
Then: the level mean of each team equals its season average shrunk toward the league average with 5 weeks of weight, with no injury term.
Evidence: a script output that works out the 12 level means from the scores and compares them with the file.

AT-14: The What-if answers with no passphrase
App: api
Stories: 16, 22
Given: the API of the branch with the published `cpc` week 10.
When: a client posts Bo Girds and one set result, a win above the median in week 11, with no passphrase.
Then: the answer is 200 with `schema_version`, `season`, `week`, `runs`, `effective_runs`, `you`, `set`, `teams`, `sample`, and `page`.
Evidence: the request, the status, and the keys of the answer.

AT-15: A What-if with no set result equals the file
App: api
Stories: 24
Given: the API of the branch with the published `cpc` week 10.
When: a client posts Bo Girds with no set result.
Then: the `page` of the answer equals the page of Bo Girds in `week-10/sim.json`.
Evidence: the request and a diff of the two blocks.

AT-16: The What-if never calls Sleeper
App: api
Stories: none
Given: the API of the branch, with each request to the Sleeper host blocked.
When: a client posts Bo Girds and one set result.
Then: the answer is 200, and the log shows no request to Sleeper.
Evidence: the test command, the status, and the log.

AT-17: The What-if has its own rate limit
App: api
Stories: 60
Given: the API of the branch.
When: one address posts What-if calls past the limit within one minute.
Then: the call past the limit gets 429 with a retry-after, and a call to `/health` and to the analyzer from that address still answers.
Evidence: the test command and the status of each call.

AT-18: The What-if answer is gzip
App: api
Stories: none
Given: the API of the branch.
When: a client posts a What-if with `Accept-Encoding: gzip`.
Then: the answer has `Content-Encoding: gzip`, and its size is under 60 KB.
Evidence: the headers and the size.

AT-19: A cancelled call stops its work
App: api
Stories: 61
Given: the API of the branch.
When: a client posts a What-if and goes away after 100 ms.
Then: the log shows that the sim stopped before it ran all 10,000 runs.
Evidence: the test command and the log lines.

AT-20: A bad set result gets 422
App: api
Stories: none
Given: the API of the branch.
When: a client posts a set result for week 3, a week already played.
Then: the answer is 422 with a message that names the week.
Evidence: the request and the answer.

AT-21: The API machine stays the same size
App: api
Stories: 59
Given: the branch.
When: the reader reads `apps/api/fly.toml`.
Then: the machine is `shared-cpu-1x` with 1 GB, as on `main`.
Evidence: `git diff main -- apps/api/fly.toml`, with no change to `[[vm]]`.

AT-22: A What-if on Fly answers in time
App: api
Stories: 58
Given: the API of the branch on Fly, idle for 10 minutes.
When: a client posts 10 What-if calls of `cpc`, one at a time.
Then: the median time is 2.5 s or less.
Evidence: the 10 times and the median.

AT-23: The time just after a deploy is on record
App: api
Stories: 58
Given: the API of the branch on Fly, within 1 minute of a deploy.
When: a client posts 10 What-if calls of `cpc`, one at a time.
Then: each call answers 200, and each time is on record for Brian.
Evidence: the 10 times.

AT-24: The page opens on Your team
App: site
Stories: 1, 2
Given: `/sim/2026/` of `cpc`, built from week 10, with Bo Girds as Your team.
When: the reader opens the page.
Then: the header shows the avatar of Bo Girds, "Bo Girds", 11-9, 4 weeks left, and the playoff odds of the file.
Evidence: the site evidence set of the page.

AT-25: The sentence opens the ladder
App: site
Stories: 3, 5
Given: the page of AT-24.
When: the reader taps the sentence of more wins.
Then: the ladder opens with each count of more wins, its odds, and its chance, as in the file.
Evidence: the site evidence set, open.

AT-26: The week switch goes from week 11 to Playoffs
App: site
Stories: 6
Given: the page of AT-24.
When: the reader taps each item of the week switch.
Then: the items are Wk 11, Wk 12, Wk 13, Wk 14, and Playoffs, and each opens its own week page.
Evidence: the site evidence set of Wk 12 and of Playoffs.

AT-27: The week card shows four tiles in cpc
App: site
Stories: 7, 8, 9
Given: the page of AT-24, week 11.
When: the reader looks at the week card.
Then: the card says "Week 11 vs Maye d'force B with U" and shows four tiles, each with the odds after, the chance, and the wins it adds, as in the file.
Evidence: the site evidence set.

AT-28: The week card shows two tiles in norcal
App: site
Stories: 10
Given: `/sim/2026/` of `norcal`, built from week 10, with Bo Girds as Your team.
When: the reader looks at the week card of week 11.
Then: the card says "Week 11 vs The Mean Machine" and shows two tiles, a win and a loss.
Evidence: the site evidence set.

AT-29: The root-for card says what a loss costs
App: site
Stories: 11, 12, 13
Given: the page of AT-24, week 11.
When: the reader opens the root-for card.
Then: the header says "If you lose, you drop to X%" with X from the file, and each row shows "<winner> beats <loser>", its reason, and "→ Y%".
Evidence: the site evidence set, with the card open on the phone.

AT-30: The root-for card opens from one row on a phone
App: site
Stories: 11
Given: the page of AT-24, week 11.
When: the reader views the page at 390x660 and at 1080x740.
Then: at 390x660 the card is one row that opens on a tap, and at 1080x740 the card shows in full.
Evidence: the site evidence set at both sizes.

AT-31: A long team name stays readable in a root-for row
App: site
Stories: 14
Given: a root-for row with "Maye d'force B with U".
When: the reader views it at 390x660.
Then: the names of the winner and the loser both show in full or as a short name, with no cut word.
Evidence: the screenshot at 390x660 and the overlap check.

AT-32: A noisy number shows "about"
App: site
Stories: 15
Given: a ladder step with the "about" flag in the real file, and a result tile with the flag in a unit test.
When: the reader looks at its tile.
Then: the number reads "about X%".
Evidence: the screenshot and the result in the file.

AT-33: A tap on a tile sets a What-if
App: site
Stories: 16, 17, 18
Given: the page of AT-24, week 11, with the API of the branch.
When: the reader taps the tile "Win and beat the median".
Then: the header odds, the sentence, and the root-for list change to the numbers of the API answer, and Wk 12 opens.
Evidence: the site evidence set after the tap, and the API answer.

AT-34: The set line lists each set result and resets
App: site
Stories: 19
Given: the page after AT-33.
When: the reader taps Reset on the set line.
Then: the set line goes away, and the page shows the numbers of the file again.
Evidence: screenshots before and after the Reset at 390x660.

AT-35: A new tap cancels the call before it
App: site
Stories: 20
Given: the page of AT-24, with the API of the branch.
When: the reader taps two tiles within 200 ms.
Then: the network log shows the first call cancelled, and the page shows the answer of the second call.
Evidence: the network log and the screenshot.

AT-36: The page works with the API down
App: site
Stories: 23
Given: the page of AT-24, with the API stopped.
When: the reader opens the page and taps a tile.
Then: the page shows the numbers of the file, and the tap shows one line that the What-if is not available now.
Evidence: the screenshots at 390x660 and the network log.

AT-37: The page makes no call with no set result
App: site
Stories: 24
Given: the page of AT-24.
When: the reader opens the page and switches weeks with no tap on a tile.
Then: the network log shows no What-if call.
Evidence: the network log.

AT-38: "Sim week 11" plays Games, then Standings
App: site
Stories: 25, 29, 32
Given: the page of AT-24.
When: the reader taps "Sim week 11".
Then: the stage plays the games with Bo Girds first and one median line, then the standings in the Race style.
Evidence: the site evidence set of each part.

AT-39: "Sim the season" plays three screens on one stage
App: site
Stories: 26, 28, 30, 31, 33
Given: the page of AT-24.
When: the reader taps "Sim the season" and lets it play.
Then: the stage plays Season, Playoffs one round at a time, then Champion, with no scroll, and the controls stay in their own row.
Evidence: the site evidence set of each screen.

AT-40: The replay follows the set results
App: site
Stories: 27
Given: the page with Bo Girds set to win week 11 and beat the median.
When: the reader taps "Sim week 11".
Then: the games show Bo Girds beat Maye d'force B with U, and the median line says Bo Girds was above.
Evidence: the screenshots of both parts.

AT-41: The replay uses fades only under reduced motion
App: site
Stories: 34
Given: the page of AT-24 with reduced motion on.
When: the reader taps "Sim the season".
Then: no element moves its position, and each change is a fade.
Evidence: the screenshots and the output of a motion check.

AT-42: A team in the playoffs sees its title odds and its game
App: both
Stories: 35, 36
Given: the round-two fixture, with the top seed as Your team.
When: the reader opens the Playoffs page of the sim page.
Then: the page shows the title odds of that team, its game of the round, and two tiles with the odds after a win and after a loss.
Evidence: the command of the fixture build, the page block, and the site evidence set.

AT-43: A team out of the playoffs sees the bracket
App: both
Stories: 37
Given: the playoff fixture, with the 12th team as Your team.
When: the reader opens the sim page.
Then: the page says "Out of the playoffs" and shows the bracket with the title odds of each team left.
Evidence: the page block and the site evidence set.

AT-44: After the final the page shows the champion
App: both
Stories: 38
Given: the season-end fixture.
When: the reader opens the sim page.
Then: the page shows the final bracket and the champion, with no result tile and no sim button.
Evidence: the page block and the site evidence set.

AT-45: The Sim tile shows Your team's odds after Standings
App: site
Stories: 39
Given: the week 10 page of `cpc`, with Bo Girds as Your team.
When: the reader scrolls past Standings.
Then: the Sim tile sits between Standings and Next week, shows the odds of Bo Girds and the line of more wins from the file, and links to `/sim/2026/`.
Evidence: the site evidence set.

AT-46: The Sim tile shows a league fact with no team set
App: site
Stories: 40
Given: the week 10 page of `cpc`, with no team set.
When: the reader scrolls past Standings.
Then: the Sim tile shows the league fact of the file.
Evidence: the site evidence set and the fact in the file.

AT-47: The Sim tile fits a playoff week
App: both
Stories: 41
Given: the week page of the playoff fixture.
When: the reader views the Sim tile, once with the top seed and once with the 12th team as Your team.
Then: the tile shows the title odds of the top seed, and the favorite fact for the 12th team.
Evidence: the screenshots of both tiles at 390x660.

AT-48: The week 17 Sim tile shows the champion
App: both
Stories: 42
Given: the week 17 page of the season-end fixture.
When: the reader views the Sim tile.
Then: the tile names the champion of the fixture and links to the sim page.
Evidence: the site evidence set.

AT-49: The home page ladder links to the sim page
App: site
Stories: 43
Given: the home page of `cpc` with Bo Girds as Your team.
When: the reader taps the link of the Playoff race ladder.
Then: the browser opens `/sim/2026/`.
Evidence: the screenshot of the ladder and the URL after the tap.

AT-50: The menu has "Season sim"
App: site
Stories: 44
Given: any page of `cpc`.
When: the reader opens the menu.
Then: the menu has "Season sim", and it opens `/sim/2026/`.
Evidence: the site evidence set of the open menu.

AT-51: The Announcement opens on the home page
App: site
Stories: 45, 46
Given: the home page of `cpc` in a fresh browser, with Bo Girds as Your team.
When: the page loads.
Then: the sheet rises with the rows of The Blue Tent, Bo Girds, and Return of T Mac, the playoff line, the chip, and the copy of the spec.
Evidence: the site evidence set.

AT-52: The What-if chip is a button
App: site
Stories: 46
Given: the open Announcement of AT-51, after the automatic turn.
When: the reader taps the chip twice.
Then: the first tap turns it off and the odds go back to the odds of the week, and the second tap turns it on again.
Evidence: screenshots after each tap at 390x660.

AT-53: The chip turns on once by itself after the sheet settles
App: site
Stories: 47
Given: the home page of AT-51.
When: the page loads and the reader does not tap.
Then: the chip turns on once after the sheet stops, and it does not turn on again.
Evidence: a timed series of screenshots at 390x660 over 5 s.

AT-54: Four ways close the Announcement
App: site
Stories: 48
Given: the open Announcement of AT-51.
When: the reader closes it by a drag down, "Not now", Escape, or a tap on the dim, once each in a fresh browser.
Then: the sheet closes each time.
Evidence: the test output of the four cases.

AT-55: A dismiss or the link hides the Announcement for good
App: site
Stories: 49
Given: a browser where the reader closed the Announcement, and a browser where the reader pressed "Open the sim".
When: the reader reloads the home page in each browser.
Then: the Announcement does not open.
Evidence: the test output of both cases and a screenshot after each reload.

AT-56: The Announcement does not open on the sim page or over a sheet
App: site
Stories: 50
Given: a fresh browser with Bo Girds as Your team.
When: the reader loads `/sim/2026/`, then loads the home page with the menu sheet open.
Then: the Announcement does not open in either case.
Evidence: the test output and screenshots.

AT-57: A first visit shows the team picker, and the next load shows the Announcement
App: site
Stories: 51
Given: the home page of `cpc` in a fresh browser with no team set.
When: the reader picks Bo Girds in the team picker, then reloads.
Then: the first load shows only the team picker, and the reload shows the Announcement.
Evidence: screenshots of both loads at 390x660.

AT-58: The Announcement does not open with no team set
App: site
Stories: 51
Given: a fresh browser with no team set. The team picker cannot close with no team.
When: the reader reloads the home page.
Then: the Announcement does not open, and it opens on a later load after a team is set.
Evidence: the test output.

AT-59: The Announcement stops after its end date
App: site
Stories: 52
Given: a fresh browser with Bo Girds as Your team, and the clock set 1 day past the end date.
When: the home page loads.
Then: the Announcement does not open.
Evidence: the test output.

AT-60: The Announcement takes other art and copy
App: site
Stories: 53
Given: the Announcement component with a test art slot and test copy.
When: the test renders it.
Then: it shows the test art and copy, with the same close rules.
Evidence: the test output.

AT-61: The Announcement under reduced motion
App: site
Stories: 47
Given: the home page of AT-51 with reduced motion on.
When: the page loads.
Then: the rows and the odds show at once, and the chip does not turn on by itself.
Evidence: screenshots at 390x660.

AT-62: No banned word shows on the new parts
App: site
Stories: none
Given: the built `cpc` and `norcal` sites.
When: the reader searches the text of the sim page, the Sim tile, and the Announcement.
Then: none has "rival", "Brian", "Jev", "Advisor", "Finder", or "front door".
Evidence: the search command and its output.

AT-63: The site has no copy of the sim
App: site
Stories: none
Given: the branch.
When: the reader searches the site code and the sim package site code for a draw of a score.
Then: no site module draws a score, and each What-if number comes from the API.
Evidence: the search command and its output.

AT-64: The midseason report does not change
App: both
Stories: none
Given: the branch.
When: the reader runs `git diff main -- clients/*/published/2026/sim.json clients/*/published/2026/midseason.json`.
Then: the diff is empty, and `/midseason/2026/` looks as on `main`.
Evidence: the diff and screenshots of `/midseason/2026/` at 390x660 on both.

AT-65: The page has no grid of every game
App: site
Stories: none
Given: the page of AT-24.
When: the reader looks at each week page.
Then: the only result tiles are the results of Bo Girds, and no grid lists every game.
Evidence: the site evidence set of each week page.

AT-66: The page offers no result of an unset bracket game
App: site
Stories: none
Given: the playoff fixture, with the top seed as Your team.
When: the reader looks at the Playoffs page.
Then: only the game of the current round has tiles, and no later round has a tile.
Evidence: the screenshots at 390x660.

AT-67: The server keeps no record of a dismiss
App: api
Stories: none
Given: the branch.
When: the reader lists the routes of the API.
Then: no route reads or writes an Announcement.
Evidence: the route list.

AT-68: The API keeps no cache of answers
App: api
Stories: none
Given: the API of the branch.
When: a client posts the same What-if twice.
Then: the log shows two runs of the sim.
Evidence: the test command and the log.

AT-69: The page shows no chart of odds by week after the final
App: site
Stories: none
Given: the season-end fixture.
When: the reader opens the sim page.
Then: the page has no chart of the odds of each team by week.
Evidence: the site evidence set.

## Trace

Story 1: AT-24
Story 2: AT-24
Story 3: AT-6, AT-25
Story 4: AT-6
Story 5: AT-6, AT-25
Story 6: AT-26
Story 7: AT-7, AT-27
Story 8: AT-7, AT-27
Story 9: AT-7, AT-27
Story 10: AT-8, AT-28
Story 11: AT-9, AT-29, AT-30
Story 12: AT-9, AT-29
Story 13: AT-9, AT-29
Story 14: AT-31
Story 15: AT-10, AT-32
Story 16: AT-11, AT-14, AT-33
Story 17: AT-11, AT-33
Story 18: AT-33
Story 19: AT-34
Story 20: AT-35
Story 21: AT-12
Story 22: AT-14
Story 23: AT-36
Story 24: AT-1, AT-15, AT-37
Story 25: AT-38
Story 26: AT-39
Story 27: AT-40
Story 28: AT-39
Story 29: AT-38
Story 30: AT-39
Story 31: AT-39
Story 32: AT-38
Story 33: AT-39
Story 34: AT-41
Story 35: AT-42
Story 36: AT-42
Story 37: AT-43
Story 38: AT-44
Story 39: AT-45
Story 40: AT-46
Story 41: AT-47
Story 42: AT-48
Story 43: AT-49
Story 44: AT-50
Story 45: AT-51
Story 46: AT-51, AT-52
Story 47: AT-53, AT-61
Story 48: AT-54
Story 49: AT-55
Story 50: AT-56
Story 51: AT-57, AT-58
Story 52: AT-59
Story 53: AT-60
Story 54: AT-2
Story 55: AT-1, AT-3
Story 56: AT-4
Story 57: AT-2, AT-5
Story 58: AT-22, AT-23
Story 59: AT-21
Story 60: AT-17
Story 61: AT-19
Out of scope "A TypeScript copy of the sim": AT-63
Out of scope "A change to the midseason report": AT-64
Out of scope "A set result of a bracket game whose teams are not set": AT-66
Out of scope "A record of a dismissed Announcement on the server": AT-67
Out of scope "A grid to pick any game of any week": AT-65
Out of scope "A cache of live sim answers": AT-68
Out of scope "A bigger API machine": AT-21
Out of scope "A refetch from Sleeper on a What-if": AT-16
Out of scope "A lower level for a team with a season-ending injury": AT-13
Out of scope "A chart of odds by week after the final": AT-69

## Revisions

None yet.
