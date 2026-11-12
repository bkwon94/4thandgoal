# Front door lineup: Start or sit, fifteen blocks, and a short Suggestions row

Status: ready-for-agent
Date: 2026-11-12
Apps: both. The site renders fifteen blocks, the names-only Suggestions row, the header sheet of the front door, and the text block. The pipeline writes the block data of six league Topics into `topics.json`. The API builds Start or sit live, the blocks of the personal and the trade Topics, the live matchup card, and the game lock.
Spec branch: `front-door-lineup`.
Source: the map `.scratch/front-door-lineup/MAP.md` and decision tickets 01 to 11. The sessions of 2026-11-11 and 2026-11-12.
Tickets: 01 to 18, in `issues/`.

## Problem Statement

A manager has no reason to open the site on game day. The front door answers questions about the league and the team, but no Topic says who to start this week. The managers set the lineup in Sleeper, with the projections of Sleeper and no reason behind them.

The Answers are plain. A Topic Answer is a list or a table, and its text is plain paragraphs. The shape of the data, such as the gap in a matchup or the playoff line, is not visible at a glance.

On a phone, the Suggestions take two rows of about 107 px at 375 px wide, and the dock floats over the foot. The Thread gets little of the screen. With an Answer in the Thread, the ask box and the dock also cover the passphrase box above the iOS keyboard.

## Solution

A new Topic, Start or sit, gives Your team its Week lineup for the live week. Each slot shows the starter, and a Swap or a Q row opens in place with its reason. Jev judges each Swap from the Fact sheets of the two players, and it may bench a player with a higher projection. A Questionable starter gets a Pivot line. The lineup reads live Sleeper data and respects the game lock.

Each Topic Answer shows one block in the Ledger look: rows in a fixed order that open in place, and one small mark, such as a tug bar, a step path, or a dot matrix. The text is optional and allows a small set of markdown marks. Fifteen blocks serve the Topics and the free answers.

The Suggestions take one row of about 48 px: only a short name of each Topic. A first tap shows the fact in a strip, and a second tap opens the Topic. On the front door, the dock and the week pill leave. A menu button in the header opens a sheet of the pages, and the Suggestions row and the ask box sit on one flush surface at the bottom. The passphrase box stays above the keyboard.

## User Stories

### Start or sit

