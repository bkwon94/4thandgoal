# Easter eggs: acceptance tests

Spec: `.scratch/easter-eggs/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

## The setup of every test

- The API runs on this machine with a temp SQLite file, a test passphrase, and a test commissioner key.
- The tests drop test eggs on the real published CPC 2026 pages: week 8 and `/midseason/2026/`.
- The test egg T1 is a double-tap on the Luck cell of Lil Fridge on `/midseason/2026/`, in the light theme. Its letter is C.
- The repo is public, so no evidence uses a real spot or `~/cpc-eggs/2026.toml`.
- A test labelled `pipeline` covers the Python of the API or the pipeline. Its evidence is the command, such as `curl` to the local API, and its output.

## Tests

AT-1: The egg check matches the test egg
App: pipeline
Stories: 1, 2
Given: T1 dropped, with no claim.
When: POST `/cpc/eggs/check` with the page, the id of the Luck cell of Lil Fridge, the action `tap2`, and the light theme.
Then: The answer holds the letter C and a claim token.
Evidence: the `curl` command and its output.

AT-2: A wrong condition is no match
App: pipeline
Stories: 3
Given: T1 dropped, with no claim.
When: POST the check of AT-1 with the dark theme.
Then: The answer is no match, with no letter and no token.
Evidence: the `curl` command and its output.

AT-3: A clock window holds
App: pipeline
Stories: 6
Given: A test egg T2 with the clock window 11 PM to midnight ET.
When: POST its check at a time outside the window.
Then: The answer is no match. The same check inside the window matches.
Evidence: the test output of both checks, with the time of each.

AT-4: A sim condition holds
App: pipeline
Stories: 4
Given: A test egg T3 on the sim champion trophy, with the condition that the champion is Teehee.
When: POST its check with the champion Lil Fridge, then with the champion Teehee.
Then: The first check is no match. The second check matches.
Evidence: the `curl` commands and their output.

AT-5: A claim counts
App: pipeline
Stories: 15, 16
Given: The token of AT-1.
When: POST `/cpc/eggs/claim` with the token, the roster of Lil Fridge, CORNERSTONE, and the passphrase.
Then: `/cpc/eggs/board` shows Lil Fridge with one C in CORNERSTONE.
Evidence: the claim and board commands and their output.

AT-6: The first claim wins a tie
App: pipeline
Stories: 27, 13
Given: Two tokens of T1 from two checks.
When: Send two claims at once, for Lil Fridge and for Teehee.
Then: One claim wins. The other answers that another manager claimed first.
Evidence: the test output of the two claims and the claims table.

AT-7: The commissioner cannot hunt
App: pipeline
Stories: 17
Given: A token of T1.
When: POST a claim for the roster of Bo Girds.
Then: The API refuses it, and T1 stays live.
Evidence: the `curl` command, its output, and the board after.

AT-8: The claim needs the passphrase
App: pipeline
Stories: 57
Given: A token of T1.
When: POST a claim with no passphrase.
Then: The API answers 401.
Evidence: the `curl` command and its output.

AT-9: A full slot refuses
App: pipeline
Stories: 20
Given: Lil Fridge holds the one C of CORNERSTONE, and a test egg T4 with the letter C.
When: POST a claim of T4 for Lil Fridge into CORNERSTONE.
Then: The API refuses it.
Evidence: the `curl` command and its output.

AT-10: A block counts as found
App: pipeline
Stories: 21, 26, 42, 43
Given: Lil Fridge holds the C of CORNERSTONE and the C of no other egg word, and T4 with the letter C.
When: POST a claim of T4 for Lil Fridge as a block.
Then: The found count of the board rises by 1. The egg word cards and the feed show no block.
Evidence: the board before and after.

AT-11: A block refuses if the letter fits
App: pipeline
Stories: 21
Given: Teehee holds no letter, and a token of T1 with the letter C.
When: POST a claim for Teehee as a block.
Then: The API refuses it, because C fits CORNERSTONE.
Evidence: the `curl` command and its output.

AT-12: A won egg word closes
App: pipeline
Stories: 25, 38
Given: Lil Fridge holds E, A, G, L, and S in EAGLES, and a test egg with the letter E.
When: Lil Fridge claims the E into EAGLES. Teehee then claims another E into EAGLES.
Then: The board names Lil Fridge the winner of EAGLES. The API refuses the claim of Teehee.
Evidence: the claim outputs and the board.

AT-13: The egg check has its own limit
App: pipeline
Stories: 14
Given: No check in the last hour from the test address.
When: Send 61 checks from one address in one hour.
Then: The 61st check answers 429 with a retry-after. The analyze route still answers for the address.
Evidence: the test output with the count and the status of each answer.

AT-14: The drop needs the commissioner key
App: pipeline
Stories: 54
Given: A test drop of one egg.
When: POST `/cpc/eggs/drop` with the passphrase and no commissioner key.
Then: The API answers 401 and drops no egg.
Evidence: the `curl` command, its output, and the board after.

AT-15: The letter rule of the first drop
App: pipeline
Stories: 50, 51
Given: An empty store.
When: Drop six test eggs for week 9.
Then: The six letters are A, C, D, E, G, and L.
Evidence: the drop output.

AT-16: The guard keeps the last letter of a leader
App: pipeline
Stories: 52
Given: Lil Fridge leads EAGLES and needs only an E. E is the letter that the most managers need.
When: Drop six test eggs.
Then: No egg of the drop holds E.
Evidence: the board before and the drop output.

AT-17: The commissioner undoes a claim
App: pipeline
Stories: 53
Given: The claim of AT-5.
When: `make egg-undo CLIENT=cpc EGG=<id of T1>` against the local API.
Then: T1 is live again, the board loses the C of Lil Fridge, and the claims table keeps the claim with its undo time.
Evidence: the command output, the board, and the claims row.

AT-18: The egg board names no spot
App: pipeline
Stories: 40, 54
Given: T1, T2, T3, and T4 dropped, and T1 claimed.
When: GET `/cpc/eggs/board`.
Then: The answer holds no page, no target, no action, and no condition.
Evidence: the full board JSON.

AT-19: The source names no spot
App: pipeline
Stories: 54, 55
Given: The test egg file of these tests, and the built CPC site.
When: Grep the repo and the built site for each page, target, and reason of the test egg file.
Then: The grep finds no reason, and no target that only an egg holds.
Evidence: the grep commands and their output.

AT-20: The draft proposes six spots
App: pipeline
Stories: 44, 45, 46
Given: CPC 2026 week 8 built, and T1 to T4 dropped before.
When: `make egg-draft CLIENT=cpc WEEK=8`, with a temp egg file.
Then: The file holds six spots, each with a reason and marked not confirmed. No spot repeats T1 to T4.
Evidence: the command output and the six spots, with the reasons cut.

AT-21: The publish drops the confirmed eggs only
App: pipeline
Stories: 47
Given: A temp egg file with six spots for week 8, four of them confirmed.
When: Run the drop step of `make publish CLIENT=cpc WEEK=8` against the local API.
Then: The output says 4 eggs dropped, and the board count to find rises by 4.
Evidence: the command output and the board before and after.

AT-22: The publish warns when the API is down
App: pipeline
Stories: 48
Given: The file of AT-21, with the local API stopped.
When: Run the drop step, then start the API and run `make egg-drop CLIENT=cpc WEEK=8`.
Then: The drop step warns and exits 0. `make egg-drop` drops the 4 eggs.
Evidence: the two command outputs and their exit codes.

AT-23: A week with no confirmed eggs
App: pipeline
Stories: 49
Given: A temp egg file with no confirmed spot for week 8.
When: Run the drop step.
Then: The output says that no eggs dropped.
Evidence: the command output.

AT-24: NorCal has no eggs
App: both
Stories: 56
Given: NorCal 2026, built and served on this machine.
When: Run the drop step for NorCal, and open the NorCal home page and `/eggs/`.
Then: The drop step skips. The site has no egg button and no listener, and `/eggs/` is the 404 page.
Evidence: the command output, and screenshots of the home page and `/eggs/` at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-25: A normal tap sends no check
App: site
Stories: 7
Given: CPC 2026 week 8.
When: Tap one game card one time.
Then: The card opens, and the listener sends no check.
Evidence: the test output with the checks sent, and screenshots of the open card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-26: A double-tap sends one check
App: site
Stories: 2
Given: `/midseason/2026/` in the light theme.
When: Tap the Luck cell of Lil Fridge 2 times, the second tap within 400 ms of the first.
Then: The listener sends one check with the page, the id, the action `tap2`, and the light theme.
Evidence: the test output with the body of the check.

AT-27: A long hold sends one check
App: site
Stories: 2
Given: `/midseason/2026/`.
When: Hold the Luck cell of Lil Fridge for 3.5 seconds. Then hold it for 1.5 seconds.
Then: The listener sends one check with the action `hold` for the hold of 3.5 seconds, and no check for the hold of 1.5 seconds.
Evidence: the test output with the body of the check.

AT-28: A tap combo sends one check
App: site
Stories: 2
Given: CPC 2026 week 8.
When: Tap target A, tap target B, then double-tap target C, within 5 seconds.
Then: The listener sends one check with the action 2 taps on C and the trail A, B.
Evidence: the test output with the body of the check.

AT-29: A selected word sends one check
App: site
Stories: 2
Given: A blurb of `/midseason/2026/`.
When: Select one whole word of the blurb.
Then: The listener sends one check with the word and the id of the blurb.
Evidence: the test output with the body of the check.

AT-30: The count by id holds across sim frames
App: site
Stories: 9
Given: The sim replay of `/midseason/2026/#sim` as it runs.
When: Tap one standings row 2 times as the frame changes.
Then: The listener sends one check with the action `tap2`.
Evidence: the test output with the frame changes and the check.

