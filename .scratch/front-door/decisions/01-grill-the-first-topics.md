# 01: Which Topics are in the first build?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Choose the Topics of the first build, such as the recap, your matchup, your roster, weak spots, sell-high players, how your roster stacks up, rankings, the playoff race, waiver targets, and trade ideas. For each Topic, say if its facts exist now or if the pipeline must make them. Say also if the Topic is weekly or live. The spec needs the list, because each Topic is one Answer to build and one route for Jev.

## Decision

Brian, 2026-11-09, in a grill.

1. The first build has 13 Topics.
   - The facts exist now, and the Topic is weekly: the week recap, your last matchup, your next matchup, the power rankings, the playoff race, your season, and position leaders with recent trades.
   - Waiver targets are for the whole league now. The Topic fits them to your weak spots.
   - The personal Topics: how your roster stacks up, weak spots, and sell high or buy low.
   - Live Topics: trade ideas and the trade check. Decision 06 sets their border with `manager-brain`.
2. The personal Topics use the facts that exist now, with no new formula. "How you stack up" uses the four parts of the Roster grade and the slot ranks against the 11 other teams. "Weak spots" uses the depth and holes and the lowest slot ranks. For sell high or buy low, code puts each player's trade value, lineup value, trend of the last 4 weeks, and schedule ahead side by side. The Advisor picks the players and writes why. Reason: Jev and Claude judge, and code gives facts. A math screen failed for the Finder.
3. The league Topics reuse their blurbs and data that exist now. Claude writes new text only for the personal Topics, and the verifier and the Jev check run on it. Reason: the league text is the same for each manager and already passes the verifier.
4. The personal Topics are live. The API builds them when the manager asks, so they follow each waiver claim and trade. Brian chose this over a weekly build with a date and over a second build on Thursday. The cost and the wait of a live personal Answer are decision 11.
