# Trade block

Status: ready-for-agent
Date: 2026-11-21
Apps: both. The site adds the Trade block picker to Find mode of the analyzer. The analyzer package and the API take a Trade block on the find route, and the search keeps only offers that send a block player. The front door chat sends its "gives" ask as a Trade block of one player. The weekly pipeline does not change.
Spec branch: `trade-block`.
Source: the map `.scratch/trade-block/MAP.md` and decision tickets 01 to 04. ADR 0037 (ui-sdk standard), ADR 0038 (Value screen).
Tickets: none yet. `4ag:to-tickets` writes them.

## Problem Statement

A manager often knows which players they want to move: a surplus back, a receiver who lost his role, a second quarterback. The Finder of the analyzer does not let them say so. It builds trades from the whole roster, so most of its five cards send players the manager wants to keep. The manager must press again and again, or give up and build each trade by hand in the analyzer.

## Solution

Find mode gets a Trade block: a strip of the manager's roster under "Your team". The manager taps up to 3 players to put them on the block. Each trade that the Finder returns sends at least one of them. The block works with "Trade with" and the position chips. When no fair trade sends a block player, the Finder says so in a plain line and does not drop the rule. An empty block changes nothing, so the Finder works as it does now.

The front door chat already finds trades for one player, as in "what can I get for Walker?". That ask now uses the same Trade block, with one player on it.

## User Stories

1. As a manager, I want to put a player of my roster on the Trade block, so that the Finder builds trades around him.
2. As a manager, I want to put up to 3 players on the block, so that I can shop all my surplus at once.
3. As a manager, I want each trade to send at least one of my block players, so that no card sends only players I want to keep.
4. As a manager with two or three block players, I want the cards spread across them, so that I see ideas for each player and not five cards for one.
5. As a manager, I want a trade that sends two of my block players together to count, so that a package deal can show up.
6. As a manager, I want to see my whole roster as a strip of headshots, so that I can find a player with one look.
7. As a manager, I want each player in the strip to show his last name and position, so that I can tell two players apart.
8. As a manager, I want a picked player to get a clear ring and a check, so that I know he is on the block.
9. As a manager, I want a picked player to move to the front of the strip, so that a pick never scrolls out of view.
10. As a manager, I want to tap a pick to take it off, so that I can change my mind with one tap.
11. As a manager, I want a counter such as "2 of 3", so that I know how many more I can add.
12. As a manager, I want a plain reason when I tap a 4th player, so that I know why nothing happened and how to fix it.
13. As a manager, I want the strip to scroll back to my picks when a 4th tap fails, so that I see which player to take off.
14. As a manager, I want the empty block to say that the search can offer any of my players, so that I know an empty block is fine.
15. As a manager, I want the strip to list only quarterbacks, running backs, receivers, and tight ends, so that I never pick a kicker or a defense that no trade can send.
16. As a manager, I want the block to work with "Every team", so that every other manager can make an offer for my players.
17. As a manager, I want the block to work with one picked partner, so that I can shop my players to one manager.
18. As a manager, I want the block to work with a position chip, so that I can ask for an RB for my surplus receiver.
19. As a manager, I want an honest empty answer when no fair trade sends a block player, so that I do not get trades that break my ask.
20. As a manager, I want the empty answer to say why, so that I know whether to change the partner, the chip, or the block.
21. As a manager, I want a block player who is out with no return week, or who is a handcuff, to give no trade and no error, so that the search still works for my other block players.
22. As a manager, I want a change of "Your team" to clear the block, so that I never search with the players of another team.
23. As a manager, I want the block to stay while I change the partner or the chip, so that I do not pick my players again.
24. As a manager, I want each card to open in the analyzer already graded, as it does now, so that the block changes nothing after the press.
25. As a manager on a phone, I want the strip to fit at 390 px wide in Safari, so that it does not cover the find button or the chips.
26. As a manager on a tablet or a desktop, I want the strip to fill the hero width with no gap, so that the page looks finished at every width.
27. As a manager who turns motion off, I want a pick to move to the front with no motion, so that the page respects my setting.
28. As a manager who uses a screen reader, I want each player in the strip to read as a toggle with his name, position, and state, so that I can build a block without sight.
29. As a manager who uses a keyboard, I want to move through the strip and toggle a player with the keyboard, so that I can build a block without a pointer.
30. As a manager in the front door chat, I want "what can I get for Walker?" to find trades that send Walker, so that the chat and the analyzer agree.
31. As a manager in the front door chat, I want "how do I get Bijan?" to work as it does now, so that the chat keeps its target ask.
32. As the commissioner, I want a bad request with 4 block players, or a player of another roster, to fail with a clear error, so that a broken client cannot ask for a trade that the page forbids.
33. As the commissioner, I want a search with a block to use the Fair cache, so that a block press costs no more Jev calls than a plain press.
34. As the commissioner, I want a search with a block never to serve the cached list of a search without one, so that a manager never sees trades that break the block.
35. As a manager, I want the page never to say "anchor", so that the words on the page are the words managers use.

## Implementation Decisions

### The Trade block on the find route

- The find request gets an optional field `trade_block`: a list of 0 to 3 player ids of the asker's roster. An empty list and a missing field mean the same thing: no rule.
- The route rejects a list of more than 3 ids, a repeated id, and an id that is not on the asker's roster, with a 422 and a plain reason.
- The `Anchor` with the side "gets" stays for the "how do I get X" ask of the front door chat. The side "gives" retires: a "gives" ask is now a Trade block of one player. A request with an anchor and a block is legal; each rule holds.
- The finder cache key includes the block, as a sorted list, so a search with a block never serves a list without one (story 34). The Fair cache key does not change: each block offer is a Value offer that the warm-up already fills (story 33).
- The code names the field `trade_block` in Python and TypeScript (ticket 03).

