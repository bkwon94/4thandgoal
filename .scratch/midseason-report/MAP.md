# Midseason report: map

App: both.
Spec branch: `midseason-report`.

## DESTINATION

One spec for a `midseason` package that both clients turn on. Brian runs its build by hand for one week. The writer writes the prose, and the site shows the report at `/midseason/2026` in the redesign look, with a home takeover. The goal: a league manager who reads it is blown away.

## DECISIONS SO FAR

- One spec. The simulator is one chapter of the report, not a second spec. Brian, in the stage 1 grill.
- The build runs once, by hand, for the week that Brian names. The build takes the week as input, so it can run again later. Brian, in the stage 1 grill.
- A manager finds the report through a home takeover: the home hero shows the report for a time, and a home tile stays. The dock does not change. Brian, in the stage 1 grill.
- The route is `/midseason/2026`. Brian, in the stage 1 grill.
- The glossary terms are **Midseason report**, **Arc**, and **Draft value**. Arc is not Storyline, which stays the reason a next-week game matters. Brian, in the stage 1 grill.
- The report has 14 chapters: the state of the league, arcs, top performers, draft steals and busts, waiver hits and misses, the trade report card, the sim, the look ahead, luck, the schedule swap, lineup choices, the record book, injury luck, and midseason awards. Prototype 09 may merge chapters. Brian, in the stage 1 grill.
- The report is a package, `midseason`, and both clients turn it on. Brian, in the stage 1 grill.
- The writer writes all the prose from the facts, and Brian reviews the draft before the publish. Brian, in the stage 1 grill.
- The roast has no limit on heat for football decisions. Life outside fantasy is off limits, with no profanity or slurs at a person. Each roast cites a fact. Each client has a `roast` setting. Brian, in the stage 1 grill.
- No outside ADP source. Draft value reads each league's own draft: dollars in the CPC auction, pick number in the NorCal snake. Brian, in the stage 1 grill.
- The site tickets wait for the merge of `site-redesign` into `main`. The pipeline tickets do not wait. The flow, ADR 0019.
- Sleeper gives the draft, the FAAB bids, and the lost bids. The report fetches each week's transactions again, because the history is incomplete. Injuries come from nflverse, by week. `decisions/01-research-sleeper-season-data.md`.
- Eight arcs. Start and now windows of 4 weeks, with 65% and 35% lines. The full record for window arcs, and head to head only for streaks. At most 2 per team. `decisions/05-grill-the-arcs.md`.

## NOT YET SPECIFIED

- What is the Draft value rule for a steal and a bust, in an auction and in a snake? `decisions/02-grill-draft-value-rule.md`.
- How does the report score a waiver hit and a waiver miss? `decisions/03-grill-waiver-hit-and-miss.md`.
- What is the rubric of a trade's grade to date, and how does it relate to the analyzer's grade? `decisions/04-grill-trade-grade-to-date.md`.
- How does the report measure luck, an overachiever, and the schedule swap? `decisions/06-grill-luck-and-schedule-swap.md`.
- Which sim model runs the rest of the season, and which inputs does it read? `decisions/07-research-the-sim-model.md`.
- Does the sim replay prebuilt runs, or does the reader pick winners live? `decisions/08-prototype-the-sim-interaction.md`.
- What are the order, the look, and the merges of the chapters? `decisions/09-prototype-the-chapters.md`.
- Which awards, top performers, and players to watch does the report name? `decisions/10-grill-awards-and-players.md`.
- How long does the takeover last, what is the build command, how does the review run, and what scale has the `roast` setting? `decisions/11-spec-takeover-build-review-roast.md`.

## OUT OF SCOPE

- A weekly rebuild of the report. Brian wants one edited moment per season, and the build can run again by hand.
- A dock item for the report. The dock has five fixed items, and the takeover and the tile are enough.
- An outside ADP source. Each league's own draft is the baseline.
- A report for a season other than 2026. The build takes the season as input, but only 2026 ships.
- An injury date finer than the NFL week. No source gives one.
- A live sim on a server. Ticket 08 decides between replay and a live sim in the browser. A server sim is past the destination.
