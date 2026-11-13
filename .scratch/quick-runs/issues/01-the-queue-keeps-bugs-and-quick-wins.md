# 01: The queue keeps Bugs and Quick Wins

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-6, AT-7, AT-8, AT-9, and AT-10.

**App:** both

**What to build:** A quick file under `.scratch/bugs/` pushes into the existing queue section `Bugs`, and a quick file under `.scratch/quick-wins/` pushes into the section `Quick Wins`. Every other feature keeps its slug as its section name. The merge sweep closes a done quick task and its wait task, and never archives `Bugs` or `Quick Wins`. A spec section still archives as before. The tracker rule asks for no row in `docs/agents/state.md` for an open quick file.

**Blocked by:** none

**Status:** done

- [x] A push of a quick file under `.scratch/bugs/` plans a task in `Bugs` and no section `bugs`.
- [x] Two pushes of quick files under `.scratch/quick-wins/` into a queue with no `Quick Wins` make that section once.
- [x] A sweep after a merged PR completes the done quick task and its wait task, and plans no archive of `Bugs` or `Quick Wins`.
- [x] A sweep still archives the section of a spec feature, such as `odds`, after every task in it is complete.
- [x] A new tracker rule test shows that a tracked open quick file needs no row.
- [x] `make check-fast` passes at the root.

## Comments

- Closes with the squash merge of the spec PR of `quick-runs`. Commits: `9e7f80f4`, with the review fixes `7b5a17fb`, `113b7225`, `3a076c15`, `37027baf`, `e2cf2256`, the sweep fix `8a55b056`, and the `odds` test `f971d14b`. Date: 2026-11-13.
- The tests of `scripts/test_queue.py` grow to 92 and `test_rule_tracker.py` has 10; AT-6 to AT-10 and AT-25 have PASS.
- The first sweep after the first quick merge closed nothing, because it read the working tree; fix E1 reads the ref of main.
- Read 6 files: AGENTS.md, apps/pipeline/AGENTS.md, .scratch/quick-runs/PRD.md, .scratch/quick-runs/ACCEPTANCE.md, scripts/queue.py, apps/pipeline/tests/test_rule_tracker.py.
