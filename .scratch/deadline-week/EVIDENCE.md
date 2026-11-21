# Deadline week: evidence

Smoke run on `98d79f98`: `Smoke run: 7 flows, 7 passed, 0 failed`. Folder: `evidence/smoke/`.

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests: `.scratch/deadline-week/ACCEPTANCE.md`.
Built from: `98d79f98`, on 2026-11-20. Every entry of this round is recorded on `98d79f98`, except the four entries of the fix round below, which are on `2e9f0f85`; no entry keeps a file of the first round (`19371052`, `0807c881`, `cacd779f`). AT-42 is Retired. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: no runner round. The agent instrument ran in phases on `98d79f98`: 6 min for 22 site tests with the shipped config, 8 min for 13 site tests with the `finder` flag on (press run 1), 6 min for press run 2 of the 8 press tests, under 1 min for AT-50 and under 1 min for AT-11, and 17 min (of which 6 min of a second warm-up) for the 11 front door asks of AT-49. 43 site tests have shots; AT-65 reads the shots of AT-38.

Background check: `make check` in the Spec worktree from 2026-11-20 16:06:15 to 16:23:39 EST. It ends red in the site check: `check:grade-bar-export` of norcal, 2 failed, 32 passed (`grade-bar.spec.ts:65` and `:83`, "getByRole('button', { name: 'Find a Trade' })" not found, because `/analyze/` opens in Grade mode). The make stops there, so the agent ran the rest: `make check APPS="pipeline api"` from 16:24:19 to 16:32:03 gives the pipeline 1735 passed and the API 1 failed, 651 passed (`test_a_stream_that_the_client_cuts_logs_one_line_with_its_cause_its_stage_and_its_seconds`, `stage="start"`, IndexError), while the builds of this round ran. After the builds the agent ran the failed member again, `make -C apps/api check`, from 17:00:15 to 17:02:43: "All checks passed!" and "652 passed in 139.63s". The packages part of `make check` never ran after the stop, so the agent ran `make -C packages/<name>/python check` for each package with Python, from 17:07:00 to 17:08:05: each exits 0 (analyzer 34 passed, eggs 37, facts 15, league 15, managers 11, midseason 132, rankings 8, sim 78, waiver 67, week 7). The root scripts check passed at the start of the first run. The site failure of grade-bar stays: the agent changes no code in this stage.

Cost of the round: $4.05 of Claude and $3.41 of Jev, about $7.46 in all. Jev: two fair warm-ups of the evidence API ($1.3639 each, 375 s and 382 s), a stopped first start ($0.0638), the warm-up of the smoke API ($0.3705 before its stop), the presses after the warm-ups ($0.2030 in all, about $0.006 to $0.008 each), the backtest ($0.0004), and the Evidence flags ($0.0447, 1,063,472 input tokens). Claude: 30 presses of the Finder and the front door on the two evidence APIs ($3.9516, each line `Press of find ... cost=`), two Claude stream answers ($0.0141), and the smoke flows ($0.0801).

Fix round on `2e9f0f85`, 2026-11-20. The entries of AT-36, AT-49, AT-72, and AT-73 are recorded again on `2e9f0f85`; every other entry stays on `98d79f98`. The commits from `98d79f98` to `2e9f0f85`: `2cacd0ea` records the first evidence; `0546ac78` and `1a723f39` are fix group u, test files only (`grade-bar.spec.ts`, `test_trade_topics.py`); `28ae3931` records the Test verdicts of the Judge; `e3d882f7` changes the text of AT-49 (one fresh local evidence API) and AT-73 (3 lines only for a pick of 15 s or more); `a24f0b2e` and `34ea8fe3` are fix group v (the pick states its count first, the stream sends `data-trades-count`, and the first trade line of step 5 comes 1.5 s after the step line); `ff89e908` and `424bafb5` merge groups u and v; `2e9f0f85` is fix group w (the fair cache keeps its answers in a file per client and loads it at the API start). The other entries stay on `98d79f98`: group u changed only tests, group v changed only the count and the step 5 timing, which these four tests cover, and group w changed only where the fair answers are kept.

The instrument of the fix round is `zz-deadline-evidence-r2.spec.mjs.txt` in `evidence/AT-36/` and `evidence/AT-49/`, cut from `evidence/instrument/zz-deadline-evidence.spec.mjs`, with `press.sh.txt`, `at49.sh.txt`, and `pw.config.mjs.txt`. One fresh evidence API from a detached worktree of `2e9f0f85` served the round (`api.sh.txt`), with the Shortlist tap and no fair cache file at its start. Two local builds call it at 127.0.0.1:8391: the shipped config for AT-49, and the `finder` flag on in the local build only for the presses; `clients/cpc/client.toml` is back as committed. The warm-up got 1042 TypeSafe answers, each 200, and the whole round got 1539 TypeSafe answers, each 200, with no `402` and no failed Jev request (`evidence/AT-49/warm-up.txt`, `evidence/AT-36/api-presses.log`). An earlier try on `424bafb5` ran out of Jev credits during its warm-up, and no file of that try is used.

Cost of the fix round: $4.23 for the recorded round, plus $0.0033 of Jev for the Evidence flags (77,728 input tokens; the flags of AT-49 got a Jev error, `max_tokens_exceeded`, and no flag). Jev cost $1.3965: the warm-up $1.2676 and the 16 presses $0.1289. Claude cost $2.8338: the 16 presses (10 asks of AT-49 and 6 presses) $2.3469 and the three `ChartRead` calls at the API start $0.4869. The failed try before it cost about $3.20: Jev $0.9083, and Claude $1.7998 for 16 presses and $0.4869 for `ChartRead`.

The instrument of the site tests. The evidence runner has no verb for a fixed clock or for a served answer of the Trade Wire route, and nearly every site test needs both. So the site tests use one Playwright file of the agent, `evidence/instrument/zz-deadline-evidence.spec.mjs` (the agent ran it from `apps/site/e2e/` and did not commit it there), with `evidence/instrument/phase.sh` and `evidence/instrument/at49.sh`. It runs WebKit, sets the browser clock of each test with `page.clock`, serves trade W from `evidence/fixtures/` through a Playwright route where the test says so, and sends every other call to a real local API. The export is served by `evidence/instrument/serve.mjs` on 127.0.0.1:8392, which answers a missing path with `404.html` and the status 404. Each test writes its measures to `measure.jsonl` and its shots as `<name>-<width>-<theme>.png` at a viewport height of 900, and most write `iphone-15-390x660.json` from `devices["iPhone 15"]` at 390 by 660. Four local builds against the local API at 127.0.0.1:8391: the shipped cpc config, the `finder` flag on (AT-12 find mode, AT-18, AT-26 flag on, AT-28, AT-29, AT-31 to AT-40, AT-53, AT-65 to AT-68, AT-72, AT-73), the Lock moved (AT-50), and norcal (AT-11). The two cpc variants changed `clients/cpc/client.toml` in the local build only, and the file is back as committed (`evidence/AT-51/output.txt`).

The local API. The evidence API is the real app of `app_from_env`, run with `uvicorn --factory` from a detached worktree of `98d79f98`, with live Sleeper, live Jev, and live Claude from `~/.secrets` in the same shell, a rate limit of 600 a minute, and its own result cache. It adds one tap, `evidence/AT-41/evidence_tap.py.txt`: it calls the real Finder search with the same arguments and writes its Shortlist (every Value offer, the fair means, step 2, the gain drops, and the Shortlist) with the chart value of each player to a file. Each press of the API tests and of the press tests ran after the log line `Fair warm-up of cpc ended: 105876 questions, 105876 asked, 0 held, about 32474697 tokens, $1.3639, 375.1s` (`evidence/AT-41/warm-up.txt`), with every file under the result cache emptied first. AT-13 and AT-17 ran on two more APIs of the same worktree with no Jev key, so their warm-ups asked no Jev: the leg 9 factory of AT-13 and the limit of 30 a minute of AT-17.

Press runs of the site. Press run 1 (six presses, one per size and theme) waited for the first enabled button of a card, which is the fold button of the Bullets, so it read the stream and took the `last-card` shots before the last card. Its measures and stream files stay in `evidence/press-run-1/`, and its shots were taken again. Press run 2 waits for the enabled button "See the Full Result". Each entry of AT-36 to AT-39, AT-65, AT-67, AT-72, and AT-73 reads press run 2. In press run 1, 5 of 6 presses picked 5 trades; in press run 2, 4 of 6 picked 5 and 2 picked 4. 2 of the 12 site presses logged a repair of the pick (`claude_calls=2` and `claude_calls=3`).

Trade W: Sleeper leg 9 of cpc 2026, transaction `1424578776058155008`. NFC Least (roster 4) gets Tetairoa McMillan WR, Makai Lemon WR, Seth McGowan RB, and Chase Brown RB. Return of T Mac (roster 8) gets Rome Odunze WR, CeeDee Lamb WR, Jordan Mason RB, and $5 of FAAB. The recorded answer is `evidence/AT-13/sleeper-leg-9.json`, read again on 2026-11-20. Week 11 of cpc on the day of the run holds no trade: Sleeper leg 11 has 15 transactions, each `free_agent` or `waiver` (`evidence/AT-14/sleeper-leg-11.json`). So the tests that need a week 11 trade use trade W, as `ACCEPTANCE.md` says. The other trade of leg 9, `1425209111854747648` (Puka Deez... and behold the lamb), is the second real trade of AT-19 and AT-20.

Rebuild: `REBUILD.md` lists no value, and `evidence/rebuild.log` (run on `19371052`, base `main` at `8780eefb`) shows `rebuild diff: 0 diffs, 0 listed, 0 not listed, 0 listed but not changed`. The round did not run it again. Since `19371052` the pipeline code that writes a week changed only in `packages/facts/python/src/facts/writer.py`: an optional stream callback (`on_text`, which only the Finder pick passes) and more fields on its log line (`git diff cacd779f..98d79f98 -- packages/facts/python/src/facts/writer.py`).

The pipeline tests (AT-44, AT-45, AT-58, AT-59, AT-61 to AT-64, AT-71) and the backtest (AT-47) ran in the detached worktree of `98d79f98` with their own environment (`UV_PROJECT_ENVIRONMENT=<worktree>/.venv-tests`), and AT-48 with `.venv-apitest`, so no `uv run` touched the environment of the Spec worktree while the background check was live.

