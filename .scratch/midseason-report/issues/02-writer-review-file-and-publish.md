# 02: The writer, the review file, and the publish

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-39, AT-40, AT-41, AT-42, and AT-43.

**App:** pipeline

**What to build:** The build sends each prose block of the report through the writer and the verifier of `facts`, with the roast rules and the `roast` setting of the client. It writes a review file that Brian reads. `make midseason-publish` checks each blurb again, refuses on a failure, and commits only the client's season folders.

**Blocked by:** 01.

**Status:** ready-for-agent

- [x] The review file shows each blurb with its prose block, its facts, and the verifier result.
- [x] Each roast blurb cites at least one fact.
- [x] With `roast = "off"` the draft has no roast lines.
- [x] An edited blurb with an uncited number makes `make midseason-publish CLIENT=cpc WEEK=8` refuse and name the blurb.
- [x] A clean publish commits `midseason.json` and `sim.json` in `clients/cpc/published/2026/` and no other path.
