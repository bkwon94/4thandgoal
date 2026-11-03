# 04: One report shape for every rule test

Spec: `.scratch/rules-as-checks/pipeline/PRD.md`, part 4 and "The report shape". One 0013, "The report of an offense".

**What to build:** A small helper in `tests/rule_report.py` prints each offense in the house shape.
`tests/test_layers.py` uses it for all three of its tests. Tickets 02, 03, 05, and 06 use it for their rules.

**Blocked by:** 01 (ADR 0014 and `make rules`).

**Status:** done

- [x] The exact shape, one offense:

```text
src/cornerstone/waiver.py:12  layers/upward-import
  cornerstone.waiver imports cornerstone.writer.
  Rule: a module imports only from its own layer or a lower one (docs/adr/0010-six-layers-import-downward-only.md).
  Fix: move the shared name to a module in a lower layer, or move cornerstone.waiver up in LAYER_OF.
```

- [x] Line 1: the path from the repo root, a colon, the line, two spaces, the rule id. Lines 2 to 4 start with two spaces.
- [x] `tests/rule_report.py` holds a frozen dataclass `Offense` with `path`, `line`, `rule_id`, `what`, `rule`, `adr`, `fix`, and a function `report(offenses) -> str`. It starts with the count, such as "2 offenses.", then each offense, with a blank line between.
- [x] A test asserts `not offenses, report(offenses)`. The helper imports no pipeline code.
- [x] Choice: the rule id is `<topic>/<name>`. The topics: `layers`, `suppression`, `readme`, `ports`.
- [x] `test_layers.py` ids: `layers/no-layer`, `layers/stale-entry`, `layers/upward-import`, `layers/api-import`. Each has a fix sentence.
- [x] `_targets` keeps the line of each import, so `layers/upward-import` names the line. The no-layer offense uses line 1 of the module. The stale-entry offense uses the line of its key in `LAYER_OF`.
- [x] A test of the helper compares `report` of one offense with the text above, byte for byte.
- [x] A test runs the layer rule on a temporary `src/` where a model module imports a write module, and reads one `layers/upward-import` offense with the right line.
- [x] `docs/adr/0014-the-rules-are-checks.md` gains "The report of an offense", with the example above.
- [x] Add `tests/rule_report.py` to the `pyright` include list. `make check` passes.

## Comments

- 2026-11-02: merged into `main` from branch `rules-as-checks-04-report-shape`, commits 2deac95, b09547e, a025d94, d352168, and 588a9f7, with `--no-ff`. 1479 passed, 9 deselected. No golden change. `make rules` runs 6 tests, all in `test_layers.py`. The helper test is `tests/test_offense_report.py`, so the `test_rule_` prefix keeps one meaning. Each of the three layer rules also runs on a temporary `src/` and finds one offense. `_stale_entry_offenses` takes a `layer_of` argument for that test. Two reviewers passed it after one fix pass. Read 13 files: .scratch/rules-as-checks/pipeline/issues/04-one-report-shape-for-every-rule-test.md, .scratch/rules-as-checks/pipeline/PRD.md, docs/adr/0014-the-rules-are-checks.md, tests/test_layers.py, docs/adr/0010-six-layers-import-downward-only.md, pyproject.toml, Makefile, ~/repos/zero/docs/adr/0013-the-rules-are-checks.md, tests/fakes.py, tests/conftest.py, tests/rule_report.py, and the two reviewers read CLAUDE.md and docs/agents/issue-tracker.md.
