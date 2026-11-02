# 02: The sheet entry point is a rule in the layer test

Spec: `.scratch/rules-as-checks/PRD.md`, part 2. One 0003. Pipeline ADR 0007.

**What to build:** A test in `tests/test_layers.py` fails when a module outside `cornerstone/sheet/` imports
any sheet module other than `cornerstone.sheet` or `cornerstone.sheet.base`. Today no module breaks it.

**Blocked by:** 04 (the report shape and its helper).

**Status:** ready-for-agent

- [x] Rule id `layers/sheet-entry`. Rule sentence: "Outside the sheet package, a module imports only `cornerstone.sheet` or `cornerstone.sheet.base`."
- [x] The scope is every module of `cornerstone` and `cornerstone_api` under `src/`, outside `cornerstone.sheet`.
- [x] Choice: the rule reads every import in the file: load time, under `TYPE_CHECKING`, and inside a function. `_top_level_imports` is for cycles. An import inside a function still goes past the entry point.
- [x] Choice: the rule does not read `tests/`. A chapter test may import its chapter module.
- [x] Reuse `_targets` for the name resolution, so `from cornerstone.sheet import awards` counts as an import of `cornerstone.sheet.awards`.
- [x] Each offense prints the report shape: the file and the import line, `layers/sheet-entry`, the imported module, the rule, the ADR path, and the fix: "re-export the name from cornerstone/sheet/__init__.py, or import it from cornerstone.sheet.base."
- [x] Choice: the rule and the fix start lowercase and have no markup, like the other rules in `tests/test_layers.py`.
- [x] A test runs the rule on a temporary `src/` with one module that imports `cornerstone.sheet.next_week`, and finds one offense.
- [x] `src/cornerstone/sheet/__init__.py`: the comment "a caller that needs one chapter imports that chapter module" is now false. Change it to state the rule.
- [x] `docs/adr/0007-six-layers-import-downward-only.md` gains a section "The sheet entry point" with the rule and the test name.
- [x] `make check` passes. The four golden tests pass with no golden change.
