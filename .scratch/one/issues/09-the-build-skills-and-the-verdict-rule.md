# 09: The build skills and the test verdict rule

Spec: `.scratch/one/PRD.md`. Solution parts 3, 4, and 5, ADR 0020, and Implementation Decisions "The branch model" and "The test verdict comment".

**What to build:** `cpc:implement` builds a spec on its spec branch and opens one PR. Brian merges it on his test verdicts, and a check blocks a merge with a FAIL or a missing test.

**Blocked by:** 08 and 04.

**Status:** done

- [ ] `cpc:implement` builds each ticket in its own worktree on a ticket branch, with `tdd`.
- [x] It merges each ticket into the spec branch only after the diff check passes.
- [ ] It runs `code-review` on the spec branch and fixes the findings.
- [x] It records evidence for each acceptance test with no test verdict, and it opens one PR to `main`.
- [ ] `cpc:review` does one round of PR feedback per run.
- [x] A CI job reads the test verdict comment and the acceptance file. Tests with real files and real comment text prove these cases: all PASS passes. A FAIL, a BLOCKED, or a missing test fails.
- [x] One dry run in a throwaway feature merges one ticket into a spec branch and opens a draft PR. The draft PR is closed and the throwaway feature is deleted after.

## Comments

- The merge: `one-09-build-skills` merged as `6aa1aa2` on 2026-11-03, with commits `37cd342`, `91810a5`, `645afce`, `ce8d2a9`, and `f68e276`. The fix `75d43bd` makes the verdict workflow read its script from `main`, so a PR cannot judge itself.
- The proof: the 14 tests of `scripts/test_verdict.py` pass in the root `make check`. The dry run on draft PR #1 set the `verdict` status to failure with no comment, failure after `AT-2: FAIL`, and success after all PASS. PR #1 is closed with no merge. The Check run of `75d43bd` passed.
- Open: three boxes wait for the first real spec, because the dry run did not run `tdd`, `code-review`, or `cpc:review`. The `issue_comment` path is also unproved live, because the workflow was not on `main` before the dry run. The ticket stays `in-review` until the first real spec PR proves them.
- The notes: agent comments end with `<!-- cpc:agent -->`, because the agent and Brian share the account `bkwon94`, and the check ignores marked comments. Site evidence is about 320 KB for each test, and it reaches `main` through the squash merge. `verdict` blocks a merge only after Brian makes it a required check.
- Read 14 files: CLAUDE.md, docs/agents/issue-tracker.md, docs/agents/state.md, GLOSSARY.md, .scratch/one/PRD.md, .scratch/one/issues/09-the-build-skills-and-the-verdict-rule.md, docs/adr/0019-main-is-the-record-branch.md, docs/adr/0020-a-spec-pr-merges-on-the-verdicts-of-its-acceptance-tests.md, Makefile, .github/workflows/check.yml, and in `~/repos/zero` branch `one`: implement/SKILL.md, review/SKILL.md, .agents/delivery.md, docs/adr/0014.
- The spec PRs #3 to #31 ran on the build skills and the verdict check.
