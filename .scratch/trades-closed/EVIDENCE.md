# Trades closed: evidence

Spec: `.scratch/trades-closed/PRD.md`. Acceptance tests: `.scratch/trades-closed/ACCEPTANCE.md`.
Built from: `c477cb22`, on 2026-11-24. AT-11, AT-12, AT-15, and AT-19 come from `c477cb22`. The other tests come from `ad1c9015`. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 10 min for 14 site tests.

Smoke run: `Smoke run: 7 flows, 7 passed, 0 failed` (`evidence/smoke/`). The smoke run ran at `d146d4ea`. The two later commits, `8996b109` and `ad1c9015`, change test files only.

The background full check ran before this stage. Every member is green at `ad1c9015`. No test covers it.

No rebuild list: the spec changes no pipeline output.

How each file was made: `evidence/scripts/setup.txt`. The runner round output is `evidence/round-output.txt`, and the log of its local API is `evidence/round-api.log.txt`. The runner takes Chromium shots, with the Desktop Chrome device of `apps/site/playwright.config.ts`. The iPhone 15 check, the text facts, and the shots that no runner verb covers come from a Playwright WebKit run in a detached scratch worktree of `ad1c9015`. The AT-15 shots come from `agent-browser` (Chromium). Each build is made on 2026-11-24, before the NorCal Lock. No call went to Fly.

## AT-1: The menu has no Trade Analyzer

App: site
Then: The menu lists no item named "Trade Analyzer".
Files: `evidence/AT-1/375-dark.png`, `evidence/AT-1/375-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/iphone-390x660.txt`, `evidence/AT-1/iphone-390x660-light.png`, `evidence/AT-1/menu-text.txt`, `evidence/AT-1/steps.json`
Observation: The open menu sheet at 375 and 768 px lists Home, Week 10, Past weeks, Power Rankings, Season Sim, Managers, and Show the tour, with no "Trade Analyzer"; at 1280 px the top band nav lists Home, Week 10, Power Rankings, Season Sim, and Managers. `menu-text.txt` gives the same links of the sheet at 390x660. The iPhone 15 check gives no horizontal scroll and no overlap of two text boxes.

## AT-2: The home tools have no analyzer row

App: site
Then: The home tools of the registry hold no analyzer row, and the import of `@/app/_routes/analyzer/home` is absent.
Files: `evidence/AT-2/registry.txt`
Observation: The generated registry of a cpc build made today with the real clock lists `homeTools: HomeTool[] = [managersHomeTool]`, and `grep -c "@/app/_routes/analyzer/home"` gives 0. The client values of that build hold `"tradesClosed": true`.

## AT-3: The closed page at /analyze/

App: site
Then: The page shows the top band, the line "The trade deadline has passed. Trades open again next season.", and one link to Home with the href `/`.
Files: `evidence/AT-3/375-dark.png`, `evidence/AT-3/375-light.png`, `evidence/AT-3/768-dark.png`, `evidence/AT-3/768-light.png`, `evidence/AT-3/1280-dark.png`, `evidence/AT-3/1280-light.png`, `evidence/AT-3/dom.txt`, `evidence/AT-3/iphone-390x660.txt`, `evidence/AT-3/iphone-390x660-light.png`, `evidence/AT-3/steps.json`
Observation: Each shot of `/analyze/` shows the top band, then one card with the line "The trade deadline has passed. Trades open again next season." and one "Home" button. `dom.txt` reads the DOM of the closed cpc page at 375 and 1280 px: main holds 1 link, named Home, with the href `/`, and the line is a visible `h1`. The accessibility snapshot in `dom.txt` lists main with that heading and one link "Home". The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-4: A prefill link gives the closed page

App: site
Then: The page shows the line "The trade deadline has passed. Trades open again next season." and no trade form.
Files: `evidence/AT-4/375-dark.png`, `evidence/AT-4/375-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/768-light.png`, `evidence/AT-4/1280-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/iphone-390x660.txt`, `evidence/AT-4/iphone-390x660-light.png`, `evidence/AT-4/steps.json`
Observation: Each shot of the prefill link shows the same closed card with the line and the Home button, and no trade form. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-5: A Finder link gives the closed page

