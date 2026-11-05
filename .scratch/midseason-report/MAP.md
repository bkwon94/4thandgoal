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
- The report has 14 chapters: the state of the league, arcs, top performers, draft steals and busts, waiver hits and misses, the trade report card, the sim, the look ahead, schedule luck, the schedule swap, lineup choices, the record book, injury toll, and midseason awards. Prototype 09 may merge chapters. Brian, in the stage 1 grill.
- The report is a package, `midseason`, and both clients turn it on. Brian, in the stage 1 grill.
- The writer writes all the prose from the facts, and Brian reviews the draft before the publish. Brian, in the stage 1 grill.
- The roast has no limit on heat for football decisions. Life outside fantasy is off limits, with no profanity or slurs at a person. Each roast cites a fact. Each client has a `roast` setting. Brian, in the stage 1 grill.
- No outside ADP source. Draft value reads each league's own draft: dollars in the CPC auction, pick number in the NorCal snake. Brian, in the stage 1 grill.
- The site tickets wait for the merge of `site-redesign` into `main`. The pipeline tickets do not wait. The flow, ADR 0019.
- Sleeper gives the draft, the FAAB bids, and the lost bids. The report fetches each week's transactions again, because the history is incomplete. Injuries come from nflverse, by week. `decisions/01-research-sleeper-season-data.md`.
- Eight arcs. Start and now windows of 4 weeks, with 60% and 40% lines. The full record for window arcs, and head to head only for streaks. At most 2 per team. `decisions/05-grill-the-arcs.md`.
- Draft value compares within the position: the cost rank against the points rank on total points. Busts have a hurt or just-bad tag. Starter ranges, top 5 each, and the drafter owns the label. `decisions/02-grill-draft-value-rule.md`.
- The sim keeps the `odds.py` draw and adds the bracket, with CPC reseeded, plus full counts and 10,000 runs. It orders by mean wins with a seed heat map, and stores 200 sample runs and the parameters. `decisions/07-research-the-sim-model.md`.
- The fix for the gap in the transaction history is its own spec, `transaction-history`, before the week 9 build. `decisions/12-research-transaction-history-gap.md`.
- A pickup earns credit for starter points for its adder, with starts and swung wins. RB, WR, and TE rank by Points over the line, streamers feed a streaming king award, a miss cost 10% of the budget or more, and an outbid list shows lost bids. `decisions/03-grill-waiver-hit-and-miss.md`.
- Each trade gets a Trade result from net Points over the line since the trade: Robbery, Clear win, Slight edge, Push, or Too soon. The record since is context, and "hurt on arrival" is a tag. Every trade shows, with the top 3 as cards. `decisions/04-grill-trade-grade-to-date.md`.
- Schedule luck is head-to-head wins minus All-play wins, with no median game. Lines of +1.5 and -1.5 give Smoke and mirrors and Snakebit. The Schedule swap is a 12 by 12 grid with the self-meet rule, and CPC cells keep the median game. Points against and close games under 5 points are context only. The injury luck chapter is Injury toll. `decisions/06-grill-luck-and-schedule-swap.md`.
- The sim is a replay of one stored run per press, beside the odds of all runs. No reader picks. It plays the regular season, freezes the final standings, then plays the bracket by round to a champion, with a clear split. `decisions/08-prototype-the-sim-interaction.md`.
- The replay moves like a sports broadcast: a lower third each week, a red PLAYOFFS wipe, a bracket that draws in, winners that slide along the lines, and a full champion card. About 20 seconds, with a skip and a reduced-motion version. `decisions/13-prototype-the-replay-motion.md`.
- The sim is a module that plugs in anywhere, not a part of the report alone. Its engine and its replay part do not depend on the `midseason` package, so a weekly page or a standalone sim page can use it later. The spec sets the package boundary. Brian, on 2026-11-05.
- The top performers chapter is the Position top 10: QB, RB, WR, TE, and DEF in CPC, by total league points, every NFL player, one position at a time. Seven awards from one fact each: MVP, Streaming king, Bench crime, Heartbreak, Beatdown, Most active, and Set and forget. Players to watch: Due to rise, Due to fall, and Grab him now. `decisions/10-grill-awards-and-players.md`.

## NOT YET SPECIFIED

- What are the order, the look, and the merges of the chapters? `decisions/09-prototype-the-chapters.md`.
- How long does the takeover last, what is the build command, how does the review run, and what scale has the `roast` setting? `decisions/11-spec-takeover-build-review-roast.md`.

## OUT OF SCOPE

- A weekly rebuild of the report. Brian wants one edited moment per season, and the build can run again by hand.
- A dock item for the report. The dock has five fixed items, and the takeover and the tile are enough.
- An outside ADP source. Each league's own draft is the baseline.
- A report for a season other than 2026. The build takes the season as input, but only 2026 ships.
- An injury date finer than the NFL week. No source gives one.
- The fix of the transaction history. It ships first as the spec `transaction-history`.
- A comparison of the Trade result with the analyzer's Grade at the time. The rubric changed since weeks 1 to 6, so it needs a re-run of the analyzer on old trades.
- The sim on a weekly page or as a standalone page. The sim is built as a module so this can come later, but only the report ships it now.
- A live sim, on a server or in the browser. Ticket 08 chose a replay, because Brian found a pick for a game confusing.
