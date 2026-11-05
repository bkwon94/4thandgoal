# Site redesign: acceptance tests

Spec: `.scratch/site-redesign/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

Every test runs on the static export of both clients, CPC and NorCal, with `2026` week 8 as the latest week. A site test names screenshots of both clients unless it names one client. Screenshots go at 375, 768, and 1280 px, each in the light theme and the dark theme. The canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8 holds the approved boards, so a reader can compare each screenshot with its board.

## Tests

AT-1: Dark is the first paint with no stored choice
App: site
Stories: 1, 11
Given: A fresh browser with no `cpc.theme` key, on the CPC and the NorCal export.
When: The reader opens the home page.
Then: `<html>` has the class `dark` in the first paint, and the page shows the dark set with no light flash.
Evidence: The served HTML of the home page with `class="dark"` on `<html>`, a screenshot at 375 px of each client, and a screen recording of the first load.

AT-2: Dark with scripts off
App: site
Stories: 12
Given: A browser with scripts off.
When: The reader opens the week 8 page of each client.
Then: The page shows the dark set, and every chapter shows at rest.
Evidence: Screenshots of the week 8 page at 375 px of each client, with scripts off.

AT-3: A stored light choice opens in light
App: site
Stories: 9, 10
Given: The reader tapped the theme button to light on an earlier visit, so `cpc.theme` is `"light"`.
When: The reader opens the home page again.
Then: The page opens in light with no dark flash, and `<html>` has no `dark` class.
Evidence: A screen recording of the load, and screenshots of the home page at 375 px of each client.

AT-4: NorCal has a light theme and the theme button
App: site
Stories: 8, 13
Given: The NorCal export.
When: The reader taps the theme button in the top band.
Then: The page goes light, with the NorCal light set of the spec: page `#f5f3ef`, white cards, and accent text `#9a3412`.
Evidence: Screenshots of the NorCal home page before and after the tap, at 375, 768, and 1280 px.

AT-5: The hero stays dark in light
App: site
Stories: 14, 15
Given: The light theme.
When: The reader opens the week 8 page.
Then: The hero sits on the `band` color with the grid, the brackets, and the glow. The page and the cards are light. NorCal gold shows only in the hero.
Evidence: Screenshots of the week 8 hero at 375, 768, and 1280 px in light, for each client.

AT-6: The brand of each client
App: site
Stories: 6, 7
Given: Both exports.
When: The reader opens the home page of each client.
Then: CPC shows its red, its logo, and its copy. NorCal shows its gold and orange, its logo, and its copy. Both use Space Grotesk and JetBrains Mono.
Evidence: Screenshots of both home pages at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-7: The hero and the motion
App: site
Stories: 2, 3, 4
Given: The dark theme, with motion allowed.
When: The reader opens the week 8 page.
Then: The hero shows a scan line once. The content under it rises in a stagger, and the share bars grow once.
Evidence: A screen recording of the load at 375 px and 1280 px, for each client.

AT-8: Reduced motion
App: site
Stories: 5
Given: The browser setting "reduce motion" is on.
When: The reader opens the week 8 page and taps a game card.
Then: No scan line, no rise, no bar growth, and no tap scale. All content shows at rest.
Evidence: A screen recording at 375 px with reduced motion on, for CPC.

AT-9: The dock on a phone
App: site
Stories: 16, 17, 18, 19
Given: A 375 px width.
When: The reader scrolls the week 8 page to the end.
Then: The dock stays at the bottom with Home, Week 8, Rankings, Managers, and Trade, each with an icon and a label. Week 8 is marked.
Evidence: Screenshots of the week 8 page at 375 px at the top and at the end, each in the light theme and the dark theme, for each client.

AT-10: The pill bar on a desktop
App: site
Stories: 19, 22
Given: A 1280 px width.
When: The reader opens the rankings page and scrolls down.
Then: The top band shows the brand mark, the pill bar with full labels, the week chip, and the theme button. Rankings is marked, and the top band stays on screen.
Evidence: Screenshots of the rankings page at 768 and 1280 px, at the top and after a scroll, each in the light theme and the dark theme.

AT-11: The week chip and the strip of weeks
App: site
Stories: 20, 21
Given: The CPC export, which has weeks 6, 7, and 8.
When: The reader taps "WK 08" in the top band of the home page.
Then: A strip shows weeks 6, 7, and 8, with the brand edge on week 8. A tap on week 7 opens the week 7 page.
Evidence: Screenshots of the open strip at 375, 768, and 1280 px, each in the light theme and the dark theme, and the URL after the tap.

