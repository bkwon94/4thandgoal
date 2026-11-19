# Front door tour: acceptance tests

Spec: `.scratch/front-door-tour/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The client of the tests is cpc, on the static export of the `2026` week 10 build, unless a test names norcal. The team is Bo Girds, roster 6 in cpc and roster 7 in norcal. The front door is `/`.

"Site screenshots" means screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme (ADR 0006). "The four viewports" means 390x660 iPhone WebKit, iPad 810x980 and 1080x740 WebKit, and 1280x800 Chromium. "A new browser" means a browser context with an empty `localStorage`. "The seen key" is `cpc.tour-seen`.

## Tests

AT-1: A new browser starts the Tour after the team pick
App: site
Stories: 1, 2, 4
Given: A new browser on the cpc front door.
When: The reader picks Bo Girds in the team sheet.
Then: After the team sheet closes, Stop 1 shows the header "Suggestions" and "1 of 4", and its hole sits on the Suggestions of Bo Girds.
Evidence: site screenshots of Stop 1, and the Playwright test name and output.

AT-2: A browser with Your team and no seen key sees the Tour
App: site
Stories: 3
Given: A browser with Your team set to Bo Girds and no seen key.
When: The reader opens the front door.
Then: Stop 1 shows on load, with no team sheet first.
Evidence: site screenshots of Stop 1, and the Playwright test name and output.

AT-3: Each Stop has its copy
App: site
Stories: 4, 5, 6, 9, 10, 44
Given: The Tour at Stop 1 for Bo Girds.
When: The reader taps Next through all four Stops.
Then: Each Stop shows the header, the line, and the count "n of 4" of the table in the PRD, word for word, and four dots with the current one marked.
Evidence: site screenshots of each of the four Stops, and the Playwright test name and output.

AT-4: Stop 4 aims at the visible menu
App: site
Stories: 7, 8
Given: The Tour for Bo Girds.
When: The reader reaches Stop 4.
Then: The hole sits on the menu button at 375 and 768 px, and on the pill bar "Site menu" at 1280 px.
Evidence: site screenshots of Stop 4.

AT-5: The Tour never shows over the team sheet
App: site
Stories: 42
Given: A new browser on the cpc front door.
When: The team sheet is open, before a pick.
Then: No dim and no Stop card show.
Evidence: site screenshots of the open team sheet, and the Playwright test name and output.

AT-6: norcal gets the same Tour
App: site
Stories: 43
Given: A new browser on the norcal front door of the `2026` week 10 build.
When: The reader picks Bo Girds and taps Next through all four Stops.
Then: The four Stops show the same headers, lines, and counts as cpc.
Evidence: site screenshots of each Stop at 375 px in the light theme, and the Playwright test name and output.

AT-7: Next goes to the next Stop
App: site
Stories: 11
Given: The Tour at Stop 1.
When: The reader taps Next.
Then: Stop 2 shows the header "Ask" and "2 of 4", and its hole sits on the ask box.
Evidence: site screenshots of Stop 2, and the Playwright test name and output.

AT-8: A tap on the dim goes to the next Stop
App: site
Stories: 12
Given: The Tour at Stop 1, and in a second case at Stop 4.
When: The reader taps the dim area, away from the card and the hole.
Then: From Stop 1, Stop 2 shows. From Stop 4, the dim and the card are gone.
Evidence: the Playwright test name and output for both cases.

AT-9: Skip ends the Tour
App: site
Stories: 13
Given: The Tour at Stop 2.
When: The reader taps Skip.
Then: The dim and the card are gone, and the front door responds to taps again.
Evidence: site screenshots of the front door after Skip, and the Playwright test name and output.

AT-10: The Escape key counts as Skip
App: site
Stories: 14
Given: The Tour at Stop 2 at 1280 px.
When: The reader presses Escape.
Then: The dim and the card are gone.
Evidence: the Playwright test name and output.

AT-11: Android Back counts as Skip
App: site
Stories: 15
Given: The Vitest test of the Tour component at Stop 2.
When: `onDismissAttempt` gets the reason `back`.
Then: The Tour ends.
Evidence: the Vitest test name and output.

AT-12: Stop 4 says Done, and Done ends the Tour
App: site
Stories: 16
Given: The Tour at Stop 4.
When: The reader taps Done.
Then: Stop 4 shows Done and no Next, and after the tap the dim and the card are gone.
Evidence: site screenshots of Stop 4, and the Playwright test name and output.

AT-13: A tap in the hole opens nothing
App: site
Stories: 17
Given: The Tour at Stop 1, with a Topic of Bo Girds in the hole.
When: The reader taps the Topic inside the hole.
Then: No Answer and no passphrase sheet open. The Tour goes to Stop 2.
Evidence: the Playwright test name and output, with the count of Answers and sheets before and after.

AT-14: The hole pad is even
App: site
Stories: 18, 19
Given: The Tour for Bo Girds at 375 and 1280 px.
When: The reader reaches each of the four Stops.
Then: The hole extends past the visual box of its control by the same pad on all four sides: 6 px, or 10 px for a box under 28 px tall, to 1 px. The hole on the menu button is a circle, and each other hole is a pill.
Evidence: the measured rect of each control and each hole, and site screenshots of each Stop.

AT-15: The hole and the card glide together
App: site
Stories: 20
Given: The Tour at Stop 1 at 390x660, with motion on.
When: The reader taps Next.
Then: In each frame sample of the move, the offset of the card from the hole differs from its offset at rest by 2 px or less, until the card changes side.
Evidence: the frame samples, and the Playwright test name and output.

AT-16: The card never covers its control
App: site
Stories: 21
Given: The Tour for Bo Girds on each of the four viewports.
When: The reader reaches each of the four Stops.
Then: The rect of the card does not overlap the rect of the control of the Stop.
Evidence: the rects of each Stop on each viewport, the overlap assert output, and a screenshot of each Stop on each viewport.

AT-17: The card height stays the same
App: site
Stories: 22
Given: The Tour for Bo Girds at 375 and 1280 px.
When: The reader taps Next through all four Stops.
Then: The card height is the same at each Stop, to 1 px.
Evidence: the card height at each Stop, and the Playwright test name and output.

AT-18: Each target scrolls into view
App: site
Stories: 23
Given: The Tour for Bo Girds at 390x660, with the page scrolled to the top.
When: The reader taps Next through all four Stops.
Then: When each Stop shows, the whole rect of its control is inside the visual viewport.
Evidence: the control rect and the viewport size at each Stop, and the Playwright test name and output.

AT-19: The hole follows a resize
App: site
Stories: 24
Given: The Tour at Stop 2 at 390x660.
When: The viewport changes to 660x390.
Then: After the resize, the center of the hole is within 2 px of the center of the ask box.
Evidence: the rects before and after, screenshots at both sizes, and the Playwright test name and output.

AT-20: Under reduced motion the hole jumps
App: site
Stories: 25, 26
Given: The Tour at Stop 1 at 375 px, with reduced motion on.
When: The reader taps Next.
Then: No frame sample shows the hole at a place between the Suggestions and the ask box, and Stop 2 shows its full copy.
Evidence: the frame samples, and the Playwright test name and output.

AT-21: Under reduced motion the swaps use no blur and no scale
App: site
Stories: 25
Given: The Tour at Stop 1 at 375 px, with reduced motion on.
When: The reader taps Next.
Then: No frame sample shows a `blur` filter on the card text or a scale other than 1 on the card.
Evidence: the frame samples of `filter` and `transform`, and the Playwright test name and output.

AT-22: Next and Done use the brand accent
App: site
Stories: 27, 28
Given: The Tour for Bo Girds in the light theme and in the dark theme.
When: The reader sees Stop 1 and Stop 4.
Then: The fill of Next and of Done is the computed color of the `accent` token, and the text is the `on-dark` color, in both themes.
Evidence: the computed colors in both themes, and site screenshots of Stop 1 and Stop 4.

AT-23: Stop 1 writes the seen key
App: site
Stories: 30
Given: A browser with Your team set to Bo Girds and no seen key.
When: Stop 1 shows.
Then: The seen key `cpc.tour-seen` holds `"1"`.
Evidence: the `localStorage` value read in the Playwright test, and its output.

AT-24: A second visit after Skip shows no Tour
App: site
Stories: 29
Given: A browser where the reader tapped Skip at Stop 1.
When: The reader opens the front door again.
Then: No dim and no Stop card show.
Evidence: site screenshots of the second visit, and the Playwright test name and output.

AT-25: A reload during the Tour does not start it again
App: site
Stories: 31
Given: The Tour at Stop 2.
When: The reader reloads the page.
Then: No dim and no Stop card show.
Evidence: the Playwright test name and output.

AT-26: A failed storage read starts no Tour
App: site
Stories: 29
Given: The Vitest test of the Tour with a `localStorage.getItem` that throws.
When: The front door renders with Bo Girds as Your team.
Then: No Stop card renders, and the Suggestions render.
Evidence: the Vitest test name and output.

AT-27: The menu sheet link replays the Tour
App: site
Stories: 32, 34, 35
Given: A browser with the seen key, at 375 px.
When: The reader opens the menu sheet and taps "Show the tour".
Then: The menu sheet closes, then Stop 1 shows.
Evidence: site screenshots of the link in the menu sheet at 375 and 768 px in both themes, and the Playwright test name and output.

AT-28: The "?" button replays the Tour on desktop
App: site
Stories: 33, 35
Given: A browser with the seen key, at 1280 px.
When: The reader taps the "?" button beside the theme button.
Then: Stop 1 shows. The button has the accessible name "Show the tour".
Evidence: screenshots of the top band at 1280 px in both themes, and the Playwright test name and output.

AT-29: The card has a name and a description
App: site
Stories: 37
Given: The Tour at Stop 1.
When: A screen reader reads the card.
Then: The accessible name of the card is "Suggestions", and its description is the line of Stop 1.
Evidence: the accessibility snapshot of the card, and the Playwright test name and output.

AT-30: Focus stays in the card
App: site
Stories: 38
Given: The Tour at Stop 2 at 1280 px.
When: The reader presses Tab four times.
Then: Focus moves only between Skip and Next, and never reaches the page behind.
Evidence: the focused element after each Tab, and the Playwright test name and output.

AT-31: Focus goes back after the Tour
App: site
Stories: 39
Given: The "?" button had focus, and the reader started the replay with the keyboard at 1280 px.
When: The reader taps Done at Stop 4.
Then: Focus is on the "?" button.
Evidence: the focused element after Done, and the Playwright test name and output.

AT-32: The Tour blurs a focused field
App: site
Stories: 40
Given: A browser with the seen key, with the ask box focused at 390x660, and then a replay from the menu sheet.
When: Stop 1 shows.
Then: No text field has focus.
Evidence: the focused element at Stop 1, and the Playwright test name and output.

AT-33: A hold in the Tour starts no egg
App: site
Stories: 41
Given: The Tour at Stop 1 at 390x660.
When: The reader holds the dim for 2 s, then holds the card for 2 s.
Then: No egg check request goes out, and no egg card shows.
Evidence: the network log of the test, and the Playwright test name and output.

AT-34: No Tour and no replay on the other pages
App: site
Stories: 36
Given: A new browser.
When: The reader opens `/analyze/` and the week 10 report.
Then: No dim, no Stop card, no "Show the tour" link, and no "?" button show, and the seen key is not set.
Evidence: site screenshots of both pages with the menu sheet open at 375 px, and the Playwright test name and output.

AT-35: The menu sheet does not open during the Tour
App: site
Stories: none
Given: The Tour at Stop 4 at 375 px, with the menu button in the hole.
When: The reader taps the menu button.
Then: No menu sheet opens.
Evidence: the Playwright test name and output.

AT-36: No tour library
App: site
Stories: none
Given: The spec branch at the head of the PR.
When: The reader searches each `package.json` and `pnpm-lock.yaml` for `driver.js`.
Then: No match.
Evidence: the search command and its output.

AT-37: No pipeline or API change
App: site
Stories: none
Given: The spec branch at the head of the PR.
When: The reader runs `git diff --stat main...front-door-tour`.
Then: No changed path starts with `apps/pipeline/` or `apps/api/`.
Evidence: the command and its output.

## Trace

Story 1: AT-1
Story 2: AT-1
Story 3: AT-2
Story 4: AT-1, AT-3
Story 5: AT-3
Story 6: AT-3
Story 7: AT-4
Story 8: AT-4
Story 9: AT-3
Story 10: AT-3
Story 11: AT-7
Story 12: AT-8
Story 13: AT-9
Story 14: AT-10
Story 15: AT-11
Story 16: AT-12
Story 17: AT-13
Story 18: AT-14
Story 19: AT-14
Story 20: AT-15
Story 21: AT-16
Story 22: AT-17
Story 23: AT-18
Story 24: AT-19
Story 25: AT-20, AT-21
Story 26: AT-20
Story 27: AT-22
Story 28: AT-22
Story 29: AT-24, AT-26
Story 30: AT-23
Story 31: AT-25
Story 32: AT-27
Story 33: AT-28
Story 34: AT-27
Story 35: AT-27, AT-28
Story 36: AT-34
Story 37: AT-29
Story 38: AT-30
Story 39: AT-31
Story 40: AT-32
Story 41: AT-33
Story 42: AT-5
Story 43: AT-6
Story 44: AT-3
Out of scope "A Tour on the other pages": AT-34
Out of scope "Live facts of the week in the Stops": AT-3. Reason: the copy check word for word covers it.
Out of scope "A replay link on the other pages": AT-34
Out of scope "Any pipeline or API change": AT-37
Out of scope "A Stop inside the menu sheet": AT-35
Out of scope "A tour library such as `driver.js`": AT-36

## Revisions

None yet.
