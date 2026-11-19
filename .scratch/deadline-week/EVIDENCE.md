# Deadline week: evidence

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests: `.scratch/deadline-week/ACCEPTANCE.md`.
Built from: `19371052` and `0807c881`, on 2026-11-19. Each entry names its commit. The commits between them (`4c4b3384`, `391c6f46`, `c067e04e`, and two merges) change no product code: three README files, the smoke flows `.claude/skills/verify/flows.json`, `apps/site/e2e/smoke-rules.spec.ts`, and the AT-43 Then line in `ACCEPTANCE.md`. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: no runner round. The agent instrument ran in parts: 7 min for 21 site tests on `19371052`, 9 min for 19 site tests on `0807c881`, and 7 min for 7 of the 10 fresh asks of AT-49 after a fix of the instrument (the first 3 asks ran with a 4 min wait each). 38 site tests have shots.

Smoke run on `0807c881`: `Smoke run: 7 flows, 7 passed, 0 failed`. Folder: `evidence/smoke/`.
Rebuild: `REBUILD.md` lists no value, and `evidence/rebuild.log` (run on `19371052`, base `main` at `8780eefb`) shows `rebuild diff: 0 diffs, 0 listed, 0 not listed, 0 listed but not changed`. The commits after it change no pipeline code.

The instrument of the site tests. The evidence runner has no verb for a fixed clock or for a served answer of the Trade Wire route, and nearly every site test needs both. So the site tests use one Playwright file of the agent, `evidence/instrument/zz-deadline-evidence.spec.mjs` (the agent ran it from `apps/site/e2e/` and did not commit it there). It runs WebKit, sets the browser clock of each test with `page.clock`, serves trade W from `evidence/fixtures/` through a Playwright route where the test says so, and sends every other call to a real local API (`make -C apps/api api-evidence` with a fresh result cache). The export is served by `evidence/instrument/serve.mjs`, which answers a missing path with `404.html` and the status 404. Each site test writes its measures to `measure.jsonl` and its shots as `<name>-<width>-<theme>.png` at a viewport height of 900, and most write `iphone-15-390x660.json` from `devices["iPhone 15"]` at 390 by 660. The builds with the `finder` flag on (AT-18, AT-26 flag-on, AT-28, AT-29, AT-31 to AT-33, AT-35 to AT-40, AT-53) and with the Lock moved (AT-50) changed `clients/cpc/client.toml` in a local build only, and the file is back as committed (`evidence/AT-51/output.txt`).

Trade W: Sleeper leg 9 of cpc 2026, transaction `1424578776058155008`. NFC Least (roster 4) gets Tetairoa McMillan WR, Makai Lemon WR, Seth McGowan RB, and Chase Brown RB. Return of T Mac (roster 8) gets Rome Odunze WR, CeeDee Lamb WR, Jordan Mason RB, and $5 of FAAB. The recorded answer is `evidence/AT-13/sleeper-leg-9.json`. Week 11 of cpc on the day of the run holds no trade: Sleeper leg 11 has 10 transactions, each `free_agent` and `complete` (`evidence/AT-14/sleeper-leg-11.json`). So the tests that need a week 11 trade use trade W, as `ACCEPTANCE.md` says. The other trade of leg 9, `1425209111854747648` (Puka Deez... and behold the lamb), is the second real trade of AT-19 and AT-20.

## AT-1: The Deadline banner shows the countdown

