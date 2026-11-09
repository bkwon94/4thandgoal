# 01: The crack starts at the tap point

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests AT-1 to AT-8.

**App:** site

**What to build:** A manager taps the egg of a find card. The egg squashes, and crack lines spread out from the spot of the tap while the egg shakes and glows inside. The shell bursts into shards from the tap point, and the letter tile grows out of that spot. The letter and its copy show at about 1.3 s. Enter on the egg cracks it from its middle. Reduced motion shows the letter at once. Decision 01 and the canvas in the Further Notes of the spec show the chosen variant.

**Blocked by:** None. It can start now.

**Status:** in-review

- [x] A hunt test fires a pointer tap at a point of the egg and reads that the crack lines start at that point.
- [x] A hunt test reads two cracks at one tap point with two seeds, and the lines differ.
- [x] A hunt test presses Enter on the egg and reads a crack from the middle of the egg and then the letter.
- [x] The hunt test with motion off reads the letter at once, with no crack line.
- [x] The constant of the time from the tap to the letter is 1.3 s, and the hunt tests pass with it.
- [ ] A Chromium run with WebGL turned off plays the crack to the letter, and the page asks for no WebGL context.
- [x] No Scrolltide source is in the diff, and no dependency is added.
