# ui-sdk sheet: acceptance tests

Spec: `.scratch/ui-sdk-sheet/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

Common setup. Unless a test says otherwise: client `cpc`, the published season 2026 with week 9 as the latest week, the static build `out/` of the Spec branch served over HTTP, the front door at `/`. "The phone" is a Playwright context of 390 x 844 px with `hasTouch` and `isMobile`, with touch gestures sent through CDP `Input.dispatchTouchEvent`. "The open sheet" is the menu sheet after a tap on the menu button, at rest. The cpc menu sheet holds the rows Home, Week 9, Power Rankings, and Managers. The evidence of each drag test holds the Playwright script and its log of measured values, and a screenshot of the phone at 375 px. Each test records the real values that it measured.

## Tests

AT-1: The sheet follows the finger
App: site
Stories: 1
Given: the open sheet on the phone.
When: the reader touches the sheet, drags up 40 px, and holds the touch.
Then: the bottom edge of the sheet sits 40 px higher than at rest, within 2 px.
Evidence: the Playwright log of the bounding box of the sheet at rest and during the hold, and a screenshot during the hold at 375 px.

AT-2: The sheet settles on a spring
App: site
Stories: 2
Given: the open sheet on the phone.
When: the reader drags the sheet down 30 px and lets go.
Then: the sheet returns to its open place within 600 ms. The bottom edge sampled on each animation frame moves on a curve that slows as it nears rest, and the sheet content has no CSS `transition` of a fixed duration on `transform` or `translate`.
Evidence: the Playwright log of the bottom edge on each frame from the release to rest, and the computed `transition` of the sheet content.

AT-3: A flick closes the sheet
App: site
Stories: 3
Given: the open sheet on the phone.
When: the reader flicks the sheet up 60 px in 80 ms and lets go.
Then: the sheet closes, and the menu button has `aria-expanded="false"`.
Evidence: the Playwright log of the gesture and of the state of the menu button after it.

AT-4: A slow drag past half the height closes the sheet
App: site
Stories: 4
Given: the open sheet on the phone.
When: the reader drags the sheet up slowly, over 600 ms, past half its height, and lets go.
Then: the sheet closes.
Evidence: the Playwright log of the sheet height, the gesture, and the state of the menu button after it.

AT-5: A short drag sends the sheet back
App: site
Stories: 5
Given: the open sheet on the phone.
When: the reader drags the sheet up slowly 20 px and lets go.
Then: the sheet stays open and returns to its open place.
Evidence: the Playwright log of the bottom edge after rest and the state of the menu button.

AT-6: A drag down meets resistance
App: site
Stories: 6
Given: the open sheet on the phone.
When: the reader drags the sheet down 100 px and holds the touch.
Then: the bottom edge of the sheet moves down less than 60 px.
Evidence: the Playwright log of the bottom edge at rest and during the hold.

AT-7: A short drag on a row still opens the row
App: site
Stories: 7
Given: the open sheet on the phone.
When: the reader touches the row "Power Rankings", moves the touch 5 px up, and lets go.
Then: the browser opens `/rankings/`.
Evidence: the Playwright log of the gesture and the URL after it.

AT-8: A real drag on a row does not open the row
App: site
Stories: 8
Given: the open sheet on the phone.
When: the reader touches the row "Power Rankings", moves the touch 30 px up, and lets go.
Then: the URL stays `/`.
Evidence: the Playwright log of the gesture and the URL after it.

AT-9: A grab handle shows on the sheet
App: site
Stories: 9
Given: the open sheet.
When: the reader looks at the bottom edge of the sheet.
Then: a small bar sits at the center of the bottom edge.
Evidence: screenshots of the open sheet at 375, 768, and 1280 px, each in the light theme and the dark theme. At 1280 px the pill bar shows in place of the sheet.

AT-10: The sheet opens to one height with every row in view
App: site
Stories: 10
Given: the closed sheet on the phone.
When: the reader taps the menu button.
Then: the rows Home, Week 9, Power Rankings, and Managers all show in the viewport, with no scroll in the sheet and no second pull.
Evidence: screenshots of the open sheet at 375, 768, and 1280 px, each in the light theme and the dark theme, and the Playwright log of the bounding box of each row against the viewport.

AT-11: Past weeks pushes the rows under it down
App: site
Stories: 11
Given: the open sheet on the phone.
When: the reader taps "Past weeks".
Then: the week chips show under the row Week 9, and the row Power Rankings moves down by the height of the chips, so no chip covers a row.
Evidence: screenshots before and after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme, and the Playwright log of the top of the row Power Rankings before and after.

AT-12: The dim follows the drag
App: site
Stories: 12
Given: the open sheet on the phone.
When: the reader drags the sheet up by half its height and holds the touch.
Then: the computed opacity of the dim during the hold is lower than at rest.
Evidence: the Playwright log of the opacity of the dim at rest and during the hold, and a screenshot during the hold at 375 px.

AT-13: A tap on the dim closes the sheet
App: site
Stories: 13
Given: the open sheet on the phone.
When: the reader taps the dimmed page under the sheet.
Then: the sheet closes, and the URL stays `/`.
Evidence: the Playwright log of the tap point, the state of the menu button, and the URL.

AT-14: The X takes the place of the menu button
App: site
Stories: 14
Given: the closed sheet on the phone.
When: the reader taps the menu button.
Then: the X shows in the same box as the menu icon, within 1 px.
Evidence: the Playwright log of the bounding box of the icon before and after, and screenshots of the band before and after at 375 px.

AT-15: The band stays above the sheet and the dim
App: site
Stories: 15
Given: the open sheet on the phone.
When: the reader taps the X in the band.
Then: the sheet closes. Before the tap, the top edge of the sheet sat at the bottom edge of the band, within 1 px, and `document.elementFromPoint` at the center of the band gave an element inside the band.
Evidence: the Playwright log of the band and sheet bounding boxes, the `elementFromPoint` result, and the state of the menu button after the tap.

AT-16: Each row shows its icon, its name, and its note
App: site
Stories: 16
Given: the closed sheet.
When: the reader opens the sheet.
Then: each row shows an icon, its name, and its note, such as "Power Rankings" over "The league, ranked".
Evidence: screenshots of the open sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-17: The check marks the open page
App: site
Stories: 17
Given: the closed sheet on `/`.
When: the reader opens the sheet.
Then: the row Home holds the check, and no other row holds it.
Evidence: screenshots of the open sheet at 375, 768, and 1280 px, each in the light theme and the dark theme, and the Playwright count of checks in each row.

AT-18: The week row opens the latest report
App: site
Stories: 18
Given: the open sheet on the phone.
When: the reader taps the row Week 9.
Then: the browser opens `/2026/week-09/`.
Evidence: the Playwright log of the URL after the tap.

AT-19: Past weeks lists every week, newest first
App: site
Stories: 18
Given: the open sheet on the phone.
When: the reader taps "Past weeks".
Then: the chips read from WK 09 first down to WK 01 last, one chip for each published week.
Evidence: the Playwright list of the chip labels in order.

AT-20: The sheet fades under reduced motion
App: site
Stories: 19
Given: the closed sheet on the phone, with `reducedMotion: "reduce"`.
When: the reader taps the menu button.
Then: the bounding box of the sheet does not move on any frame, and its opacity goes from 0 to 1 in about 150 ms.
Evidence: the Playwright log of the bounding box and the opacity of the sheet on each frame from the tap to rest.

AT-21: The focus moves into the sheet on open
App: site
Stories: 20
Given: the closed sheet on the phone, with the focus on the menu button.
When: the reader presses Enter.
Then: `document.activeElement` is inside the sheet.
Evidence: the Playwright log of the active element after the key.

AT-22: Escape closes the sheet and returns the focus
App: site
Stories: 21
Given: the open sheet on the phone, opened by the keyboard.
When: the reader presses Escape.
Then: the sheet closes, and the focus is on the menu button.
Evidence: the Playwright log of the state of the menu button and of the active element.

AT-23: The focus stays in the sheet and the band
App: site
Stories: 22
Given: the open sheet on the phone, opened by the keyboard.
When: the reader presses Tab ten times.
Then: after each press, the active element is inside the sheet or inside the band, never in the page under the dim.
Evidence: the Playwright log of the active element after each press.

AT-24: The closed sheet is out of the accessibility tree
App: site
Stories: 23
Given: the closed sheet on the phone.
When: the reader takes an accessibility snapshot of the page.
Then: the snapshot holds no row of the sheet.
Evidence: the Playwright accessibility snapshot.

AT-25: The open sheet is named "Pages"
App: site
Stories: 24
Given: the closed sheet on the phone.
When: the reader opens the sheet.
Then: the open sheet has the accessible name "Pages".
Evidence: the Playwright accessibility snapshot of the open sheet.

AT-26: The menu button says what it does
App: site
Stories: 25
Given: the closed sheet on the phone.
When: the reader opens the sheet.
Then: the button reads "Open the menu" before the tap and "Close the menu" after it.
Evidence: the Playwright log of the accessible name of the button before and after.

AT-27: The desktop shows the pill bar in place of the menu sheet
App: site
Stories: 26
Given: the front door in a desktop context of 1280 x 800 px.
When: the reader looks at the band.
Then: the pill bar shows, and the menu button does not.
Evidence: screenshots of the band at 1280 px in the light theme and the dark theme, and the Playwright visibility of both controls.

AT-28: With no scripts, the band shows no menu button
App: site
Stories: 27
Given: the front door on the phone with `javaScriptEnabled: false`.
When: the reader looks at the band.
Then: the band shows no menu button.
Evidence: a screenshot of the band at 375 px and the Playwright visibility of the button.

AT-29: A dock page loads no more code
App: site
Stories: 28
Given: the static builds of `main` and of the Spec branch for `cpc`.
When: the agent sums the gzip size, at level 9, of each `/_next/static/**/*.js` file that `/rankings/index.html` loads.
Then: the sum on the Spec branch is less than or equal to the sum on `main`.
Evidence: the script, both sums, and the list of chunks of each build. Also the same sums for `/`, for the record.

AT-30: The first tap opens the sheet with no wait
App: site
Stories: 29
Given: the front door on the phone, after the network is idle.
When: the reader taps the menu button.
Then: the tap starts no new request of a script, and the sheet opens.
Evidence: the Playwright log of the network requests from the tap to the open sheet.

AT-31: The sheet keeps the look of each league
App: site
Stories: 30
Given: the open sheet in client `cpc` and in client `norcal`.
When: the reader looks at the sheet in each client.
Then: the sheet background is the page color of that client, and the check is the accent color of that client.
Evidence: screenshots of the open sheet in both clients at 375, 768, and 1280 px, each in the light theme and the dark theme, and the computed colors next to the theme tokens of each client.

AT-32: Only the ui folder imports ui-sdk
App: site
Stories: 31
Given: the Spec branch.
When: the agent runs `rg -l "@ui-sdk" --glob '*.{ts,tsx}' --glob '!**/node_modules/**' apps packages`.
Then: every listed file is in `packages/design/site/ui/`.
Evidence: the command and its output.

AT-33: The rule test fails an import of ui-sdk outside the ui folder
App: site
Stories: 32
Given: the Spec branch, with a throwaway line `import "@ui-sdk/react/drawer";` added to a file in `packages/design/site/shell/`.
When: the agent runs the rule test of ui-sdk.
Then: the test fails and names that file and that line.
Evidence: the command and its output with the line, and the output of the same test after the agent removes the line, which passes.

AT-34: ui-sdk is pinned in one place
App: site
Stories: 34
Given: the Spec branch.
When: the agent reads the `package.json` of the design package and of the site app.
Then: the design package lists `@ui-sdk/react` and `@ui-sdk/core` at one exact version with no caret or tilde, and the site app lists neither.
Evidence: the two dependency blocks.

AT-35: The hand-built drag code of the menu sheet is gone
App: site
Stories: 35
Given: the Spec branch.
When: the agent runs `rg -n "rubberband|SLOP|CLOSE_SPEED|CLOSE_DISTANCE|onPointerMove|setPointerCapture" packages/design/site/shell/menu-sheet.tsx`.
Then: the command finds nothing.
Evidence: the command and its empty output.

AT-36: The README of the ui folder names the sheet and the rule
App: site
Stories: 36
Given: the Spec branch.
When: the agent reads `packages/design/site/ui/README.md`.
Then: it names the sheet wrapper, and it says that only this folder imports `@ui-sdk`.
Evidence: the lines of the README.

AT-37: No ui-sdk default look loads
App: site
Stories: none
Given: the Spec branch and the open sheet on the phone.
When: the agent searches the source for `web.css` and lists the style sheets of the page.
Then: no source file imports `web.css`, and the page loads no ui-sdk style sheet file.
Evidence: the `rg` command and its output, and the Playwright list of the `<link rel="stylesheet">` hrefs.

AT-38: The other sheets, the dock, and the pill bar do not change
App: site
Stories: none
Given: the Spec branch.
When: the agent runs `git diff main --stat` on the files of the player sheet, the claim sheet, the team sheet, the passphrase sheet, the dock, and the pill bar.
Then: the diff shows no change to any of them.
Evidence: the command, the list of files, and its empty output.

AT-39: No check of the bundle size enters CI
App: site
Stories: none
Given: the Spec branch.
When: the agent runs `git diff main --stat -- .github/workflows/`.
Then: the diff is empty.
Evidence: the command and its empty output.

## Trace

Story 1: AT-1
Story 2: AT-2
Story 3: AT-3
Story 4: AT-4
Story 5: AT-5
Story 6: AT-6
Story 7: AT-7
Story 8: AT-8
Story 9: AT-9
Story 10: AT-10
Story 11: AT-11
Story 12: AT-12
Story 13: AT-13
Story 14: AT-14
Story 15: AT-15
Story 16: AT-16
Story 17: AT-17
Story 18: AT-18, AT-19
Story 19: AT-20
Story 20: AT-21
Story 21: AT-22
Story 22: AT-23
Story 23: AT-24
Story 24: AT-25
Story 25: AT-26
Story 26: AT-27
Story 27: AT-28
Story 28: AT-29
Story 29: AT-30
Story 30: AT-31
Story 31: AT-32
Story 32: AT-33
Story 33: no test. Reason: the style method is a matter of review. AT-37 shows that no default look loads, and AT-31 shows the look.
Story 34: AT-34
Story 35: AT-35
Story 36: AT-36
Out of scope "the other four sheets": AT-38
Out of scope "side-tabs, show-all, index-list": no test. Reason: no ticket of this spec touches them, and AT-32 fails any import of ui-sdk in them.
Out of scope "the ui-sdk default look": AT-37
Out of scope "the pill bar": AT-38
Out of scope "the dock": AT-38
Out of scope "a check of the bundle size in CI": AT-39
Out of scope "a mouse drag on a row on the desktop": no test. Reason: nothing to build.
Out of scope "a sheet from the bottom edge": AT-15

## Revisions

None yet.
