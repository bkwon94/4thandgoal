# 03: Push makes one task match one ticket

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-8, AT-9, AT-10, AT-11, AT-12, AT-22, AT-24, and AT-32.

**App:** both. A root script, with no product code.

**What to build:** An agent runs one command and the queue task of one ticket or one decision ticket matches the file. This ticket builds the base of the root script of the spec, in the pattern of the other root scripts: the standard library only, tests beside it, and the run in `make check-fast`. The base finds `td` in the newest nvm Node with no PATH set, gives each call a timeout of about 10 seconds, reads the JSON errors, and turns a failed call into one warning line and exit 0. Each subcommand has `--dry-run` and `--root`. `push` writes the title, the description with the key line, the app, the blockers, the link, and the summary, and the labels, under the ownership rules of the spec. A flow status always wins. A triage status is written only when the task is made. The priority and the labels of Brian outside the flow stay. A decision ticket gets `decision` and its status label by kind, and completes when it is `done`. A ticket task never completes as `done` from a push.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The unit tests check the plan of `push` with real ticket files and saved real `td` JSON, with no mock and no network.
- [x] A second `push` of the same file plans zero writes.
- [ ] A real `push` on the throwaway feature gives each decision ticket its label by kind.
- [ ] A triage label from Brian, his extra label, and his priority survive a real `push`.
- [ ] A flow status replaces a triage label in a real `push`.
- [x] A real `push` with an invalid token exits 0 with one warning line that names the ticket.
- [x] `--dry-run` sends nothing, and the task count stays the same.
- [x] A new comment in the file adds no Todoist comment and does not change the description.
