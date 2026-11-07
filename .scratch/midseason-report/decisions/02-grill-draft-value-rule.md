# 02: What is the Draft value rule for a steal and a bust?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Draft value is a player's points so far against his draft cost: dollars in the CPC auction, pick number in the NorCal snake. The spec needs one rule per draft type for a steal and for a bust. Choices: points or points per game; position rank against cost rank or points per dollar; how a player who missed weeks to injury counts; a minimum cost for a bust; and whether the roster that drafted the player keeps the credit after a trade or a drop.

## Decision

Brian decided it in the grill on 2026-11-05.

- A pick compares within its position: the cost rank at the position against the points rank at the position. The cost is the price in CPC and the pick number in NorCal. The swing is the cost rank minus the points rank.
- The points rank reads total points to date, not points per game, because the report grades the pick.
- A bust has a tag from the nflverse weekly injury status: "hurt" if he missed 2 or more games with an injury, else "just bad". The tag changes the roast, not the rank.
- A bust was drafted as a starter, and a steal plays like a starter now. That means a rank in the top 12 for QB and TE, and in the top 24 for RB and WR. Kickers and defenses are out.
- The page shows the top 5 steals and the top 5 busts per league. Prototype 09 may change the count.
- The drafter owns the label, and the points count the player's whole season on any roster. A steal that the drafter dropped or traded before his rise gets a "the one that got away" line. A bust bought in a trade belongs to the trade report card.