App: site
Commit: `19371052`
Then: Under the top band, the Deadline banner shows "TRADE DEADLINE" over "~2d 14h 05m".
Files: `evidence/AT-1/iphone-15-390x660.json`, `evidence/AT-1/measure.jsonl`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/375-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/768-light.png`
Observation: At 09:55:00 Eastern on Sat 2026-11-21, each of the 6 shots shows the Deadline banner under the top band with "TRADE DEADLINE" over "~2d 14h 05m" (measure.jsonl: eyebrow and countdown text). The iPhone 15 check at 390 by 660 reads a sideways scroll of 0, the band row bottom at 60 and the banner top at 60, and no overlap.

## AT-2: The countdown ticks

App: site
Commit: `19371052`
Then: The countdown reads "~2d 14h 04m".
Files: `evidence/AT-2/iphone-15-390x660.json`, `evidence/AT-2/measure.jsonl`, `evidence/AT-2/after-1280-dark.png`, `evidence/AT-2/after-1280-light.png`, `evidence/AT-2/after-375-dark.png`, `evidence/AT-2/after-375-light.png`, `evidence/AT-2/after-768-dark.png`, `evidence/AT-2/after-768-light.png`
Observation: In each of the 6 runs the countdown reads "~2d 14h 05m" before and "~2d 14h 04m" after the fake clock moves on 60000 ms (measure.jsonl). The shots are taken after the move.

## AT-3: The last hours show seconds on the accent fill

App: site
Commit: `19371052`
Then: The Deadline banner has the accent fill and reads "~2h 41m 10s".
Files: `evidence/AT-3/iphone-15-390x660.json`, `evidence/AT-3/measure.jsonl`, `evidence/AT-3/1280-dark.png`, `evidence/AT-3/1280-light.png`, `evidence/AT-3/375-dark.png`, `evidence/AT-3/375-light.png`, `evidence/AT-3/768-dark.png`, `evidence/AT-3/768-light.png`
Observation: At 21:18:50 Eastern on Mon 2026-11-23 the countdown reads "~2h 41m 10s", `data-phase` is `last-hours`, and the computed background of the banner button, rgb(184, 52, 42), equals the computed `--color-accent` in both themes (measure.jsonl). The shots show the red fill with seconds.

## AT-4: Reduced motion stops the shimmer

App: site
Commit: `19371052`
Then: No element of the Deadline banner has a running animation.
Files: `evidence/AT-4/iphone-15-390x660.json`, `evidence/AT-4/measure.jsonl`, `evidence/AT-4/1280-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/375-dark.png`, `evidence/AT-4/375-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/768-light.png`
Observation: With `prefers-reduced-motion: reduce` (true in the page) at 21:18:50 Eastern on Mon 2026-11-23, `getAnimations({ subtree: true })` on the banner gives an empty list at each size and theme, so 0 animations run (measure.jsonl).

## AT-5: The whole Deadline banner opens the Trade Wire

App: site
Commit: `19371052`
Then: The Trade Wire sheet opens, and the Deadline banner is one button named "Open the Trade Wire, N new trades", where N is the count of week 11 trades.
Files: `evidence/AT-5/imports.txt`, `evidence/AT-5/iphone-15-390x660.json`, `evidence/AT-5/measure.jsonl`, `evidence/AT-5/1280-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/375-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/768-light.png`
Observation: On `/rankings/` with trade W served as the one week 11 trade, the banner holds one `BUTTON` with `aria-haspopup=dialog` and the name "Open the Trade Wire, 1 new trade" (singular for N = 1). A tap on `[data-deadline-countdown]` opens the Trade Wire dialog in each shot (measure.jsonl). `imports.txt` shows `deadline-banner.tsx` and `wire-sheet.tsx` import the sheet parts from `@cpc/design/ui/sheet`, and only `packages/design/site/ui/sheet.tsx` imports `@ui-sdk/react/drawer`.

## AT-6: The badge counts the trades of week 11

App: site
Commit: `19371052`
Then: The badge reads "N new" for N week 11 trades, or shows no badge when N is 0.
Files: `evidence/AT-6/iphone-15-390x660.json`, `evidence/AT-6/measure.jsonl`, `evidence/AT-6/1280-dark.png`, `evidence/AT-6/1280-light.png`, `evidence/AT-6/375-dark.png`, `evidence/AT-6/375-light.png`, `evidence/AT-6/768-dark.png`, `evidence/AT-6/768-light.png`
Observation: Against the real Trade Wire route of the local API (no served answer), the route answers 200 with leg 11 and 0 trades, the banner has no `[data-deadline-badge]` element, and its name is "Open the Trade Wire, 0 new trades" at each size and theme (measure.jsonl). Real week 11 holds no trade, so the shots show no badge.

## AT-7: The Deadline banner sinks on a press

App: site
Commit: `19371052`
Then: The content of the Deadline banner scales to 0.98 over 150 ms.
Files: `evidence/AT-7/iphone-15-390x660.json`, `evidence/AT-7/measure.jsonl`, `evidence/AT-7/press-1280-dark.png`, `evidence/AT-7/press-1280-light.png`, `evidence/AT-7/press-375-dark.png`, `evidence/AT-7/press-375-light.png`, `evidence/AT-7/press-768-dark.png`, `evidence/AT-7/press-768-light.png`
Observation: At rest `[data-deadline-grid]` has `scale: none`. 400 ms into a held mouse press it has `scale: 0.98`, `transition-duration: 0.15s`, and `transition-timing-function: cubic-bezier(0.23, 1, 0.32, 1)` at each size and theme (measure.jsonl). The shots are taken during the press.

## AT-8: The Deadline banner has even padding and one left edge

App: site
Commit: `19371052`
Then: The top padding and the bottom padding of the Deadline banner differ by 1 px or less, and "TRADE DEADLINE" and the countdown start at the same x.
Files: `evidence/AT-8/iphone-15-390x660.json`, `evidence/AT-8/measure.jsonl`, `evidence/AT-8/1280-dark.png`, `evidence/AT-8/1280-light.png`, `evidence/AT-8/375-dark.png`, `evidence/AT-8/375-light.png`, `evidence/AT-8/768-dark.png`, `evidence/AT-8/768-light.png`
Observation: At each size and theme the top padding and the bottom padding are each 8 px (difference 0), and the eyebrow and the countdown both start at x 32 (difference 0) (measure.jsonl).

## AT-9: The Deadline banner says the trade deadline has passed

App: site
Commit: `19371052`
Then: The Deadline banner reads "The trade deadline has passed. Good luck in the playoffs." and the badge reads "Final".
Files: `evidence/AT-9/iphone-15-390x660.json`, `evidence/AT-9/measure.jsonl`, `evidence/AT-9/1280-dark.png`, `evidence/AT-9/1280-light.png`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/375-light.png`, `evidence/AT-9/768-dark.png`, `evidence/AT-9/768-light.png`
Observation: At 00:00:01 Eastern on Tue 2026-11-24 the banner text is "The trade deadline has passed. Good luck in the playoffs.", then "Trade Wire" and "Final" (measure.jsonl `bannerText`; the instrument looked for `[data-deadline-badge]`, which is not the element of "Final"). The button name is "Open the Trade Wire, final. The trade deadline has passed." The shots show the closed state.

## AT-10: Deadline week ends by itself

App: site
Commit: `19371052`
Then: Neither page shows the Deadline banner or the deadline eyebrow.
Files: `evidence/AT-10/iphone-15-390x660.json`, `evidence/AT-10/measure.jsonl`, `evidence/AT-10/analyzer-1280-dark.png`, `evidence/AT-10/analyzer-1280-light.png`, `evidence/AT-10/analyzer-375-dark.png`, `evidence/AT-10/analyzer-375-light.png`, `evidence/AT-10/analyzer-768-dark.png`, `evidence/AT-10/analyzer-768-light.png`, `evidence/AT-10/front-door-1280-dark.png`, `evidence/AT-10/front-door-1280-light.png`, `evidence/AT-10/front-door-375-dark.png`, `evidence/AT-10/front-door-375-light.png`, `evidence/AT-10/front-door-768-dark.png`, `evidence/AT-10/front-door-768-light.png`
Observation: At 00:00:01 Eastern on Wed 2026-11-25 the front door and `/analyze/` each have 0 banner elements and no text "trade deadline"; the analyzer hero eyebrow reads "TRADE ANALYZER" (measure.jsonl). The shots `front-door-*` and `analyzer-*` show the top of each page.

## AT-11: Norcal has no Deadline week

