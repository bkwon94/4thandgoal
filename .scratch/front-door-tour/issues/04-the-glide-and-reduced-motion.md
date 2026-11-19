# 04: The glide, and the Tour under reduced motion

Spec: `.scratch/front-door-tour/PRD.md`. Acceptance tests AT-15, AT-20, and AT-21.

**App:** site

**What to build:** The hole and the card move between Stops on the same `GLIDE` spring, so the two never part. When the card changes side of its control, it fades out, holds its place, and fades back in once the hole lands. On a move that scrolls the page, the scroll ends first, then the Tour measures and glides. The dim fades in on `FAST` and out on `QUICK`. The card opens as Menu dropdown (05) and closes on `QUICK`. The header, the line, and the count change as Text swap soft (34). Under reduced motion, each Stop still shows. The hole jumps, the card fades with no glide and no scale, the text swaps by opacity only, and the scroll into view is not smooth.

**Blocked by:** 03

**Status:** in-review

- [x] During a move at 390x660, the card stays within 2 px of its offset from the hole at rest, until it changes side (AT-15).
- [x] Under reduced motion, no frame sample shows the hole between two Stops, and Stop 2 shows its full copy (AT-20).
- [x] Under reduced motion, no frame sample shows a `blur` filter on the card text or a scale other than 1 on the card (AT-21).
- [x] The motion uses only the tokens of the front door `motion` module, with no second token block.
- [ ] The ticket uses the design bar: `transitions-dev`, scrolltide, `apple-design`, `animate`, `critique`, and `polish`.
