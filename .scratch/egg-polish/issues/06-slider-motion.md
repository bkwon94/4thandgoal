# 06: The motion of the slider

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests AT-24 and AT-30.

**App:** site

**What to build:** A side swipe on the slider moves to the next or the last slide, and a vertical swipe stays a page scroll. A move rolls the slides with a blur on the neighbors, the giant word swaps letter by letter, and a move to a won slide washes the frame red. Reduced motion makes each move instant. The method comes from the Stack Slider item of Scrolltide, and ADR 0028 covers its motion.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] A board test fires a side swipe and reads the next slide selected.
- [ ] A board test fires a vertical swipe and reads that the slide does not change.
- [ ] The board test with motion off reads an instant change after a tab tap.
- [ ] No Scrolltide source is in the diff, and no dependency is added.
