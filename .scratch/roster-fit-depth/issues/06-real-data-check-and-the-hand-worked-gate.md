# 06: Real-data check and the hand-worked gate

Spec: `.scratch/roster-fit-depth/PRD.md`, "Testing Decisions", "Real-data check". Decision record: ADR 0003.

**What to build:** The week 6 hand-worked trades run on the whole branch, and the report lists every grade that
moves with its old letter, its new letter, and the hole or rank that moved it. Brian says yes or no to each before
the branch merges to main. One live grade through `make analyze` with a trade that opens a hole, read by hand:
the fit reason, the slot facts, the hole fact with the free agent, and the analysis paragraph. One finder call
between two rosters, read by hand: no offered trade empties a starting slot. The glossary, ADR 0003, the rubric
prompt, and every new reason pass `ste`.

**Blocked by:** 03 (A bye or a return with no cover is a hole), 04 (Depth, strength, and slot facts for Claude),
05 (The best free agent at a hole).

**Status:** done

- [ ] The report lists every hand-worked trade whose letter moves, with old and new letters and the cause.
- [ ] Brian has said yes or no to each moved grade, and the ledger records each ruling.
- [ ] A live grade with a trade that opens a hole shows the hole in the fit reason, the free agent in the facts, and the hole in the analysis paragraph.
- [ ] A live finder call offers no trade that leaves a starting slot below the line.
- [ ] `ste` passes on the glossary entries, ADR 0003, and the rubric prompt.
- [ ] The suite passes on main after the merge, and ruff is clean.

## Comments

- 2026-11-02: `main` holds the merge 84d9349. Status set to done by the state-file sweep of agent-habits 02.
