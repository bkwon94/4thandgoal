# Trades closed: acceptance tests

Spec: `.scratch/trades-closed/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The Lock of client `cpc` is 00:00 Eastern on Tue 2026-11-24. The Lock of client `norcal` is 00:00 Eastern on Tue 2026-12-15. Each site build of a test is made on the day of the run, so the evidence must be recorded before 2026-12-15. A fixed clock in a unit test or in the browser is a test input, not a mock mode of the app.

The API tests use the local evidence API of the branch, never a deploy to Fly. The data is real: client `cpc` and client `norcal`, season 2026.

The site tests run in WebKit. Screenshots are at 375, 768, and 1280 px, each in the light theme and the dark theme (ADR 0006). Each site test also runs `devices["iPhone 15"]` at 390 by 660 and asserts no horizontal scroll and no overlap of two text boxes. That result is "the iPhone 15 check result".

## Tests

AT-1: The menu has no Trade Analyzer
App: site
Stories: 1, 2
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. The front door at `/`.
When: The reader opens the menu sheet.
Then: The menu lists no item named "Trade Analyzer".
Evidence: screenshots of the open menu sheet at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-2: The home tools have no analyzer row
App: site
Stories: 1, 3
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader reads the generated registry of the build.
Then: The home tools of the registry hold no analyzer row, and the import of `@/app/_routes/analyzer/home` is absent.
Evidence: the lines of the generated registry that list the home tools.

AT-3: The closed page at /analyze/
App: site
Stories: 1, 4, 7, 30
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader opens `/analyze/`.
Then: The page shows the top band, the line "The trade deadline has passed. Trades open again next season.", and one link to Home with the href `/`.
Evidence: screenshots of `/analyze/` at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-4: A prefill link gives the closed page
App: site
Stories: 5
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader opens `/analyze/?team=3&with=6&give=5045&get=8151`.
Then: The page shows the line "The trade deadline has passed. Trades open again next season." and no trade form.
Evidence: screenshots of the page at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-5: A Finder link gives the closed page
App: site
Stories: 6
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader opens `/analyze/?mode=find`.
Then: The page shows the line "The trade deadline has passed. Trades open again next season." and no switch "Grade a trade · Find a trade".
Evidence: screenshots of the page at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-6: The front door offers no trade Topic
App: site
Stories: 8
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. The front door at `/`, with roster 1 chosen on the team sheet.
When: The reader opens More.
Then: No chip and no Suggestion reads "Trades", "Check", or "Sell high or buy low", and no trade block strip shows.
Evidence: screenshots of the front door with More open at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-7: A typed trade question gets the closed line
App: site and API
Stories: 9, 10
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. The local evidence API of the branch serves `cpc`. Roster 1 is chosen.
When: The reader types "Who should I trade for at RB?" and sends it.
Then: The answer reads "The trade deadline has passed. Trades open again next season.", and it never reads "I can't answer that."
Evidence: the API log line of the route of the question, which shows the closed line from code and no Claude call, and screenshots of the answer at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-8: The Site answer lists no analyzer line
App: site and API
Stories: 11
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. The local evidence API serves `cpc`.
When: The reader asks "What can this site do?"
Then: The answer lists no line "Grades a trade between two or more teams."
Evidence: the text of the answer, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-9: The Tour names no trade
App: site
Stories: 12
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. A browser with no Tour seen.
When: The reader steps through the Tour to its step about the ask box.
Then: The line of that step names no trade. It does not contain the word "trade".
Evidence: the text of each Tour step, and screenshots of the ask box step at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-10: No Deadline banner after the Lock
App: site
Stories: 13
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader opens `/`, `/rankings/`, and `/analyze/`.
Then: No page shows the Deadline banner, and no page has a button named "Open the Trade Wire".
Evidence: screenshots of each of the three pages at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-11: The weekly trade cards stay
App: site
Stories: 14
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader opens the week 10 page, `/2026/week-10/`.
Then: The page shows each trade card of week 10, the same count as `clients/cpc/published/2026/week-10/page.json` holds.
Evidence: screenshots of the trades chapter of week 10 at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result. Also the count of trade cards on the page and in the file.

AT-12: The recent trades Topic stays
App: site
Stories: 15
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. The front door at `/`, with roster 1 chosen.
When: The reader opens the Topic "Position leaders and recent trades".
Then: The Answer shows the position leaders and the recent trades of 2026.
Evidence: screenshots of the Answer at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-13: The transaction history stays
App: site
Stories: 16
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock.
When: The reader opens the manager page of roster 1 at `/2026/managers/`, the moves part.
Then: The moves part shows the count of 2 trades, as `managers.json` holds for roster 1.
Evidence: screenshots of the moves part at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-14: Each trade route refuses after the Lock
App: API
Stories: 17, 18
Given: The local evidence API of the branch serves `cpc`, on the day of the run, after the CPC Lock.
When: The evidence agent calls each route under `/clients/cpc/`: `POST /analyze`, `POST /find`, `POST /trade-check`, `POST /trade-ideas`, `POST /find-stream`, `POST /sell-high`, and `GET /deadline/trades`, each with a valid body.
Then: Each call returns HTTP 410 with the body `{"closed": true, "line": "The trade deadline has passed. Trades open again next season."}`.
Evidence: the command and the status and body of each call.

AT-15: A page from before the close shows the closed line
App: site and API
Stories: 17
Given: An analyzer page of a `cpc` build with a Lock in the future, served by the evidence agent. The local evidence API of the branch serves `cpc` after the real Lock.
When: The reader picks a valid trade of roster 1 and presses Grade the Trade.
Then: The analyzer shows the line "The trade deadline has passed. Trades open again next season." in place of a grade.
Evidence: screenshots of the analyzer after the press at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-16: A refused call costs nothing
App: API
Stories: 18
Given: The API test client with a fake Jev and a fake Claude that count each call, and the `cpc` values with a Lock in the past.
When: The test calls each of the 7 trade routes of AT-14.
Then: The fake Jev and the fake Claude count 0 calls.
Evidence: the pytest command and its output, with the test names.

AT-17: The fair warm-up skips a closed client
App: API
Stories: 19
Given: The local evidence API of the branch, started with the warm-up on, after the CPC Lock.
When: The evidence agent reads the log of the first 2 minutes after the start.
Then: The log has no line "Fair warm-up of cpc started".
Evidence: the start command and the log of the first 2 minutes.

AT-18: Suggestions make no trade fact
App: API
Stories: 20
Given: The local evidence API of the branch serves `cpc`, after the CPC Lock.
When: The evidence agent calls `POST /clients/cpc/suggestions` for roster 1.
Then: The answer holds no Topic `trade_ideas`, `trade_check`, or `sell_high`, and no fact of `trade_ideas` or `sell_high`.
Evidence: the command and the full answer.

AT-19: NorCal keeps its trade tools
App: site
Stories: 23
Given: The site build of `norcal`, made on the day of the run, before the NorCal Lock.
When: The reader opens the menu sheet, then `/analyze/`.
Then: The menu lists "Trade Analyzer", and `/analyze/` shows the trade form with the switch "Grade a trade · Find a trade".
Evidence: screenshots of the menu and `/analyze/` at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-20: NorCal shows no Deadline banner
App: site
Stories: 24, 25
Given: The site build of `norcal`, made on the day of the run.
When: The reader opens `/` and `/rankings/`.
Then: No page shows the Deadline banner.
Evidence: screenshots of each page at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-21: A NorCal trade route answers before its Lock
App: API
Stories: 23
Given: The API test client with the `norcal` values, the clock at 12:00 Eastern on Mon 2026-12-14.
When: The test calls `POST /clients/norcal/trade-check` with a valid body.
Then: The call does not return 410, and the stream holds a grade.
Evidence: the pytest command and its output.

AT-22: NorCal closes at its Lock
App: API
Stories: 22
Given: The API test client with the `norcal` values, the clock at 00:00:01 Eastern on Tue 2026-12-15.
When: The test calls `POST /clients/norcal/trade-check` with a valid body.
Then: The call returns HTTP 410 with the line "The trade deadline has passed. Trades open again next season.".
Evidence: the pytest command and its output.

AT-23: A client with no lock is never closed
App: site and API
Stories: 26
Given: A client values file with no `lock`.
When: The test asks Trades closed at the times 2026-11-24 12:00 Eastern and 2027-06-01 12:00 Eastern, in each app.
Then: Each app answers not closed for both times.
Evidence: the bun test and pytest commands and their output.

AT-24: The client values hold the Lock and the Deadline week
App: site and API
Stories: 21, 22, 25
Given: The `client.toml` files on the Spec branch.
When: The reader reads `[values.analyzer]` of `clients/norcal/client.toml` and of `clients/cpc/client.toml`.
Then: NorCal holds `lock = "2026-12-15T00:00:00-05:00"` and no `deadline_week`. CPC holds its `lock` and `deadline_week = true`.
Evidence: the `[values.analyzer]` table of each file.

AT-25: The trade code stays
App: site
Stories: 27
Given: The `cpc` values with `lock` changed to `2027-11-23T00:00:00-05:00` in a scratch copy, not committed.
When: The evidence agent builds the site of `cpc` and opens `/analyze/`.
Then: `/analyze/` shows the trade form, and the menu lists "Trade Analyzer".
Evidence: the build command, and screenshots of `/analyze/` at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-26: The build decides, not the browser
App: site
Stories: 28
Given: The site build of `cpc`, made on the day of the run, after the CPC Lock. The browser clock is set to 20:00 Eastern on Mon 2026-11-23, before the Lock.
When: The reader opens `/analyze/`.
Then: The page still shows the line "The trade deadline has passed. Trades open again next season.", and the menu lists no "Trade Analyzer".
Evidence: screenshots of `/analyze/` at 375, 768, and 1280 px, each in the light theme and the dark theme, and the iPhone 15 check result.

AT-27: The eggs stay as they are
App: site and API
Stories: none
Given: The diff of the Spec branch against `main`.
When: The reader lists the changed files.
Then: No changed file is under `packages/eggs/`, and the CPC egg store is not touched.
Evidence: `git diff --stat main...trades-closed`.

## Trace

Story 1: AT-1 to AT-10
Story 2: AT-1
Story 3: AT-2
Story 4: AT-3
Story 5: AT-4
Story 6: AT-5
Story 7: AT-3
Story 8: AT-6
Story 9: AT-7
Story 10: AT-7
Story 11: AT-8
Story 12: AT-9
Story 13: AT-10
Story 14: AT-11
Story 15: AT-12
Story 16: AT-13
Story 17: AT-14, AT-15
Story 18: AT-14, AT-16
Story 19: AT-17
Story 20: AT-18
Story 21: AT-24
Story 22: AT-22, AT-24
Story 23: AT-19, AT-21
Story 24: AT-20
Story 25: AT-20, AT-24
Story 26: AT-23
Story 27: AT-25
Story 28: AT-26
Story 29: no test. Reason: the Tuesday weekly build already exists, and AT-26 shows that the build decides.
Story 30: AT-3
Out of scope "The eggs": AT-27
Out of scope "A delete of the trade code": AT-25
Out of scope "A browser check of the Lock": AT-26
Out of scope "A NorCal Deadline week": AT-20
Out of scope "A change to the trade history": AT-11, AT-12, AT-13

## Revisions

None yet.