App: site
Then: The page shows the line "The trade deadline has passed. Trades open again next season." and no switch "Grade a trade · Find a trade".
Files: `evidence/AT-5/375-dark.png`, `evidence/AT-5/375-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/768-light.png`, `evidence/AT-5/1280-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/iphone-390x660.txt`, `evidence/AT-5/iphone-390x660-light.png`, `evidence/AT-5/steps.json`
Observation: Each shot of `/analyze/?mode=find` shows the same closed card, and no switch "Grade a trade · Find a trade". The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-6: The front door offers no trade Topic

App: site
Then: No chip and no Suggestion reads "Trades", "Check", or "Sell high or buy low", and no trade block strip shows.
Files: `evidence/AT-6/375-dark.png`, `evidence/AT-6/375-light.png`, `evidence/AT-6/768-dark.png`, `evidence/AT-6/768-light.png`, `evidence/AT-6/1280-dark.png`, `evidence/AT-6/1280-light.png`, `evidence/AT-6/iphone-390x660.txt`, `evidence/AT-6/iphone-390x660-light.png`, `evidence/AT-6/steps.json`, `evidence/AT-6/topics-text.txt`
Observation: With The Blue Tent (roster 1) chosen and More open, the list "All Topics" holds Week recap, Your last matchup, Your next matchup, Power rankings, Playoff race, Your season, Position leaders and recent trades, Waiver targets, How you stack up, Weak spots, and Start or sit. `topics-text.txt` gives a trade block strip count of 0 and no match of "Trades", "Check", or "Sell high or buy low" in the Thread text. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-7: A typed trade question gets the closed line

App: site and API
Then: The answer reads "The trade deadline has passed. Trades open again next season.", and it never reads "I can't answer that."
Files: `evidence/AT-7/375-dark.png`, `evidence/AT-7/375-light.png`, `evidence/AT-7/768-dark.png`, `evidence/AT-7/768-light.png`, `evidence/AT-7/1280-dark.png`, `evidence/AT-7/1280-light.png`, `evidence/AT-7/answer-text.txt`, `evidence/AT-7/api-log.txt`, `evidence/AT-7/iphone-390x660.txt`, `evidence/AT-7/iphone-390x660-light.png`, `evidence/AT-7/steps.json`, `evidence/round-api.log.txt`
Observation: Each shot shows the question "Who should I trade for at RB?" and the answer "The trade deadline has passed. Trades open again next season.", with no "I can't answer that." `api-log.txt` shows 6 lines "A trade question stopped at the Lock, with no Claude call" before the 6 `POST /clients/cpc/ask` lines of AT-7, and the round API log has 0 calls to api.anthropic.com. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-8: The Site answer lists no analyzer line

App: site and API
Then: The answer lists no line "Grades a trade between two or more teams."
Files: `evidence/AT-8/375-dark.png`, `evidence/AT-8/375-light.png`, `evidence/AT-8/768-dark.png`, `evidence/AT-8/768-light.png`, `evidence/AT-8/1280-dark.png`, `evidence/AT-8/1280-light.png`, `evidence/AT-8/answer-text.txt`, `evidence/AT-8/iphone-390x660.txt`, `evidence/AT-8/iphone-390x660-light.png`, `evidence/AT-8/steps.json`
Observation: The answer reads "The site has 1 tool and 4 pages to read.", with the tool Season Sim and the pages Week 10, Power Rankings, Managers, and Midseason Report. `answer-text.txt` holds the whole Thread text, and it has no line "Grades a trade between two or more teams.". The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-9: The Tour names no trade

App: site
Then: The line of that step names no trade. It does not contain the word "trade".
Files: `evidence/AT-9/375-dark.png`, `evidence/AT-9/375-light.png`, `evidence/AT-9/768-dark.png`, `evidence/AT-9/768-light.png`, `evidence/AT-9/1280-dark.png`, `evidence/AT-9/1280-light.png`, `evidence/AT-9/iphone-390x660.txt`, `evidence/AT-9/iphone-390x660-light.png`, `evidence/AT-9/steps.json`, `evidence/AT-9/tour-text.txt`
Observation: The shots show the Tour step "Ask", 2 of 4: "Type any question about your team or your league, such as start or sit or the playoff race.". `tour-text.txt` gives the 4 steps: Suggestions, Ask, Your team, and Menu, and no step contains the word "trade". The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-10: No Deadline banner after the Lock

