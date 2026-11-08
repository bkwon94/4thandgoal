# Hero slots: evidence

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests: `.scratch/hero-slots/ACCEPTANCE.md`.
Built from: `c1a7c91c`, on 2026-11-08. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 7 min for 37 site tests.

The instrument of the site tests is a Playwright script, `evidence/AT-1/hero-slots.ev.ts.txt`, with its config `evidence/AT-1/ev.config.ts.txt`. Each `steps.txt` gives the method. The runner of `pnpm evidence` takes full-page shots after a scroll pass, and the pass plays the scene again, so its shot shows the scene before the settle. No runner verb times a frame, reads a computed style, counts frames, or taps a point of the canvas. The round time is the sum of the script runs: 4.5 min, 1.8 min, 0.6 min, 0.3 min, and 0.1 min.

The cpc export is `CLIENT=cpc NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build`. The norcal export of AT-34 is the export that `make check` built at the same commit. The analyzer tests ran on `make -C apps/api api-evidence` from the detached worktree `hero-slots-api` at `c1a7c91c`, with real Sleeper data and real Claude calls.

## AT-1: The slot order

App: site
Then: The hero shows, top to bottom: the eyebrow "7-9 · 9th of 12", the title "To Infinity and Bijan", the owner "bjpicard96", the avatar with the grade mark and the week chips, then the odds tiles.
Files: `evidence/AT-1/steps.txt`, `evidence/AT-1/slots.json`, `evidence/AT-1/375-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`
Observation: At 375 px the shots show, top to bottom, the scene, "7-9 · 9TH OF 12", "To Infinity and Bijan", "bjpicard96", the avatar with the grade "D" and the chips of weeks 1 to 8, then the tiles PLAYOFF 7%, BYE 1%, SEED —. At 768 and 1280 px "bjpicard96" sits at the top right, next to the eyebrow, and the scene sits between the title row and the grade. `slots.json` gives the DOM order eyebrow, title, meta, feature, stats at each width.

## AT-2: One title style

App: site
Then: The title of each hero has a computed font size of 40px and a weight of 300.
Files: `evidence/AT-2/steps.txt`, `evidence/AT-2/table.md`, `evidence/AT-2/styles.json`, `evidence/AT-2/week-375-dark.png`, `evidence/AT-2/manager-375-dark.png`, `evidence/AT-2/rankings-375-dark.png`, `evidence/AT-2/midseason-375-dark.png`, `evidence/AT-2/analyze-375-dark.png`, `evidence/AT-2/404-375-dark.png`
Observation: `table.md` gives an `h1` title of 40px and weight 300 on each of the six pages: "The Blue Tent by 1.43", "To Infinity and Bijan", "All You Need Is Love", "The Title Race", "Trade Analyzer", and "Page not found". The six shots show each hero at 375 px in the dark theme, and the analyzer shot is taken after the passphrase "localtest".

## AT-3: One eyebrow style

App: site
Then: Each eyebrow has the same computed font family, font size, text transform, letter spacing, and color.
Files: `evidence/AT-3/table.md`, `evidence/AT-2/styles.json`, `evidence/AT-2/steps.txt`
Observation: The five eyebrows of the week, manager, rankings, midseason, and analyze heroes all read jetbrainsMono, 12px, uppercase, 1.92px, and rgb(242, 165, 158). The 404 hero has no eyebrow element, so the table has no row of values for it.

## AT-4: A short meta line

App: site
Then: Each meta line has a computed font size of 16px and takes two lines or fewer.
Files: `evidence/AT-4/table.md`, `evidence/AT-2/styles.json`, `evidence/AT-2/steps.txt`, and the six shots of AT-2
Observation: Each of the six meta lines reads 16px. The line counts are week 2, manager 1, rankings 1, midseason 2, analyze 1, and 404 2. The AT-2 shots show the same wraps at 375 px.

## AT-5: The action sits at the bottom

