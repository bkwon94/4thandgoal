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
Stories: 53, 54, 55, 109
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker and every team, against the local API.
When: The reader taps "Find".
Then: One line at a time shows each real step with the counts of the press, such as "3 of 5 · Checking 9,412 trades for fairness". Each step line stays on screen at least about 1.5 s and holds until the next step starts, and step 5 changes its line as AT-73 says.
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
Stories: 59, 60, 61, 62, 63
Given: The Finder result of AT-36.
When: The result lands.
Then: Up to 5 cards show in one list under the hero, each with a Lean of Send it, Lean yes, or Gut call, a Case of at most 3 lines, folded Bullets, and no headline.
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

AT-41: A press runs one pick call with no id retry
App: api
Stories: 68
Given: The local API on the week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds (roster 6) and every team, three times.
Then: Each press runs one pick call, and no id retry line shows in the log.
Evidence: the command, the log lines of each step, and the cost.

AT-42: Retired. One picked partner skips the Partner filter
Retired: the Spares tree gates no partner, and the targets step is gone (decisions 15 and 16).
App: api
Stories: 70
Given: The local API on the week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds with Teehee (roster 12) as the partner.
Then: The log shows no Partner filter step, and the targets build 2 or more offers before the gain check.
Evidence: the command, the log lines, and the Shortlist.

AT-43: The Shortlist has variety
App: api
Stories: 101, 102
Given: The press of AT-41.
When: The evidence agent reads the Shortlist.
Then: The best offer of each shape direction comes first, then the best offer of each partner, then the best offer of each player of Bo Girds, before a second form of any trade.
Evidence: the Shortlist with the shape direction, the partner, the players, and the fair mean of each offer.

AT-44: The Spares tree lists a player only with cover who can play now
App: pipeline
Stories: 72, 73, 74
Given: The week 11 rosters of `cpc`, and one test roster whose only backup at RB is Out.
When: The evidence agent runs the Spares tree tests.
Then: A starter at RB of the test roster is not listed, and each listed player in the run has a backup above the line who can play now.
Evidence: the test command and its output.

AT-45: A clear no stops, an unsure answer passes, and a failed call is an error
App: pipeline
Stories: 77, 78, 97
Given: The fair mean and the gain Noul with fixed Jev answers of 0.2, 0.5, and a failed call.
When: The evidence agent runs the decision tests.
Then: 0.2 drops the offer, 0.5 keeps it, and the failed call raises an error, not a drop.
Evidence: the test command and its output.

AT-46: The two bad ideas never come back
App: api
Stories: 75, 76, 83, 98
Given: The local API on the week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds and every team.
Then: Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is among the 5 trades, and "Kenneth Walker III for Patrick Mahomes" is not on the Shortlist.
Evidence: the command, the Shortlist, the 5 trades, and the gain Noul answers of any dropped offer.

AT-47: The backtest runs as one command and passes the bar
App: pipeline
Stories: 81, 82, 84, 85
Given: The Backtest marks that Brian made during the build, with the two marks of AT-46.
When: The evidence agent runs the backtest command.
Then: The output lists each mark with its result, and the count of right marks is the baseline of 1 of 5 or more.
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
Given: The front door of `cpc` against one fresh local evidence API of the spec branch, with Bo Girds as the team.
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

AT-55: The Value offers hold every shape in both directions
App: api
Stories: 89, 90, 91
Given: The local API on the 2026 week 11 snapshot of `cpc`.
When: The evidence agent runs one press for Bo Girds (roster 6) and every team.
Then: The Value offers include all 7 shape directions: 1-for-1, 2-for-1, 1-for-2, 3-for-1, 1-for-3, 3-for-2, and 2-for-3.
Evidence: the command, and the count of Value offers per shape direction from the log.

AT-56: Each Value offer is inside the band with its direction
App: api
Stories: 92, 93
Given: The press of AT-55.
When: The evidence agent checks the trade value sums of each Value offer.
Then: On each uneven offer, the side that gets more players has 100% to 125% of the other sum, and each 1-for-1 is within 10% either way.
Evidence: the command, the count of offers checked, and the count outside the band, which is 0.

AT-57: No filler and no player without a chart value
App: api
Stories: 94
Given: The press of AT-55.
When: The evidence agent checks the players of each Value offer.
Then: No player under 5 trade value sits on a side of 2 or 3 players, and Justin Herbert is in no Value offer.
Evidence: the command, the lowest trade value on a side of 2 or 3 players, and the search for Justin Herbert.

