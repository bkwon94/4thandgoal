# 10: Long stage lines fit

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-33 and AT-34.

**App:** site

**What to build:** The stage line of the wait is set at `text-body`, one step smaller than `text-lead`. A line that does not fit the width of the hero scrolls into view from right to left, once, inside its 2.5 s, so it never shows cut off. A line that fits does not move. With motion off, a long line wraps to a second line and does not scroll. The status region keeps its one label, so a screen reader still hears one message. Follow the decision in `decisions/06-prototype-compact-stage-and-edit.md` and the design bar of the spec.

**Blocked by:** none

**Status:** done

- [ ] Each stage line has the computed font size of `text-body`.
- [ ] At 375 px with trade B, a line wider than the hero scrolls until its end is in view, within its 2.5 s.
- [x] A line that fits does not move.
- [ ] With reduced motion at 375 px, a long line wraps in full and does not move.
- [x] The accessibility tree in the wait still shows one status, "Grading the trade", and no stage line.

## Comments

The merge: `1720ae36` merged into `analyzer-stage` on 2026-11-17; review fixes `a8f2b48d` and `4eb5bef2`; Judge fix round `7b1d09c7`.
The proof: `make check-fast` passed at each merge, the full check passed on 2026-11-17, and the Judge gave PASS to AT-1 to AT-34 after one fix round.
The note: A long line shows a hard cut at the right edge before it scrolls, because the line has no edge fade.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/analyzer-stage/PRD.md, .scratch/analyzer-stage/ACCEPTANCE.md, .scratch/analyzer-stage/issues/10-long-stage-lines-fit.md.
Closes with the squash merge of the spec PR.
