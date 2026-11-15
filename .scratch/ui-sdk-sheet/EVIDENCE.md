# ui-sdk sheet: evidence

Spec: `.scratch/ui-sdk-sheet/PRD.md`. Acceptance tests: `.scratch/ui-sdk-sheet/ACCEPTANCE.md`.
Built from: `fee8d319`, on 2026-11-15. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 4 min for 7 site tests.

The runner output is `evidence/runner-output.txt`. The measure scripts run on a static `CLIENT=cpc` build of `fee8d319` in a detached worktree, served with `python3 -m http.server`; AT-31 runs its script on a `CLIENT=norcal` build of the same commit too. Each script picks the first team on the team sheet of the front door before the first step.

## AT-1: The sheet follows the finger

App: site
Then: the bottom edge of the sheet sits 32 px higher than at rest, which is the 40 px drag less the 8 px tap slop of the `Drawer`, within 2 px.
Files: `evidence/AT-1/script.mjs`, `evidence/AT-1/log.txt`, `evidence/AT-1/hold-375.png`
Observation: On the phone the sheet rests at top 61, bottom 368 (height 307). A touch at y 348, a 40 px drag up over 200 ms, and a hold put the bottom edge at 336, 32 px higher than at rest. The 375 run gives the same numbers: 368 to 336, 32 px. `hold-375.png` shows the sheet raised under the band, with the band and the X still on top. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-2: The sheet settles on a spring

App: site
Then: the sheet returns to its open place within 600 ms. The bottom edge sampled on each animation frame moves on a curve that slows as it nears rest, and the sheet content has no CSS `transition` of a fixed duration on `transform` or `translate`.
Files: `evidence/AT-2/script.mjs`, `evidence/AT-2/log.txt`, `evidence/AT-2/rest-375.png`
Observation: A 30 px drag down held the bottom edge at 383.3 (rest 368). After the release, at 390, the offset of the bottom edge from rest on each frame is 15.3, 14.7, 13.4, 11.7, 9.9, 8.3, 6.8, 5.5, 4.4, 3.5, 2.8, 2.2, 1.7, 1.3, 1.0, 0.8, 0.6, 0.2, 0 px, about 17 ms apart; the step per frame grows to 1.8 px, then shrinks to 0.2 px. It is within 0.5 px of rest for good 265 ms after the first move at 390, and 266 ms at 375, and stays at 368 to the end of the 900 ms log. The computed transition of the sheet content is `all 0s` (property `all`, duration `0s`) at rest and on every sampled frame; the move is on the `translate` property. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-3: A flick closes the sheet

App: site
Then: the sheet closes, and the menu button has `aria-expanded="false"`.
Files: `evidence/AT-3/script.mjs`, `evidence/AT-3/log.txt`, `evidence/AT-3/after-375.png`
Observation: A flick from y 348 to 288, 60 px in 80 ms with 5 moves, then a release. 1000 ms later the menu button has `aria-expanded="false"` and the label "Open the menu", and the DOM holds 0 sheet content elements. The 375 run gives the same result. `after-375.png` shows the page with no sheet. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-4: A slow drag past half the height closes the sheet

App: site
Then: the sheet closes.
Files: `evidence/AT-4/script.mjs`, `evidence/AT-4/log.txt`, `evidence/AT-4/after-A-375.png`, `evidence/AT-4/after-B-375.png`
Observation: The sheet height is 307 px, half is 153.5 px. A drag up of 184 px (59.9% of the height) over 600 ms with 38 moves (mean 307 px/s) put the bottom edge 176 px above rest. Run A lets go at once; run B holds still 200 ms, then lets go. After each release, at 390 and at 375, the menu button has `aria-expanded="false"` and the DOM holds 0 sheet content elements. `after-A-375.png` and `after-B-375.png` show the page with no sheet. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-5: A short drag sends the sheet back

App: site
Then: the sheet stays open and returns to its open place.
Files: `evidence/AT-5/script.mjs`, `evidence/AT-5/log.txt`, `evidence/AT-5/rest-375.png`
Observation: A slow drag up of 20 px over 600 ms held the bottom edge at 356 (rest 368). 1000 ms after the release the bottom edge is 368 and the top is 61, both the same as at rest, and the menu button has `aria-expanded="true"`. The 375 run gives the same numbers. `rest-375.png` shows the open sheet at rest. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-6: A drag down meets resistance