AT-31: The iOS callout is off on targets only
App: site
Stories: 8
Given: `/midseason/2026/`.
When: Read the callout style of the Luck cell, of a link, and of an image.
Then: The callout is off on the Luck cell and on for the link and the image.
Evidence: the test output with the style of each element.

AT-32: The find shows the egg and its letter
App: site
Stories: 10, 11, 12
Given: T1 dropped, on `/midseason/2026/` in the light theme.
When: Tap the Luck cell of Lil Fridge 3 times, then tap the egg.
Then: The page blurs, the ring and the egg show, the egg cracks, and the red C tile springs up.
Evidence: screenshots of the egg and of the C tile at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-33: The team pills omit the commissioner
App: site
Stories: 16, 17
Given: The C tile of AT-32.
When: Tap "Claim C".
Then: The sheet shows 11 team pills, and Bo Girds is not one of them.
Evidence: screenshots of the sheet at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-34: The egg word cards of the claim
App: site
Stories: 18, 19, 20
Given: The sheet of AT-33, with Teehee holding the C of CORNERSTONE, and no C in the other egg words.
When: Pick Teehee.
Then: CORNERSTONE is faded and disabled. A ghost tile pulses in its C slot only on a word with an open slot.
Evidence: screenshots of step 2 at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-35: The block notice
App: site
Stories: 21
Given: The sheet of AT-33, and a manager with no open slot for C in any egg word.
When: Pick that manager.
Then: A dashed notice offers a block.
Evidence: screenshots of the notice at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-36: The passphrase field shows only when needed
App: site
Stories: 22, 23
Given: The sheet of AT-33, first with no passphrase in the browser, then with one.
When: Pick Lil Fridge and CORNERSTONE.
Then: With no passphrase, the field shows and the button names it. With one, the field is gone.
Evidence: screenshots of both states at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-37: The claim hero card
App: site
Stories: 24, 25
Given: The sheet of AT-36, with a passphrase.
When: Claim C for Lil Fridge into CORNERSTONE.
Then: The hero card shows the count rise and the C tile in its slot. A claim that fills an egg word says the gift card is the manager's.
Evidence: screenshots of both hero cards at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-38: Another manager claimed first
App: site
Stories: 13
Given: T1 claimed by Teehee.
When: Find T1 again.
Then: The hero card says that another manager claimed first.
Evidence: screenshots of the hero card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-39: The limit hero card
App: site
Stories: 14
Given: The limit of the egg check hit for the address.
When: Tap the Luck cell of Lil Fridge 3 times.
Then: The card reads "The eggs need a rest. Try again in N minutes." with a real N.
Evidence: screenshots of the card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-40: The egg button is on every page
App: site
Stories: 28, 29
Given: Six test eggs dropped, none claimed.
When: Open the home page, week 8, and `/midseason/2026/`, then tap the egg button.
Then: Each top band shows the egg button with the badge 6. The tap opens `/eggs/`.
Evidence: screenshots of the three top bands at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-41: The egg banner
App: site
Stories: 30, 31, 32
Given: Six test eggs dropped for week 9, none claimed.
When: Open the home page on the Tuesday of the drop. Open it again on Wednesday, after one claim. Hide the banner, and reload.
Then: On Tuesday the banner reads "6 eggs dropped today · 6 left". On Wednesday it reads "6 eggs dropped Tue · 5 left". It links to `/eggs/`, and after the reload it stays hidden.
Evidence: screenshots before and after at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-42: The hero of the egg board
App: site
Stories: 33, 34, 35
Given: Six eggs dropped for week 9, two of them claimed.
When: Open `/eggs/`.
Then: The counts are 4 left to find, 2 found, and 48 to drop. The grid shows 2 white, 4 red, and 48 dashed slots.
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-43: The egg word cards of the board
App: site
Stories: 36, 37
Given: The state of AT-42, with letters for seven managers.
When: Tap "Show all 11" on the CORNERSTONE card.
Then: The cards show $50, $30, and $20 and the top 5 of each egg word. The tap shows all 11 managers.
Evidence: screenshots before and after at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-44: A won egg word
App: site
Stories: 38
Given: The state of AT-12, with EAGLES won by Lil Fridge.
When: Open `/eggs/`.
Then: EAGLES is a hero card with a WON stamp and Lil Fridge.
Evidence: screenshots of the card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-45: Latest claims
App: site
Stories: 39, 40, 42
Given: Two claims and one block.
When: Open `/eggs/`.
Then: The feed shows two rows, each with the manager, the letter, and the egg word. It shows no page, no spot, and no block.
Evidence: screenshots of the feed at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-46: How the hunt works
App: site
Stories: 41
Given: `/eggs/`.
When: Read the last card.
Then: It states the egg drop each Tuesday, the claim, the letter rule, the gift cards, and that the commissioner cannot hunt.
Evidence: screenshots of the card at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-47: Nothing of the hunt shows before the first drop
App: site
Stories: 28, 30
Given: An empty store.
When: Open the home page, week 8, and `/eggs/`, and double-tap the Luck cell of Lil Fridge on `/midseason/2026/`.
Then: No page shows the egg button or the egg banner, the listener sends no check, and `/eggs/` shows the 404 page.
Evidence: screenshots of the home page, week 8, and `/eggs/` at 375, 768, and 1280 px, each in the light theme and the dark theme, and the log of the checks sent.

