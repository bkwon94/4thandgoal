# Front door tour: evidence

Spec: `.scratch/front-door-tour/PRD.md`. Acceptance tests: `.scratch/front-door-tour/ACCEPTANCE.md`.
Built from: `884ee50d`, on 2026-11-19. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 9 min for 12 site tests.
The runner round took 542.2 s for 11 cpc tests and 17.9 s for AT-6 on norcal. The runner and agent-browser shots come from `74717c9c`. `884ee50d` changes only `apps/site/e2e/front-door-tour-look.spec.ts`, and every output comes from `884ee50d`.

## AT-1: A new browser starts the Tour after the team pick

App: site
Then: After the team sheet closes, Stop 1 shows the header "Suggestions" and "1 of 4", and its hole sits on the Suggestions of Bo Girds.
Files: `evidence/AT-1/steps.json`, `evidence/AT-1/output.txt`, `evidence/AT-1/stop-1-1280-dark.png`, `evidence/AT-1/stop-1-1280-light.png`, `evidence/AT-1/stop-1-375-dark.png`, `evidence/AT-1/stop-1-375-light.png`, `evidence/AT-1/stop-1-768-dark.png`, `evidence/AT-1/stop-1-768-light.png`
Observation: Each shot shows the team sheet gone and the Stop card with the header "Suggestions" and "1 OF 4", with the hole on the Suggestions row of Bo Girds, at each width and theme. The output shows the test of AT-1, AT-5, and AT-6 passed in Chromium.

## AT-2: A browser with Your team and no seen key sees the Tour

App: site
Then: Stop 1 shows on load, with no team sheet first.
Files: `evidence/AT-2/steps.txt`, `evidence/AT-2/output.txt`, `evidence/AT-2/stop-1-1280-dark.png`, `evidence/AT-2/stop-1-1280-light.png`, `evidence/AT-2/stop-1-375-dark.png`, `evidence/AT-2/stop-1-375-light.png`, `evidence/AT-2/stop-1-768-dark.png`, `evidence/AT-2/stop-1-768-light.png`
Observation: Each shot shows Stop 1, "Suggestions" and "1 OF 4", over the front door of Bo Girds, with no team sheet. The output shows the test of AT-2 passed and found no dialog named "Which team is yours?".

## AT-3: Each Stop has its copy

App: site
Then: Each Stop shows the header, the line, and the count "n of 4" of the table in the PRD, word for word, and four dots with the current one marked.
Files: `evidence/AT-3/steps.json`, `evidence/AT-3/output.txt`, `evidence/AT-3/vitest.txt`, `evidence/AT-3/stop-1-1280-dark.png`, `evidence/AT-3/stop-1-1280-light.png`, `evidence/AT-3/stop-1-375-dark.png`, `evidence/AT-3/stop-1-375-light.png`, `evidence/AT-3/stop-1-768-dark.png`, `evidence/AT-3/stop-1-768-light.png`, `evidence/AT-3/stop-2-1280-dark.png`, `evidence/AT-3/stop-2-1280-light.png`, `evidence/AT-3/stop-2-375-dark.png`, `evidence/AT-3/stop-2-375-light.png`, `evidence/AT-3/stop-2-768-dark.png`, `evidence/AT-3/stop-2-768-light.png`, `evidence/AT-3/stop-3-1280-dark.png`, `evidence/AT-3/stop-3-1280-light.png`, `evidence/AT-3/stop-3-375-dark.png`, `evidence/AT-3/stop-3-375-light.png`, `evidence/AT-3/stop-3-768-dark.png`, `evidence/AT-3/stop-3-768-light.png`, `evidence/AT-3/stop-4-1280-dark.png`, `evidence/AT-3/stop-4-1280-light.png`, `evidence/AT-3/stop-4-375-dark.png`, `evidence/AT-3/stop-4-375-light.png`, `evidence/AT-3/stop-4-768-dark.png`, `evidence/AT-3/stop-4-768-light.png`
Observation: The four named shots at each width and theme show the headers Suggestions, Ask, Your team, and Menu with "1 OF 4" to "4 OF 4", the line of each Stop, and four dots with one long dot that moves one place per Stop. The Playwright output shows the test that checks each line and count of the four Stops passed, and `vitest.txt` shows the Vitest test of the copy, the count, and the four dots passed.

