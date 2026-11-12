# 02: How do the Suggestions fit one short row on a phone?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

At 375 px, "More" and 3 chips wrap to two rows of about 107 px (`.scratch/front-door/evidence/AT-4/row-375-light.txt`). Long facts make the chips wide. The spec needs the layout and the length cap of a fact.

Options to show on the preview:

1. One row that scrolls sideways, about 50 px high, with short facts such as "Allgeier: 12.7 a game".
2. Names only, with the fact on tap.
3. The Suggestions only in the dock after the first Answer.

Search scrolltide first. Use `transitions-dev`, `apple-design`, and `critique`. Give the prototype its own port, not 3000 or 8090.

## Decision

Brian chose variant B on 2026-11-11, on his iPhone, over A (one sideways row with a 24-character cap) and C (the dock only).

1. Each chip shows only the Topic name, in one row of about 48 px at 375 px wide, at every Thread state. "More" leads the row.
2. The first tap on a chip opens a full-width strip of about 44 px under the row, with the whole fact and "Open →". A second tap on the chip or on the strip opens the Topic. A tap on another chip cross-fades the strip to its fact with a soft blur.
3. The reveal is a tap, not a long press. A long press is hard to find on the web, and it fights the text callout of iOS.
4. The strip is full width, so a fact needs no length cap. Decision 08 still keeps the fact short.
5. The morph from a chip into its question, the "More" panel, reduced motion, and both themes stay.

The cost: each Topic takes one more tap. Brian accepted it.

The prototype also found a bug of the live code. With an Answer in the Thread, the ask box is sticky at the foot (`apps/site/src/app/front-door/front-door.tsx:528`). When the iOS keyboard opens for the passphrase box inside an Answer card, the ask box and the dock cover that box. Brian decided the fix goes in this spec as its own ticket.

The screenshots of all variants are in the scratchpad of the session, under `shots/`. The prototype code is deleted.
