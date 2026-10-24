# 10: The price is flat per position

**What to build:** On the fresh week 6 board of 2026-10-24, every WR cost $29, every RB $14, every TE $9, and every QB $9 or $6. The floor, the last winning claim at the position in the last 3 weeks plus one, beats every expected rival bid, so the board score term never shows. Make the price follow the player. Options to weigh in a grill: scale the floor by the player's board score, so the floor is the full last win only for a top player; use the median of the last three wins at the position instead of the last one; or let the expected rival bid rise with the trending count, since a player added in 400,000 leagues draws bids. One rule, one tunable, and a test that two players at one position get two prices on a realistic fixture.

Also: the drop fact reads "projects 1 points a week higher" at a margin of 1.0. Make the unit agree with the number.

**Blocked by:** None (can start immediately). Found on the real week 6 board, 2026-10-24.

**Status:** needs-triage

- [ ] Two players at one position with different board scores get different prices on the fresh week 6 raw.
- [ ] The rule is one tunable with a reason comment, and the PRD price bullet records it.
- [ ] The drop fact says "point" at a margin of 1 and "points" otherwise.