## AT-4: Stop 4 aims at the visible menu

App: site
Then: The hole sits on the menu button at 375 and 768 px, and on the pill bar "Site menu" at 1280 px.
Files: `evidence/AT-4/steps.json`, `evidence/AT-4/output.txt`, `evidence/AT-4/stop-4-1280-dark.png`, `evidence/AT-4/stop-4-1280-light.png`, `evidence/AT-4/stop-4-375-dark.png`, `evidence/AT-4/stop-4-375-light.png`, `evidence/AT-4/stop-4-768-dark.png`, `evidence/AT-4/stop-4-768-light.png`
Observation: At 375 and 768 px the hole is a circle on the menu button at the top right. At 1280 px the hole is a pill on the pill bar of the site menu, with the Menu card under it. The output shows the three tests of AT-4 passed, each with the hole center within 1 px of the target center.

## AT-5: The Tour never shows over the team sheet

App: site
Then: No dim and no Stop card show.
Files: `evidence/AT-5/steps.json`, `evidence/AT-5/output.txt`, `evidence/AT-5/team-sheet-1280-dark.png`, `evidence/AT-5/team-sheet-1280-light.png`, `evidence/AT-5/team-sheet-375-dark.png`, `evidence/AT-5/team-sheet-375-light.png`, `evidence/AT-5/team-sheet-768-dark.png`, `evidence/AT-5/team-sheet-768-light.png`
Observation: Each shot shows the team sheet "Which team is yours?" open with no dim of the Tour and no Stop card. The output shows the test found no `[data-tour-card]` and no `[data-tour-hole]` 1200 ms after load, while the sheet was open.

## AT-6: norcal gets the same Tour

App: site
Then: The four Stops show the same headers, lines, and counts as cpc.
Files: `evidence/AT-6/steps.json`, `evidence/AT-6/output.txt`, `evidence/AT-6/vitest.txt`, `evidence/AT-6/stop-1-375-light.png`, `evidence/AT-6/stop-2-375-light.png`, `evidence/AT-6/stop-3-375-light.png`, `evidence/AT-6/stop-4-375-light.png`
Observation: The four norcal shots at 375 px light show the headers Suggestions, Ask, Your team, and Menu, the same lines, and "1 OF 4" to "4 OF 4", on the NorCal Apex 6 front door. The output shows the e2e test passed on the norcal export, and `vitest.txt` shows the norcal Vitest test passed.

## AT-7: Next goes to the next Stop

App: site
Then: Stop 2 shows the header "Ask" and "2 of 4", and its hole sits on the ask box.
Files: `evidence/AT-7/steps.json`, `evidence/AT-7/output.txt`, `evidence/AT-7/stop-2-1280-dark.png`, `evidence/AT-7/stop-2-1280-light.png`, `evidence/AT-7/stop-2-375-dark.png`, `evidence/AT-7/stop-2-375-light.png`, `evidence/AT-7/stop-2-768-dark.png`, `evidence/AT-7/stop-2-768-light.png`
Observation: Each shot shows the card "Ask" with "2 OF 4" and the hole on the ask box. The output shows the test of AT-7 and AT-8 passed, with `data-tour-target` on `form[aria-label="Ask"]`.

## AT-8: A tap on the dim goes to the next Stop

App: site
Then: From Stop 1, Stop 2 shows. From Stop 4, the dim and the card are gone.
Files: `evidence/AT-8/output.txt`
Observation: The output shows one test passed. A tap on a dim corner at Stop 1 went to Stop 2 and showed the card "Your team" after one more tap. A tap on the dim at Stop 4 left no dialog and no hole.

## AT-9: Skip ends the Tour

