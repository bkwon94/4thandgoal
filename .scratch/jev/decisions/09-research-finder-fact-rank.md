# 09: Can Jev rank the facts of a Finder trade well enough for a card?

Map: `.scratch/jev/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

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

The research agent ran on 2026-11-09, on the saved week 8 data. The findings are in `decisions/09-research-finder-fact-rank.notes.md`. The spend was $0.092 on Jev and 3 Claude calls.

1. **About half the cards read well.** Need facts took 34 of 108 top-2 slots, and a code filter on the fact kind fixes most of that. 17 of 27 Claude sentences use the Upside line, which sits in the grade lines, not in the fact sheet, so Jev cannot rank it.
2. **The latency** is 0.39 s median for one request of 8 to 10 trades. One `write_reasons` call takes 21 s to 27 s.
3. **The order of the trades in one state matters.** Reversed, 57% of sides change their top 2. One request per trade removes that effect. A plain repeat still changes 15% to 24%, because of near ties.

A Jev fact card is a real fourth option for your-league ticket 04, beside option 3. It needs a filter on the fact kind, one request per trade, a question on direction, and the result cache. It does not replace the Claude sentence. Brian decides in your-league ticket 04.