## AT-1: The Deadline banner shows the countdown

App: site
Commit: `98d79f98`
Then: Under the top band, the Deadline banner shows "TRADE DEADLINE" over "~2d 14h 05m".
Files: `evidence/AT-1/iphone-15-390x660.json`, `evidence/AT-1/measure.jsonl`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/375-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/768-light.png`
Observation: At 09:55:00 Eastern on Sat 2026-11-21, each of the 6 shots shows the Deadline banner under the top band with "TRADE DEADLINE" over "~2d 14h 05m" (measure.jsonl: eyebrow and countdown text). The iPhone 15 check at 390 by 660 reads a sideways scroll of 0, the band row bottom at 60, the banner from 60 to 106.9, and no overlap.

## AT-2: The countdown ticks

App: site
Commit: `98d79f98`
Then: The countdown reads "~2d 14h 04m".
Files: `evidence/AT-2/iphone-15-390x660.json`, `evidence/AT-2/measure.jsonl`, `evidence/AT-2/after-1280-dark.png`, `evidence/AT-2/after-1280-light.png`, `evidence/AT-2/after-375-dark.png`, `evidence/AT-2/after-375-light.png`, `evidence/AT-2/after-768-dark.png`, `evidence/AT-2/after-768-light.png`
Observation: In each of the 6 runs the countdown reads "~2d 14h 05m" before and "~2d 14h 04m" after the fake clock moves on 60000 ms (measure.jsonl). The shots are taken after the move.

## AT-3: The last hours show seconds on the accent fill

App: site
Commit: `98d79f98`
Then: The Deadline banner has the accent fill and reads "~2h 41m 10s".
Files: `evidence/AT-3/iphone-15-390x660.json`, `evidence/AT-3/measure.jsonl`, `evidence/AT-3/1280-dark.png`, `evidence/AT-3/1280-light.png`, `evidence/AT-3/375-dark.png`, `evidence/AT-3/375-light.png`, `evidence/AT-3/768-dark.png`, `evidence/AT-3/768-light.png`
Observation: At 21:18:50 Eastern on Mon 2026-11-23 the countdown reads "~2h 41m 10s", `data-phase` is `last-hours`, and the computed background of the banner button, rgb(184, 52, 42), equals the computed `--color-accent` in both themes (measure.jsonl). The shots show the red fill with seconds.

## AT-4: Reduced motion stops the shimmer

App: site
Commit: `98d79f98`
Then: No element of the Deadline banner has a running animation.
Files: `evidence/AT-4/iphone-15-390x660.json`, `evidence/AT-4/measure.jsonl`, `evidence/AT-4/1280-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/375-dark.png`, `evidence/AT-4/375-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/768-light.png`
Observation: With `prefers-reduced-motion: reduce` (true in the page) at 21:18:50 Eastern on Mon 2026-11-23, `getAnimations({ subtree: true })` on the banner gives an empty list at each size and theme, so 0 animations run (measure.jsonl).

## AT-5: The whole Deadline banner opens the Trade Wire

App: site
Commit: `98d79f98`
Then: The Trade Wire sheet opens, and the Deadline banner is one button named "Open the Trade Wire, N new trades", where N is the count of week 11 trades.
Files: `evidence/AT-5/imports.txt`, `evidence/AT-5/iphone-15-390x660.json`, `evidence/AT-5/measure.jsonl`, `evidence/AT-5/1280-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/375-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/768-light.png`
Observation: On `/rankings/` with trade W served as the one week 11 trade, the banner holds one `BUTTON` with `aria-haspopup=dialog` and the name "Open the Trade Wire, 1 new trade" (singular for N = 1). A tap on `[data-deadline-countdown]` opens the Trade Wire dialog in each shot (measure.jsonl). `imports.txt` shows `deadline-banner.tsx` and `wire-sheet.tsx` import the sheet parts from `@cpc/design/ui/sheet`, and only `packages/design/site/ui/sheet.tsx` imports `@ui-sdk/react/drawer`.

## AT-6: The badge counts the trades of week 11

App: site
Commit: `98d79f98`
Then: The badge reads "N new" for N week 11 trades, or shows no badge when N is 0.
Files: `evidence/AT-6/iphone-15-390x660.json`, `evidence/AT-6/measure.jsonl`, `evidence/AT-6/1280-dark.png`, `evidence/AT-6/1280-light.png`, `evidence/AT-6/375-dark.png`, `evidence/AT-6/375-light.png`, `evidence/AT-6/768-dark.png`, `evidence/AT-6/768-light.png`
Observation: Against the real Trade Wire route of the evidence API (no served answer), the route answers 200 with leg 11 and 0 trades, the banner has no `[data-deadline-badge]` element, and its name is "Open the Trade Wire, 0 new trades" at each size and theme (measure.jsonl). Real week 11 holds no trade on 2026-11-20 (`evidence/AT-14/sleeper-leg-11.json`), so the shots show no badge.

## AT-7: The Deadline banner sinks on a press

App: site
Commit: `98d79f98`
Then: The content of the Deadline banner scales to 0.98 over 150 ms.
Files: `evidence/AT-7/iphone-15-390x660.json`, `evidence/AT-7/measure.jsonl`, `evidence/AT-7/press-1280-dark.png`, `evidence/AT-7/press-1280-light.png`, `evidence/AT-7/press-375-dark.png`, `evidence/AT-7/press-375-light.png`, `evidence/AT-7/press-768-dark.png`, `evidence/AT-7/press-768-light.png`
Observation: At rest `[data-deadline-grid]` has `scale: none`. 400 ms into a held mouse press it has `scale: 0.98`, `transition-duration: 0.15s`, and `transition-timing-function: cubic-bezier(0.23, 1, 0.32, 1)` at each size and theme (measure.jsonl). The shots are taken during the press.

## AT-8: The Deadline banner has even padding and one left edge

App: site
Commit: `98d79f98`
Then: The top padding and the bottom padding of the Deadline banner differ by 1 px or less, and "TRADE DEADLINE" and the countdown start at the same x.
Files: `evidence/AT-8/iphone-15-390x660.json`, `evidence/AT-8/measure.jsonl`, `evidence/AT-8/1280-dark.png`, `evidence/AT-8/1280-light.png`, `evidence/AT-8/375-dark.png`, `evidence/AT-8/375-light.png`, `evidence/AT-8/768-dark.png`, `evidence/AT-8/768-light.png`
Observation: At each size and theme the top padding and the bottom padding are each 8 px (difference 0). The eyebrow and the countdown start at the same x: 32 at 375 and 768, and 72 at 1280 (difference 0) (measure.jsonl).

## AT-9: The Deadline banner says the trade deadline has passed

App: site
Commit: `98d79f98`
Then: The Deadline banner reads "The trade deadline has passed. Good luck in the playoffs." and the badge reads "Final".
Files: `evidence/AT-9/iphone-15-390x660.json`, `evidence/AT-9/measure.jsonl`, `evidence/AT-9/1280-dark.png`, `evidence/AT-9/1280-light.png`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/375-light.png`, `evidence/AT-9/768-dark.png`, `evidence/AT-9/768-light.png`
Observation: At 00:00:01 Eastern on Tue 2026-11-24 the banner text is "The trade deadline has passed. Good luck in the playoffs.", then "Trade Wire" and "Final" (measure.jsonl `bannerText`; the instrument looks for `[data-deadline-badge]`, which is not the element of "Final", so `badge` is null). The button name is "Open the Trade Wire, final. The trade deadline has passed." The shots show the closed state.

## AT-10: Deadline week ends by itself

App: site
Commit: `98d79f98`
Then: Neither page shows the Deadline banner or the deadline eyebrow.
Files: `evidence/AT-10/iphone-15-390x660.json`, `evidence/AT-10/measure.jsonl`, `evidence/AT-10/analyzer-1280-dark.png`, `evidence/AT-10/analyzer-1280-light.png`, `evidence/AT-10/analyzer-375-dark.png`, `evidence/AT-10/analyzer-375-light.png`, `evidence/AT-10/analyzer-768-dark.png`, `evidence/AT-10/analyzer-768-light.png`, `evidence/AT-10/front-door-1280-dark.png`, `evidence/AT-10/front-door-1280-light.png`, `evidence/AT-10/front-door-375-dark.png`, `evidence/AT-10/front-door-375-light.png`, `evidence/AT-10/front-door-768-dark.png`, `evidence/AT-10/front-door-768-light.png`
Observation: At 00:00:01 Eastern on Wed 2026-11-25 the front door and `/analyze/` each have 0 banner elements and no text "trade deadline"; the analyzer hero eyebrow reads "TRADE ANALYZER" (measure.jsonl). The shots `front-door-*` and `analyzer-*` show the top of each page.

## AT-11: Norcal has no Deadline week