App: site
Then: The share bar is the last part inside the hero, under the team rows.
Files: `evidence/AT-5/steps.txt`, `evidence/AT-5/parts.json`, `evidence/AT-5/375-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/768-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/1280-dark.png`
Observation: Each shot shows the red and gray bar of the share of the points as the last part of the hero, under the rows of The Blue Tent and London Cooking. `parts.json` gives `action` as the last slot, and it holds the `meter` "Share of the points".

## AT-6: One column on a phone

App: site
Then: The scene, the eyebrow, the title, the meta, the team rows, and the share bar stack in one column, in that order.
Files: `evidence/AT-5/375-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/parts.json`
Observation: At 375 px the shots show one column: the scene, "WEEK 08 // MATCHUP OF THE WEEK", "The Blue Tent by 1.43", the dates, the team rows under "CLOSEST FINISH", then the share bar. `parts.json` at 375 px gives the tops scene 106, eyebrow 330, title 360, meta 492, feature 569, and action 785.

## AT-7: Two rows on a tablet

App: site
Then: The eyebrow and the title sit at the top left, the meta sits at the top right, and the odds tiles sit at the bottom left.
Files: `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/slots.json`
Observation: At 768 and 1280 px the shots show "7-9 · 9TH OF 12" and "To Infinity and Bijan" at the top left, "bjpicard96" at the top right, and the three odds tiles at the bottom left. The scene, the grade, and the chips sit between the two rows.

## AT-8: The hairline above the stats

App: site
Then: A thin line shows directly above the odds tiles at 768 and 1280 px. No line shows there at 375 px.
Files: `evidence/AT-8/steps.txt`, `evidence/AT-8/rule.json`, `evidence/AT-8/375-light.png`, `evidence/AT-8/375-dark.png`, `evidence/AT-8/768-light.png`, `evidence/AT-8/768-dark.png`, `evidence/AT-8/1280-light.png`, `evidence/AT-8/1280-dark.png`
Observation: The 768 and 1280 px shots show a faint line between the week chips and the tiles, which fades at both ends. The 375 px shots show no line there. `rule.json` gives the rule `display: block`, 1 px high, 12 px above the tiles at 768 and 1280 px, and `display: none` at 375 px.

## AT-9: No empty gap

App: site
Then: The hero ends at the fairness block, with the same space under it as above the eyebrow. No empty area for stats or an action shows.
Files: `evidence/AT-9/steps.txt`, `evidence/AT-9/space.json`, `evidence/AT-9/tradeA.response.json`, `evidence/AT-9/375-light.png`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/768-light.png`, `evidence/AT-9/768-dark.png`, `evidence/AT-9/1280-light.png`, `evidence/AT-9/1280-dark.png`
Observation: Each shot shows the verdict hero "DECISION FOR BEHOLD THE LAMB", "Yes", ending at the FAIRNESS card "Lopsided: Bo Girds gives more.", with no stats row and no action row. `space.json` gives the slots eyebrow, title, meta, feature, and 29 px under the card at each width. At 768 and 1280 px the space above the eyebrow is also 29 px; at 375 px the scene band sits above the eyebrow, so the eyebrow is 253 px under the top edge. In the light theme the fairness card is white.

## AT-10: The Matchup title is words

App: site
Then: The title of the hero reads "The Blue Tent by 1.43".
Files: `evidence/AT-5/375-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/768-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/1280-dark.png`, `evidence/AT-5/parts.json`
Observation: Each shot shows the title "The Blue Tent by 1.43". `parts.json` gives the title text "The Blue Tent by 1.43" at each width and theme.

## AT-11: The blurb sits under the hero

App: site
Then: The blurb shows as a paragraph directly under the hero, outside its frame. The hero holds no blurb.
Files: `evidence/AT-11/steps.txt`, `evidence/AT-11/blurb.json`, `evidence/AT-11/375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/1280-dark.png`
Observation: Each shot shows the paragraph "The Blue Tent stole this one by 1.43 in an upset…" under the frame of the hero, on the page color. `blurb.json` gives `insideHero: false`, a gap of 20 px under the hero, and `heroHasBlurbText: false` at each width. The scene in `375-light.png` is caught before its settle, because the shot follows a scroll back to the top.

## AT-12: The 404 title

App: site
Then: The `h1` of the hero reads "Page not found", and a large "404" shows in the hero as art.
Files: `evidence/AT-12/steps.txt`, `evidence/AT-12/h1.json`, `evidence/AT-12/375-light.png`, `evidence/AT-12/375-dark.png`, `evidence/AT-12/768-light.png`, `evidence/AT-12/768-dark.png`, `evidence/AT-12/1280-light.png`, `evidence/AT-12/1280-dark.png`
Observation: `h1.json` gives one `h1`, "Page not found", at each width and theme. Each shot shows "Page not found" as the title and a large "404" lower in the hero, above "Go to Week 8" and "Go Home".

## AT-13: The heading level

App: site
Then: The title of the opener is an `h1`, the title of each act title is an `h2`, and both have the same computed font size and weight.
Files: `evidence/AT-13/steps.txt`, `evidence/AT-13/headings.json`
Observation: `headings.json` gives the opener "The Title Race" as `h1`, and "How We Got Here", "The Moves", and "What Comes Next" as `h2`. All four read 40px and weight 300.

## AT-14: Hero takes no free content

App: site
Then: The typecheck passes, which proves that `Hero` rejects `children`. A hero with only a `title` renders.
Files: `evidence/AT-14/look.test.tsx.txt`, `evidence/AT-14/typecheck-output.txt`, `evidence/AT-14/test-output.txt`
Observation: Line 48 of the test file holds `// @ts-expect-error Hero takes the six slots and no children.` over `<Hero label="Page not found">404</Hero>`. `pnpm --dir apps/site typecheck` ends with exit 0, and the site tsconfig includes `../../packages/*/site/**/*.tsx`. Vitest runs the file with 16 passed, which includes "takes no free content, and renders a hero with only a title … (AT-14)".