1. As a manager, I want a Start or sit Topic, so that I leave the site on game day with a lineup decision.
2. As a manager, I want the lineup in the slot order of Sleeper, so that I read it in one pass and match it to the app.
3. As a manager, I want each row to show the slot, the player, his NFL team, the opponent, the kickoff, and the projection in league points, so that I see the whole lineup at a glance.
4. As a manager, I want the projection in the scoring of my league, so that half PPR and full PPR read right.
5. As a manager, I want a Swap row that says "Swap over K. Vidal" with the benched name struck through, so that I see the change and who loses the slot.
6. As a manager, I want the reason of a Swap to open in place under its row, so that I see why without a new screen.
7. As a manager, I want Jev to weigh the whole Fact sheet, so that a Swap can beat a higher projection when the matchup or the usage says so.
8. As a manager, I want a Q tag on a Questionable starter with the body part and the practice level, so that I know the risk.
9. As a manager, I want the Q tag to say "No practice report yet" before the first report of the week, so that a blank level does not read as healthy.
10. As a manager, I want a Pivot line under a Q row, such as "Start Kamara if he is active. If he is ruled out, start Allgeier.", so that I have a plan for the late news.
11. As a manager, I want the first Swap or Q row to open on arrival, so that the most important change shows first.
12. As a manager, I want the other rows to stay still when a row opens, so that I do not lose my place.
13. As a manager, I want OUT, IR, and bye players in one line under the rows, such as "Can't play: J. Jacobs Out (finger)", so that I know who to replace.
14. As a manager, I want a toggle of "By projection" and "With 1 Swap" in the header of the block, so that I see what the Swaps change in the total.
15. As a manager, I want the digits of the total to roll on the toggle, so that the change is clear.
16. As a manager, I want a player whose game has started to be locked, so that the lineup never asks me to move him.
17. As a manager of cpc, I want the DEF slot in the lineup, so that every slot is covered.
18. As a manager of norcal, I want three FLEX slots and no DEF, so that the lineup matches my league.
19. As a manager, I want Start or sit to lead the Suggestions from Thursday to Sunday, so that I find it on game day.
20. As a manager, I want Start or sit at the top on any day when a starter is OUT, on IR, or on a bye, so that I fix a hole at once.
21. As a manager, I want Start or sit third on Wednesday, after the waiver targets, so that the claims come first.
22. As a manager, I want the Start or sit Suggestion to show a short fact, such as "1 can't play, 1 Q", so that I know if the lineup needs me.
23. As a manager, I want to type "Start Downs or Pittman?" with two players of my team and get the comparison block, so that I settle one choice.
24. As a manager, I want the comparison block to show a pair of bars for each fact from a center line, so that I see who wins each fact.
25. As a manager, I want the side that wins a fact in red, and a dot on each deciding fact, so that I see the reason of the pick.
26. As a manager, I want the comparison to close with the pick, such as "Start J. Downs.", so that the answer is plain.
27. As a manager, I want a question with three or more of my players to get the lineup block for their slot, so that a bigger choice still has an answer.
28. As a manager, I want a question about a player off my roster to go to a free answer, so that Start or sit stays about my team.
29. As a manager, I want to ask "How does the Bears game look?" and get the NFL game card, so that I see the game behind a choice.
30. As a manager, I want the NFL game card to show a tug bar of the expected margin, a strip of the 32 defenses with the opponent lit, and two pass-share bars against a league mark, so that I read the game at a glance.

### The blocks of the Topics

31. As a manager, I want each Topic Answer to show one block, so that the Thread stays short on a phone.
32. As a manager, I want an Answer with no text when the block says it all, so that I read less.
33. As a manager, I want the Week recap to show the recap card: my score, a strip of the 12 scores, the top scorer against his projection, and the first sentence of the recap, so that I see my week at a glance.
34. As a manager of cpc, I want a median tick on the strip of the recap card, so that I see the median game.
35. As a manager of norcal, I want no median tick, so that the card shows no game that my league does not play.
36. As a manager, I want Your last matchup to show the matchup card with the final scores slot by slot, so that I see where I won or lost.
37. As a manager, I want Your next matchup to show the matchup card with the projected scores and the win odds, so that I know my chance.
38. As a manager, I want the win odds and the projections of the next matchup to be live, so that a bye, an OUT player, or a Swap shows on Sunday.
39. As a manager, I want a bar from the center line for the gap in each slot of a matchup, so that I see where the matchup turns.
40. As a manager, I want Power rankings to show the rank mover list with a bar from the center for each move, so that I see who rose and who fell.
41. As a manager, I want Playoff race to show the standings ladder with a bar of the playoff odds for each team and a rule at the playoff line, so that I see the race.
42. As a manager, I want my row on the ladder in red, so that I find my team at once.
43. As a manager, I want Your season to show the schedule strip: a dashed step path of the ranks of my opponents, drawn against the playoff line, so that I see how hard the rest of the season is.
44. As a manager, I want Position leaders and recent trades to show the leaders as a list in the text, so that I read the top scorer at each position.
45. As a manager, I want Waiver targets to show the waiver list: one row per free agent with the position, the team, the projection, and the slot he fills, so that I choose a claim.
46. As a manager, I want the why of a waiver target to open in place, so that I see the reason of the claim.
47. As a manager, I want How you stack up to show the slot rank bars for QB, RB, WR, and TE, each from the league middle, so that I see my strong and weak positions.
48. As a manager, I want the header of the slot rank bars to show my roster grade and its one-line read, so that I see the whole team.
49. As a manager, I want Weak spots to show the bye grid: a dot matrix of my players against the next weeks, with a red dot for a starter on a bye, so that I plan for the byes.
50. As a manager, I want Sell high or buy low to show the sell list: one row per player with his ranks and the headline, with the bullets in place, so that I see who to sell.
51. As a manager, I want Trade ideas to show one trade card with a row for each offer, so that I see every offer in one block.
52. As a manager, I want the first offer to open on arrival into the full trade card, and a tap to open another, so that I compare the offers.
53. As a manager, I want Trade check to show the trade card of the trade that I typed, so that I see the two sides.
54. As a manager, I want the trade card to show a bar of the projected points for the rest of the season for each player and a tug bar of the two totals, so that I see the value of each side.
55. As a manager, I want the trade card to close with the Lean of the Advisor, such as "Lean yes.", so that the card has one verdict.
56. As a manager, I want the case and the top bullets of a trade to open in place, so that I see why.
57. As a manager, I want the transaction feed in a free answer, with a strip of the moves per day and a dot for the kind of each move, so that I see the league activity.
58. As a manager, I want a trade row of the feed to show what each side got, so that I read a trade in one row.
59. As a manager, I want a free answer to show any of the fifteen blocks, so that a typed question gets the same rich Answer as a Topic.
60. As a manager, I want the text of an Answer to allow bold, italic, and lists, so that a list of players reads as a list.
61. As a manager, I want no links, images, or headings in the text of an Answer, so that the Answers stay safe and clean.

