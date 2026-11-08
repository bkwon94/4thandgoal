# Card polish: evidence

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests: `.scratch/card-polish/ACCEPTANCE.md`.
Built from: `a44daee5`, on 2026-11-08. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 4 min for 9 site tests.

The runner output of the round is `evidence/round.txt`. The background `make check` of the spec worktree ran from 08:25 and ended green; AT-27 and AT-28 use its floor runs. `evidence/crops.txt` says how the `crop-*.png` cuts were made. The local ref `main` is behind `origin/main`, so each diff uses `origin/main` 25f98a02.

## AT-1: Game card opens in place

App: site
Then: The card grows in place under its own head, the cards below move down, the chevron turns 180 degrees, and the panel text comes into focus after the card grows.
Files: `evidence/AT-1/record.mjs`, `evidence/AT-1/steps.json`, `evidence/AT-1/closed-1280-dark.png`, `evidence/AT-1/closed-1280-light.png`, `evidence/AT-1/closed-375-dark.png`, `evidence/AT-1/closed-375-light.png`, `evidence/AT-1/closed-768-dark.png`, `evidence/AT-1/closed-768-light.png`, `evidence/AT-1/crop-closed-1280-dark.png`, `evidence/AT-1/crop-closed-1280-light.png`, `evidence/AT-1/crop-closed-375-dark.png`, `evidence/AT-1/crop-closed-375-light.png`, `evidence/AT-1/crop-closed-768-dark.png`, `evidence/AT-1/crop-closed-768-light.png`, `evidence/AT-1/crop-open-1280-dark.png`, `evidence/AT-1/crop-open-1280-light.png`, `evidence/AT-1/crop-open-375-dark.png`, `evidence/AT-1/crop-open-375-light.png`, `evidence/AT-1/crop-open-768-dark.png`, `evidence/AT-1/crop-open-768-light.png`, `evidence/AT-1/open-1280-dark.png`, `evidence/AT-1/open-1280-light.png`, `evidence/AT-1/open-375-dark.png`, `evidence/AT-1/open-375-light.png`, `evidence/AT-1/open-375-light.webm`, `evidence/AT-1/open-768-dark.png`, `evidence/AT-1/open-768-light.png`
Observation: The closed shots show the card of All You Need Is Love vs Unsolicited Dak Picks with a down chevron. The open shots show the same card grown in place under its own head, with the chips, the recap, and the Manager page pill, and the chevron turned up. The cards below sit lower: at 375 px the page grows from 6938 px to 7447 px, and at 1280 px from 5389 px to 5962 px. `open-375-light.webm` (record.mjs, 3.4 s, motion on) shows the card grow, with the chevron at a quarter turn and the panel still faint in a frame mid-open, then the text sharp.

## AT-2: A closed game card keeps the scoreboard

App: site
Then: The card shows both avatars, both team names, 116.83 and 92.55, and the share bar.
Files: `evidence/AT-1/closed-1280-dark.png`, `evidence/AT-1/closed-1280-light.png`, `evidence/AT-1/closed-375-dark.png`, `evidence/AT-1/closed-375-light.png`, `evidence/AT-1/closed-768-dark.png`, `evidence/AT-1/closed-768-light.png`, `evidence/AT-1/crop-closed-1280-dark.png`, `evidence/AT-1/crop-closed-1280-light.png`, `evidence/AT-1/crop-closed-375-dark.png`, `evidence/AT-1/crop-closed-375-light.png`, `evidence/AT-1/crop-closed-768-dark.png`, `evidence/AT-1/crop-closed-768-light.png`
Observation: The closed shots of AT-1 show the card with both avatars, All You Need Is Love 116.83 in bold, the red share bar, and Unsolicited Dak Picks 92.55, at each width and theme.

## AT-3: An open game card shows three chips