App: site
Commit: `0807c881`
Then: The page shows no Deadline banner.
Files: `evidence/AT-11/iphone-15-390x660.json`, `evidence/AT-11/measure.jsonl`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`
Observation: On the norcal export (title "NorCal Apex 6") at 09:55:00 Eastern on Sat 2026-11-21, each size and theme has 0 banner elements and no text "trade deadline" (measure.jsonl). The iPhone 15 check reads `bannerPresent: false`.

## AT-12: The copy uses plain words

App: site
Commit: `19371052 (shipped config) and 0807c881 (finder flag on)`
Then: No text holds "Lock", "Rosters are locked", "Deadline Board", "feed", "Jev", "Advisor", "Finder", or "Brian".
Files: `evidence/AT-12/search.txt`, `evidence/AT-12/text-analyzer-closed.txt`, `evidence/AT-12/text-analyzer-find-flag-on-closed.txt`, `evidence/AT-12/text-analyzer-find-flag-on-last-hours.txt`, `evidence/AT-12/text-analyzer-find-flag-on-open.txt`, `evidence/AT-12/text-analyzer-last-hours.txt`, `evidence/AT-12/text-analyzer-open.txt`, `evidence/AT-12/text-front-door-closed.txt`, `evidence/AT-12/text-front-door-last-hours.txt`, `evidence/AT-12/text-front-door-open.txt`, `evidence/AT-12/text-sheet-closed.txt`, `evidence/AT-12/text-sheet-find-flag-on-closed.txt`, `evidence/AT-12/text-sheet-find-flag-on-last-hours.txt`, `evidence/AT-12/text-sheet-find-flag-on-open.txt`, `evidence/AT-12/text-sheet-last-hours.txt`, `evidence/AT-12/text-sheet-open.txt`, `evidence/AT-12/analyzer-closed-1280-dark.png`, `evidence/AT-12/analyzer-closed-1280-light.png`, `evidence/AT-12/analyzer-closed-375-dark.png`, `evidence/AT-12/analyzer-closed-375-light.png`, `evidence/AT-12/analyzer-closed-768-dark.png`, `evidence/AT-12/analyzer-closed-768-light.png`, `evidence/AT-12/analyzer-find-flag-on-closed-375-light.png`, `evidence/AT-12/analyzer-find-flag-on-last-hours-375-light.png`, `evidence/AT-12/analyzer-find-flag-on-open-375-light.png`, `evidence/AT-12/analyzer-last-hours-1280-dark.png`, `evidence/AT-12/analyzer-last-hours-1280-light.png`, `evidence/AT-12/analyzer-last-hours-375-dark.png`, `evidence/AT-12/analyzer-last-hours-375-light.png`, `evidence/AT-12/analyzer-last-hours-768-dark.png`, `evidence/AT-12/analyzer-last-hours-768-light.png`, `evidence/AT-12/analyzer-open-1280-dark.png`, `evidence/AT-12/analyzer-open-1280-light.png`, `evidence/AT-12/analyzer-open-375-dark.png`, `evidence/AT-12/analyzer-open-375-light.png`, `evidence/AT-12/analyzer-open-768-dark.png`, `evidence/AT-12/analyzer-open-768-light.png`, `evidence/AT-12/front-door-closed-1280-dark.png`, `evidence/AT-12/front-door-closed-1280-light.png`, `evidence/AT-12/front-door-closed-375-dark.png`, `evidence/AT-12/front-door-closed-375-light.png`, `evidence/AT-12/front-door-closed-768-dark.png`, `evidence/AT-12/front-door-closed-768-light.png`, `evidence/AT-12/front-door-last-hours-1280-dark.png`, `evidence/AT-12/front-door-last-hours-1280-light.png`, `evidence/AT-12/front-door-last-hours-375-dark.png`, `evidence/AT-12/front-door-last-hours-375-light.png`, `evidence/AT-12/front-door-last-hours-768-dark.png`, `evidence/AT-12/front-door-last-hours-768-light.png`, `evidence/AT-12/front-door-open-1280-dark.png`, `evidence/AT-12/front-door-open-1280-light.png`, `evidence/AT-12/front-door-open-375-dark.png`, `evidence/AT-12/front-door-open-375-light.png`, `evidence/AT-12/front-door-open-768-dark.png`, `evidence/AT-12/front-door-open-768-light.png`, `evidence/AT-12/sheet-closed-1280-dark.png`, `evidence/AT-12/sheet-closed-1280-light.png`, `evidence/AT-12/sheet-closed-375-dark.png`, `evidence/AT-12/sheet-closed-375-light.png`, `evidence/AT-12/sheet-closed-768-dark.png`, `evidence/AT-12/sheet-closed-768-light.png`, `evidence/AT-12/sheet-find-flag-on-closed-375-light.png`, `evidence/AT-12/sheet-find-flag-on-last-hours-375-light.png`, `evidence/AT-12/sheet-find-flag-on-open-375-light.png`, `evidence/AT-12/sheet-last-hours-1280-dark.png`, `evidence/AT-12/sheet-last-hours-1280-light.png`, `evidence/AT-12/sheet-last-hours-375-dark.png`, `evidence/AT-12/sheet-last-hours-375-light.png`, `evidence/AT-12/sheet-last-hours-768-dark.png`, `evidence/AT-12/sheet-last-hours-768-light.png`, `evidence/AT-12/sheet-open-1280-dark.png`, `evidence/AT-12/sheet-open-1280-light.png`, `evidence/AT-12/sheet-open-375-dark.png`, `evidence/AT-12/sheet-open-375-light.png`, `evidence/AT-12/sheet-open-768-dark.png`, `evidence/AT-12/sheet-open-768-light.png`
Observation: `search.txt` lists 15 text dumps: the front door, the open Trade Wire sheet, and the analyzer at the three times on `19371052`, and the analyzer in Find mode and the sheet with the flag on at the three times on `0807c881`. Each dump holds `body.innerText` plus every aria-label, alt, title, and placeholder, and each has 0 hits of Lock, Rosters are locked, Deadline Board, feed, Jev, Advisor, Finder, or Brian (case as written). The shots cover the shipped pages at 3 sizes and 2 themes, and the flag-on pages at 375 light.

## AT-13: The Trade Wire route reads a trade in full

App: api
Commit: `19371052`
Then: Trade W shows both teams with name and avatar, the players each team gets with positions, $5 of FAAB to roster 8, and no draft picks.
Files: `evidence/AT-13/api.log`, `evidence/AT-13/output.txt`, `evidence/AT-13/sleeper-leg-9.json`, `evidence/AT-13/wire_leg9.py.txt`
Observation: The real API app, with only its Trade Wire read pinned to Sleeper leg 9 (`wire_leg9.py.txt`), answers `leg: 9` with 2 trades. Trade W shows NFC Least (roster 4) and Return of T Mac (roster 8), each with a name and an avatar URL, the players each team gets with positions, `faab: 5` for roster 8 and 0 for roster 4, and no key for draft picks (output.txt). The Sleeper answer of W has `waiver_budget` [{amount 5, sender 4, receiver 8}] and `draft_picks` [] (sleeper-leg-9.json).

## AT-14: The Trade Wire lists only accepted week 11 trades, newest first

App: api
Commit: `19371052`
Then: Each trade in the answer has leg 11 and status `complete`, in descending order of acceptance time, and no week 9 trade shows.
Files: `evidence/AT-14/api.log`, `evidence/AT-14/output.txt`, `evidence/AT-14/sleeper-leg-11.json`, `evidence/AT-14/sleeper-state.txt`
Observation: Sleeper state gives leg 11, and the raw leg 11 answer holds 10 transactions, all `free_agent`, so no trade (sleeper-leg-11.json). The route answers `leg: 11` and `trades: []` (output.txt), so no week 9 trade shows; with no trade in the list, the order of acceptance has nothing to show.

## AT-15: The Trade Wire route keeps its answer for 5 s

App: api
Commit: `19371052`
Then: The log shows one Sleeper read for the first two calls and a second Sleeper read for the call at 6 s.
Files: `evidence/AT-15/output.txt`
Observation: The call at 0.33 s logs two Sleeper reads (`state/nfl` and `transactions/11?t=...`). The call at 2.20 s logs no Sleeper read. The call at 6.21 s logs the two reads again (output.txt, with the httpx log lines).

## AT-16: The Trade Wire route needs the passphrase

App: api
Commit: `19371052`
Then: The route answers 401 with no trades.
Files: `evidence/AT-16/output.txt`
Observation: A call with no passphrase header answers `HTTP/1.1 401 Unauthorized` with `content-length: 0` (output.txt).

## AT-17: The Trade Wire route takes many phones on one IP

App: api
Commit: `19371052`
Then: All 40 calls answer 200.
Files: `evidence/AT-17/control.txt`, `evidence/AT-17/output.txt`
Observation: With `CORNERSTONE_RATE_LIMIT_PER_MINUTE=30`, 40 calls from 127.0.0.1 in 58 s all answer 200 (output.txt). On the same API, 35 quick calls of the counted teams route answer 200 thirty times, then 429 five times, so the limit is live (control.txt).

## AT-18: The sheet holds the parts in order

App: site
Commit: `0807c881`
Then: From the top, the sheet shows "Grade a trade" and "Find a trade", "TRADE DEADLINE ~2d 14h 05m", "Trade Wire", the live dot with "Updated", and trade W.
Files: `evidence/AT-18/iphone-15-390x660.json`, `evidence/AT-18/measure.jsonl`, `evidence/AT-18/1280-dark.png`, `evidence/AT-18/1280-light.png`, `evidence/AT-18/375-dark.png`, `evidence/AT-18/375-light.png`, `evidence/AT-18/768-dark.png`, `evidence/AT-18/768-light.png`
Observation: With the flag on and trade W served, the DOM order and the top of each part inside the sheet are: "Grade a trade" and "Find a trade" (index 3 and 4, side by side), the eyebrow "Trade deadline ~2d 14h 05m" (index 6, shown upper case), "Trade Wire" (8), the live dot with "Updated 0s ago" (9), and trade W (14), each lower on the screen than the one before (measure.jsonl).

## AT-19: The Trade Wire rows have even gaps

App: site
Commit: `19371052`
Then: Inside each trade the gaps are 8 px, and the gaps between trades are equal, each within 1 px.
Files: `evidence/AT-19/iphone-15-390x660.json`, `evidence/AT-19/measure.jsonl`, `evidence/AT-19/1280-dark.png`, `evidence/AT-19/1280-light.png`, `evidence/AT-19/375-dark.png`, `evidence/AT-19/375-light.png`, `evidence/AT-19/768-dark.png`, `evidence/AT-19/768-light.png`
Observation: With trade W and the other real leg 9 trade served, each trade has 3 rows with gaps of 8 px and 8 px at each size and theme. The one gap between the two trades is 33 px (16 px pad, 1 px rule, 16 px pad), and the first line sits 16 px under the top rule (measure.jsonl). With two trades there is one gap between trades, so no second gap to compare.

## AT-20: A new trade slides in

App: site
Commit: `19371052`
Then: Within 15 s, trade W shows at the top and the badge changes from "1 new" to "2 new".
Files: `evidence/AT-20/iphone-15-390x660.json`, `evidence/AT-20/measure.jsonl`, `evidence/AT-20/after-1280-dark.png`, `evidence/AT-20/after-1280-light.png`, `evidence/AT-20/after-375-dark.png`, `evidence/AT-20/after-375-light.png`, `evidence/AT-20/after-768-dark.png`, `evidence/AT-20/after-768-light.png`, `evidence/AT-20/before-1280-dark.png`, `evidence/AT-20/before-1280-light.png`, `evidence/AT-20/before-375-dark.png`, `evidence/AT-20/before-375-light.png`, `evidence/AT-20/before-768-dark.png`, `evidence/AT-20/before-768-light.png`
Observation: The route first serves the other trade (badge "1 new"), then serves W and the other trade. Trade W shows at the top 8.48 to 8.54 s after the route change at each size and theme, and the badge reads "2 new" (measure.jsonl: `secondsToShow`, `badgeBefore`, `badgeAfter`, `orderAfter`, route calls with times). The `before` and `after` shots show the change.

## AT-21: The Trade Wire shows when it last updated

App: site
Commit: `0807c881`
Then: The sheet shows the live dot and "Updated 3s ago".
Files: `evidence/AT-21/iphone-15-390x660.json`, `evidence/AT-21/measure.jsonl`, `evidence/AT-21/1280-dark.png`, `evidence/AT-21/1280-light.png`, `evidence/AT-21/375-dark.png`, `evidence/AT-21/375-light.png`, `evidence/AT-21/768-dark.png`, `evidence/AT-21/768-light.png`
Observation: The page samples the live line each 100 ms across a poll, timed by the page clock from the first "Updated 0s ago". "Updated 3s ago" first shows at 3.51 to 3.63 s, and at 3.0 s the line still reads "Updated 2s ago" at each size and theme; "1s" first shows at about 1.5 s (measure.jsonl `firstSampleOf`). The live dot is present (1 element). The line ticks on its own 1 s timer, which does not start at the read.

## AT-22: The poll stops when the tab hides and runs when it shows

App: site
Commit: `19371052`
Then: No route call goes out while the tab hides, and one goes out within 1 s of the show.
Files: `evidence/AT-22/network-log.json`
Observation: Route calls go out at -12.6 s and -2.52 s before the hide, none in the 30 s while the tab is hidden, and one at 0.01 s after the show (network-log.json). The tab hides by an override of `document.visibilityState` and a `visibilitychange` event.

## AT-23: The empty Trade Wire says so

App: site
Commit: `19371052`
Then: The sheet reads "No trades yet this week."
Files: `evidence/AT-23/iphone-15-390x660.json`, `evidence/AT-23/measure.jsonl`, `evidence/AT-23/1280-dark.png`, `evidence/AT-23/1280-light.png`, `evidence/AT-23/375-dark.png`, `evidence/AT-23/375-light.png`, `evidence/AT-23/768-dark.png`, `evidence/AT-23/768-light.png`
Observation: With no week 11 trade served at 09:55:00 Eastern on Sat 2026-11-21, the sheet shows "No trades yet this week." at each size and theme (measure.jsonl, shots).

## AT-24: The empty Trade Wire after the Lock says so

App: site
Commit: `19371052`
Then: The sheet reads "No trades this week."
Files: `evidence/AT-24/iphone-15-390x660.json`, `evidence/AT-24/measure.jsonl`, `evidence/AT-24/1280-dark.png`, `evidence/AT-24/1280-light.png`, `evidence/AT-24/375-dark.png`, `evidence/AT-24/375-light.png`, `evidence/AT-24/768-dark.png`, `evidence/AT-24/768-light.png`
Observation: With no week 11 trade served at 00:00:01 Eastern on Tue 2026-11-24, the sheet shows "No trades this week." and no trade link at each size and theme (measure.jsonl, shots).

## AT-25: A failed read keeps the list

App: site
Commit: `19371052`
Then: Trade W stays, and a short note says that the last read failed.
Files: `evidence/AT-25/measure.jsonl`, `evidence/AT-25/1280-dark.png`, `evidence/AT-25/1280-light.png`, `evidence/AT-25/375-dark.png`, `evidence/AT-25/375-light.png`, `evidence/AT-25/768-dark.png`, `evidence/AT-25/768-light.png`
Observation: The first route call answers 200 with trade W, the next poll, 10 s later, answers 500. After it, trade W is still visible and the sheet shows "The last update failed." at each size and theme (measure.jsonl with the route calls and their status, shots).

## AT-26: "Grade a trade" opens Grade mode

App: site
Commit: `0807c881`
Then: The analyzer opens with "Grade a trade" selected in the switch.
Files: `evidence/AT-26/measure-flag-off.jsonl`, `evidence/AT-26/measure-flag-on.jsonl`, `evidence/AT-26/flag-off-1280-dark.png`, `evidence/AT-26/flag-off-1280-light.png`, `evidence/AT-26/flag-off-375-dark.png`, `evidence/AT-26/flag-off-375-light.png`, `evidence/AT-26/flag-off-768-dark.png`, `evidence/AT-26/flag-off-768-light.png`, `evidence/AT-26/flag-on-1280-dark.png`, `evidence/AT-26/flag-on-1280-light.png`, `evidence/AT-26/flag-on-375-dark.png`, `evidence/AT-26/flag-on-375-light.png`, `evidence/AT-26/flag-on-768-dark.png`, `evidence/AT-26/flag-on-768-light.png`
Observation: A tap on "Grade a trade" in the sheet opens `/analyze/?mode=grade`. With the flag on, the hero has the radiogroup "Mode" with "Grade a trade" checked and the title "Trade Analyzer" (measure-flag-on.jsonl, `flag-on-*` shots). With the flag off (the shipped config), the same URL opens the "Trade Analyzer" hero with no Mode switch on the page (measure-flag-off.jsonl, `flag-off-*` shots).

## AT-27: "Find a trade" hides while the `finder` flag is off

App: site
Commit: `19371052`
Then: The sheet shows "Grade a trade" and no "Find a trade".
Files: `evidence/AT-27/iphone-15-390x660.json`, `evidence/AT-27/measure.jsonl`, `evidence/AT-27/1280-dark.png`, `evidence/AT-27/1280-light.png`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/375-light.png`, `evidence/AT-27/768-dark.png`, `evidence/AT-27/768-light.png`
Observation: With the shipped config (flag off) and trade W served, the only link in the sheet is "Grade a trade" at each size and theme (measure.jsonl `links`, shots).

