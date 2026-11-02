# The rules are checks

A rule ran only when an agent chose to run it, and CI ran only on `main`. We decided that one
command holds every rule. `pnpm check` runs typecheck, test, build, and `check:export`. CI runs it on
every push to any branch. A prek hook runs `pnpm check:fast`, a subset of typecheck and test, before
each commit. The hook and CI run the same rules from the same scripts in `package.json`. The hook
subset must stay under 30 seconds, because `--no-verify` is banned. CI runs all of the rules. The
deploy workflow keeps its own `pnpm check`, because a separate workflow cannot gate the deploy
without `workflow_run`. Later tickets add a section each.
