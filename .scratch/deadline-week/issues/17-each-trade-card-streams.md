# 17: Each trade card streams

Spec: `.scratch/deadline-week/PRD.md`. Decision 20. Acceptance test AT-72.

**App:** both

**What to build:** The pick call streams its answer. As soon as one trade of the pick stands, with its guards passed or repaired, the API sends it as a trade event of the find stream, with the same fields as a trade of the find answer. The last event still carries the whole find answer, so a client that reads only the end keeps working. The site shows each card as its event comes, with the rise transition, in pick order. A line under the cards counts the trades still to come, such as "Writing 4 more trades", until the last card shows. The near fold shows at the end. The pick keeps effort medium and up to 5 trades (decision 20).

**Blocked by:** 16

**Status:** done

- [x] A test shows that the find stream sends each trade as its own event before the final answer, with the same fields as the trade in the final answer.
- [x] A real press for Bo Girds on the local API sends the first trade event before the last one, with the time of each.
- [x] A site test shows each card as its event comes, and the count line counts down to none.
- [x] A real press on a local build shows the first card before the last, at 375, 768, and 1280 px, in both themes.

## Comments

The merge: `deadline-week-17` merged into `deadline-week` as a fast-forward before `08552a27` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/17-each-trade-card-streams.md.
Closes with the squash merge of the spec PR.
