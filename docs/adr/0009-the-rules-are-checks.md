# The rules are checks

A rule that runs only when an agent chooses to run it is not a rule. An agent follows the checks that
run, not the text that describes them. So each rule of this repo is a check, and one command runs the
checks. `make check` runs lint, typecheck, and all the tests. `make check-fast` runs lint, typecheck,
and the rule tests.

The hook and CI call the same targets. A prek hook runs `make check-fast` on each commit. The repo
bans `--no-verify`, so the hook must stay under 30 seconds. A GitHub Action runs `make check` on every
push, on every branch. CI runs all the tests, and the hook runs the fast subset. One 0013 runs the
same command in both places; we chose a subset for the hook, because the full suite takes minutes.

Name a rule test `tests/test_rule_<topic>.py`. `make rules` finds each one with no edit.
`tests/test_layers.py` is a rule test and keeps its name.

One 0013 runs the hook on the staged files. This hook reads the whole tree, because the subset takes
about 3 seconds and a file list saves nothing. One 0013 installs the packages inside the hook. This
hook does not, because `uv run` syncs the environment itself. The hook does not run `ruff --fix`,
because a hook that writes files makes a commit that differs from the staged change.
