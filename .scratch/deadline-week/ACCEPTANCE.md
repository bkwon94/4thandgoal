# Deadline week: acceptance tests

Spec: `.scratch/deadline-week/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The Lock of client `cpc` is 00:00 Eastern on Tue 2026-11-24. The site tests set the browser clock to a fixed time, named in each test. A fixed clock is a test input, not a mock mode of the app.

Trade W is real data of client `cpc`, season `2026`, week 9 (Sleeper leg 9): the trade in which roster 4 sends $5 of FAAB to roster 8. The evidence agent reads it live from Sleeper, records the full Sleeper answer, and records the name of each team and player. A site test that needs a known list of trades serves this recorded answer through a Playwright route, as `analyzer-stage` did.

Week 11 is the real week 11 of `cpc` on the day of the run. The evidence agent records its accepted trades. If week 11 holds no trade, the tests that need one use trade W.

The site tests run in WebKit. Screenshots are at 375, 768, and 1280 px, each in the light theme and the dark theme (ADR 0006). Each site test also runs `devices["iPhone 15"]` at 390 by 660 and asserts no horizontal scroll and no overlap of the Deadline banner with the top band.

## Tests

AT-1: The Deadline banner shows the countdown
App: site
Stories: 1, 2, 3, 13, 20, 21
Given: The front door of `cpc`, the clock at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader opens the page.
Then: Under the top band, the Deadline banner shows "TRADE DEADLINE" over "~2d 14h 05m".
Evidence: screenshots of the top of the front door at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-2: The countdown ticks
App: site
Stories: 4
Given: The front door of `cpc`, the clock at 09:55:00 Eastern on Sat 2026-11-21.
When: The clock moves on 60 s.
Then: The countdown reads "~2d 14h 04m".
Evidence: the countdown text before and after, and screenshots of the Deadline banner after, at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-3: The last hours show seconds on the accent fill
App: site
Stories: 5, 6
Given: The front door of `cpc`, the clock at 21:18:50 Eastern on Mon 2026-11-23.
When: The reader opens the page.
Then: The Deadline banner has the accent fill and reads "~2h 41m 10s".
Evidence: the computed background of the Deadline banner, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-4: Reduced motion stops the shimmer
App: site
Stories: 7
Given: The front door of `cpc`, the clock at 21:18:50 Eastern on Mon 2026-11-23, with `prefers-reduced-motion: reduce`.
When: The reader opens the page.
Then: No element of the Deadline banner has a running animation.
Evidence: the result of `document.getAnimations()` inside the Deadline banner, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-5: The whole Deadline banner opens the Trade Wire
App: site
Stories: 8, 12, 22
Given: The rankings page of `cpc`, the clock at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader taps the countdown text at the left of the Deadline banner.
Then: The Trade Wire sheet opens, and the Deadline banner is one button named "Open the Trade Wire, N new trades", where N is the count of week 11 trades.
Evidence: the accessible name and role of the Deadline banner, the import line of the sheet wrapper, and screenshots of the open sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-6: The badge counts the trades of week 11
App: site
Stories: 9, 10
Given: The front door of `cpc`, the clock at 09:55:00 Eastern on Sat 2026-11-21, with the real week 11 trades.
When: The reader opens the page.
Then: The badge reads "N new" for N week 11 trades, or shows no badge when N is 0.
Evidence: the count from the Trade Wire route, the badge text or its absence, and screenshots of the Deadline banner at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-7: The Deadline banner sinks on a press
App: site
Stories: 11
Given: The front door of `cpc`, the clock at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader holds a press on the Deadline banner.
Then: The content of the Deadline banner scales to 0.98 over 150 ms.
Evidence: the computed transform and transition during the press, and screenshots during the press at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-8: The Deadline banner has even padding and one left edge
App: site
Stories: 14
Given: The front door of `cpc`, the clock at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader opens the page.
Then: The top padding and the bottom padding of the Deadline banner differ by 1 px or less, and "TRADE DEADLINE" and the countdown start at the same x.
Evidence: the measured padding and x values at each size, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-9: The Deadline banner says the trade deadline has passed
App: site
Stories: 15, 16
Given: The front door of `cpc`, the clock at 00:00:01 Eastern on Tue 2026-11-24.
When: The reader opens the page.
Then: The Deadline banner reads "The trade deadline has passed. Good luck in the playoffs." and the badge reads "Final".
Evidence: screenshots of the Deadline banner at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-10: Deadline week ends by itself
App: site
Stories: 17
Given: The front door and the analyzer of `cpc`, the clock at 00:00:01 Eastern on Wed 2026-11-25.
When: The reader opens each page.
Then: Neither page shows the Deadline banner or the deadline eyebrow.
Evidence: screenshots of the top of each page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-11: Norcal has no Deadline week
App: site
Stories: 18
Given: The front door of `norcal`, the clock at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader opens the page.
Then: The page shows no Deadline banner.
Evidence: screenshots of the top of the page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-12: The copy uses plain words
App: site
Stories: 19, 88
Given: The front door, the open Trade Wire sheet, and the analyzer of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21, 21:18:50 Eastern on Mon 2026-11-23, and 00:00:01 Eastern on Tue 2026-11-24.
When: The evidence agent reads the visible text and the accessible names.
Then: No text holds "Lock", "Rosters are locked", "Deadline Board", "feed", "Jev", "Advisor", "Finder", or "Brian".
Evidence: the text dump of each page at each time, the search result, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-13: The Trade Wire route reads a trade in full
App: api
Stories: 24, 25
Given: The local API, with the route pointed at Sleeper leg 9 of `cpc` 2026.
When: The evidence agent calls the Trade Wire route with the passphrase.
Then: Trade W shows both teams with name and avatar, the players each team gets with positions, $5 of FAAB to roster 8, and no draft picks.
Evidence: the command, the recorded Sleeper answer, and the route answer.

AT-14: The Trade Wire lists only accepted week 11 trades, newest first
App: api
Stories: 23, 35
Given: The local API on the real Sleeper data of `cpc`.
When: The evidence agent calls the Trade Wire route with the passphrase.
Then: Each trade in the answer has leg 11 and status `complete`, in descending order of acceptance time, and no week 9 trade shows.
Evidence: the command, the raw Sleeper answer of leg 11, and the route answer.

AT-15: The Trade Wire route keeps its answer for 5 s
App: api
Stories: 27
Given: The local API with its request log on.
When: The evidence agent calls the route at 0 s, 2 s, and 6 s.
Then: The log shows one Sleeper read for the first two calls and a second Sleeper read for the call at 6 s.
Evidence: the commands with their times, and the log lines.

AT-16: The Trade Wire route needs the passphrase
App: api
Stories: 43
Given: The local API.
When: The evidence agent calls the route with no passphrase.
Then: The route answers 401 with no trades.
Evidence: the command and the answer.

AT-17: The Trade Wire route takes many phones on one IP
App: api
Stories: 42
Given: The local API with the limit of 30 requests per minute per IP.
When: The evidence agent makes 40 calls to the route from one IP in 60 s.
Then: All 40 calls answer 200.
Evidence: the script and the 40 status codes.

AT-18: The sheet holds the parts in order
App: site
Stories: 36, 40
Given: The front door of `cpc` with the `finder` flag on, the clock at 09:55:00 Eastern on Sat 2026-11-21, and trade W served as week 11.
When: The reader opens the Trade Wire.
Then: From the top, the sheet shows "Grade a trade" and "Find a trade", "TRADE DEADLINE ~2d 14h 05m", "Trade Wire", the live dot with "Updated", and trade W.
Evidence: the order of the parts in the DOM, and screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-19: The Trade Wire rows have even gaps
App: site
Stories: 24, 26
Given: The open Trade Wire of `cpc`, with trade W and one more real season trade served as week 11.
When: The evidence agent measures the rows.
Then: Inside each trade the gaps are 8 px, and the gaps between trades are equal, each within 1 px.
Evidence: the measured gaps at each size, and screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-20: A new trade slides in
App: site
Stories: 27, 28
Given: The open Trade Wire of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21, with the route first serving 1 week 11 trade.
When: The route starts to serve trade W as a second trade.
Then: Within 15 s, trade W shows at the top and the badge changes from "1 new" to "2 new".
Evidence: the time of the route change and of the first frame of trade W, and screenshots before and after at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-21: The Trade Wire shows when it last updated
App: site
Stories: 29
Given: The open Trade Wire of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader waits 3 s after a read.
Then: The sheet shows the live dot and "Updated 3s ago".
Evidence: the text at 0 s and 3 s, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-22: The poll stops when the tab hides and runs when it shows
App: site
Stories: 30, 31
Given: The front door of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21.
When: The tab hides for 30 s, then shows again.
Then: No route call goes out while the tab hides, and one goes out within 1 s of the show.
Evidence: the network log with times.

AT-23: The empty Trade Wire says so
App: site
Stories: 32
Given: The open Trade Wire of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21, with no week 11 trade served.
When: The reader opens the Trade Wire.
Then: The sheet reads "No trades yet this week."
Evidence: screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-24: The empty Trade Wire after the Lock says so
App: site
Stories: 33
Given: The open Trade Wire of `cpc`, at 00:00:01 Eastern on Tue 2026-11-24, with no week 11 trade served.
When: The reader opens the Trade Wire.
Then: The sheet reads "No trades this week."
Evidence: screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-25: A failed read keeps the list
App: site
Stories: 34
Given: The open Trade Wire of `cpc` with trade W shown.
When: The next route call answers 500.
Then: Trade W stays, and a short note says that the last read failed.
Evidence: the network log, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-26: "Grade a trade" opens Grade mode
App: site
Stories: 37
Given: The open Trade Wire of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21.
When: The reader taps "Grade a trade".
Then: The analyzer opens with "Grade a trade" selected in the switch.
Evidence: the URL, and screenshots of the analyzer hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-27: "Find a trade" hides while the `finder` flag is off
App: site
Stories: 38
Given: The open Trade Wire of `cpc` with the `finder` flag off.
When: The reader looks at the top of the sheet.
Then: The sheet shows "Grade a trade" and no "Find a trade".
Evidence: screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-28: "Find a trade" opens Find mode
App: site
Stories: 37, 48
Given: The open Trade Wire of `cpc` with the `finder` flag on.
When: The reader taps "Find a trade".
Then: The analyzer opens with "Find a trade" selected, the title "Trade Ideas", and the line "Who has a trade for you?".
Evidence: the URL, and screenshots of the analyzer hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-29: The trade links hide after the Lock
App: site
Stories: 39
Given: The front door of `cpc` with the `finder` flag on, at 00:00:01 Eastern on Tue 2026-11-24.
When: The reader opens the Trade Wire.
Then: The sheet shows neither "Grade a trade" nor "Find a trade".
Evidence: screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-30: A drag up does not lift the sheet off the bottom
App: site
Stories: 41
Given: The open Trade Wire of `cpc`, and the open team sheet of the front door.
When: The reader drags the grip of each sheet 200 px up.
Then: The bottom edge of each sheet stays at the bottom of the viewport, within 1 px.
Evidence: the bottom edge of each sheet during the drag, and screenshots during the drag at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-31: The analyzer switch is the ui-sdk SegmentedControl
App: site
Stories: 44, 45
Given: The analyzer of `cpc` with the `finder` flag on.
When: The reader opens the page.
Then: The hero shows "Grade a trade · Find a trade" across its full width in two halves whose widths differ by 1 px or less.
Evidence: the import line of the wrapper, the measured widths, and screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-32: The switch locks during a wait
App: site
Stories: 46
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker and the find stream held.
When: The reader taps "Find" and then taps "Grade a trade".
Then: The switch stays on "Find a trade", and the wait goes on.
Evidence: the switch state and attributes during the wait, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-33: Find mode shows the partner choice and the position chips
App: site
Stories: 47, 50, 51
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker.
When: The reader opens the page.
Then: The hero shows the partner choice of one team or every team, and the chips "Any · RB · WR · TE · QB".
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-34: The analyzer shows the deadline eyebrow
App: site
Stories: 49
Given: The analyzer of `cpc`, at 09:55:00 Eastern on Sat 2026-11-21, then at 00:00:01 Eastern on Tue 2026-11-24.
When: The reader opens the page at each time.
Then: The hero eyebrow reads "Trade deadline ~2d 14h 05m", then "The trade deadline has passed".
Evidence: screenshots of the hero at each time at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-35: A chip sets the same limit as a typed question
App: site
Stories: 52
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker.
When: The reader taps the chip "RB" and taps "Find".
Then: The find request has `aim_position` "RB", the same value that the front door sends for "trade ideas for an RB".
Evidence: both request bodies, and screenshots of the hero with "RB" picked at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-36: The Finder wait shows the real steps in `StageLines`
App: site
Stories: 53, 54, 55, 57
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker and every team, against the local API.
When: The reader taps "Find".
Then: One line at a time shows each real step, such as "4 of 5 · Making a shortlist", and each line holds until the next step ends.
Evidence: the step events of the stream with times, the line text with times, the `StageLines` part in the DOM, and screenshots of two lines at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-37: The team avatars light up in turn
App: site
Stories: 56
Given: The Finder wait of AT-36.
When: The stream reports the teams read.
Then: The avatars light up one after another, in the order of the stream.
Evidence: the lit state of each avatar with times, and screenshots of the wait at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-38: The Finder trades show as cards with the Lean and a short Case
App: site
Stories: 58, 59, 60, 61, 62, 63
Given: The Finder result of AT-36.
When: The result lands.
Then: Up to 3 cards show in one list under the hero, each with a Lean of Send it, Lean yes, or Gut call, a Case of at most 3 lines, folded Bullets, and no headline.
Evidence: the find answer, and screenshots of the cards at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-39: A tap on a card opens the trade already graded
App: site
Stories: 64
Given: The Finder result of AT-36.
When: The reader taps the first card.
Then: The analyzer shows that trade in Grade mode with its read, and no analyze request goes out.
Evidence: the network log, and screenshots of the graded trade at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-40: A failed find shows Try Again
App: site
Stories: 66
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker, and the find route answers 500.
When: The reader taps "Find".
Then: The hero shows the error line and a "Try Again" button.
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-41: A press of the Finder takes about 25 s
App: api
Stories: 67, 68, 69
Given: The local API on the week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds (roster 6) and every team, three times.
Then: Each press ends in 30 s or less, with one pick call and no id retry.
Evidence: the command, the time of each press, the log lines of each step, and the cost.

AT-42: One picked partner skips the Partner filter
App: api
Stories: 70
Given: The local API on the week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds with Teehee (roster 12) as the partner.
Then: The log shows no Partner filter step, and the Shortlist holds 2 or more offers.
Evidence: the command, the log lines, and the Shortlist.

AT-43: The Shortlist has variety
App: api
Stories: 71
Given: The press of AT-41.
When: The evidence agent reads the Shortlist.
Then: No player of Bo Girds and no partner shows in a second offer before each other player and partner with an offer shows once.
Evidence: the Shortlist with the player and the partner of each offer.

AT-44: The Spares tree lists a player only with cover who can play now
App: pipeline
Stories: 72, 73, 74
Given: The week 11 rosters of `cpc`, and one test roster whose only backup at RB is Out.
When: The evidence agent runs the Spares tree tests.
Then: A starter at RB of the test roster is not listed, and each listed player in the run has a backup above the line who can play now.
Evidence: the test command and its output.

AT-45: A clear no stops, an unsure answer passes, and a failed call is an error
App: pipeline
Stories: 77, 78
Given: The Spares tree and the gain Noul with fixed Jev answers of 0.2, 0.5, and a failed call.
When: The evidence agent runs the decision tests.
Then: 0.2 stops, 0.5 passes, and the failed call raises an error, not a stop.
Evidence: the test command and its output.

AT-46: The two bad ideas never come back
App: api
Stories: 75, 76, 83
Given: The local API on the week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds and every team.
Then: Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is on the Shortlist or among the 3 trades.
Evidence: the command, the Shortlist, the 3 trades, and the gain Noul answers of any dropped offer.

AT-47: The backtest runs as one command and passes the bar
App: pipeline
Stories: 81, 82, 84, 85
Given: The Backtest marks that Brian made during the build, with the two marks of AT-46.
When: The evidence agent runs the backtest command.
Then: The output lists each mark with its result, and every mark is right.
Evidence: the command, its output, and the cost.

AT-48: A failed stream logs its cause
App: api
Stories: 86
Given: The local API, and a trade Topic stream that the client cuts after 5 s.
When: The stream fails.
Then: The API logs one line with the cause, the stage, and the seconds since the start.
Evidence: the command and the log line.

AT-49: The first call of a trade Topic does not fail
App: site
Stories: 87
Given: The front door of `cpc` against the deployed API of the spec branch, with Bo Girds as the team.
When: The reader asks for trade ideas 10 times, each in a fresh session with no cache.
Then: All 10 answers arrive with no retry line.
Evidence: the time and the result of each run, the API log of each run, and screenshots of one answer at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-50: The Lock is one value in the client config
App: site
Stories: 79
Given: The client config of `cpc`, with the Lock changed to 1 h after the fixed clock in a local build.
When: The reader opens the front door.
Then: The Deadline banner shows the last-hours state with "~1h 00m 00s".
Evidence: the config diff, and screenshots of the Deadline banner at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-51: The `finder` flag of CPC stays off
App: site
Stories: 80
Given: The spec branch at its merge commit.
When: The evidence agent reads the client config of `cpc`.
Then: The `finder` flag is `false`.
Evidence: the config line.

AT-52: No Deadline Board ships
App: site
Stories: none
Given: The `cpc` site built from the spec branch.
When: The reader opens `/deadline/` and `/deadline-board/`, and the evidence agent searches the build for a link to a board.
Then: Both pages answer 404, and no link to a Deadline Board exists.
Evidence: the two status codes and the search result.

AT-53: The Finder offers no three-team trade
App: site
Stories: none
Given: The analyzer of `cpc` in Find mode.
When: The reader looks for a team count.
Then: The hero has no choice of two or three teams.
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-54: Next.js stays at its version
App: site
Stories: none
Given: The spec branch at its merge commit.
When: The evidence agent compares the `next` version with `main`.
Then: The version is the same.
Evidence: the two version lines.

## Trace

Story 1: AT-1
Story 2: AT-1
Story 3: AT-1
Story 4: AT-2
Story 5: AT-3
Story 6: AT-3
Story 7: AT-4
Story 8: AT-5
Story 9: AT-6
Story 10: AT-6
Story 11: AT-7
Story 12: AT-5
Story 13: AT-1
Story 14: AT-8
Story 15: AT-9
Story 16: AT-9
Story 17: AT-10
Story 18: AT-11
Story 19: AT-12
Story 20: AT-1
Story 21: AT-1
Story 22: AT-5
Story 23: AT-14
Story 24: AT-13, AT-19
Story 25: AT-13
Story 26: AT-19
Story 27: AT-15, AT-20
Story 28: AT-20
Story 29: AT-21
Story 30: AT-22
Story 31: AT-22
Story 32: AT-23
Story 33: AT-24
Story 34: AT-25
Story 35: AT-14
Story 36: AT-18
Story 37: AT-26, AT-28
Story 38: AT-27
Story 39: AT-29
Story 40: AT-18
Story 41: AT-30
Story 42: AT-17
Story 43: AT-16
Story 44: AT-31
Story 45: AT-31
Story 46: AT-32
Story 47: AT-33
Story 48: AT-28
Story 49: AT-34
Story 50: AT-33
Story 51: AT-33
Story 52: AT-35
Story 53: AT-36
Story 54: AT-36
Story 55: AT-36
Story 56: AT-37
Story 57: AT-36
Story 58: AT-38
Story 59: AT-38
Story 60: AT-38
Story 61: AT-38
Story 62: AT-38
Story 63: AT-38
Story 64: AT-39
Story 65: no test. Reason: no real press of week 11 gives an empty result, and the empty line stays as the Finder has it now.
Story 66: AT-40
Story 67: AT-41
Story 68: AT-41
Story 69: AT-41
Story 70: AT-42
Story 71: AT-43
Story 72: AT-44
Story 73: AT-44
Story 74: AT-44
Story 75: AT-46
Story 76: AT-46
Story 77: AT-45
Story 78: AT-45
Story 79: AT-50
Story 80: AT-51
Story 81: AT-47
Story 82: AT-47
Story 83: AT-46
Story 84: AT-47
Story 85: AT-47
Story 86: AT-48
Story 87: AT-49
Story 88: AT-12
Out of scope "The Deadline Board": AT-52
Out of scope "A Finder for three-team trades": AT-53
Out of scope "The upgrade of Next.js": AT-54
Out of scope "A season history in the Trade Wire": AT-14
Out of scope "The Trade Wire on the front door": no test. Reason: AT-1 and AT-5 show the Trade Wire only in the sheet.
Out of scope "A push alert", "Norcal", "A theme for the whole site", "A stream of Finder results per partner", "A prewarm of the Finder cache", "The Accept tree", "A change to YES_AT or NO_AT": no test. Reason: no ticket builds near them, and AT-11 and AT-47 cover Norcal and the thresholds.

## Revisions

None yet.
