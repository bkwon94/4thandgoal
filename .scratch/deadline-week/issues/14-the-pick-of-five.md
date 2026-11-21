# 14: The pick of 5, with the totals and ranks in the find answer

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-41 and AT-70.

**App:** api

**What to build:** The pick call reads the Shortlist of 10, labelled `A` to `J`, and picks up to 5 trades and up to 3 near ideas, across all partners in one call. It can pick fewer when fewer are good. The pick sheet carries the Spares tree facts and the need and gain answers as reasons for the Case. The find answer of each trade and each near idea carries the trade value total of each side and the position, NFL team, and rank of each player, so the Ledger card of ticket 15 needs no second call (decision 17).

**Blocked by:** 13, 16

**Status:** done

- [x] Three real presses for Bo Girds and every team each run one pick call, and no id retry line shows in the log.
- [x] The picks of a real press for Bo Girds hold at least 2 shapes and at least 3 partners.
- [x] The find answer of each trade holds the trade value total of each side and the position, NFL team, and rank of each player.

## Comments

The merge: `cab14134` merged `deadline-week-14` into `deadline-week` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/14-the-pick-of-five.md.
Closes with the squash merge of the spec PR.