App: site
Then: The dim and the card are gone, and the front door responds to taps again.
Files: `evidence/AT-9/steps.json`, `evidence/AT-9/output.txt`, `evidence/AT-9/after-skip-1280-dark.png`, `evidence/AT-9/after-skip-1280-light.png`, `evidence/AT-9/after-skip-375-dark.png`, `evidence/AT-9/after-skip-375-light.png`, `evidence/AT-9/after-skip-768-dark.png`, `evidence/AT-9/after-skip-768-light.png`
Observation: Each shot shows the front door with no dim and no card after Skip at Stop 2. The output shows the test passed, and the tap on More after Skip set `aria-expanded` to `true`.

## AT-10: The Escape key counts as Skip

App: site
Then: The dim and the card are gone.
Files: `evidence/AT-10/output.txt`
Observation: The output shows the test at 1280x800 passed. After Escape at Stop 2, no dialog and no hole are on the page.

## AT-11: Android Back counts as Skip

App: site
Then: The Tour ends.
Files: `evidence/AT-11/e2e-output.txt`, `evidence/AT-11/output.txt`
Observation: The output shows three Vitest tests of AT-11 passed, among them "ends on Android Back, through the CloseWatcher of the Stop card" and "sends the reason back to onDismissAttempt on a close request of the browser". `e2e-output.txt` shows the Chromium test of a close request at Stop 2 passed.

## AT-12: Stop 4 says Done, and Done ends the Tour

App: site
Then: Stop 4 shows Done and no Next, and after the tap the dim and the card are gone.
Files: `evidence/AT-12/steps.json`, `evidence/AT-12/output.txt`, `evidence/AT-12/stop-4-1280-dark.png`, `evidence/AT-12/stop-4-1280-light.png`, `evidence/AT-12/stop-4-375-dark.png`, `evidence/AT-12/stop-4-375-light.png`, `evidence/AT-12/stop-4-768-dark.png`, `evidence/AT-12/stop-4-768-light.png`
Observation: Each shot shows Stop 4 "Menu" with Skip and Done and no Next. The output shows the test passed, with no Next button at Stop 4 and no dialog or hole after Done.

## AT-13: A tap in the hole opens nothing

App: site
Then: No Answer and no passphrase sheet open. The Tour goes to Stop 2.
Files: `evidence/AT-13/output.txt`
Observation: The output shows the Topic center sat inside the hole and the test passed. It prints "Answers before: 0, after: 0. Passphrase sheets before: 0, after: 0.", and the card "Ask" showed after the tap.

## AT-14: The hole pad is even

App: site
Then: The hole extends past the visual box of its control by the same pad on all four sides: 6 px, or 10 px for a box under 28 px tall, to 1 px. The hole on the menu button is a circle, and each other hole is a pill.
Files: `evidence/AT-14/steps.json`, `evidence/AT-14/output.txt`, `evidence/AT-14/stop-1-1280-dark.png`, `evidence/AT-14/stop-1-1280-light.png`, `evidence/AT-14/stop-1-375-dark.png`, `evidence/AT-14/stop-1-375-light.png`, `evidence/AT-14/stop-2-1280-dark.png`, `evidence/AT-14/stop-2-1280-light.png`, `evidence/AT-14/stop-2-375-dark.png`, `evidence/AT-14/stop-2-375-light.png`, `evidence/AT-14/stop-3-1280-dark.png`, `evidence/AT-14/stop-3-1280-light.png`, `evidence/AT-14/stop-3-375-dark.png`, `evidence/AT-14/stop-3-375-light.png`, `evidence/AT-14/stop-4-1280-dark.png`, `evidence/AT-14/stop-4-1280-light.png`, `evidence/AT-14/stop-4-375-dark.png`, `evidence/AT-14/stop-4-375-light.png`
Observation: The output prints the pads of each Stop at 375 and 1280 px: 6 px on each side for the Suggestions, the ask box, and the pill bar, and 10 px or 9.98 px for the team switch and the 20 px menu icon. The menu hole at 375 px is 40x40 with radius 20, and each other hole is wider than tall with a radius of half its height. The shots show each Stop.

## AT-15: The hole and the card glide together