### The look and the motion

62. As a manager, I want every block in the same Ledger look, so that the front door reads as one product.
63. As a manager, I want the detail of an open row to come into focus from a blur, so that the open feels smooth.
64. As a manager, I want red for my team or the side that wins and gray for the rest, so that the colors mean the same thing in every block.
65. As a manager, I want each block to work in light and dark, so that it reads at night.
66. As a manager who turns on reduced motion, I want the blocks to show with no motion, so that the page does not move.
67. As a manager on a desktop, I want the blocks stacked in the column of about 560 px, so that the layout matches the phone.

### The Suggestions row

68. As a manager, I want the Suggestions in one row of about 48 px at 375 px wide, so that the Thread gets the screen.
69. As a manager, I want each chip to show only a short name of its Topic, so that the row stays short.
70. As a manager, I want "More" to lead the row, so that I find the other Topics.
71. As a manager, I want a first tap on a chip to show its fact in a full-width strip with "Open →", so that I see the fact before I open the Topic.
72. As a manager, I want a second tap on the chip or the strip to open the Topic, so that I choose with intent.
73. As a manager, I want a tap on another chip to cross-fade the strip to its fact, so that I compare the facts.

### The navigation of the front door

74. As a manager on the front door, I want no dock at the bottom, so that the ask box and the Suggestions get the space.
75. As a manager on the front door, I want a menu button at the right of the header that opens a sheet of the pages, so that I still reach every page.
76. As a manager, I want each row of the sheet to show an icon, the page name, and a short note, with a check on the current page, so that I know where each row goes.
77. As a manager, I want the sheet to close by the X, a tap on the dimmed page, Escape, or a swipe up, so that it closes the way I expect.
78. As a keyboard user, I want the focus to go to the sheet on open and back to the button on close, so that I do not lose my place.
79. As a manager on the front door, I want no week pill in the header, so that I do not read the last report week as the live week.
80. As a manager, I want a week row in the sheet that opens the latest report, and "Past weeks" under it, so that I still reach the reports.
81. As a manager, I want the Suggestions row and the ask box on one flush surface at the bottom, so that nothing floats over the Thread.
82. As a manager on another page, I want the dock and the week pill as today, so that those pages do not change.
83. As a manager on a desktop, I want the pages inline in the header and no menu button, so that the desktop does not change.
84. As a manager, I want the passphrase box above the iOS keyboard when I type in it, so that I see what I type.