App: site
Then: The panel shows three chips: the avatar of All You Need Is Love with Best J. Burrow 42.48, the avatar of Unsolicited Dak Picks with Best J. Jacobs 20.2, and Records 11-5 · 6-10. No Margin chip and no Vs proj chip shows.
Files: `evidence/AT-1/crop-open-1280-dark.png`, `evidence/AT-1/crop-open-1280-light.png`, `evidence/AT-1/crop-open-375-dark.png`, `evidence/AT-1/crop-open-375-light.png`, `evidence/AT-1/crop-open-768-dark.png`, `evidence/AT-1/crop-open-768-light.png`, `evidence/AT-1/open-1280-dark.png`, `evidence/AT-1/open-1280-light.png`, `evidence/AT-1/open-375-dark.png`, `evidence/AT-1/open-375-light.png`, `evidence/AT-1/open-768-dark.png`, `evidence/AT-1/open-768-light.png`
Observation: The open shots of AT-1 show three chips: the avatar of All You Need Is Love with Best J. Burrow 42.48, the avatar of Unsolicited Dak Picks with Best J. Jacobs 20.2, and Records 11-5 · 6-10. No Margin chip and no Vs proj chip shows.

## AT-4: An open game card shows the recap and the manager link

App: site
Then: The recap text shows under the chips, and a Manager page pill links to the manager page of All You Need Is Love. The pill label sits on a solid fill.
Files: `evidence/AT-1/crop-open-1280-dark.png`, `evidence/AT-1/crop-open-1280-light.png`, `evidence/AT-1/crop-open-375-dark.png`, `evidence/AT-1/crop-open-375-light.png`, `evidence/AT-1/crop-open-768-dark.png`, `evidence/AT-1/crop-open-768-light.png`, `evidence/AT-1/open-1280-dark.png`, `evidence/AT-1/open-1280-light.png`, `evidence/AT-1/open-375-dark.png`, `evidence/AT-1/open-375-light.png`, `evidence/AT-1/open-768-dark.png`, `evidence/AT-1/open-768-light.png`, `evidence/AT-4/link.txt`
Observation: The open shots of AT-1 show the recap under a rule below the chips, then a Manager page pill: ink fill with page text in light, white fill with dark text in dark. `link.txt` shows the pill href /2026/managers/2/, roster 2, All You Need Is Love, with the hidden label "of All You Need Is Love".

## AT-5: A ladder card shows the rank large

App: site
Then: The card shows 05 large in a plain raised panel, then The Blue Tent, 9-7, ▲3, the odds bar, and Playoff 75%.
Files: `evidence/AT-6/steps.json`, `evidence/AT-6/closed-1280-dark.png`, `evidence/AT-6/closed-1280-light.png`, `evidence/AT-6/closed-375-dark.png`, `evidence/AT-6/closed-375-light.png`, `evidence/AT-6/closed-768-dark.png`, `evidence/AT-6/closed-768-light.png`, `evidence/AT-6/crop-closed-1280-dark.png`, `evidence/AT-6/crop-closed-1280-light.png`, `evidence/AT-6/crop-closed-375-dark.png`, `evidence/AT-6/crop-closed-375-light.png`, `evidence/AT-6/crop-closed-768-dark.png`, `evidence/AT-6/crop-closed-768-light.png`
Observation: The closed shots show the card of The Blue Tent with 05 in a large mono figure in a plain raised panel, then the avatar, The Blue Tent, 9-7 · ▲3, the Playoff 75% pill, and the red odds bar under it.

## AT-6: An open ladder card shows its chips and blurb

