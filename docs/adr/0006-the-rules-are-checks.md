# The rules are checks

A rule ran only when an agent chose to run it, and CI ran only on `main`. An agent follows the checks
that run, so a rule with no check is no rule. We decided that one command holds every rule. `pnpm check`
runs typecheck, test, build, and `check:export`. CI runs it on every push to any branch. A prek hook
runs `pnpm check:fast`, a subset of typecheck and test, before each commit. The hook and CI call the
same scripts in `package.json`. The hook runs a subset, and CI runs all of the rules. The hook subset
must stay under 30 seconds, because `--no-verify` is banned. The hook checks the whole tree, not the
staged files, because the subset takes about 17 seconds and a staged-only check would miss a type
error in a file the commit does not touch. The hook does not run `pnpm install`. In a worktree with
no `node_modules` it fails, and the fix is `pnpm install`. The deploy workflow keeps its own
`pnpm check`, because a separate workflow cannot gate the deploy without `workflow_run`.
