# design-checks-speed: Evidence flags

The agent sets the action of each entry: `recorded again`, `fix group`, `disagree: <one line>`, or `open`. The Judge never reads this file.

## AT-3, question (a)

Question: the facts
Probability: 0.79
Reason: No file may show this fact of the Then line: "the command exits non-zero and names the raw color rule once for each of the two lines." (shown at 0.21).
Action: disagree: output.txt prints design(no-raw-color) once at line 6 and once at line 7; the fixture adds a third line, also hit once

## AT-12, question (a)

Question: the facts
Probability: 0.93
Reason: No file may show this fact of the Then line: "Each of the 8 files that had a raw `<button>` on 2026-11-20 now uses a wrapper of `ui/`." (shown at 0.07).
Action: disagree: output.txt gives the diff stat of all 12 files that had a raw button at the base, each now on Button; the 8 of the Then line are among them

## AT-14, question (a)

Question: the facts
Probability: 0.76
Reason: No file may show this fact of the Then line: "the hook fails, the commit does not land, and the output names the element rule and the file." (shown at 0.24).
Action: disagree: output.txt shows the hook Failed, the no-raw-element line with the file, exit 1, and git log 2108f8bc before and after; Jev saw a cut file

## AT-16, question (d)

Question: the Observation
Probability: 0.72
Reason: No file may show this sentence of the Observation: "The shots of the two branches show the same chip fills; the Spec `375-light.png` from the runner is 399 px wide with a blank strip at the right edge, and the Spec runner shots lack the "1 new" badge of the Trade Wire that the main shots show." (shown at 0.23, a result of the Then line at 0.94).
Action: disagree: the PNG files show the width and the badge; Jev reads text, not images

## AT-21, question (a)

Question: the facts
Probability: 0.79
Reason: No file may show this fact of the Then line: "neither search finds a match." (shown at 0.21).
Action: fix group

## AT-24, question (a)

Question: the facts
Probability: 0.77
Reason: No file may show this fact of the Then line: "The commit does not land." (shown at 0.23).
Action: disagree: output.txt shows git log -1 = 2108f8bc before and after the failed commit; Jev saw a cut file

## AT-25, question (a)

Question: the facts
Probability: 0.98
Reason: No file may show this fact of the Then line: "no version of a package that `main` already locks has changed." (shown at 0.02).
Action: disagree: lock-diff.txt shows no kept package with a new version; the removed versions belong to vite, vitest, and jsdom, and the two new versions come from happy-dom

## AT-26, question (a)

Question: the facts
Probability: 0.86
Reason: No file may show this fact of the Then line: "each run exits 0, and each wall-clock time is 97 s or less, against the baseline of 195 s." (shown at 0.14).
Action: disagree: run-1.txt and run-2.txt hold start and end times, exit 0, 69 s and 64 s; Jev saw cut files

## AT-26, question (d)

Question: the Observation
Probability: 0.78
Reason: No file may show this sentence of the Observation: "Run 2 went from 11:03:10 to 11:04:14, 64 s, exit code 0, with load averages 5.18 5.53 4.61 at start." (shown at 0.20, a result of the Then line at 0.98).
Action: disagree: run-2.txt line 3 and 4 give the load and the start 11:03:10, and its end gives 11:04:14 and exit 0; Jev saw a cut file

## AT-27, question (d)

Question: the Observation
Probability: 0.70
Reason: No file may show this sentence of the Observation: "Run 3 uses the repo hook config plus `verbose: true`; there each worktree runs `bun test --isolate --parallel=3` with "1954 pass, 0 fail", and a search of both run 3 outputs for "timed out", "timeout", or "(fail)" counts 0." (shown at 0.26, a result of the Then line at 0.95).
Action: disagree: hook-wt-a-run3.txt and hook-wt-b-run3.txt each hold 1954 pass, and a search for timed out or (fail) counts 0; Jev saw cut files

## AT-32, question (a)

Question: the facts
Probability: 0.85
Reason: No file may show this fact of the Then line: "the unit job runs the full suite with no `--changed`." (shown at 0.15).
Action: disagree: run.txt shows BUN_TEST_BASE empty, the bun test line with no --changed, and The run takes the full suite.
