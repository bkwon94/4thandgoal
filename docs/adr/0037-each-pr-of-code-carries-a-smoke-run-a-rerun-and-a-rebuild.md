# Each PR of code carries a smoke run, a re-run, and a base and head rebuild

A green `Check` did not show that a change works. Brian still read each diff before the merge, and fix PRs
followed, such as #65 after #64 and #47 after #46. We decided that each PR that changes code carries three
checks, and that `Check` blocks the merge on each one. The spec `trusted-green` builds them.

## The three checks

1. A smoke run boots the site and the API, and drives each flow that the diff touches.
2. A re-run of the loop of the PR runs its red test and its fix again, so a green result is not luck.
3. A base and head rebuild runs the facts-only rebuild with the code of `main` and with the code of the PR,
   then diffs the output.

## The scope

The diff picks the checks (decision 01 of `trusted-green`). The records are `.scratch/`, `docs/`, and
Markdown files at the root. A PR of records only gets the plain `Check`. `scripts/scope.py` reads the diff and
prints the checks that it selects. A diff of the pipeline selects the rebuild. A diff of the site selects the
smoke run. A change of code always selects the re-run.

## Considered Options

- Verify by flow, so a PR runs the checks of the flows it names. An agent can name too few flows.
- Verify by diff. A rule that anyone can read from the diff picks the checks, so no agent skips one.

## Consequences

- A PR of code costs more minutes in CI. A PR of records stays fast.
- A new folder of code selects each check until `scripts/scope.py` knows its owner.
- The weekly `publish` has no PR, so these checks do not run on it.
- The spec adds no trailer check and no commit gate to the hook.
