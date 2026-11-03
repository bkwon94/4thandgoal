# 12: `SeasonInputs` built once

**What to build:** A frozen `SeasonInputs` dataclass holds the snapshot, the projections ahead, the history, and the chart. The build saves the week, then makes `SeasonInputs` once and passes it to the rankings writer and the managers writer. The functions that take the tuple of four take the object. `ProjectionsAhead` is a type alias for the dict shape and nothing more. This closes manager-pages pipeline ticket 14.

**Blocked by:** 01

**Status:** done

- [ ] The raw week loads once per build. A test counts the loads.
- [ ] The rankings writer and the managers writer share one history load.
- [ ] No signature takes the four values as separate parameters.
- [ ] The four golden tests pass with no golden change.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-12-season-inputs`, commits bf20fd5 and 26766d6. 1,490 tests collected. `SeasonInputs` sits in its own module beside the snapshot, because `models.py` cannot import the snapshot without a cycle. `ProjectionsAhead` lives in `models.py` and is the one alias. The failure path matches `modular`: a history failure skips both season files, and a snapshot, projections, or chart failure skips only the managers file. `run_build` takes a `raw_loader` seam. Two reviewers passed it after one fix pass.
