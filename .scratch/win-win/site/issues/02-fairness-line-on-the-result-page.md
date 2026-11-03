# 02 — Fairness line on the result page

**Repo:** site. **Spec:** pipeline repo `.scratch/win-win/pipeline/PRD.md`, phase 1.

**What to build:** A manager who reads a result sees a fairness line under the decision block and above the swap card. The line reads "Good for both", "Fair", or "Lopsided: <team> gives more." Under it sit two reasons, one per side, the asker's side first. The decision stays the lead of the page. The line reads the `fairness` block of the response document. A document without the block shows no line.

**Blocked by:** 01 — Fairness rule and document block (pipeline).

**Status:** done

- [x] The fixture response document is a byte-identical copy of the pipeline's after ticket 01.
- [x] The result component renders the three states, with a test per state. The lopsided line names the team.
- [x] The two reasons render under the line, the asker's first, with a test.
- [x] A document with no `fairness` block renders no line, with a test.
- [x] The line meets the reduced-motion rule like the decision block.
- [x] The tests pass.

## Comments

2026-10-22: The fixture is now a byte-identical copy of the pipeline fixture on `main`. The result page shows a Fairness chapter under the decision and above the swap card. The line reads "Good for both", "Fair", or "Lopsided: <team> gives more." The two reasons follow, the asker's side first, each under its team name. A document with no `fairness` block shows no chapter. The line uses `rise` with its own `DURATION.fairness` key, so reduced motion shows it at rest at once. Two old tests count the chart sentence, and the fixture fairness reason repeats that sentence. Those two tests now read a document without the block. All 180 tests pass.
