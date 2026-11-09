# 08: Which ADR records the vendor, the data sent, and the pass rule?

Map: `.scratch/jev/MAP.md`.

**Kind:** spec

**Blocked by:** 02

**Status:** done

## Question

The ADR records three choices:

1. TypeSafe Jev is the second model vendor, beside Anthropic.
2. The pipeline sends blurbs and fact sheets to TypeSafe, and those hold the names of managers and players. TypeSafe does not train on the data. ZDR is for enterprise accounts only.
3. In this spec, a Jev answer passes no check alone. A later spec may change that only with an eval bar on real labels. A failed Jev call never counts as a pass.

## Decision

The spec records it under The ADR: the next number after 0028, with the vendor, the data sent, and the rule that a Jev answer passes no check alone. Brian approved the spec on 2026-11-09.
