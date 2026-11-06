# 13: The sim replay

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-29, AT-30, AT-31, AT-32, AT-33, AT-34, AT-35, AT-36, and AT-50.

**App:** site

**What to build:** The `sim` package's site part replays one sim run per press in the Broadcast motion of ticket 13 of `decisions/`. It reads only `sim.json`. The report page mounts it as the finale. This ticket waits for the merge of `site-redesign` into `main`, because it uses the redesign's parts and look.

**Blocked by:** 03 and 11.

**Status:** ready-for-agent

- [x] A press plays a random sim run: a lower third each week, a red PLAYOFFS wipe, the final standings with the cut and the byes, the bracket, and a champion card with "Wins the title in N% of all 10,000 runs".
- [x] "Skip to the end" shows the final state at once, and a press during a run starts a clean new run.
- [x] With reduced motion, each beat fades with no movement.
- [x] The odds of all runs show beside the replay on a desktop and below it on a phone.
- [x] The replay has no control to pick a game's winner.