AT-48: The copy rules hold
App: site
Stories: none
Given: The site part of `eggs`.
When: Grep its copy for "rival", for "Brian", and for the name of a page or a spot.
Then: The grep finds none.
Evidence: the grep commands and their output.

AT-49: Reduced motion
App: site
Stories: 10, 12
Given: T1 dropped, with reduced motion on.
When: Find T1 and tap the egg.
Then: The C tile shows with no motion.
Evidence: screenshots of the tile at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-50: The readability floor holds
App: site
Stories: none
Given: `/eggs/`, the claim sheet, and the egg banner.
When: Run the floor check of ADR 0025.
Then: Each one passes.
Evidence: the output of the floor check.

AT-51: The whole flow, end to end
App: both
Stories: 1, 15, 24, 39
Given: The built CPC site and the local API, with T1 dropped.
When: Find T1, claim C for Lil Fridge into CORNERSTONE, and open `/eggs/`.
Then: The egg board shows the C of Lil Fridge in CORNERSTONE and the claim in the feed.
Evidence: the Playwright output, and screenshots of each step at 375 and 1280 px, each in the light theme and the dark theme.

AT-52: A touch hold sends its check when the browser fires the menu event
App: site
Stories: 2, 8
Given: `/midseason/2026/`, with the listener on.
When: Press the Luck cell of Lil Fridge with a touch for 2.2 seconds, and fire `contextmenu` during the press, as Android Chrome does. Then fire `contextmenu` on a mouse right-click of the cell, on a link, and on an image.
Then: The listener blocks the menu of the touch press and sends one check with the action `hold`. The right-click, the link, and the image keep the menu.
Evidence: the test output with the check sent and the blocked state of each menu event.

