# 08: The build saves its inputs

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-19 and AT-20.

**App:** pipeline

**What to build:** Each build saves the nflverse extract of the week, also a degraded one, the values of the slow sources, and the Sleeper news into the week folder. A facts-only rebuild reads those inputs, the build clock of `verify.json`, and the research of the saved facts, with no Claude call and no network call.

**Blocked by:** none

**Status:** done

- [x] `build --no-fetch` of cpc 2026 week 10 with no key writes the three inputs before the first Claude call.
- [x] Two facts-only rebuilds of cpc week 10 give the same sha256 of `facts.json`.
- [x] The facts-only rebuild runs with no secret and makes no network call.
- [x] A pipeline test builds the facts of a saved week two times and compares them byte for byte.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-08` (`0716c7e4`) merged into `trusted-green` as `f34644fd` on 2026-11-18.
`apps/pipeline/tests/test_pipeline.py` gained 4 tests, and AT-19 and AT-20 have PASS.
The committed week 10 holds no saved inputs, so the first week that a facts diff can check is the next week built.
The builder did not count the files it read; the ticket commit changed 5 files: apps/pipeline/Makefile, apps/pipeline/src/cornerstone/cli.py, apps/pipeline/src/cornerstone/pipeline.py, apps/pipeline/tests/test_pipeline.py, packages/waiver/python/src/waiver/research.py.
