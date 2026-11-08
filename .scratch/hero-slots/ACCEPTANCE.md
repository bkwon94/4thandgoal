# Hero slots: acceptance tests

Spec: `.scratch/hero-slots/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

All tests use the `cpc` client and the published data of `2026` week 8, unless the test names another client. The evidence agent records the values that the spec does not give: the rank-1 team of the power rankings of week 8, the leader of the midseason report, and the odds of the manager tiles.

A "scene screenshot" is a screenshot of the scene after the settle, at 2.5 s after entry, unless the test names another time.

## Tests

AT-1: The slot order
App: site
Stories: 1, 6, 7, 15, 16
Given: The manager page of roster 7, "To Infinity and Bijan".
When: The reader opens the page.
Then: The hero shows, top to bottom: the eyebrow "7-9 · 9th of 12", the title "To Infinity and Bijan", the owner "bjpicard96", the avatar with the grade mark and the week chips, then the odds tiles.
Evidence: screenshots of the manager hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-2: One title style
App: site
Stories: 2
Given: The first hero of the week page of week 8, the manager page of roster 7, `/rankings/`, `/midseason/2026/`, `/analyze/`, and the 404 page.
When: The reader opens each page.
Then: The title of each hero has a computed font size of 40px and a weight of 300.
Evidence: a table of the computed font size and weight of each title, from Playwright, and screenshots of each hero at 375 px in the dark theme.

AT-3: One eyebrow style
App: site
Stories: 3
Given: The same six pages as AT-2.
When: The reader opens each page.
Then: Each eyebrow has the same computed font family, font size, text transform, letter spacing, and color.
Evidence: a table of the computed styles of each eyebrow, from Playwright.

AT-4: A short meta line
App: site
Stories: 4, 5
Given: The same six pages as AT-2.
When: The reader opens each page at 375 px.
Then: Each meta line has a computed font size of 16px and takes two lines or fewer.
Evidence: a table of the font size and the line count of each meta line, from Playwright, and screenshots of each hero at 375 px in the dark theme.

AT-5: The action sits at the bottom
App: site
Stories: 8
Given: The week page of week 8.
When: The reader opens the page.
Then: The share bar is the last part inside the hero, under the team rows.
Evidence: screenshots of the week hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-6: One column on a phone
App: site
Stories: 9
Given: The week page of week 8.
When: The reader opens the page at 375 px.
Then: The scene, the eyebrow, the title, the meta, the team rows, and the share bar stack in one column, in that order.
Evidence: screenshots of the week hero at 375 px in the light theme and the dark theme.

AT-7: Two rows on a tablet
App: site
Stories: 10
Given: The manager page of roster 7.
When: The reader opens the page at 768 px.
Then: The eyebrow and the title sit at the top left, the meta sits at the top right, and the odds tiles sit at the bottom left.
Evidence: screenshots of the manager hero at 768 and 1280 px, each in the light theme and the dark theme.

AT-8: The hairline above the stats
App: site
Stories: 7
Given: The manager page of roster 7.
When: The reader opens the page at each width.
Then: A thin line shows directly above the odds tiles at 768 and 1280 px. No line shows there at 375 px.
Evidence: screenshots of the bottom of the manager hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-9: No empty gap
App: site
Stories: 11
Given: The analyzer result of grade-clarity trade A: roster 10 gives Omar Cooper Jr. (`13276`) to roster 6 for Parker Washington (`9487`). Roster 10 asks.
When: The reader grades trade A.
Then: The hero ends at the fairness block, with the same space under it as above the eyebrow. No empty area for stats or an action shows.
Evidence: screenshots of the analyzer result at 375, 768, and 1280 px, each in the light theme and the dark theme, from a run on the real API.

AT-10: The Matchup title is words
App: site
Stories: 12
Given: The week page of week 8. The Blue Tent scored 100.31 and London Cooking scored 98.88.
When: The reader opens the page.
Then: The title of the hero reads "The Blue Tent by 1.43".
Evidence: screenshots of the week hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-11: The blurb sits under the hero
App: site
Stories: 13
Given: The week page of week 8. Its blurb starts "The Blue Tent stole this one by 1.43".
When: The reader opens the page.
Then: The blurb shows as a paragraph directly under the hero, outside its frame. The hero holds no blurb.
Evidence: screenshots of the week hero and the paragraph under it at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-12: The 404 title
App: site
Stories: 14
Given: A path that no page has, such as `/no-such-page/`.
When: The reader opens it.
Then: The `h1` of the hero reads "Page not found", and a large "404" shows in the hero as art.
Evidence: screenshots of the 404 page at 375, 768, and 1280 px, each in the light theme and the dark theme, and the text of its `h1` from Playwright.

AT-13: The heading level
App: site
Stories: 47
Given: The midseason report `/midseason/2026/`.
When: The reader opens the report.
Then: The title of the opener is an `h1`, the title of each act title is an `h2`, and both have the same computed font size and weight.
Evidence: a list of the heading level, font size, and weight of each hero title of the report, from Playwright.

AT-14: Hero takes no free content
App: site
Stories: 44, 46
Given: A test file that passes `children` to `Hero` under `@ts-expect-error`.
When: The developer runs the typecheck.
Then: The typecheck passes, which proves that `Hero` rejects `children`. A hero with only a `title` renders.
Evidence: the test file and the output of `pnpm typecheck` and `pnpm test` for that file.

AT-15: The Matchup scene
App: site
Stories: 17, 18, 20, 21
Given: The week page of week 8. The league median is 99.60. The lowest score is Lil Fridge, 80.11, and the highest is Teehee, 134.1.
When: The reader opens the page and waits for the settle.
Then: The scene shows 12 lights from low to high, a dashed line labeled "99.60", and the lights of The Blue Tent and London Cooking in the accent color.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-16: The settle time
App: site
Stories: 18, 19
Given: The week page of week 8.
When: The reader opens the page at 375 px.
Then: At 0.5 s after entry the lights are not yet in their chart places. At 2.2 s they are settled.
Evidence: frames of the scene at 0.5, 1.0, and 2.2 s after entry, at 375 px in the dark theme.

AT-17: The margin stays visible
App: site
Stories: 22
Given: The week page of week 8.
When: The reader waits for the settle, so the label of The Blue Tent shows.
Then: The margin mark "+1.43" shows in full, and no label covers any part of it.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-18: The manager scene
App: site
Stories: 23
Given: The manager page of roster 7. Its weeks 1 to 8 score 109.21 L, 96.1 L, 107.39 W, 118.28 W, 66.82 L, 46.08 L, 106.32 L, 118.89 W.
When: The reader opens the page and waits for the settle.
Then: The scene shows 8 lights from week 1 to week 8. The lights of weeks 3, 4, and 8 are bright, the other five are dim, and a dashed line marks the median of each week.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-19: The rankings scene
App: site
Stories: 24
Given: `/rankings/` for week 8.
When: The reader opens the page and waits for the settle.
Then: The scene shows 12 lights in the order of the power rank, each at the height of its playoff odds. The light of the rank-1 team is in the accent color and shows its label.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme, and the name and odds of the rank-1 team.

AT-20: The analyzer drift
App: site
Stories: 25
Given: `/analyze/` with no trade graded.
When: The reader opens the page and waits 6 s.
Then: The lights of the scene move the whole time and do not settle into a chart.
Evidence: frames of the scene at 2 s and 6 s after entry, at 375 px in the dark theme.

AT-21: The analyzer settle
App: site
Stories: 26
Given: `/analyze/` and grade-clarity trade A. The verdict is "Yes" for behold the lamb.
When: The reader grades trade A.
Then: When the verdict arrives, the lights settle into two groups, one per side, and the bigger group sits on the side of behold the lamb.
Evidence: frames of the scene before the grade and 2.5 s after the verdict, at 375 and 1280 px in the dark theme, from a run on the real API.

AT-22: The midseason scene
App: site
Stories: 27
Given: `/midseason/2026/` for the `cpc` client.
When: The reader opens the report and waits for the settle.
Then: The scene shows 12 lights at the season total points in the order of the standings, and the light of the leader is in the accent color.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme, and the name of the leader.

AT-23: The 404 drift
App: site
Stories: 28
Given: A path that no page has, such as `/no-such-page/`.
When: The reader opens it and waits 6 s.
Then: The frames at 2 s and at 6 s differ, and the lights never form a chart.
Evidence: frames of the scene at 2 s and 6 s after entry, at 375 px in the dark theme.

AT-24: The label at rest
App: site
Stories: 29
Given: The week page of week 8.
When: The reader waits for the settle and taps nothing.
Then: The label "The Blue Tent · 100.31" shows next to its light.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-25: A tap selects the nearest light
App: site
Stories: 30
Given: The week page of week 8, after the settle.
When: The reader taps empty space in the scene, closer to the light of Lil Fridge than to any other light.
Then: The label "Lil Fridge · 80.11" shows, and the scene does not play again.
Evidence: the point of the tap, and scene screenshots before and after the tap at 375 px in the dark theme.

AT-26: A slide scrubs the lights
App: site
Stories: 31
Given: The week page of week 8, after the settle.
When: The reader drags a finger sideways across the scene and stops over the light of London Cooking.
Then: The label "London Cooking · 98.88" shows.
Evidence: the path of the drag, and a scene screenshot at its end at 375 px in the dark theme.

AT-27: A vertical swipe scrolls
App: site
Stories: 32
Given: The week page of week 8 at 375 px, with touch on.
When: The reader swipes up from a point inside the scene.
Then: The page scrolls down.
Evidence: the scroll position before and after the swipe, from Playwright, and screenshots before and after.

AT-28: The hint shows once
App: site
Stories: 33, 34
Given: The week page of week 8, with no stored hint flag.
When: The reader sees the scene, taps it once, then reloads the page.
Then: "TAP OR SLIDE" shows before the tap, is gone after the tap, and does not show after the reload.
Evidence: scene screenshots before the tap, after the tap, and after the reload, at 375 px in the dark theme.

AT-29: A label at an edge
App: site
Stories: 35
Given: The week page of week 8, after the settle.
When: The reader taps the right-most light, Teehee.
Then: The label "Teehee · 134.1" shows in full, inside the scene.
Evidence: scene screenshots after the tap at 375, 768, and 1280 px in the dark theme.

AT-30: Replay on re-entry
App: site
Stories: 36
Given: The week page of week 8, after the settle.
When: The reader scrolls until the hero is fully out of view, then scrolls back.
Then: The lights move again and settle again.
Evidence: frames of the scene at 0.5 s and 2.5 s after the hero comes back, at 375 px in the dark theme.

AT-31: Reduced motion
App: site
Stories: 37
Given: The week page of week 8, with reduced motion on.
When: The reader opens the page.
Then: The settled chart shows at once, with the frame at 0.1 s the same as the frame at 2.5 s.
Evidence: frames of the scene at 0.1 s and 2.5 s after entry, at 375 px in the light theme and the dark theme.

AT-32: The loop stops at rest
App: site
Stories: 38
Given: The week page of week 8.
When: The reader waits for the settle, then waits 3 s more.
Then: The page requests no animation frame in those 3 s.
Evidence: the count of `requestAnimationFrame` calls in the 3 s, from Playwright.

AT-33: The hero stays dark in the light theme
App: site
Stories: 39
Given: The week page of week 8 in the light theme.
When: The reader opens the page.
Then: The page is light, and the hero and its scene stay dark with the same lights as in the dark theme.
Evidence: scene screenshots at 375, 768, and 1280 px in the light theme.

AT-34: NorCal colors
App: site
Stories: 40
Given: The `norcal` client and its latest published week.
When: The reader opens the week page and waits for the settle.
Then: The two flared lights of the Matchup have the color `#c2410c`.
Evidence: scene screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme, and the color of a flared light read from the canvas.