AT-53: A 404 egg matches on any missing URL
App: pipeline
Stories: 6
Given: A test egg on the 404 hero with the action `tap2` and the condition `not_found = true`, dropped with the page `/golden-egg/`.
When: POST its check with `not_found` true from `/golden-egg`, `/no-such-page/`, and `/2026/week-99`. Then POST the check from `/golden-egg/` with no `not_found`.
Then: Each 404 check matches. The check with no `not_found` is no match. The drop answers the page `*404` for the egg.
Evidence: the test output of each check and of the drop.

AT-54: A two-team egg matches any trade between its two teams
App: both
Stories: 5
Given: A test egg on the verdict word of `/analyzer/` with the action `tap2` and the condition `trade_teams` of The Blue Tent and Lil Fridge, roster ids 1 and 3.
When: Double-tap the verdict word of a graded trade, and read the check that the listener sends. Then POST the check with the teams 1 and 3, with 3 and 1, with 1 and 12, and with 1, 3, and 12.
Then: The listener sends `trade_teams`, the two roster ids of the trade, smallest first, and no `trade`. The checks with 1 and 3 in either order match. The other two checks are no match. The drop refuses the old `trade` condition.
Evidence: the test output with the body of the check from the listener, and the output of each API check and of the refused drop.

AT-55: A burst of 3 or more taps sends nothing
App: both
Stories: 2
Given: `/midseason/2026/`.
When: Tap the Luck cell of Lil Fridge 3 times, each tap within 400 ms of the one before. Then tap another cell 5 times.
Then: The listener sends no check. The drop refuses the actions `tap3`, `tap5`, `hold1`, `hold3`, and `hold5`.
Evidence: the test output with the checks sent, and the output of each refused drop.

