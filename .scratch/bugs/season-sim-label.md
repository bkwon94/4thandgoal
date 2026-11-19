# The menu label of the season sim is not title case

Kind: bug
Status: in-progress
Branch: `bug-season-sim-label`.
Source: the session of 2026-11-19.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The menu label of the season sim is not title case

Done condition: The menu link of the sim package reads "Season Sim", in title case like the other menu labels such as "Power Rankings" and "Trade Analyzer".
Method: diagnosing-bugs
Cause: `menuLink` in `apps/site/src/app/_routes/sim/menu.ts` sets the label `"Season sim"` in sentence case, so the menu shows it unlike the other title-case labels.
Red: at `2e799df4` with `apps/site/src/app/_routes/sim/menu.test.ts` of `efa25ec6`, `cd apps/site && pnpm exec vitest run src/app/_routes/sim/menu.test.ts`

```text
 FAIL  src/app/_routes/sim/menu.test.ts > the menu link of the sim package > links the sim page of the season of the latest week
AssertionError: expected { label: 'Season sim', …(1) } to deeply equal { label: 'Season Sim', …(1) }
-   "label": "Season Sim",
+   "label": "Season sim",
 Test Files  1 failed (1)
      Tests  1 failed | 3 passed (4)
```

Green: at `efa25ec6`, `cd apps/site && pnpm exec vitest run src/app/_routes/sim/menu.test.ts`

```text
 Test Files  1 passed (1)
      Tests  4 passed (4)
```
Test verdict: PASS

### 2. The rerun check misses a quoted Red line in colored output

Done condition: The rerun check in `scripts/rerun.py` matches a quoted Red line when the output of the loop holds ANSI color codes, as Vitest prints them on GitHub Actions.
Method: diagnosing-bugs
Cause: `normal` in `scripts/rerun.py` keeps the ANSI color codes of the loop output, so `shows` cannot find a quoted Red line inside the colored line that Vitest prints on GitHub Actions.
Red: at `14d2782b` with `scripts/test_rerun.py` of `7bf53c46`, `python3 -B -m unittest scripts.test_rerun.TheRerun.test_a_quoted_line_matches_output_with_ansi_color_codes`

```text
  Red at 7cdf0d14: exit 1
FAIL item 1 (add gives the sum): the Red output has no line `Test Files  1 failed (1)`
AssertionError: 1 != 0 : quick file: .scratch/bugs/add.md
Ran 1 test in 0.419s
FAILED (failures=1)
```

Green: at `7bf53c46`, `python3 -B -m unittest scripts.test_rerun.TheRerun.test_a_quoted_line_matches_output_with_ansi_color_codes`

```text
Ran 1 test in 0.316s
OK
```
Test verdict: pending

## Smoke

Smoke: none. `pnpm --dir apps/site pick --base main` printed "No flow: no file of the diff matches a glob of the flow list."

## Comments

Item 2 joins the run on 2026-11-19 after the job `Run the loops of the quick file again` failed on PR 78: the Vitest output in CI holds ANSI codes, and `normal()` keeps them.