App: site
Then: In each frame sample of the move, the offset of the card from the hole differs from its offset at rest by 2 px or less, until the card changes side.
Files: `evidence/AT-15/output.txt`
Observation: The output prints 84 frame samples from Stop 1 to Stop 2 at 390x660 with motion on. It prints "side change: false, compared: 84, largest drift: 0.51 px", and the test passed.

## AT-16: The card never covers its control

App: site
Then: The rect of the card does not overlap the rect of the control of the Stop.
Files: `evidence/AT-16/steps.txt`, `evidence/AT-16/output.txt`, `evidence/AT-16/1080x740-ask.png`, `evidence/AT-16/1080x740-menu.png`, `evidence/AT-16/1080x740-suggestions.png`, `evidence/AT-16/1080x740-your-team.png`, `evidence/AT-16/1280x800-ask.png`, `evidence/AT-16/1280x800-menu.png`, `evidence/AT-16/1280x800-suggestions.png`, `evidence/AT-16/1280x800-your-team.png`, `evidence/AT-16/390x660-ask.png`, `evidence/AT-16/390x660-menu.png`, `evidence/AT-16/390x660-suggestions.png`, `evidence/AT-16/390x660-your-team.png`, `evidence/AT-16/810x980-ask.png`, `evidence/AT-16/810x980-menu.png`, `evidence/AT-16/810x980-suggestions.png`, `evidence/AT-16/810x980-your-team.png`
Observation: The output prints the card and control rects of the four Stops on each of the four viewports, each with "overlap false", and the four tests passed. The 16 shots show each Stop card beside its control, with the copy of that Stop.

## AT-17: The card height stays the same

App: site
Then: The card height is the same at each Stop, to 1 px.
Files: `evidence/AT-17/output.txt`
Observation: The output prints the card heights 176.09375 at each of the four Stops at 375 px, and 211.390625 at each Stop at 1280 px. Both tests passed.

## AT-18: Each target scrolls into view

App: site
Then: When each Stop shows, the whole rect of its control is inside the visual viewport.
Files: `evidence/AT-18/output.txt`
Observation: The output prints the control rect of each Stop inside the visual viewport of 390x660. The lowest bottom edge is 493.39 px, for the team switch, and the test passed.

## AT-19: The hole follows a resize

App: site
Then: After the resize, the center of the hole is within 2 px of the center of the ask box.
Files: `evidence/AT-19/steps.txt`, `evidence/AT-19/output.txt`, `evidence/AT-19/390x660.png`, `evidence/AT-19/660x390.png`
Observation: The output prints the ask box center at the hole center before the turn, and after it at 660x390: hole x 60 y 306.92 540x66, ask box x 66 y 312.92 528x54. The test passed, and the two shots show the Ask card and the hole on the ask box at each size.

## AT-20: Under reduced motion the hole jumps

App: site
Then: No frame sample shows the hole at a place between the Suggestions and the ask box, and Stop 2 shows its full copy.
Files: `evidence/AT-20/output.txt`
Observation: The output prints 74 frame samples of the hole at 375x660 under reduced motion, and "frames between the Stops: 0". The test passed and found the full Ask line visible at Stop 2.

## AT-21: Under reduced motion the swaps use no blur and no scale

App: site
Then: No frame sample shows a `blur` filter on the card text or a scale other than 1 on the card.
Files: `evidence/AT-21/output.txt`
Observation: The output prints 68 frame samples under reduced motion, each with `filters` 0 and `scale` 1, and "most parts with a filter: 0, scales: 1". The test passed.

## AT-22: Next and Done use the brand accent

