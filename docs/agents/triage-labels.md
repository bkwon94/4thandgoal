# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |
| none                       | `in-review`          | Merged into its spec branch. It exists only on a spec branch: the last commit before the push sets it to `done` |
| none                       | `blocked`            | `4ag:implement` could not build it; the comment says why |

## The queue labels

The queue is a Todoist project (ADR 0032). Each open task has one status label, and the label has the same
name as the status. A push writes a flow status to the queue. A pull writes a triage status to git.

| Status               | Queue label       | Who sets it        | Task state |
| -------------------- | ----------------- | ------------------ | ---------- |
| `needs-triage`       | `needs-triage`    | Brian or a push    | open       |
| `needs-info`         | `needs-info`      | Brian or a push    | open       |
| `ready-for-agent`    | `ready-for-agent` | Brian or a push    | open       |
| `ready-for-human`    | `ready-for-human` | Brian or a push    | open       |
| `in-progress`        | `in-progress`     | a `4ag` skill      | open       |
| `in-review`          | `in-review`       | a `4ag` skill      | open       |
| `blocked`            | `blocked`         | a `4ag` skill      | open       |
| `done`               | none              | the merge sweep    | complete   |
| `wontfix`            | `wontfix`         | Brian or a push    | complete   |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.
