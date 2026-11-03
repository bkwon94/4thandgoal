# `main` is the record branch

An agent that commits on `main` skips every gate that a branch gives. So `main` is the record
branch: it holds only work that passed review. No agent commits on `main` or pushes to `main`.

Work lands in this order:

1. A spec branch is named `<slug>` and starts from `main`.
2. A ticket branch is named `<slug>-<NN>`. It is local, starts from the spec branch, and has its
   own worktree.
3. A ticket merges into the spec branch with `git merge --no-edit`, after `check` passes.
4. One pull request goes from the spec branch to `main`, as a squash merge.

The squash gives `main` one commit for each spec, so the history reads as a list of features.
The ticket commits stay in the spec branch until it is deleted.

## The `publish` exception

The weekly `publish` must put a new week on `main` with no pull request, because the report ships
on a fixed day. So `publish` may push to `main`, and it may stage only `apps/site/public/<season>/`.
A check enforces this. The check fails if the staged set holds any other path. The exception is
narrow on purpose: it covers data and never code.

We rejected three alternatives:

- **A pull request for each publish.** It adds a human step to a task with a deadline, and the
  data has no diff to review.
- **A separate data branch.** The deploy would then read two branches, and a reader could not see
  what the site shows from `main` alone.
- **Trunk-based work on `main`.** An agent would push unreviewed code, and a bad push would deploy.