AT-58: The fair check reads the chart facts in both side orders
App: pipeline
Stories: 95, 96, 97
Given: The week 11 rosters of `cpc`, with Jev answers fixed in the test.
When: The evidence agent runs the fair step tests.
Then: Each fair request holds `chart_value` and `chart_sum`, answers of 0.2 and 0.3 drop the offer, and answers of 0.1 and 0.6 keep it.
Evidence: the test command and its output, and one fair request payload.

AT-59: A need answer drops no offer
App: pipeline
Stories: 99
Given: The week 11 rosters of `cpc`, with Jev answers fixed in the test.
When: The evidence agent runs the step 2 tests with need answers of 0.1 on both sides and a gain of 0.8.
Then: The offer stays on the Shortlist.
Evidence: the test command and its output.

AT-60: Step 2 gets the best 3 offers of each group
App: api
Stories: 101, 102
Given: The press of AT-55.
When: The evidence agent reads the offers that reach step 2.
Then: Step 2 holds at most 3 offers per partner and shape direction, no more than 231 offers, and each has one of the 3 highest fair means of its group.
Evidence: the command, and the step 2 offers with their group and fair mean.

AT-61: A Spares tree yes is a fact, not a gate
App: pipeline
Stories: 100
Given: The week 11 rosters of `cpc`, with Jev answers fixed in the test.
When: The evidence agent runs the Spares tree fact test, with a "yes" for a QB that Bo Girds gets in one Value offer.
Then: That offer gets the fact "fills the weak slot QB, and the partner can spare him", and the count of offers stays the same.
Evidence: the test command and its output.

AT-62: The Shortlist order follows the fair answer
App: pipeline
Stories: 102
Given: The week 11 rosters of `cpc`, with Jev answers fixed in the test.
When: The evidence agent runs the `varied()` tests.
Then: After the best offers, the rest follow by the fair mean, highest first.
Evidence: the test command and its output.

AT-63: A large partner splits under the 64k context
App: pipeline
Stories: 112
Given: The week 11 rosters of `cpc`, with Jev answers fixed in the test.
When: The evidence agent runs the request test with one partner of 1,200 offers.
Then: The partner sends 3 or more requests, each under 64,000 tokens by the estimate, and no offer passes as unsure.
Evidence: the test command and its output.

AT-64: Two presses share one pacer
App: pipeline
Stories: 112
Given: One API process with a fixed clock, and two presses of 300,000 tokens each.
When: The evidence agent runs the pacer test with both presses at once.
Then: No second holds more than 100,000 tokens across both presses.
Evidence: the test command and its output.

AT-65: The trade card is the Ledger
App: site
Stories: 104, 105, 106, 108
Given: The Finder result of AT-36, with cards of three different shapes, such as a 1-for-2, a 1-for-3, and a 3-for-2.
When: The result lands.
Then: Each card shows "You get · N" and "You give · N" columns, each player row shows the position, the NFL team, and the rank with no trade value, and a total shows under each column.
Evidence: the find answer, and screenshots of the three cards at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-66: The card states the gap in plain words
App: site
Stories: 107
Given: A card whose totals are 68.0 for "You get" and 62.5 for "You give".
When: The card renders.
Then: The card shows "You get 9% more trade value" under the totals.
Evidence: the test command and its output, and screenshots of the card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-67: Five picks, with the near ideas folded
App: site
Stories: 103
Given: The Finder result of AT-36.
When: The result lands.
Then: Up to 5 cards show, then "Close, but not sent · N", folded, with up to 3 near ideas under it.
Evidence: the find answer, and screenshots of the list with the fold closed and open at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-68: The wait states no time
App: site
Stories: 110
Given: The analyzer of `cpc` in Find mode.
When: The reader taps "Find".
Then: The hero shows no "This can take about 25 seconds." and no other count of seconds or minutes.
Evidence: the text of the hero during the wait, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-69: An anchor and a limit hold on every Value offer
App: api
Stories: 111
Given: The local API on the 2026 week 11 snapshot of `cpc`.
When: The evidence agent runs a press for Bo Girds around Trey McBride, then a press with an aim of RB.
Then: Each Value offer of the first press holds Trey McBride, and each Value offer of the second press brings Bo Girds an RB.
Evidence: the commands, and the Value offers of each press.

AT-70: The picks spread across shapes and partners
App: api
Stories: 89, 101
Given: The press of AT-55.
When: The evidence agent reads the 5 picks.
Then: The picks hold at least 2 shapes and at least 3 partners.
Evidence: the command, and the 5 picks with the shape and the partner of each.

AT-71: No request sends the long-context header
App: api
Stories: none
Given: The press of AT-55.
When: The evidence agent reads the Jev requests of the press.
Then: No request sends the header `TypeSafe-Danger-Zone-Long-Context`.
Evidence: the command, and the headers of the Jev requests from the log or a search of the code.

