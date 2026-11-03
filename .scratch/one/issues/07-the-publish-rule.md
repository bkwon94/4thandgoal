# 07: The publish rule

Spec: `.scratch/one/PRD.md`. Solution part 3, and ADR 0008.

**What to build:** `publish` is the one writer that may push to `main`. A check fails a publish commit that stages a file outside the site's published data.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] `publish` stages only the published-data folder. A stray file elsewhere in the tree stays unstaged.
- [ ] A rule test with a real git repo in a temp folder passes a commit of only published data.
- [ ] The same test fails a commit that also stages a file outside it, and the report names the file and the fix.
- [ ] The root `make check` runs the rule.
- [ ] The state file hold "Nothing uncommitted may sit on `main` at publish time" is gone, because the rule makes it false.
