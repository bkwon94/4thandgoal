# Todoist queue: map

App: both. The change is to the `4ag` plugin and the tracker records, not to the code of an app.
Spec branch: `todoist-queue`.

## DESTINATION

Git stays the record, and the Todoist project `4thandgoal` becomes the queue that Brian reads and changes. An audit fixes the stale tickets, an import loads the open work, and the `4ag` skills push each change and pull the triage of Brian per feature.

## DECISIONS SO FAR

- Git owns the content and done-ness. Todoist owns priority, order, triage, and ideas. `decisions/01-grill-record-and-queue.md`.
- One project has one section per feature, one task per ticket, and an `Ideas` section. `decisions/01-grill-record-and-queue.md`.
- Seven open status labels. `done` completes the task. `wontfix` completes it with the label `wontfix`. `decisions/01-grill-record-and-queue.md`.
- The scope is the open tickets on `main`, the live spec branches, the open decision tickets, and one wait task per feature that waits on Brian. `decisions/01-grill-record-and-queue.md`.
- An audit of the open tickets is ticket 01 of the spec. An agent proposes, and Brian approves. `decisions/01-grill-record-and-queue.md`.
- The pull is lazy, per feature, onto the spec branch. `decisions/01-grill-record-and-queue.md`.
- The ticket path in the task description is the key. Each push is idempotent. `decisions/01-grill-record-and-queue.md`.
- A failed `td` call never blocks the flow. CI never calls `td`. `decisions/01-grill-record-and-queue.md`.
- `td` cannot search a description, so the sync reads the project once and matches locally. Each call needs the nvm PATH and a timeout. `decisions/02-research-td-facts.md`.
- Each `4ag` skill pushes at the steps in a fixed table. Wait tasks mark an approval or a merge. A sweep at the start of each skill closes the tasks of a merged PR. `decisions/03-grill-push-points.md`.
- One stdlib script, `scripts/queue.py`, with the subcommands push, pull, wait, sweep, and import. Each skill calls it. `decisions/04-grill-tool-shape.md`.
- A task has a title from the H1, a description with the key, app, blockers, link, and summary, and no priority set by a push. `decisions/05-spec-task-content.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- A triage of the `ready-for-agent` tickets past the audit. That is the work of Brian in Todoist after the import.
- The cleanup of the old worktrees. It is not tracker work.
- The root `scratch.md`. Git does not track it. Brian moves its one idea to the `Ideas` section.
