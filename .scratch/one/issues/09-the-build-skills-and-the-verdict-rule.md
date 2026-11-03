# 09: The build skills and the test verdict rule

Spec: `.scratch/one/PRD.md`. Solution parts 3, 4, and 5, ADR 0020, and Implementation Decisions "The branch model" and "The test verdict comment".

**What to build:** `cpc:implement` builds a spec on its spec branch and opens one PR. Brian merges it on his test verdicts, and a check blocks a merge with a FAIL or a missing test.

**Blocked by:** 08 and 04.

**Status:** ready-for-agent

- [ ] `cpc:implement` builds each ticket in its own worktree on a ticket branch, with `tdd`.
- [x] It merges each ticket into the spec branch only after the diff check passes.
- [ ] It runs `code-review` on the spec branch and fixes the findings.
- [x] It records evidence for each acceptance test with no test verdict, and it opens one PR to `main`.
- [ ] `cpc:review` does one round of PR feedback per run.
- [x] A CI job reads the test verdict comment and the acceptance file. Tests with real files and real comment text prove these cases: all PASS passes. A FAIL, a BLOCKED, or a missing test fails.
- [x] One dry run in a throwaway feature merges one ticket into a spec branch and opens a draft PR. The draft PR is closed and the throwaway feature is deleted after.
