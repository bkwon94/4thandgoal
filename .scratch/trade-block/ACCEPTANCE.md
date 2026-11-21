# Trade block: acceptance tests

Spec: `.scratch/trade-block/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

Each live press runs on the local evidence API, never on Fly. If Walker, Flowers, Corum, or Jackson is no longer on the roster of Bo Girds, the evidence agent uses another player of the same position and names him in the evidence.

## Tests

AT-1: Each offer sends a block player
App: pipeline
Stories: 1, 3
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, with Jev answers fixed in the test.
When: The evidence agent runs `search()` with the Trade block Kenneth Walker III and Zay Flowers.
Then: Each offer sends Walker, Flowers, or both on the side of Bo Girds.
Evidence: The test command and its output, with the count of offers.

AT-2: Two block players both reach the Shortlist
App: pipeline
Stories: 2, 4
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, with Jev answers fixed in the test. Each of Walker and Flowers has at least one fair offer.
When: The evidence agent runs `search()` with the Trade block Walker and Flowers.
Then: The Shortlist holds at least one offer that sends Walker and at least one offer that sends Flowers.
Evidence: The test command and its output, with the Shortlist.

AT-3: A package of two block players counts
App: pipeline
Stories: 5
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, with Jev answers fixed in the test.
When: The evidence agent runs the Value screen with the Trade block Walker and Flowers.
Then: An offer that sends Walker and Flowers together passes the block rule.
Evidence: The test command and its output.

AT-4: A block player who fails the pool gives no error
App: pipeline
Stories: 21
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, with Jev answers fixed in the test. One block player is a handcuff on the test snapshot.
When: The evidence agent runs `search()` with the handcuff and Walker on the block.
Then: The search raises no error, no offer sends the handcuff, and offers that send Walker remain.
Evidence: The test command and its output.

AT-5: An empty block changes nothing
App: pipeline
Stories: 14
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, with Jev answers fixed in the test.
When: The evidence agent runs `search()` once with `trade_block` empty and once with no block.
Then: Both runs give the same offers in the same order.
Evidence: The test command and its output.

AT-6: The route rejects a bad block
App: api
Stories: 32
Given: The find route of the API with its test client.
When: The evidence agent sends a block of 4 ids, a block with a repeated id, and a block with a player of another roster.
Then: Each request gets a 422 with a plain reason.
Evidence: The test command and its output, with the three reasons.

AT-7: A block search never serves the plain cache
App: api
Stories: 34
Given: The find route of the API with its test client.
When: The evidence agent computes the finder cache key with and without the Trade block Walker, and with the block in two orders.
Then: The key with Walker differs from the key with no block, and the two orders give one key.
Evidence: The test command and its output.

AT-8: A block press uses the Fair cache
App: api
Stories: 33
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, on the local evidence API after the fair warm-up ends.
When: The evidence agent presses Find a Trade with Walker on the block and Every team.
Then: The press makes 0 new fair asks.
Evidence: The API log lines of the press that count the fair asks and the cache hits.

AT-9: The pick hears the block
App: pipeline
Stories: 4
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, with Jev answers fixed in the test.
When: The evidence agent builds the user message of the pick for a press with the Trade block Walker and Flowers.
Then: The message names Walker and Flowers as the Trade block, and the prompt holds the rule that a block player with a fair Shortlist offer gets at least one pick.
Evidence: The test command and its output, with the block line of the message and the prompt rule.

AT-10: A press around Walker
App: both
Stories: 1, 3, 16
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, on the local evidence API after the fair warm-up ends.
When: The reader puts Walker on the block, keeps Every team and the chip Any, and presses Find a Trade.
Then: Each card sends Walker.
Evidence: The find answer, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, of the cards.

AT-11: The cards spread across two block players
App: both
Stories: 4
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, on the local evidence API after the fair warm-up ends.
When: The reader puts Walker and Flowers on the block and presses Find a Trade.
Then: Each of Walker and Flowers that has a fair offer on the Shortlist is sent by at least one card.
Evidence: The find answer, the Shortlist from the API log, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, of the cards.

AT-12: The block with one partner
App: both
Stories: 17
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, on the local evidence API after the fair warm-up ends.
When: The reader puts Walker on the block, picks one partner in Trade with, and presses Find a Trade.
Then: Each card has that partner and sends Walker, or the empty line shows.
Evidence: The find answer, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, of the result.

AT-13: The block with the RB chip
App: both
Stories: 18
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, on the local evidence API after the fair warm-up ends.
When: The reader puts Flowers on the block, picks the chip RB, and presses Find a Trade.
Then: Each card sends Flowers and gets at least one RB, or the empty line shows.
Evidence: The find answer, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, of the result.

AT-14: The empty answer names the block
App: both
Stories: 19, 20
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, on the local evidence API after the fair warm-up ends. The block, the partner, and the chip leave no fair trade.
When: The reader presses Find a Trade.
Then: The page shows no card and the line "No fair trade sends Walker or Flowers with the partner and the position you picked.", with the names of the block.
Evidence: The find answer, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, of the empty result.

AT-15: The strip lists QB, RB, WR, and TE only
App: site
Stories: 6, 7, 15
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site.
When: The reader opens Find mode.
Then: The strip shows the QB, RB, WR, and TE of Bo Girds, in that position order and then by name, each with the headshot, the last name, and the position, and no kicker and no defense.
Evidence: The `/teams` roster of Bo Girds, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit.

AT-16: A tap puts a player on the block
App: site
Stories: 8, 9, 11
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site.
When: The reader taps Walker.
Then: Walker shows a red ring and a check at the front of the strip, and the counter reads "1 of 3".
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, before and after the tap.

AT-17: A tap on a pick takes it off
App: site
Stories: 10
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker is on the block.
When: The reader taps Walker.
Then: Walker has no ring, he is back in his roster place, and the counter reads "0 of 3".
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, after the tap.

AT-18: A 4th tap is blocked
App: site
Stories: 12, 13
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker, Flowers, and Blake Corum are on the block, and the strip shows the end of the roster.
When: The reader taps Lamar Jackson.
Then: No player is added, the strip scrolls back to the 3 picks, and the line "Your block holds 3 players. Take one off to add another." shows.
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, after the tap.

AT-19: The full block label
App: site
Stories: 11
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker, Flowers, and Corum are on the block.
When: The reader looks at the label.
Then: The label reads "Trade block · tap a pick to take it off" and the counter reads "3 of 3".
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit.

AT-20: The empty block line
App: site
Stories: 14
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. No player is on the block.
When: The reader opens Find mode.
Then: The line "No one on the block. The search can offer any of your players." shows.
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit.

AT-21: A team change clears the block
App: site
Stories: 22
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker is on the block.
When: The reader changes Your team to another team.
Then: The block is empty, the counter reads "0 of 3", and the strip shows the roster of the new team.
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, after the change.

AT-22: A partner or chip change keeps the block
App: site
Stories: 23
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker and Flowers are on the block.
When: The reader picks one partner in Trade with, then the chip RB.
Then: Walker and Flowers stay on the block after each change.
Evidence: The Vitest command and its output, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, after the two changes.

AT-23: The strip locks during a find
App: site
Stories: 22, 23
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker is on the block and a find runs.
When: The reader taps Flowers.
Then: The block stays Walker alone.
Evidence: The Vitest command and its output.

AT-24: Motion off
App: site
Stories: 27
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. The reduced motion setting is on.
When: The reader taps Walker.
Then: Walker is at the front of the strip at once, with no motion frame between.
Evidence: The Playwright command and its output, with the position of Walker one frame after the tap.

AT-25: Screen reader
App: site
Stories: 28
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker is on the block.
When: The evidence agent reads the accessibility tree of the strip.
Then: Each item is a toggle named with the player name and the position, Walker has the pressed state, and the others do not.
Evidence: The accessibility tree of the strip.

AT-26: Keyboard
App: site
Stories: 29
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site.
When: The reader moves to the strip with Tab, moves to Flowers with the arrow keys, and presses Space.
Then: Flowers is on the block.
Evidence: The Playwright command and its output, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, after the key press.

AT-27: It fits on each screen
App: site
Stories: 25, 26
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker and Flowers are on the block.
When: The evidence agent loads Find mode in iPhone WebKit at 390x660, iPad WebKit at 810x980 and 1080x740, and desktop at 1280x800.
Then: No text box overlaps another, no fixed bar covers content, and the strip fills the width of the hero.
Evidence: The Playwright command and its overlap assert output, and screenshots at each size.

AT-28: The "gives" ask uses the block
App: api
Stories: 30
Given: The trade topics handler of the front door with its test client.
When: The evidence agent sends the ask "What can I get for Walker?" as Bo Girds.
Then: The find request carries `trade_block` with the id of Walker and no anchor.
Evidence: The test command and its output, with the find request.

AT-29: The "gets" ask is unchanged
App: api
Stories: 31
Given: The trade topics handler of the front door with its test client.
When: The evidence agent sends the ask "How do I get Bijan Robinson?" as Bo Girds.
Then: The find request carries the anchor of Bijan Robinson with the side "gets" and no `trade_block`.
Evidence: The test command and its output, with the find request.

AT-30: No "anchor" on the page
App: site
Stories: 35
Given: The built site of `cpc`.
When: The evidence agent searches the built pages and the analyzer site source for the word "anchor" in copy.
Then: No copy that a reader sees says "anchor".
Evidence: The search command and its output.

AT-31: Out of scope: no other roster on the strip
App: site
Stories: none
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site.
When: The reader scrolls the whole strip.
Then: Each player on the strip is on the roster of Bo Girds in `/teams`.
Evidence: The `/teams` roster of Bo Girds, the strip player ids, and screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit.

AT-32: Out of scope: no stored block
App: site
Stories: none
Given: The week 11 rosters of `cpc`, with Bo Girds as the asker, in Find mode of the analyzer on the local site. Walker is on the block.
When: The reader reloads the page.
Then: The block is empty.
Evidence: Screenshots of the Find hero at 375, 768, and 1280 px, each in the light theme and the dark theme, and one at 390x660 in iPhone WebKit, after the reload.

## Trace

Story 1: AT-1, AT-10
Story 2: AT-2
Story 3: AT-1, AT-10
Story 4: AT-2, AT-9, AT-11
Story 5: AT-3
Story 6: AT-15
Story 7: AT-15
Story 8: AT-16
Story 9: AT-16
Story 10: AT-17
Story 11: AT-16, AT-19
Story 12: AT-18
Story 13: AT-18
Story 14: AT-5, AT-20
Story 15: AT-15
Story 16: AT-10
Story 17: AT-12
Story 18: AT-13
Story 19: AT-14
Story 20: AT-14
Story 21: AT-4
Story 22: AT-21, AT-23
Story 23: AT-22, AT-23
Story 24: no test. Reason: the block changes nothing after the press, and the deadline-week tests cover a card that opens graded.
Story 25: AT-27
Story 26: AT-27
Story 27: AT-24
Story 28: AT-25
Story 29: AT-26
Story 30: AT-28
Story 31: AT-29
Story 32: AT-6
Story 33: AT-8
Story 34: AT-7
Story 35: AT-30
Out of scope "Players of other rosters on the block": AT-31
Out of scope "A stored block": AT-32
Out of scope "A block of more than one player in the front door chat": no test. Reason: AT-28 checks the one-player block of the chat.
Out of scope "Three-team trades": no test. Reason: no part of the spec touches the trade shape.
Out of scope "A mark on a block player in the Ledger card": no test. Reason: the spec does not touch the card.
Out of scope "A full pool check in the picker": no test. Reason: AT-15 checks the positions that the strip lists.

## Revisions

- 2026-11-21, approved by Brian: the stand-in rule also covers a block player who fails the pool rules. On the week 11 data, Walker is Out with no return week, so the search drops him (story 21). Cam Skattebo stands in for Walker in each test that names Walker. Kirk Cousins stands in for Jackson, who left the roster.
