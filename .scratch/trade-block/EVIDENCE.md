# Trade block: evidence

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests: `.scratch/trade-block/ACCEPTANCE.md`.
Built from: `3dd395a0`, on 2026-11-21. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 13 min for 13 site tests.

Smoke run: `Smoke run: 7 flows, 7 passed, 0 failed` (`evidence/smoke/`).

Stand-ins, per the Revisions line of `ACCEPTANCE.md`, approved by Brian: Cam Skattebo (12481) stands in for Kenneth Walker III, who is Out with no return week on the week 11 data. Kirk Cousins (1166) stands in for Lamar Jackson, who left the roster of Bo Girds. Each press ran on the local evidence API, never on Fly. `evidence/scripts/setup.txt` says how each site file was made.

## AT-1: Each offer sends a block player

App: pipeline
Then: Each offer sends Walker, Flowers, or both on the side of Bo Girds.
Files: `evidence/AT-1/output.txt`, `evidence/scripts/live_block_search.py`
Observation: Walker is Out with no return week on the live week 11 `cpc` snapshot, so Cam Skattebo stands in for him (Revisions line). The search with the block Skattebo and Flowers gives 3237 offers: 1398 send Skattebo only, 1400 send Flowers only, 439 send both, and 0 send neither, each from roster 6. The unit test prints "1648 offers, each sends Collins, Williams, or both".

## AT-2: Two block players both reach the Shortlist

App: pipeline
Then: The Shortlist holds at least one offer that sends Walker and at least one offer that sends Flowers.
Files: `evidence/AT-2/output.txt`, `evidence/scripts/live_block_search.py`
Observation: With Cam Skattebo as the stand-in for Walker, the fixed Jev keeps 1837 fair offers that send Skattebo and 1839 that send Flowers. The Shortlist of 10 has 5 offers that send Skattebo and 6 that send Flowers, and the unit test prints a Shortlist with offers of both Collins (7569) and Williams (8148).

## AT-3: A package of two block players counts

App: pipeline
Then: An offer that sends Walker and Flowers together passes the block rule.
Files: `evidence/AT-3/output.txt`, `evidence/scripts/live_block_search.py`
Observation: With Cam Skattebo as the stand-in for Walker, the Value screen gives 3237 offers, and 439 send Skattebo and Flowers together, each with `_sends_block=True`, such as `6:12481+9997-1:8167` for Christian Watson. The unit test prints "313 offers send Collins and Williams together".

## AT-4: A block player who fails the pool gives no error

App: pipeline
Then: The search raises no error, no offer sends the handcuff, and offers that send Walker remain.
Files: `evidence/AT-4/output.txt`, `evidence/scripts/live_block_search.py`
Observation: Roster 6 has no handcuff on the live snapshot, so the player who fails the pool rules is Walker himself: Out, no return week, `in_pool=False`. Cam Skattebo stands in for Walker as the second block player. The search with Walker and Skattebo raises no error and gives 1837 offers: 0 send Walker and 1837 send Skattebo. The two unit tests of a block player who fails the pool rules also run on the test fixture.

## AT-5: An empty block changes nothing

App: pipeline
Then: Both runs give the same offers in the same order.
Files: `evidence/AT-5/output.txt`, `evidence/scripts/live_block_search.py`
Observation: On the live snapshot, the run with `trade_block=[]` and the run with no block each give 5658 offers and a Shortlist of 10. The script prints "Same offers in the same order: True" and "Same Shortlist in the same order: True", with the first 10 offers and the Shortlist side by side.

## AT-6: The route rejects a bad block

App: api
Then: Each request gets a 422 with a plain reason.
Files: `evidence/AT-6/output.txt`
Observation: The three cases on the test client print "four: 422 Your trade block holds at most 3 players.", "repeat: 422 Your trade block names one player twice.", and "other: 422 Your trade block holds a player who is not on your roster.".

