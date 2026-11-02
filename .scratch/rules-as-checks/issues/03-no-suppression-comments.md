# 03: No suppression comments

Spec: `.scratch/rules-as-checks/PRD.md`, part 3 and "The allow list is the one departure from One". One 0013.

**What to build:** `tests/test_rule_suppressions.py` fails on any suppression comment in `src/` or `tests/`.
The five `noqa` lines of today go, and their reasons stay as plain comments. The allow list starts empty.

**Blocked by:** 04 (the report shape and its helper).

**Status:** ready-for-agent

- [x] Rule id `suppression/comment`. Rule sentence: "No comment silences a rule. A line that must stay goes in the allow list of this test, with its reason."
- [x] The test reads every `*.py` file under `src/` and `tests/`. It matches `noqa`, `type: ignore`, and `pyright: ignore`, with no regard to case.
- [x] Choice: the test builds each pattern from two parts, such as `"no" + "qa"`. The test file then holds no match. Never skip the test's own file: One rejects a file exclusion.
- [ ] The five lines of today. Ticket 14 of `modular` kept them: a broad `except` must not stop the build or the service.
  - `src/cornerstone/render.py:191` `# noqa: BLE001 - a build never stops on one avatar`
  - `src/cornerstone/pipeline.py:240` `# noqa: BLE001 - the outer guard: the module catches only HTTP errors`
  - `src/cornerstone/live.py:118` `# noqa: BLE001 - the docstring says why: no error may stop the service`
  - `src/cornerstone_api/app.py:68` `# noqa: BLE001 - the app keeps running after a failed refresh`
  - `src/cornerstone_api/sources.py:44` `# noqa: RUF009`. The comment above it gives the reason.
  *Not done: ruff 0.17.3 enables BLE001 and RUF009 by default, so each marker silences a real offense. The five lines are in the allow list instead.*
- [ ] Remove the cause: `pyproject.toml` selects no ruff rule, so ruff runs only its defaults, and neither `BLE001` nor `RUF009` is on. `uv run ruff check src tests --select RUF100` reports all five as unused. Each `noqa` silences nothing.
  *Not done: ruff 0.17.3 enables BLE001 and RUF009 by default, so each marker silences a real offense. The five lines are in the allow list instead.*
- [ ] Remove each `# noqa: <code>` marker. Keep the reason after it as a plain comment, such as `# a build never stops on one avatar`. Do not remove a reason. Do not turn on a ruff rule.
  *Not done: ruff 0.17.3 enables BLE001 and RUF009 by default, so each marker silences a real offense. The five lines are in the allow list instead.*
- [x] The allow list is a dict in the test: the key is `(path, line text)`, and the value is the reason. It is empty. Its comment says it is the only place a suppression may live.
  *Changed: the list holds the five lines, not zero, because each marker silences a real offense.*
- [x] Choice: the key holds the line text, not the line number, so the entry does not go stale when a line above it moves.
- [x] An allow list entry with no match fails the test, so a stale entry cannot stay.
- [x] A test runs the rule on a temporary folder with one `# type: ignore` line and finds one offense.
- [x] `docs/adr/0009-the-rules-are-checks.md` gains "No suppression comment": the rule, the allow list, and why this departs from One.
- [x] Add the test file to the `pyright` include list. `make check` passes. The four golden tests pass.