App: site
Then: the bottom edge of the sheet moves down less than 60 px.
Files: `evidence/AT-6/script.mjs`, `evidence/AT-6/log.txt`, `evidence/AT-6/hold-375.png`
Observation: A drag down of 100 px over 300 ms, then a hold. The bottom edge moved from 368 to 389.1, down 21.1 px, at 390 and at 375. `hold-375.png` shows the sheet in the held place. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-7: A short drag on a row still opens the row

App: site
Then: the browser opens `/rankings/`.
Files: `evidence/AT-7/script.mjs`, `evidence/AT-7/log.txt`, `evidence/AT-7/after-375.png`
Observation: The row Power Rankings spans y 233 to 289. A touch at its center (y 261), a 5 px move up over 120 ms, and a release. 1500 ms later the URL is `http://127.0.0.1:59911/rankings/`, path `/rankings/`, at 390 and at 375. `after-375.png` shows the Power Rankings page. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-8: A real drag on a row does not open the row

App: site
Then: the URL stays `/`.
Files: `evidence/AT-8/script.mjs`, `evidence/AT-8/log.txt`, `evidence/AT-8/after-375.png`
Observation: A touch at the center of the row Power Rankings (y 261), a 30 px move up over 120 ms, and a release. 1500 ms later the URL is `http://127.0.0.1:59911/`, path `/`, at 390 and at 375. `after-375.png` shows the front door with the sheet. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-9: A grab handle shows on the sheet

App: site
Then: a small bar sits at the center of the bottom edge.
Files: `evidence/AT-9/steps.json`, `evidence/AT-9/script.mjs`, `evidence/AT-9/log.txt`, `evidence/AT-9/1280-dark.png`, `evidence/AT-9/1280-light.png`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/375-light.png`, `evidence/AT-9/768-dark.png`, `evidence/AT-9/768-light.png`
Observation: The shots at 375 and 768 show the open sheet with a short grey bar at the center of its bottom edge, in light and dark. At 1280 the band shows the pill bar and no sheet. The log puts the grip at 40 x 6 px, its center x equal to the sheet center x (187.5 at 375, 384 at 768), its bottom 9 px above the sheet bottom, and it is the last child of the sheet.

## AT-10: The sheet opens to one height with every row in view

App: site
Then: the rows Home, Week 9, Power Rankings, and Managers all show in the viewport, with no scroll in the sheet and no second pull.
Files: `evidence/AT-10/steps.json`, `evidence/AT-10/script.mjs`, `evidence/AT-10/log.txt`, `evidence/AT-10/1280-dark.png`, `evidence/AT-10/1280-light.png`, `evidence/AT-10/375-dark.png`, `evidence/AT-10/375-light.png`, `evidence/AT-10/768-dark.png`, `evidence/AT-10/768-light.png`
Observation: The shots at 375 and 768 show the open sheet with the four rows Home, Week 9, Power Rankings, and Managers, then the grip; at 1280 the pill bar shows in place of the sheet. The log at 390, 375, and 768 (viewport height 844): Home 69 to 125, Week 9 129 to 185, Power Rankings 233 to 289, Managers 293 to 349, all inside the viewport. The sheet scrollHeight and clientHeight are both 306, no element in the sheet scrolls, and `data-snap-point` is `content`.

## AT-11: Past weeks pushes the rows under it down

App: site
Then: the week chips show under the row Week 9, and the row Power Rankings moves down by the height of the chips, so no chip covers a row.
Files: `evidence/AT-11/steps.json`, `evidence/AT-11/script.mjs`, `evidence/AT-11/log.txt`, `evidence/AT-11/after-1280-dark.png`, `evidence/AT-11/after-1280-light.png`, `evidence/AT-11/after-375-dark.png`, `evidence/AT-11/after-375-light.png`, `evidence/AT-11/after-768-dark.png`, `evidence/AT-11/after-768-light.png`, `evidence/AT-11/before-1280-dark.png`, `evidence/AT-11/before-1280-light.png`, `evidence/AT-11/before-375-dark.png`, `evidence/AT-11/before-375-light.png`, `evidence/AT-11/before-768-dark.png`, `evidence/AT-11/before-768-light.png`
Observation: The `before` shots show the open sheet with "Past weeks" closed; the `after` shots at 375 and 768 show the chips WK 09 to WK 06 under the row Week 9 and above the row Power Rankings, with no overlap; at 1280 both shots show the pill bar and no sheet. The log at 390 and 375: the top of Power Rankings goes from 233 to 337, down 104 px; the chips list spans 229 to 333, height 104 px, and its bottom 333 is above the Power Rankings top 337. The sheet bottom goes from 368 to 472.

## AT-12: The dim follows the drag

App: site
Then: the computed opacity of the dim during the hold is lower than at rest.
Files: `evidence/AT-12/script.mjs`, `evidence/AT-12/log.txt`, `evidence/AT-12/hold-375.png`
Observation: The dim opacity is 1 at rest. A drag up of 153.5 px (half of 307) over 300 ms and a hold moved the bottom edge up 145.5 px, and the dim opacity during the hold is 0.5261, at 390 and at 375. `hold-375.png` shows the raised sheet and a lighter dim over the page. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-13: A tap on the dim closes the sheet

App: site
Then: the sheet closes, and the URL stays `/`.
Files: `evidence/AT-13/script.mjs`, `evidence/AT-13/log.txt`, `evidence/AT-13/after-375.png`
Observation: The tap point is (195, 700) at 390 and (188, 700) at 375, below the sheet bottom 368; `elementFromPoint` there gives `DIV[data-slot=drawer-backdrop]`. Before the tap `aria-expanded` is true; 1000 ms after it `aria-expanded` is false, the DOM holds 0 sheet content elements, and the URL stays `http://127.0.0.1:59911/`. `after-375.png` shows the page with no sheet. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-14: The X takes the place of the menu button

