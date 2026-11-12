# 06: Import loads the queue

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-5, AT-6, AT-7, AT-23, and AT-25.

**App:** both. A root script, with no product code.

**What to build:** One command loads the open work into the real queue after the audit. `import` makes the 11 labels of the flow, the `Ideas` section, and the filter "Waits on Brian", each once. It pushes each open ticket and each open decision ticket. It reads each feature from its live spec branch if one exists, else from the current checkout. A live spec branch has a feature folder and no merged PR, per `gh`. It makes the wait tasks of each live spec, such as an open PR that waits on a merge. A `done` ticket never enters. A second run plans zero writes. The script runs from a clean environment with no PATH.

**Blocked by:** 01, 03, and 05

**Status:** in-review

- [x] The unit tests check the plan of `import`, including the choice of the live spec branches.
- [ ] The real import loads `01 The formula` in the section `rankings` with `ready-for-agent`, `pipeline`, and the full description.
- [ ] Both `rankings` subfolders share one section, with the labels `site` and `pipeline`.
- [x] The `codex-flow` ticket 01 shows `in-review` and "On the spec branch codex-flow." with no link.
- [x] No task names a `done` ticket of `front-door`.
- [x] Each label, `Ideas`, and the filter exist once after a second import.
- [x] A second `import --dry-run` plans zero writes, and it runs under `env -i` with no `td` error.
- [x] `make check-scripts` passes and lists the cases of the script tests.