App: site
Then: The panel shows the chips Stand 6, Form 6, Sched 8, Pts 7, Move ▲3, Bye 22%, and Seed 5, then the blurb of The Blue Tent.
Files: `evidence/AT-6/steps.json`, `evidence/AT-6/crop-open-1280-dark.png`, `evidence/AT-6/crop-open-1280-light.png`, `evidence/AT-6/crop-open-375-dark.png`, `evidence/AT-6/crop-open-375-light.png`, `evidence/AT-6/crop-open-768-dark.png`, `evidence/AT-6/crop-open-768-light.png`, `evidence/AT-6/open-1280-dark.png`, `evidence/AT-6/open-1280-light.png`, `evidence/AT-6/open-375-dark.png`, `evidence/AT-6/open-375-light.png`, `evidence/AT-6/open-768-dark.png`, `evidence/AT-6/open-768-light.png`
Observation: The open shots show the panel with an overview line Rank 5 · 9-7 · ▲3, then the chips Stand 6, Form 6, Sched 8, Pts 7, Move ▲3, Bye 22%, and Seed 5, then the blurb "The Blue Tent climbs 3 places on a 1-point win..." and a Manager page pill.

## AT-7: Retired. The award and trade cards open the same way

App: site
Then: Each card opens with the same drawer, blur-in, and chevron as the game card.
Files: none.
Observation: The title says Retired (revision of 2026-11-08), so no evidence is recorded.

## AT-8: The text of a closed card stays findable

App: site
Then: The browser finds the word and the card opens. The closed panel has `hidden="until-found"`, and its toggle has `aria-expanded="false"` and `aria-controls` set to the panel id.
Files: `evidence/AT-8/dom.txt`, `evidence/AT-8/find-output.txt`, `evidence/AT-8/steps.json`, `evidence/AT-8/find-1280-dark.png`, `evidence/AT-8/find-1280-light.png`
Observation: The route opens a text fragment of the recap words "shrugged off Jeremiyah Love", the same search as find-in-page. The shots show the card of game 4 open with that recap in view; the browser highlight of the match does not show in a screenshot. `find-output.txt` holds the open-card project run: "find: \"and lost the median game too\" opened recap-4". `dom.txt` shows the closed head toggle with aria-expanded="false" and aria-controls="recap-4", and the panel div id="recap-4" hidden="until-found", read after hydration.

## AT-9: Reduced motion opens a card at once

App: site
Then: Each part reaches its end state at once, with no height animation, no blur, no spring, and no fill animation.
Files: `evidence/AT-9/computed.txt`, `evidence/AT-9/steps.txt`, `evidence/AT-9/vitest-output.txt`, `evidence/AT-9/game-card-375-light.png`, `evidence/AT-9/grade-dial-375-light.png`, `evidence/AT-9/index-row-375-light.png`, `evidence/AT-9/ladder-card-375-light.png`
Observation: `vitest-output.txt` holds 24 tests of src/reduced-motion.test.tsx and open-card.test.tsx, among them the game card, the ladder card, the Index list row, and the Grade dial with reduced motion, and the run exits 0. The four shots, taken about 50 ms after each tap with reduced motion on, show each part at its end state: the game card and the ladder card open with sharp text, the row open with its arcs, and the dial with its blades lit. `computed.txt` shows transition-duration 0s, filter blur(0px), opacity 1, chevron rotate 180deg, no row animation, and no blade animation.

## AT-10: The blur stays smooth on a slow phone

App: site
Then: The median frame rate of the open is 50 fps or more. If it is lower, the blur is gone from the Open card and the evidence says why (ADR 0028).
Files: `evidence/AT-10/open-card.spec.ts`, `evidence/AT-10/output.txt`
Observation: `output.txt` shows "frame rate: median 60 fps over 47 frames, throttle 4x, viewport 375px, worst gap 33.3 ms" for the open of game 4, with motion on. The throttle is Emulation.setCPUThrottlingRate rate 4, set in `open-card.spec.ts`.

## AT-11: Season So Far shows the Grade dial

