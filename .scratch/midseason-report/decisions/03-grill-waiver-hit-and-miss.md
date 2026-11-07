# 03: How does the report score a waiver hit and a waiver miss?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Brian named the signals: points, a pickup that won a week, a pickup that became a regular starter, and the FAAB spent. The spec needs one score that ranks every waiver and free-agent add, and a rule for a miss. Choices: the weight of each signal; whether Key starter from the glossary is the regular-starter test; how a high bid that scored little counts; and whether a claim that failed can be a miss, for example the player that a team bid on and lost.

## Decision

Brian decided it in the grill on 2026-11-05.

- A pickup earns credit only for the starter points of the team that added it, with its starts and its swung wins. A swung win is a win that the player's own points decided.
- The hits list covers RB, WR, and TE, ranked by Points over the line: each start counts the points above that week's score at the line of the position, RB36, WR36, or TE24. The term reuses The line of the glossary, so the report has one baseline.
- Streamed QBs, defenses, and kickers feed a "streaming king" award, not the hits list.
- A miss cost 10% of the FAAB budget or more, and gave back 1 start or fewer, or Points over the line below zero. Misses rank by the dollars spent. A $0 add is never a miss.
- The outbid list pairs a lost claim with a pickup that became a top-5 hit, and shows the margin of the lost bid.
- The page shows the top 5 hits, the top 5 misses, and the top 3 outbid per league. Prototype 09 may change the counts.
- Each stint is its own pickup. A manager who drops a hit too early gets the "the one that got away" line, the same rule as the draft.
