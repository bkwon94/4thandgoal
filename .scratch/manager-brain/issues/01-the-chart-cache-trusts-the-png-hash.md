# 01: The chart cache trusts the PNG hash

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-1, AT-2, and AT-3.

**App:** pipeline

**What to build:** A chart PNG placed by hand is read, whatever its file time. The saved read of a chart stores a hash of its PNG, and a read runs again only when the hash differs. The manual step works: put the PNG in the chart cache of the week, then `cornerstone chart --client <slug> --week NN` reads and checks it and prints its row count. The build log says plainly when a week has no chart. This fix also helps `main` now.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A PNG with a newer file time than its saved read and the same hash is not read again.
- [ ] A PNG with a changed hash is read again.
- [ ] `cornerstone chart --client cpc --week 8` reads a placed PNG and prints the count of chart rows.
- [ ] The build of a week with no chart PNG logs one plain line that says so.
- [ ] `make check-fast` passes.