App: site
Then: The section shows the letter A, the grade read, and four arcs in a 2x2 grid: 4th, 6th, 7th, and 7th, with 9, 7, 6, and 6 of 12 blades lit.
Files: `evidence/AT-11/steps.json`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/crop-season-1280-dark.png`, `evidence/AT-11/crop-season-1280-light.png`, `evidence/AT-11/crop-season-375-dark.png`, `evidence/AT-11/crop-season-375-light.png`, `evidence/AT-11/crop-season-768-dark.png`, `evidence/AT-11/crop-season-768-light.png`
Observation: The shots and the season cuts show Season So Far with the points chart and the season numbers, then Roster Grade with the letter A and "Strong at QB and TE. Soft at RB.", then four arcs in a 2x2 grid: 4th, 6th, 7th, and 7th of 12. In the cuts the lit blades count 9, 7, 6, and 6 of 12. `evidence/AT-9/computed.txt` reads 28 lit blades of 48.

## AT-12: Each arc names its part, rank, and weight as text

App: site
Then: Each arc has its part name, its rank such as 4th, and N% of the grade as text: Projection 45%, Production 30%, Trade value 10%, Depth 15%.
Files: `evidence/AT-12/accessible-names.txt`, `evidence/AT-12/vitest-output.txt`, `evidence/AT-11/crop-season-1280-dark.png`, `evidence/AT-11/crop-season-1280-light.png`, `evidence/AT-11/crop-season-375-dark.png`, `evidence/AT-11/crop-season-375-light.png`, `evidence/AT-11/crop-season-768-dark.png`, `evidence/AT-11/crop-season-768-light.png`
Observation: `accessible-names.txt` holds the four arc names from the built page: "Projection Ahead: 4th of 12, 45% of the grade", "Season Production: 6th of 12, 30% of the grade", "Trade Value: 7th of 12, 10% of the grade", and "Depth And Holes: 7th of 12, 15% of the grade". The part names on the page are Projection Ahead, Season Production, Trade Value, and Depth And Holes, and each name, rank, and weight also shows as text under its arc in the cuts. The grade-dial test run exits 0.

## AT-13: The weights match the pipeline

App: site
Then: The weights test fails. With the constant back at 15, it passes.
Files: `evidence/AT-13/output-depth-15.txt`, `evidence/AT-13/output-depth-16.txt`
Observation: `output-depth-16.txt` shows the diff of depth 15 to 16, then the run of src/grade-weights.test.ts: "Tests  1 failed (1)", with the expected "depth": 15 and the received "depth": 16, exit 1. `output-depth-15.txt` shows the file equal to HEAD again and "Tests  1 passed (1)", exit 0.

## AT-14: The top score trend runs from week 1

App: site
Then: The tile shows 134.1 and eight bars: 156.92, 156.52, 140.6, 145.63, 158.96, 126.79, 148.13, and 134.1, with the week 8 bar lit.
Files: `evidence/AT-15/steps.json`, `evidence/AT-15/cpc-1280-dark.png`, `evidence/AT-15/cpc-1280-light.png`, `evidence/AT-15/cpc-375-dark.png`, `evidence/AT-15/cpc-375-light.png`, `evidence/AT-15/cpc-768-dark.png`, `evidence/AT-15/cpc-768-light.png`, `evidence/AT-15/crop-cpc-numbers-1280-dark.png`, `evidence/AT-15/crop-cpc-numbers-1280-light.png`, `evidence/AT-15/crop-cpc-numbers-375-dark.png`, `evidence/AT-15/crop-cpc-numbers-375-light.png`, `evidence/AT-15/crop-cpc-numbers-768-dark.png`, `evidence/AT-15/crop-cpc-numbers-768-light.png`
Observation: The cpc shots and cuts of AT-15 show the Top Score tile with 134.1, Teehee, and eight bars. The bar heights follow the series 156.92, 156.52, 140.6, 145.63, 158.96, 126.79, 148.13, and 134.1 of clients/cpc/published/2026/managers.json: the fifth is the tallest, the sixth the lowest, and the eighth bar is red, the lit bar.

## AT-15: The median trend ends at the number of the tile

App: site
Then: The CPC stepped area has eight points and ends at 99.6, the number on the tile. The NorCal trend ends at the number on the NorCal tile.
Files: `evidence/AT-15/steps.json`, `evidence/AT-15/cpc-1280-dark.png`, `evidence/AT-15/cpc-1280-light.png`, `evidence/AT-15/cpc-375-dark.png`, `evidence/AT-15/cpc-375-light.png`, `evidence/AT-15/cpc-768-dark.png`, `evidence/AT-15/cpc-768-light.png`, `evidence/AT-15/crop-cpc-numbers-1280-dark.png`, `evidence/AT-15/crop-cpc-numbers-1280-light.png`, `evidence/AT-15/crop-cpc-numbers-375-dark.png`, `evidence/AT-15/crop-cpc-numbers-375-light.png`, `evidence/AT-15/crop-cpc-numbers-768-dark.png`, `evidence/AT-15/crop-cpc-numbers-768-light.png`, `evidence/AT-15/crop-norcal-numbers-1280-dark.png`, `evidence/AT-15/crop-norcal-numbers-1280-light.png`, `evidence/AT-15/norcal-1280-dark.png`, `evidence/AT-15/norcal-1280-light.png`, `evidence/AT-15/norcal-375-dark.png`, `evidence/AT-15/norcal-375-light.png`, `evidence/AT-15/norcal-768-dark.png`, `evidence/AT-15/norcal-768-light.png`
Observation: The cpc cuts show the Median tile with 99.6 and "6 above, 6 below" over a stepped area of eight steps that ends in a red step at the low right. Its screen reader name in AT-18 reads "Down from 103.87 in week 7.". The NorCal cuts and shots show the Median tile with 117.55 and a stepped area that ends in an orange step.

## AT-16: An older week page stops its trend at that week

App: site
Then: The tile shows six bars, from 156.92 to 126.79, with the week 6 bar lit and no bar for week 7 or 8.
Files: `evidence/AT-16/steps.json`, `evidence/AT-16/1280-dark.png`, `evidence/AT-16/1280-light.png`, `evidence/AT-16/375-dark.png`, `evidence/AT-16/375-light.png`, `evidence/AT-16/768-dark.png`, `evidence/AT-16/768-light.png`, `evidence/AT-16/crop-numbers-1280-dark.png`, `evidence/AT-16/crop-numbers-1280-light.png`, `evidence/AT-16/crop-numbers-375-dark.png`, `evidence/AT-16/crop-numbers-375-light.png`, `evidence/AT-16/crop-numbers-768-dark.png`, `evidence/AT-16/crop-numbers-768-light.png`
Observation: The shots and cuts of week 6 show the Top Score tile with 126.79, Lil Fridge, and six bars, the sixth red and the lowest, with no seventh or eighth bar. The Median tile shows 106.83 with a stepped area that ends at the right edge.

## AT-17: The Moves tiles show the moves of each week

App: site
Then: The Adds tile shows bars 5, 1, 2, 4, 1, 1, 6, and 3 for weeks 1 to 8. The Trades tile shows dots at week 1 and week 4 only.
Files: `evidence/AT-11/steps.json`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/crop-moves-1280-dark.png`, `evidence/AT-11/crop-moves-1280-light.png`, `evidence/AT-11/crop-moves-375-dark.png`, `evidence/AT-11/crop-moves-375-light.png`, `evidence/AT-11/crop-moves-768-dark.png`, `evidence/AT-11/crop-moves-768-light.png`
Observation: The shots and the moves cuts show Moves with three tiles: Adds 23 with eight bars, the seventh the tallest and the eighth red; Drops 22 with eight bars; and Trades 2 with two dots on a line, at the first and the fourth of eight places. The bar heights follow 5, 1, 2, 4, 1, 1, 6, and 3. The screen reader names in AT-18 read "The most adds in one week: 6, in week 7." and "Trades in week 1 and week 4.".

