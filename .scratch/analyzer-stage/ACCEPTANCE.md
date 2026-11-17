# Analyzer stage: acceptance tests

Spec: `.scratch/analyzer-stage/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

Trade B is real data of client `cpc`, season `2026`, from the teams route of 2026 on 2026-11-17: The Blue Tent (roster 1) gets `11560`, `1466`, `2449`, `3198`, and `4034` from Lil Fridge (roster 3). All You Need Is Love (roster 2) gets `10229` and `11604` from The Blue Tent. Lil Fridge gets `12527` and `13287` from All You Need Is Love, and `11584` from The Blue Tent. The evidence agent records the name of each player. If a roster has moved, the agent picks a real trade of 3 sides where one side gets 5 players, and records it.

Trade T is real data of client `cpc`, season `2026`, week 9: roster 6, Bo Girds, gives Kenneth Walker III (`8151`) to roster 12, Teehee, for Tee Higgins (`6801`) and Bhayshul Tuten (`12490`). Bo Girds asks. The grade reads the live snapshot, so the Lean of trade T can move. The evidence agent records the Lean and the favored side on the day of the run.

The analyzer tests run against the local API through the evidence harness (`apps/site/e2e/evidence.ts`). A test that samples the wait holds the real analyze request with a Playwright route, then passes it on to the local API. The hero stays dark in both themes, but each site test still takes both themes (ADR 0006).

## Tests

AT-1: The idle mesh is calm
App: site
Stories: 3
Given: The analyzer of `cpc` with an empty Stack.
When: The reader opens the page and waits 3 s.
Then: The hero shows a flat mesh at the 24 px pitch of the hero grid, with no pulses, and two screenshots 2 s apart show the same mesh.
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and the two screenshots 2 s apart at 1280 px.

AT-2: An added player shows on the stage
App: site
Stories: 1, 2
Given: The analyzer of `cpc`, with Bo Girds and Teehee as the two teams of the Stack.
When: The reader adds Kenneth Walker III to the side of Bo Girds.
Then: The row of Teehee on the stage shows "1 player" and no headshot.
Evidence: screenshots of the hero before and after the add, at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-3: The wait starts on the tap
App: site
Stories: 4
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade".
Then: Within 100 ms of the tap, the mesh moves and the stage line "Weighing the sides" shows.
Evidence: the time stamps of the tap and of the first line, and screenshots of the hero 100 ms after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-4: The grade button goes pending
App: site
Stories: 17, 18
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" with the keyboard.
Then: The button has `aria-busy="true"` and `data-pending`, it keeps the focus, its label stays "Grade the Trade", and it is the wrapper of the ui-sdk `Button`.
Evidence: the attributes of the button and the active element 2 s into the wait, the import line of the wrapper, and screenshots of the button at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-5: The mesh weighs each side in turn
App: site
Stories: 5, 6
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 5 s.
Then: The mesh dips under the side of Bo Girds, then under the side of Teehee, about 1.25 s each, with light pulses on the mesh lines.
Evidence: a screen recording of 5 s of the wait at 1280 px, and screenshots at each dip at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-6: The stage lines change every 2.5 s
App: site
Stories: 7
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 10 s.
Then: 4 different stage lines show in the 10 s, each for about 2.5 s, and the first is "Weighing the sides".
Evidence: the text and the time stamp of each line in the 10 s, and screenshots of two lines at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-7: A stage line names the trade
App: site
Stories: 8
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 30 s.
Then: At least one stage line names Kenneth Walker III, Tee Higgins, Bhayshul Tuten, Bo Girds, or Teehee.
Evidence: the text of each line in the 30 s, and screenshots of a line with a name at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-8: The stage lines never claim a step is done
App: site
Stories: 9
Given: The stage line function, with trade T and with a real trade of three sides that the evidence agent picks and records.
When: The unit test runs.
Then: Each list has 12 lines, line 1 is "Weighing the sides", line 12 is "Weighing it all together", and no line says Jev, Advisor, Finder, front door, rival, done, or finished.
Evidence: the vitest command, its output, and the 12 lines of each list.

AT-9: A screen reader hears one message
App: site
Stories: 16
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 7 s.
Then: Two snapshots of the accessibility tree, at 2 s and at 7 s, show the same one status, "Grading the trade", and no stage line.
Evidence: both snapshots of the accessibility tree, and screenshots of the hero at the same times at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-10: The grade shows with no fake delay
App: site
Stories: 10
Given: The analyzer of `cpc` with trade T in the Stack, after one grade of trade T, so the next grade is a cached repeat.
When: The reader taps "Grade the Trade".
Then: The Lean word shows within 1.3 s of the analyze response.
Evidence: the time stamps of the response and of the Lean word, and screenshots of the result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-11: The reveal shows the Lean first
App: site
Stories: 11, 12
Given: The analyzer of `cpc` with trade T in the Stack.
When: The analyze response arrives.
Then: The Lean word shows first, then the Lean scale, then the Case and the side tabs, all within about 1 s.
Evidence: the time stamp of each part, a screen recording of the reveal at 1280 px, and screenshots of the end of the reveal at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-12: The mesh dips toward the favored side
App: site
Stories: 13
Given: The analyzer of `cpc` with trade T in the Stack, and a Lean that favors one side.
When: The analyze response arrives.
Then: The mesh lines of the favored side flash once, then the mesh dips toward that side and goes flat.
Evidence: the Lean and the favored side, a screen recording of the reveal at 1280 px, and screenshots of the flash and the dip at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-13: With motion off, the hero stays still
App: site
Stories: 14
Given: The analyzer of `cpc` with trade T in the Stack and reduced motion on.
When: The reader taps "Grade the Trade" and the result arrives.
Then: The mesh does not move during the wait, and the result appears in a plain fade.
Evidence: two screenshots of the hero 2 s apart in the wait, a screen recording of the reveal, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-14: With motion off, the stage lines still change
App: site
Stories: 15
Given: The analyzer of `cpc` with trade T in the Stack, reduced motion on, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 6 s.
Then: The stage line changes about every 2.5 s, with no shimmer.
Evidence: the text and the time stamp of each line, and screenshots of two lines at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-15: The wait stays smooth on a phone
App: site
Stories: 19
Given: The analyzer of `cpc` at 375 px with a 4x CPU slowdown, trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 5 s.
Then: After the first second, no frame of the wait takes longer than 50 ms.
Evidence: the performance trace, the longest frame after the first second, and screenshots of the wait at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-16: The canvas pauses out of view
App: site
Stories: 19
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held, in the wait.
When: The reader scrolls the hero out of view, and then hides the tab.
Then: The canvas draws no frame while the hero is out of view, and no frame while the tab is hidden.
Evidence: the frame count of the canvas over 2 s in each case, and screenshots of the page scrolled down at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-17: Hero text has no dark box
App: site
Stories: 20
Given: Client `cpc`, `2026` week 9: the week hero, the manager page of Bo Girds, the midseason report opener, the 404 page, and the analyzer result of trade T.
When: The reader opens each page.
Then: No hero text has a dark box behind it.
Evidence: screenshots of each hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-18: The floor reads every hero text
App: site
Stories: 21, 24, 25, 27
Given: The static export of each client, `cpc` and `norcal`.
When: The readability floor runs with the pixel scan of hero text.
Then: Each hero text on each page of the floor reaches 4.5:1 or more, at 390 and 1280 px, and the floor passes.
Evidence: the floor command and its output in each client, with the worst ratio of each hero, and screenshots of the week hero of each client at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-19: The losing score of the week hero stays readable
App: site
Stories: 22
Given: The week hero of `cpc`, `2026` week 9, where Maye d'force B with U lost with 106.71. With no plate and the old glow, the score measured 4.35:1.
When: The pixel scan reads the hero.
Then: The score 106.71 reaches 4.5:1 or more at 390 and 1280 px.
Evidence: the ratio of the score at each width, and screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-20: The analyzer text stays readable while the mesh moves
App: site
Stories: 23
Given: The analyzer of each client, `cpc` and `norcal`, with a real trade of two sides. Trade T is the trade in `cpc`. The evidence agent picks and records a trade in `norcal`.
When: The pixel scan reads the hero in idle, in the wait with 10 samples over 3 s, and at the end of the reveal.
Then: Each hero text, including the row label of each side, reaches 4.5:1 or more in each state, at 390 and 1280 px.
Evidence: the worst ratio of each text in each state, and screenshots of each state at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-21: The egg banner text stays readable
App: site
Stories: 21
Given: A page with the egg banner, with eggs on as in `apps/site/e2e/eggs.spec.ts`.
When: The pixel scan reads the banner.
Then: Each text of the egg banner reaches 4.5:1 or more at 390 and 1280 px.
Evidence: the ratio of each text, and screenshots of the banner at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-22: The floor still catches a gap
App: site
Stories: 27
Given: The scans of the readability floor.
When: The unit test runs with an axe "incomplete" result outside a hero, and with a hero where the pixel scan finds no text.
Then: The floor fails in both cases, and each failure names the case.
Evidence: the test command and its output.

AT-23: The Finder keeps Sweep
App: site
Stories: 28
Given: The analyzer of `norcal`, where the Finder is on.
When: The reader starts a Finder search.
Then: The Finder wait shows the `Sweep` bar, and no mesh and no stage line.
Evidence: screenshots of the Finder wait at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-24: The front door chat wait does not change
App: site
Stories: none
Given: The front door of `cpc`, with a question asked.
When: The answer is in progress.
Then: The chat wait shows no mesh and no stage line.
Evidence: screenshots of the chat wait at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-25: The hero scene does not change
App: site
Stories: none
Given: The week hero of `cpc`, `2026` week 9.
When: The reader opens the page.
Then: The hero scene keeps its own row, and no light of the scene sits under a hero text.
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-26: The analyze call stays one request with no stream
App: site
Stories: none
Given: The analyzer of `cpc` with trade T in the Stack.
When: The reader grades the trade.
Then: The network log shows one `POST` to the analyze route, with a JSON response, not `text/event-stream`.
Evidence: the network log of the grade, and screenshots of the result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-27: A big trade stays compact
App: site
Stories: 29
Given: The analyzer of `cpc` with trade B in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade".
Then: The stage shows 3 rows, one per side, and the row of The Blue Tent shows 3 headshots and a "+2" token.
Evidence: screenshots of the hero in the wait at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-28: Idle shows no headshot on the stage
App: site
Stories: 30
Given: The analyzer of `cpc` with trade T in the Stack.
When: The reader looks at the hero before the grade.
Then: The row of Bo Girds shows "2 players", the row of Teehee shows "1 player", and the hero shows no headshot.
Evidence: screenshots of the hero and the Stack at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-29: The headshots rise into the rows on the tap
App: site
Stories: 30
Given: The analyzer of `cpc` with trade T in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade".
Then: Within 1 s, the row of Bo Girds shows the headshots of Tee Higgins and Bhayshul Tuten, and the row of Teehee shows the headshot of Kenneth Walker III.
Evidence: the time stamps of the tap and of the last headshot in view, and screenshots of the hero 1 s after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-30: The result shows the players once
App: site
Stories: 31
Given: The analyzer of `cpc` with the result of trade T.
When: The reader scrolls from the hero to the end of the result.
Then: The result has no "The Trade" chapter, and below the hero it has no player chip, no headshot, and no `FoldLine` card.
Evidence: screenshots of the full result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-31: Edit sits in the header of The Sides
App: site
Stories: 32
Given: The analyzer of `cpc` with the result of trade T.
When: The reader taps Edit in the header of "The Sides".
Then: The Stack opens with trade T and scrolls into view, and the target of Edit is 44 px or more on each side.
Evidence: the size of the Edit target, and screenshots of the header and of the open Stack at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-32: A long fairness reason folds
App: site
Stories: 33
Given: The analyzer of `cpc` at 375 px with the result of a real trade whose fairness reason of one side runs past 3 lines. The evidence agent picks the trade and records it.
When: The reader taps "More" under that reason.
Then: Before the tap the reason shows 3 lines and "More", and after the tap it shows in full.
Evidence: screenshots of the reason before and after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-33: A long stage line shows in full
App: site
Stories: 34
Given: The analyzer of `cpc` at 375 px with trade B in the Stack, and the analyze request held.
When: The reader taps "Grade the Trade" and the wait runs for 30 s.
Then: Each stage line is set at the size of `text-body`, and a line wider than the hero scrolls from right to left until its end is in view.
Evidence: the computed font size, the text and the width of each line, a screen recording of a long line, and screenshots of its start and its end at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-34: With motion off, a long stage line wraps
App: site
Stories: 34
Given: The analyzer of `cpc` at 375 px with trade B in the Stack, reduced motion on, and the analyze request held.
When: The wait shows a stage line wider than the hero.
Then: The line wraps to a second line in full and does not move.
Evidence: two screenshots of the line 1 s apart, and screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

## Trace

Story 1: AT-2
Story 2: AT-2
Story 3: AT-1
Story 4: AT-3
Story 5: AT-5
Story 6: AT-5
Story 7: AT-6
Story 8: AT-7
Story 9: AT-8
Story 10: AT-10
Story 11: AT-11
Story 12: AT-11
Story 13: AT-12
Story 14: AT-13
Story 15: AT-14
Story 16: AT-9
Story 17: AT-4
Story 18: AT-4
Story 19: AT-15, AT-16
Story 20: AT-17
Story 21: AT-18, AT-21
Story 22: AT-19
Story 23: AT-20
Story 24: AT-18
Story 25: AT-18
Story 26: no test. Reason: ADR 0036 is already on the Spec branch, from decision 05.
Story 27: AT-18, AT-22
Story 28: AT-23
Story 29: AT-27
Story 30: AT-28, AT-29
Story 31: AT-30
Story 32: AT-31
Story 33: AT-32
Story 34: AT-33, AT-34
Out of scope "The wait of the front door chat": AT-24
Out of scope "Real progress from an API stream": AT-26
Out of scope "A new loader for the Finder wait": AT-23
Out of scope "A change to the hero scene of the other pages": AT-25

## Revisions

- 2026-11-17: Decision 06. Brian approved a change to AT-2 (idle shows a count, not the name) and to AT-20 (row label, not column label), and the new tests AT-27 to AT-34.
