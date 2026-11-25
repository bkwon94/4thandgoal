# playoff-paths: Evidence flags

The agent sets the action of each entry: `recorded again`, `fix group`, `disagree: <one line>`, or `open`. The Judge never reads this file.

## AT-15, question (a)

Question: the facts
Probability: 0.88
Reason: No file may show this fact of the Then line: "each of the 4 results holds 5 rows, one per other head-to-head game, each with the odds after each side wins, and a row with a lift under 1 point is marked doesn't matter." (shown at 0.12).
Action: recorded again

## AT-31, question (a)

Question: the facts
Probability: 0.86
Reason: No file may show this fact of the Then line: "the Finish reads "4-2 · ends 15-13" with its chance, and each Path reads "If <team> ends <record> or worse…" and "Happens N% · you're in N%."." (shown at 0.14).
Action: disagree: evidence/AT-31/paths.txt and reading.txt quote "4-2 · ends 15-13 · 26% likely" and each Path line with "Happens N% · you're in N%.".

## AT-32, question (a)

Question: the facts
Probability: 0.70
Reason: No file may show this fact of the Then line: "a Finish at 99.5% or more reads "You're in whatever the others do.", a Finish under 0.5% reads "No way in at this record.", and a Finish under 90% shows "Best chance"." (shown at 0.30).
Action: disagree: evidence/AT-32/finishes.txt and reading.txt quote each of the three copies under 6-0, 0-6, and 3-3.

## AT-34, question (d)

Question: the Observation
Probability: 0.76
Reason: No file may show this sentence of the Observation: "The tap sends POST `/clients/cpc/sim/what-if` with `{"you":6,"set":[{"week":12,"game":"win","median":"above"},{"week":13,"game":"win","median":"above"},{"week":14,"game":"loss","median":"below"}]}`, the local API answers 200 with `page.playoff` 81, and the sheet closes." (shown at 0.19, a result of the Then line at 0.94).
Action: recorded again

## AT-40, question (a)

Question: the facts
Probability: 0.91
Reason: No file may show this fact of the Then line: "each Clinch line of the file shows under its team, names the Goal, and names at most 2 other results before "and N more results"." (shown at 0.09).
Action: recorded again