## AT-18: A Trend tile has a text of its trend

App: site
Then: Each of the five Trend tiles reads its number and one sentence of its trend.
Files: `evidence/AT-18/accessible-text.txt`, `evidence/AT-18/vitest-output.txt`
Observation: `accessible-text.txt` holds the five Trend tiles from the built pages. Each holds its label and number, then one chart name of one sentence: Top Score 134.1, "Down from 148.13 in week 7."; Median 99.6, "Down from 103.87 in week 7."; Adds 23, "The most adds in one week: 6, in week 7."; Drops 22, "The most drops in one week: 6, in week 7."; Trades 2, "Trades in week 1 and week 4.". The week-numbers and moves test runs exit 0.

## AT-19: The Ready halo brightens step by step

App: site
Then: The halo glows at the level of 2 of 6 checks, brighter than with no team and below full.
Files: none.
Observation: STUCK: the analyzer form needs the API for its teams. Port 8080 holds the API of hero-slots (uvicorn from .claude/worktrees/hero-slots-api), and it does not serve the evidence origin. A CORS preflight from Origin http://127.0.0.1:4173 to http://localhost:8080 answered 400 "Disallowed CORS origin". The guide says to start nothing on 8080, so no shot of the halo exists. The full floor checks the empty /analyze/ page at 390 px and 1280 px (see AT-28), and src/reduced-motion.test.tsx holds "shows the Ready halo at its level at once" (see AT-9).