## AT-7: A block search never serves the plain cache

App: api
Then: The key with Walker differs from the key with no block, and the two orders give one key.
Files: `evidence/AT-7/output.txt`, `evidence/scripts/live_block_search.py`
Observation: On the live snapshot for roster 6, with Cam Skattebo as the stand-in for Walker, the keys with no block and with `trade_block=[]` are both `d1f570f4…`, and the key with Skattebo is `52880e0f…`. The keys of [Skattebo, Flowers] and [Flowers, Skattebo] are both `a1143bfb…`, and the unit test prints a plain key `174ea9318324` and a block key `55d034d42d08`.

## AT-8: A block press uses the Fair cache

App: api
Then: The press makes 0 new fair asks.
Files: `evidence/AT-8/api.log.txt`, `evidence/AT-8/round-api.log.txt`
Observation: Cam Skattebo stands in for Walker. After the warm-up line (line 573 of the API log), the Skattebo press with Every team (line 619) logs `Finder Value offers of Bo Girds: 1837` and `Finder fair answers of Bo Girds: 3674 questions, 3674 from the cache, 0 asked live`; the runner's own API serves the same request from its stored result, with `claude_calls=0`.

## AT-9: The pick hears the block

App: pipeline
Then: The message names Walker and Flowers as the Trade block, and the prompt holds the rule that a block player with a fair Shortlist offer gets at least one pick.
Files: `evidence/AT-9/output.txt`, `evidence/scripts/live_block_search.py`
Observation: With Cam Skattebo as the stand-in for Walker, the user message of the pick has the line "The Trade block: Cam Skattebo and Zay Flowers." after the asker line. The system prompt holds "When the list holds a fair offer for a block player, at least one pick sends him.", and the script prints True for it.

## AT-10: A press around Walker

App: both
Then: Each card sends Walker.
Files: `evidence/AT-10/find-iphone-390x660.json`, `evidence/AT-10/find-stream-iphone-390x660.txt`, `evidence/AT-10/find.json`, `evidence/AT-10/steps.json`, `evidence/AT-10/steps.txt`, `evidence/AT-10/1280-dark.png`, `evidence/AT-10/1280-light.png`, `evidence/AT-10/375-dark.png`, `evidence/AT-10/375-light.png`, `evidence/AT-10/768-dark.png`, `evidence/AT-10/768-light.png`, `evidence/AT-10/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. The request is `{"season":2026,"asker":6,"trade_block":["12481"]}`, and `find.json` and each shot have 1 card, in which Bo Girds gives Cam Skattebo alone to Unsolicited Dak Picks for Caleb Douglas, Tank Dell, and C.J. Stroud.

### AT-10 extra press: Walker alone (story 21)

Files: `evidence/AT-10/walker/api.log.txt`, `evidence/AT-10/walker/find-1280-light.json`, `evidence/AT-10/walker/find-iphone-390x660.json`, `evidence/AT-10/walker/find-stream-1280-light.txt`, `evidence/AT-10/walker/find-stream-iphone-390x660.txt`, `evidence/AT-10/walker/find.json`, `evidence/AT-10/walker/steps.json`, `evidence/AT-10/walker/steps.txt`, `evidence/AT-10/walker/1280-dark.png`, `evidence/AT-10/walker/1280-light.png`, `evidence/AT-10/walker/375-dark.png`, `evidence/AT-10/walker/375-light.png`, `evidence/AT-10/walker/768-dark.png`, `evidence/AT-10/walker/768-light.png`, `evidence/AT-10/walker/iphone-390x660-light.png`
Observation: With Kenneth Walker III alone on the block, the API logs `Finder Value offers of Bo Girds: 0` and `0 questions, 0 from the cache, 0 asked live`, and the press ends with no error and `claude_calls=0`. `find.json` has 0 trades, and each shot shows Walker ringed and the line "No fair trade sends Walker with the partner and the position you picked."

## AT-11: The cards spread across two block players

App: both
Then: Each of Walker and Flowers that has a fair offer on the Shortlist is sent by at least one card.
Files: `evidence/AT-11/api-shortlist.txt`, `evidence/AT-11/api.log.txt`, `evidence/AT-11/find-iphone-390x660.json`, `evidence/AT-11/find-stream-iphone-390x660.txt`, `evidence/AT-11/find.json`, `evidence/AT-11/steps.json`, `evidence/AT-11/steps.txt`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. `api-shortlist.txt` has 1 `Finder shortlist` line, `6:12481-11:13296+9502+9758`, which sends Skattebo; no Shortlist line sends Flowers (9997), and 183 offers end in a gain drop. `find.json` and each shot have 1 card, which sends Cam Skattebo.

## AT-12: The block with one partner

App: both
Then: Each card has that partner and sends Walker, or the empty line shows.
Files: `evidence/AT-12/api.log.txt`, `evidence/AT-12/find-iphone-390x660.json`, `evidence/AT-12/find-stream-iphone-390x660.txt`, `evidence/AT-12/find.json`, `evidence/AT-12/steps.json`, `evidence/AT-12/steps.txt`, `evidence/AT-12/1280-dark.png`, `evidence/AT-12/1280-light.png`, `evidence/AT-12/375-dark.png`, `evidence/AT-12/375-light.png`, `evidence/AT-12/768-dark.png`, `evidence/AT-12/768-light.png`, `evidence/AT-12/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker, and the partner is Lil Fridge (roster 3): the request is `{"season":2026,"asker":6,"partner":3,"trade_block":["12481"]}`. `find.json` has 0 trades, and each shot shows Trade with "Lil Fridge", no card, and "No fair trade sends Skattebo with the partner and the position you picked."

