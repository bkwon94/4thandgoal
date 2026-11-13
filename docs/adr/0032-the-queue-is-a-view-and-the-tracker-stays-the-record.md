# The queue is a view, and the tracker stays the record

This ADR amends ADR 0021. ADR 0021 made the tracker local markdown under `.scratch/<feature>/`. It
named one cost: the tracker has no board. Brian cannot see or change the current work with ease.
We decided that a Todoist project, the queue, answers that cost. The tracker stays the record.

## What each place owns

- The tracker in `.scratch/` owns the content and the done-ness of each ticket. That means the body,
  the blockers, the comments, and the `Status:` line. Only a merge sets `done`.
- The queue owns priority, order, the triage statuses, and new ideas. The queue is a view and a
  triage tool. It is not a record.
- On a conflict, git wins for content and done-ness. The queue wins for the rest.

## The change to ADR 0021

ADR 0021 kept manager names out of every online tool except the pull requests. This ADR allows one
exception. A private Todoist project may hold manager names. The project is private, so the reason
for ADR 0021 still holds: no public place names a manager. The tracker stays in `.scratch/`.

## The rules of the sync

- The script `scripts/queue.py` is the only code that calls `td`. Each `4ag` skill calls the script.
- A task holds a key line, `4ag: <path>`. The key line names the ticket file. Git holds no Todoist ID.
- A failed `td` call prints one warning, and the skill continues.
- CI never calls `td`. A GitHub Action cannot close a task. The merge sweep closes the tasks.

## The cost

The queue and the tracker can differ for a while. A pull before work on a feature brings the triage
statuses into git. A push sends each flow status to the queue. If no `4ag` skill runs, the queue
shows the old state until the next run.

We rejected two alternatives:

- **Todoist as the record.** It holds no branch, no commit link, and no check that CI can read.
- **No queue.** It leaves the cost of ADR 0021 as it is.

The details sit in `docs/agents/issue-tracker.md`, under "The queue".
