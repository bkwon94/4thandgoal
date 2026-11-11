# 12: The waiver package

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1, AT-31, and AT-32.

**App:** both

**What to build:** The waiver board moves into the `waiver` package, with its research prompt. The check proves the dependency order and the selection by package.

**Blocked by:** 06, 07

**Status:** done

- [x] The `waiver` package holds the modules of decision 01 and the research prompt, and writes the waiver board.
- [x] A test import of `waiver` from the API fails the check with `ModuleNotFoundError` (AT-31).
- [x] A diff of one line in the Python of `waiver` checks both languages of `waiver` and each dependent (AT-32).
- [x] A test client with `waiver` in its list builds the waiver route.
- [x] The CPC golden diff is empty (AT-1).

## Comments
- Closed by the merge of PR #3.