## AT-28: "Find a trade" opens Find mode

App: site
Commit: `0807c881`
Then: The analyzer opens with "Find a trade" selected, the title "Trade Ideas", and the line "Who has a trade for you?".
Files: `evidence/AT-28/measure.jsonl`, `evidence/AT-28/1280-dark.png`, `evidence/AT-28/1280-light.png`, `evidence/AT-28/375-dark.png`, `evidence/AT-28/375-light.png`, `evidence/AT-28/768-dark.png`, `evidence/AT-28/768-light.png`
Observation: With the flag on, a tap on "Find a trade" in the sheet opens `/analyze/?mode=find`, with "Find a trade" checked in the radiogroup "Mode", the title "Trade Ideas", and the line "Who has a trade for you?" at each size and theme (measure.jsonl, shots).

## AT-29: The trade links hide after the Lock

App: site
Commit: `0807c881`
Then: The sheet shows neither "Grade a trade" nor "Find a trade".
Files: `evidence/AT-29/iphone-15-390x660.json`, `evidence/AT-29/measure.jsonl`, `evidence/AT-29/1280-dark.png`, `evidence/AT-29/1280-light.png`, `evidence/AT-29/375-dark.png`, `evidence/AT-29/375-light.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/768-light.png`
Observation: With the flag on at 00:00:01 Eastern on Tue 2026-11-24, the sheet holds no link (`linksInSheet: []`) at each size and theme (measure.jsonl, shots).