App: site
Commit: `98d79f98`
Then: The page shows no Deadline banner.
Files: `evidence/AT-11/iphone-15-390x660.json`, `evidence/AT-11/measure.jsonl`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`
Observation: On the norcal export (title "NorCal Apex 6") at 09:55:00 Eastern on Sat 2026-11-21, each size and theme has 0 banner elements and no text "trade deadline" (measure.jsonl). The iPhone 15 check reads `bannerPresent: false`.

## AT-12: The copy uses plain words

App: site
Commit: `98d79f98`
Then: No text holds "Lock", "Rosters are locked", "Deadline Board", "feed", "Jev", "Advisor", "Finder", or "Brian".
Files: `evidence/AT-12/search.txt`, `evidence/AT-12/text-analyzer-closed.txt`, `evidence/AT-12/text-analyzer-find-flag-on-closed.txt`, `evidence/AT-12/text-analyzer-find-flag-on-last-hours.txt`, `evidence/AT-12/text-analyzer-find-flag-on-open.txt`, `evidence/AT-12/text-analyzer-last-hours.txt`, `evidence/AT-12/text-analyzer-open.txt`, `evidence/AT-12/text-front-door-closed.txt`, `evidence/AT-12/text-front-door-last-hours.txt`, `evidence/AT-12/text-front-door-open.txt`, `evidence/AT-12/text-sheet-closed.txt`, `evidence/AT-12/text-sheet-find-flag-on-closed.txt`, `evidence/AT-12/text-sheet-find-flag-on-last-hours.txt`, `evidence/AT-12/text-sheet-find-flag-on-open.txt`, `evidence/AT-12/text-sheet-last-hours.txt`, `evidence/AT-12/text-sheet-open.txt`, `evidence/AT-12/analyzer-closed-1280-dark.png`, `evidence/AT-12/analyzer-closed-1280-light.png`, `evidence/AT-12/analyzer-closed-375-dark.png`, `evidence/AT-12/analyzer-closed-375-light.png`, `evidence/AT-12/analyzer-closed-768-dark.png`, `evidence/AT-12/analyzer-closed-768-light.png`, `evidence/AT-12/analyzer-find-flag-on-closed-375-light.png`, `evidence/AT-12/analyzer-find-flag-on-last-hours-375-light.png`, `evidence/AT-12/analyzer-find-flag-on-open-375-light.png`, `evidence/AT-12/analyzer-last-hours-1280-dark.png`, `evidence/AT-12/analyzer-last-hours-1280-light.png`, `evidence/AT-12/analyzer-last-hours-375-dark.png`, `evidence/AT-12/analyzer-last-hours-375-light.png`, `evidence/AT-12/analyzer-last-hours-768-dark.png`, `evidence/AT-12/analyzer-last-hours-768-light.png`, `evidence/AT-12/analyzer-open-1280-dark.png`, `evidence/AT-12/analyzer-open-1280-light.png`, `evidence/AT-12/analyzer-open-375-dark.png`, `evidence/AT-12/analyzer-open-375-light.png`, `evidence/AT-12/analyzer-open-768-dark.png`, `evidence/AT-12/analyzer-open-768-light.png`, `evidence/AT-12/front-door-closed-1280-dark.png`, `evidence/AT-12/front-door-closed-1280-light.png`, `evidence/AT-12/front-door-closed-375-dark.png`, `evidence/AT-12/front-door-closed-375-light.png`, `evidence/AT-12/front-door-closed-768-dark.png`, `evidence/AT-12/front-door-closed-768-light.png`, `evidence/AT-12/front-door-last-hours-1280-dark.png`, `evidence/AT-12/front-door-last-hours-1280-light.png`, `evidence/AT-12/front-door-last-hours-375-dark.png`, `evidence/AT-12/front-door-last-hours-375-light.png`, `evidence/AT-12/front-door-last-hours-768-dark.png`, `evidence/AT-12/front-door-last-hours-768-light.png`, `evidence/AT-12/front-door-open-1280-dark.png`, `evidence/AT-12/front-door-open-1280-light.png`, `evidence/AT-12/front-door-open-375-dark.png`, `evidence/AT-12/front-door-open-375-light.png`, `evidence/AT-12/front-door-open-768-dark.png`, `evidence/AT-12/front-door-open-768-light.png`, `evidence/AT-12/sheet-closed-1280-dark.png`, `evidence/AT-12/sheet-closed-1280-light.png`, `evidence/AT-12/sheet-closed-375-dark.png`, `evidence/AT-12/sheet-closed-375-light.png`, `evidence/AT-12/sheet-closed-768-dark.png`, `evidence/AT-12/sheet-closed-768-light.png`, `evidence/AT-12/sheet-find-flag-on-closed-375-light.png`, `evidence/AT-12/sheet-find-flag-on-last-hours-375-light.png`, `evidence/AT-12/sheet-find-flag-on-open-375-light.png`, `evidence/AT-12/sheet-last-hours-1280-dark.png`, `evidence/AT-12/sheet-last-hours-1280-light.png`, `evidence/AT-12/sheet-last-hours-375-dark.png`, `evidence/AT-12/sheet-last-hours-375-light.png`, `evidence/AT-12/sheet-last-hours-768-dark.png`, `evidence/AT-12/sheet-last-hours-768-light.png`, `evidence/AT-12/sheet-open-1280-dark.png`, `evidence/AT-12/sheet-open-1280-light.png`, `evidence/AT-12/sheet-open-375-dark.png`, `evidence/AT-12/sheet-open-375-light.png`, `evidence/AT-12/sheet-open-768-dark.png`, `evidence/AT-12/sheet-open-768-light.png`
Observation: `search.txt` lists 15 text dumps: the front door, the open Trade Wire sheet, and the analyzer at the three times with the shipped config, and the analyzer in Find mode and the sheet with the flag on at the three times. Each dump holds `body.innerText` plus every aria-label, alt, title, and placeholder, and each has 0 hits of Lock, Rosters are locked, Deadline Board, feed, Jev, Advisor, Finder, or Brian (case as written). In two analyzer dumps the teams still load ("Loading the teams…"). The shots cover the shipped pages at 3 sizes and 2 themes, and the flag-on pages at 375 light.

## AT-13: The Trade Wire route reads a trade in full

App: api
Commit: `98d79f98`
Then: Trade W shows both teams with name and avatar, the players each team gets with positions, $5 of FAAB to roster 8, and no draft picks.
Files: `evidence/AT-13/api.log`, `evidence/AT-13/output.txt`, `evidence/AT-13/sleeper-leg-9.json`, `evidence/AT-13/wire_leg9.py.txt`
Observation: The real API app, with only its Trade Wire read pinned to Sleeper leg 9 (`wire_leg9.py.txt`), answers `leg: 9` with 2 trades. Trade W shows NFC Least (roster 4) and Return of T Mac (roster 8), each with a name and an avatar URL, the players each team gets with positions, `faab: 5` for roster 8 and 0 for roster 4, and no key for draft picks (output.txt). The Sleeper answer of W has `waiver_budget` [{amount 5, sender 4, receiver 8}] and `draft_picks` [] (sleeper-leg-9.json). This API ran with no Jev key, so the log shows failed fair requests of its warm-up and no Jev cost (api.log).

## AT-14: The Trade Wire lists only accepted week 11 trades, newest first

App: api
Commit: `98d79f98`
Then: Each trade in the answer has leg 11 and status `complete`, in descending order of acceptance time, and no week 9 trade shows.
Files: `evidence/AT-14/api.log`, `evidence/AT-14/output.txt`, `evidence/AT-14/sleeper-leg-11.json`, `evidence/AT-14/sleeper-state.txt`
Observation: Sleeper state gives leg 11, and the raw leg 11 answer of 2026-11-20 holds 15 transactions: 11 `free_agent` complete, 3 `waiver` complete, and 1 `waiver` failed, so no trade (sleeper-leg-11.json). The route answers `leg: 11` and `trades: []` (output.txt), so no week 9 trade shows; with no trade in the list, the order of acceptance has nothing to show.

## AT-15: The Trade Wire route keeps its answer for 5 s

App: api
Commit: `98d79f98`
Then: The log shows one Sleeper read for the first two calls and a second Sleeper read for the call at 6 s.
Files: `evidence/AT-15/output.txt`
Observation: The call at 0.44 s logs two Sleeper reads (`state/nfl` and `transactions/11?t=...`). The call at 2.22 s logs no Sleeper read. The call at 6.32 s logs the two reads again (output.txt, with the httpx log lines).

## AT-16: The Trade Wire route needs the passphrase

App: api
Commit: `98d79f98`
Then: The route answers 401 with no trades.
Files: `evidence/AT-16/output.txt`
Observation: A call with no passphrase header answers `HTTP/1.1 401 Unauthorized` with `content-length: 0` (output.txt).

## AT-17: The Trade Wire route takes many phones on one IP

App: api
Commit: `98d79f98`
Then: All 40 calls answer 200.
Files: `evidence/AT-17/control.txt`, `evidence/AT-17/output.txt`
Observation: With `CORNERSTONE_RATE_LIMIT_PER_MINUTE=30`, 40 calls from 127.0.0.1 between 16:16:24 and 16:17:21 all answer 200 (output.txt). On the same API, 35 quick calls of the counted teams route answer 422 thirty times (the calls send no season) and then 429 five times, so the limit is live (control.txt).

## AT-18: The sheet holds the parts in order

App: site
Commit: `98d79f98`
Then: From the top, the sheet shows "Grade a trade" and "Find a trade", "TRADE DEADLINE ~2d 14h 05m", "Trade Wire", the live dot with "Updated", and trade W.
Files: `evidence/AT-18/iphone-15-390x660.json`, `evidence/AT-18/measure.jsonl`, `evidence/AT-18/1280-dark.png`, `evidence/AT-18/1280-light.png`, `evidence/AT-18/375-dark.png`, `evidence/AT-18/375-light.png`, `evidence/AT-18/768-dark.png`, `evidence/AT-18/768-light.png`
Observation: With the flag on and trade W served, the parts inside the sheet come in this DOM order (index among the elements of the sheet) and this top on the screen at 375 light: "Grade a trade" (4, top 610.2) and "Find a trade" (5, top 610.2) side by side, the eyebrow "Trade deadline ~2d 14h 05m" (7, top 666.2, shown upper case), "Trade Wire" (9, top 684), the live dot with "Updated 0s ago" (10, top 689.4), and trade W (15, top 720.6) (measure.jsonl `partsInOrder`, one line per size and theme).

## AT-19: The Trade Wire rows have even gaps

App: site
Commit: `98d79f98`
Then: Inside each trade the gaps are 8 px, and the gaps between trades are equal, each within 1 px.
Files: `evidence/AT-19/iphone-15-390x660.json`, `evidence/AT-19/measure.jsonl`, `evidence/AT-19/1280-dark.png`, `evidence/AT-19/1280-light.png`, `evidence/AT-19/375-dark.png`, `evidence/AT-19/375-light.png`, `evidence/AT-19/768-dark.png`, `evidence/AT-19/768-light.png`
Observation: With trade W and the other real leg 9 trade served, each trade has 3 rows with gaps of 8 px and 8 px at each size and theme. The one gap between the two trades is 33 px (16 px pad, 1 px rule, 16 px pad), and the first line sits 16 px under the top rule (measure.jsonl). With two trades there is one gap between trades, so no second gap to compare.

## AT-20: A new trade slides in

App: site
Commit: `98d79f98`
Then: Within 15 s, trade W shows at the top and the badge changes from "1 new" to "2 new".
Files: `evidence/AT-20/iphone-15-390x660.json`, `evidence/AT-20/measure.jsonl`, `evidence/AT-20/after-1280-dark.png`, `evidence/AT-20/after-1280-light.png`, `evidence/AT-20/after-375-dark.png`, `evidence/AT-20/after-375-light.png`, `evidence/AT-20/after-768-dark.png`, `evidence/AT-20/after-768-light.png`, `evidence/AT-20/before-1280-dark.png`, `evidence/AT-20/before-1280-light.png`, `evidence/AT-20/before-375-dark.png`, `evidence/AT-20/before-375-light.png`, `evidence/AT-20/before-768-dark.png`, `evidence/AT-20/before-768-light.png`
Observation: The route first serves the other trade (badge "1 new"), then serves W and the other trade. Trade W shows at the top 8.21 to 8.53 s after the route change at each size and theme, and the badge reads "2 new" (measure.jsonl: `secondsToShow`, `badgeBefore`, `badgeAfter`, `orderAfter`, route calls with times). The `before` and `after` shots show the change.

## AT-21: The Trade Wire shows when it last updated

App: site
Commit: `98d79f98`
Then: The sheet shows the live dot and "Updated 3s ago".
Files: `evidence/AT-21/iphone-15-390x660.json`, `evidence/AT-21/measure.jsonl`, `evidence/AT-21/1280-dark.png`, `evidence/AT-21/1280-light.png`, `evidence/AT-21/375-dark.png`, `evidence/AT-21/375-light.png`, `evidence/AT-21/768-dark.png`, `evidence/AT-21/768-light.png`
Observation: The page samples the live line each 100 ms across a poll, timed by the page clock from the first "Updated 0s ago". "Updated 3s ago" first shows at 2.98 to 3.09 s, and the text at 3.0 s is "Updated 3s ago" at each size and theme; "1s" shows at 0.94 to 1.02 s and "4s" at 3.94 to 4.03 s (measure.jsonl `firstSampleOf`, `textAt3_0s`). The live dot is present (1 element).

## AT-22: The poll stops when the tab hides and runs when it shows

App: site
Commit: `98d79f98`
Then: No route call goes out while the tab hides, and one goes out within 1 s of the show.
Files: `evidence/AT-22/network-log.json`
Observation: Route calls go out at -12.6 s and -2.52 s before the hide, none in the 30 s while the tab is hidden, and one at 0 s after the show (network-log.json). The tab hides by an override of `document.visibilityState` and a `visibilitychange` event.

## AT-23: The empty Trade Wire says so

App: site
Commit: `98d79f98`
Then: The sheet reads "No trades yet this week."
Files: `evidence/AT-23/iphone-15-390x660.json`, `evidence/AT-23/measure.jsonl`, `evidence/AT-23/1280-dark.png`, `evidence/AT-23/1280-light.png`, `evidence/AT-23/375-dark.png`, `evidence/AT-23/375-light.png`, `evidence/AT-23/768-dark.png`, `evidence/AT-23/768-light.png`
Observation: With no week 11 trade served at 09:55:00 Eastern on Sat 2026-11-21, the sheet shows "No trades yet this week." at each size and theme (measure.jsonl, shots).

## AT-24: The empty Trade Wire after the Lock says so

App: site
Commit: `98d79f98`
Then: The sheet reads "No trades this week."
Files: `evidence/AT-24/iphone-15-390x660.json`, `evidence/AT-24/measure.jsonl`, `evidence/AT-24/1280-dark.png`, `evidence/AT-24/1280-light.png`, `evidence/AT-24/375-dark.png`, `evidence/AT-24/375-light.png`, `evidence/AT-24/768-dark.png`, `evidence/AT-24/768-light.png`
Observation: With no week 11 trade served at 00:00:01 Eastern on Tue 2026-11-24, the sheet shows "No trades this week." and no trade link at each size and theme (measure.jsonl, shots).

## AT-25: A failed read keeps the list

App: site
Commit: `98d79f98`
Then: Trade W stays, and a short note says that the last read failed.
Files: `evidence/AT-25/measure.jsonl`, `evidence/AT-25/1280-dark.png`, `evidence/AT-25/1280-light.png`, `evidence/AT-25/375-dark.png`, `evidence/AT-25/375-light.png`, `evidence/AT-25/768-dark.png`, `evidence/AT-25/768-light.png`
Observation: The first route call answers 200 with trade W, the next poll, 10 s later, answers 500. After it, trade W is still visible and the sheet shows "The last update failed." at each size and theme (measure.jsonl with the route calls and their status, shots).

## AT-26: "Grade a trade" opens Grade mode

App: site
Commit: `98d79f98`
Then: The analyzer opens with "Grade a trade" selected in the switch.
Files: `evidence/AT-26/measure-flag-off.jsonl`, `evidence/AT-26/measure-flag-on.jsonl`, `evidence/AT-26/flag-off-1280-dark.png`, `evidence/AT-26/flag-off-1280-light.png`, `evidence/AT-26/flag-off-375-dark.png`, `evidence/AT-26/flag-off-375-light.png`, `evidence/AT-26/flag-off-768-dark.png`, `evidence/AT-26/flag-off-768-light.png`, `evidence/AT-26/flag-on-1280-dark.png`, `evidence/AT-26/flag-on-1280-light.png`, `evidence/AT-26/flag-on-375-dark.png`, `evidence/AT-26/flag-on-375-light.png`, `evidence/AT-26/flag-on-768-dark.png`, `evidence/AT-26/flag-on-768-light.png`
Observation: A tap on "Grade a trade" in the sheet opens `/analyze/?mode=grade`. With the flag on, the hero has the radiogroup "Mode" with "Grade a trade" checked and the title "Trade Analyzer" (measure-flag-on.jsonl, `flag-on-*` shots). With the flag off (the shipped config), the same URL opens the "Trade Analyzer" hero with no Mode switch on the page (measure-flag-off.jsonl, `flag-off-*` shots).

## AT-27: "Find a trade" hides while the `finder` flag is off

App: site
Commit: `98d79f98`
Then: The sheet shows "Grade a trade" and no "Find a trade".
Files: `evidence/AT-27/iphone-15-390x660.json`, `evidence/AT-27/measure.jsonl`, `evidence/AT-27/1280-dark.png`, `evidence/AT-27/1280-light.png`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/375-light.png`, `evidence/AT-27/768-dark.png`, `evidence/AT-27/768-light.png`
Observation: With the shipped config (flag off) and trade W served, the only link in the sheet is "Grade a trade" at each size and theme (measure.jsonl `links`, shots).

