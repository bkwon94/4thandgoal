# 06: The math of the scene

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-38.

**App:** site

**What to build:** The hero scene has a plain data shape and pure functions that a test checks with no canvas: the place of each light in a box, the nearest light to a point, the side of a label near an edge, and the place of the margin mark clear of every label. A builder makes the data of the Matchup scene from the real week 8 fixture.

**Blocked by:** none

**Status:** ready-for-agent

- [x] The data shape holds lights with an x value, a y value, a label, and a tone of `flare`, `bright`, or `dim`, plus guide lines, an optional margin mark, the index of the label at rest, and a mode of `settle` or `drift`.
- [x] A test proves that the nearest light to a point in empty space is the closest light.
- [x] A test proves that a label near the right edge flips to the inner side and stays inside the box.
- [x] A test proves that the margin mark "+1.43" of week 8 overlaps no label, also while the winner is selected.
- [x] The builder of the Matchup scene gives 12 lights from low to high, a median of 99.60, and The Blue Tent and London Cooking as `flare`, from the real week 8 fixture.
- [x] The tests pass with `pnpm test` (AT-38).
