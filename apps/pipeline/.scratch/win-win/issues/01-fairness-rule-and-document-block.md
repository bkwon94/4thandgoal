# 01 — Fairness rule and document block

**Repo:** pipeline. **Spec:** `.scratch/win-win/PRD.md`, phase 1.

**What to build:** A manager who grades a trade gets a fairness result beside the decision: `win_win` when both sides' final letters are B or better, `lopsided` when either side is D or worse, `fair` for the rest. Each side gets one reason, taken from the first adjuster with a step up in rubric order, or the start letter reason when no step is up. In a lopsided trade, `gives_more` names the side that gives more: the lower final letter, then the lower start letter at a tie. The rule lives in the rubric module beside the verdict rule. The function takes the letters that stand after the Claude call and the two breakdowns. The two bounds live in the tunable table, and the rubric file names them without their values. The result document builds the `fairness` block, with the sides in the order of the trade's sides. `DOCUMENT_VERSION` bumps, so an old cached document never serves without the block. `make analyze` prints the state and the two reasons.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] `WIN_WIN_AT_OR_ABOVE = "B"` and `LOPSIDED_AT_OR_BELOW = "D"` in the tunable table, with the reason. The rubric file has a Fairness section that names them.
- [x] A fairness function beside the verdict rule: the letters that stand and the two breakdowns in, a state, `gives_more`, and a reason per side out. Tests with fixture breakdowns: both B; A and B; both C; C and D; A and F; equal letters with different starts; a side with no step up.
- [x] The fairness text holds no letter, no trade value, no sum, no ratio, and no chart name, with a test.
- [x] The response document has a `fairness` block: `state`, `gives_more`, and `sides` with `roster_id` and `reason`, in the order of the trade's sides. `DOCUMENT_VERSION` bumps, with a test that the key changes, so an old document never serves without the block.
- [x] The fixture response document gains the block. It stays byte-identical with the site's copy after ticket 02.
- [x] `make analyze` prints the fairness line after the verdict.
- [x] `GLOSSARY.md` gains **Fairness** and **Good for both**.
- [x] `make test` passes. `make lint` stays at 123 or lower.

## Comments

2026-10-22: The fairness rule is in `src/cornerstone/rubric.py` beside the verdict, with its two bounds in the tunable table. It reads the final letter that stands per side, which is Claude's letter after the call and the rubric's letter without it. The document builder computes the block, and `DOCUMENT_VERSION` is now 3. The stored document holds no letter, so the block cannot come from a cached document. The sides of the block are in the order of the trade's sides, not asker first. Ticket 02 puts the asker first on the page. `cornerstone analyze` prints the fairness line and one reason per side after the verdict.