App: site
Then: The fill of Next and of Done is the computed color of the `accent` token, and the text is the `on-dark` color, in both themes.
Files: `evidence/AT-22/steps.json`, `evidence/AT-22/output.txt`, `evidence/AT-22/stop-1-1280-dark.png`, `evidence/AT-22/stop-1-1280-light.png`, `evidence/AT-22/stop-1-375-dark.png`, `evidence/AT-22/stop-1-375-light.png`, `evidence/AT-22/stop-1-768-dark.png`, `evidence/AT-22/stop-1-768-light.png`, `evidence/AT-22/stop-4-1280-dark.png`, `evidence/AT-22/stop-4-1280-light.png`, `evidence/AT-22/stop-4-375-dark.png`, `evidence/AT-22/stop-4-375-light.png`, `evidence/AT-22/stop-4-768-dark.png`, `evidence/AT-22/stop-4-768-light.png`
Observation: The output prints the same computed colors in both themes: the `accent` token, Next, and Done all have the fill rgb(184, 52, 42), and the `on-dark` token and the button text are rgb(255, 255, 255). The shots show Next at Stop 1 and Done at Stop 4 in red with white text.

## AT-23: Stop 1 writes the seen key

App: site
Then: The seen key `cpc.tour-seen` holds `"1"`.
Files: `evidence/AT-23/output.txt`
Observation: The output prints "AT-23 localStorage cpc.tour-seen: \"1\"" after Stop 1 showed, and the test passed.

## AT-24: A second visit after Skip shows no Tour

App: site
Then: No dim and no Stop card show.
Files: `evidence/AT-24/steps.txt`, `evidence/AT-24/dom.txt`, `evidence/AT-24/output.txt`, `evidence/AT-24/second-visit-1280-dark.png`, `evidence/AT-24/second-visit-1280-light.png`, `evidence/AT-24/second-visit-375-dark.png`, `evidence/AT-24/second-visit-375-light.png`, `evidence/AT-24/second-visit-768-dark.png`, `evidence/AT-24/second-visit-768-light.png`
Observation: Each full-page shot shows the front door with no dim and no card on the second visit after Skip at Stop 1. `dom.txt` shows 0 cards, 0 holes, and the seen key "1" for each width and theme, and the output shows the test passed.

## AT-25: A reload during the Tour does not start it again

App: site
Then: No dim and no Stop card show.
Files: `evidence/AT-25/output.txt`
Observation: The output shows the test passed. After a reload at Stop 2, it found no dialog and no hole 1200 ms after the Suggestions showed.

## AT-26: A failed storage read starts no Tour

App: site
Then: No Stop card renders, and the Suggestions render.
Files: `evidence/AT-26/output.txt`
Observation: The output shows the two Vitest tests of AT-26 passed: the store reads as seen when the read throws, and the front door shows no Tour and still renders the Suggestions.

## AT-27: The menu sheet link replays the Tour

App: site
Then: The menu sheet closes, then Stop 1 shows.
Files: `evidence/AT-27/steps.json`, `evidence/AT-27/output.txt`, `evidence/AT-27/menu-sheet-375-dark.png`, `evidence/AT-27/menu-sheet-375-light.png`, `evidence/AT-27/menu-sheet-768-dark.png`, `evidence/AT-27/menu-sheet-768-light.png`
Observation: The shots at 375 and 768 px in both themes show the open menu sheet with a "Show the tour" row at its end, under Trade Analyzer. The output shows both tests passed: after the tap, the sheet navigation was gone and Stop 1 showed "1 of 4".

## AT-28: The "?" button replays the Tour on desktop

App: site
Then: Stop 1 shows. The button has the accessible name "Show the tour".
Files: `evidence/AT-28/steps.json`, `evidence/AT-28/output.txt`, `evidence/AT-28/top-band-1280-dark.png`, `evidence/AT-28/top-band-1280-light.png`
Observation: The shots show the top band at 1280 px with a "?" icon button just before the theme button, in both themes. The output shows the test passed, with the accessible name "Show the tour", the next sibling named "Switch to ... theme", and Stop 1 after the tap.

## AT-29: The card has a name and a description

App: site
Then: The accessible name of the card is "Suggestions", and its description is the line of Stop 1.
Files: `evidence/AT-29/output.txt`
Observation: The output prints the accessibility snapshot: `dialog "Suggestions"` with the heading "Suggestions", "1 of 4", the paragraph of the Stop 1 line, and the buttons Skip and Next. The test passed its accessible description check with the Stop 1 line.

