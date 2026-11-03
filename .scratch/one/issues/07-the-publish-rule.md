# 07: The publish rule

Spec: `.scratch/one/PRD.md`. Solution part 3, and ADR 0019.

**What to build:** `publish` is the one writer that may push to `main`. A check fails a publish commit that stages a file outside the site's published data.

**Blocked by:** 04.

**Status:** done

- [x] `publish` stages only the published-data folder. A stray file elsewhere in the tree stays unstaged.
- [x] A rule test with a real git repo in a temp folder passes a commit of only published data.
- [x] The same test fails a commit that also stages a file outside it, and the report names the file and the fix.
- [x] The root `make check` runs the rule.
- [x] The state file hold "Nothing uncommitted may sit on `main` at publish time" is gone, because the rule makes it false.

## Comments

- The merge: `one-07-publish-rule` merged as `d5c4e9c` on 2026-11-03, with commits `367678e` and `13ea5a3`. The fix of the ADR refs landed as `8a61343`.
- The proof: the three tests of `test_rule_publish.py` pass on a real git repo in a temp folder. A real `run_publish` with no push left a stray root file untracked. The Check run and the Deploy API run of `8a61343` passed, and they ran the full pipeline suite.
- The notes: `publish` makes two commits. The first holds `apps/pipeline/site/` and `apps/pipeline/data/`, and the second holds `apps/site/public/`. The rule `publish/scope` checks the second commit. ADR 0019 now names both commits.
- Read 7 files: CLAUDE.md, apps/pipeline/CLAUDE.md, .scratch/one/PRD.md, .scratch/one/issues/07-the-publish-rule.md, docs/adr/0019-main-is-the-record-branch.md, apps/pipeline/src/cornerstone/publish.py, apps/pipeline/tests/test_rule_tracker.py.