## AT-13: The block with the RB chip

App: both
Then: Each card sends Flowers and gets at least one RB, or the empty line shows.
Files: `evidence/AT-13/api.log.txt`, `evidence/AT-13/find-iphone-390x660.json`, `evidence/AT-13/find-stream-iphone-390x660.txt`, `evidence/AT-13/find.json`, `evidence/AT-13/steps.json`, `evidence/AT-13/steps.txt`, `evidence/AT-13/1280-dark.png`, `evidence/AT-13/1280-light.png`, `evidence/AT-13/375-dark.png`, `evidence/AT-13/375-light.png`, `evidence/AT-13/768-dark.png`, `evidence/AT-13/768-light.png`, `evidence/AT-13/iphone-390x660-light.png`
Observation: The request carries `"limit":{"aim_position":"RB"}` and `"trade_block":["9997"]`; the log shows 1187 Value offers, 121 after step 2, and no Shortlist line. `find.json` has 0 trades, and each shot shows the chip RB, no card, and "No fair trade sends Flowers with the partner and the position you picked."

## AT-14: The empty answer names the block

App: both
Then: The page shows no card and the line "No fair trade sends Walker or Flowers with the partner and the position you picked.", with the names of the block.
Files: `evidence/AT-14/api.log.txt`, `evidence/AT-14/find-iphone-390x660.json`, `evidence/AT-14/find-stream-iphone-390x660.txt`, `evidence/AT-14/find.json`, `evidence/AT-14/probe-api.log.txt`, `evidence/AT-14/probe-stream.txt`, `evidence/AT-14/steps.json`, `evidence/AT-14/steps.txt`, `evidence/AT-14/1280-dark.png`, `evidence/AT-14/1280-light.png`, `evidence/AT-14/375-dark.png`, `evidence/AT-14/375-light.png`, `evidence/AT-14/768-dark.png`, `evidence/AT-14/768-light.png`, `evidence/AT-14/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker; the partner is behold the lamb (its only QB is Jayden Daniels) and the chip is QB, picked by one probe POST that logs 81 Value offers and a gain drop of each offer after step 2. `find.json` has 0 trades, and each shot shows no card and "No fair trade sends Skattebo or Flowers with the partner and the position you picked."

## AT-15: The strip lists QB, RB, WR, and TE only

App: site
Then: The strip shows the QB, RB, WR, and TE of Bo Girds, in that position order and then by name, each with the headshot, the last name, and the position, and no kicker and no defense.
Files: `evidence/AT-15/steps.json`, `evidence/AT-15/steps.txt`, `evidence/AT-15/teams.json`, `evidence/AT-15/1280-dark.png`, `evidence/AT-15/1280-light.png`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/375-light.png`, `evidence/AT-15/768-dark.png`, `evidence/AT-15/768-light.png`, `evidence/AT-15/iphone-390x660-light.png`
Observation: `teams.json` gives Bo Girds 14 players, one of them the Los Angeles Chargers DEF. The shots show headshots with a last name and a position, from Mendoza and Cousins (QB) to Corum, Skattebo, Walker, Spears, Knight (RB), then WR; `AT-31/strip-ids.txt` lists 13 toggles, 2 QB, 5 RB, 5 WR, McBride TE last, and no DEF, each position sorted by full name.

