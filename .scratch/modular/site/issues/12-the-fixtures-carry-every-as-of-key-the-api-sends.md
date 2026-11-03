# 12: The fixtures carry every as_of key the API sends

**What to build:** The Zod schemas follow the two fixtures under `src/fixtures/`, but the fixtures lack `no_chart` and `no_chart_note`, and no fixture holds a null `chart_week` or `rosters_fetched`. The API sends all of them, so the schema test passed while the live analyzer failed with "The API sent an answer the site cannot read." Regenerate the two fixtures from a live analyze call and a live find call, one on a week with a chart and one in the no-chart window if the window is open. Then add one schema test per nullable `as_of` key that uses a real document, not a hand edit. Record in the schema header which API commit the fixtures come from.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Both fixtures hold `no_chart` and `no_chart_note` as the API sends them.
- [ ] The schema header names the API commit the fixtures come from.
- [ ] `pnpm test` passes.