App: site
Then: No page shows the Deadline banner, and no page has a button named "Open the Trade Wire".
Files: `evidence/AT-10/analyze-375-dark.png`, `evidence/AT-10/analyze-375-light.png`, `evidence/AT-10/analyze-768-dark.png`, `evidence/AT-10/analyze-768-light.png`, `evidence/AT-10/analyze-1280-dark.png`, `evidence/AT-10/analyze-1280-light.png`, `evidence/AT-10/counts.txt`, `evidence/AT-10/home-375-dark.png`, `evidence/AT-10/home-375-light.png`, `evidence/AT-10/home-768-dark.png`, `evidence/AT-10/home-768-light.png`, `evidence/AT-10/home-1280-dark.png`, `evidence/AT-10/home-1280-light.png`, `evidence/AT-10/home-iphone-390x660-light.png`, `evidence/AT-10/iphone-390x660.txt`, `evidence/AT-10/rankings-375-dark.png`, `evidence/AT-10/rankings-375-light.png`, `evidence/AT-10/rankings-768-dark.png`, `evidence/AT-10/rankings-768-light.png`, `evidence/AT-10/rankings-1280-dark.png`, `evidence/AT-10/rankings-1280-light.png`, `evidence/AT-10/rankings-iphone-390x660-light.png`, `evidence/AT-10/steps.json`, `evidence/AT-3/` (the iPhone 15 check of `/analyze/`)
Observation: The home and rankings shots come from the runner; the `/analyze/` shots come from the scratch WebKit run (`analyze-*.png`), because no runner verb opens a second route with no link to it. No shot shows a Deadline banner. `counts.txt` gives `deadlineBanner` 0 and `tradeWireButtons` 0 on `/`, `/rankings/`, and `/analyze/`. The iPhone 15 check of `/` and `/rankings/` gives no horizontal scroll and no overlap; the `/analyze/` page has its check in AT-3.

## AT-11: The weekly trade cards stay

App: site
Then: The page shows each trade card of week 9, the same count as `clients/cpc/published/2026/week-09/page.json` holds.
Files: `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/counts.txt`, `evidence/AT-11/iphone-390x660.txt`, `evidence/AT-11/iphone-390x660-light.png`, `evidence/AT-11/steps.json`, `evidence/round-output-2.txt`
Observation: `clients/cpc/published/2026/week-09/page.json` holds 2 trades, and the week 9 page shows the Trades chapter with the note "2 this week" and 2 trade cards: NFC Least with Return of T Mac, and London Cooking with behold the lamb. `counts.txt` gives 2 cards on the page and 2 in the file for week 9, and the same match for weeks 6, 7, 8, and 10 (5, 2, 1, 0). The iPhone 15 check of week 9 gives no horizontal scroll and no overlap.

## AT-12: The recent trades Topic stays

App: site
Then: The Answer shows the position leaders of 2026, the same as on `main`.
Files: `evidence/AT-12/375-dark.png`, `evidence/AT-12/375-light.png`, `evidence/AT-12/768-dark.png`, `evidence/AT-12/768-light.png`, `evidence/AT-12/1280-dark.png`, `evidence/AT-12/1280-light.png`, `evidence/AT-12/answer-text.txt`, `evidence/AT-12/iphone-390x660.txt`, `evidence/AT-12/iphone-390x660-light.png`, `evidence/AT-12/main-compare.txt`, `evidence/AT-12/steps.json`, `evidence/round-output-2.txt`
Observation: The Answer of "Position leaders and recent trades" shows the leaders QB Patrick Mahomes, RB Christian McCaffrey, WR George Pickens, TE Isaiah Likely, and DEF Minnesota Vikings, a paragraph about them, and "Read the full report". `answer-text.txt` holds the Thread text of the Spec branch build and of a build of `main` at the merge base `671e9f24`, each with its own local API, and gives "the same: true". `main-compare.txt` gives no diff of `topics.py` or of the week 10 `topics.json` between the two commits, and says that `main` after the merge base adds the Week 11 report. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-13: The transaction history stays

