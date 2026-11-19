# 10: A failed stream logs its cause, and the first call holds

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-48 and AT-49.

**App:** api

**What to build:** Each failed stream of a trade Topic logs one line with its cause, its stage, and the seconds since the start. With those lines, the ticket finds why the first call of a trade Topic sometimes fails while a retry answers fast, and fixes the cause. A Fly machine always runs, so the cause is not a cold start. The likely cause is a long stream that drops.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A stream that the client cuts after 5 s logs one line with the cause, the stage, and the seconds.
- [ ] The cause of the failed first call is named in the close comment, with the log lines that show it.
- [ ] Ten fresh asks for trade ideas for Bo Girds each answer with no retry line.
