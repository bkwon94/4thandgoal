# 03: Trending

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The file gains the trending bucket: the top 8 free agents by adds across all
Sleeper leagues in the last 24 hours, each with the count as its fact, "added in 41,200 Sleeper
leagues in the last day". A player in both best adds and trending shows in both.

The week fetch gains one call to Sleeper's trending adds endpoint, lookback 24 hours, top 50, saved
as one raw file beside the others. The engine reads the counts from the raw file. A past week with
no trending file gets an empty bucket, not a failed build.

**Blocked by:** 01 The week file, thin.

**Status:** ready-for-agent

- [ ] The week fetch saves the trending file from a fake client.
- [ ] The trending bucket follows the counts and skips rostered players.
- [ ] A player in best adds and trending appears in both buckets.
- [ ] A week with no trending file gives an empty bucket and the build completes.
- [ ] Every count is a fact with the digit in its numbers.