## AT-30: Focus stays in the card

App: site
Then: Focus moves only between Skip and Next, and never reaches the page behind.
Files: `evidence/AT-30/output.txt`
Observation: The output prints the focused element after each of four Tabs at Stop 2: ["Skip","Next","Skip","Next"]. Each one was inside the dialog, and the test passed.

## AT-31: Focus goes back after the Tour

App: site
Then: Focus is on the "?" button.
Files: `evidence/AT-31/output.txt`
Observation: The output prints "AT-31 focused element after Done: BUTTON aria-label=\"Show the tour\"", and the test passed.

## AT-32: The Tour blurs a focused field

App: site
Then: No text field has focus.
Files: `evidence/AT-32/output.txt`
Observation: The replay test prints the page when the card joined it, `{"field":false,"sheet":false}`, and the focused element at Stop 1, `BODY`. The second test, with a test modal layer, prints `{"tag":"BODY","text":false}`. Both tests passed.

## AT-33: A hold in the Tour starts no egg

App: site
Then: No egg check request goes out, and no egg card shows.
Files: `evidence/AT-33/output.txt`
Observation: The output prints the network log of 18 requests: the page, its scripts, fonts, and images on 127.0.0.1, and calls to api.4thandgoal.app and gc.zgo.at that the test route aborts. No request goes to `/eggs/check`, the egg check list is `[]`, and the test passed.

## AT-34: No Tour and no replay on the other pages

App: site
Then: No dim, no Stop card, no "Show the tour" link, and no "?" button show, and the seen key is not set.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/dom.txt`, `evidence/AT-34/output.txt`, `evidence/AT-34/2026-week-10-menu-375-dark.png`, `evidence/AT-34/2026-week-10-menu-375-light.png`, `evidence/AT-34/analyze-menu-375-dark.png`, `evidence/AT-34/analyze-menu-375-light.png`
Observation: The shots of `/2026/week-10/` and `/analyze/` at 375 px show the menu sheet open with no "Show the tour" row, no dim, and no card. `dom.txt` shows 0 replay buttons, 0 cards, 0 holes, and the seen key null for each page and theme. The output shows both tests passed.

## AT-35: The menu sheet does not open during the Tour

App: site
Then: No menu sheet opens.
Files: `evidence/AT-35/output.txt`
Observation: The output shows the test at 375 px passed. After a tap on the menu button in the hole at Stop 4, no dialog "Menu", no navigation "Pages", and no "Close the menu" button are on the page.

## AT-36: No tour library

App: site
Then: No match.
Files: `evidence/AT-36/output.txt`
Observation: The output shows `grep -n "driver.js"` over the 11 tracked `package.json` files and `pnpm-lock.yaml` printed no line and ended with exit 1.

## AT-37: No pipeline or API change

App: site
Then: No changed path starts with `apps/pipeline/` or `apps/api/`.
Files: `evidence/AT-37/output.txt`
Observation: The output lists 43 changed files under `apps/site/`, `packages/design/`, `.scratch/front-door-tour/`, and `docs/agents/`, and `GLOSSARY.md`. The grep for `^apps/(pipeline|api)/` over the changed names printed no line and ended with exit 1.

## AT-38: The Tour waits for an open modal layer

App: site
Then: No Stop card shows while the layer is open, and Stop 1 shows after the layer finishes its exit.
Files: `evidence/AT-38/output.txt`
Observation: The output prints "AT-38 open modal layers: [\"test-modal-layer (A test modal layer)\"]". The layer is the test's own `div` with role `dialog` and `aria-modal="true"`, because no Announcement ships yet. The test found no card while the layer was open, and Stop 1 "1 of 4" after the test removed the layer.

## AT-39: The Stop card is a modal layer

App: site
Then: The card has role `dialog` and `aria-modal="true"`.
Files: `evidence/AT-39/output.txt`
Observation: The output prints "AT-39 role: dialog, aria-modal: true" and the accessibility snapshot `dialog "Suggestions"` of the card. The test passed.
