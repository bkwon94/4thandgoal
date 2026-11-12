# 05: Wait and the merge sweep

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-17, AT-18, AT-19, AT-20, and AT-21.

**App:** both. A root script, with no product code.

**What to build:** A skill opens a wait task when a step waits on Brian, and closes it when the step is done. The kinds are `approve-prd`, `approve-acceptance`, `approve-tickets`, and `merge-pr` with a PR number. Each wait task has `ready-for-human`. The merge sweep checks each open `Merge PR #N` task with `gh`. For a merged PR, it completes the task of each ticket that is `done` on `main`, then the wait task. A ticket still open on `main` keeps its task. The section is archived only when every task in it is complete. For a PR closed without a merge, the wait task gets `blocked`. An open PR changes nothing.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] The unit tests check the plan of `wait` and `sweep` with saved real `td` and `gh` JSON, including an open PR.
- [ ] A real `wait` makes `Approve PRD` with `ready-for-human`, and `--done` completes it.
- [ ] A real `sweep` with the merged PR #34 completes the task of the done zz ticket and the wait task, and leaves the blocked zz ticket open.
- [ ] A real `sweep` archives the zz section once every task in it is complete.
- [ ] A real `sweep` with the closed PR #16 gives its wait task `blocked`.
