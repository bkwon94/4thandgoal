# 05: A README in each package folder

Spec: `.scratch/rules-as-checks/PRD.md`, part 5. One 0001 and 0007.

**What to build:** Each package folder holds a `README.md` with three headings: Knows, Ports, Does not do.
`tests/test_rule_readmes.py` fails on a package folder with no README, a missing heading, 25 lines or more,
or a `CLAUDE.md` anywhere below the repo root.

**Blocked by:** 04 (the report shape and its helper).

**Status:** ready-for-agent

- [x] A package folder is each folder under `src/` that holds an `__init__.py`. Today that is four: `src/cornerstone/`, `src/cornerstone/sheet/`, `src/cornerstone/provider/`, and `src/cornerstone_api/`.
- [x] Choice: `src/cornerstone/` gets a README too. The test finds it by its `__init__.py`, and a skip would be an exclusion. Its README names the six layers and points at ADR 0007. It does not repeat the repo `README.md`.
- [x] `src/cornerstone/prompts/` has no `__init__.py`, so it needs no README.
- [x] The headings are exactly `## Knows`, `## Ports`, and `## Does not do`, in that order. A folder with no port writes "None." under Ports.
- [x] **Knows**: what the folder knows, in the terms of `GLOSSARY.md`. Do not define a term again.
- [x] **Ports**: each protocol the folder declares. `provider/` lists `Provider` in `provider/base.py`. After ticket 06, the folder of `Writer` lists it.
- [x] **Does not do**: the lines that let an agent stop the search. For example, `sheet/` writes no prose and calls no model. `provider/` holds no league rule.
- [x] Each README is under 25 lines, in STE.
- [x] Rule ids: `readme/missing`, `readme/headings`, `readme/length`, `readme/no-claude-md`. ADR: `docs/adr/0009-the-rules-are-checks.md`.
- [x] The `CLAUDE.md` rule reads `git ls-files` and fails on any `CLAUDE.md` other than the root one. One 0007 says why: a nested `CLAUDE.md` loads by itself, and the agent must choose to read.
- [x] A test runs the rule on a temporary folder with an `__init__.py` and no README, and finds one offense.
- [x] `docs/adr/0009-the-rules-are-checks.md` gains "A README in each package folder".
- [ ] Add the test file to the `pyright` include list. `make check` passes.
