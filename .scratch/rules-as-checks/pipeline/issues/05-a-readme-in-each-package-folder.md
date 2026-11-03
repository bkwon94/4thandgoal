# 05: A README in each package folder

Spec: `.scratch/rules-as-checks/pipeline/PRD.md`, part 5. One 0001 and 0007.

**What to build:** Each package folder holds a `README.md` with three headings: Knows, Ports, Does not do.
`tests/test_rule_readmes.py` fails on a package folder with no README, a missing heading, 25 lines or more,
or a `CLAUDE.md` anywhere below the repo root.

**Blocked by:** 04 (the report shape and its helper).

**Status:** done

- [x] A package folder is each folder under `src/` that holds an `__init__.py`. Today that is four: `src/cornerstone/`, `src/cornerstone/sheet/`, `src/cornerstone/provider/`, and `src/cornerstone_api/`.
- [x] Choice: `src/cornerstone/` gets a README too. The test finds it by its `__init__.py`, and a skip would be an exclusion. Its README names the six layers and points at ADR 0010. It does not repeat the repo `README.md`.
- [x] `src/cornerstone/prompts/` has no `__init__.py`, so it needs no README.
- [x] The headings are exactly `## Knows`, `## Ports`, and `## Does not do`, in that order. A folder with no port writes "None." under Ports.
- [x] **Knows**: what the folder knows, in the terms of `GLOSSARY.md`. Do not define a term again.
- [x] **Ports**: each protocol the folder declares. `provider/` lists `Provider` in `provider/base.py`. After ticket 06, the folder of `Writer` lists it.
- [x] **Does not do**: the lines that let an agent stop the search. For example, `sheet/` writes no prose and calls no model. `provider/` holds no league rule.
- [x] Each README is under 25 lines, in STE.
- [x] Rule ids: `readme/missing`, `readme/headings`, `readme/length`, `readme/no-claude-md`. ADR: `docs/adr/0014-the-rules-are-checks.md`.
- [x] The `CLAUDE.md` rule reads `git ls-files` and fails on any `CLAUDE.md` other than the root one. One 0007 says why: a nested `CLAUDE.md` loads by itself, and the agent must choose to read.
- [x] A test runs the rule on a temporary folder with an `__init__.py` and no README, and finds one offense.
- [x] `docs/adr/0014-the-rules-are-checks.md` gains "A README in each package folder".
- [x] Add the test file to the `pyright` include list. `make check` passes.

## Comments

- 2026-11-02: merged into `main` from branch `rules-as-checks-05-readmes`, commits 1c580de, 1a387d4, a834fa9, b5febaa, b9de4cb, and 9c418ac, with `--no-ff`. 1492 passed, 9 deselected. No golden change. `make rules` runs 20 tests. Four READMEs, 18 to 21 lines each. A truth review checked every line against the code with grep and found one false line in `sheet` about the odds engine and two overclaims in `provider`, all fixed. The sheet has one port: `assemble.py` calls `provider.sleeper.fetch_news` by default. Note for later: `test_rule_suppressions.py` fix strings have no end period, and every other rule test has one. Two reviewers passed it after one fix pass. Read 21 files and file sets, module docstrings only for the 78 modules: the ticket, the PRD, ticket 04, ~/repos/zero/docs/VISION.md, One ADRs 0007 and 0001, tests/test_rule_suppressions.py, tests/test_layers.py, tests/rule_report.py, ADRs 0010 and 0014, GLOSSARY.md, pyproject.toml, Makefile, README.md, the four __init__.py files, the first 5 lines of each module in the four folders, the import lines of sheet, provider, and cornerstone_api, sheet/base.py and sleeper.py in part.
