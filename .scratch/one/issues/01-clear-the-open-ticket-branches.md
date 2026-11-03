# 01: Clear the open ticket branches

Spec: `.scratch/one/PRD.md`. Implementation Decisions, "The order of the move".

**What to build:** No open ticket branch is left in the site repo or the pipeline repo. A branch from before the move cannot merge after the paths change.

**Blocked by:** None. It can start now.

**Status:** done

- [x] The agent lists every local and remote branch other than `main` in both repos, with its last commit, its date, and whether `main` contains it.
- [x] Brian decides merge or delete for each branch that `main` does not contain. The agent does not decide.
- [x] Each branch is merged or deleted as Brian decided. Each worktree on a deleted branch is removed.
- [x] Both repos show only `main`, or branches that `main` contains.

## Comments

- The merge: no branch, the work was branch and worktree cleanup in both repos on 2026-11-03.
- The proof: both repos show only `main`, and the pipeline also keeps `origin/archive/weekly-action` at `7557923`.
- The notes: `weekly-action` built and published the weekly report on GitHub Actions. It was 13 days old and conflicts with the platform refactor. Its idea is fog for the first map after this spec.
- Read 0 files: the agent read only git output.
