# 01: The scope of the checks and ADR 0037

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-32, AT-33 and AT-35.

**App:** both

**What to build:** A scope script reads a diff and says if it is records only or a change of code, and which heavy checks it selects: the smoke run, the re-run, and the rebuild. The records are `.scratch/`, `docs/`, and Markdown files at the root. ADR 0037 states that each PR that changes code carries a smoke run, a re-run of its loop, and a base and head rebuild.

**Blocked by:** none

**Status:** in-review

- [x] The scope script prints "records only" on the diff of commit `c9b6282c`, and selects no heavy check.
- [x] The scope script selects the rebuild on a diff of the pipeline, and the smoke run on a diff of the site.
- [x] A test of the root scripts covers both cases with a real git repo.
- [x] ADR 0037 exists and the ADR README lists it.
- [x] The hook config and the commit scripts gain no trailer check and no commit gate.
