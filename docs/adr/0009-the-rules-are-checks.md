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

The rule id is `<topic>/<name>`. The topics are `layers`, `suppression`, `readme`, `tracker`, and `ports`. The
report starts with the count, such as "2 offenses.", and puts a blank line between two offenses. A
rule test asserts `not offenses, report(offenses)`, so pytest prints the report when the test fails.
One 0013 also gives a column. This report does not, because a rule here names a whole line.

## No suppression comment

No comment silences a rule. `tests/test_rule_suppressions.py` reads every `*.py` file under `src/` and
`tests/`. It fails on `noqa`, `type: ignore`, and `pyright: ignore`, with no regard to case. The rule
id is `suppression/comment`. The test builds each pattern from two parts, so its own file holds no
match. The test skips no file, because a file exclusion hides new code from the rule.

A line that must stay lives in the allow list, the `ALLOW` dict of the test. No other place may hold
one. The key is the path and the line text, not the line number, so an entry stays true when a line
above it moves. The value is the reason. An entry with no match fails the test, so a stale entry
cannot stay. To find out if a marker silences a real offense, run
`uv run ruff check src tests --extend-select RUF100`. Do not use `--select RUF100`: it turns off every
other rule, so each marker then shows as unused.

One 0013 allows no suppression at all. Here the allow list is the one departure from One. The reason:
ruff owns its rules, and we do not fork them or turn one off to clear a marker. ruff 0.17.3 enables
BLE001 and RUF009 by default. Five lines catch a broad error or call `partial` in a default, and each
must stay. So the list starts with these five lines.

## A README in each package folder

An agent new to the repo reads a folder README to decide whether to open the folder. A package
folder is each folder under `src/` that holds an `__init__.py`. Each one holds a `README.md` with a
one-line title and three headings, in this order:

- `## Knows` says what the folder knows, in the terms of `GLOSSARY.md`. It defines no term again.
- `## Ports` lists each port that the folder declares. A folder with no port writes "None."
- `## Does not do` says what the folder never does, and which folder does it.

The third heading has the most value, because it is the only one that lets an agent stop the search.
Each README is under 25 lines, so an agent reads little.

No `CLAUDE.md` is in the repo other than the root one. One 0007 gives the reason. Claude Code loads
a nested `CLAUDE.md` by itself, so its text goes into the context when the agent does not need it.
The agent must choose to read the next level. A README also serves people and each tool, and holds
the rule in one place.

`tests/test_rule_readmes.py` holds the rules. The rule ids are `readme/missing`, `readme/headings`,
`readme/length`, and `readme/no-claude-md`. The `CLAUDE.md` rule reads `git ls-files`, so a staged
file counts. The test checks that each README exists and has the right shape. It cannot check that
the text is true, so review checks that.

## The state file

A cold agent reads `CLAUDE.md`, then `docs/agents/state.md`, then the ticket. The state file has one
table with one row for each feature that has an open ticket. A ticket is open when its Status is not
`done` and not `wontfix`. A done feature leaves the file, and the tracker holds its history. The
state file replaces the handoff file, because a handoff is a copy of the tracker that drifts.

`tests/test_rule_tracker.py` holds the rule, with the id `tracker/state-file`. It fails on an open
feature with no row, and on a row with no open feature. It reads only the tickets that
`git ls-files .scratch` lists, so the hook and CI read the same set. Untracked files under `.scratch/`
are notes, not the tracker. The test cannot check the next ticket or the hold, so review checks them.