## AT-15: The Matchup scene

App: site
Then: The scene shows 12 lights from low to high, a dashed line labeled "99.60", and the lights of The Blue Tent and London Cooking in the accent color.
Files: `evidence/AT-15/steps.txt`, `evidence/AT-15/scene.json`, `evidence/AT-15/375-light.png`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/768-light.png`, `evidence/AT-15/768-dark.png`, `evidence/AT-15/1280-light.png`, `evidence/AT-15/1280-dark.png`
Observation: Each shot shows 12 lights that rise from left to right, a dashed line labeled "MEDIAN 99.60", and two red lights in the middle. `scene.json` reads the pixel at the lights of "London Cooking · 98.88" and "The Blue Tent · 100.31" as `#b8342a`, the value of `--color-accent`, and the other ten as `#ffffff`, from "Lil Fridge · 80.11" to "Teehee · 134.1". At 768 and 1280 px the label "The Blue Tent · 100.31" sits on the dashed line.

## AT-16: The settle time

App: site
Then: At 0.5 s after entry the lights are not yet in their chart places. At 2.2 s they are settled.
Files: `evidence/AT-16/steps.txt`, `evidence/AT-16/frames.json`, `evidence/AT-16/frame-500ms-375-dark.png`, `evidence/AT-16/frame-1000ms-375-dark.png`, `evidence/AT-16/frame-2200ms-375-dark.png`, `evidence/AT-16/frame-3700ms-375-dark.png`
Observation: The frame at 520 ms shows the lights scattered, with no line and no label. The frame at 1017 ms shows them near a rising row, with no line. The frame at 2218 ms shows the full chart with the line, "MEDIAN 99.60", and "The Blue Tent · 100.31". `frames.json` gives the state `rest` at 2206 ms, and the frame at 2218 ms equals the frame at 3736 ms.

## AT-17: The margin stays visible