App: site
Then: the X shows in the same box as the menu icon, within 1 px.
Files: `evidence/AT-14/script.mjs`, `evidence/AT-14/log.txt`, `evidence/AT-14/band-after-375.png`, `evidence/AT-14/band-before-375.png`
Observation: At 390 the menu icon before the tap is at (354, 20), 20 x 20, opacity 1; after the tap the X is at (354, 20), 20 x 20, opacity 1, and the menu icon is at opacity 0. The difference is 0 px on each edge. At 375 both are at (339, 20), 20 x 20. The button box stays (342, 8, 44 x 44) at 390. `band-before-375.png` shows the menu icon, and `band-after-375.png` shows the X in the same spot. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-15: The band stays above the sheet and the dim

App: site
Then: the sheet closes. Before the tap, the top edge of the sheet sat at the bottom edge of the band, within 1 px, and `document.elementFromPoint` at the center of the band gave an element inside the band.
Files: `evidence/AT-15/script.mjs`, `evidence/AT-15/log.txt`, `evidence/AT-15/after-375.png`
Observation: Before the tap the band spans y 0 to 61 and the sheet top is at 61, a difference of 0 px, at 390 and at 375. `elementFromPoint` at the band center (195, 30.5) gives a DIV with `insideHeader: true`. A tap on the X (label "Close the menu") gives `aria-expanded=false` and 0 sheet content elements 1000 ms later. `after-375.png` shows the page with no sheet. The phone is 390 x 844 with `hasTouch` and `isMobile`; each script runs the gesture again at 375 x 844 for the shot.

## AT-16: Each row shows its icon, its name, and its note

App: site
Then: each row shows an icon, its name, and its note, such as "Power Rankings" over "The league, ranked".
Files: `evidence/AT-16/steps.json`, `evidence/AT-16/script.mjs`, `evidence/AT-16/log.txt`, `evidence/AT-16/1280-dark.png`, `evidence/AT-16/1280-light.png`, `evidence/AT-16/375-dark.png`, `evidence/AT-16/375-light.png`, `evidence/AT-16/768-dark.png`, `evidence/AT-16/768-light.png`
Observation: Each shot at 375 and 768, light and dark, shows four rows, each with an icon tile, a bold name, and a grey note under it; at 1280 the pill bar shows in place of the sheet. The log reads: house "Home" over "Ask about your team", calendar-days "Week 9" over "Scores and recaps", trophy "Power Rankings" over "The league, ranked", users "Managers" over "Grades and records".

## AT-17: The check marks the open page

