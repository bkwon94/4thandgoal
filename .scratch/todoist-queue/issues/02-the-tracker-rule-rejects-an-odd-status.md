# 02: The tracker rule rejects an odd status

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-28.

**App:** both. The tracker rule of the site and the tracker rule of the pipeline change.

**What to build:** A ticket under `issues/` whose `Status:` first word is outside the nine canonical statuses fails the tracker rule of each app, and the failure names the ticket. The nine are `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `in-review`, `blocked`, `done`, and `wontfix`. A ticket with no `Status:` line stays legal and open. The rule comes after the audit, because the odd statuses on `main` would fail it.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] A new case in each tracker rule test fails a ticket at `backlog` and names it.
- [x] A ticket with no `Status:` line still passes.
- [x] A planted ticket at `backlog` fails both rules by name in a real run, and the planted file is removed after.
- [x] `make check-fast` passes on the audited tracker.