## AT-28: "Find a trade" opens Find mode

App: site
Commit: `98d79f98`
Then: The analyzer opens with "Find a trade" selected, the title "Trade Ideas", and the line "Who has a trade for you?".
Files: `evidence/AT-28/measure.jsonl`, `evidence/AT-28/1280-dark.png`, `evidence/AT-28/1280-light.png`, `evidence/AT-28/375-dark.png`, `evidence/AT-28/375-light.png`, `evidence/AT-28/768-dark.png`, `evidence/AT-28/768-light.png`
Observation: With the flag on, a tap on "Find a trade" in the sheet opens `/analyze/?mode=find`, with "Find a trade" checked in the radiogroup "Mode", the title "Trade Ideas", and the line "Who has a trade for you?" at each size and theme (measure.jsonl, shots).

## AT-29: The trade links hide after the Lock

App: site
Commit: `98d79f98`
Then: The sheet shows neither "Grade a trade" nor "Find a trade".
Files: `evidence/AT-29/iphone-15-390x660.json`, `evidence/AT-29/measure.jsonl`, `evidence/AT-29/1280-dark.png`, `evidence/AT-29/1280-light.png`, `evidence/AT-29/375-dark.png`, `evidence/AT-29/375-light.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/768-light.png`
Observation: With the flag on at 00:00:01 Eastern on Tue 2026-11-24, the sheet holds no link (`linksInSheet: []`) at each size and theme (measure.jsonl, shots).

## AT-30: A drag up does not lift the sheet off the bottom

App: site
Commit: `98d79f98`
Then: The bottom edge of each sheet stays at the bottom of the viewport, within 1 px.
Files: `evidence/AT-30/measure.jsonl`, `evidence/AT-30/team-sheet-drag-1280-dark.png`, `evidence/AT-30/team-sheet-drag-1280-light.png`, `evidence/AT-30/team-sheet-drag-375-dark.png`, `evidence/AT-30/team-sheet-drag-375-light.png`, `evidence/AT-30/team-sheet-drag-768-dark.png`, `evidence/AT-30/team-sheet-drag-768-light.png`, `evidence/AT-30/trade-wire-drag-1280-dark.png`, `evidence/AT-30/trade-wire-drag-1280-light.png`, `evidence/AT-30/trade-wire-drag-375-dark.png`, `evidence/AT-30/trade-wire-drag-375-light.png`, `evidence/AT-30/trade-wire-drag-768-dark.png`, `evidence/AT-30/trade-wire-drag-768-light.png`
Observation: During a 200 px drag up of the grip, at each size and theme, the dialog box of the Trade Wire and of the team sheet moves up: its bottom edge sits at 877.4 to 877.5 px in a viewport of 900, a gap of 22.5 to 22.6 px. The bleed is a child `[data-slot=sheet-bleed]` with `aria-hidden=true`, 96 px high from 877.5 px, with the same computed background as the box, so the visible surface (box plus bleed) reaches 973.5 px, past the bottom of the viewport, a gap of 0 (measure.jsonl, with 10 samples per drag). The shots are taken during the drag.

## AT-31: The analyzer switch is the ui-sdk SegmentedControl

App: site
Commit: `98d79f98`
Then: The hero shows "Grade a trade · Find a trade" across its full width in two halves whose widths differ by 1 px or less.
Files: `evidence/AT-31/imports.txt`, `evidence/AT-31/iphone-15-390x660.json`, `evidence/AT-31/measure.jsonl`, `evidence/AT-31/1280-dark.png`, `evidence/AT-31/1280-light.png`, `evidence/AT-31/375-dark.png`, `evidence/AT-31/375-light.png`, `evidence/AT-31/768-dark.png`, `evidence/AT-31/768-light.png`
Observation: With the flag on, `[aria-label=Mode]` has the role radiogroup and two radio items, "Grade a trade" and "Find a trade". The two halves are 140.5 px each at 375, 273 px at 768, and 313 px at 1280 (difference 0), and the switch spans the inner width of the hero less 1 px each side (measure.jsonl). `imports.txt` shows `mode-switch.tsx` imports `@cpc/design/ui/segmented-control`, and only that wrapper imports `@ui-sdk/react/segmented-control`.

