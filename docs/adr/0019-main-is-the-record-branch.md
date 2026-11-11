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

## The tickets close with the merge

The last commit of the spec branch sets each ticket to `done`, so the squash merge closes the tickets. No extra pull request is needed.
A separate status pull request adds a step that nobody did, and 95 tickets stayed `in-review`.

## The `publish` exception

The weekly `publish` must put a new week on `main` with no pull request, because the report ships
on a fixed day. So `publish` may push to `main`. It makes two commits, and each stages only its own folders. The
first commit holds the week output of the pipeline: the build folder `clients/<slug>/build/<season>/` and the
data `clients/<slug>/data/<season>/`. The API image seeds from that data, so it must reach `main`. The second
commit holds the published data of the client, `clients/<slug>/published/<season>/`. The rule `publish/scope`
checks both commits against these three paths.
A check enforces this. The check fails if the staged set holds any other path. The exception is
narrow on purpose: it covers data and never code.

We rejected three alternatives:

- **A pull request for each publish.** It adds a human step to a task with a deadline, and the
  data has no diff to review.
- **A separate data branch.** The deploy would then read two branches, and a reader could not see
  what the site shows from `main` alone.
- **Trunk-based work on `main`.** An agent would push unreviewed code, and a bad push would deploy.