App: site
Then: The margin mark "+1.43" shows in full, and no label covers any part of it.
Files: `evidence/AT-15/375-light.png`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/768-light.png`, `evidence/AT-15/768-dark.png`, `evidence/AT-15/1280-light.png`, `evidence/AT-15/1280-dark.png`
Observation: Each shot shows "+1.43" in full above the two red lights. At 375 px it sits above the label "The Blue Tent · 100.31", and at 768 and 1280 px it sits to the left of and above that label. No text touches it.

## AT-18: The manager scene

App: site
Then: The scene shows 8 lights from week 1 to week 8. The lights of weeks 3, 4, and 8 are bright, the other five are dim, and a dashed line marks the median of each week.
Files: `evidence/AT-18/steps.txt`, `evidence/AT-18/scene.json`, `evidence/AT-18/375-light.png`, `evidence/AT-18/375-dark.png`, `evidence/AT-18/768-light.png`, `evidence/AT-18/768-dark.png`, `evidence/AT-18/1280-light.png`, `evidence/AT-18/1280-dark.png`
Observation: Each shot shows 8 lights joined by a line, white at the 3rd, 4th, and 8th places and gray at the other five, and a dashed curve labeled "WEEK MEDIAN". `scene.json` gives the label at rest "Week 8 · 118.89 · W", and the shots show it next to the last light.

## AT-19: The rankings scene

App: site
Then: The scene shows 12 lights in the order of the power rank, each at the height of its playoff odds. The light of the rank-1 team is in the accent color and shows its label.
Files: `evidence/AT-19/steps.txt`, `evidence/AT-19/scene.json`, `evidence/AT-19/375-light.png`, `evidence/AT-19/375-dark.png`, `evidence/AT-19/768-light.png`, `evidence/AT-19/768-dark.png`, `evidence/AT-19/1280-light.png`, `evidence/AT-19/1280-dark.png`
Observation: The rank-1 team of week 8 is All You Need Is Love, with playoff odds of 81%. Each shot shows 12 lights, the first one red with the label "All You Need Is Love · 81%", and a shape that matches the odds by rank in `clients/cpc/published/2026/rankings.json`: 81, 61, 77, 42, 75, 86, 76, 83, 7, 8, 4, 1. The scene sits in the hero "Rank 1".

## AT-20: The analyzer drift

App: site
Then: The lights of the scene move the whole time and do not settle into a chart.
Files: `evidence/AT-20/steps.txt`, `evidence/AT-20/frames.json`, `evidence/AT-20/frame-2s-375-dark.png`, `evidence/AT-20/frame-6s-375-dark.png`
Observation: The frames at 2025 ms and 6013 ms after the drift starts show scattered lights in different places, with no line and no label. `frames.json` gives the states `idle` then `drift` only, `framesDiffer: true`, and the state `drift` at 6 s, in the hero "Trade Analyzer".

## AT-21: The analyzer settle

App: site
Then: When the verdict arrives, the lights settle into two groups, one per side, and the bigger group sits on the side of behold the lamb.
Files: `evidence/AT-21/steps.txt`, `evidence/AT-21/frames.json`, `evidence/AT-21/tradeA.response.json`, `evidence/AT-21/before-grade-375-dark.png`, `evidence/AT-21/after-verdict-2.5s-375-dark.png`, `evidence/AT-21/before-grade-1280-dark.png`, `evidence/AT-21/after-verdict-2.5s-1280-dark.png`
Observation: The frames before the grade show scattered drift lights. The frames 2.5 s after the verdict show 5 red lights on the left, a cross of four around one, and 2 lights on the right, one white and one gray. One gray line joins all 7 lights, so the line runs from the left group to the right group. The verdict hero reads "DECISION FOR BEHOLD THE LAMB", "Yes", "Lopsided: Bo Girds gives more."; `tradeA.response.json` lists roster 10 first, with 4 factors "for", and roster 6 with 1 factor "for" (upside).

## AT-22: The midseason scene

App: site
Then: The scene shows 12 lights at the season total points in the order of the standings, and the light of the leader is in the accent color.
Files: `evidence/AT-22/steps.txt`, `evidence/AT-22/scene.json`, `evidence/AT-22/375-light.png`, `evidence/AT-22/375-dark.png`, `evidence/AT-22/768-light.png`, `evidence/AT-22/768-dark.png`, `evidence/AT-22/1280-light.png`, `evidence/AT-22/1280-dark.png`
Observation: The leader is All You Need Is Love. Each shot shows 12 lights joined by a line, the first one red with the label "All You Need Is Love · 850.17". The scene sits in the opener hero "The Title Race".

## AT-23: The 404 drift

App: site
Then: The frames at 2 s and at 6 s differ, and the lights never form a chart.
Files: `evidence/AT-23/steps.txt`, `evidence/AT-23/frames.json`, `evidence/AT-23/frame-2s-375-dark.png`, `evidence/AT-23/frame-6s-375-dark.png`
Observation: The two frames show scattered lights in different places, with no line and no label. `frames.json` gives `framesDiffer: true`, the states `idle` then `drift` only, and an empty label at 6 s, in the hero "Page not found".

## AT-24: The label at rest

App: site
Then: The label "The Blue Tent · 100.31" shows next to its light.
Files: `evidence/AT-15/375-light.png`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/768-light.png`, `evidence/AT-15/768-dark.png`, `evidence/AT-15/1280-light.png`, `evidence/AT-15/1280-dark.png`, `evidence/AT-15/scene.json`
Observation: Each shot shows "The Blue Tent · 100.31" next to the right red light, with no tap. `scene.json` gives `data-scene-label` "The Blue Tent · 100.31" at each width and theme.