App: site
Then: the row Home holds the check, and no other row holds it.
Files: `evidence/AT-17/steps.json`, `evidence/AT-17/script.mjs`, `evidence/AT-17/log.txt`, `evidence/AT-17/1280-dark.png`, `evidence/AT-17/1280-light.png`, `evidence/AT-17/375-dark.png`, `evidence/AT-17/375-light.png`, `evidence/AT-17/768-dark.png`, `evidence/AT-17/768-light.png`
Observation: The shots at 375 and 768 show a check at the right end of the row Home only, in light and dark; at 1280 the pill bar shows with Home marked. The log at 390, 375, and 768 on path `/`: Home 1 check with `aria-current=page`, Week 9 0, Power Rankings 0, Managers 0; the sheet holds 1 check in all.

## AT-18: The week row opens the latest report

App: site
Then: the browser opens `/2026/week-09/`.
Files: `evidence/AT-18/script.mjs`, `evidence/AT-18/log.txt`
Observation: A tap at the center of the row Week 9 (y 129 to 185). After the tap the URL is `http://127.0.0.1:59911/2026/week-09/`.

## AT-19: Past weeks lists every week, newest first

App: site
Then: the chips read WK 09, WK 08, WK 07, WK 06, in that order, one chip for each published week of `cpc`.
Files: `evidence/AT-19/script.mjs`, `evidence/AT-19/log.txt`
Observation: After a tap on "Past weeks" the chip labels in order are WK 09, WK 08, WK 07, WK 06, with hrefs `/2026/week-09/` to `/2026/week-06/`, all four visible. `clients/cpc/published/2026/` holds 4 week folders: week-06, week-07, week-08, week-09.

## AT-20: The sheet fades under reduced motion

App: site
Then: the bounding box of the sheet does not move on any frame, and its opacity goes from 0 to 1 in about 150 ms.
Files: `evidence/AT-20/script.mjs`, `evidence/AT-20/log.txt`
Observation: With `reducedMotion: "reduce"` the media query matches. On every frame with the sheet, from t=92 ms to t=710 ms, the box is x 0, y 61, 390 x 307, with `translate: 0px`: 1 distinct box. The opacity is 0 at t=92 and t=112, then 0.11, 0.22, 0.33 ... 0.89, and 1 at t=259 ms: 167 ms from the first frame with the sheet, and about 150 ms from the first frame above 0.

## AT-21: The focus moves into the sheet on open

App: site
Then: `document.activeElement` is inside the sheet.
Files: `evidence/AT-21/script.mjs`, `evidence/AT-21/log.txt`
Observation: Before the key the focus is on the menu button in the band. After Enter, `aria-expanded` is true and `document.activeElement` is the link Home (`href="/"`) inside the sheet.

## AT-22: Escape closes the sheet and returns the focus

App: site
Then: the sheet closes, and the focus is on the menu button.
Files: `evidence/AT-22/script.mjs`, `evidence/AT-22/log.txt`
Observation: After Enter the focus is on the link Home inside the sheet. After Escape `aria-expanded` is false, the DOM holds 0 sheet content elements, and `document.activeElement` is the menu button ("Open the menu"); the identity check gives true.

## AT-23: The focus stays in the sheet and the band

App: site
Then: after each press, the active element is inside the sheet or inside the band, never in the page under the dim.
Files: `evidence/AT-23/script.mjs`, `evidence/AT-23/log.txt`
Observation: After the open by Enter the focus is on Home in the sheet. Tab 1 to 10 give: Week 9, Past weeks, Power Rankings, Managers, Home, Week 9, Past weeks, Power Rankings, Managers, Home. Each one is inside the sheet; none is in the band or the page.

## AT-24: The closed sheet is out of the accessibility tree

App: site
Then: the snapshot holds no row of the sheet.
Files: `evidence/AT-24/script.mjs`, `evidence/AT-24/log.txt`
Observation: With `aria-expanded=false` the snapshot of the body holds the banner (link, theme button, "Open the menu") and the main thread. It holds no row link of the sheet, no "Scores and recaps", "The league, ranked", "Grades and records", "Past weeks", no navigation "Pages", and no dialog "Pages". The DOM holds 0 sheet content elements. The snapshot holds "Ask about your team" only in the placeholder of the textbox.

## AT-25: The open sheet is named "Pages"