## AT-32: The switch locks during a wait

App: site
Commit: `98d79f98`
Then: The switch stays on "Find a trade", and the wait goes on.
Files: `evidence/AT-32/measure.jsonl`, `evidence/AT-32/1280-dark.png`, `evidence/AT-32/1280-light.png`, `evidence/AT-32/375-dark.png`, `evidence/AT-32/375-light.png`, `evidence/AT-32/768-dark.png`, `evidence/AT-32/768-light.png`
Observation: With the find stream held (no answer), after a tap on "Find a Trade" and then a tap on "Grade a trade", the radiogroup has `aria-disabled=true`, "Find a trade" keeps `aria-checked=true`, "Grade a trade" keeps `aria-checked=false`, the URL stays `/analyze/?mode=find`, and the "Finding Trades" wait still shows at each size and theme (measure.jsonl, shots).

## AT-33: Find mode shows the partner choice and the position chips

App: site
Commit: `98d79f98`
Then: The hero shows the partner choice of one team or every team, and the chips "Any · RB · WR · TE · QB".
Files: `evidence/AT-33/measure.jsonl`, `evidence/AT-33/1280-dark.png`, `evidence/AT-33/1280-light.png`, `evidence/AT-33/375-dark.png`, `evidence/AT-33/375-light.png`, `evidence/AT-33/768-dark.png`, `evidence/AT-33/768-light.png`
Observation: With the flag on and Bo Girds as Your team, the Find hero reads "Trade Ideas", "Who has a trade for you?", YOUR TEAM Bo Girds, TRADE WITH "Every team" with "Change", the chips "Any RB WR TE QB", and "Find a Trade" at each size and theme (measure.jsonl, shots).

## AT-34: The analyzer shows the deadline eyebrow

App: site
Commit: `98d79f98`
Then: The hero eyebrow reads "Trade deadline ~2d 14h 05m", then "The trade deadline has passed".
Files: `evidence/AT-34/iphone-15-390x660.json`, `evidence/AT-34/measure.jsonl`, `evidence/AT-34/closed-1280-dark.png`, `evidence/AT-34/closed-1280-light.png`, `evidence/AT-34/closed-375-dark.png`, `evidence/AT-34/closed-375-light.png`, `evidence/AT-34/closed-768-dark.png`, `evidence/AT-34/closed-768-light.png`, `evidence/AT-34/open-1280-dark.png`, `evidence/AT-34/open-1280-light.png`, `evidence/AT-34/open-375-dark.png`, `evidence/AT-34/open-375-light.png`, `evidence/AT-34/open-768-dark.png`, `evidence/AT-34/open-768-light.png`
Observation: On `/analyze/` the hero eyebrow reads "TRADE DEADLINE ~2d 14h 05m" at 09:55:00 Eastern on Sat 2026-11-21 and "THE TRADE DEADLINE HAS PASSED" at 00:00:01 Eastern on Tue 2026-11-24 (upper case by style) at each size and theme (measure.jsonl, `open-*` and `closed-*` shots).

## AT-35: A chip sets the same limit as a typed question

App: site
Commit: `98d79f98`
Then: The find request has `aim_position` "RB", the same value that the front door sends for "trade ideas for an RB".
Files: `evidence/AT-35/front-door.json`, `evidence/AT-35/measure.jsonl`, `evidence/AT-35/rb-1280-dark.png`, `evidence/AT-35/rb-1280-light.png`, `evidence/AT-35/rb-375-dark.png`, `evidence/AT-35/rb-375-light.png`, `evidence/AT-35/rb-768-dark.png`, `evidence/AT-35/rb-768-light.png`
Observation: With the flag on, a tap on the chip "RB" and on "Find a Trade" sends the body `{"season": 2026, "asker": 6, "limit": {"aim_position": "RB"}}` (measure.jsonl, each size and theme; the `rb-*` shots show RB picked). On the front door, the typed question "trade ideas for an RB" sends `{"roster_id":6,"partner":null,"question":"trade ideas for an RB","turns":[]}` to `/trade-ideas`, and the API stream answers with the part `data-limit` `{"keep_positions": [], "keep_players": [], "aim_position": "RB"}` (front-door.json). So both reach the Limit `aim_position` "RB"; the front door sends the question and the API reads the value from it.

## AT-36: The Finder wait shows the real steps in `StageLines`

App: site
Commit: `2e9f0f85`
Then: One line at a time shows each real step with the counts of the press, such as "3 of 5 · Checking 9,412 trades for fairness". Each step line stays on screen at least about 1.5 s and holds until the next step starts, and step 5 changes its line as AT-73 says.
Files: `evidence/AT-36/api-presses.log`, `evidence/AT-36/api.sh.txt`, `evidence/AT-36/cache-cleared.txt`, `evidence/AT-36/line-1-1280-dark.png`, `evidence/AT-36/line-1-1280-light.png`, `evidence/AT-36/line-1-375-dark.png`, `evidence/AT-36/line-1-375-light.png`, `evidence/AT-36/line-1-768-dark.png`, `evidence/AT-36/line-1-768-light.png`, `evidence/AT-36/line-2-1280-dark.png`, `evidence/AT-36/line-2-1280-light.png`, `evidence/AT-36/line-2-375-dark.png`, `evidence/AT-36/line-2-375-light.png`, `evidence/AT-36/line-2-768-dark.png`, `evidence/AT-36/line-2-768-light.png`, `evidence/AT-36/measure.jsonl`, `evidence/AT-36/press.sh.txt`, `evidence/AT-36/pw.config.mjs.txt`, `evidence/AT-36/stagelines-dom.html`, `evidence/AT-36/stream-1280-dark.txt`, `evidence/AT-36/stream-1280-light.txt`, `evidence/AT-36/stream-375-dark.txt`, `evidence/AT-36/stream-375-light.txt`, `evidence/AT-36/stream-768-dark.txt`, `evidence/AT-36/stream-768-light.txt`, `evidence/AT-36/warm-up.txt`, `evidence/AT-36/zz-deadline-evidence-r2.spec.mjs.txt`
Observation: Six real presses, one per size and theme, for Bo Girds and every team against the evidence API, after the warm-up line, with the result cache emptied before each (cache-cleared.txt). In each press the wait shows one line at a time (measure.jsonl `lineTextWithSecondsFromTap`): "1 of 5 · Reading 11 teams" from the tap for 2.50 to 2.81 s, then "2 of 5 · Matching trade value", "3 of 5 · Checking 4,307 trades for fairness", "4 of 5 · Checking 202 against both lineups", and "5 of 5 · Picking the best 5", each held 1.50 to 1.51 s. The stream sent the live lines of steps 2 to 4 within 0.19 s and step 5 at 5.24 to 5.82 s (`stepEventsWithSecondsFromTap` and the stream files), so each line waits for the hold of the line before it. After the step 5 line come the step 5 lines of AT-73, and "5 of 5 · Picking the best 5" shows again when the first card lands. `stagelines-dom.html` shows the `StageLines` part (`t-think`) with the step 3 line. The `line-1` shots show the step 1 line, and the `line-2` shots show the step 3 line. `api-presses.log` holds the API log of the six presses, with six press lines and 178 TypeSafe answers of 200.

## AT-37: The team avatars light up in turn

App: site
Commit: `98d79f98`
Then: The avatars light up one after another, in the order of the stream.
Files: `evidence/AT-37/measure.jsonl`, `evidence/AT-37/1280-dark.png`, `evidence/AT-37/1280-light.png`, `evidence/AT-37/375-dark.png`, `evidence/AT-37/375-light.png`, `evidence/AT-37/768-dark.png`, `evidence/AT-37/768-light.png`
Observation: In each of the six presses of AT-36 the avatars light one by one in the order of the stream parts `data-team` (for example 10, 2, 3, 4, 12, 5, 1, 8, 9, 11, 7 at 375 light), all within 0.18 to 0.38 s, from 2.55 to 7.73 s after the tap (measure.jsonl: lit avatars with seconds, and the stream order, which match in each press). The shots show the wait with the lit row.

## AT-38: The Finder trades show as cards with the Lean and a short Case

App: site
Commit: `98d79f98`
Then: Up to 5 cards show in one list under the hero, each with a Lean of Send it, Lean yes, or Gut call, a Case of at most 3 lines, folded Bullets, and no headline.
Files: `evidence/AT-38/find-answer-1280-dark.json`, `evidence/AT-38/find-answer-1280-light.json`, `evidence/AT-38/find-answer-375-dark.json`, `evidence/AT-38/find-answer-375-light.json`, `evidence/AT-38/find-answer-768-dark.json`, `evidence/AT-38/find-answer-768-light.json`, `evidence/AT-38/measure.jsonl`, `evidence/AT-38/1280-dark.png`, `evidence/AT-38/1280-light.png`, `evidence/AT-38/375-dark.png`, `evidence/AT-38/375-light.png`, `evidence/AT-38/768-dark.png`, `evidence/AT-38/768-light.png`
Observation: The six results of AT-36 land as 5 cards (375 light, 375 dark, 1280 light, 1280 dark) or 4 cards (768 light, 768 dark, where the pick kept 4) in one list `ol[aria-label="Trade ideas"]` under the hero. Each card leads with its Lean (Send it, Lean yes, or Gut call), has a Case of 2 or 3 rendered lines with a clamp of 3, Bullets folded behind "Why it works", and no heading other than the Lean (measure.jsonl, find-answer files, full-page shots).

## AT-39: A tap on a card opens the trade already graded

App: site
Commit: `98d79f98`
Then: The analyzer shows that trade in Grade mode with its read, and no analyze request goes out.
Files: `evidence/AT-39/measure.jsonl`, `evidence/AT-39/1280-dark.png`, `evidence/AT-39/1280-light.png`, `evidence/AT-39/375-dark.png`, `evidence/AT-39/375-light.png`, `evidence/AT-39/768-dark.png`, `evidence/AT-39/768-light.png`
Observation: A tap on "See the Full Result" of the first card, after the answer lands, opens `/analyze/?mode=grade` with the read of that card (hero title "Send it" or "Lean yes", the Lean of the card) at each size and theme. In the 3 s after the tap the page makes 0 API requests and 0 analyze requests (measure.jsonl, full-page shots).

