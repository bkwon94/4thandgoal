# 02: The tracker rule rejects an odd status

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-28.

**App:** both. The tracker rule of the site and the tracker rule of the pipeline change.

**What to build:** A ticket under `issues/` whose `Status:` first word is outside the nine canonical statuses fails the tracker rule of each app, and the failure names the ticket. The nine are `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `in-review`, `blocked`, `done`, and `wontfix`. A ticket with no `Status:` line stays legal and open. The rule comes after the audit, because the odd statuses on `main` would fail it.

**Blocked by:** 01

**Status:** done

- [x] A new case in each tracker rule test fails a ticket at `backlog` and names it.
- [x] A ticket with no `Status:` line still passes.
- [x] A planted ticket at `backlog` fails both rules by name in a real run, and the planted file is removed after.
- [x] `make check-fast` passes on the audited tracker.

## Comments

Closes with the squash merge of the spec PR. The branch `todoist-queue` holds commit `b222009b`, built on 2026-11-12.
Proof: Both tracker rules pass with 3 new pipeline tests and 2 new site tests, and both pass on the real tree.
Read 3 files: .scratch/todoist-queue/PRD.md, .scratch/todoist-queue/ACCEPTANCE.md, .scratch/todoist-queue/VERDICTS.md.