App: site
Then: the open sheet has the accessible name "Pages".
Files: `evidence/AT-25/script.mjs`, `evidence/AT-25/log.txt`
Observation: The open sheet has `role=dialog`, and its `aria-labelledby` points to the text "Pages". `getByRole("dialog", { name: "Pages" })` finds 1. The snapshot starts `- dialog "Pages":`, and the CDP accessibility tree holds one dialog with the name "Pages".

## AT-26: The menu button says what it does

App: site
Then: the button reads "Open the menu" before the tap and "Close the menu" after it.
Files: `evidence/AT-26/script.mjs`, `evidence/AT-26/log.txt`
Observation: Before the tap the button snapshot is `button "Open the menu"`; after the tap it is `button "Close the menu" [expanded]`. `getByRole` finds 1 button for each name at its time.

## AT-27: The desktop shows the pill bar in place of the menu sheet

App: site
Then: the pill bar shows, and the menu button does not.
Files: `evidence/AT-27/steps.json`, `evidence/AT-27/script.mjs`, `evidence/AT-27/log.txt`, `evidence/AT-27/1280-dark.png`, `evidence/AT-27/1280-light.png`
Observation: Both shots at 1280 show the band with the logo, the league name, the pills Home, Week 9, Power Rankings, Managers, and the theme button, and no menu button. The log at 1280 x 800: the pill bar is visible, `display: flex`, 697 x 44 px; the menu button is in the DOM, not visible, `display: none`.

## AT-28: With no scripts, the band shows no menu button

App: site
Then: the band shows no menu button.
Files: `evidence/AT-28/script.mjs`, `evidence/AT-28/log.txt`, `evidence/AT-28/band-375.png`
Observation: With `javaScriptEnabled: false` at 390 and 375 the menu button is in the DOM, not visible, with no box. `band-375.png` shows the band with the logo only.

## AT-29: A dock page loads no more code

App: site
Then: the sum on the Spec branch is less than or equal to the sum on `main`.
Files: `evidence/AT-29/at29.sh`, `evidence/AT-29/output.txt`
Observation: On `main` (`origin/main` 8dc8ff5c) `/rankings/` loads 8 chunks with a gzip -9 sum of 317814 bytes. On the Spec branch (fee8d319) it loads 8 chunks with a sum of 316270 bytes, 1544 bytes less. For `/`, the sums are 413757 bytes on `main` (9 chunks) and 456780 bytes on the Spec branch (10 chunks). Both builds are `CLIENT=cpc` static builds in detached worktrees.

## AT-30: The first tap opens the sheet with no wait

App: site
Then: the tap starts no new request of a script, and the sheet opens.
Files: `evidence/AT-30/script.mjs`, `evidence/AT-30/log.txt`
Observation: After network idle and a 1000 ms wait, a tap on the menu button. The sheet is visible 42 ms after the tap, with `aria-expanded=true`. From the tap to 945 ms after it the page makes 0 requests, 0 of them scripts.

## AT-31: The sheet keeps the look of each league

App: site
Then: the sheet background is the page color of that client, and the check is the accent color of that client.
Files: `evidence/AT-31/steps.json`, `evidence/AT-31/script.mjs`, `evidence/AT-31/log.txt`, `evidence/AT-31/cpc-1280-dark.png`, `evidence/AT-31/cpc-1280-light.png`, `evidence/AT-31/cpc-375-dark.png`, `evidence/AT-31/cpc-375-light.png`, `evidence/AT-31/cpc-768-dark.png`, `evidence/AT-31/cpc-768-light.png`, `evidence/AT-31/norcal-1280-dark.png`, `evidence/AT-31/norcal-1280-light.png`, `evidence/AT-31/norcal-375-dark.png`, `evidence/AT-31/norcal-375-light.png`, `evidence/AT-31/norcal-768-dark.png`, `evidence/AT-31/norcal-768-light.png`
Observation: The shots of each client at 375 and 768 show the open sheet with the page color of that client and the check in its accent; at 1280 the pill bar shows. Computed: cpc light sheet `rgb(244, 244, 244)` = `--color-page` #f4f4f4, check `rgb(165, 46, 37)` = `--color-accent-ink` #a52e25 (`--color-accent` #b8342a); cpc dark sheet `rgb(20, 20, 20)` = #141414, check `rgb(242, 165, 158)` = accent-ink #f2a59e. norcal light sheet `rgb(245, 243, 239)` = #f5f3ef, check `rgb(154, 52, 18)` = accent-ink #9a3412 (`--color-accent` #c2410c); norcal dark sheet `rgb(20, 20, 20)` = #141414, check `rgb(224, 165, 38)` = accent-ink #e0a526.

