# The rules are checks

A rule that runs only when an agent chooses to run it is not a rule. So each rule of this repo is a
check, and one command runs the checks. `make check` runs lint, typecheck, and all the tests.
`make check-fast` runs lint, typecheck, and the rule tests.

The hook and CI run the same rules. A prek hook runs `make check-fast` on each commit. `--no-verify`
is banned, so the hook must stay under 30 seconds. A GitHub Action runs `make check` on every push,
on every branch. CI runs all the tests, and the hook runs a subset.

A rule test is named `tests/test_rule_<topic>.py`, so `make rules` finds a new one with no edit.
`tests/test_layers.py` is the first rule test and keeps its name.

The hook runs on the whole tree, not on the staged files. It does not run `ruff --fix`, because a hook
that writes files makes a commit that differs from the staged change.
