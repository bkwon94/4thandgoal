# 10: Long stage lines fit

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-33 and AT-34.

**App:** site

**What to build:** The stage line of the wait is set at `text-body`, one step smaller than `text-lead`. A line that does not fit the width of the hero scrolls into view from right to left, once, inside its 2.5 s, so it never shows cut off. A line that fits does not move. With motion off, a long line wraps to a second line and does not scroll. The status region keeps its one label, so a screen reader still hears one message. Follow the decision in `decisions/06-prototype-compact-stage-and-edit.md` and the design bar of the spec.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Each stage line has the computed font size of `text-body`.
- [ ] At 375 px with trade B, a line wider than the hero scrolls until its end is in view, within its 2.5 s.
- [x] A line that fits does not move.
- [ ] With reduced motion at 375 px, a long line wraps in full and does not move.
- [x] The accessibility tree in the wait still shows one status, "Grading the trade", and no stage line.
