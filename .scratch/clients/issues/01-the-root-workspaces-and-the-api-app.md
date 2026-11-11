# 01: The root workspaces and the API app

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1.

**App:** both

**What to build:** The repo has one uv workspace and one pnpm workspace at the root, each with one lock file. The API is its own app, apart from the pipeline. The check selects what to run by package, and a change to a root file runs the full check. Nothing that a reader sees changes.

**Blocked by:** none

**Status:** done

- [x] One root uv workspace holds the pipeline, the API, and the package globs, with one root `uv.lock`.
- [x] One root pnpm workspace holds the site and the package globs, with one root `pnpm-lock.yaml`.
- [ ] The API is its own app and its own uv member. Its deploy to Fly still runs, and `/health` answers 200.
- [x] The check runs each Python member with `uv run --exact --package`.
- [x] A diff of a root file runs the full check. The root files are the workspace files, the lock files, the root `Makefile`, and `.github/`.
- [x] The CPC golden diff is empty (AT-1).

## Comments
- Closed by the merge of PR #3.
