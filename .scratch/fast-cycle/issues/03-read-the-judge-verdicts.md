# 03: The check verdict reads the verdicts of the Judge

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-10, AT-11, AT-12, and AT-13.

**App:** both

**What to build:** `scripts/verdict.py` reads `VERDICTS.md` at the PR head, under the heading `Test verdicts`, with one line per test. It passes only if each live test has PASS and the blob SHAs of `ACCEPTANCE.md` and `EVIDENCE.md` match the ones the Judge read. A FAIL or BLOCKED line in the latest Test verdicts comment of Brian fails the test, until a newer comment of Brian has no FAIL for it. `verdict.yml` keeps its name, its trigger, and its read of the script from `main`.

**Blocked by:** none

**Status:** done

- [x] A full PASS with matched SHAs exits 0 (AT-10).
- [x] A changed `EVIDENCE.md` exits 1 with a rule id that names `EVIDENCE.md` as stale. A changed `ACCEPTANCE.md` does the same for its file (AT-11).
- [x] A comment of Brian with `AT-2: FAIL` exits 1 over a Judge PASS (AT-12).
- [x] A newer comment of Brian with no FAIL for AT-2 exits 0 (AT-13).
- [x] A PR with no `ACCEPTANCE.md` still passes, and the unit tests of the old rule that still apply still pass.
- [x] `verdict.yml` passes the blob SHAs of the two files at the PR head to the script, read through the API as data.

## Comments
- Closed by the merge of PR #14.