## AT-40: A failed find shows Try Again

App: site
Commit: `98d79f98`
Then: The hero shows the error line and a "Try Again" button.
Files: `evidence/AT-40/measure.jsonl`, `evidence/AT-40/1280-dark.png`, `evidence/AT-40/1280-light.png`, `evidence/AT-40/375-dark.png`, `evidence/AT-40/375-light.png`, `evidence/AT-40/768-dark.png`, `evidence/AT-40/768-light.png`
Observation: With the find route answering 500, after a tap on "Find a Trade" the hero shows "The API did not answer. Try again." and the button "Try Again" at each size and theme (measure.jsonl, shots).

## AT-41: A press runs one pick call with no id retry

App: api
Commit: `98d79f98`
Then: Each press runs one pick call, and no id retry line shows in the log.
Files: `evidence/AT-41/api-presses.sh.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press.py.txt`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: After the warm-up line `Fair warm-up of cpc ended: 105876 questions, 105876 asked ... $1.3639, 375.1s` (warm-up.txt), three presses for Bo Girds and every team, with the result cache emptied before each, take 55.6 s, 50.3 s, and 41.8 s on the server. Each logs `claude_calls=1`, one `FinderPickOut call` line, and no retry, repair, or id line (press-N-api.log). The Claude cost is $0.1656, $0.1519, and $0.1489, and the Jev cost is about $0.0076 per press (181,549 to 181,600 tokens in the Jev wave lines). In the browser presses of AT-36 on the same API, 2 of 12 presses logged a repair of a number in the Case (`finder pick 4 failed: pick # case: number # is not in the cited facts`, then `finder repair of pick 4 passed`), with `claude_calls=2` and `claude_calls=3`.

## AT-42: Retired. One picked partner skips the Partner filter
Retired: the Spares tree gates no partner, and the targets step is gone (decisions 15 and 16).

App: api
Then: The log shows no Partner filter step, and the targets build 2 or more offers before the gain check.
Files: none
Observation: The title holds the word Retired, so the round records no evidence (decisions 15 and 16).

## AT-43: The Shortlist has variety

App: api
Commit: `98d79f98`
Then: The best offer of each shape direction comes first, then the best offer of each partner, then the best offer of each player of Bo Girds, before a second form of any trade.
Files: `evidence/AT-43/shortlist.txt`, `evidence/AT-41/at43.py.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`
Observation: Read against the Then line, the Shortlist of each of the 3 presses of AT-41 holds 10 offers in the same order (shortlist.txt, from the Shortlist dumps). Offers 1 to 3 are the first of each of the 3 shape directions that pass step 2 (1-for-2, 2-for-3, 1-for-3; 16 offers pass step 2 and the gain check, and none has another shape). Offers 4 to 6 bring the partners not shown before (Return of T Mac, Unsolicited Dak Picks, Lil Fridge), and offer 7 brings the last player of Bo Girds not shown before (Kyren Williams). Offers 8 to 10 bring no new shape, partner, or player. Each first offer has the best fair mean of its key (0.970, or 0.960 for Lil Fridge).

## AT-44: The Spares tree lists a player only with cover who can play now

App: pipeline
Commit: `98d79f98`
Then: A starter at RB of the test roster is not listed, and each listed player in the run has a backup above the line who can play now.
Files: `evidence/AT-44/output.txt`, `evidence/AT-44/spares-week11.txt`, `evidence/AT-44/spares_week11.py.txt`
Observation: Both Spares tree tests pass (output.txt): each listed player has a backup at his position above the line who can play now, and a test roster whose only RB backup is Out lists no RB. The tests read the week 6 fixture snapshot, not week 11. On the live week 11 snapshot of cpc, `spare_list` over all 132 ordered pairs lists 672 players, and 0 of them lack a backup at the position who can cover now by `can_cover` (spares-week11.txt).

## AT-45: A clear no stops, an unsure answer passes, and a failed call is an error

App: pipeline
Commit: `98d79f98`
Then: 0.2 drops the offer, 0.5 keeps it, and the failed call raises an error, not a drop.
Files: `evidence/AT-45/output.txt`
Observation: 7 decision tests pass (output.txt, with the source of each test). In step 2, a gain of 0.2 drops the offer and 0.5 keeps it, and a failed step 2 call of one offer raises an error and does not read as a drop. In the fair step, a mean of 0.25 drops and 0.35 stays, and a failed fair request drops no offer. In the Spares tree, 0.2 for each listed player stops the side, an unsure answer passes, and a failed call raises an error, not a stop. The tests read the week 6 fixture rosters with the week 9 chart.

## AT-46: The two bad ideas never come back

App: api
Commit: `98d79f98`
Then: Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is among the 5 trades, and "Kenneth Walker III for Patrick Mahomes" is not on the Shortlist.
Files: `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: In none of the 3 presses of AT-41 is "Kenneth Walker III for Patrick Mahomes" or "Zay Flowers for Jared Goff" a Value offer, so neither is on the Shortlist, in a gain drop, or among the 5 trades (press-N-read.txt, `## AT-46` lines). The chart values are 62.5 for Walker, 9.5 for Mahomes, 23.0 for Flowers, and 9.0 for Goff (the Shortlist dumps), outside the 10% band of a 1-for-1. The 5 trades of each press are listed under `## AT-70` in the same files.

## AT-47: The backtest runs as one command and passes the bar

App: pipeline
Commit: `98d79f98`
Then: The output lists each mark with its result, and the count of right marks is the baseline of 1 of 5 or more.
Files: `evidence/AT-47/output.txt`
Observation: `make -C apps/pipeline backtest CLIENT=cpc` on the live week 11 lists 5 marks: 1 RIGHT (Walker for Mahomes, expect drop, got drop) and 4 WRONG (Flowers for Goff expects drop and gets keep; three Spares marks expect stop and get pass), then "Right marks: 1 of 5.", "Jev: 5 requests, $0.0004.", and exit 2 from make (output.txt).

## AT-48: A failed stream logs its cause

App: api
Commit: `98d79f98`
Then: The API logs one line with the cause, the stage, and the seconds since the start.
Files: `evidence/AT-48/output.txt`
Observation: The test cuts a real uvicorn stream of trade ideas from the client, and the API logs one line: `Trade stream failed: topic=trade_ideas cause=client-cut stage="Made a shortlist of 10" seconds=4.7` (output.txt, the command and the live log). In the background `make check`, the same test failed once with `stage="start" seconds=0.2` and an IndexError (see the header).

## AT-49: The first call of a trade Topic does not fail

App: site
Commit: `2e9f0f85`
Then: All 10 answers arrive with no retry line.
Files: `evidence/AT-49/answer-1280-dark.png`, `evidence/AT-49/answer-1280-light.png`, `evidence/AT-49/answer-375-dark.png`, `evidence/AT-49/answer-375-light.png`, `evidence/AT-49/answer-768-dark.png`, `evidence/AT-49/answer-768-light.png`, `evidence/AT-49/api-run-1.log`, `evidence/AT-49/api-run-10.log`, `evidence/AT-49/api-run-2.log`, `evidence/AT-49/api-run-3.log`, `evidence/AT-49/api-run-4.log`, `evidence/AT-49/api-run-5.log`, `evidence/AT-49/api-run-6.log`, `evidence/AT-49/api-run-7.log`, `evidence/AT-49/api-run-8.log`, `evidence/AT-49/api-run-9.log`, `evidence/AT-49/api.sh.txt`, `evidence/AT-49/at49.sh.txt`, `evidence/AT-49/pw.config.mjs.txt`, `evidence/AT-49/run-1.json`, `evidence/AT-49/run-10-390x660.png`, `evidence/AT-49/run-10.json`, `evidence/AT-49/run-2.json`, `evidence/AT-49/run-3.json`, `evidence/AT-49/run-4.json`, `evidence/AT-49/run-5.json`, `evidence/AT-49/run-6.json`, `evidence/AT-49/run-7-390x660.png`, `evidence/AT-49/run-7.json`, `evidence/AT-49/run-8-390x660.png`, `evidence/AT-49/run-8.json`, `evidence/AT-49/run-9-390x660.png`, `evidence/AT-49/run-9.json`, `evidence/AT-49/runs.txt`, `evidence/AT-49/warm-up.txt`, `evidence/AT-49/zz-deadline-evidence-r2.spec.mjs.txt`
Observation: One fresh evidence API of `2e9f0f85` served all 10 asks, and the 10 asks were its first 10 grades (runs.txt, warm-up.txt). Each run opened the front door of cpc in a fresh browser context with Bo Girds as Your team, tapped More, then the Trade ideas Topic, with the result cache emptied first. All 10 runs end with the trade ideas answer in 41.6 to 57.3 s (run-<n>.json `outcome`, `secondsToAnswer`). Each run has 0 retry lines on the page and one POST /trade-ideas that answers 200. The API log of each run has 0 lines "Trade stream failed" and 0 lines with 429 (api-run-<n>.log). The server press of each run takes 37.5 to 51.4 s, and run 2 logs `claude_calls=2`. Runs 1 to 6 give the shots `answer-375-light` to `answer-1280-dark`, which show the answer with its cards, and runs 7 to 10 give `run-<n>-390x660` in the iPhone 15 context.

## AT-50: The Lock is one value in the client config

App: site
Commit: `98d79f98`
Then: The Deadline banner shows the last-hours state with "~1h 00m 00s".
Files: `evidence/AT-50/config.diff`, `evidence/AT-50/iphone-15-390x660.json`, `evidence/AT-50/measure.jsonl`, `evidence/AT-50/1280-dark.png`, `evidence/AT-50/1280-light.png`, `evidence/AT-50/375-dark.png`, `evidence/AT-50/375-light.png`, `evidence/AT-50/768-dark.png`, `evidence/AT-50/768-light.png`
Observation: In a local build with the Lock at `2026-11-21T10:55:00-05:00` (config.diff), at 09:55:00 Eastern on Sat 2026-11-21 the banner has `data-phase` `last-hours` and reads "~1h 00m 00s" at each size and theme (measure.jsonl, shots). The iPhone 15 check reads no overlap. The config is back as committed (AT-51).