App: site
Then: The moves part shows the count of 2 trades, as `managers.json` holds for roster 1.
Files: `evidence/AT-13/375-dark.png`, `evidence/AT-13/375-light.png`, `evidence/AT-13/768-dark.png`, `evidence/AT-13/768-light.png`, `evidence/AT-13/1280-dark.png`, `evidence/AT-13/1280-light.png`, `evidence/AT-13/iphone-390x660.txt`, `evidence/AT-13/iphone-390x660-light.png`, `evidence/AT-13/moves-text.txt`, `evidence/AT-13/steps.json`
Observation: The page `/2026/managers/1/` of The Blue Tent shows the Moves part with Adds 27, Drops 26, and Trades 2, and the two trade cards "Trade With Lil Fridge" and "Trade With To Infinity and Bijan". `moves-text.txt` gives "MOVES | ADDS | 27 | DROPS | 26 | TRADES | 2", and `managers.json` holds `"trades": 2` for roster 1. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-14: Each trade route refuses after the Lock

App: API
Then: Each call returns HTTP 410 with the body `{"closed": true, "line": "The trade deadline has passed. Trades open again next season."}`.
Files: `evidence/AT-14/output.txt`
Observation: Each of the 7 calls, `POST /analyze`, `/find`, `/trade-check`, `/trade-ideas`, `/find-stream`, `/sell-high`, and `GET /deadline/trades` under `/clients/cpc/`, returns HTTP status 410 with the body `{"closed":true,"line":"The trade deadline has passed. Trades open again next season."}`.

## AT-15: A page from before the close shows the closed line

App: site and API
Then: The analyzer shows the line "The trade deadline has passed. Trades open again next season." in place of a grade.
Files: `evidence/AT-15/375-dark.png`, `evidence/AT-15/375-light.png`, `evidence/AT-15/768-dark.png`, `evidence/AT-15/768-light.png`, `evidence/AT-15/1280-dark.png`, `evidence/AT-15/1280-light.png`, `evidence/AT-15/after-iphone-390x660-light.png`, `evidence/AT-15/api-log.txt`, `evidence/AT-15/iphone-390x660.txt`, `evidence/AT-15/steps.txt`
Observation: The build with `BUILD_NOW=2026-11-21T09:55:00-05:00` at `c477cb22` holds `"tradesClosed": false` and `"deadlineWeek": true`, so `/analyze/` shows the trade form. After The Blue Tent gets Stefon Diggs, Lil Fridge gets Bucky Irving, and the press of Grade the Trade, each shot shows the error box "The trade deadline has passed. Trades open again next season." with Try Again, and no grade. `api-log.txt` shows each press as `POST /clients/cpc/analyze` with 410 Gone. The hero eyebrow reads "THE TRADE DEADLINE HAS PASSED", and `steps.txt` logs that line for each run. The iPhone 15 check gives no horizontal scroll, and it reports one overlap: the fixed button "Grade the Trade" over the text "Stefon Diggs" at the scroll position of the check.

## AT-16: A refused call costs nothing

App: API
Then: The fake Jev and the fake Claude count 0 calls.
Files: `evidence/AT-16/output.txt`
Observation: The command runs `test_a_refused_call_makes_no_jev_call_and_no_claude_call` and exits 0. The test calls the 7 routes of AT-14 with the clock after the CPC Lock, and asserts `jev.requests == []` and `counts.claude() == 0`.

## AT-17: The fair warm-up skips a closed client

App: API
Then: The log has no line "Fair warm-up of cpc started".
Files: `evidence/AT-17/output.txt`
Observation: The log of the first 120 s after the start has no line "Fair warm-up of cpc started" and no line with "Fair warm-up" at all; `grep -c` gives 0. It shows the start, "Application startup complete.", and the Sleeper reads of both leagues. `WARM_SLUGS = ("cpc",)` is the list of clients that the warm-up warms.

## AT-18: Suggestions make no trade fact

App: API
Then: The answer holds no Topic `trade_ideas`, `trade_check`, or `sell_high`, and no fact of `trade_ideas` or `sell_high`.
Files: `evidence/AT-18/output.txt`
Observation: The call returns HTTP status 200. `picks` holds weak_spots, stack_up, and waiver_targets; `facts` and `lifts` hold no `trade_ideas`, `trade_check`, or `sell_high` key; the only trade-named key is `leaders_trades`, which is the league Topic of AT-12.

