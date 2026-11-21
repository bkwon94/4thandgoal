# 12: Fair Value offers: the Value screen and the fair check in both orders

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-55, AT-56, AT-57, AT-58, and AT-69.

**App:** api

**What to build:** A press builds its offers from the Value screen (decision 14, ADR 0038). Code builds each trade of the shapes 1-for-1, 2-for-1, 3-for-1, and 3-for-2, in both directions, from the players that pass the hard rules. The side that gets more players gets 100% to 125% of the trade value sum of the other side, and a 1-for-1 stays within 10% either way. Each player on a side of two or three players has at least 5 trade value. A player with no week 11 chart value never enters a Value offer. No cap follows the screen. The targets step and the wider pass go. An anchor player, and the keep and aim choices of a Limit, become hard rules on Value offers. Step 1 asks the fair Noul of each Value offer with the wording of decision 15, once in each side order, with `chart_value` on each player and `chart_sum` on each side in the state. Code takes the mean, and a clear no on the mean, below `NO_AT` 0.3, drops the offer. The stream reports the count of Value offers and the count checked for fairness.

**Blocked by:** 11

**Status:** done

- [x] A real press for Bo Girds and every team, on the 2026 week 11 snapshot, builds Value offers of all 7 shape directions.
- [x] Every Value offer of that press is inside the band with its direction, and no player under 5 trade value sits on a side of 2 or 3 players.
- [x] Justin Herbert, who has no chart value, is in no Value offer.
- [x] A test with fixed answers shows that 0.2 and 0.3 drop the offer and 0.1 and 0.6 keep it, and each fair request holds `chart_value` and `chart_sum`.
- [x] A press around Trey McBride gives Value offers that all hold him, and a press with an aim of RB gives Value offers that all bring Bo Girds an RB.

## Comments

The merge: `deadline-week-12` merged into `deadline-week` as a fast-forward before `dd5bde44` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/12-fair-value-offers.md.
Closes with the squash merge of the spec PR.
