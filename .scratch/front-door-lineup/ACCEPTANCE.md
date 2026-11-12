# Front door lineup: acceptance tests

Spec: `.scratch/front-door-lineup/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The team of the tests is Bo Girds: roster 6 in cpc and roster 7 in norcal. A test of the weekly build uses `2026` week 9. A live test uses the live week of `2026` at the time of the evidence, and the evidence names that week and the time.

"Site screenshots" means screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme (ADR 0006). "The stream" means the raw streamed parts of the API route of the Topic, saved as text.

## Tests

AT-1: The cpc lineup follows the Sleeper slot order
App: api, site
Stories: 1, 2, 3, 17
Given: Bo Girds of cpc in the live week.
When: The reader taps the Start or sit Suggestion.
Then: The lineup block shows the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF in that order. Each row shows the slot, the player, his NFL team, the opponent, the kickoff, and the projection.
Evidence: the stream, and site screenshots of the Answer.

AT-2: The norcal lineup has three FLEX and no DEF
App: api, site
Stories: 18
Given: Bo Girds of norcal in the live week.
When: The reader taps the Start or sit Suggestion.
Then: The lineup block shows the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, FLEX in that order, and no DEF row.
Evidence: the stream, and site screenshots of the Answer.

AT-3: The projection is in the points of the league
App: api
Stories: 4
Given: Bo Girds of cpc in the live week, and one named starter with receptions in his projected stat line.
When: The reader opens Start or sit.
Then: The projection of that starter equals his Sleeper projected stat line scored with the scoring settings of cpc, half PPR, to 0.1 point.
Evidence: the stream, the projected stat line of the player from Sleeper, the scoring settings of cpc, and the sum written out.

AT-4: A Swap row names the benched starter
App: site
Stories: 5, 6, 11
Given: A lineup with at least one Swap in the live week. Use Bo Girds, or any manager of either league whose lineup has a Swap, and name the manager.
When: The reader opens Start or sit.
Then: The Swap row reads "Swap over <starter name>" with the starter name struck through, and the first row with a Swap or a Q is open on arrival with its reason.
Evidence: site screenshots of the Answer on arrival.

AT-5: A Swap needs a probability of 0.7
App: api
Stories: 7
Given: The API test of Start or sit with the Jev fake of the repo, over a fixture lineup of real Sleeper data.
When: Jev gives a bench player 0.70 over a starter in one case, and 0.69 in a second case.
Then: The first case marks a Swap. The second case keeps the starter.
Evidence: the test names and the pytest output.

AT-6: The Swap candidates resolve by the highest probability
App: api
Stories: 7
Given: The API test of Start or sit with the Jev fake, over a fixture lineup of real Sleeper data.
When: Two bench players each beat one starter at 0.75 and 0.85, and one bench player beats two starters at 0.8 and 0.9.
Then: The bench player at 0.85 takes the first slot. The bench player who beats two starters fills only the slot at 0.9.
Evidence: the test names and the pytest output.

AT-7: A Q row shows the risk and the Pivot
App: site
Stories: 8, 10
Given: A lineup with a Questionable starter in the live week. Use Bo Girds, or any manager of either league with one, and name the manager.
When: The reader opens the Q row.
Then: The row shows the body part and the practice level, and the Pivot line reads "Start <starter> if he is active. If he is ruled out, start <bench player>."
Evidence: site screenshots of the open Q row.

AT-8: A blank practice level reads as no report
App: api
Stories: 9
Given: A Questionable starter whose `practice_participation` is null in Sleeper, before the first practice report of the week.
When: The reader opens Start or sit.
Then: The Q tag reads "No practice report yet".
Evidence: the stream, and the Sleeper player record with the null field.

AT-9: An open row does not move the other rows
App: site
Stories: 12, 63
Given: The lineup block of AT-1.
When: The reader opens a row that is closed.
Then: Each row above the open row keeps the same top position to 1 px, and the detail comes into view from a blur.
Evidence: the top position of each row before and after the tap, and two screenshots at 375 px.

AT-10: The players who cannot play sit in one line
App: site
Stories: 13
Given: A lineup in the live week with a player who is OUT, on IR, or on a bye. Name the manager.
When: The reader opens Start or sit.
Then: One line under the rows names each such player with his status, in the shape "Can't play: J. Jacobs Out (finger)".
Evidence: site screenshots of the Answer.

AT-11: The toggle shows what the Swaps change
App: site
Stories: 14, 15
Given: The lineup of AT-4.
When: The reader taps "By projection", then "With N Swaps".
Then: The total in the header changes between the two states, and the "With N Swaps" total equals the sum of the projections of the lineup with the Swaps.
Evidence: two screenshots at 375 px and the sum written out.

AT-12: A started game locks its players
App: api
Stories: 16
Given: The live week, after the Thursday kickoff, and a roster of either league with a player in that game. Name the manager and the player.
When: The reader opens Start or sit.
Then: That player is neither a Swap nor a starter that a Swap replaces.
Evidence: the stream, and the `start_time` and `has_started` of that game from the Sleeper `scores` query.

AT-13: Start or sit follows the order of the day
App: api
Stories: 19, 21
Given: Bo Girds of cpc with no starter OUT, on IR, or on a bye.
When: The Suggestions load on a Thursday, a Sunday, a Wednesday, and a Monday.
Then: Start or sit is first on Thursday and on Sunday, third on Wednesday after Waiver targets, and the Monday order is the order of today.
Evidence: the test names and the pytest output of the Suggestions test for each day.

AT-14: A hole in the lineup lifts Start or sit
App: api
Stories: 20
Given: A team with a starter OUT, on IR, or on a bye.
When: The Suggestions load on a Tuesday.
Then: Start or sit is first.
Evidence: the test name and the pytest output, or the live Suggestions of a named manager with such a starter.

AT-15: The Suggestion fact counts the holes and the Q starters
App: api
Stories: 22
Given: Two teams: one with starters who cannot play or Q starters, and one with neither.
When: The Suggestions load.
Then: The first fact has the shape "1 can't play, 1 Q". The second fact reads "Next kickoff <day> <time>".
Evidence: the Suggestions output of both teams.

AT-16: A two-player question gets the comparison block
App: api, site
Stories: 23, 24, 25, 26
Given: Bo Girds of cpc in the live week, and two of his players at one position.
When: The reader types "Start <player A> or <player B>?".
Then: The Answer is Start or sit with the comparison block: a pair of bars from a center line for each fact, the winning side of each fact in red, a dot on each cited fact, and the line "Start <name>."
Evidence: the stream, and site screenshots of the Answer.

AT-17: A question with three players gets the lineup block for their slot
App: api, site
Stories: 27
Given: Bo Girds of cpc in the live week.
When: The reader types a start question that names three of his WRs.
Then: The Answer shows the lineup block for the WR and FLEX slots.
Evidence: the stream, and site screenshots of the Answer.

AT-18: A player off the roster goes to a free answer
App: api
Stories: 28
Given: Bo Girds of cpc in the live week.
When: The reader types "Start <his player> or <a player on another roster>?".
Then: The Answer is a free answer, not Start or sit.
Evidence: the stream.

AT-19: The NFL game card shows in a free answer
App: api, site
Stories: 29, 30, 59
Given: The live week, with a Bears game.
When: The reader types "How does the Bears game look?".
Then: The free answer shows the NFL game card: a tug bar of the expected margin, a strip of the 32 defenses with the opponent lit, and two pass-share bars against a league mark. The margin equals the gap of the two Sleeper DEF projections.
Evidence: the stream, the two DEF projections from Sleeper, and site screenshots of the Answer.

AT-20: A failed Jev call gives the honest miss
App: api
Stories: 7
Given: The API test of Start or sit with the Jev fake.
When: The Jev call fails.
Then: The Answer is the honest miss, with no lineup and no Swap.
Evidence: the test name and the pytest output.

AT-21: A Topic Answer shows one block at most
App: site
Stories: 31, 32, 44
Given: Bo Girds of cpc, `2026` week 9.
When: The reader opens each of the 14 Topics.
Then: Each Answer shows one block or none. Position leaders and recent trades shows no block, and its text lists one leader per position.
Evidence: site screenshots at 375 px of each Answer, and the 1280 px light screenshot of Position leaders.

AT-22: The cpc recap card shows the median
App: pipeline, site
Stories: 33, 34
Given: Bo Girds of cpc, `2026` week 9.
When: The reader opens Week recap.
Then: The recap card shows 114.07, 3rd of 12, a strip with a mark for each team, and a median tick at 103.51.
Evidence: the `block` field of Week recap in `clients/cpc/published/2026/week-09/topics.json`, and site screenshots of the Answer.

AT-23: The norcal recap card has no median
App: pipeline, site
Stories: 35
Given: Bo Girds of norcal, `2026` week 9.
When: The reader opens Week recap.
Then: The recap card shows 155.38 against kaiedmonds, and no median tick.
Evidence: the `block` field of Week recap in the norcal `topics.json`, and site screenshots of the Answer.

AT-24: The last matchup shows the final scores slot by slot
App: pipeline, site
Stories: 36, 39
Given: Bo Girds of cpc, `2026` week 9.
When: The reader opens Your last matchup.
Then: The matchup card shows 114.07 to 100.63 against Teehee, then the two lineups slot by slot, each slot with a bar from the center line for its gap.
Evidence: the `block` field in the cpc `topics.json`, and site screenshots of the Answer.

AT-25: The next matchup is live
App: api, site
Stories: 37, 38
Given: Bo Girds of cpc in the live week.
When: The reader opens Your next matchup.
Then: The matchup card shows the two projected totals of the live week and the win odds, and the team with the higher total has odds above 50%. The card data has a read time within the minute of the request.
Evidence: the stream with its read time, and site screenshots of the Answer.

AT-26: Power rankings shows the rank mover list
App: pipeline, site
Stories: 40
Given: cpc, `2026` week 9.
When: The reader opens Power rankings.
Then: The block shows one row per team with the rank, the name, a bar from the center for the move, and an arrow with the number of places.
Evidence: the `block` field in the cpc `topics.json`, and site screenshots of the Answer.

AT-27: Playoff race shows the standings ladder
App: pipeline, site
Stories: 41, 42
Given: Bo Girds of cpc, `2026` week 9.
When: The reader opens Playoff race.
Then: The ladder shows 12 rows with the rank, the name, an odds bar, and the record, a rule under the 6th row, and the Bo Girds row in red.
Evidence: the `block` field in the cpc `topics.json`, and site screenshots of the Answer.

AT-28: Your season shows the schedule strip
App: pipeline, site
Stories: 43
Given: Bo Girds of cpc, `2026` week 9.
When: The reader opens Your season.
Then: The schedule strip shows a step path over weeks 10 to 14 against the playoff line, and one row per week with the opponent, the rank, and the record.
Evidence: the `block` field in the cpc `topics.json`, and site screenshots of the Answer.

AT-29: Waiver targets shows the waiver list
App: api, site
Stories: 45, 46
Given: Bo Girds of cpc in the live week.
When: The reader opens Waiver targets and taps the first row.
Then: Each row shows the position, the NFL team, the projection, and the slot that the player fills, and the tapped row opens in place with the why.
Evidence: the stream, and site screenshots of the open row.

AT-30: How you stack up shows four slot rank bars
App: api, site
Stories: 47, 48
Given: Bo Girds of cpc in the live week.
When: The reader opens How you stack up.
Then: The block shows exactly four rows, QB, RB, WR, and TE, each with a bar from the league middle and a rank such as "6th of 12". The header shows the roster grade and its read.
Evidence: the stream, and site screenshots of the Answer.

AT-31: Weak spots shows the bye grid
App: api, site
Stories: 49
Given: Bo Girds of cpc in the live week.
When: The reader opens Weak spots.
Then: The bye grid shows his players against the next weeks, with a red dot for each starter on a bye in that week.
Evidence: the stream, the bye weeks of his starters from the Sleeper schedules, and site screenshots of the Answer.

AT-32: Sell high shows the sell list
App: api, site
Stories: 50
Given: Bo Girds of cpc in the live week.
When: The reader opens Sell high or buy low and taps the first row.
Then: Each row shows the player, his ranks, and the headline, and the tapped row opens in place with the bullets. A roster with no clear sell shows its plain line.
Evidence: the stream, and site screenshots of the open row.

AT-33: Trade ideas shows one card with a row per offer
App: api, site
Stories: 51, 52
Given: Bo Girds of cpc in the live week.
When: The reader opens Trade ideas.
Then: The Answer shows one trade card with one row per offer, and the first offer is open as the full card.
Evidence: the stream, and site screenshots of the Answer.

AT-34: The Lean closes the trade card
App: api, site
Stories: 53, 54, 55, 56
Given: Bo Girds of cpc in the live week.
When: The reader runs a Trade check of one named trade.
Then: The trade card shows the two sides with a bar of the projected points for the rest of the season for each player, a tug bar of the two totals, and it closes with the Lean of the Advisor. It shows no edge line in points. The case and the bullets open in place.
Evidence: the stream, and site screenshots of the card closed and open.

AT-35: A free answer shows the transaction feed
App: api, site
Stories: 57, 58, 59
Given: cpc in the live week.
When: The reader types "What moves happened this week?".
Then: The free answer shows the transaction feed: a strip of the moves per day, one row per move newest first with a dot for its kind, and a trade row that shows what each side got.
Evidence: the stream, and site screenshots of the Answer.

AT-36: The text block renders the allowed marks
App: site
Stories: 60
Given: An Answer whose text has bold, italic, a bullet list, and a numbered list.
When: The Answer renders.
Then: The bold, the italic, and both lists render as marks.
Evidence: the test name and the vitest output, and one screenshot at 375 px.

AT-37: The text block shows blocked marks as plain text
App: site
Stories: 61
Given: An Answer whose text has a link, an image, a heading, and raw HTML.
When: The Answer renders.
Then: Each one shows as plain text. The page has no `a`, `img`, heading, or raw HTML element from the text.
Evidence: the test name and the vitest output.

AT-38: Every block takes the Ledger look
App: site
Stories: 62, 64, 65, 67
Given: The blocks of AT-1, AT-16, AT-19, and AT-22 to AT-35.
When: The reader views each block.
Then: Each block renders with no overflow and no overlap. Red marks Your team or the side that wins, and gray marks the rest. At 1280 px the blocks stack in the column of about 560 px.
Evidence: site screenshots of each block.

AT-39: The blocks honor reduced motion
App: site
Stories: 66
Given: The browser setting `prefers-reduced-motion: reduce`.
When: The reader opens Start or sit and taps a row.
Then: The block and the row show at once, with no slide, no blur, and no roll of digits.
Evidence: the test name and the output of a run with reduced motion, or a screen capture.

AT-40: `topics.json` carries one block for six league Topics
App: pipeline
Stories: 31
Given: cpc and norcal, `2026` week 9.
When: The weekly build of week 9 runs.
Then: `schema_version` is 2. Week recap, Your last matchup, Your next matchup, Power rankings, Playoff race, and Your season each have a `block` with a `kind`. Position leaders and recent trades has no `block`.
Evidence: the command and its output, and the `block` fields of both `topics.json` files.

AT-41: A version 1 `topics.json` still renders
App: site
Stories: none
Given: A `topics.json` with `schema_version` 1 and no `block` field.
When: The front door renders its Topics.
Then: Each league Topic Answer renders as before this spec, with its stats and rows.
Evidence: the test name and the vitest output.

AT-42: The Suggestions take one row
App: site
Stories: 68, 69, 70
Given: The front door of Bo Girds of cpc, with an empty Thread and with one Answer.
When: The reader views the Suggestions at 375 px.
Then: The row is one line of about 48 px, with "More" first and each chip showing only a Topic name.
Evidence: site screenshots, and the height of the row in px at 375 px.

AT-43: A first tap shows the fact, and a second tap opens the Topic
App: site
Stories: 71, 72
Given: The front door of AT-42.
When: The reader taps the Start or sit chip once, then again.
Then: The first tap shows a full-width strip under the row with the whole fact and "Open →". The second tap opens Start or sit.
Evidence: two screenshots at 375 px.

AT-44: A tap on another chip changes the strip
App: site
Stories: 73
Given: The strip of AT-43 is open.
When: The reader taps another chip.
Then: The strip shows the fact of the other chip, and the Topic does not open.
Evidence: a screenshot at 375 px.

AT-45: The header menu opens the sheet of pages
App: site
Stories: 74, 75, 76
Given: The front door at 375 px.
When: The reader taps the menu button.
Then: The front door has no dock. The sheet drops from under the header with five page rows, each with an icon, a name, and its note: "Ask about your team", "Scores and recaps", "The league, ranked", "Grades and records", and "Check a trade". The current page has a check, and the button shows an X.
Evidence: site screenshots at 375 and 768 px of the open sheet.

AT-46: The sheet closes four ways and returns the focus
App: site
Stories: 77, 78
Given: The open sheet of AT-45.
When: The reader closes it by the X, by a tap on the dimmed page, by Escape, and by a swipe up, one at a time.
Then: Each way closes the sheet. The focus goes to the sheet on open and back to the menu button on close.
Evidence: the test names and the output of the four cases.

AT-47: The week moves into the sheet
App: site
Stories: 79, 80
Given: The front door at 375 px.
When: The reader opens the sheet.
Then: The header has no week pill. The sheet has a week row that opens the latest report, and "Past weeks" under it.
Evidence: site screenshots of the header and the open sheet.

AT-48: The foot is one flush surface
App: site
Stories: 81
Given: The front door at 375 px, with one Answer in the Thread.
When: The reader views the bottom of the page.
Then: The Suggestions row and the ask box sit on one surface that touches the bottom edge, with no gap under it.
Evidence: site screenshots at 375 px.

AT-49: The other pages keep the dock and the week pill
App: site
Stories: 82
Given: The week report page and the rankings page of cpc.
When: The reader opens each page at 375 px.
Then: Each page shows the dock and the week pill as before this spec.
Evidence: site screenshots of both pages.

AT-50: The desktop header keeps the inline pages
App: site
Stories: 83
Given: The front door at 1280 px.
When: The reader views the header.
Then: The header shows the pages inline and no menu button.
Evidence: screenshots at 1280 px, light and dark.

AT-51: The passphrase box stays above the keyboard
App: site
Stories: 84
Given: An Answer in the Thread with the miss card and its passphrase box.
When: The reader focuses the passphrase box with the iOS keyboard open.
Then: The whole passphrase box is above the foot and in view.
Evidence: a screenshot from an iPhone, or a WebKit run that sets the keyboard height, with the box and foot positions.

AT-52: The roster grade keeps four slots
App: pipeline
Stories: none
Given: cpc, `2026` week 9.
When: The weekly build of week 9 runs.
Then: Each grade in `managers.json` has slots for QB, RB, WR, and TE only, with no DEF and no FLEX.
Evidence: the slot positions of each grade in `clients/cpc/published/2026/managers.json`.

AT-53: Start or sit fetches no news
App: api
Stories: none
Given: Bo Girds of cpc in the live week.
When: The reader opens Start or sit.
Then: The API calls no host other than Sleeper, ESPN, TypeSafe, and Anthropic.
Evidence: the log of the outbound hosts of the request.

## Trace

Story 1: AT-1
Story 2: AT-1
Story 3: AT-1
Story 4: AT-3
Story 5: AT-4
Story 6: AT-4
Story 7: AT-5, AT-6, AT-20
Story 8: AT-7
Story 9: AT-8
Story 10: AT-7
Story 11: AT-4
Story 12: AT-9
Story 13: AT-10
Story 14: AT-11
Story 15: AT-11
Story 16: AT-12
Story 17: AT-1
Story 18: AT-2
Story 19: AT-13
Story 20: AT-14
Story 21: AT-13
Story 22: AT-15
Story 23: AT-16
Story 24: AT-16
Story 25: AT-16
Story 26: AT-16
Story 27: AT-17
Story 28: AT-18
Story 29: AT-19
Story 30: AT-19
Story 31: AT-21, AT-40
Story 32: AT-21
Story 33: AT-22
Story 34: AT-22
Story 35: AT-23
Story 36: AT-24
Story 37: AT-25
Story 38: AT-25
Story 39: AT-24
Story 40: AT-26
Story 41: AT-27
Story 42: AT-27
Story 43: AT-28
Story 44: AT-21
Story 45: AT-29
Story 46: AT-29
Story 47: AT-30
Story 48: AT-30
Story 49: AT-31
Story 50: AT-32
Story 51: AT-33
Story 52: AT-33
Story 53: AT-34
Story 54: AT-34
Story 55: AT-34
Story 56: AT-34
Story 57: AT-35
Story 58: AT-35
Story 59: AT-19, AT-35
Story 60: AT-36
Story 61: AT-37
Story 62: AT-38
Story 63: AT-9
Story 64: AT-38
Story 65: AT-38
Story 66: AT-39
Story 67: AT-38
Story 68: AT-42
Story 69: AT-42
Story 70: AT-42
Story 71: AT-43
Story 72: AT-43
Story 73: AT-44
Story 74: AT-45
Story 75: AT-45
Story 76: AT-45
Story 77: AT-46
Story 78: AT-46
Story 79: AT-47
Story 80: AT-47
Story 81: AT-48
Story 82: AT-49
Story 83: AT-50
Story 84: AT-51
Out of scope "A DEF rank in the roster grade": AT-52
Out of scope "A news source or a web fetch": AT-53
Out of scope "A change to the dock or the week pill of the other pages": AT-49
Out of scope "Betting lines and weather": AT-19 (the margin comes from the DEF projections)
Out of scope "A second projection source": no test. Reason: the projection checks of AT-3 name Sleeper Rotowire, and no ticket adds a feed.
Out of scope "A backtest of the free judgment": no test. Reason: no agent builds a backtest by mistake.
Out of scope "A season score trend chart and a playoff odds bar": no test. Reason: no Topic of the map asks for them.
Out of scope "The top five leaders at each position": no test. Reason: AT-21 checks one leader per position.

## Revisions

None yet.
