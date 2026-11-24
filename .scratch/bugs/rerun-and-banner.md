# The rerun check reads no Bun failure, and the closed Deadline banner is under the tap floor

Kind: bug
Status: done
Branch: `bug-rerun-and-banner`.
Source: the session of 2026-11-24, from the CI run of PR #93.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The rerun check finds no failure line in Bun output

Done condition: `scripts/rerun.py` reads the Bun lines `(fail) <test name>` and `error: expect(received).toBe(expected)` in a Red block as failure lines, so a quick file with a Bun loop gets no "the Red block quotes no failure line" problem.
Method: diagnosing-bugs
Cause: `FAILURE_MARK` in `scripts/rerun.py` reads only "FAIL", "Error", "✘", "×", "failed", and "E ", so `read_runs` finds no failure line in the Bun lines "(fail) <test name>" and "error: expect(...)".
Red: at `5292c3e3` with `scripts/test_rerun.py` of `efccfa32`, `python3 -B -m unittest discover -s scripts -p test_rerun.py -k bun`

```text
FAIL: test_the_bun_lines_of_a_failed_test_are_failure_lines (test_rerun.TheRerun.test_the_bun_lines_of_a_failed_test_are_failure_lines)
AssertionError: 1 != 0 : quick file: .scratch/bugs/add.md
item 1 (add gives the sum): does not hold
FAIL item 1 (add gives the sum): the Red block quotes no failure line
Ran 1 test in 0.182s
FAILED (failures=1)
```

Green: at `efccfa32`, `python3 -B -m unittest discover -s scripts -p test_rerun.py -k bun`

```text
Ran 1 test in 0.236s

OK
```
Test verdict: PASS

### 2. The Deadline banner after the Lock is 43 px tall

Done condition: After the Lock of cpc, the Deadline banner button is at least 44 px tall at 1280 px and at 1024 px, so the tap floor of `e2e/floor.spec.ts` passes on `/2026/managers/` and `/analyze/`.
Method: diagnosing-bugs
Cause: the `SheetTrigger` button in `Banner` of `packages/analyzer/site/deadline/deadline-banner.tsx` has no minimum height, and `Grid` in the closed phase holds one line of text, so the button is 43 px tall, under the tap floor of 44 px.
Red: at `6a57072e`, `cd apps/site && CLIENT=cpc pnpm build && CLIENT=cpc pnpm check:floor -g "full floor: cpc /(2026/managers|analyze)/ dark 1280px|top band of cpc is one row at 1024px"`

```text
    Error: cpc /2026/managers/ dark 1280px breaks the readability floor
    +   "button.group \"The trade deadline has passed. Good luck\" is 1280x43px, under the tap floor of 44px",
    Error: cpc /analyze/ dark 1280px breaks the readability floor
    +   "button.group \"The trade deadline has passed. Good luck\" is 1280x43px, under the tap floor of 44px",
    Error: expect(received).toEqual(expected) // deep equality
    +   "button.group \"The trade deadline has passed. Good luck\" is 1024x43px, under the tap floor of 44px",
  3 failed
```
Green: at `08232a91`, `cd apps/site && CLIENT=cpc pnpm build && CLIENT=cpc pnpm check:floor -g "full floor: cpc /(2026/managers|analyze)/ dark 1280px|top band of cpc is one row at 1024px"`

```text
  ✓  1 [floor] › e2e/floor.spec.ts:379:7 › the top band of cpc is one row at 1024px, with the pill bar (445ms)
  ✓  2 [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/ dark 1280px (972ms)
  ✓  3 [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /analyze/ dark 1280px (703ms)
  3 passed (2.9s)
```
Test verdict: PASS

## Smoke

Smoke: flow `Analyzer`. "Smoke run: 1 flow, 1 passed, 0 failed". Shots in `.scratch/bugs/rerun-and-banner/smoke/`.

## Comments

Closes with the squash merge of the PR of `bug-rerun-and-banner`. Commits: `5292c3e3`, `efccfa32`, `6a57072e`, `08232a91`, `1ce8c22c`, `81a3b2d2`, `4ddf35a7`. Date: 2026-11-24.
Item 1 went red at 1 failed, then green at 1 passed; item 2 went red at 3 failed, then green at 3 passed; `make check-fast BASE=main` passed with 267 root tests and 1969 site tests.
The site test "empties the Thread at once on Clear (AT-36)" in `page.test.tsx` failed once under load with a dialog still open, then passed; a later run can check it for a flake.
The Red block of item 2 quotes only lines with no time, because `rerun.py` reads "(804ms)" and "(1.3s)" as different lines; the first CI rerun failed on a `✘` line for this cause.
The Playwright test "a question typed in a scrolled-up Thread scrolls to the top under the Thread header" failed once in site-browser shard 4 of CI, then passed 10 of 10 local runs; a later run can check it for a flake.
Read 8 files: AGENTS.md, apps/site/AGENTS.md, scripts/rerun.py, scripts/test_rerun.py, packages/analyzer/site/deadline/deadline-banner.tsx, packages/analyzer/site/lib/deadline.ts, apps/site/e2e/floor.spec.ts, clients/cpc/client.toml.
