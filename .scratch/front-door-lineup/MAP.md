# Front door lineup: map

App: both.
Spec branch: `front-door-lineup`.

## DESTINATION

One spec: a live Start or sit Topic that gives a manager a lineup with each Swap and Pivot explained, fifteen blocks in the Answers of the Topics and the free answers, and a row of Suggestions that fits one short row on a phone.

## DECISIONS SO FAR

- The goal, one spec, live Sleeper data only, free judgment by Jev, no backtest gate, every slot, the order of the day, the pivot line, the route of a typed two-player question, blocks in both paths, the words, thirteen blocks with a markdown text block, and the design bar. `decisions/01-grill-the-shape.md`.
- The Suggestions show names only in one 48 px row. A first tap shows the fact in a strip, and a second tap opens the Topic. The spec also fixes the ask box and the dock that cover the passphrase box above the iOS keyboard. `decisions/02-prototype-suggestions-row.md`.
- The game lock reads `start_time` and `has_started` of the Sleeper GraphQL `scores` query, with ESPN as the fallback. `decisions/06-research-game-lock.md`.
- The Start or sit blocks take the Ledger look: slot-order rows that open in place for a Swap or a Q, paired fact bars for the comparison, and the game card of variant C with a tug bar and a strip of 32 defenses. `decisions/03-prototype-lineup-blocks.md`.
- On the front door, the dock and the week pill leave. A header menu button opens a sheet of page rows, and the Suggestions row and the ask box sit on one flush bottom surface. Other pages keep the dock. `decisions/10-prototype-nav-place.md`.
- The nine other blocks take "Rows and marks": the Ledger rows of decision 03, each block with one small mark, such as a tug bar, a step path, odds bars, bars from a center line, or a dot matrix. `decisions/04-prototype-topic-blocks.md`.
- One block per Topic Answer, with optional text. Fifteen blocks: a waiver list and a sell list join the thirteen. The weekly build writes the blocks of six league Topics, and the API builds the rest, with the next matchup card live. The NFL game card shows only in a free answer. `decisions/05-grill-which-topic-shows-which-block.md`.
- The win odds of one game come live from the projection gap and the league spread. The Lean closes the trade card. The slot rank bars show QB, RB, WR, and TE. The median tick shows only in a league that plays the median. `decisions/11-grill-block-data-gaps.md`.
- The spec settles the Jev Swap question, the Suggestion fact of Start or sit, and the marks of the text block. `decisions/07-spec-jev-swap-question.md`, `decisions/08-spec-start-sit-suggestion-fact.md`, `decisions/09-spec-text-block-marks.md`.

## NOT YET SPECIFIED

None. The spec `PRD.md` holds every decision.

## OUT OF SCOPE

- A news source or a web fetch. Sleeper has no news text, and Jev cannot check a claim from a web page against our data.
- A second projection source, such as FantasyPros. It is a new feed and a separate decision.
- A backtest of the free judgment over weeks 2 to 9. Brian judges by feel. Run it if the feel turns bad.
- Betting lines and weather. They are not in our data.
- A DEF rank in the roster grade. The manager pages and the grade weights use the grade, so the change belongs to its own spec.
- A season score trend chart and a playoff odds bar. No Topic needs them yet.
