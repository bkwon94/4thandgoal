# 01: The audit of the open tickets

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-26 and AT-27.

**App:** both. The tracker records of both apps change, and no product code.

**What to build:** Each open ticket under `issues/` on `main` gets a checked result before the queue sees it. An agent checks each open ticket against the git log, the code, and the memory notes, and writes one report, `audit.md`, grouped by feature. Each line proposes `done` with the commit that did the work, `wontfix` with a reason, or `open` with its correct status label. Brian approves or changes each line in a session with the agent. The agent then writes each `Status:` line and a close comment that names the commit or the reason, and updates `docs/agents/state.md` in the same commit. The odd statuses `triage`, `built`, `accepted`, and `backlog` become canonical ones. This ticket needs Brian at the approval, so it runs in a session with him and not AFK.

**Blocked by:** none

**Status:** done

- [x] `audit.md` lists each open ticket of `main` once, under its feature, with a result.
- [x] Each `done` line names a commit that exists in `git log`.
- [x] Brian approved each line of `audit.md`.
- [x] Each `Status:` line matches its approved line, with a close comment.
- [x] `docs/agents/state.md` lists each feature with an open ticket, and `make check-fast` passes.
- [x] No ticket has the status `triage`, `built`, `accepted`, or `backlog`.

## Comments

Built on the spec branch `todoist-queue` on 2026-11-12. Three audit agents wrote `audit.md`, and Brian approved it with the changes under its Approved heading.
Proof: 71 tickets audited, 44 done, 21 wontfix, 6 open; each named commit passed `git cat-file -e`.
Later: ticket 06 adds buy low from `front-door` 12 to the Ideas section after the import makes it.
Read 3 files: .scratch/todoist-queue/audit.md, docs/agents/state.md, docs/agents/issue-tracker.md.

Closes with the squash merge of the spec PR. The branch `todoist-queue` holds commit `9bb3994b`, built on 2026-11-12.
Proof: The audit report `audit.md` holds each approved line, and the tracker rules pass on the audited tree.
Read 3 files: .scratch/todoist-queue/PRD.md, .scratch/todoist-queue/ACCEPTANCE.md, .scratch/todoist-queue/VERDICTS.md.
