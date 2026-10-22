# 01 — Fairness rule and document block

**Repo:** pipeline. **Spec:** `.scratch/win-win/PRD.md`, phase 1.

**What to build:** A manager who grades a trade gets a fairness result beside the decision: `win_win` when both sides' final letters are B or better, `lopsided` when either side is D or worse, `fair` for the rest. Each side gets one reason, taken from the first adjuster with a step up in rubric order, or the start letter reason when no step is up. The lopsided state names the side that gives more: the lower final letter, then the lower start letter at a tie. The rule lives in the rubric module beside the verdict rule, the two bounds live in the tunable table, and the rubric file names them without their values. The response document gains a `fairness` block computed at response time from the sides, so a cached document gets it too and the cache key stays. `make analyze` prints the state and the two reasons.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `WIN_WIN_AT_OR_ABOVE = "B"` and `LOPSIDED_AT_OR_BELOW = "D"` in the tunable table, with the reason. The rubric file has a Fairness section that names them.
- [ ] A fairness function beside the verdict rule: two breakdowns in, a state and a reason per side out. Tests with fixture breakdowns: both B; A and B; both C; C and D; A and F; equal letters with different starts; a side with no step up.
- [ ] The fairness text holds no letter, no trade value, no sum, no ratio, and no chart name, with a test.
- [ ] The response document has a `fairness` block: `state`, and `sides` with `roster_id` and `reason`, the asker first. A cached document without the block gets it at response time, with a test. The cache key does not change, with a test.
- [ ] The fixture response document gains the block. It stays byte-identical with the site's copy after ticket 02.
- [ ] `make analyze` prints the fairness line after the verdict.
- [ ] `GLOSSARY.md` gains **Fairness** and **Good for both**.
- [ ] `make test` passes. `make lint` stays at 123 or lower.
