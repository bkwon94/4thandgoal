# 01: The queue keeps Bugs and Quick Wins

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-6, AT-7, AT-8, AT-9, and AT-10.

**App:** both

**What to build:** A quick file under `.scratch/bugs/` pushes into the existing queue section `Bugs`, and a quick file under `.scratch/quick-wins/` pushes into the section `Quick Wins`. Every other feature keeps its slug as its section name. The merge sweep closes a done quick task and its wait task, and never archives `Bugs` or `Quick Wins`. A spec section still archives as before. The tracker rule asks for no row in `docs/agents/state.md` for an open quick file.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A push of a quick file under `.scratch/bugs/` plans a task in `Bugs` and no section `bugs`.
- [ ] Two pushes of quick files under `.scratch/quick-wins/` into a queue with no `Quick Wins` make that section once.
- [ ] A sweep after a merged PR completes the done quick task and its wait task, and plans no archive of `Bugs` or `Quick Wins`.
- [ ] A sweep still archives the section of a spec feature, such as `odds`, after every task in it is complete.
- [ ] A new tracker rule test shows that a tracked open quick file needs no row.
- [ ] `make check-fast` passes at the root.