## AT-32: Only the ui folder imports ui-sdk

App: site
Then: every listed file is in `packages/design/site/ui/`.
Files: `evidence/AT-32/output.txt`
Observation: The command lists one file: `packages/design/site/ui/sheet.tsx`.

## AT-33: The rule test fails an import of ui-sdk outside the ui folder

App: site
Then: the test fails and names that file and that line.
Files: `evidence/AT-33/output.txt`
Observation: With `import "@ui-sdk/react/drawer";` added as line 6 of `packages/design/site/shell/week-chip.tsx`, the rule test exits 1: 1 failed, 4 passed. The message names `../../packages/design/site/shell/week-chip.tsx:6` and "week-chip.tsx imports @ui-sdk/react/drawer". After `git restore` the diff is empty and the test exits 0: 5 passed.

## AT-34: ui-sdk is pinned in one place

App: site
Then: the design package lists `@ui-sdk/react` and `@ui-sdk/core` at one exact version with no caret or tilde, and the site app lists neither.
Files: `evidence/AT-34/output.txt`
Observation: `packages/design/site/package.json` lists `"@ui-sdk/core": "0.1.0-beta.2"` and `"@ui-sdk/react": "0.1.0-beta.2"` in `dependencies`, with no caret or tilde. `apps/site/package.json` lists neither; `rg -n "@ui-sdk"` on both files finds only the two lines of the design package.

## AT-35: The hand-built drag code of the menu sheet is gone

App: site
Then: the command finds nothing.
Files: `evidence/AT-35/output.txt`
Observation: The command prints nothing and exits 1, the exit code of `rg` with no match.

## AT-36: The README of the ui folder names the sheet and the rule

App: site
Then: it names the sheet wrapper, and it says that only this folder imports `@ui-sdk`.
Files: `evidence/AT-36/output.txt`
Observation: The README names the sheet wrapper: "The sheet wraps the ui-sdk `Drawer` ... `sheet.tsx` is the one file that imports `@ui-sdk`." Under Does not do it says: "No file outside this folder imports `@ui-sdk`. The rule test `apps/site/src/ui-sdk-rule.test.ts` fails on one."

## AT-37: No ui-sdk default look loads

App: site
Then: no source file imports `web.css`, and the page loads no ui-sdk style sheet file.
Files: `evidence/AT-37/script.mjs`, `evidence/AT-37/log.txt`, `evidence/AT-37/output.txt`
Observation: `rg -n "web.css"` over `apps` and `packages`, outside `node_modules`, prints nothing and exits 1. With the sheet open the page has one `<link rel="stylesheet">`, `/_next/static/chunks/2o_re657i7nen.css`, the site style sheet; no href holds "ui-sdk" or "web.css". That file holds "ui-sdk" once, in the layer order statement `@layer ui-sdk;` that `apps/site/src/app/globals.css` line 6 writes.

## AT-38: The other sheets, the dock, and the pill bar do not change

App: site
Then: the diff shows no change to any of them.
Files: `evidence/AT-38/output.txt`
Observation: The files are `packages/analyzer/site/form/player-sheet.tsx`, `packages/waiver/site/player-sheet.tsx`, `packages/eggs/site/hunt/claim-sheet.tsx`, `apps/site/src/app/front-door/team-sheet.tsx`, `packages/analyzer/site/form/team-sheet.tsx`, `apps/site/src/app/front-door/passphrase-sheet.tsx`, `packages/design/site/shell/dock.tsx`, and `packages/design/site/shell/pill-bar.tsx`; `git ls-files` lists all eight. `git diff origin/main --stat` on them prints nothing and exits 0. A control run on `menu-sheet.tsx` prints 1 changed file. The command uses `origin/main` (8dc8ff5c), because the local `main` is behind it.

## AT-39: No check of the bundle size enters CI

App: site
Then: the diff is empty.
Files: `evidence/AT-39/output.txt`
Observation: `git diff origin/main --stat -- .github/workflows/` prints nothing and exits 0. The command uses `origin/main` (8dc8ff5c), because the local `main` is behind it.
