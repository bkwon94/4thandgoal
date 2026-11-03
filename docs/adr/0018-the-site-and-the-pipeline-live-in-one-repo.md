# The site and the pipeline live in one repo

The site and the pipeline lived in two repos, and each had its own tracker. Nine features needed
work in both, so each one had two sets of tickets that drifted apart. The pipeline publishes a
shape and the site reads it, but no check crossed the repo line. A change to a model in one repo
broke the other repo with no warning. The `publish` script pushed to the site repo by a path
hard-coded in the script, so it worked on one machine only.

We decided that the home is `bkwon94/cpcfantasyfootball`. The site moves to `apps/site/`. The
pipeline moves to `apps/pipeline/` by `git subtree add`, so its full history comes with it. The
pipeline repo is then archived read-only. The `.scratch/` folders, `docs/adr/`, and the glossaries
merge at the root. The ADRs become one series.

The cost is two toolchains in one tree: pnpm and Python. It is also one migration that touches
both repos. The migration lands on a Wednesday or a Thursday, never before a Tuesday report, so a
failed move has two days to heal. Before the migration, every open ticket branch in both repos is
merged or deleted.

We rejected three alternatives:

- **Keep two repos and add a cross check.** A check in CI would need a checkout of the other repo
  and a pinned version, so the check itself would drift.
- **A git submodule.** It keeps two trackers and two histories, and an agent in a worktree must
  also update the submodule.
- **A subtree with squashed history.** It loses the blame for the pipeline, and the history costs
  almost nothing to keep.