AT-35: Only the first hero moves
App: site
Stories: 41, 45
Given: The home page, and the midseason report `/midseason/2026/`.
When: The reader opens each page.
Then: The home page has exactly one scene. In the report, the opener has a scene and no act title has one.
Evidence: the count of scene canvases on each page, from Playwright, and screenshots of the act titles at 375 px in the dark theme.

AT-36: A tap on the content still works
App: site
Stories: 42
Given: The manager page of roster 7.
When: The reader taps the grade mark.
Then: The grade popover opens.
Evidence: screenshots before and after the tap at 375 and 1280 px in the dark theme.

AT-37: The readability floor passes
App: site
Stories: 43, 50
Given: The static export of `cpc` and of `norcal`.
When: The developer runs `pnpm check:floor` for each client.
Then: Both runs pass.
Evidence: the output of each run.

AT-38: The math of the scene
App: site
Stories: 48, 49
Given: The pure functions of the scene and the real fixture of week 8.
When: The developer runs their tests.
Then: The tests pass for the place of each light, the nearest light to a point, the side of a label near an edge, and the place of the margin mark clear of every label.
Evidence: the test file and the output of `pnpm test` for it.

AT-39: No scan line
App: site
Stories: none
Given: The week page of week 8 and the manager page of roster 7.
When: The reader opens each page.
Then: No line sweeps across the hero on entry, and the stylesheet holds no scan-line rule.
Evidence: frames of each hero at 0.3 and 0.8 s after entry, at 375 px in the dark theme, and a search of the global stylesheet for the scan-line rule.

