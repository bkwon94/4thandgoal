# 06: What does the analyzer look like in the look?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** 03, 04

**Status:** done

## Question

The analyzer grades a trade, so it must feel quick and sure. Settle the team picker, the player lists, the pick state, and the result view in the look. The result view keeps the decisions of `.scratch/grade-clarity/` about its content. The spec needs each state of the analyzer: empty, picked, loading, result, and error.

## Decision

The analyzer uses board "Analyzer 1 · Stack", with the picker of board "Picker 3 · Gets". Brian chose this on 2026-11-05, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. The trade finder was in scope, and it follows the Stack too.

The page is one scroll, in this order:

1. The title: "Trade Analyzer" and "Who gets what?".
2. The teams row: an avatar for each team of the trade, with its number, and a "+" slot with "<n> of 4". A tap on "+" opens a short sheet of every team. A team that is in the trade shows dimmed.
3. One card for each team: "Your Team gets", "Team Two gets", and so on. Each card lists the players the team gets. Each player shows a "from <team>" tag. Team Three and Team Four have a remove button.
4. A line that says each team gives and gets at least one player.
5. The bar "Grade the Trade" sits on the dock, so it stays in reach at every scroll.

The picker:

- A tap on "Add a player <team> gets" opens a short sheet. It has a tab for each other team of the trade, a search field, and the position chips All, QB, RB, WR, TE, and DEF. A tap on a row toggles a check.
- The sheet closes three ways: the Done button with the count, the close button, and a tap on the dim page.
- A pick names its source team, and the card names the team that gets it. So the form has no send-to control. The body of `POST /analyze` stays the same: each pick becomes a `gives` entry of the source side, with `to` set to the card team.
- The picker is the same for 2, 3, and 4 teams.

The states:

- **Empty:** the teams row with Your Team and Team Two, two empty cards, and the bar turned off.
- **Loading:** the form folds to one line of faces. The hero waits for the verdict, with the grid, the brackets, the scan line, two pulsed bars, and the sweep. The copy is "Grading the Trade" and "This can take up to a minute on a new chart week." The bar reads "Grading…".
- **Result:** the verdict fills the hero, with the fairness block under it. Then come the trade, one card for each side, Suggested Counters, and the as-of line. The content stays as `.scratch/grade-clarity/decisions/04-prototype-result-view.md` sets it.
- **Error:** the form unlocks. A box with the alert icon, the message, and "Try Again" sits above the bar. The messages stay as `toErrorLine` writes them.
- **3 teams or more:** the swap card shows one row for each team, with "You Give" or "Gives", then "You Get" or "Gets". Each player shows a "TO <team>" or "FROM <team>" tag.

The finder, for a client with `finder = true`:

- The card "Find a Trade" sits under the form: the copy, the Trade Partner row with "Change", and the "Find a Trade" button.
- While it runs, the button reads "Finding…", with the sweep and the status line of the code.
- The result shows up to three cards. Each card has the swap, the Fairness pill, the reason for each side, the reason of the trade, and "See the Full Result". The as-of line comes last.

Brian picked the Stack over board "Analyzer 2 · Face-off" and board "Analyzer 3 · Steps". He liked its design and its loading state. Then he asked for 3 teams and an easier picker, because of four problems of the form now: the dropdowns cover the screen, they are hard to close, the third team is hard to find, and the send-to control is not clear. He took Claude's recommendation of the picker "Gets" over board "Picker 1 · Sheet" and board "Picker 2 · Inline". The reason: those two keep a send-to control, and "Gets" removes it. He also approved the 3-team result as drawn.

The boards showed two facts. First, the text of the grade fixtures names teams that are in no league now, so their avatars show initials. The fallback of the look covers it. Second, "Suggested Counters · No counters yet." is a fixed placeholder in the code. The boards keep it, because this ticket changes the look, not the content.

All the states use only the data that the API returns now, so the list of ideas that need new data stays empty.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete.
