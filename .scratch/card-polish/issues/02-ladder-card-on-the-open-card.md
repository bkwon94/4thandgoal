# 02: LadderCard on the Open card

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-5 and AT-6.

**App:** site

**What to build:** The ladder of the rankings page uses the Open card with the full Showcase shell. The closed card shows the rank large in a plain raised panel, then the team, the record, the move, the odds bar, and the playoff chip. The open panel shows the overview line, the chips Stand, Form, Sched, Pts, Move, Bye, and Seed, and the blurb. The old ladder accordion and its `framer-motion` height animation go.

**Blocked by:** 01

**Status:** in-review

- [x] The card of The Blue Tent at week 8 shows 05, 9-7, ▲3, the odds bar, and Playoff 75%.
- [x] The open card shows Stand 6, Form 6, Sched 8, Pts 7, Move ▲3, Bye 22%, and Seed 5, then the blurb.
- [x] The page test of the rankings route passes with the new card.
- [x] `make check-fast` passes.
