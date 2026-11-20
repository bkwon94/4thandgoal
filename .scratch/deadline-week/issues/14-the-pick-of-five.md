# 14: The pick of 5, with the totals and ranks in the find answer

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-41 and AT-70.

**App:** api

**What to build:** The pick call reads the Shortlist of 10, labelled `A` to `J`, and picks up to 5 trades and up to 3 near ideas, across all partners in one call. It can pick fewer when fewer are good. The pick sheet carries the Spares tree facts and the need and gain answers as reasons for the Case. The find answer of each trade and each near idea carries the trade value total of each side and the position, NFL team, and rank of each player, so the Ledger card of ticket 15 needs no second call (decision 17).

**Blocked by:** 13

**Status:** ready-for-agent

- [ ] Three real presses for Bo Girds and every team each run one pick call, and no id retry line shows in the log.
- [ ] The picks of a real press for Bo Girds hold at least 2 shapes and at least 3 partners.
- [ ] The find answer of each trade holds the trade value total of each side and the position, NFL team, and rank of each player.