## AT-20: The Ready halo is full only when the trade is ready

App: site
Then: The halo reaches full when the Grade button can grade, and it dims when the player goes.
Files: none.
Observation: STUCK: the analyzer form needs the API for its teams. Port 8080 holds the API of hero-slots (uvicorn from .claude/worktrees/hero-slots-api), and it does not serve the evidence origin. A CORS preflight from Origin http://127.0.0.1:4173 to http://localhost:8080 answered 400 "Disallowed CORS origin". The guide says to start nothing on 8080, so no shot of the halo exists. The full floor checks the empty /analyze/ page at 390 px and 1280 px (see AT-28), and src/reduced-motion.test.tsx holds "shows the Ready halo at its level at once" (see AT-9).

## AT-21: The Ready halo works in the light theme and with reduced motion

App: site
Then: The halo reads against the light page. With reduced motion it shows the level with no pulse or orbit.
Files: none.
Observation: STUCK: the analyzer form needs the API for its teams. Port 8080 holds the API of hero-slots (uvicorn from .claude/worktrees/hero-slots-api), and it does not serve the evidence origin. A CORS preflight from Origin http://127.0.0.1:4173 to http://localhost:8080 answered 400 "Disallowed CORS origin". The guide says to start nothing on 8080, so no shot of the halo exists. The full floor checks the empty /analyze/ page at 390 px and 1280 px (see AT-28), and src/reduced-motion.test.tsx holds "shows the Ready halo at its level at once" (see AT-9).

## AT-22: The Index list shows every team on one phone screen

App: site
Then: All 12 rows show on one screen with the chips closed. Each row shows the place, a small avatar, the team name, and the playoff odds, and nothing more.
Files: `evidence/AT-23/steps.json`, `evidence/AT-23/before-1280-dark.png`, `evidence/AT-23/before-1280-light.png`, `evidence/AT-23/before-375-dark.png`, `evidence/AT-23/before-375-light.png`, `evidence/AT-23/before-768-dark.png`, `evidence/AT-23/before-768-light.png`
Observation: The before shots of AT-23 show the Managers index with the chips All 12, In 6, Bubble 2, and Out 4, then 12 rows. Each row shows a place, a small avatar, the team name, and the playoff odds. At 375 px all 12 rows and the bottom bar fit in the 900 px viewport, with space left under row 12. The shots are at 375 px, not 390 px, as the Evidence line asks.

## AT-23: The race chips filter the list