## AT-16: A tap puts a player on the block

App: site
Then: Walker shows a red ring and a check at the front of the strip, and the counter reads "1 of 3".
Files: `evidence/AT-16/steps.json`, `evidence/AT-16/steps.txt`, `evidence/AT-16/after-1280-dark.png`, `evidence/AT-16/after-1280-light.png`, `evidence/AT-16/after-375-dark.png`, `evidence/AT-16/after-375-light.png`, `evidence/AT-16/after-768-dark.png`, `evidence/AT-16/after-768-light.png`, `evidence/AT-16/after-iphone-390x660-light.png`, `evidence/AT-16/before-1280-dark.png`, `evidence/AT-16/before-1280-light.png`, `evidence/AT-16/before-375-dark.png`, `evidence/AT-16/before-375-light.png`, `evidence/AT-16/before-768-dark.png`, `evidence/AT-16/before-768-light.png`, `evidence/AT-16/before-iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. The before shots show "0 of 3" with Skattebo fourth after Mendoza, Cousins, and Corum; the after shots show Skattebo first, with a red ring and a red check badge, and "1 of 3".

## AT-17: A tap on a pick takes it off

App: site
Then: Walker has no ring, he is back in his roster place, and the counter reads "0 of 3".
Files: `evidence/AT-17/steps.json`, `evidence/AT-17/steps.txt`, `evidence/AT-17/1280-dark.png`, `evidence/AT-17/1280-light.png`, `evidence/AT-17/375-dark.png`, `evidence/AT-17/375-light.png`, `evidence/AT-17/768-dark.png`, `evidence/AT-17/768-light.png`, `evidence/AT-17/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. After the second tap, each shot shows "0 of 3", the empty block line, and no ring, with Skattebo back in fourth place between Corum and Walker.

## AT-18: A 4th tap is blocked

App: site
Then: No player is added, the strip scrolls back to the 3 picks, and the line "Your block holds 3 players. Take one off to add another." shows.
Files: `evidence/AT-18/playwright.txt`, `evidence/AT-18/steps.txt`, `evidence/AT-18/after-1280-dark.png`, `evidence/AT-18/after-1280-light.png`, `evidence/AT-18/after-375-dark.png`, `evidence/AT-18/after-375-light.png`, `evidence/AT-18/after-768-dark.png`, `evidence/AT-18/after-768-light.png`, `evidence/AT-18/after-iphone-390x660-light.png`, `evidence/AT-18/end-1280-dark.png`, `evidence/AT-18/end-1280-light.png`, `evidence/AT-18/end-375-dark.png`, `evidence/AT-18/end-375-light.png`, `evidence/AT-18/end-768-dark.png`, `evidence/AT-18/end-768-light.png`, `evidence/AT-18/end-iphone-390x660-light.png`
Observation: Skattebo stands in for Walker and Kirk Cousins for Jackson; Cousins, a QB, sits right after the 3 picks. With Skattebo, Flowers, and Corum ringed, the end shots show the strip at its end (scrollLeft 635, 370, 290, and 620 on the iPhone); after a DOM click on Cousins with no scroll first, `steps.txt` logs scrollLeft 0, the same 3 picks, "3 of 3", and the full-block line, and the after shots show the picks at the front, Cousins with no ring, and that line.