## AT-25: A tap selects the nearest light

App: site
Then: The label "Lil Fridge · 80.11" shows, and the scene does not play again.
Files: `evidence/AT-25/steps.txt`, `evidence/AT-25/tap.json`, `evidence/AT-25/before-375-dark.png`, `evidence/AT-25/after-375-dark.png`
Observation: The tap is at (19, 194) in the canvas, 10.4 px from the light of Lil Fridge at (16, 184) and 32.8 px from the next light. The after shot shows a ring on the lowest light and the label "Lil Fridge · 80.11", with the other lights in their chart places. `tap.json` gives the states `idle`, `settle`, `rest` both before and after the tap, so no second settle ran.

## AT-26: A slide scrubs the lights

App: site
Then: The label "London Cooking · 98.88" shows.
Files: `evidence/AT-26/steps.txt`, `evidence/AT-26/drag.json`, `evidence/AT-26/end-375-dark.png`
Observation: The drag runs in 12 steps from (57, 231.6) to (175.6, 231.6) on the page, with the button down. The label moves through NFC Least, behold the lamb, Bo Girds, and Unsolicited Dak Picks to "London Cooking · 98.88". The end shot shows a ring on the left red light and the label "London Cooking · 98.88".

## AT-27: A vertical swipe scrolls

App: site
Then: The page scrolls down.
Files: `evidence/AT-27/steps.txt`, `evidence/AT-27/scroll.json`, `evidence/AT-27/before-375-dark.png`, `evidence/AT-27/after-375-dark.png`
Observation: The touch swipe starts at (188, 286) inside the scene and moves 300 px up. `scroll.json` gives `scrollY` 0 before and 445 after. The before shot shows the scene at the top of the hero, and the after shot shows the team rows and the blurb.

## AT-28: The hint shows once

App: site
Then: "TAP OR SLIDE" shows before the tap, is gone after the tap, and does not show after the reload.
Files: `evidence/AT-28/steps.txt`, `evidence/AT-28/hint.json`, `evidence/AT-28/before-tap-375-dark.png`, `evidence/AT-28/after-tap-375-dark.png`, `evidence/AT-28/after-reload-375-dark.png`
Observation: The before shot shows "TAP OR SLIDE" at the top left of the scene. The after-tap shot and the after-reload shot show no "TAP OR SLIDE". `hint.json` gives no stored flag at the start, `data-scene-hint` `shown`, then `gone`, then `gone` after the reload, with the flag "1".

## AT-29: A label at an edge

App: site
Then: The label "Teehee · 134.1" shows in full, inside the scene.
Files: `evidence/AT-29/steps.txt`, `evidence/AT-29/tap.json`, `evidence/AT-29/375-dark.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/1280-dark.png`
Observation: Each shot shows the label "Teehee · 134.1" to the left of the ring on the top-right light, inside the scene. The last "1" sits next to the ring and is not cut. `tap.json` gives the label "Teehee · 134.1" at each width.

