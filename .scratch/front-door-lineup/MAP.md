# Front door lineup: map

App: both.
Spec branch: `front-door-lineup`.

## DESTINATION

One spec: a live Start or sit Topic that gives a manager a lineup with each Swap and Pivot explained, thirteen blocks in the Answers of the Topics and the free answers, and a row of Suggestions that fits one short row on a phone.

## DECISIONS SO FAR

- The goal, one spec, live Sleeper data only, free judgment by Jev, no backtest gate, every slot, the order of the day, the pivot line, the route of a typed two-player question, blocks in both paths, the words, thirteen blocks with a markdown text block, and the design bar. `decisions/01-grill-the-shape.md`.
- The Suggestions show names only in one 48 px row. A first tap shows the fact in a strip, and a second tap opens the Topic. The spec also fixes the ask box and the dock that cover the passphrase box above the iOS keyboard. `decisions/02-prototype-suggestions-row.md`.
- The game lock reads `start_time` and `has_started` of the Sleeper GraphQL `scores` query, with ESPN as the fallback. `decisions/06-research-game-lock.md`.
- The Start or sit blocks take the Ledger look: slot-order rows that open in place for a Swap or a Q, paired fact bars for the comparison, and the game card of variant C with a tug bar and a strip of 32 defenses. `decisions/03-prototype-lineup-blocks.md`.
- On the front door, the dock and the week pill leave. A header menu button opens a sheet of page rows, and the Suggestions row and the ask box sit on one flush bottom surface. Other pages keep the dock. `decisions/10-prototype-nav-place.md`.

## NOT YET SPECIFIED

- What do the blocks of the other Topics look like, in the Ledger look of decision 03? `decisions/04-prototype-topic-blocks.md`.
- Which Topic Answer shows which block? `decisions/05-grill-which-topic-shows-which-block.md`.
- What does Jev answer for a Swap? `decisions/07-spec-jev-swap-question.md`.
- What is the Suggestion fact of Start or sit? `decisions/08-spec-start-sit-suggestion-fact.md`.
- Which marks of markdown does the text block allow? `decisions/09-spec-text-block-marks.md`.

## OUT OF SCOPE

- A news source or a web fetch. Sleeper has no news text, and Jev cannot check a claim from a web page against our data.
- A second projection source, such as FantasyPros. It is a new feed and a separate decision.
- A backtest of the free judgment over weeks 2 to 9. Brian judges by feel. Run it if the feel turns bad.
- Betting lines and weather. They are not in our data.
- A season score trend chart and a playoff odds bar. No Topic needs them yet.
