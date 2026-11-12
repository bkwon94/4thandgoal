# 02: What can the Todoist CLI do for the sync?

Map: `.scratch/todoist-queue/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The sync calls the Todoist CLI `td`. The spec needs these facts before it picks the shape of the tool:

1. How does `td` find a task by a line in its description? Is there a search or a filter for it, or must the sync list the project and match locally?
2. How does `td` make, update, complete, and uncomplete a task with labels, a section, and a description? Which calls return JSON?
3. How does `td` create and archive a section, and create the labels?
4. What are the limits of `td task add-many` and of the Todoist API rate for an import of about 100 tasks?
5. `td` lives at `/Users/brian.kwon/.nvm/versions/node/v24.15.0/bin/td`, which is not on the default PATH. How does a skill, a subagent in a worktree, and the Codex flow call it?
6. Does a call fail with a clear exit code when the login or the network is missing, so the soft fail can catch it?

## Decision

None yet.