### The search

- The Value screen keeps an offer only when the asker's side sends at least one block player. This is a hard rule beside the anchor rule and the limit rules. An empty block keeps every offer.
- A block player who fails the pool rules (a handcuff, out with no return week, no chart value) enters no offer. The search runs for the other block players. It raises no error (story 21).
- When every block player fails the pool rules, or no fair offer sends one, the Finder document carries the empty list with a plain line. The line names the cause in manager words, such as "No fair trade sends Walker, Flowers, or Corum with the partner and the position you picked." Code writes the line, as it does now for an empty search.
- The Partner filter and the Spares tree run as they do now.

### The spread of the cards (ticket 03)

- In `varied`, the tier of "the best offer of each player that the asker gives" counts only block players when the block is not empty. So the best offer of each block player comes before the rest, and a non-block player in the same trade takes no slot of that tier.
- The pick of the Advisor gets one more line in its user message: the names of the block players. The prompt gets one rule: when the shortlist holds a fair offer for a block player, at least one pick sends him. The pick still keeps its spread of shapes and partners.
- The Ledger card does not change. It shows no mark on a block player.

### The picker (ticket 01, prototype `trade-block-01-proto` at `285f2789`)

- The picker sits in the Find hero under "Your team" and above "Trade with". The label reads "Trade block · tap to add", with the counter "N of 3" on the right. At 3 of 3, the label reads "Trade block · tap a pick to take it off".
- It is one horizontal strip of the asker's roster. Each item shows the headshot, the last name, and the position. The strip edge fades, so the scroll is obvious.
- A tap on a player toggles him on the block. A pick gets a red ring and a check, and it moves to the front of the strip with a spring of 0.4 s and no bounce. The picks lead in the order of the taps, then the rest of the roster. With motion turned off, the move is instant.
- A tap on a 4th player adds nothing. The strip scrolls back to the picks, and the reason line reads "Your block holds 3 players. Take one off to add another."
- The empty block shows the line "No one on the block. The search can offer any of your players."
- The part is the ui-sdk `ToggleGroup` with `multiple`, through the wrapper in the design package, in a ui-sdk `ScrollArea` (ADR 0037). Each item is a toggle with an accessible name of the player, his position, and his state.
- The picker is locked during a find, as the other pickers are.

### The players that the picker lists (ticket 02)

- The strip lists the quarterbacks, running backs, receivers, and tight ends of the asker's roster, in that position order, then by name. It never lists a kicker or a defense, because the chart lists neither, so no trade can send them.
- The strip does not hide a handcuff or a player out with no return week. The `/teams` route reads only the roster snapshot, and a full pool check there needs the slow sources. The search drops such a player (story 21), and the empty line explains it when he is the only block player.

### The life of the block (ticket 04)

- The block lives in the page state of Find mode only. Nothing stores it.
- A change of "Your team" clears it.
- A change of "Trade with" or of the position chip keeps it, and clears the old cards, as such a change does now.
- A switch to Grade mode and back keeps the block exactly when it keeps the partner and the chip. The block follows the same rule as the other Find controls.

### The front door chat

- The trade-ideas handler of the front door sends a "gives" ask as `trade_block` with one player id, and no anchor.
- The "gets" ask still sends the anchor with the side "gets".

## Testing Decisions

A good test checks behavior that a manager or a caller can see: the trades that a search returns, the answer of the route, the page in a browser. It does not check the inside of a function, such as which tier of `varied` placed an offer.

The seams, highest first:

1. **The search, `search()` of the analyzer package, with the fake Jev of the tests.** Every offer sends at least one block player. A block player who fails the pool rules gives no offer and no error. Two picks with fair offers each give a list that holds both. Prior art: the anchor tests in the Finder search test file, such as "an anchor that the asker gives is in each offer on the asker side".
2. **The find route of the API, with its test client.** The route takes a block of 0 to 3 players. It rejects 4, a repeat, and a player of another roster with a 422. The cache key separates a block search from a plain one. Prior art: the find route tests in the API test file.
3. **The front door trade-ideas handler.** A "gives" ask sends a Trade block of one. A "gets" ask still sends the anchor. Prior art: the trade topics tests of the API.
4. **The Find hero on the site, in Vitest.** The strip lists only QB, RB, WR, and TE. A tap adds and removes a player. A 4th tap shows the reason. A team change clears the block. The find body carries `trade_block`. Prior art: the trade finder component tests and `findBody` tests.
5. **The Find hero in the browser, Playwright WebKit with the iPhone profile at 390x660, plus iPad 810x980 and 1080x740 and desktop 1280x800.** No text box overlaps another. No fixed bar covers content. A pick moves to the front. Prior art: the finder ledger and grade bar browser specs.

The pick of the Advisor is a Claude call, so a test checks its user message and its parse, not its choice. The spread of a live pick is evidence for an acceptance test, not a unit test.

## Out of Scope

- Players of other rosters on the block. The analyzer grades a trade for a known target.
- A block of more than one player in the front door chat. A later spec can add it.
- Three-team trades. Brian scrapped them in deadline-week decision 11.
- A stored block, across visits or devices.
- A mark on a block player in the Ledger card.
- A full pool check in the picker. It needs the slow sources in `/teams`.

## Further Notes

- The prototype stays on the branch `trade-block-01-proto` at `285f2789`, in the `block-proto` folder of the analyzer site form. A builder reads it for the motion and the copy, then writes the real part with tests. The prototype code never merges.
- The glossary already holds the term Trade block. The entry for the Partner filter says that a search with an anchor skips it, but the code runs the Spares tree with an anchor too. The build fixes that line of the glossary.
- The `finder` flag of the cpc client is a separate change. This spec does not turn it on.
