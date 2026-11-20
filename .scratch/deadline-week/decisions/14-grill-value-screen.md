# 14: What value screen cuts the candidate list in code?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** 13

**Status:** done

## Question

Brian allows a value screen on the chart sums for this feature only (handoff ruling 4). This breaks the memory rule `no-math-filters` on purpose. Decide:

1. The band of the screen.
2. Whether the band applies to the sum per side, or has a separate band per shape.
3. Whether the exception needs an ADR, and the exact limit of the exception.
4. The glossary terms "value pair" and "shape".

This decision also replaces the out-of-scope line "A Jev tree for fair" of decision 05 where the two conflict.

## Decision

Brian decided each part on 2026-11-19, from the facts of decision 13.

1. **Shapes.** 1-for-1, 2-for-1, 3-for-1, and 3-for-2, each in both directions. A manager can consolidate or add depth.
2. **The band.** The side that gets more players gets 100% to 125% of the sum of the other side. A 1-for-1 stays within 10% either way. This puts ruling 3 into the screen. Jev still judges fairness in decision 15.
3. **No cap now.** The band and the direction cut the list. A cap ranks by the sums and drops ideas before Jev reads them. Decision 16 can bring a cap back if the preview shows too many waves.
4. **A floor of 5 chart points** for each player on a side of two or three players. It keeps filler out of a "fair" sum.
5. **No chart value, no Value offer.** The 29 pool players with no week 11 chart value, Justin Herbert among them, stay out. The Spares tree can still offer them.
6. **ADR 0038** limits the exception to `no-math-filters` to the Value screen.
7. **Terms:** Shape, Value screen, and Value offer in `GLOSSARY.md`. "Value pair" goes under _Avoid_. Offer now allows one to three players per side.

**Plumbing for the spec.** The Jev requests of one partner split into chunks under the 64k context of a request. Today one request per partner fails above about 590 candidates, and its offers pass as "unsure" (`finder_search.py:583-586`). Brian chose the split over the long-context header.

**Follow-up.** Find out why the week 11 chart has no value for 29 pool players.