App: site
Then: The chips read All 12, In 6, Bubble 2, and Out 4. After the tap, only Teehee (61%) and Return of T Mac (42%) show.
Files: `evidence/AT-23/steps.json`, `evidence/AT-23/after-1280-dark.png`, `evidence/AT-23/after-1280-light.png`, `evidence/AT-23/after-375-dark.png`, `evidence/AT-23/after-375-light.png`, `evidence/AT-23/after-768-dark.png`, `evidence/AT-23/after-768-light.png`, `evidence/AT-23/before-1280-dark.png`, `evidence/AT-23/before-1280-light.png`, `evidence/AT-23/before-375-dark.png`, `evidence/AT-23/before-375-light.png`, `evidence/AT-23/before-768-dark.png`, `evidence/AT-23/before-768-light.png`
Observation: The before shots show the chips All 12, In 6, Bubble 2, and Out 4 with All pressed. The after shots show Bubble pressed and two rows only: 2 Teehee 61% and 4 Return of T Mac 42%.

## AT-24: A row opens in place

App: site
Then: The Blue Tent opens in place with the letter A, the grade read, the four arcs, and a link to its manager page, and its name rolls its letters. The tap on Lil Fridge closes The Blue Tent and opens Lil Fridge.
Files: `evidence/AT-24/steps.json`, `evidence/AT-24/blue-tent-open-1280-dark.png`, `evidence/AT-24/blue-tent-open-1280-light.png`, `evidence/AT-24/blue-tent-open-375-dark.png`, `evidence/AT-24/blue-tent-open-375-light.png`, `evidence/AT-24/blue-tent-open-768-dark.png`, `evidence/AT-24/blue-tent-open-768-light.png`, `evidence/AT-24/lil-fridge-open-1280-dark.png`, `evidence/AT-24/lil-fridge-open-1280-light.png`, `evidence/AT-24/lil-fridge-open-375-dark.png`, `evidence/AT-24/lil-fridge-open-375-light.png`, `evidence/AT-24/lil-fridge-open-768-dark.png`, `evidence/AT-24/lil-fridge-open-768-light.png`
Observation: The blue-tent-open shots show The Blue Tent open in place under its row, with the line 9-7 · Power #5 · 75% playoff, the letter A in a box, "Strong at QB and TE. Soft at RB.", four small arcs 4th, 6th, 7th, and 7th, and a Manager page pill; the rows below sit lower. The lil-fridge-open shots show The Blue Tent closed and Lil Fridge open with 10-6 · Power #6 · 86% playoff, A, "Deep at QB. Thin at WR.", arcs 5th, 5th, 6th, and 9th, and the pill. The roll of the letters is motion, and a still shot does not show it.

## AT-25: The desktop stage swaps on hover and focus

App: site
Then: The stage beside the ledger shows The Blue Tent, then Lil Fridge. The stage is built from the hero slots: the race word, the team name, the record and odds, the four arcs, the grade letter, and the manager link.
Files: none.
Observation: Ticket 09 (the desktop stage) is blocked until the hero-slots spec merges into main, so no evidence is recorded.

## AT-26: The NorCal Index list uses the NorCal data and brand

