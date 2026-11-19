# 04: The Tour under reduced motion, and the seen key

Map: `.scratch/front-door-tour/MAP.md`.

**Kind:** spec

**Blocked by:** 02

**Status:** done

## Question

Two small choices that `4ag:to-spec` records in the spec:

1. Under reduced motion, the Tour keeps its Stops and drops the moves, as the other front door parts do through `useMotionOff`.
2. The name of the `localStorage` key that marks the Tour as seen, beside the keys of Your team, the opened Topics, and the Thread.

## Decision

`4ag:to-spec` recorded both choices in `PRD.md` on 2026-11-18, and Brian approved the spec.

1. Under reduced motion, each Stop still shows. The hole jumps, the card fades out and in with no glide or scale, the text swaps by opacity only, the dim keeps its fade, and the scroll into view is not smooth.
2. The seen key is `cpc.tour-seen` with the value `"1"`. The Tour writes it when Stop 1 opens. A throw on the read counts as seen.