AT-12: The chapter rail
App: site
Stories: 23
Given: A 1280 px width.
When: The reader scrolls the week 8 page to Standings.
Then: The chapter rail on the left marks Standings.
Evidence: Screenshots of the week 8 page at 1280 px at Standings, each in the light theme and the dark theme.

AT-13: The client menu has no layout key
App: site
Stories: 24
Given: The two `client.toml` files.
When: The build of each client runs.
Then: Neither file has a `layout` key in `[menu]`, and a `layout` key fails the build with a message that names it.
Evidence: The `[menu]` table of each file, and the output of a build with a `layout` key added by hand.

AT-14: The home page order
App: site
Stories: 25, 26, 27, 28, 29, 30, 31
Given: CPC, week 8. The Matchup of the Week is The Blue Tent over London Cooking, 100.31 to 98.88.
When: The reader opens the home page.
Then: The page shows, in order: the intro, the hero with "1.43" as the big number and a "Read Week 8" button, the four numbers, the top three of Power Rankings led by All You Need Is Love, the tool tiles, and a row for weeks 8, 7, and 6.
Evidence: Full-page screenshots of the CPC home page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-15: The NorCal home page
App: site
Stories: 25, 26, 32
Given: NorCal, week 8. The Matchup of the Week is kaiedmonds over The Mean Machine, 132.38 to 121.76.
When: The reader opens the home page.
Then: The hero shows "10.62" as the big number. Power Rankings is led by Mitseeker5000. One weekly report row shows, for week 8.
Evidence: Full-page screenshots of the NorCal home page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-16: The week page order
App: site
Stories: 33, 34, 35, 38, 39, 40, 41, 42, 43, 44, 45, 46
Given: CPC, week 8.
When: The reader opens the week 8 page.
Then: The page shows one scroll with no tabs, in order: the hero, the four numbers, every game, Game Changer with Joe Burrow at 42.48, Awards, Position leaders, Trades, the median game, Standings, Next week, and the footer.
Evidence: Full-page screenshots of the week 8 page of each client at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-17: A recap opens on a tap
App: site
Stories: 36, 37
Given: CPC, week 8.
When: The reader taps the game card of The Blue Tent and London Cooking.
Then: The card opens its recap with a brand edge. The recap holds one "Manager page" link.
Evidence: Screenshots of the open card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-18: Position leaders
App: site
Stories: 40
Given: CPC, week 8.
When: The reader taps the chip WR in Position leaders.
Then: The chapter shows the top three WR of week 8.
Evidence: Screenshots of the chapter after the tap at 375 and 1280 px, in the dark theme.

AT-19: The analyzer, empty
App: site
Stories: 47, 48, 50, 57, 58
Given: The analyzer page of each client, with no pick.
When: The reader opens the page.
Then: The page shows "Trade Analyzer", "Who gets what?", the teams row with Your Team, Team Two, and a "+" slot with "2 of 4", two empty cards, the line on what each team needs, and the "Grade the Trade" bar turned off on the dock.
Evidence: Screenshots of the empty analyzer at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-20: The picker
App: site
Stories: 51, 53, 54, 55
Given: The live API, CPC, with Your Team and Team Two chosen.
When: The reader taps "Add a player Your Team gets", checks two players, and taps Done.
Then: The sheet shows a tab for Team Two, a search field, and the chips All, QB, RB, WR, TE, and DEF. After Done, the Your Team card lists both players, each with a "from <Team Two>" tag.
Evidence: Screenshots of the open sheet and of the card after Done, at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-21: The sheet closes three ways
App: site
Stories: 55
Given: The picker sheet is open.
When: The reader closes it with Done, then with the close button, then with a tap on the dim page.
Then: Each action closes the sheet and keeps the picks.
Evidence: A screen recording at 375 px, for CPC.

AT-22: A third team
App: site
Stories: 49, 52, 56
Given: The live API, CPC, with two teams in the trade.
When: The reader taps "+" and taps a team.
Then: The sheet shows every team, with the two teams in the trade dimmed. A third card shows with a remove button, and the slot reads "3 of 4".
Evidence: Screenshots of the team sheet and of the form after the tap, at 375 and 1280 px, each in the light theme and the dark theme.

AT-23: The body of `POST /analyze` holds
App: site
Stories: 51
Given: The live API, CPC. Your Team gets one player from Team Two, and Team Two gets one player from Your Team.
When: The reader taps "Grade the Trade".
Then: The request body has one `gives` entry for each side, with `to` set to the team of the card. It has the same shape as before the redesign.
Evidence: The request body from the network log, and the body that `main` sends for the same trade.

