# front-door: Evidence flags

The agent sets the action of each entry: `recorded again`, `fix group`, `disagree: <one line>`, or `open`. The Judge never reads this file.

## AT-4, question (a)

Question: the facts
Probability: 0.70
Reason: No file may show this fact of the Then line: "3 Suggestion chips show, each with a Topic name and one number, and "More" leads the row." (shown at 0.30).
Action: disagree: `row-*.txt` lists More first, then 3 chips, each with a Topic name and one number, and the shots show them.

## AT-20, question (d)

Question: the Observation
Probability: 0.77
Reason: No file may show this sentence of the Observation: "Light: the mark reads "Checking" in rgb(102, 102, 102), the mute color, from 8.39 s, and turns to "Checked" in rgb(20, 20, 20), the ink color, at 11.02 s through a blur cross-fade." (shown at 0.21, a result of the Then line at 0.98).
Action: disagree: `samples-light.txt` holds the Checking line at 8.388 s in rgb(102, 102, 102) and the Checked line at 11.021 s in rgb(20, 20, 20).

## AT-44, question (d)

Question: the Observation
Probability: 0.72
Reason: No file may show this sentence of the Observation: "word-samples.txt shows the free answer text of 51 words show at 6.69 s, all 51 blurred, then the blurred count drops by about 5 words every 50 ms to 0 at 7.39 s." (shown at 0.27, a result of the Then line at 0.98).
Action: disagree: `word-samples.txt` holds 51 words, 51 blurred, at 6.685 s, and the count of blurred words falls to 0 after.

## AT-58, question (d)

Question: the Observation
Probability: 0.71
Reason: No file may show this sentence of the Observation: "The picks are Derrick Henry (0.64) and Justin Jefferson (0.11), both `sure: false`, and the answer part is a `form` with empty `gives` and `gets`." (shown at 0.28, a result of the Then line at 0.98).
Action: disagree: `api-calls.json` holds both picks, Derrick Henry at 0.64 and Justin Jefferson at 0.11, each with `sure: false`.

## AT-64, question (d)

Question: the Observation
Probability: 0.91
Reason: No file may show this sentence of the Observation: "The route is `free` (fits_topic 0.49)." (shown at 0.05, a result of the Then line at 0.96).
Action: recorded again: the Observation now gives fits_topic 0.44, as `api-calls.json` holds.

## AT-72, question (a)

Question: the facts
Probability: 0.78
Reason: No file may show this fact of the Then line: "Each total matches the standings data." (shown at 0.22).
Action: recorded again: `standings-points-for.txt` now holds the live `standings` tool result, and the Observation compares the totals with it.
