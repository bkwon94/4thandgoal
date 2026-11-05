# 04: The form of a row, and the deal, roster, and standing rows

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-19, AT-20, AT-22, AT-23, and AT-35.

**App:** pipeline

**What to build:** A row shows only when it moves the grade or says something new. Each row is one plain sentence, and its mark shows the step. No bullet, row, or verdict reason uses an inner word. The deal row, the roster row, and the standing row read as decision 03 says.

**Blocked by:** 01, 02, 03.

**Status:** ready-for-agent

- [ ] A row that says nothing, such as "No player it gets is a handcuff", is not in the document.
- [ ] No row says "one step up", "one step down", or "no step".
- [ ] A check rejects each banned word of decision 03 in a bullet, a row, and the verdict reason. The analysis prompt lists the same words. Rule 10 of the prompt goes.
- [ ] The roster row counts the players in the top N at each position the trade touches, before and after, such as "You keep 3 WRs in the top 36, and you get the better player."
- [ ] The standing row names the race, the need, and whether the trade meets it, in one sentence.
- [ ] No document has an expected gap row.
- [ ] `make check-fast` passes at the root.