AT-56: A blurb takes a double-tap egg and refuses a hold egg
App: both
Stories: 2
Given: A page with the listener on and a blurb with the stable id `blurb-luck`.
When: Double-tap two places in the blurb. Then draft a spot with the action `hold` on the target `blurb-luck`, and drop an egg with the same spot.
Then: The listener sends one check `tap2` with the target `blurb-luck` for each double-tap. The draft writes nothing and names the spot. The drop answers 422 and stores no egg. A `tap2` egg on `blurb-luck` drops.
Evidence: the test output of the listener, the draft, and the drop.

## Trace

Story 1: AT-1, AT-51
Story 2: AT-1, AT-26, AT-27, AT-28, AT-29, AT-52, AT-55, AT-56
Story 3: AT-2
Story 4: AT-4
Story 5: AT-54
Story 6: AT-3, AT-53
Story 7: AT-25
Story 8: AT-31, AT-52
Story 9: AT-30
Story 10: AT-32, AT-49
Story 11: AT-32
Story 12: AT-32, AT-49
Story 13: AT-6, AT-38
Story 14: AT-13, AT-39
Story 15: AT-5, AT-51
Story 16: AT-5, AT-33
Story 17: AT-7, AT-33
Story 18: AT-34
Story 19: AT-34
Story 20: AT-9, AT-34
Story 21: AT-10, AT-11, AT-35
Story 22: AT-36
Story 23: AT-36
Story 24: AT-37, AT-51
Story 25: AT-12, AT-37
Story 26: AT-10
Story 27: AT-6
Story 28: AT-40, AT-47
Story 29: AT-40
Story 30: AT-41, AT-47
Story 31: AT-41
Story 32: AT-41
Story 33: AT-42
Story 34: AT-42
Story 35: AT-42
Story 36: AT-43
Story 37: AT-43
Story 38: AT-12, AT-44
Story 39: AT-45, AT-51
Story 40: AT-18, AT-45
Story 41: AT-46
Story 42: AT-10, AT-45
Story 43: AT-10
Story 44: AT-20
Story 45: AT-20
Story 46: AT-20
Story 47: AT-21
Story 48: AT-22
Story 49: AT-23
Story 50: AT-15
Story 51: AT-15
Story 52: AT-16
Story 53: AT-17
Story 54: AT-14, AT-18, AT-19
Story 55: AT-19
Story 56: AT-24
Story 57: AT-8
Out of scope "A hint of any kind": AT-18, AT-48
Out of scope "Eggs for norcal or any other client": AT-24
Out of scope "A login, a PIN, or Google sign-in": AT-33
Out of scope "A riddle, an answer box, or any typed answer": AT-48

## Revisions

- 2026-11-06: AT-41 names the day of the drop, because the banner stays up all week and "6 new eggs" read as eggs of that day. Brian approved.
- 2026-11-07: AT-47 tests that nothing of the hunt shows before the first drop, because the hunt turns on at the first drop (Brian chose the automatic flag). Brian approved.
- 2026-11-07: Brian tested the hunt by hand and changed the catalog (decision tickets 01 and 10, revised 2026-11-07). T1, AT-1, AT-26, AT-30, and AT-47 use a double-tap, because the actions `tap3` to `tap5` are gone. AT-27 tests the one action `hold` of 2 seconds or more, and no check for a press of 1.5 seconds. AT-52 tests the hold of a touch press on Android Chrome, which fires `contextmenu`. AT-53 tests a 404 egg on any missing URL. AT-54 tests a two-team analyzer egg and covers story 5. AT-55 tests that a burst of 3 or more taps sends nothing. Brian decided each change. He reviews the new test text in the PR.
- 2026-11-07: Brian decided that a hold egg never goes on a blurb, because on Android a long press on text selects a word. A blurb may take a double-tap egg. AT-56 tests the double-tap on a blurb and the refusal of a hold on a blurb by the draft and the drop. Brian reviews the new test text in the PR.