## AT-19: NorCal keeps its trade tools

App: site
Then: The menu lists "Trade Analyzer", and `/analyze/` shows the trade form with the switch "Grade a trade · Find a trade".
Files: `evidence/AT-19/analyze-375-dark.png`, `evidence/AT-19/analyze-375-light.png`, `evidence/AT-19/analyze-768-dark.png`, `evidence/AT-19/analyze-768-light.png`, `evidence/AT-19/analyze-1280-dark.png`, `evidence/AT-19/analyze-1280-light.png`, `evidence/AT-19/analyze-iphone-390x660-light.png`, `evidence/AT-19/analyze-text.txt`, `evidence/AT-19/iphone-390x660.txt`, `evidence/AT-19/menu-375-dark.png`, `evidence/AT-19/menu-375-light.png`, `evidence/AT-19/menu-768-dark.png`, `evidence/AT-19/menu-768-light.png`, `evidence/AT-19/menu-1280-dark.png`, `evidence/AT-19/menu-1280-light.png`, `evidence/AT-19/menu-iphone-390x660-light.png`, `evidence/AT-19/menu-text.txt`, `evidence/AT-19/steps.json`, `evidence/round-output-2.txt`, `evidence/round3-api.log.txt`
Observation: The norcal menu at 375 and 768 px and the top band nav at 1280 px list "Trade Analyzer", and `menu-text.txt` gives "Trade Analyzer / Check a trade". The `/analyze/` shots at `c477cb22` show the hero eyebrow "TRADE ANALYZER", the switch "Grade a trade · Find a trade", the teams loaded with Your Team Bo Girds, and Grade the Trade, with no error line. `analyze-text.txt` gives the same switch, one Grade the Trade button, and false for "The API did not answer" and for "Loading the teams". `round3-api.log.txt` shows each `GET /clients/norcal/teams?season=2026` with 200 OK. The iPhone 15 check gives no horizontal scroll; at the "analyze" shot it reports one overlap, the fixed button "Grade the Trade" over the heading "Team Two gets".

## AT-20: NorCal shows no Deadline banner

App: site
Then: No page shows the Deadline banner.
Files: `evidence/AT-20/counts.txt`, `evidence/AT-20/home-375-dark.png`, `evidence/AT-20/home-375-light.png`, `evidence/AT-20/home-768-dark.png`, `evidence/AT-20/home-768-light.png`, `evidence/AT-20/home-1280-dark.png`, `evidence/AT-20/home-1280-light.png`, `evidence/AT-20/home-iphone-390x660-light.png`, `evidence/AT-20/iphone-390x660.txt`, `evidence/AT-20/rankings-375-dark.png`, `evidence/AT-20/rankings-375-light.png`, `evidence/AT-20/rankings-768-dark.png`, `evidence/AT-20/rankings-768-light.png`, `evidence/AT-20/rankings-1280-dark.png`, `evidence/AT-20/rankings-1280-light.png`, `evidence/AT-20/rankings-iphone-390x660-light.png`, `evidence/AT-20/steps.json`
Observation: No shot of the norcal `/` and `/rankings/` shows a Deadline banner. `counts.txt` gives `deadlineBanner` 0 and `tradeWireButtons` 0 on both pages. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-21: A NorCal trade route answers before its Lock

App: API
Then: The call does not return 410, and the stream holds a grade.
Files: `evidence/AT-21/output.txt`
Observation: The command runs `test_the_norcal_trade_check_still_grades_the_day_before_its_lock` and exits 0. The test sets the clock to 12:00 Eastern on 2026-12-14 and asserts status 200 and a `data-answer` part of kind `check`.

## AT-22: NorCal closes at its Lock

App: API
Then: The call returns HTTP 410 with the line "The trade deadline has passed. Trades open again next season.".
Files: `evidence/AT-22/output.txt`
Observation: The command runs `test_the_norcal_trade_check_is_410_one_second_after_its_lock` and exits 0. The test sets the clock to 00:00:01 Eastern on 2026-12-15 and asserts status 410 and the closed body.

## AT-23: A client with no lock is never closed

