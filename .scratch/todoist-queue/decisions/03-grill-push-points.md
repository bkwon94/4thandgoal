# 03: Which skill pushes what, at which step?

Map: `.scratch/todoist-queue/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Each `4ag` skill changes the tracker at known steps. The spec needs the list of steps that push to Todoist, and the steps that pull from it. Examples: `4ag:plan` writes decision tickets, `4ag:to-spec` writes a PRD that waits on Brian, `4ag:to-tickets` writes tickets, `4ag:implement` sets `in-progress`, `in-review`, and `blocked`, opens a PR, and closes tickets. `4ag:review` may change a status too. The spec also needs the steps that make and complete a wait task, and the step that archives a section after the merge.

## Decision

Brian decided this in the grill of 2026-11-12. He took the table and option (A).

| Skill and step | Git change | Todoist action |
| --- | --- | --- |
| `4ag:plan` stage 1 | writes the decision tickets | make the section, and one task per open decision ticket |
| `4ag:plan` stage 2 start | none | pull the labels of the feature |
| `4ag:plan` stage 2 end | sets the decision ticket to `done` | complete its task |
| `4ag:to-spec`, `4ag:to-acceptance`, `4ag:to-tickets` | write a file that waits on the approval of Brian | make the wait task "Approve PRD", "Approve ACCEPTANCE", or "Approve tickets". The next skill completes it at its start |
| `4ag:to-tickets` end | writes the tickets at `ready-for-agent` | one task per ticket |
| `4ag:implement` start | none | pull the labels of the feature |
| `4ag:implement` stage 1 | sets a ticket to `in-review` or `blocked` | change the label |
| `4ag:implement` stage 5, before the push | sets each `in-review` ticket to `done` | no change. The tasks stay `in-review` until the merge |
| `4ag:implement` stage 5, after `gh pr create` | none | make the wait task "Merge PR #N" |
| `4ag:review` | fix rounds | change the label of each ticket that changes |

**The close after a merge is a sweep.** Each `4ag` skill runs the sweep at its start. The sweep checks each open "Merge PR #N" task with `gh pr view N --json state`. For a merged PR, it completes each ticket task of the feature, then the wait task, then archives the section. For a PR closed without a merge, it sets the label `blocked` on the wait task. The import can run the sweep by hand.

Reason: GitHub is the truth for a merge, and Brian does nothing extra. CI never calls `td` (decision 01), so a GitHub Action cannot close the tasks. The sweep archives a section only after each task in it is complete, because an archive also archives the open tasks (decision 02).

Known limit: if no `4ag` skill runs for a week, Todoist shows the old state for a week.