AT-40: No 3D engine
App: site
Stories: none
Given: The finished spec branch.
When: The developer reads the dependencies and the scene code.
Then: No package of three.js or another 3D engine is added, and the scene asks for a `2d` context only.
Evidence: the diff of each `package.json` and `pnpm-lock.yaml`, and the line of the scene that gets its context.

AT-41: No "Read more"
App: site
Stories: none
Given: The week page of week 8.
When: The reader reads the blurb.
Then: The full blurb shows, with no "Read more" control and no fold.
Evidence: screenshots of the blurb at 375 px in the light theme and the dark theme.

AT-42: No pipeline change
App: site
Stories: none
Given: The finished spec branch.
When: The developer diffs it against `main`.
Then: No file under `apps/pipeline/` and no published file under `clients/` changes.
Evidence: the output of `git diff --stat main -- apps/pipeline clients`.

## Trace

Story 1: AT-1
Story 2: AT-2
Story 3: AT-3
Story 4: AT-4
Story 5: AT-4
Story 6: AT-1
Story 7: AT-1, AT-8
Story 8: AT-5
Story 9: AT-6
Story 10: AT-7
Story 11: AT-9
Story 12: AT-10
Story 13: AT-11
Story 14: AT-12
Story 15: AT-1
Story 16: AT-1
Story 17: AT-15
Story 18: AT-15, AT-16
Story 19: AT-16
Story 20: AT-15
Story 21: AT-15
Story 22: AT-17
Story 23: AT-18
Story 24: AT-19
Story 25: AT-20
Story 26: AT-21
Story 27: AT-22
Story 28: AT-23
Story 29: AT-24
Story 30: AT-25
Story 31: AT-26
Story 32: AT-27
Story 33: AT-28
Story 34: AT-28
Story 35: AT-29
Story 36: AT-30
Story 37: AT-31
Story 38: AT-32
Story 39: AT-33
Story 40: AT-34
Story 41: AT-35
Story 42: AT-36
Story 43: AT-37
Story 44: AT-14
Story 45: AT-35
Story 46: AT-14
Story 47: AT-13
Story 48: AT-38
Story 49: AT-38
Story 50: AT-37
Out of scope "the scan line": AT-39
Out of scope "Three.js or WebGL": AT-40
Out of scope "a 'Read more' control for the blurb of the Matchup": AT-41
Out of scope "a change to the pipeline": AT-42
Out of scope "a tap or a slide during the settle": no test. Reason: the spec accepts it as a known gap, so a test would only fix the gap in place.

## Revisions

None yet.