App: site and API
Then: Each app answers not closed for both times.
Files: `evidence/AT-23/output.txt`
Observation: The site test "is never closed for a client with no Lock (AT-23)" asserts `tradesClosed(null, ...)` is false at 2026-11-24 12:00 Eastern and 2027-06-01 12:00 Eastern; the client-build test asserts `tradesClosed` false for a client.toml with no lock. The API test `test_a_client_with_no_lock_is_never_closed` asserts not closed at the same two times. Each command exits 0.

## AT-24: The client values hold the Lock and the Deadline week

App: site and API
Then: NorCal holds `lock = "2026-12-15T00:00:00-05:00"` and no `deadline_week`. CPC holds its `lock` and `deadline_week = true`.
Files: `evidence/AT-24/output.txt`
Observation: NorCal `[values.analyzer]` holds `finder = true` and `lock = "2026-12-15T00:00:00-05:00"`, and no `deadline_week`. CPC holds `finder = true`, `lock = "2026-11-24T00:00:00-05:00"`, and `deadline_week = true`.

## AT-25: The trade code stays

App: site
Then: `/analyze/` shows the trade form, and the menu lists "Trade Analyzer".
Files: `evidence/AT-25/analyze-375-dark.png`, `evidence/AT-25/analyze-375-light.png`, `evidence/AT-25/analyze-768-dark.png`, `evidence/AT-25/analyze-768-light.png`, `evidence/AT-25/analyze-1280-dark.png`, `evidence/AT-25/analyze-1280-light.png`, `evidence/AT-25/build.txt`, `evidence/AT-25/menu-375-dark.png`, `evidence/AT-25/menu-375-light.png`, `evidence/AT-25/menu-768-dark.png`, `evidence/AT-25/menu-768-light.png`, `evidence/AT-25/menu-1280-dark.png`, `evidence/AT-25/menu-1280-light.png`
Observation: With `lock = "2027-11-23T00:00:00-05:00"` in the scratch copy, the build holds `"tradesClosed": false` and the analyzer imports in the registry. The `/analyze/` shots show the Deadline banner strip, the trade form, and the switch "Grade a trade · Find a trade". The menu shots at 375 and 768 px show the sheet with "Trade Analyzer / Check a trade" as the current page; at 1280 px the top band nav shows "Trade Analyzer".

## AT-26: The build decides, not the browser

App: site
Then: The page still shows the line "The trade deadline has passed. Trades open again next season.", and the menu lists no "Trade Analyzer".
Files: `evidence/AT-26/analyze-375-dark.png`, `evidence/AT-26/analyze-375-light.png`, `evidence/AT-26/analyze-768-dark.png`, `evidence/AT-26/analyze-768-light.png`, `evidence/AT-26/analyze-1280-dark.png`, `evidence/AT-26/analyze-1280-light.png`, `evidence/AT-26/analyze-iphone-390x660-light.png`, `evidence/AT-26/check-trades-closed.txt`, `evidence/AT-26/iphone-390x660.txt`, `evidence/AT-26/menu-375-dark.png`, `evidence/AT-26/menu-375-light.png`, `evidence/AT-26/menu-768-dark.png`, `evidence/AT-26/menu-768-light.png`, `evidence/AT-26/menu-1280-dark.png`, `evidence/AT-26/menu-1280-light.png`, `evidence/AT-26/menu-iphone-390x660-light.png`, `evidence/AT-26/sizes.txt`
Observation: The browser clock is fixed at 20:00 Eastern on Mon 2026-11-23, and `sizes.txt` gives "Mon Nov 23 2026 20:00:00 GMT-0500" in each page. Each `analyze-*.png` shows the closed line and the Home button; the `menu-*.png` shots at 375 and 768 px show the sheet with Home, Week 10, Past weeks, Power Rankings, Season Sim, and Managers, and the 1280 px shots show the same items in the top band, with no "Trade Analyzer". `check-trades-closed.txt` holds the e2e run of the spec, with the AT-26 test in it. The iPhone 15 check gives no horizontal scroll and no overlap.

## AT-27: The eggs stay as they are

App: site and API
Then: No changed file is under `packages/eggs/`, and the CPC egg store is not touched.
Files: `evidence/AT-27/output.txt`
Observation: The diff has 77 changed files. No path is under `packages/eggs/`, and no path contains "eggs".

