# 02: Which eval bar and which threshold make the cascade live?

Map: `.scratch/jev/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** open

## Question

The facts check goes live only if the eval on past labels clears a bar. This ticket sets the bar and the threshold.

- The bar: for example, "on all past weeks, Jev passes no blurb that Claude failed".
- The threshold: the Noul probability above which Jev passes a sentence, such as 0.9.
- The truth table: the outcome for every combination of Jev answers, including a Noul between the thresholds.

The spec needs these values to write its acceptance tests.

## Decision

None yet.