AT-24: Loading and the result
App: site
Stories: 59, 60
Given: The live API, CPC, with a valid trade of two teams.
When: The reader taps "Grade the Trade".
Then: The form folds to a line of faces, the hero shows "Grading the Trade", and the bar reads "Grading…". Then the verdict fills the hero with the fairness block under it.
Evidence: Screenshots of the loading state and of the result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-25: The result of 3 teams
App: site
Stories: 61
Given: The live API, CPC, with a valid trade of three teams.
When: The reader taps "Grade the Trade".
Then: The swap card shows one row for each team with "Gives" and "Gets", and each player shows a "TO" or "FROM" tag.
Evidence: Screenshots of the result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-26: The error state
App: site
Stories: 62
Given: The live API, CPC, with a trade that the API rejects.
When: The reader taps "Grade the Trade".
Then: The form unlocks, and a box with the alert icon, the message of `toErrorLine`, and "Try Again" sits above the bar.
Evidence: Screenshots of the error at 375 and 1280 px, each in the light theme and the dark theme, and the API response.

AT-27: The finder on NorCal only
App: site
Stories: 63, 64
Given: The live API. NorCal has `finder = true`, and CPC has `finder = false`.
When: The reader opens the analyzer of each client, and on NorCal taps "Find a Trade".
Then: Only NorCal shows the "Find a Trade" card under the form. Its result shows up to three cards, each with the swap, the Fairness pill, the reasons, and "See the Full Result".
Evidence: Screenshots of both analyzer pages, and of the NorCal finder result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-28: The rankings Ladder
App: site
Stories: 65, 66, 68, 69
Given: CPC, week 8. All You Need Is Love is rank 1 at 11 and 5, up 4.
When: The reader opens the rankings page.
Then: The hero shows "01", All You Need Is Love, 11-5, up 4, and the tiles Playoff, Bye, and Seed. Under it come the week chips, one card for each other team, and the note on the four parts.
Evidence: Full-page screenshots of the rankings page of each client at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-29: A ranking card opens
App: site
Stories: 67
Given: CPC, week 8.
When: The reader taps the card at rank 2.
Then: The card opens four tiles for Stand, Form, Sched, and Pts, the blurb, and a link to the manager page.
Evidence: Screenshots of the open card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-30: The managers index
App: site
Stories: 70, 71, 72
Given: CPC, week 8.
When: The reader opens the managers index and taps a card outside its text.
Then: The index shows one card for each of the 12 teams in standings order, each with the grade box and the grade text. The tap opens that manager page.
Evidence: Full-page screenshots of the index at 375, 768, and 1280 px, each in the light theme and the dark theme, and the URL after the tap.

AT-31: The manager page
App: site
Stories: 73, 74, 75, 76, 77, 78, 79
Given: CPC, week 8, the team To Infinity and Bijan, the longest team name of CPC.
When: The reader opens its manager page.
Then: The page shows the back link, the hero with the grade letter as the big number and a W or L chip for each week, then Season So Far, Roster, Best Adds, Top Performers, and Moves. The name does not cut off.
Evidence: Full-page screenshots of the page at 375, 768, and 1280 px, each in the light theme and the dark theme, for To Infinity and Bijan and for The Mean Machine of NorCal.

AT-32: The 404 page
App: site
Stories: 80, 81
Given: Both exports.
When: The reader opens a URL that no page has, such as `/2026/week-99/`.
Then: The page shows the hero with "ERROR // PAGE NOT FOUND", a big "404", the line of the spec, and the buttons "Go to Week 8" and "Go Home".
Evidence: Screenshots of the 404 page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-33: Photos and the fallback
App: site
Stories: 82, 83, 84
Given: NorCal, week 8, which lacks a headshot for some players.
When: The reader opens the week 8 page.
Then: Each team row shows its Sleeper avatar. Each headshot sits in a round frame, cropped at the shoulders. A player with no headshot shows the initials in the frame.
Evidence: Screenshots of Awards and Position leaders at 375 px, each in the light theme and the dark theme, with the name of a player that shows initials.

AT-34: The readability floor passes in CI
App: site
Stories: 85, 86, 87, 88, 89
Given: The PR of the Spec branch.
When: CI runs `build-each-client.mjs`.
Then: The floor passes for both clients: the full floor on the 7 pages and the 3 open states, and the fast sweep on every other page. The output prints the count of each text tier and each exempt link.
Evidence: The CI log of the floor, with its time.

AT-35: The readability floor catches a break
App: site
Stories: 89
Given: A local branch from the Spec branch with one blurb set to 14px.
When: `build-each-client.mjs` runs.
Then: The floor fails and names the page, the element, and the size.
Evidence: The command output.

AT-36: The fonts load from the site
App: site
Stories: 92, 93, 94
Given: The CPC export, served by the Worker.
When: The reader opens the week 8 page.
Then: The page loads exactly two font files from its own origin, 56,000 bytes or less in total, with two preloads. No request goes to an outside font host. The number columns stay aligned before the mono font loads.
Evidence: The network log of the load, the cache headers of each font file, the layout shift, and a screenshot with the font files blocked.