App: site
Then: The chips read In 4, Bubble 5, and Out 3, and the rows and chips use the NorCal brand colors.
Files: `evidence/AT-26/steps.json`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/375-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/768-light.png`
Observation: The NorCal shots show the Managers index with "NORCAL APEX 6" in the header and the chips All 12, In 4, Bubble 5, and Out 3, then 12 NorCal rows from Mitseeker5000 97% to The Dart Side 1%. The pressed chip and the ink use the warm cream and near-black of the NorCal brand, not the pure white and black of cpc. The avatar of VarsityBlue2 shows as a blank grey circle.

## AT-27: The readability floor passes

App: site
Then: Both runs pass, with no axe violation and no axe incomplete result.
Files: `evidence/AT-27/floor-cpc.txt`, `evidence/AT-27/floor-norcal.txt`
Observation: The last line of each run reads: cpc "106 passed (1.0m)" and norcal "103 passed (56.9s)", and neither file holds the word violation or incomplete. Each run scans axe violations and incomplete results on 7 pages and 4 open states (the ladder card, the Index list row, the game card, and the strip of weeks) at 390 px and 1280 px in both themes. The Season So Far dial sits on the manager page of the list. The runs cover every open state of the spec except the desktop stage, which waits for ticket 09.

## AT-28: No page scrolls sideways and each new control is 44 px

App: site
Then: No page scrolls sideways, and each new toggle, chip, row, and button is 44 px or more.
Files: `evidence/AT-28/floor-390.txt`, `evidence/AT-27/floor-cpc.txt`, `evidence/AT-27/floor-norcal.txt`
Observation: `floor-390.txt` lists the 390 px full floor lines of each client for the week page, the rankings page, the Managers index, a manager page (cpc /2026/managers/7/, norcal /2026/managers/4/), and the empty analyzer, plus the open game card, ladder card, and Index list row. Each line has a check mark. A full floor test stops with an error on a sideways scroll or a tap target under 44 px. Each page also logs "exempt links inside prose: none". The analyzer floor checks the empty form, with no team picked.

## AT-29: The manager page hero does not change

App: site
Then: The hero is the same: this spec adds no Grade dial and no other change to it.
Files: `evidence/AT-29/hero-diff.txt`, `evidence/AT-29/steps.txt`, `evidence/AT-29/main-hero-375-dark.png`, `evidence/AT-29/main-hero-375-light.png`, `evidence/AT-29/spec-hero-375-dark.png`, `evidence/AT-29/spec-hero-375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`
Observation: `hero-diff.txt` shows an empty diff of packages/managers/site/page/manager-hero.tsx against origin/main 25f98a02, both two-dot and three-dot. The stale local ref main (df2c08c0) shows the easter eggs change that main already holds. The main and spec shots of the hero at 375 px show The Blue Tent, the grade A, Playoff 75%, Bye 22%, Seed 5th, and the week chips, and `steps.txt` shows each pair has the same MD5. The full-page spec shots at 375 px of AT-11 show the same hero.

## AT-30: Closest and Game Changer stay plain tiles

App: site
Then: Both tiles show their number and note with no chart.
Files: `evidence/AT-15/steps.json`, `evidence/AT-15/cpc-1280-dark.png`, `evidence/AT-15/cpc-1280-light.png`, `evidence/AT-15/cpc-375-dark.png`, `evidence/AT-15/cpc-375-light.png`, `evidence/AT-15/cpc-768-dark.png`, `evidence/AT-15/cpc-768-light.png`, `evidence/AT-15/crop-cpc-numbers-1280-dark.png`, `evidence/AT-15/crop-cpc-numbers-1280-light.png`, `evidence/AT-15/crop-cpc-numbers-375-dark.png`, `evidence/AT-15/crop-cpc-numbers-375-light.png`, `evidence/AT-15/crop-cpc-numbers-768-dark.png`, `evidence/AT-15/crop-cpc-numbers-768-light.png`
Observation: The cpc shots and cuts of AT-15 show the Closest tile with 1.43 and "The Blue Tent over London Cooking", and the Game Changer tile with +20.44 and "Burrow over projection", each with no chart. The week 6 cuts of AT-16 show the same two tiles plain too.

## AT-31: The pipeline does not change

App: site
Then: The diff is empty.
Files: `evidence/AT-31/output.txt`
Observation: `output.txt` shows an empty stat of `git diff origin/main --stat -- apps/pipeline 'packages/*/python'` and of the three-dot form. The local ref main is df2c08c0, behind origin/main 25f98a02. Against it the diff lists 9 pipeline files of the easter eggs spec, which origin/main already holds.

## AT-32: No Scrolltide source enters the repo

App: site
Then: No run matches.
Files: `evidence/AT-32/output.txt`, `evidence/AT-32/scrolltide_search.py`
Observation: `output.txt` shows the search of the 2980 added non-empty lines of `git diff origin/main...HEAD` against each of the five prompts: showcase-card, health-tracker, lime-metrics, send-button (Send Halo), and team-roster. Each has 0 matching runs of 8, and the total is 0. The run on the larger diff against the stale local main also gives 0. The prompts sit only in the session scratchpad.
