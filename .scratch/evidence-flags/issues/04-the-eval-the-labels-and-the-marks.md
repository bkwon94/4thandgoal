# 04: The eval, the label file, and the marks for the flow

Spec: `.scratch/evidence-flags/PRD.md`. Acceptance tests AT-4, AT-7, AT-8, AT-9, AT-14, and AT-22.

**App:** pipeline.

**What to build:** `cornerstone evidence-flags-eval` reads the label file, runs each question on each labeled test at its commit through `git show`, and prints the hits, misses, and false flags at the cut, with `meets the bar: yes` or `meets the bar: no`. The label file holds the 56 tests of decision tickets 02 and 06 and names no manager. The live run sets the in-flow mark of each question in the module, and `evidence-flags` asks only the questions in the flow. The bar is half of the past gaps of a kind and 10% or fewer false flags.

**Blocked by:** 03.

**Status:** ready-for-agent

- [x] The live eval prints the four rows and the bar result, and the marks of the module equal them (AT-7).
- [x] On easter-eggs AT-41 at `8d646bd0`, the printed question keys equal the in-flow keys (AT-4).
- [x] A script counts 56 tests, 7 `gap`, 5 `defect`, and 44 `pass`, and finds no name of `managers.json` (AT-8).
- [x] A CLI test with a temp git repo and a `FakeJev` error counts each test as an error, never as a miss or a pass (AT-9).
- [x] A search finds each question text, cut, and bar value in one module only (AT-14).
- [x] `env -u TYPESAFE_API_KEY make -C apps/pipeline check` passes (AT-22).