## Implementation Decisions

### The Topic and its words

- Start or sit is a new Topic with the key `start_sit`. It is a personal Topic and runs live on the API, as the other personal Topics do. The glossary already holds Start or sit, Week lineup, Swap, Pivot, and Fact sheet.
- The front door has 14 Topics. The order of the day changes: Start or sit leads Thursday to Sunday, Your next matchup moves to second, and Start or sit is third on Wednesday after Waiver targets. Jev lifts Start or sit to the top on any day when a starter is OUT, on IR, or on a bye. Monday does not change.
- A typed question that names two players of Your team and asks which to start routes to Start or sit with the comparison block. A question with three or more players of Your team gets the lineup block for their slot. A question with a player off the roster goes to a free answer.

### The data of Start or sit

- The data is live Sleeper only: the rosters, the injury status, the body part, the practice level (`practice_participation`), and the week projections of Rotowire (`company: rotowire`).
- Code scores each projection from its stat line with the scoring of the league. cpc is half PPR with 2 FLEX and a DEF. norcal is full PPR with 3 FLEX and no DEF.
- The Fact sheet of one player holds the projection and its stat line, the defense against his position (`fan_pts_allow_<pos>` of the Sleeper DEF rows), the strength of his team from `pts_allow`, the expected margin, the pass or run tilt of his team, his share of targets, carries, and snaps over the last 3 weeks, and his status.
- The expected margin of an NFL game is the gap of the projected points of the two Sleeper DEF projections, not a betting line.
- `practice_participation` is null for every player before the first practice report of the week. The Q tag then says "No practice report yet".

### The hard rules in code

Code holds only facts and legal rules. It has no points cutoff and no screen by projection.

- Slot eligibility: a player can fill a slot only if his position is allowed there.
- A player on a bye, with an out status (OUT, IR, or suspended), cannot play. He goes to the "Can't play" line.
- The game lock: a game is locked when `now >= start_time` or when `metadata.has_started` is true. The source is the Sleeper GraphQL `scores` query at `https://sleeper.com/graphql`, with no key. Its `start_time` is the kickoff in epoch ms, UTC. The API fetches the times fresh for each Answer. The fallback is the ESPN scoreboard JSON, with a map of team codes, such as `WSH` to `WAS`. The live stats are a second signal only, because they lag the kickoff by 0.4 to 4.9 minutes.
- A locked player can be neither a Swap nor a starter that a Swap replaces.
- No source sets the final inactive status in time, so the lock does not read it. The Pivot line covers a Questionable starter.

### The Jev Swap question (decision ticket 07)

- One request per Week lineup bundles every question, because the questions share the state.
- The state holds the scoring of the league in words, the week, and one Fact sheet per player, keyed by the player name. The names, not ids, go in the state.
- Code lists each pair of a bench player who can play and a starter of a slot that the bench player can fill. Neither player is locked. Each pair gets one Choice question: "Which player will score more fantasy points this week in the scoring of this league?" Its two options are the two player names. The question names the slot.
- Code reads the probability of the bench player. A pair is a Swap candidate when it is at least `YES_AT`, 0.7, the threshold that the trade code already uses. A pair below 0.7 keeps the starter, including the band between 0.3 and 0.7.
- Code resolves the candidates in order: the candidate with the highest probability wins first. A bench player fills one slot at most, and a starter loses his slot to one bench player at most.
- The comparison block of a typed "Start A or B?" asks the same question over the same Fact sheets. The pick is the player with the higher probability.
- The Pivot of a Q starter is the best legal bench player for his slot by the projection. Code picks it.
- Claude writes the reason of each Swap and the text from the Fact sheets and the Swaps of code. The Jev check of the text runs as for the other personal Topics.
- A failed Jev call is an error, not a "keep the starter". The Answer shows the honest miss.
- The question wording lives in the one wording module of the personal Topics, with the other question text.