AT-37: The brand schema rejects old keys
App: site
Stories: none
Given: A `brand.toml` with a `[fonts]` key, a `radius_card` key, or only one set.
When: The build of the client runs.
Then: The build fails and names the key or the missing set.
Evidence: The output of each of the three builds.

AT-38: No waiver page
App: site
Stories: none
Given: Both exports.
When: The reader opens `/2026/week-08/waiver/`.
Then: No client builds a waiver page, and the URL shows the 404 page.
Evidence: The list of built routes of each client, and a screenshot of the URL.

AT-39: The theme does not follow the system setting
App: site
Stories: none
Given: The system setting is light, and no `cpc.theme` key is stored.
When: The reader opens the home page.
Then: The page opens in dark.
Evidence: A screenshot at 375 px with the system setting light, for CPC.

AT-40: The analyzer content holds
App: site
Stories: none
Given: The live API, CPC, with the result of AT-24.
When: The reader reads the result.
Then: The result shows "Suggested Counters · No counters yet.", and its text matches the text that `main` shows for the same trade.
Evidence: The text of the result on the Spec branch and on `main`.

AT-41: The pipeline does not change
App: both
Stories: none
Given: The diff of the Spec branch against `main`.
When: The evidence agent lists the changed paths.
Then: No path under `apps/pipeline/`, `apps/api/`, or `clients/<slug>/published/` changes.
Evidence: The output of `git diff --stat main...site-redesign` for those paths.

## Trace

Story 1: AT-1
Story 2: AT-7
Story 3: AT-7
Story 4: AT-7
Story 5: AT-8
Story 6: AT-6
Story 7: AT-6
Story 8: AT-4
Story 9: AT-3
Story 10: AT-3
Story 11: AT-1
Story 12: AT-2
Story 13: AT-4
Story 14: AT-5
Story 15: AT-5
Story 16: AT-9
Story 17: AT-9
Story 18: AT-9
Story 19: AT-9, AT-10
Story 20: AT-11
Story 21: AT-11
Story 22: AT-10
Story 23: AT-12
Story 24: AT-13
Story 25: AT-14, AT-15
Story 26: AT-14, AT-15
Story 27: AT-14
Story 28: AT-14
Story 29: AT-14
Story 30: AT-14
Story 31: AT-14
Story 32: AT-15
Story 33: AT-16
Story 34: AT-16
Story 35: AT-16
Story 36: AT-17
Story 37: AT-17
Story 38: AT-16
Story 39: AT-16
Story 40: AT-16, AT-18
Story 41: AT-16
Story 42: AT-16
Story 43: AT-16
Story 44: AT-16
Story 45: AT-16
Story 46: AT-16
Story 47: AT-19
Story 48: AT-19
Story 49: AT-22
Story 50: AT-19
Story 51: AT-20, AT-23
Story 52: AT-22
Story 53: AT-20
Story 54: AT-20
Story 55: AT-20, AT-21
Story 56: AT-22
Story 57: AT-19
Story 58: AT-19
Story 59: AT-24
Story 60: AT-24
Story 61: AT-25
Story 62: AT-26
Story 63: AT-27
Story 64: AT-27
Story 65: AT-28
Story 66: AT-28
Story 67: AT-29
Story 68: AT-28
Story 69: AT-28
Story 70: AT-30
Story 71: AT-30
Story 72: AT-30
Story 73: AT-31
Story 74: AT-31
Story 75: AT-31
Story 76: AT-31
Story 77: AT-31
Story 78: AT-31
Story 79: AT-31
Story 80: AT-32
Story 81: AT-32
Story 82: AT-33
Story 83: AT-33
Story 84: AT-33
Story 85: AT-34
Story 86: AT-34
Story 87: AT-34
Story 88: AT-34
Story 89: AT-34, AT-35
Story 90: no test. Reason: the screenshots are the evidence of every site test, so each test proves it.
Story 91: no test. Reason: it is a step of the build, not a behavior of the finished site.
Story 92: AT-36
Story 93: AT-36
Story 94: AT-36
Out of scope "The pipeline and any new data": AT-41
Out of scope "The waiver page": AT-38
Out of scope "A test of the first reaction with other managers": no test. Reason: an agent cannot build it by mistake.
Out of scope "Timed tasks": no test. Reason: an agent cannot build it by mistake.
Out of scope "A font or a radius per brand": AT-37
Out of scope "A change to the content of the analyzer result": AT-40
Out of scope "A theme that follows the system setting": AT-39

## Revisions

None yet.
