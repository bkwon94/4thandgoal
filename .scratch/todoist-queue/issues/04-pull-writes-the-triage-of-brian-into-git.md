# 04: Pull writes the triage of Brian into git

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-13, AT-14, AT-15, and AT-16.

**App:** both. A root script, with no product code.

**What to build:** Brian changes a status label or completes a task in the queue, and the next `pull` of that feature writes the result into the `Status:` line of the ticket. A label change writes that triage status. A completed task writes `wontfix`, or `done` when a comment on the task holds the word `done`. Text after the first word of the `Status:` line stays only when the first word does not change. A failed read of the queue changes no file and gives a warning with exit 0. The skill that calls `pull` commits the result on the spec branch.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] The unit tests check the plan of `pull` with saved real `td` JSON for a label change, a completion, and a completion with a `done` comment.
- [ ] A real `pull` on the throwaway feature writes `needs-info` from a label change.
- [ ] A real `pull` writes `wontfix` from a completed task with no comment.
- [ ] A real `pull` writes `done` from a completed task with the comment "done in #34".
- [ ] A real `pull` with an invalid token leaves `git status` of the temp root clean.