## AT-30: Replay on re-entry

App: site
Then: The lights move again and settle again.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/frames.json`, `evidence/AT-30/frame-before-leave-375-dark.png`, `evidence/AT-30/frame-500ms-after-back-375-dark.png`, `evidence/AT-30/frame-2500ms-after-back-375-dark.png`
Observation: The hero leaves the view, with its bottom at −5249 px. The frame 528 ms after the return shows scattered lights with no line. The frame 2523 ms after the return shows the full chart and equals the frame before the hero left. `frames.json` gives the states `idle`, `settle`, `rest`, `settle`, `rest`.

## AT-31: Reduced motion

App: site
Then: The settled chart shows at once, with the frame at 0.1 s the same as the frame at 2.5 s.
Files: `evidence/AT-31/steps.txt`, `evidence/AT-31/frames.json`, `evidence/AT-31/frame-0.1s-375-light.png`, `evidence/AT-31/frame-2.5s-375-light.png`, `evidence/AT-31/frame-0.1s-375-dark.png`, `evidence/AT-31/frame-2.5s-375-dark.png`
Observation: All four frames show the full chart with "MEDIAN 99.60", "+1.43", and "The Blue Tent · 100.31". `frames.json` gives the states `idle` then `rest` with no `settle`, frames at 110 ms and 2502 ms in light and at 103 ms and 2510 ms in dark, and `framesEqual: true` in both themes.

## AT-32: The loop stops at rest

App: site
Then: The page requests no animation frame in those 3 s.
Files: `evidence/AT-32/steps.txt`, `evidence/AT-32/raf.json`
Observation: `raf.json` gives 141 calls of `requestAnimationFrame` before and 141 after a wait of 3007 ms, which starts 200 ms after the state turns `rest`. That is 0 calls in the window.

## AT-33: The hero stays dark in the light theme

App: site
Then: The page is light, and the hero and its scene stay dark with the same lights as in the dark theme.
Files: `evidence/AT-33/steps.txt`, `evidence/AT-33/colors.json`, `evidence/AT-33/375-light.png`, `evidence/AT-33/768-light.png`, `evidence/AT-33/1280-light.png`
Observation: The shots show a light page and header around a dark hero with the full chart. `colors.json` gives the hero rgb(20, 20, 20) in both themes, a light body (rgb(244, 244, 244) at 375 px, rgb(255, 255, 255) at 768 and 1280 px), and `canvasPixelsLightEqualDark: true` at each width.

## AT-34: NorCal colors

App: site
Then: The two flared lights of the Matchup have the color `#c2410c`.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/colors.json`, `evidence/AT-34/375-light.png`, `evidence/AT-34/375-dark.png`, `evidence/AT-34/768-light.png`, `evidence/AT-34/768-dark.png`, `evidence/AT-34/1280-light.png`, `evidence/AT-34/1280-dark.png`
Observation: The norcal week is `/2026/week-08/`. `colors.json` reads the pixel at "The Mean Machine · 121.76" and "kaiedmonds · 132.38" as `#c2410c` at each width and theme, with `--color-accent` `#c2410c`. Each shot shows two orange lights, the label "kaiedmonds · 132.38", and "+10.62".

## AT-35: Only the first hero moves

App: site
Then: The home page has exactly one scene. In the report, the opener has a scene and no act title has one.
Files: `evidence/AT-35/steps.txt`, `evidence/AT-35/counts.json`, `evidence/AT-35/act-1-375-dark.png`, `evidence/AT-35/act-2-375-dark.png`, `evidence/AT-35/act-3-375-dark.png`
Observation: `counts.json` gives 1 canvas on `/`, in the hero "2026 Midseason Report". On `/midseason/2026/` it gives 1 canvas, in "The Title Race", and 0 in "Act I: How We Got Here", "Act II: The Moves", and "Act III: What Comes Next". The three shots show each act title with the grid and brackets and no lights.

## AT-36: A tap on the content still works

