# 08: The build saves its inputs

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-19 and AT-20.

**App:** pipeline

**What to build:** Each build saves the nflverse extract of the week, also a degraded one, the values of the slow sources, and the Sleeper news into the week folder. A facts-only rebuild reads those inputs, the build clock of `verify.json`, and the research of the saved facts, with no Claude call and no network call.

**Blocked by:** none

**Status:** in-review

- [x] `build --no-fetch` of cpc 2026 week 10 with no key writes the three inputs before the first Claude call.
- [x] Two facts-only rebuilds of cpc week 10 give the same sha256 of `facts.json`.
- [x] The facts-only rebuild runs with no secret and makes no network call.
- [x] A pipeline test builds the facts of a saved week two times and compares them byte for byte.
