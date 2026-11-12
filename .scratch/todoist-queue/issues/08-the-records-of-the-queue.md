# 08: The records of the queue

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-30 and AT-31.

**App:** both. The ADRs and the agent docs, with no product code.

**What to build:** A later reader learns what the queue owns and what the tracker owns from the records. A new ADR, 0032, amends ADR 0021. It says that the tracker in `.scratch/` stays the record, that the queue is a view and a triage tool, and that a private Todoist project may hold manager names. `docs/agents/issue-tracker.md` gets a section on the queue: what it owns, the labels, the key line, and the script. `docs/agents/triage-labels.md` gives the queue label of each status. No CI file calls `td`.

**Blocked by:** none

**Status:** ready-for-agent

- [x] ADR 0032 exists, says it amends ADR 0021, and appears in `docs/adr/README.md` if that file lists the ADRs.
- [x] `docs/agents/issue-tracker.md` names the queue, its labels, the key line, and the script.
- [x] `docs/agents/triage-labels.md` gives the queue label of each status.
- [x] A grep of `.github/` and the Makefiles finds `td` and the script only in the `scripts-check` target.