AT-72: Each trade card shows as soon as it is ready
App: both
Stories: 113
Given: The analyzer of `cpc` in Find mode, with Bo Girds as the asker and every team, against the local API.
When: The reader taps "Find".
Then: The first trade card shows before the last one, each card shows one at a time as the stream sends it, and a line under the cards counts the trades still to come until the last card shows.
Evidence: the trade events of the stream with times, the time each card shows in the DOM, and screenshots after the first card and after the last card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-73: Step 5 names the trades it weighs
App: site
Stories: 114
Given: The press of AT-72.
When: The wait reaches step 5.
Then: While the pick runs, step 5 changes its line about every 3 s, and each line names a real trade of the Shortlist of the press by its players. A press whose pick runs 15 s or more after step 5 starts shows at least 3 such lines. A faster pick shows fewer, and no card waits for a line.
Evidence: the Shortlist of the press, the line text with times, and screenshots of two step 5 lines at 375 px in the light theme and the dark theme.

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
Story 57: no test. Reason: replaced by story 109 (AT-36).
Story 58: no test. Reason: replaced by story 103 (AT-67).
Story 59: AT-38
Story 60: AT-38
Story 61: AT-38
Story 62: AT-38
Story 63: AT-38
Story 64: AT-39
Story 65: no test. Reason: no real press of week 11 gives an empty result, and the empty line stays as the Finder has it now.
Story 66: AT-40
Story 67: no test. Reason: replaced by story 110 (AT-68).
Story 68: AT-41
Story 69: no test. Reason: replaced by story 103 (AT-67).
Story 70: no test. Reason: replaced by stories 89 to 91; AT-42 is retired.
Story 71: no test. Reason: replaced by stories 101 and 102 (AT-43).
Story 72: no test. Reason: replaced by story 99 (AT-59).
Story 73: no test. Reason: replaced by story 100 (AT-61). AT-44 still checks the list.
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
Story 89: AT-55, AT-70
Story 90: AT-55
Story 91: AT-55
Story 92: AT-56
Story 93: AT-56
Story 94: AT-57
Story 95: AT-58
Story 96: AT-58
Story 97: AT-45, AT-58
Story 98: AT-46
Story 99: AT-59
Story 100: AT-61
Story 101: AT-43, AT-60, AT-70
Story 102: AT-43, AT-60, AT-62
Story 103: AT-67
Story 104: AT-65
Story 105: AT-65
Story 106: AT-65
Story 107: AT-66
Story 108: AT-65
Story 109: AT-36
Story 110: AT-68
Story 111: AT-69
Story 112: AT-63, AT-64
Story 113: AT-72
Story 114: AT-73
Out of scope "The long-context header of TypeSafe": AT-71
Out of scope "A trade value on each player row of a card": AT-65
Out of scope "A cap on the count of trades after the Value screen": AT-60
Out of scope "A second Fly machine for the API", "The cause of the 29 pool players with no week 11 chart value": no test. Reason: no ticket builds near them.
Out of scope "The Deadline Board": AT-52
Out of scope "A Finder for three-team trades": AT-53
Out of scope "The upgrade of Next.js": AT-54
Out of scope "A season history in the Trade Wire": AT-14
Out of scope "The Trade Wire on the front door": no test. Reason: AT-1 and AT-5 show the Trade Wire only in the sheet.
Out of scope "A push alert", "Norcal", "A theme for the whole site", "A stream of Finder results per partner", "The Accept tree", "A change to YES_AT or NO_AT": no test. Reason: no ticket builds near them, and AT-11 and AT-47 cover Norcal and the thresholds.

## Revisions

- 2026-11-19: Brian approved the tests of the fair-first Finder (decisions 13 to 17). AT-36, AT-38, AT-41, AT-43, AT-45, and AT-46 changed. AT-42 is retired. AT-55 to AT-71 are new. AT-41 lost its 30 s limit, because it is a time claim.
- 2026-11-20: Brian approved four changes. AT-60 counts the 3 best offers of each group, up to 231. AT-65 needs three different shapes, not a 1-for-1 and a 2-for-1, because the gain check drops every 1-for-1, 2-for-1, and 3-for-1 offer of Bo Girds. AT-36 holds each step line at least about 1.5 s. AT-72 and AT-73 are new (decision 20). The prewarm left Out of scope (decision 19).
- 2026-11-20: Brian approved two changes after the first Judge round. AT-49 runs on one fresh local evidence API, because no unmerged branch deploys to Fly for evidence. AT-73 asks for 3 lines only when the pick runs 15 s or more, because a fast pick must not wait for a line.
