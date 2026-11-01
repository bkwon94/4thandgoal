# 12: `SeasonInputs` built once

**What to build:** A frozen `SeasonInputs` dataclass holds the snapshot, the projections ahead, the history, and the chart. The build saves the week, then makes `SeasonInputs` once and passes it to the rankings writer and the managers writer. The functions that take the tuple of four take the object. `ProjectionsAhead` is a type alias for the dict shape and nothing more. This closes manager-pages pipeline ticket 14.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The raw week loads once per build. A test counts the loads.
- [ ] The rankings writer and the managers writer share one history load.
- [ ] No signature takes the four values as separate parameters.
- [ ] The four golden tests pass with no golden change.
