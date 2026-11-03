# 01: The pipeline README names the verdict check

Spec: `.scratch/zz-verdict-dry-run/PRD.md`. Acceptance tests AT-1 and AT-2.

**App:** pipeline

**What to build:** the pipeline README has one line that names the check `verdict` and ADR 0020. (dry run)

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] `grep -n 'verdict' apps/pipeline/README.md` prints one line.
