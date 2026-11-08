# 05: Where the blurb of the Matchup of the Week goes

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The blurb of the Matchup of the Week is about 90 words. In the prototype of decision 01 it made the hero twice as tall as the others on a phone. Two paths:

1. Move the blurb out of the hero, into a paragraph directly under it in the same chapter. The hero keeps the title, the meta, the team rows, and the share bar.
2. Keep the first sentence in the hero and fold the rest behind a "Read more" control.

Path 1 needs no new control and no new test of a toggle, so it is the default. The spec records the choice.

## Decision

Path 1, the default of this ticket. The blurb moves out of the hero, into a paragraph directly under it in the same chapter, with no "Read more" control. `PRD.md` records it under Implementation Decisions, 2026-11-07.