## AT-30: A drag up does not lift the sheet off the bottom

App: site
Commit: `19371052`
Then: The bottom edge of each sheet stays at the bottom of the viewport, within 1 px.
Files: `evidence/AT-30/measure.jsonl`, `evidence/AT-30/team-sheet-drag-1280-dark.png`, `evidence/AT-30/team-sheet-drag-1280-light.png`, `evidence/AT-30/team-sheet-drag-375-dark.png`, `evidence/AT-30/team-sheet-drag-375-light.png`, `evidence/AT-30/team-sheet-drag-768-dark.png`, `evidence/AT-30/team-sheet-drag-768-light.png`, `evidence/AT-30/trade-wire-drag-1280-dark.png`, `evidence/AT-30/trade-wire-drag-1280-light.png`, `evidence/AT-30/trade-wire-drag-375-dark.png`, `evidence/AT-30/trade-wire-drag-375-light.png`, `evidence/AT-30/trade-wire-drag-768-dark.png`, `evidence/AT-30/trade-wire-drag-768-light.png`
Observation: During a 200 px drag up of the grip, at each size and theme, the dialog box of the Trade Wire and of the team sheet moves up: its bottom edge sits at 877.4 to 877.5 px in a viewport of 900, a gap of 22.5 to 22.6 px. A `::after` bleed of 96 px with the same computed background as the box fills that gap, so the visible surface (box plus bleed) reaches 973.4 px, past the bottom of the viewport, a gap of 0 (measure.jsonl, with 10 samples per drag). The shots are taken during the drag.

## AT-31: The analyzer switch is the ui-sdk SegmentedControl

App: site
Commit: `0807c881`
Then: The hero shows "Grade a trade · Find a trade" across its full width in two halves whose widths differ by 1 px or less.
Files: `evidence/AT-31/imports.txt`, `evidence/AT-31/iphone-15-390x660.json`, `evidence/AT-31/measure.jsonl`, `evidence/AT-31/1280-dark.png`, `evidence/AT-31/1280-light.png`, `evidence/AT-31/375-dark.png`, `evidence/AT-31/375-light.png`, `evidence/AT-31/768-dark.png`, `evidence/AT-31/768-light.png`
Observation: With the flag on, `[aria-label=Mode]` has the role radiogroup and two radio items, "Grade a trade" and "Find a trade". The two halves are 140.5 px each at 375, 273 px at 768, and 313 px at 1280 (difference 0), and the switch spans the inner width of the hero less 1 px each side (measure.jsonl). `imports.txt` shows `mode-switch.tsx` imports `@cpc/design/ui/segmented-control`, and only that wrapper imports `@ui-sdk/react/segmented-control`.

## AT-32: The switch locks during a wait

App: site
Commit: `0807c881`
Then: The switch stays on "Find a trade", and the wait goes on.
Files: `evidence/AT-32/measure.jsonl`, `evidence/AT-32/1280-dark.png`, `evidence/AT-32/1280-light.png`, `evidence/AT-32/375-dark.png`, `evidence/AT-32/375-light.png`, `evidence/AT-32/768-dark.png`, `evidence/AT-32/768-light.png`
Observation: With the find stream held (no answer), after a tap on "Find a Trade" and then a tap on "Grade a trade", the radiogroup has `aria-disabled=true`, "Find a trade" keeps `aria-checked=true`, "Grade a trade" keeps `aria-checked=false`, the URL stays `/analyze/?mode=find`, and the "Finding Trades" wait still shows at each size and theme (measure.jsonl, shots).

