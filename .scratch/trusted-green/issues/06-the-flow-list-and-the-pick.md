# 06: The full flow list and the pick

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-2, AT-3, AT-4, AT-5, AT-7, AT-9, AT-10 and AT-34.

**App:** site

**What to build:** The flow list holds the seven flows of the spec, each with its globs, its route, its steps, its expected results, and its Claude and layout flags. `verify` picks the flows from the globs of the diff since the merge base. A layout flow adds the two iPad sizes. A flow that calls Claude runs once, at one width.

**Blocked by:** 05

**Status:** in-review

- [x] A diff of the analyzer site folder picks only Analyzer.
- [x] A diff of the pipeline only picks no flow.
- [x] A diff of the design package picks all seven flows.
- [ ] A smoke run of all seven flows of cpc 2026 week 10 passes with the real API.
- [x] With the API stopped, the Analyzer flow fails and names the request.
- [x] The flow list has no route of the egg board.