## AT-51: The `finder` flag of CPC stays off

App: site
Commit: `98d79f98`
Then: The `finder` flag is `false`.
Files: `evidence/AT-51/output.txt`
Observation: `clients/cpc/client.toml` at `98d79f98` holds `finder = false` on line 22 (output.txt). The local builds with the flag on and with the Lock moved changed the file and put it back; `git status` shows no change to it.

## AT-52: No Deadline Board ships

App: site
Commit: `98d79f98`
Then: Both pages answer 404, and no link to a Deadline Board exists.
Files: `evidence/AT-52/status.txt`
Observation: On the cpc export of `98d79f98` served with the 404 rule, `/deadline/` and `/deadline-board/` each answer 404. A search of the export finds 0 files with "deadline-board" or "deadline board", 0 links to `/deadline`, and no folder named deadline (status.txt).

## AT-53: The Finder offers no three-team trade

App: site
Commit: `98d79f98`
Then: The hero has no choice of two or three teams.
Files: `evidence/AT-53/measure.jsonl`, `evidence/AT-53/1280-dark.png`, `evidence/AT-53/1280-light.png`, `evidence/AT-53/375-dark.png`, `evidence/AT-53/375-light.png`, `evidence/AT-53/768-dark.png`, `evidence/AT-53/768-light.png`
Observation: With the flag on, the Find hero holds Your team, Trade with (Every team), the position chips, and "Find a Trade", and its text has no choice of two or three teams at each size and theme (measure.jsonl `teamCountChoice: false`, shots).

## AT-54: Next.js stays at its version

App: site
Commit: `98d79f98`
Then: The version is the same.
Files: `evidence/AT-54/output.txt`
Observation: `apps/site/package.json` has `"next": "^16.4.5"` on `main` (`1fc0a06e`) and on `98d79f98`, and the diff of `package.json` and `pnpm-lock.yaml` has no `next` line (output.txt). The installed version in the worktree is 16.4.5.

## AT-55: The Value offers hold every shape in both directions

App: api
Commit: `98d79f98`
Then: The Value offers include all 7 shape directions: 1-for-1, 2-for-1, 1-for-2, 3-for-1, 1-for-3, 3-for-2, and 2-for-3.
Files: `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: Each of the 3 presses of AT-41 logs `Finder Value offers of Bo Girds: 5571; 1-for-1=59, 2-for-1=104, 1-for-2=363, 3-for-1=62, 1-for-3=661, 3-for-2=1126, 2-for-3=3196` (press-N-api.log), and the count from the Shortlist dump gives the same 7 counts (press-N-read.txt, `## AT-55`).

## AT-56: Each Value offer is inside the band with its direction

App: api
Commit: `98d79f98`
Then: On each uneven offer, the side that gets more players has 100% to 125% of the other sum, and each 1-for-1 is within 10% either way.
Files: `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: In each of the 3 presses, the read checks the chart sums of all 5,571 Value offers, and 0 are outside the band. The ratio of the side with more players to the other, or of the larger to the smaller side of a 1-for-1, runs from 1.0000 to 1.2500 (press-N-read.txt, `## AT-56`).

## AT-57: No filler and no player without a chart value

App: api
Commit: `98d79f98`
Then: No player under 5 trade value sits on a side of 2 or 3 players, and Justin Herbert is in no Value offer.
Files: `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: In each of the 3 presses, the lowest chart value on a side of 2 or 3 players is 5.0 (Adonai Mitchell), 0 players of a Value offer lack a chart value, and 0 Value offers hold Justin Herbert (press-N-read.txt, `## AT-57`).

## AT-58: The fair check reads the chart facts in both side orders

App: pipeline
Commit: `98d79f98`
Then: Each fair request holds `chart_value` and `chart_sum`, answers of 0.2 and 0.3 drop the offer, and answers of 0.1 and 0.6 keep it.
Files: `evidence/AT-58/fair-request-payload.txt`, `evidence/AT-58/fair_payload.py.txt`, `evidence/AT-58/output.txt`
Observation: Both fair step tests pass (output.txt): every fair request holds `chart_value` for each player and `chart_sum` for each side, each offer is asked once in each side order, answers of 0.2 and 0.3 (mean 0.25) drop the offer, and 0.1 and 0.6 (mean 0.35) keep it. The tests read the week 6 fixture rosters with the week 9 chart. `fair-request-payload.txt` shows the fair request of one live week 11 Value offer (Bo Girds gives Blake Corum 17.0, Unsolicited Dak Picks gives Ollie Gordon II 16.5) in both side orders, each with `chart_value` and `chart_sum`.

## AT-59: A need answer drops no offer

App: pipeline
Commit: `98d79f98`
Then: The offer stays on the Shortlist.
Files: `evidence/AT-59/output.txt`
Observation: The test with need answers of 0.1 on both sides and a gain of 0.8 passes (output.txt, with the source of the test): no offer drops, the Shortlist holds min(SHORTLIST_KEEP, step 2) offers, and each Shortlist offer has need answers of 0.1 and 0.1. The test reads the week 6 fixture rosters with the week 9 chart.

## AT-60: Step 2 gets the best 3 offers of each group

App: api
Commit: `98d79f98`
Then: Step 2 holds at most 3 offers per partner and shape direction, no more than 231 offers, and each has one of the 3 highest fair means of its group.
Files: `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: In each of the 3 presses, step 1 checks 5,571 offers and drops 1,258 (no offer without an answer), and step 2 holds 209 offers in 72 groups of partner and shape direction, at most 3 per group. 0 step 2 offers sit outside the 3 highest fair means of their group, and every group with an offer after step 1 has a step 2 offer (press-N-read.txt, `## AT-60`, with each group, its fair means highest first, and its step 2 offers with their fair mean). The API log reads `Finder step 2 of Bo Girds: 209 offers, the 3 best of each partner and shape direction`.

## AT-61: A Spares tree yes is a fact, not a gate

App: pipeline
Commit: `98d79f98`
Then: That offer gets the fact "fills the weak slot QB, and the partner can spare him", and the count of offers stays the same.
Files: `evidence/AT-61/output.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`
Observation: The Spares tree fact test passes (output.txt, with the source of the test). With Spares tree answers of 0.9, each Shortlist offer with a listed player of the partner carries the fact "For <asker>, <name> fills the weak slot <slot>, and <partner> can spare him.", and the offers, step 2, and the Shortlist order are the same as with answers of 0.1, which give no such fact. The test takes the slot of each listed player and does not fix it to QB. It reads the week 6 fixture rosters with the week 9 chart. In the live week 11 presses of AT-41, every one of the 10 Shortlist offers carries a Spares tree "yes" for a QB that Bo Girds gets, such as `{"4046": "QB"}` for Patrick Mahomes (the `spares` field of each Shortlist offer in the dumps), and the Value screen count stays 5,571 in each press.

## AT-62: The Shortlist order follows the fair answer

App: pipeline
Commit: `98d79f98`
Then: After the best offers, the rest follow by the fair mean, highest first.
Files: `evidence/AT-62/output.txt`
Observation: Both `varied()` tests pass: after the best offers of each shape, partner, and player, the rest follow by the fair mean, highest first (output.txt).

## AT-63: A large partner splits under the 64k context

App: pipeline
Commit: `98d79f98`
Then: The partner sends 3 or more requests, each under 64,000 tokens by the estimate, and no offer passes as unsure.
Files: `evidence/AT-63/output.txt`
Observation: The request test with one partner of 1,200 offers passes (output.txt, with the source of the test): the partner sends 3 or more requests, each under 64,000 tokens by the estimate, and no offer passes as unsure (output.txt).

## AT-64: Two presses share one pacer

App: pipeline
Commit: `98d79f98`
Then: No second holds more than 100,000 tokens across both presses.
Files: `evidence/AT-64/output.txt`
Observation: The pacer test with two presses at once passes: no second holds more than 100,000 tokens across both presses (output.txt).

## AT-65: The trade card is the Ledger

App: site
Commit: `98d79f98`
Then: Each card shows "You get · N" and "You give · N" columns, each player row shows the position, the NFL team, and the rank with no trade value, and a total shows under each column.
Files: `evidence/AT-65/find-answer-1280-dark.json`, `evidence/AT-65/find-answer-1280-light.json`, `evidence/AT-65/find-answer-375-dark.json`, `evidence/AT-65/find-answer-375-light.json`, `evidence/AT-65/find-answer-768-dark.json`, `evidence/AT-65/find-answer-768-light.json`, `evidence/AT-65/measure.jsonl`, `evidence/AT-38/375-light.png`, `evidence/AT-38/375-dark.png`, `evidence/AT-38/768-light.png`, `evidence/AT-38/768-dark.png`, `evidence/AT-38/1280-light.png`, `evidence/AT-38/1280-dark.png`
Observation: The cards come from the six results of AT-36. Each 5-card result (375 light, 375 dark, 1280 light, 1280 dark) holds three shapes: 1-for-2 (Shough and Bijan Robinson for Walker), 1-for-3 (such as Moore, Pollard, and Lawrence for Walker), and 2-for-3 (Williams, Kelce, and McCaffrey for Walker and Flowers). The 4-card results hold two shapes: 1-for-2 and 1-for-3 (768 light: one and three; 768 dark: two and two). Each card shows a "You get · N" and a "You give · N" column, each row shows the position, the NFL team, and the rank (such as "QB · NO · QB13") with no trade value, and a total such as "Trade value 62.5" shows under each column (measure.jsonl with the rows and totals of each card, find-answer files, AT-38 full-page shots). In these picks both totals of each card are the same (62.5, 85.5, 23.0, 17.0), so each card reads "Even in trade value"; the chart values of the Shortlist dumps give the same sums.

## AT-66: The card states the gap in plain words