## AT-33: Find mode shows the partner choice and the position chips

App: site
Commit: `0807c881`
Then: The hero shows the partner choice of one team or every team, and the chips "Any · RB · WR · TE · QB".
Files: `evidence/AT-33/measure.jsonl`, `evidence/AT-33/1280-dark.png`, `evidence/AT-33/1280-light.png`, `evidence/AT-33/375-dark.png`, `evidence/AT-33/375-light.png`, `evidence/AT-33/768-dark.png`, `evidence/AT-33/768-light.png`
Observation: With the flag on and Bo Girds as Your team, the Find hero reads "Trade Ideas", "Who has a trade for you?", YOUR TEAM Bo Girds, TRADE WITH "Every team" with "Change", the chips "Any RB WR TE QB", and "Find a Trade" at each size and theme (measure.jsonl, shots).

## AT-34: The analyzer shows the deadline eyebrow

App: site
Commit: `19371052`
Then: The hero eyebrow reads "Trade deadline ~2d 14h 05m", then "The trade deadline has passed".
Files: `evidence/AT-34/iphone-15-390x660.json`, `evidence/AT-34/measure.jsonl`, `evidence/AT-34/closed-1280-dark.png`, `evidence/AT-34/closed-1280-light.png`, `evidence/AT-34/closed-375-dark.png`, `evidence/AT-34/closed-375-light.png`, `evidence/AT-34/closed-768-dark.png`, `evidence/AT-34/closed-768-light.png`, `evidence/AT-34/open-1280-dark.png`, `evidence/AT-34/open-1280-light.png`, `evidence/AT-34/open-375-dark.png`, `evidence/AT-34/open-375-light.png`, `evidence/AT-34/open-768-dark.png`, `evidence/AT-34/open-768-light.png`
Observation: On `/analyze/` the hero eyebrow reads "TRADE DEADLINE ~2d 14h 05m" at 09:55:00 Eastern on Sat 2026-11-21 and "THE TRADE DEADLINE HAS PASSED" at 00:00:01 Eastern on Tue 2026-11-24 (upper case by style) at each size and theme (measure.jsonl, `open-*` and `closed-*` shots).

## AT-35: A chip sets the same limit as a typed question

App: site
Commit: `0807c881`
Then: The find request has `aim_position` "RB", the same value that the front door sends for "trade ideas for an RB".
Files: `evidence/AT-35/front-door.json`, `evidence/AT-35/measure.jsonl`, `evidence/AT-35/rb-1280-dark.png`, `evidence/AT-35/rb-1280-light.png`, `evidence/AT-35/rb-375-dark.png`, `evidence/AT-35/rb-375-light.png`, `evidence/AT-35/rb-768-dark.png`, `evidence/AT-35/rb-768-light.png`
Observation: With the flag on, a tap on the chip "RB" and on "Find a Trade" sends the body `{"season": 2026, "asker": 6, "limit": {"aim_position": "RB"}}` (measure.jsonl, each size and theme; the `rb-*` shots show RB picked). On the front door, the typed question "trade ideas for an RB" sends `{"roster_id":6,"partner":null,"question":"trade ideas for an RB","turns":[]}` to `/trade-ideas`, and the API stream answers with the part `data-limit` `{"keep_positions": [], "keep_players": [], "aim_position": "RB"}` (front-door.json). So both reach the Limit `aim_position` "RB"; the front door sends the question and the API reads the value from it.

## AT-36: The Finder wait shows the real steps in `StageLines`

App: site
Commit: `0807c881`
Then: One line at a time shows each real step, such as "4 of 5 · Making a shortlist", and each line holds until the next step ends.
Files: `evidence/AT-36/measure.jsonl`, `evidence/AT-36/stagelines-dom.html`, `evidence/AT-36/stream-1280-dark.txt`, `evidence/AT-36/stream-1280-light.txt`, `evidence/AT-36/stream-375-dark.txt`, `evidence/AT-36/stream-375-light.txt`, `evidence/AT-36/stream-768-dark.txt`, `evidence/AT-36/stream-768-light.txt`, `evidence/AT-36/line-1-1280-dark.png`, `evidence/AT-36/line-1-1280-light.png`, `evidence/AT-36/line-1-375-dark.png`, `evidence/AT-36/line-1-375-light.png`, `evidence/AT-36/line-1-768-dark.png`, `evidence/AT-36/line-1-768-light.png`, `evidence/AT-36/line-2-1280-dark.png`, `evidence/AT-36/line-2-1280-light.png`, `evidence/AT-36/line-2-375-dark.png`, `evidence/AT-36/line-2-375-light.png`, `evidence/AT-36/line-2-768-dark.png`, `evidence/AT-36/line-2-768-light.png`
Observation: Six real presses (one per size and theme) for Bo Girds and every team against the local API, with the result cache emptied before each. The wait shows one line at a time, each held until the next step starts: "1 of 5 · Reading every team" from the tap, "2 of 5 · Looking for players who fit" at 2.7 to 4.8 s, "3 of 5 · Building offers" and "4 of 5 · Making a shortlist" about 0.3 s later, and "5 of 5 · Picking the best 3" at 3.6 to 5.8 s, which holds until the answer (measure.jsonl). The stream files give each step event with its time (the done lines "Read 11 teams", "Found 15 players who fit", "Built 81 offers", "Made a shortlist of 10", "Picked the best 2"). `stagelines-dom.html` shows the `t-think` part of `StageLines`. The `line-1` and `line-2` shots show two lines.

## AT-37: The team avatars light up in turn

App: site
Commit: `0807c881`
Then: The avatars light up one after another, in the order of the stream.
Files: `evidence/AT-37/measure.jsonl`, `evidence/AT-37/1280-dark.png`, `evidence/AT-37/1280-light.png`, `evidence/AT-37/375-dark.png`, `evidence/AT-37/375-light.png`, `evidence/AT-37/768-dark.png`, `evidence/AT-37/768-light.png`
Observation: In each press the avatars light one by one, in the order of the stream parts `data-team` (for example 1, 5, 3, 2, 10, 11, 7, 9, 12, 8, 4), all within about 0.2 s, about 2.6 to 4.8 s after the tap (measure.jsonl: lit avatars with seconds, and the stream order). The shots show the wait with the lit row.

## AT-38: The Finder trades show as cards with the Lean and a short Case