### The Suggestion fact of Start or sit (decision ticket 08)

- The fact comes from code facts only, so the Suggestions make no Jev call. The Swaps need the Jev read, so the fact does not count them.
- The fact counts the starters who cannot play and the Questionable starters: "1 can't play, 1 Q". It names one part when the other is zero: "2 Q".
- With no starter out and no Q, the fact names the next kickoff of the lineup: "Next kickoff Sun 1:00 PM".
- The kickoff time shows in the time zone of the browser.

### The text block (decision ticket 09)

- The text of every Answer is the text block. It is optional: an Answer may be only a block.
- The allowed marks: bold, italic, bullet lists, numbered lists, and paragraphs.
- Blocked marks: links, images, headings, raw HTML, and markdown tables. A blocked mark shows as plain text. A table has its own block. A link or an image from Claude is a risk on a public site. A heading competes with the title of the card.
- The site renders the text with an allowlist of elements. No element outside the list reaches the page.
- Code strips the marks before the Jev check, so Jev reads the same plain sentences.

### The fifteen blocks

Each block has a `kind`. The fifteen kinds: the lineup block, the two-player comparison, the NFL game card, the matchup card, the schedule strip, the standings ladder, the slot rank bars, the trade card, the rank mover list, the bye grid, the transaction feed, the recap card, the waiver list, the sell list, and the text block. The block schema of the site is one union over `kind`. The `list`, `table`, and `player` kinds of the free answer stay in the union, so a free answer that uses them now does not change.

All blocks take the Ledger look. Rows keep a fixed order. A row with detail shows a chevron, opens taller in place, and its detail comes into focus from a blur. The other rows do not move. The first row with detail opens on arrival where the block says so. Red marks Your team or the side that wins, gray the rest, and the up and down colors of the site mark a move. Each block works in light and dark, on a phone and in the desktop column of about 560 px, and with reduced motion.

- **Lineup block:** the slots in Sleeper order. Each row shows the slot, the player, his team, the opponent, the kickoff, and the projection. A Swap row reads "Swap over K. Vidal" with the benched name struck through. A Q row shows the body part, the practice level, and the Pivot under a red rule. The first Swap or Q row opens on arrival. The "Can't play" line sits under the rows. The header holds the toggle "By projection" and "With N Swaps", and the digits of the total roll on the change.
- **Two-player comparison:** one pair of bars for each fact, from a center line. The side that wins a fact is red. A dot marks each fact that the checked text cites. The pick closes the block: "Start J. Downs."
- **NFL game card:** a tug bar of the expected margin, a strip of the 32 defenses against the position with the opponent lit, and two pass-share bars against a league mark. It shows only in a free answer.
- **Matchup card:** the two teams, the scores, and a tug bar of the win odds. The lineups follow slot by slot, with a bar from the center line for the gap in each slot. Final scores for Your last matchup, projected scores for Your next matchup.
- **Schedule strip:** a dashed step path of the ranks of the opponents over the weeks left, drawn against the playoff line. The rows show the week, the opponent, the rank, and the record.
- **Standings ladder:** one row per team with the rank, the name, a bar of the playoff odds, and the record. A rule marks the playoff line from `settings.playoff_teams`. The row of Your team is red.
- **Slot rank bars:** one row each for QB, RB, WR, and TE, the `SLOT_POSITIONS` of the roster grade. Each bar grows from the league middle, worse to the left and better to the right, with the rank "6th of 12". The header holds the roster grade and its read. No FLEX rank and no DEF rank.
- **Trade card:** the two sides. Each player has a bar of his projected points for the rest of the season, and a tug bar shows the two totals. The Lean of the Advisor closes the card. The case and the top bullets open in place. For Trade ideas, the card holds one row per offer with the partner and the gist, and the first row opens on arrival into the full card.
- **Rank mover list:** one row per team with the rank, the name, a bar from the center for the move, and the arrow with the number of places.
- **Bye grid:** a dot matrix of the starters and the bench against the next weeks. A red dot marks a starter on a bye.
- **Transaction feed:** a strip of the moves per day over the header, then one row per move, newest first. A dot marks the kind: trade, waiver, or free agent. A trade row shows what each side got.
- **Recap card:** the score, a strip with a mark for each team, the top scorer against his projection, and the first sentence of the recap. The strip has a median tick only in a league that plays the median: cpc does, norcal does not.
- **Waiver list:** one row per free agent that Jev kept, with the position, the team, the projection, and the slot he fills. The why opens in place.
- **Sell list:** one row per player to sell, with his ranks and the headline. The bullets open in place.
- **Text block:** see the text block above.