## AT-19: The full block label

App: site
Then: The label reads "Trade block · tap a pick to take it off" and the counter reads "3 of 3".
Files: `evidence/AT-19/steps.json`, `evidence/AT-19/steps.txt`, `evidence/AT-19/1280-dark.png`, `evidence/AT-19/1280-light.png`, `evidence/AT-19/375-dark.png`, `evidence/AT-19/375-light.png`, `evidence/AT-19/768-dark.png`, `evidence/AT-19/768-light.png`, `evidence/AT-19/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. Each shot shows "TRADE BLOCK · TAP A PICK TO TAKE IT OFF" in caps, as the label styles it, and "3 of 3" in a filled pill, with Skattebo, Flowers, and Corum ringed at the front.

## AT-20: The empty block line

App: site
Then: The line "No one on the block. The search can offer any of your players." shows.
Files: `evidence/AT-20/steps.json`, `evidence/AT-20/steps.txt`, `evidence/AT-20/1280-dark.png`, `evidence/AT-20/1280-light.png`, `evidence/AT-20/375-dark.png`, `evidence/AT-20/375-light.png`, `evidence/AT-20/768-dark.png`, `evidence/AT-20/768-light.png`, `evidence/AT-20/iphone-390x660-light.png`
Observation: Each shot shows "0 of 3" and the line "No one on the block. The search can offer any of your players." under the strip.

## AT-21: A team change clears the block

App: site
Then: The block is empty, the counter reads "0 of 3", and the strip shows the roster of the new team.
Files: `evidence/AT-21/steps.json`, `evidence/AT-21/steps.txt`, `evidence/AT-21/1280-dark.png`, `evidence/AT-21/1280-light.png`, `evidence/AT-21/375-dark.png`, `evidence/AT-21/375-light.png`, `evidence/AT-21/768-dark.png`, `evidence/AT-21/768-light.png`, `evidence/AT-21/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. The steps tap Skattebo, then change Your team to Lil Fridge; each shot shows Your team "Lil Fridge", "0 of 3", the empty block line, and a strip of Lil Fridge players (Young, Williams QB, McCaffrey, Henry, and on), with no ring.

## AT-22: A partner or chip change keeps the block

App: site
Then: Walker and Flowers stay on the block after each change.
Files: `evidence/AT-22/steps.json`, `evidence/AT-22/steps.txt`, `evidence/AT-22/vitest.txt`, `evidence/AT-22/1280-dark.png`, `evidence/AT-22/1280-light.png`, `evidence/AT-22/375-dark.png`, `evidence/AT-22/375-light.png`, `evidence/AT-22/768-dark.png`, `evidence/AT-22/768-light.png`, `evidence/AT-22/iphone-390x660-light.png`
Observation: The Vitest output lists "clears the block on a change of Your team, and keeps it on a change of the partner or the chip" with a check mark, 56 tests, exit code 0; that test uses the fixed Walker data of the test file. The shots, with Cam Skattebo in place of Walker, show the state after the second change only: Trade with "Lil Fridge", the chip RB, Skattebo and Flowers ringed at the front, and "2 of 3".

## AT-23: The strip locks during a find

