# 01: The scope of the checks and ADR 0037

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-32, AT-33 and AT-35.

**App:** both

**What to build:** A scope script reads a diff and says if it is records only or a change of code, and which heavy checks it selects: the smoke run, the re-run, and the rebuild. The records are `.scratch/`, `docs/`, and Markdown files at the root. ADR 0037 states that each PR that changes code carries a smoke run, a re-run of its loop, and a base and head rebuild.

**Blocked by:** none

**Status:** done

- [x] The scope script prints "records only" on the diff of commit `c9b6282c`, and selects no heavy check.
- [x] The scope script selects the rebuild on a diff of the pipeline, and the smoke run on a diff of the site.
- [x] A test of the root scripts covers both cases with a real git repo.
- [x] ADR 0037 exists and the ADR README lists it.
- [x] The hook config and the commit scripts gain no trailer check and no commit gate.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-01` (`9c869911`) merged into `trusted-green` as a fast-forward on 2026-11-18.
The root scripts gained 6 tests in `scripts/test_scope.py`, each on a real git repo in a temp folder, and AT-32 and AT-33 have PASS.
A test of the root scripts that runs git must strip each `GIT_*` variable, or the index of the hook leaks into it.
The builder did not count the files it read; the ticket commit changed 4 files: docs/adr/0037-each-pr-of-code-carries-a-smoke-run-a-rerun-and-a-rebuild.md, docs/adr/README.md, scripts/scope.py, scripts/test_scope.py.