### Which Topic shows which block

| Topic | Block | Where it is built |
| --- | --- | --- |
| Week recap | recap card | the weekly build |
| Your last matchup | matchup card, final scores | the weekly build |
| Your next matchup | matchup card, projected scores | the API, live |
| Power rankings | rank mover list | the weekly build |
| Playoff race | standings ladder | the weekly build |
| Your season | schedule strip | the weekly build |
| Position leaders and recent trades | no block: the text, with the leaders as a list | the weekly build |
| Waiver targets | waiver list | the API |
| How you stack up | slot rank bars | the API |
| Weak spots | bye grid | the API |
| Sell high or buy low | sell list | the API |
| Trade ideas | trade card, one row per offer | the API |
| Trade check | trade card | the API |
| Start or sit | lineup block | the API |

- A Topic Answer shows one block at most.
- A free answer may show any block. The comparison block shows for a typed two-player question. The NFL game card and the transaction feed show only in a free answer.

### The contracts

- **`topics.json`:** each league Topic gains one optional `block` field beside `fact`, `stats`, `rows`, and `text`. The field holds the `kind` and the data of the block. `schema_version` goes to 2. The site reads version 1 as today, with no block.
- **The live matchup card:** the API builds the block of Your next matchup from the Sleeper projections of the week and sends it on the stream of the Topic. The rest of the Topic still comes from `topics.json`.
- **The win odds of one game:** the gap of the two projected totals of the week, with the league `spread` of `sim.json` as the noise. The API computes them with the live matchup card.
- **The stream of an API Topic:** the data part of the block carries a `kind` and the data of one of the fifteen blocks. The text part follows, then the Jev check, as today.
- **The trade card** reads the Lean, the case, and the bullets that the analyzer gives now. It adds no grade.

### The Suggestions row (decision 02)

- Each chip shows only a short name of its Topic, in one row of about 48 px at 375 px wide, at every state of the Thread. "More" leads the row.
- The full Topic name shows in the strip, in "More", and in the question.
- The first tap on a chip opens a full-width strip of about 44 px under the row, with the whole fact and "Open →". A second tap on the chip or on the strip opens the Topic. A tap on another chip cross-fades the strip to its fact with a soft blur.
- The reveal is a tap, not a long press.
- The morph from a chip into its question, the "More" panel, reduced motion, and both themes stay.

### The navigation of the front door (decision 10)

- On the front door, the dock leaves. A menu button at the right of the header opens a sheet that drops from under the header. Its icon turns into an X.
- The sheet is a list of rows: an icon, the page name, and a short note. The current page has a check. The notes: "Ask about your team", "Scores and recaps", "The league, ranked", "Grades and records", and "Check a trade".
- The sheet closes by the X, a tap on the dimmed page, Escape, or a swipe up. The focus goes to the sheet on open and back to the button on close.
- The bottom of the front door is one solid surface, flush with the bottom edge: the Suggestions row and the ask box at full width. Its padding holds the home indicator, and it drops that padding while the keyboard is open.
- On the front door, the week pill leaves the header. The header holds the logo, the theme toggle, and the menu button. In the sheet, the week row opens the latest report, and "Past weeks" under it opens the list of weeks.
- The other pages keep the dock and the week pill.
- On a desktop, the menu button hides and the pages show inline in the header, as today.

