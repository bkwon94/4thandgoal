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

## The report of an offense

Each report gives enough to fix the offense without the ADR. Each rule test prints each offense in
one shape, with `report` from `tests/rule_report.py`:

```text
src/cornerstone/waiver.py:12  layers/upward-import
  cornerstone.waiver imports cornerstone.writer.
  Rule: a module imports only from its own layer or a lower one (docs/adr/0007-six-layers-import-downward-only.md).
  Fix: move the shared name to a module in a lower layer, or move cornerstone.waiver up in LAYER_OF.
```

- Line 1 holds the path from the repo root, a colon, the line, two spaces, and the rule id.
- Line 2 says what is wrong at this place, with the names of this place.
- Line 3 gives the rule in one sentence, and the path of its ADR.
- Line 4 gives the fix.

The rule id is `<topic>/<name>`. The topics are `layers`, `suppression`, `readme`, and `ports`. The
report starts with the count, such as "2 offenses.", and puts a blank line between two offenses. A
rule test asserts `not offenses, report(offenses)`, so pytest prints the report when the test fails.
One 0013 also gives a column. This report does not, because a rule here names a whole line.
