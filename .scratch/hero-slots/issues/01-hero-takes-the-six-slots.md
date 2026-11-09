# 01: `Hero` takes the six slots, and the manager hero moves to them

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-1, AT-7, and AT-8.

**App:** site

**What to build:** A manager opens the manager page of roster 7, "To Infinity and Bijan", and the hero shows the six hero slots in order: the eyebrow "7-9 · 9th of 12", the title, the owner, the avatar with the grade mark and the week chips, and the odds tiles. On a phone the slots stack in one column. From the `tablet` tier up the hero takes the two rows of the spec, with a faded hairline above the stats. `Hero` takes the six named slots with their fixed styles and a heading-level prop, and it still accepts `children`, so the other ten heroes keep working until they move.

**Blocked by:** none

**Status:** done

- [x] `Hero` renders `eyebrow`, `title`, `meta`, `feature`, `stats`, and `action` in that order, and an absent slot renders no element. A Vitest test proves it.
- [ ] The title style is 40px, Space Grotesk 300, tight tracking, on every hero that uses the slots.
- [x] The heading-level prop renders an `h1` or an `h2` with the same look. A Vitest test proves it.
- [x] The manager hero of roster 7 shows the slot order of AT-1, with the week chips in `feature`.
- [ ] At 768 px the title sits top left, the meta top right, and the odds tiles bottom left (AT-7).
- [ ] The hairline shows above the odds tiles at 768 and 1280 px and not at 375 px (AT-8).
- [x] The other ten heroes render as before, and `make check-fast` passes.