App: site
Commit: `0807c881`
Then: Up to 3 cards show in one list under the hero, each with a Lean of Send it, Lean yes, or Gut call, a Case of at most 3 lines, folded Bullets, and no headline.
Files: `evidence/AT-38/find-answer-1280-dark.json`, `evidence/AT-38/find-answer-1280-light.json`, `evidence/AT-38/find-answer-375-dark.json`, `evidence/AT-38/find-answer-375-light.json`, `evidence/AT-38/find-answer-768-dark.json`, `evidence/AT-38/find-answer-768-light.json`, `evidence/AT-38/measure.jsonl`, `evidence/AT-38/1280-dark.png`, `evidence/AT-38/1280-light.png`, `evidence/AT-38/375-dark.png`, `evidence/AT-38/375-light.png`, `evidence/AT-38/768-dark.png`, `evidence/AT-38/768-light.png`
Observation: Each of the six results lands as 2 cards in one list `ol[aria-label="Trade ideas"]` under the hero. Each card leads with its Lean (Lean yes or Gut call), has a Case clamped at 3 lines (3 rendered lines, one card 2), Bullets folded behind "Why it works", and no heading other than the Lean (measure.jsonl, find-answer files, full-page shots).

## AT-39: A tap on a card opens the trade already graded

App: site
Commit: `0807c881`
Then: The analyzer shows that trade in Grade mode with its read, and no analyze request goes out.
Files: `evidence/AT-39/measure.jsonl`, `evidence/AT-39/1280-dark.png`, `evidence/AT-39/1280-light.png`, `evidence/AT-39/375-dark.png`, `evidence/AT-39/375-light.png`, `evidence/AT-39/768-dark.png`, `evidence/AT-39/768-light.png`
Observation: A tap on "See the Full Result" of the first card opens `/analyze/?mode=grade` with the read of that card (hero title "Lean yes", or "Gut call" in one run), and the page makes 0 API requests in the 3 s after the tap, so 0 analyze requests, at each size and theme (measure.jsonl, full-page shots).

## AT-40: A failed find shows Try Again

App: site
Commit: `0807c881`
Then: The hero shows the error line and a "Try Again" button.
Files: `evidence/AT-40/measure.jsonl`, `evidence/AT-40/1280-dark.png`, `evidence/AT-40/1280-light.png`, `evidence/AT-40/375-dark.png`, `evidence/AT-40/375-light.png`, `evidence/AT-40/768-dark.png`, `evidence/AT-40/768-light.png`
Observation: With the find route answering 500, after a tap on "Find a Trade" the hero shows "The API did not answer. Try again." and the button "Try Again" at each size and theme (measure.jsonl, shots).

## AT-41: A press of the Finder takes about 25 s

