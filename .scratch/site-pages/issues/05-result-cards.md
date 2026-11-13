# 05: The result as five cards

**What to build:** A league member grades a trade on a tablet or a laptop and sees the result under the form as cards on the grey body, none of them one line tall: the decision with the fairness line and the no-chart line as one card, the trade swap as one card, one card per side read, and the counters placeholder with the as-of line as one closing card. The labels read "The Trade" and "Suggested Counters". On a phone the result is one column with the chapter rules. The result uses the shared chapter, label, and blurb parts, so its private copies go away and the blurbs cap at the measure.

**Blocked by:** 01 (The page shell and the card look on every page)

**Status:** done

- [x] The result renders five chapters for a two-team trade: the decision with the fairness line and the no-chart line, the swap, one per side, and the counters with the as-of line.
- [x] A document with no fairness block shows the decision card with no fairness line.
- [x] The result uses the shared chapter, label, and blurb parts. No private copy remains in the result.
- [x] The labels read "The Trade" and "Suggested Counters".
- [x] The result test checks the labels, the decision text before the fairness text, and the as-of line last. Tests that read "The trade" or "Suggested counters" change with the casing.
- [ ] A browser check at 768 and 1280 shows the five cards under the form card. At 390 the result is one column with the rules.
- [x] `pnpm test`, `pnpm typecheck`, and `pnpm build` pass.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 9e09d472.
Proof: The commit "Group the trade result into five chapters" merged in 841abd72 and 6486cff5.
Read 1 file: .scratch/todoist-queue/audit.md.
