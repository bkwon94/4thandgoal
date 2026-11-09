# Egg polish: acceptance tests

Spec: `.scratch/egg-polish/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

## The setup of every test

- The CPC site is built from `clients/cpc/published/2026/`, page week 8, and served from the static export.
- The API runs on this machine with a temp SQLite file, the test passphrase, and the test commissioner key of `make -C apps/api api-evidence`.
- The test egg T1 is a double-tap on the Luck cell of Lil Fridge on `/midseason/2026/`, in the light theme. Its letter is C.
- Each other state of the board comes from claims posted to the local API, as each Given says.
- The repo is public, so no evidence uses a real spot or `~/cpc-eggs/2026.toml`.
- A test of motion adds a screen recording at 375 px. A time in a Then is read from the recording.

## Tests

AT-1: The tap squashes the egg
App: site
Stories: 1
Given: T1 dropped, with no claim. The find card shows the egg.
When: The reader taps the middle of the egg.
Then: The egg squashes within 0.2 s of the tap, before any crack line shows.
Evidence: a screen recording at 375 px, and frames at 0 s, 0.1 s, and 0.2 s after the tap.

AT-2: The crack starts at the tap point
App: site
Stories: 2
Given: T1 dropped, with no claim. The find card shows the egg.
When: The reader taps the egg near its upper left, about one quarter in from the left and one third down.
Then: Every crack line starts at the spot of the tap.
Evidence: a screen recording at 375 px, and a frame at 0.4 s after the tap with the tap point marked.

AT-3: Each find cracks anew
App: site
Stories: 3
Given: T1 dropped, with no claim.
When: The reader finds T1 twice in two fresh page loads, and taps the same spot of the egg each time.
Then: The crack lines of the two finds differ.
Evidence: two frames at 0.4 s after the tap, one from each find, side by side.

AT-4: The crack builds, then bursts
App: site
Stories: 4, 5
Given: T1 dropped, with no claim. The find card shows the egg.
When: The reader taps the egg.
Then: The egg shakes and glows from the tap point while the lines draw, then the shell bursts into shards that fly out from the tap point at about 0.56 s.
Evidence: a screen recording at 375 px, and frames at 0.3 s and 0.6 s after the tap.

AT-5: The tile grows from the tap point
App: site
Stories: 6, 7
Given: T1 dropped, with no claim. The find card shows the egg.
When: The reader taps the egg near its lower right.
Then: The letter tile grows out of the spot of the tap, and the tile C with the copy "The letter C is yours to claim." shows at 1.3 s, plus or minus 0.2 s, after the tap.
Evidence: a screen recording at 375 px, and screenshots of the letter state at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-6: Enter cracks the egg from its middle
App: site
Stories: 8
Given: T1 dropped, with no claim. The find card shows the egg, and the focus is on the egg.
When: The reader presses Enter.
Then: The crack lines start at the middle of the egg, and the letter C shows.
Evidence: a screen recording at 375 px of the run by the keyboard.

AT-7: Reduced motion shows the letter at once
App: site
Stories: 9
Given: T1 dropped, with no claim. The browser sets `prefers-reduced-motion: reduce`.
When: The reader taps the egg.
Then: The letter C shows at once, with no crack line, no shard, and no motion.
Evidence: a screen recording at 375 px, and the output of the hunt test with motion off.

AT-8: The crack needs no WebGL
App: site
Stories: 10
Given: T1 dropped, with no claim. Chromium runs with WebGL turned off.
When: The reader finds T1 and taps the egg.
Then: The crack plays to the letter C, and the page asks for no WebGL context.
Evidence: a screen recording at 375 px, and the output of a page script that counts the calls of `getContext` with a WebGL type, which is 0.

AT-9: The claim ticket shows what the manager claims
App: site
Stories: 11
Given: T1 dropped, with no claim. The reader opened the claim sheet from the letter C.
When: The reader picks Lil Fridge and CORNERSTONE, and the browser holds the passphrase.
Then: The claim ticket shows the tile C, CORNERSTONE, and Lil Fridge, and the stub reads "Tear to claim".
Evidence: screenshots of the claim sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-10: A locked stub names the next step
App: site
Stories: 12
Given: T1 dropped, with no claim. The reader opened the claim sheet and picked Lil Fridge, with no egg word.
When: The reader taps the stub.
Then: The stub reads "Pick an egg word", it does not tear, and the API gets no claim.
Evidence: screenshots of the claim sheet at 375, 768, and 1280 px, each in the light theme and the dark theme, and the request log of the local API with no claim.

AT-11: A drag tears the stub and sends the claim
App: site
Stories: 13, 17
Given: T1 dropped, with no claim. The claim ticket of AT-9 is ready.
When: The reader drags the stub to the right to its full length.
Then: The holes of the perforation pop from the top down during the drag, the stub flutters away, the ticket shows the sweep, and the API gets one claim of T1 for Lil Fridge into CORNERSTONE.
Evidence: a screen recording at 375 px, and the request log of the local API with one claim.

AT-12: An early release sends nothing
App: site
Stories: 14
Given: T1 dropped, with no claim. The claim ticket of AT-9 is ready.
When: The reader drags the stub halfway and lets go.
Then: The stub springs back onto the ticket, and the API gets no claim.
Evidence: a screen recording at 375 px, and the request log of the local API with no claim.

AT-13: A tap tears the stub
App: site
Stories: 15
Given: T1 dropped, with no claim. The claim ticket of AT-9 is ready.
When: The reader taps the stub, with no drag.
Then: The stub tears by itself, and the API gets one claim of T1.
Evidence: a screen recording at 375 px, and the request log of the local API with one claim.

AT-14: A key tears the stub
App: site
Stories: 16
Given: T1 dropped, with no claim. The claim ticket of AT-9 is ready, and the focus is on the stub.
When: The reader presses Enter.
Then: The stub tears, and the API gets one claim of T1. The accessible name of the stub is "Tear to claim C for CORNERSTONE".
Evidence: a screen recording at 375 px, the accessibility tree of the stub, and the request log of the local API. Run it again with Space on a fresh drop.

AT-15: A claim stamps CLAIMED
App: site
Stories: 18
Given: T1 dropped, with no claim. The claim ticket of AT-9 is ready.
When: The reader tears the stub.
Then: The ticket stamps CLAIMED, and then the end card of a claim shows, with the red tile C in its slot of CORNERSTONE.
Evidence: screenshots of the stamp and of the end card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-16: A claim too late stamps TAKEN
App: site
Stories: 19
Given: T1 dropped. The first browser claims T1 for Lil Fridge into CORNERSTONE, and its claim wins. The second browser shows the claim ticket of T1 for Teehee into CORNERSTONE.
When: The second browser tears its stub.
Then: The second ticket stamps TAKEN, the stub comes back onto it, and then the end card for another manager first shows.
Evidence: screenshots of the second browser at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-17: A wrong passphrase brings the stub back
App: site
Stories: 20
Given: T1 dropped, with no claim. The browser holds no passphrase. The reader picked Lil Fridge and CORNERSTONE and typed "wrongpass".
When: The reader tears the stub.
Then: The text "The passphrase is wrong. Ask a league member for it." shows, and the stub comes back onto the ticket. After the reader types the test passphrase and tears again, the ticket stamps CLAIMED.
Evidence: screenshots of the error at 375, 768, and 1280 px, each in the light theme and the dark theme, and a screen recording at 375 px of the second tear.

AT-18: A block ticket shows the block
App: site
Stories: 21
Given: Lil Fridge holds the C of CORNERSTONE and the C of no other egg word, and a test egg T4 with the letter C is dropped.
When: The reader finds T4, opens the claim sheet, and picks Lil Fridge.
Then: The ticket shows the tile C and the block in place of an egg word, and the stub reads "Tear to claim".
Evidence: screenshots of the claim sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-19: Reduced motion keeps the claim still
App: site
Stories: 22
Given: T1 dropped, with no claim. The claim ticket of AT-9 is ready. The browser sets `prefers-reduced-motion: reduce`.
When: The reader taps the stub.
Then: The stub leaves and the stamp CLAIMED shows, with no flutter, no sweep, and no motion.
Evidence: a screen recording at 375 px.

AT-20: The egg board hero sits on the hero slots
App: site
Stories: 23, 24, 25
Given: T1 dropped, with no claim. The reader opens the egg board.
When: The reader looks at the hero.
Then: The hero shows the eyebrow "Egg hunt", the title "The Egg Board", the meta line of the gift cards, the grid of the eggs of each week with its legend, and three tiles for left to find, found, and to drop. The hero has no scene canvas.
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and the count of `canvas` elements in the hero, which is 0.

AT-21: The tab row shows each race
App: site
Stories: 26, 27
Given: Lil Fridge holds C and O in CORNERSTONE, and Teehee holds L in LANSDALE. No manager holds a letter of EAGLES.
When: The reader opens the egg board.
Then: The tab row reads CORNERSTONE 2/11, LANSDALE 1/8, and EAGLES 0/6, in that order.
Evidence: screenshots of the tab row at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-22: The closest race opens first
App: site
Stories: 28
Given: Lil Fridge holds E, A, G, L, and S in EAGLES, and holds C and O in CORNERSTONE. No manager holds a letter of LANSDALE.
When: The reader opens the egg board.
Then: The slider opens on EAGLES, and the tabs keep the order CORNERSTONE, LANSDALE, EAGLES.
Evidence: screenshots of the slider at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-23: The giant word lights the letters of the leader
App: site
Stories: 29
Given: The board of AT-22.
When: The reader looks at the slide of EAGLES.
Then: The giant word lights E, A, G, L, and S in white, and shows the second E as a dim outline.
Evidence: screenshots of the slide at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-24: A swipe or a tab moves the slide
App: site
Stories: 30
Given: The board of AT-22, on the slide of EAGLES.
When: The reader swipes the slider to the side, then taps the tab LANSDALE, then swipes up on the slider.
Then: The side swipe moves to the next slide, the tap moves to LANSDALE with the giant word swapping letter by letter, and the swipe up scrolls the page.
Evidence: a screen recording at 375 px.

AT-25: A slide keeps the detail of each manager
App: site
Stories: 31
Given: Six managers hold letters of CORNERSTONE: Lil Fridge holds 4, and five other managers hold 1 each.
When: The reader opens the slide of CORNERSTONE and taps "Show all 11".
Then: The slide shows "Lil Fridge leads with 4 of 11.", the top 5 managers with their tiles, and after the tap, all 11 managers in place.
Evidence: screenshots before and after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-26: A tie says that the managers tie
App: site
Stories: 32
Given: Lil Fridge and Teehee each hold 2 letters of CORNERSTONE, and no other manager holds more.
When: The reader opens the slide of CORNERSTONE.
Then: The leader line reads "Lil Fridge and Teehee tie with 2 of 11.", with the two teams in the order of the rosters.
Evidence: screenshots of the slide at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-27: A won word washes red and goes last
App: site
Stories: 33, 34
Given: Lil Fridge holds every letter of EAGLES, so EAGLES is won. Lil Fridge holds C in CORNERSTONE.
When: The reader opens the egg board and moves to the last slide.
Then: The last slide is EAGLES. It washes the frame red, lights every letter in red, and shows Lil Fridge and the gift card. The tab reads "EAGLES · Won".
Evidence: screenshots of the slide and the tab row at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-28: Before any claim the board opens on CORNERSTONE
App: site
Stories: 35
Given: T1 dropped, with no claim.
When: The reader opens the egg board.
Then: The slider opens on CORNERSTONE with every letter as a dim outline, and the line "No letters yet. The race is open." shows.
Evidence: screenshots of the slider at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-29: The arrow keys move between tabs
App: site
Stories: 36
Given: The board of AT-22. The focus is on the tab CORNERSTONE.
When: The reader presses the right arrow twice.
Then: The focus moves to LANSDALE, then to EAGLES, and the slide follows each tab. The tab row has the role `tablist`, each tab has the role `tab`, and each slide has the role `tabpanel`.
Evidence: a screen recording at 375 px, and the accessibility tree of the slider.

AT-30: Reduced motion changes the word at once
App: site
Stories: 37
Given: The board of AT-22. The browser sets `prefers-reduced-motion: reduce`.
When: The reader taps the tab LANSDALE.
Then: The slide changes at once, with no roll, no blur, and no letter swap.
Evidence: a screen recording at 375 px.

AT-31: Every part keeps the readability floor
App: site
Stories: 38
Given: T1 dropped, and the boards of AT-22 and AT-27.
When: The floor check runs on the find card, the claim sheet, and the egg board.
Then: Axe finds 0 violations and 0 incomplete items, each tap target is 44px or more, and no page scrolls to the side at 390px.
Evidence: the output of the floor check, with the count of violations and the count of incomplete items printed apart.

AT-32: The board gives no hint
App: site
Stories: 39
Given: T1 dropped, and the board of AT-22.
When: The reader reads the egg board.
Then: No text, attribute, or link on the board names `/midseason/2026/`, `luck-3`, or any other page or target of an egg.
Evidence: the output of a page script that searches the HTML of the board for each page and target of the test eggs, with 0 matches.

AT-33: A manager finds, cracks, tears, and sees the claim
App: site
Stories: 2, 13, 26
Given: The CPC site and the local API, with T1 dropped.
When: The e2e test of the eggs runs at 375 and 1280 px.
Then: The test finds T1, cracks the egg, tears the stub, and sees the letter of T1 for Lil Fridge on the egg board.
Evidence: the output of the e2e test of the eggs, with the pass count.

AT-34: The egg button and the egg banner do not change
App: site
Stories: none
Given: T1 dropped, with no claim.
When: The reader opens the home page.
Then: The egg button and the egg banner look and read as on `main`.
Evidence: screenshots of the top band and the egg banner on `main` and on the spec branch at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-35: The latest claims and the rules do not change
App: site
Stories: none
Given: The board of AT-22.
When: The reader scrolls under the slider.
Then: The latest claims and how the hunt works look and read as on `main`.
Evidence: screenshots of both sections on `main` and on the spec branch at 375 and 1280 px, each in the light theme and the dark theme.

AT-36: No new dependency and no Scrolltide source
App: site
Stories: none
Given: The spec branch at its head.
When: The reader diffs it against `main`.
Then: No `package.json` adds a dependency, and the diff holds no Scrolltide source.
Evidence: the output of `git diff main -- '**/package.json'`, and the list of files in the diff.

AT-37: The API does not change
App: site
Stories: none
Given: The spec branch at its head.
When: The reader diffs `apps/api` and the API part of the eggs package against `main`.
Then: The diff is empty.
Evidence: the output of the diff command.

AT-38: No egg word gets its own tint
App: site
Stories: none
Given: The board of AT-27.
When: The reader moves through the three slides.
Then: CORNERSTONE and LANSDALE sit on the dark hero ground, and only EAGLES, the won word, is red.
Evidence: screenshots of the three slides at 375 px, in the light theme and the dark theme.

## Trace

Story 1: AT-1
Story 2: AT-2, AT-33
Story 3: AT-3
Story 4: AT-4
Story 5: AT-4
Story 6: AT-5
Story 7: AT-5
Story 8: AT-6
Story 9: AT-7
Story 10: AT-8
Story 11: AT-9
Story 12: AT-10
Story 13: AT-11, AT-33
Story 14: AT-12
Story 15: AT-13
Story 16: AT-14
Story 17: AT-11
Story 18: AT-15
Story 19: AT-16
Story 20: AT-17
Story 21: AT-18
Story 22: AT-19
Story 23: AT-20
Story 24: AT-20
Story 25: AT-20
Story 26: AT-21, AT-33
Story 27: AT-21
Story 28: AT-22
Story 29: AT-23
Story 30: AT-24
Story 31: AT-25
Story 32: AT-26
Story 33: AT-27
Story 34: AT-27
Story 35: AT-28
Story 36: AT-29
Story 37: AT-30
Story 38: AT-31
Story 39: AT-32
Out of scope "The egg button and the egg banner": AT-34
Out of scope "The latest claims and how the hunt works": AT-35
Out of scope "Block Field, Unfurl, Step Path, Particle Text, and Crumple Reveal": AT-36
Out of scope "Any change to the API, the claim rules, the egg drop, or the board answer": AT-37
Out of scope "A tint for each egg word": AT-38
Out of scope "A hero scene on the egg board": AT-20

## Revisions

- 2026-11-09: Brian approved three changes of values after the first evidence round. AT-16: the second browser claims for Teehee, because a second claim for Lil Fridge finds no open slot and gets a 422. AT-25: "Show all 11" and all 11 managers, because the commissioner hunts no eggs. AT-33: the letter of T1, because the e2e test drops T1 into an empty store, where the letter rule gives A.