App: site
Then: The grade popover opens.
Files: `evidence/AT-36/steps.txt`, `evidence/AT-36/tap.json`, `evidence/AT-36/before-375-dark.png`, `evidence/AT-36/after-375-dark.png`, `evidence/AT-36/before-1280-dark.png`, `evidence/AT-36/after-1280-dark.png`
Observation: The tap is on the button "Grade D, how the grade reads". The after shots show the popover "HOW THE GRADE READS" with "Projection Ahead · 11th of 12" and three more rows, at both widths. `tap.json` gives `dialogVisible: true` at 375 and 1280 px.

## AT-37: The readability floor passes

App: site
Then: Both runs pass.
Files: `evidence/AT-37/check-floor-cpc.txt`, `evidence/AT-37/check-floor-norcal.txt`
Observation: The output is the `check:floor` part of the `make check` log at `c1a7c91c`. For cpc it ends "129 passed (56.7s)". For norcal it ends "3 failed, 1 skipped, 123 passed (55.9s)" and "The site check:floor of the client norcal failed.": the three failures are `manager-scene.spec.ts:80` "draws one light per played week … (AT-18)" at 375, 768, and 1280 px, each with "TypeError: Cannot read properties of undefined (reading 'points')" at `guide.points.length`.

## AT-38: The math of the scene

App: site
Then: The tests pass for the place of each light, the nearest light to a point, the side of a label near an edge, and the place of the margin mark clear of every label.
Files: `evidence/AT-38/scene-math.test.ts.txt`, `evidence/AT-38/matchup-scene.test.ts.txt`, `evidence/AT-38/output.txt`
Observation: Vitest runs the two files with 36 passed and exit 0. The passed tests include `placeLights`, `nearestLight` "selects the closest light for a tap in empty space", `placeLabel` "flips a label near the right edge to the inner side", `placeMarginMark` "moves the mark off a label", and the week 8 tests of `matchup-scene.test.ts`, which read the fixture `week8`.

## AT-39: No scan line

App: site
Then: No line sweeps across the hero on entry, and the stylesheet holds no scan-line rule.
Files: `evidence/AT-39/steps.txt`, `evidence/AT-39/frames.json`, `evidence/AT-39/stylesheet-search.txt`, `evidence/AT-39/week-0.3s-375-dark.png`, `evidence/AT-39/week-0.8s-375-dark.png`, `evidence/AT-39/manager-0.3s-375-dark.png`, `evidence/AT-39/manager-0.8s-375-dark.png`
Observation: The four hero shots, taken from 311 ms and 809 ms after navigation, show the grid, the brackets, and the scene lights, and no line across the hero. `frames.json` gives no CSS animation in either hero at 0.8 s. In `globals.css` the one match of "scan" is a comment, "Tailwind scans the app only", and `git grep` finds no "scan-line", "scanline", or "@keyframes scan".

## AT-40: No 3D engine

App: site
Then: No package of three.js or another 3D engine is added, and the scene asks for a `2d` context only.
Files: `evidence/AT-40/output.txt`
Observation: `git diff main -- '*package.json' pnpm-lock.yaml` prints nothing, and the branch changes 90 files in all. A grep of the package files and the lock file for three, babylon, pixi, regl, ogl, and playcanvas finds no match. The one `getContext(` call outside tests is `packages/design/site/parts/hero-scene.tsx:21: const ctx = canvas.current.getContext("2d");`.

## AT-41: No "Read more"

App: site
Then: The full blurb shows, with no "Read more" control and no fold.
Files: `evidence/AT-11/375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/blurb.json`
Observation: Both shots show the whole blurb, from "The Blue Tent stole this one by 1.43" to "while the losers slid to 4th.", with no control under it. `blurb.json` gives `readMore: false` for the whole page, no `details` parent, `-webkit-line-clamp: none`, and a `scrollHeight` equal to the `clientHeight`.

## AT-42: No pipeline change

App: site
Then: No file under `apps/pipeline/` and no published file under `clients/` changes.
Files: `evidence/AT-42/output.txt`
Observation: `git diff --stat main -- apps/pipeline clients` prints nothing, with `main` at `df2c08c0` and HEAD at `c1a7c91c`.
