# 09: Can Jev rank the facts of a Finder trade well enough for a card?

Map: `.scratch/jev/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

Your-league ticket 04 asks whether each Finder trade gets a Claude sentence. A fourth option is to ask Jev for one Score per fact: "How much does this fact matter to this side?"
The card then shows the top 2 fact texts that code already writes, with no Claude call. All 10 trades go in one Jev request.

This spec builds nothing for it. The result goes to your-league ticket 04, and the your-league spec builds it.

Run the Finder on the week 8 rosters for 3 or 4 teams. Send each `trade_fact_sheet` to Jev. Find out:

1. Whether the top 2 facts per trade read well beside the Claude sentence from `write_reasons`.
2. The latency of one request for 10 trades.
3. Whether the order of the facts changes the answer, because Jev favors the first option.

Write the findings to `decisions/09-research-finder-fact-rank.notes.md`, and show Brian the cards side by side. Keep the names of managers out of tracked files (ADR 0021).

## Decision

None yet.