### The passphrase fix (decision 02)

- The passphrase field of the miss card marks itself as a keyboard field, as the ask box does, so the foot moves above the keyboard for it.
- The card gets a scroll margin as tall as the foot, so the field stays in view.
- It is its own ticket.

### The design bar

Every UI ticket uses `transitions-dev`, `transitions-polish`, scrolltide components when one fits, `apple-design`, `animate`, `emil-design-eng`, `make-interfaces-feel-better`, `critique`, `polish`, and `frontend-design` or the claude.ai Design artifact as needed.

## Testing Decisions

A good test checks the behavior that a manager or a caller sees: the parts of the stream, the fields of `topics.json`, or the page that renders. It does not check the internal functions. Tests use the fakes of the repo for Sleeper, Jev, and Claude, as the tests of the personal Topics do now.

The seams, one per app, all of them existing:

1. **The API stream of a Topic.** Post to the route of a Topic and read the streamed parts. This seam covers Start or sit, the Swap rules, the game lock, the Pivot, the live matchup card, the win odds, the blocks of the personal and the trade Topics, and the Suggestion fact. Prior art: the tests of the personal Topics, the trade Topics, sell high, and the Suggestions in `apps/api/tests/`.
2. **The weekly build of `topics.json`.** Build the Topics from a fixture week and read the `block` field of each league Topic, in cpc and in norcal. This seam covers the median rule and the playoff line. Prior art: the Topics test in `apps/pipeline/tests/`.
3. **The front door page.** Render the page with a stream or a `topics.json` fixture and check what shows. This seam covers each block, the text marks and the blocked marks, the Suggestions row and its strip, the header sheet, and the passphrase field. Prior art: the `page-*.test.tsx` tests of the site and the tests in the front door folder.

The cases that each seam must hold:

- A bench player with a Swap probability of 0.7 or more takes the slot. One below 0.7 does not.
- Two bench players who beat one starter: the higher probability wins. One bench player who beats two starters fills one slot.
- A locked player is never a Swap and never loses his slot to a Swap.
- A failed Jev call gives the honest miss, not a lineup.
- A cpc lineup has a DEF and 2 FLEX. A norcal lineup has 3 FLEX and no DEF.
- The recap block of norcal has no median. The recap block of cpc has one.
- A link, an image, a heading, or raw HTML in the text renders as plain text.
- The Suggestion fact of Start or sit counts the starters who cannot play and the Q starters, and names the next kickoff when both are zero.

## Out of Scope

- A news source or a web fetch. Sleeper has no news text, and Jev cannot check a claim from a web page against our data.
- A second projection source, such as FantasyPros. It is a new feed and a separate decision.
- A backtest of the free judgment over weeks 2 to 9. Brian judges by feel. Run it if the feel turns bad.
- Betting lines and weather. They are not in our data.
- A DEF rank in the roster grade. The manager pages and the grade weights use the grade, so the change belongs to its own spec.
- A season score trend chart and a playoff odds bar. No Topic needs them yet.
- The top five leaders at each position. It is its own small spec.
- A change to the dock or the week pill of the other pages.

## Further Notes

- Free judgment is a known risk. Jev may bench a player with a higher Rotowire projection, and Rotowire already prices in the opponent. Brian chose it with that risk known, and he judges the calls by feel after the ship.
- Neither Sleeper GraphQL path has docs, so Sleeper can change or block it. The ESPN fallback covers that case.
- The first live game seen by the research was NYG at WAS on 2026-11-13 at 01:15 UTC. The live values of a game in progress are not seen yet.
- The bye grid of the prototype read the NFL bye weeks from a gitignored cache of nflverse. The spec reads the byes from the Sleeper schedules that the snapshot of the API already holds.
- The prototypes of decisions 02, 03, 04, and 10 are deleted. Their tickets hold the answers.