App: site
Then: The block stays Walker alone.
Files: `evidence/AT-23/vitest.txt`
Observation: The Vitest output lists "locks the strip during a find, so a tap there changes nothing" with a check mark, exit code 0. That test, on the fixed Walker data of the test file, removes the strip while the find runs, so no toggle takes a tap, and after the answer the only pressed toggle is "Kenneth Walker III, RB" (`trade-block.test.tsx` lines 205 to 215).

## AT-24: Motion off

App: site
Then: Walker is at the front of the strip at once, with no motion frame between.
Files: `evidence/AT-24/frames.txt`, `evidence/AT-24/playwright.txt`, `evidence/AT-24/steps.txt`
Observation: Cam Skattebo stands in for Walker. With reduced motion on, iPhone WebKit shows Skattebo at x=257 before the tap and at x=41, the front of the strip, from the first frame (7 ms) and on each frame for 300 ms; Chromium 1280x800 shows x=537, then x=321, the front, from the first frame (5 ms) on.

## AT-25: Screen reader

App: site
Then: Each item is a toggle named with the player name and the position, Walker has the pressed state, and the others do not.
Files: `evidence/AT-25/a11y.txt`, `evidence/AT-25/playwright.txt`
Observation: Cam Skattebo stands in for Walker. The aria snapshot shows `group "Trade block"` with 13 buttons, each named "<name>, <position>", such as "Cam Skattebo, RB"; only Skattebo has `[pressed]`, and the attribute list gives `aria-pressed=true` for him and `aria-pressed=false` for the other 12.

## AT-26: Keyboard

App: site
Then: Flowers is on the block.
Files: `evidence/AT-26/keys.txt`, `evidence/AT-26/playwright.txt`, `evidence/AT-26/steps.txt`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/375-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/iphone-390x660-light.png`
Observation: At each of the 7 sizes, Tab from Your team lands on "Fernando Mendoza, QB" in the group "Trade block", ArrowRight moves through each player to "Zay Flowers, WR", and after Space the log reads `pressed=["Zay Flowers, WR"]`, `counter="1 of 3"`, with the focus on Flowers. The shots show Flowers ringed at the front with a focus ring and "1 of 3"; the real site ran on the live roster, and the spec `trade-block.spec.ts` was not run.

## AT-27: It fits on each screen

App: site
Then: No text box overlaps another, no fixed bar covers content, and the strip fills the width of the hero.
Files: `evidence/AT-27/fit.txt`, `evidence/AT-27/playwright.txt`, `evidence/AT-27/steps.txt`, `evidence/AT-27/desktop-1280x800-dark.png`, `evidence/AT-27/desktop-1280x800-light.png`, `evidence/AT-27/ipad-1080x740-dark.png`, `evidence/AT-27/ipad-1080x740-light.png`, `evidence/AT-27/ipad-810x980-dark.png`, `evidence/AT-27/ipad-810x980-light.png`, `evidence/AT-27/iphone-390x660-dark.png`, `evidence/AT-27/iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. At each of the 4 sizes in light and dark, `fit.txt` gives `overlap: none`, scrollWidth equal to innerWidth, and strip edges equal to the inner edges of the hero (left gap 0, right gap 0), such as 17 to 373 on the iPhone; the only fixed part on screen is `header`, and it covers none of the strip, the chips, or the find button. The shots show Skattebo and Flowers ringed with "2 of 3"; the real site ran on the live roster, and `playwright.txt` has no test named "none".

## AT-28: The "gives" ask uses the block

App: api
Then: The find request carries `trade_block` with the id of Walker and no anchor.
Files: `evidence/AT-28/output.txt`
Observation: The ask "What can I get for Walker?" as Bo Girds gives the find request `{"season":2026,"asker":6,"partner":null,"limit":null,"trade_block":["8151"]}`, with no `anchor` key. The test runs on the fixture of the test client, not on the live snapshot, so it keeps Walker and no stand-in applies.

## AT-29: The "gets" ask is unchanged

