# 01: What does git own, and what does Todoist own?

Map: `.scratch/todoist-queue/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Brian cannot easily see or change the current work. The tickets live in `.scratch/` and the live work sits on spec branches. The spec needs the split between git and Todoist, the shape in Todoist, and the rules of the sync.

## Decision

Brian decided these in the grill of 2026-11-12, in eight questions.

1. **Git is the record. Todoist is the queue.** Git owns the content and done-ness of each ticket: the body, the blockers, the comments, and the `Status:` line. Todoist owns priority, order, triage choices, and new ideas. On a conflict, git wins for content and done-ness, and Todoist wins for the rest. Reason: the status of a ticket depends on the branch, CI reads `.scratch/` through git, and the close comment ties a ticket to a commit. Todoist cannot hold any of these.
2. **The shape.** The Todoist project `4thandgoal` has one section per feature and one top-level task per ticket. An `Ideas` section holds new ideas. A closed feature's section is archived. Reason: Brian triages tickets, not features, so a ticket must be a top-level task. Sections avoid one project per feature.
3. **The status labels.** Each open task has one of seven labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `in-review`, `blocked`. `done` completes the task with no label. `wontfix` completes the task with the label `wontfix`. The odd strings `triage`, `built`, `accepted`, and `backlog` change to a canonical label in the markdown too.
4. **The scope.** Todoist holds the open tickets on `main`, the tickets on each live spec branch, and each open decision ticket with the label `decision`. A `grill` or `prototype` decision ticket gets `ready-for-human`. A `research` one gets `ready-for-agent`. A feature that waits on Brian, such as a PRD to approve or a PR to merge, gets one wait task with `ready-for-human`. The 544 `done` tickets stay out.
5. **The audit.** The open tickets of `main` are stale. Ticket 01 of the spec is an audit. An agent checks each open ticket against the git log, the code, and the memory notes. It proposes `done` with a commit, `wontfix` with a reason, or `open` with a label, in one report grouped by feature. Brian approves each line. The agent then writes the `Status:` lines and close comments on the spec branch. The import runs on the audited set only.
6. **The pull is lazy, per feature.** No agent commits on `main` (ADR 0019). Todoist holds a triage choice of Brian until work starts on that feature. Then `4ag:plan`, `4ag:to-tickets`, or `4ag:implement` pulls the Todoist labels of that feature and commits them on its spec branch. A completed task in Todoist is a request for `wontfix`, unless Brian comments that the work is done. Only a merge sets `done`. A task in `Ideas` stays in Todoist until Brian runs `4ag:plan` on it.
7. **The key.** The task description starts with a fixed line that names the ticket path, such as `4ag: .scratch/<feature>/issues/03-<slug>.md`. A push finds the task by that line. Git holds no Todoist ID. A wait task uses a key such as `4ag: <feature>/wait`. Each push is idempotent: it makes or updates the task to match the file.
8. **A soft fail.** A failed `td` call prints one warning and the skill continues. The final report of the skill names each missed push. Any later push or the import repairs it. CI never calls `td`. A failed pull falls back to the git status.
