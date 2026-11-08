# Card polish: acceptance tests

Spec: `.scratch/card-polish/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

## Tests

AT-1: Game card opens in place
App: site
Stories: 1, 2, 3, 4
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page `/2026/week-08/`, all cards closed
When: The reader taps the card of All You Need Is Love vs Unsolicited Dak Picks.
Then: The card grows in place under its own head, the cards below move down, the chevron turns 180 degrees, and the panel text comes into focus after the card grows.
Evidence: screenshots of the card closed and open at 375, 768, and 1280 px, each in the light theme and the dark theme. Add a screen recording of the open at 375 px.

AT-2: A closed game card keeps the scoreboard
App: site
Stories: 5
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page, the same card closed
When: The reader looks at the closed card.
Then: The card shows both avatars, both team names, 116.83 and 92.55, and the share bar.
Evidence: screenshots of the closed card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-3: An open game card shows three chips
App: site
Stories: 6, 7
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the same card
When: The reader opens the card.
Then: The panel shows three chips: the avatar of All You Need Is Love with Best J. Burrow 42.48, the avatar of Unsolicited Dak Picks with Best J. Jacobs 20.2, and Records 11-5 · 6-10. No Margin chip and no Vs proj chip shows.
Evidence: screenshots of the open panel at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-4: An open game card shows the recap and the manager link
App: site
Stories: 8
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the same card open
When: The reader looks at the panel.
Then: The recap text shows under the chips, and a Manager page pill links to the manager page of All You Need Is Love. The pill label sits on a solid fill.
Evidence: screenshots of the open panel at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-5: A ladder card shows the rank large
App: site
Stories: 9, 10
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the rankings page `/rankings/`, week 8
When: The reader looks at the closed card of The Blue Tent.
Then: The card shows 05 large in a plain raised panel, then The Blue Tent, 9-7, ▲3, the odds bar, and Playoff 75%.
Evidence: screenshots of the closed card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-6: An open ladder card shows its chips and blurb
App: site
Stories: 11
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the rankings page, the card of The Blue Tent
When: The reader opens the card.
Then: The panel shows the chips Stand 6, Form 6, Sched 8, Pts 7, Move ▲3, Bye 22%, and Seed 5, then the blurb of The Blue Tent.
Evidence: screenshots of the open panel at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-7: The manager, award, and trade cards open the same way
App: site
Stories: 12
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page for AwardTile and TradeCard, and the page of each manager card
When: The reader opens one card of each kind.
Then: Each card opens with the same drawer, blur-in, and chevron as the game card.
Evidence: screenshots of each card open at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-8: The text of a closed card stays findable
App: site
Stories: 13, 14
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page, all cards closed
When: The reader runs find-in-page for a word of the recap of All You Need Is Love vs Unsolicited Dak Picks.
Then: The browser finds the word. The closed panel has `inert`, and its toggle has `aria-expanded="false"` and `aria-controls` set to the panel id.
Evidence: the find result in a screenshot at 1280 px, and the DOM attributes of the toggle and the panel.

AT-9: Reduced motion opens a card at once
App: site
Stories: 15, 23, 37, 49
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the browser set to `prefers-reduced-motion: reduce`
When: The reader opens a game card, a ladder card, and an Index list row, and scrolls a Grade dial into view.
Then: Each part reaches its end state at once, with no height animation, no blur, no spring, and no fill animation.
Evidence: the output of the reduced-motion test, and screenshots at 375 px of each part right after the tap.

AT-10: The blur stays smooth on a slow phone
App: site
Stories: 16
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page at a 375 px viewport, Chromium with 4x CPU throttle
When: The reader opens the card of All You Need Is Love vs Unsolicited Dak Picks.
Then: The median frame rate of the open is 50 fps or more. If it is lower, the blur is gone from the Open card and the evidence says why (ADR 0028).
Evidence: the script, its output with the frame rate, and the throttle setting.

AT-11: Season So Far shows the Grade dial
App: site
Stories: 17, 19, 21
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the manager page `/2026/managers/1/` of The Blue Tent
When: The reader scrolls to Season So Far.
Then: The section shows the letter A, the grade read, and four arcs in a 2x2 grid: 4th, 6th, 7th, and 7th, with 9, 7, 6, and 6 of 12 blades lit.
Evidence: screenshots of Season So Far at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-12: Each arc names its part, rank, and weight as text
App: site
Stories: 18, 20, 22
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the same page
When: The reader reads the four arcs, or a screen reader reads them.
Then: Each arc has its part name, its rank such as 4th, and N% of the grade as text: Projection 45%, Production 30%, Trade value 10%, Depth 15%.
Evidence: the accessible names of the four arcs, and the screenshots of AT-11.

AT-13: The weights match the pipeline
App: site
Stories: none (decision 09)
Given: the site weight constant and `GRADE_WEIGHTS` in the pipeline tunables file
When: The agent changes the site constant of depth from 15 to 16 and runs the site test.
Then: The weights test fails. With the constant back at 15, it passes.
Evidence: the two test outputs.

AT-14: The top score trend runs from week 1
App: site
Stories: 24, 28
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page
When: The reader looks at the Top score tile.
Then: The tile shows 134.1 and eight bars: 156.92, 156.52, 140.6, 145.63, 158.96, 126.79, 148.13, and 134.1, with the week 8 bar lit.
Evidence: screenshots of the week numbers at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-15: The median trend ends at the number of the tile
App: site
Stories: 25
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page, and the NorCal site at week 8
When: The reader looks at the Median tile of each client.
Then: The CPC stepped area has eight points and ends at 99.6, the number on the tile. The NorCal trend ends at the number on the NorCal tile.
Evidence: screenshots of the week numbers of each client at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-16: An older week page stops its trend at that week
App: site
Stories: 29
Given: the CPC site, the week page `/2026/week-06/`
When: The reader looks at the Top score tile.
Then: The tile shows six bars, from 156.92 to 126.79, with the week 6 bar lit and no bar for week 7 or 8.
Evidence: screenshots of the week numbers at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-17: The Moves tiles show the moves of each week
App: site
Stories: 30, 31
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the manager page of The Blue Tent
When: The reader looks at Moves.
Then: The Adds tile shows bars 5, 1, 2, 4, 1, 1, 6, and 3 for weeks 1 to 8. The Trades tile shows dots at week 1 and week 4 only.
Evidence: screenshots of Moves at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-18: A Trend tile has a text of its trend
App: site
Stories: 32
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page and the manager page of The Blue Tent
When: A screen reader reads each Trend tile.
Then: Each of the five Trend tiles reads its number and one sentence of its trend.
Evidence: the accessible text of the five tiles.

AT-19: The Ready halo brightens step by step
App: site
Stories: 33
Given: the Trade Analyzer `/analyze/` on the CPC site, a new trade with two sides
When: The reader picks a team for each side and adds no player.
Then: The halo glows at the level of 2 of 6 checks, brighter than with no team and below full.
Evidence: screenshots of the grade button with no team, with two teams, and with a full trade, at 375 px in both themes, and the level value of each.

AT-20: The Ready halo is full only when the trade is ready
App: site
Stories: 34, 35
Given: the Trade Analyzer, two teams picked
When: The reader adds a get and a give to each side, then removes one player.
Then: The halo reaches full when the Grade button can grade, and it dims when the player goes.
Evidence: the screenshots of each state at 375 px in both themes.

AT-21: The Ready halo works in the light theme and with reduced motion
App: site
Stories: 36, 37
Given: the Trade Analyzer, a full trade
When: The reader views it in the light theme, then with reduced motion.
Then: The halo reads against the light page. With reduced motion it shows the level with no pulse or orbit.
Evidence: screenshots at 375 px in the light theme and with reduced motion.

AT-22: The Index list shows every team on one phone screen
App: site
Stories: 38, 39
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the Managers index `/2026/managers/`, a 390 px viewport
When: The reader opens the page.
Then: All 12 rows show on one screen with the chips closed. Each row shows the place, a small avatar, the team name, and the playoff odds, and nothing more.
Evidence: screenshots of the Managers index at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-23: The race chips filter the list
App: site
Stories: 40, 41, 42
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the Managers index
When: The reader taps the Bubble chip.
Then: The chips read All 12, In 6, Bubble 2, and Out 4. After the tap, only Teehee (61%) and Return of T Mac (42%) show.
Evidence: screenshots of the list before and after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-24: A row opens in place
App: site
Stories: 43, 44, 45
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the Managers index at 390 px
When: The reader taps The Blue Tent, then taps Lil Fridge.
Then: The Blue Tent opens in place with the letter A, the grade read, the four arcs, and a link to its manager page, and its name rolls its letters. The tap on Lil Fridge closes The Blue Tent and opens Lil Fridge.
Evidence: screenshots of each open row at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-25: The desktop stage swaps on hover and focus
App: site
Stories: 46, 47, 48
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the Managers index at 1280 px, after `hero-slots` merges into `main`
When: The reader hovers over The Blue Tent, then moves the keyboard focus to Lil Fridge.
Then: The stage beside the ledger shows The Blue Tent, then Lil Fridge. The stage is built from the hero slots: the race word, the team name, the record and odds, the four arcs, the grade letter, and the manager link.
Evidence: screenshots at 1280 px in both themes of each state, and the slot names in the DOM.

AT-26: The NorCal Index list uses the NorCal data and brand
App: site
Stories: 50
Given: the NorCal site built from `clients/norcal/published/2026/`, page week 8
When: The reader opens the Managers index.
Then: The chips read In 4, Bubble 5, and Out 3, and the rows and chips use the NorCal brand colors.
Evidence: screenshots of the NorCal Managers index at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-27: The readability floor passes
App: site
Stories: 51
Given: both clients built with this spec
When: The agent runs `CLIENT=cpc pnpm check:floor` and `CLIENT=norcal pnpm check:floor`, with the new open states in the floor spec.
Then: Both runs pass, with no axe violation and no axe incomplete result.
Evidence: the output of both runs.

AT-28: No page scrolls sideways and each new control is 44 px
App: site
Stories: 52, 53
Given: both clients, a 390 px viewport
When: The agent runs the floor check of width and tap targets on the week page, the rankings page, the Managers index, a manager page, and the analyzer.
Then: No page scrolls sideways, and each new toggle, chip, row, and button is 44 px or more.
Evidence: the floor output for each page.

AT-29: The manager page hero does not change
App: site
Stories: none
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the manager page of The Blue Tent
When: The agent compares the hero with the hero on `main`.
Then: The hero is the same: this spec adds no Grade dial and no other change to it.
Evidence: screenshots of the hero on `main` and on the spec branch at 375 px, and the diff of the manager hero file, which is empty.

AT-30: Closest and Game Changer stay plain tiles
App: site
Stories: 26, 27
Given: the CPC site built from `clients/cpc/published/2026/`, page week 8, the week page
When: The reader looks at the Closest and Game Changer tiles.
Then: Both tiles show their number and note with no chart.
Evidence: screenshots of the week numbers at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-31: The pipeline does not change
App: site
Stories: none
Given: the spec branch
When: The agent runs `git diff main --stat -- apps/pipeline packages/*/python`.
Then: The diff is empty.
Evidence: the command output.

AT-32: No Scrolltide source enters the repo
App: site
Stories: none
Given: the spec branch and the Scrolltide prompts in the session scratchpad
When: The agent searches the diff of the spec branch for runs of eight or more lines copied from each prompt.
Then: No run matches.
Evidence: the search script and its output.

## Trace

Story 1: AT-1
Story 2: AT-1
Story 3: AT-1
Story 4: AT-1
Story 5: AT-2
Story 6: AT-3
Story 7: AT-3
Story 8: AT-4
Story 9: AT-5
Story 10: AT-5
Story 11: AT-6
Story 12: AT-7
Story 13: AT-8
Story 14: AT-8
Story 15: AT-9
Story 16: AT-10
Story 17: AT-11
Story 18: AT-12
Story 19: AT-11
Story 20: AT-12
Story 21: AT-11
Story 22: AT-12
Story 23: AT-9
Story 24: AT-14
Story 25: AT-15
Story 26: AT-30
Story 27: AT-30
Story 28: AT-14
Story 29: AT-16
Story 30: AT-17
Story 31: AT-17
Story 32: AT-18
Story 33: AT-19
Story 34: AT-20
Story 35: AT-20
Story 36: AT-21
Story 37: AT-9, AT-21
Story 38: AT-22
Story 39: AT-22
Story 40: AT-23
Story 41: AT-23
Story 42: AT-23
Story 43: AT-24
Story 44: AT-24
Story 45: AT-24
Story 46: AT-25
Story 47: AT-25
Story 48: AT-25
Story 49: AT-9
Story 50: AT-26
Story 51: AT-27
Story 52: AT-28
Story 53: AT-28
Out of scope "the Grade dial in the manager hero": AT-29
Out of scope "a trend on the Closest and Game Changer tiles": AT-30
Out of scope "a pipeline series for the trends": AT-31
Out of scope "no Scrolltide source in the repo" (map rule): AT-32
Decision 09 "the weights test": AT-13

## Revisions

None yet.
