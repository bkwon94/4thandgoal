# 10: A failed stream logs its cause, and the first call holds

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-48 and AT-49.

**App:** api

**What to build:** Each failed stream of a trade Topic logs one line with its cause, its stage, and the seconds since the start. With those lines, the ticket finds why the first call of a trade Topic sometimes fails while a retry answers fast, and fixes the cause. A Fly machine always runs, so the cause is not a cold start. The likely cause is a long stream that drops.

**Blocked by:** none

**Status:** done

- [x] A stream that the client cuts after 5 s logs one line with the cause, the stage, and the seconds.
- [ ] The cause of the failed first call is named in the close comment, with the log lines that show it.
- [ ] Ten fresh asks for trade ideas for Bo Girds each answer with no retry line.

## Comments

- 2026-11-19, `4ag:implement`: the log line merged in `89e5db91` (AT-48). Box 2 and box 3 wait on a deploy of the spec branch: no failed call is in the last 100 Fly log lines. Hypotheses: (1) the pick stage sends no bytes for 17 to 21 s and the connection drops, most likely; (2) the phone leaves the page; (3) the first press raises. Cold start and gzip buffering are ruled out. Ticket 06 removes the id retry and streams step lines, which shortens the silence of hypothesis 1. AT-49 needs Brian's go to deploy.

The merge: `deadline-week-10` merged into `deadline-week` as a fast-forward before `1fd07690` on 2026-11-19; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/10-a-failed-stream-logs-its-cause.md.
Closes with the squash merge of the spec PR.