App: api
Commit: `19371052`
Then: Each press ends in 30 s or less, with one pick call and no id retry.
Files: `evidence/AT-41/api.log`, `evidence/AT-41/output.txt`, `evidence/AT-41/press-0-stream-shell-timer.txt`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-summary.txt`, `evidence/AT-41/press.py.txt`, `evidence/AT-41/presses.py.txt`
Observation: Three timed presses for Bo Girds and every team on the live week 11 snapshot, with the result cache emptied before each, take 23.93 s, 22.76 s, and 27.97 s wall time; the server logs 23.9 s, 22.7 s, and 28.0 s, each with `claude_calls=1` and one `FinderPickOut` call, and no repair or retry line. A first warm-up press took 29.7 s. The Claude cost is $0.0719, $0.0695, and $0.0766; Jev waves are logged per press (output.txt, api.log, press streams). In the browser presses of AT-36 on `0807c881`, two of the nine presses that the site API logged (one of them from a run that the agent stopped) had a second call, a `PickOut` repair of a bullet number (`finder repair of pick 2`), with `claude_calls=2`. The front door presses of AT-49 (the same find press, on `0807c881`) take 17.7 to 42.5 s on the server, and 6 of 10 take more than 30 s.

## AT-42: One picked partner skips the Partner filter

App: api
Commit: `19371052`
Then: The log shows no Partner filter step, and the Shortlist holds 2 or more offers.
Files: `evidence/AT-42/api.log`, `evidence/AT-42/output.txt`, `evidence/AT-42/press-stream.txt`, `evidence/AT-42/press-summary.txt`
Observation: The press for Bo Girds with Teehee (roster 12) logs "Spares tree of Bo Girds: skipped for one picked partner" and no Partner filter line. It builds 6 offers, and the gain check drops all 6 (each with a gain below 0.3 for one side), so the stream says "Made a shortlist of 0" and the Shortlist holds 0 offers (output.txt, press-summary.txt).

## AT-43: The Shortlist has variety

App: api
Commit: `0807c881 (read of the presses of 19371052)`
Then: The best offer of each player of Bo Girds and the best offer of each partner come before a second form of any trade.
Files: `evidence/AT-43/at43.py.txt`, `evidence/AT-43/shortlist.txt`
Observation: Read against the new Then line. In each of the 4 presses of AT-41 the Shortlist holds 10 offers. The first 4 or 5 offers each bring a player of Bo Girds or a partner not shown before (McBride, Flowers, Golden, and in press 1 Parker Washington; partners Unsolicited Dak Picks, To Infinity and Bijan, Lil Fridge), and every later offer repeats a player and a partner already shown. Each first offer of a player and of a partner is its best score, except Zay Flowers in press 3: his first offer scores 0.256, and his best, 0.265, comes later as a further form (shortlist.txt).

## AT-44: The Spares tree lists a player only with cover who can play now

App: pipeline
Commit: `19371052`
Then: A starter at RB of the test roster is not listed, and each listed player in the run has a backup above the line who can play now.
Files: `evidence/AT-44/output.txt`, `evidence/AT-44/spares_week11.py.txt`
Observation: Both Spares tree tests pass on the week 6 fixture snapshot: each listed player has a backup at his position above the line who can play now, and a test roster whose only RB backup is Out lists no RB. On the live week 11 snapshot of cpc, `spare_list` over all 132 ordered pairs lists 610 players, and 0 of them lack a backup at the position who can cover now by `can_cover` (output.txt). The pytest tests read the week 6 snapshot, not week 11.

## AT-45: A clear no stops, an unsure answer passes, and a failed call is an error

App: pipeline
Commit: `19371052`
Then: 0.2 stops, 0.5 passes, and the failed call raises an error, not a stop.
Files: `evidence/AT-45/output.txt`
Observation: 13 decision tests pass (output.txt). In the Spares tree, fixed answers of 0.2 for each listed player stop the side, 0.5 passes, and a failed call raises `JevError`. In the gain check the tests use 0.29 (drops) and 0.3 (stays), and a failed shortlist request keeps its offers as unsure. A failed Spares tree request inside the Finder search lets the partner go on and logs, and the Spares tree function itself raises.

## AT-46: The two bad ideas never come back

App: api
Commit: `19371052`
Then: Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is on the Shortlist or among the 3 trades.
Files: `evidence/AT-46/output.txt`
Observation: In all 4 presses for Bo Girds and every team, "Kenneth Walker III for Patrick Mahomes" is dropped by the gain check (gain of Bo Girds 0.04 to 0.05). "Zay Flowers for Jared Goff" is on the Shortlist in all 4 presses (gain of Bo Girds 0.97 to 0.98), and is not among the trades, which are McBride for Dak Prescott, McBride for C.J. Stroud, and Flowers for Prescott (output.txt).

## AT-47: The backtest runs as one command and passes the bar

App: pipeline
Commit: `19371052`
Then: The output lists each mark with its result, and every mark is right.
Files: `evidence/AT-47/output.txt`
Observation: `make -C apps/pipeline backtest CLIENT=cpc` on the live week 11 lists 5 marks: 1 RIGHT (Walker for Mahomes, drop) and 4 WRONG (Flowers for Goff expects drop and gets keep; three Spares marks expect stop and get pass), "Right marks: 1 of 5", Jev 5 requests, $0.0004, and exit 1 (output.txt). The commits after `19371052` do not change the tree or the marks.

## AT-48: A failed stream logs its cause

App: api
Commit: `19371052`
Then: The API logs one line with the cause, the stage, and the seconds since the start.
Files: `evidence/AT-48/output.txt`
Observation: The test cuts a real uvicorn stream of trade ideas from the client, and the API logs one line: `Trade stream failed: topic=trade_ideas cause=client-cut stage="Made a shortlist of 10" seconds=4.8` (output.txt with the command, the live log, and the test source).

## AT-49: The first call of a trade Topic does not fail

App: site
Commit: `0807c881`
Then: All 10 answers arrive with no retry line.
Files: `evidence/AT-49/api-run-1.log`, `evidence/AT-49/api-run-10.log`, `evidence/AT-49/api-run-2.log`, `evidence/AT-49/api-run-3.log`, `evidence/AT-49/api-run-4.log`, `evidence/AT-49/api-run-5.log`, `evidence/AT-49/api-run-6.log`, `evidence/AT-49/api-run-7.log`, `evidence/AT-49/api-run-8.log`, `evidence/AT-49/api-run-9.log`, `evidence/AT-49/run-1.json`, `evidence/AT-49/run-10.json`, `evidence/AT-49/run-2.json`, `evidence/AT-49/run-3.json`, `evidence/AT-49/run-4.json`, `evidence/AT-49/run-5.json`, `evidence/AT-49/run-6.json`, `evidence/AT-49/run-7.json`, `evidence/AT-49/run-8.json`, `evidence/AT-49/run-9.json`, `evidence/AT-49/runs.txt`, `evidence/AT-49/answer-1280-dark.png`, `evidence/AT-49/answer-1280-light.png`, `evidence/AT-49/answer-375-dark.png`, `evidence/AT-49/answer-375-light.png`, `evidence/AT-49/answer-768-dark.png`, `evidence/AT-49/answer-768-light.png`, `evidence/AT-49/run-10-390x660.png`, `evidence/AT-49/run-7-390x660.png`, `evidence/AT-49/run-8-390x660.png`, `evidence/AT-49/run-9-390x660.png`
Observation: By Brian's choice the API was local, not a deploy of the spec branch. Each of the 10 runs started its own local API with empty result and ask caches, opened the front door of cpc in a fresh browser context with Bo Girds as Your team, and tapped More, then the Trade ideas Topic. All 10 runs end with the trade ideas answer (the region "Trade ideas" with its trade card) in 27.4 to 51.2 s, with 0 retry lines on the page, one POST /trade-ideas that answers 200, and 0 lines "Trade stream failed" in each API log (runs.txt, run-<n>.json, api-run-<n>.log). The server press of each run takes 17.7 to 42.5 s; runs 1 and 5 log claude_calls=2. The shots: runs 4, 5, and 6 give answer-768-dark, answer-1280-light, and answer-1280-dark, and runs 7 to 10 give run-<n>-390x660 in the iPhone 15 context. Runs 1 to 3 saved no shot (an instrument fault), so answer-375-light, answer-375-dark, and answer-768-light come from a repeat of the cached answer of run 10 (server press 2 to 3 s, no Claude call); those three repeats are not among the 10 runs.

## AT-50: The Lock is one value in the client config

App: site
Commit: `0807c881`
Then: The Deadline banner shows the last-hours state with "~1h 00m 00s".
Files: `evidence/AT-50/config.diff`, `evidence/AT-50/iphone-15-390x660.json`, `evidence/AT-50/measure.jsonl`, `evidence/AT-50/1280-dark.png`, `evidence/AT-50/1280-light.png`, `evidence/AT-50/375-dark.png`, `evidence/AT-50/375-light.png`, `evidence/AT-50/768-dark.png`, `evidence/AT-50/768-light.png`
Observation: In a local build with the Lock at `2026-11-21T10:55:00-05:00` (config.diff), at 09:55:00 Eastern on Sat 2026-11-21 the banner has `data-phase` `last-hours` and reads "~1h 00m 00s" at each size and theme (measure.jsonl, shots). The config is back as committed (AT-51).

## AT-51: The `finder` flag of CPC stays off

App: site
Commit: `0807c881`
Then: The `finder` flag is `false`.
Files: `evidence/AT-51/output.txt`
Observation: `clients/cpc/client.toml` at `0807c881` holds `finder = false` on line 22, and the worktree file has no change (output.txt).

## AT-52: No Deadline Board ships

App: site
Commit: `19371052`
Then: Both pages answer 404, and no link to a Deadline Board exists.
Files: `evidence/AT-52/status.txt`
Observation: On the cpc export served with the 404 rule, `/deadline/` and `/deadline-board/` each answer 404. A search of the export finds 0 files with "deadline-board" or "deadline board", 0 links to `/deadline`, and no folder named deadline (status.txt).

## AT-53: The Finder offers no three-team trade

App: site
Commit: `0807c881`
Then: The hero has no choice of two or three teams.
Files: `evidence/AT-53/measure.jsonl`, `evidence/AT-53/1280-dark.png`, `evidence/AT-53/1280-light.png`, `evidence/AT-53/375-dark.png`, `evidence/AT-53/375-light.png`, `evidence/AT-53/768-dark.png`, `evidence/AT-53/768-light.png`
Observation: With the flag on, the Find hero holds Your team, Trade with (Every team), the position chips, and "Find a Trade", and its text has no choice of two or three teams at each size and theme (measure.jsonl `teamCountChoice: false`, shots).

## AT-54: Next.js stays at its version

App: site
Commit: `0807c881`
Then: The version is the same.
Files: `evidence/AT-54/output.txt`
Observation: `apps/site/package.json` has `"next": "^16.4.5"` on `main` (`8780eefb`) and on `0807c881`, and the diff of `package.json` and `pnpm-lock.yaml` has no `next` line (output.txt). The installed version in the worktree is 16.4.5.