App: api
Then: The find request carries the anchor of Bijan Robinson with the side "gets" and no `trade_block`.
Files: `evidence/AT-29/output.txt`
Observation: The ask "How do I get Bijan Robinson?" as Bo Girds gives the find request `{"season":2026,"asker":6,"partner":7,"anchor":{"player_id":"9509","side":"gets"},"limit":null}`, with no `trade_block` key.

## AT-30: No "anchor" on the page

App: site
Then: No copy that a reader sees says "anchor".
Files: `evidence/AT-30/output.txt`
Observation: The search of the HTML and TXT files of the cpc export of 3dd395a0 matches no line, and the source search finds only code comments, a `data-mesh-anchor` attribute, and an `anchor` prop of the tour. The rendered-text search of Find mode, with Skattebo and Flowers on the block before and after a press, finds no line with "anchor" in the page text or in any aria-label, title, placeholder, or alt.

## AT-31: Out of scope: no other roster on the strip

App: site
Then: Each player on the strip is on the roster of Bo Girds in `/teams`.
Files: `evidence/AT-31/playwright.txt`, `evidence/AT-31/steps.json`, `evidence/AT-31/steps.txt`, `evidence/AT-31/strip-ids.txt`, `evidence/AT-31/teams.json`, `evidence/AT-31/end-1280-dark.png`, `evidence/AT-31/end-1280-light.png`, `evidence/AT-31/end-375-dark.png`, `evidence/AT-31/end-375-light.png`, `evidence/AT-31/end-768-dark.png`, `evidence/AT-31/end-768-light.png`, `evidence/AT-31/end-iphone-390x660-light.png`, `evidence/AT-31/start-1280-dark.png`, `evidence/AT-31/start-1280-light.png`, `evidence/AT-31/start-375-dark.png`, `evidence/AT-31/start-375-light.png`, `evidence/AT-31/start-768-dark.png`, `evidence/AT-31/start-768-light.png`, `evidence/AT-31/start-iphone-390x660-light.png`
Observation: The strip has 13 toggles, and the player id in each headshot URL, such as `players/12481.jpg`, matches a player of Bo Girds (roster 6) in `teams.json`, with no other roster that holds him. The start shots show the first items, and the end shots show the strip scrolled to Golden, Washington, Flowers, and McBride.

## AT-32: Out of scope: no stored block

App: site
Then: The block is empty.
Files: `evidence/AT-32/playwright.txt`, `evidence/AT-32/reload.txt`, `evidence/AT-32/steps.txt`, `evidence/AT-32/1280-dark.png`, `evidence/AT-32/1280-light.png`, `evidence/AT-32/375-dark.png`, `evidence/AT-32/375-light.png`, `evidence/AT-32/768-dark.png`, `evidence/AT-32/768-light.png`, `evidence/AT-32/before-1280-dark.png`, `evidence/AT-32/before-1280-light.png`, `evidence/AT-32/before-375-dark.png`, `evidence/AT-32/before-375-light.png`, `evidence/AT-32/before-768-dark.png`, `evidence/AT-32/before-768-light.png`, `evidence/AT-32/before-iphone-390x660-light.png`, `evidence/AT-32/iphone-390x660-light.png`, `evidence/AT-32/repick-1280-dark.png`, `evidence/AT-32/repick-1280-light.png`, `evidence/AT-32/repick-375-dark.png`, `evidence/AT-32/repick-375-light.png`, `evidence/AT-32/repick-768-dark.png`, `evidence/AT-32/repick-768-light.png`, `evidence/AT-32/repick-iphone-390x660-light.png`
Observation: Cam Skattebo stands in for Walker. Before the reload each size logs Skattebo pressed and "1 of 3"; after the reload Find mode stays, but Your team reads "Pick a team" and no strip shows, and after a new pick of Bo Girds the log reads `pressed=[]`, `counter="0 of 3"`, and the repick shots show no ring and the empty block line.
