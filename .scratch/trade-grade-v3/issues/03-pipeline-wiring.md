# 03: Pipeline wiring

**What to build:** A normal build fetches and reads the chart for its week with no manual step, hands the values to the bundle builder, and records whether the chart was used. A chart outage or a failed read logs a warning and the build goes on with no value facts.

**Blocked by:** 02 (Chart fetch, read, match, and the `chart` command)

**Status:** done

- [ ] The pipeline wires a chart fetcher the same way it wires the nflverse fetcher, bound to the repo's cache directory, and tests patch that name.
- [ ] The bundle builder receives the matched values for the week's trades, or none.
- [ ] The build record in the verify file gains a `chart` source flag that is true only when value facts were made.
- [ ] A smoke render from disk with no Claude call works with and without the chart values.
- [ ] Tests cover a build with a fake chart fetcher that yields values, one that yields none, and one that raises inside the fetch, with the build going on in all three.
- [ ] `uv run pytest -q` passes.
