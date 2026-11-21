# 20: How does the Finder wait feel shorter?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** 19

**Status:** done

## Question

With the pick of 5 at effort medium, a press takes about 45 to 50 s. Steps 1 to 4 end in about 5 s. Then the line "5 of 5 · Picking the best 5" stays on screen for about 38 s, and all cards show at once at the end. Effort low keeps only 3 picks and breaks more guards. Decide how the wait feels shorter.

## Decision

Brian decided on 2026-11-20.

1. **Effort stays medium.** The pick keeps 5 trades. Brian saw a real low-effort answer: it wrote well but kept 3 trades and slipped on the guards.
2. **Each trade card streams.** The API sends each trade of the pick as soon as it stands, and the site shows each card as it comes, with the rise transition. A line under the cards counts the trades still to come. The near fold shows at the end.
3. **Each step line holds.** Each step line stays on screen at least about 1.5 s, so the reader can read it.
4. **Step 5 names real trades.** On step 5, the line changes about every 3 s. Each line names a real trade of the Shortlist of the press by its players, such as "Weighing Walker for Lawrence, Pollard, Moore".

Copy names no internal tool and states no time. Tests: AT-36 changes, and AT-72 and AT-73 are new.
