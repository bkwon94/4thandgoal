# 01: The audit of the open tickets

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-26 and AT-27.

**App:** both. The tracker records of both apps change, and no product code.

**What to build:** Each open ticket under `issues/` on `main` gets a checked result before the queue sees it. An agent checks each open ticket against the git log, the code, and the memory notes, and writes one report, `audit.md`, grouped by feature. Each line proposes `done` with the commit that did the work, `wontfix` with a reason, or `open` with its correct status label. Brian approves or changes each line in a session with the agent. The agent then writes each `Status:` line and a close comment that names the commit or the reason, and updates `docs/agents/state.md` in the same commit. The odd statuses `triage`, `built`, `accepted`, and `backlog` become canonical ones. This ticket needs Brian at the approval, so it runs in a session with him and not AFK.

**Blocked by:** none

**Status:** ready-for-human

- [ ] `audit.md` lists each open ticket of `main` once, under its feature, with a result.
- [ ] Each `done` line names a commit that exists in `git log`.
- [ ] Brian approved each line of `audit.md`.
- [ ] Each `Status:` line matches its approved line, with a close comment.
- [ ] `docs/agents/state.md` lists each feature with an open ticket, and `make check-fast` passes.
- [ ] No ticket has the status `triage`, `built`, `accepted`, or `backlog`.
