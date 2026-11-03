# 01: Clear the open ticket branches

Spec: `.scratch/one/PRD.md`. Implementation Decisions, "The order of the move".

**What to build:** No open ticket branch is left in the site repo or the pipeline repo. A branch from before the move cannot merge after the paths change.

**Blocked by:** None. It can start now.

**Status:** ready-for-agent

- [ ] The agent lists every local and remote branch other than `main` in both repos, with its last commit, its date, and whether `main` contains it.
- [ ] Brian decides merge or delete for each branch that `main` does not contain. The agent does not decide.
- [ ] Each branch is merged or deleted as Brian decided. Each worktree on a deleted branch is removed.
- [ ] Both repos show only `main`, or branches that `main` contains.