App: site
Commit: `98d79f98`
Then: The card shows "You get 9% more trade value" under the totals.
Files: `evidence/AT-66/measure.jsonl`, `evidence/AT-66/output.txt`, `evidence/AT-66/served-answer.json`, `evidence/AT-66/served-answer.txt`, `evidence/AT-66/card-1280-dark.png`, `evidence/AT-66/card-1280-light.png`, `evidence/AT-66/card-375-dark.png`, `evidence/AT-66/card-375-light.png`, `evidence/AT-66/card-768-dark.png`, `evidence/AT-66/card-768-light.png`
Observation: The unit test passes, with the line "You get 9% more trade value" for 68.0 against 62.5 (output.txt). The instrument serves a real find answer of this round whose first card has the totals 68.0 for "You get" and 62.5 for "You give" (served-answer.txt says the one change). That card shows "Trade value 68.0" and "Trade value 62.5" and the line "You get 9% more trade value" under the totals at each size and theme (measure.jsonl, `card-*` shots).

## AT-67: Five picks, with the near ideas folded

App: site
Commit: `98d79f98`
Then: Up to 5 cards show, then "Close, but not sent · N", folded, with up to 3 near ideas under it.
Files: `evidence/AT-67/find-answer-1280-dark.json`, `evidence/AT-67/find-answer-1280-light.json`, `evidence/AT-67/find-answer-375-dark.json`, `evidence/AT-67/find-answer-375-light.json`, `evidence/AT-67/find-answer-768-dark.json`, `evidence/AT-67/find-answer-768-light.json`, `evidence/AT-67/measure.jsonl`, `evidence/AT-67/fold-closed-1280-dark.png`, `evidence/AT-67/fold-closed-1280-light.png`, `evidence/AT-67/fold-closed-375-dark.png`, `evidence/AT-67/fold-closed-375-light.png`, `evidence/AT-67/fold-closed-768-dark.png`, `evidence/AT-67/fold-closed-768-light.png`, `evidence/AT-67/fold-open-1280-dark.png`, `evidence/AT-67/fold-open-1280-light.png`, `evidence/AT-67/fold-open-375-dark.png`, `evidence/AT-67/fold-open-375-light.png`, `evidence/AT-67/fold-open-768-dark.png`, `evidence/AT-67/fold-open-768-light.png`
Observation: The six results of AT-36 show 5 or 4 cards, then the button "Close, but not sent · 3", closed (the `fold-closed` shots). After a tap the fold shows 3 near ideas, each with its shape, partner, players, and one reason (measure.jsonl `nearRowsAfterOpen`, the `fold-open` shots).

## AT-68: The wait states no time

App: site
Commit: `98d79f98`
Then: The hero shows no "This can take about 25 seconds." and no other count of seconds or minutes.
Files: `evidence/AT-68/measure.jsonl`, `evidence/AT-68/1280-dark.png`, `evidence/AT-68/1280-light.png`, `evidence/AT-68/375-dark.png`, `evidence/AT-68/375-light.png`, `evidence/AT-68/768-dark.png`, `evidence/AT-68/768-light.png`
Observation: With the find stream held, the hero during the wait reads "TRADE DEADLINE ~2d 14h 05m", the switch, "Finding Trades", "Who has a trade for you?", and "1 of 5 · Reading 11 teams" at each size and theme. The text of `main` has no "about 25 seconds" and no count of seconds or minutes (measure.jsonl `about25: false`, `countsOfTime: []`). The wait lines of AT-36 name no time either.

## AT-69: An anchor and a limit hold on every Value offer

App: api
Commit: `98d79f98`
Then: Each Value offer of the first press holds Trey McBride, and each Value offer of the second press brings Bo Girds an RB.
Files: `evidence/AT-69/press-aim-rb-api.log`, `evidence/AT-69/press-aim-rb-read.txt`, `evidence/AT-69/press-aim-rb-shortlist.json`, `evidence/AT-69/press-aim-rb-stream.txt`, `evidence/AT-69/press-anchor-api.log`, `evidence/AT-69/press-anchor-read.txt`, `evidence/AT-69/press-anchor-shortlist.json`, `evidence/AT-69/press-anchor-stream.txt`
Observation: The press around Trey McBride (anchor `8130`, side gives) builds 1,660 Value offers, and all 1,660 hold him. The press with an aim of RB builds 3,830 Value offers, and all 3,830 bring Bo Girds an RB (press-anchor-read.txt and press-aim-rb-read.txt, `## AT-69`; each Shortlist dump lists every Value offer). Both presses ran after the warm-up of AT-41 with the result cache emptied, with `claude_calls=1` each; the anchor press logs `finder pick kept 3 of 5`.

## AT-70: The picks spread across shapes and partners

App: api
Commit: `98d79f98`
Then: The picks hold at least 2 shapes and at least 3 partners.
Files: `evidence/AT-41/press-1-read.txt`, `evidence/AT-41/press-2-read.txt`, `evidence/AT-41/press-3-read.txt`, `evidence/AT-41/press-1-shortlist.json`, `evidence/AT-41/press-2-shortlist.json`, `evidence/AT-41/press-3-shortlist.json`, `evidence/AT-41/press-1-stream.txt`, `evidence/AT-41/press-2-stream.txt`, `evidence/AT-41/press-3-stream.txt`, `evidence/AT-41/press-1-api.log`, `evidence/AT-41/press-2-api.log`, `evidence/AT-41/press-3-api.log`, `evidence/AT-41/read_press.py.txt`, `evidence/AT-41/evidence_tap.py.txt`, `evidence/AT-41/warm-up.txt`
Observation: Press 1 picks 5 trades of 3 shapes (1-for-2, 2-for-3, 1-for-3) with 4 partners (Return of T Mac, Lil Fridge, Teehee, Unsolicited Dak Picks). Presses 2 and 3 also pick 5 trades of 3 shapes with 4 partners (press-N-read.txt, `## AT-70`, with the shape, partner, players, and Lean of each).

## AT-71: No request sends the long-context header

App: api
Commit: `98d79f98`
Then: No request sends the header `TypeSafe-Danger-Zone-Long-Context`.
Files: `evidence/AT-71/code-search.txt`, `evidence/AT-71/output.txt`, `evidence/AT-41/press-1-api.log`
Observation: The code search finds no `TypeSafe-Danger-Zone-Long-Context` in the Python of the apps and packages; the one Danger-Zone header in the code is `TypeSafe-Danger-Zone-Images` in `league/jev.py`, and the other hit is the test (code-search.txt). The test that sends each request of a press through the real TypeSafe adapter and keeps its headers passes, with no request that holds the long-context header (output.txt). The API log does not print request headers.

## AT-72: Each trade card shows as soon as it is ready

App: both
Commit: `2e9f0f85`
Then: The first trade card shows before the last one, each card shows one at a time as the stream sends it, and a line under the cards counts the trades still to come until the last card shows.
Files: `evidence/AT-72/first-card-1280-dark.png`, `evidence/AT-72/first-card-1280-light.png`, `evidence/AT-72/first-card-375-dark.png`, `evidence/AT-72/first-card-375-light.png`, `evidence/AT-72/first-card-768-dark.png`, `evidence/AT-72/first-card-768-light.png`, `evidence/AT-72/last-card-1280-dark.png`, `evidence/AT-72/last-card-1280-light.png`, `evidence/AT-72/last-card-375-dark.png`, `evidence/AT-72/last-card-375-light.png`, `evidence/AT-72/last-card-768-dark.png`, `evidence/AT-72/last-card-768-light.png`, `evidence/AT-72/measure.jsonl`
Observation: In each of the six presses of AT-36 the stream sends `data-trades-count` before the first `data-trade`, then the trade parts one at a time, then `data-trades-done` and the answer (measure.jsonl `tradeEventsWithSecondsFromTap`). In five presses the count is 5, five cards come, and the count line under the cards reads "Writing 4 more trades" at card 1, then 3, 2, "Writing 1 more trade" at card 4, and no line at card 5 (`cardsInDomWithSecondsFromTap`). In the 1280 dark press the count is 4 at 37.89 s, cards 1 and 2 show at 42.53 s and 43.51 s with "Writing 3 more trades" and "Writing 2 more trades", the stream sends count 3 at 44.86 s, the line reads "Writing 1 more trade" with 2 cards at 44.87 s, and card 3 shows with no line at 44.92 s; the answer holds 3 trades. Each card shows in the DOM 0.00 to 0.05 s after its part, and the first card shows 2.39 to 6.83 s before the last card. The `first-card` shots show the first card with the count line ("Writing 3 more trades" in the 1280 dark shot), and the `last-card` shots show all cards with no count line. In the full-page shots the sticky top band shows at the scroll place of the page.

## AT-73: Step 5 names the trades it weighs

App: site
Commit: `2e9f0f85`
Then: While the pick runs, step 5 changes its line about every 3 s, and each line names a real trade of the Shortlist of the press by its players. A press whose pick runs 15 s or more after step 5 starts shows at least 3 such lines. A faster pick shows fewer, and no card waits for a line.
Files: `evidence/AT-73/measure.jsonl`, `evidence/AT-73/step5-line-1-375-dark.png`, `evidence/AT-73/step5-line-1-375-light.png`, `evidence/AT-73/step5-line-2-375-dark.png`, `evidence/AT-73/step5-line-2-375-light.png`, `evidence/AT-73/step5-summary.txt`, `evidence/AT-73/step5_summary.py.txt`
Observation: In each press of AT-36 the stream sends `data-shortlist` with the 10 Shortlist trades before step 5 (measure.jsonl `shortlistEvent`). Step 5 starts with the stream event "Picking the best 5" at 5.24 to 5.82 s, and the pick ends with the first card at 31.94 to 43.27 s, so each pick runs 26.24 to 37.45 s after step 5 starts (`step5StreamEventSecondsFromTap`, `firstCardSecondsFromTap`, step5-summary.txt). The wait shows "5 of 5 · Picking the best 5" for 1.50 to 1.51 s, then lines such as "Weighing Corum for McConkey, Mahomes", each the players of one Shortlist trade in Shortlist order, starting again at trade 1 after trade 10. Before the first card there are 10, 10, 8, 9, 12, and 12 such lines (375 light, 375 dark, 768 light, 768 dark, 1280 light, 1280 dark). Each line before the last holds 3.00 to 3.01 s, and the first card ends the last line after 0.44 to 2.14 s. step5-summary.txt names the Shortlist trade of each line, and no line is outside the Shortlist. The `step5-line-1` and `step5-line-2` shots at 375 show two such lines in each theme.

