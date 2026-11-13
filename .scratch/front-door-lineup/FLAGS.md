# front-door-lineup: Evidence flags

The agent sets the action of each entry: `recorded again`, `fix group`, `disagree: <one line>`, or `open`. The Judge never reads this file.

## AT-2, question (d)

Question: the Observation
Probability: 0.72
Reason: No file may show this sentence of the Observation: "In the first run of this test the second curl gave 134.0 against 134.1, so the test ran again; in the second run both curls give the same block." (shown at 0.15, a result of the Then line at 0.85).
Action: disagree: `evidence/round.txt` line 7 states the first run gave 134.0 against 134.1 and that the test ran again.

## AT-5, question (a)

Question: the facts
Probability: 0.86
Reason: No file may show this fact of the Then line: "The second case keeps the starter." (shown at 0.14).
Action: recorded again: `output.txt` now holds the source of the parametrized test, with 0.69 giving no Swap; the second run gives 0 flags.

## AT-6, question (a)

Question: the facts
Probability: 0.97
Reason: No file may show this fact of the Then line: "The bench player at 0.85 takes the first slot." (shown at 0.03).
Action: recorded again: `output.txt` now holds the source of the test, with the 0.85 pair taking the RB slot; the second run gives 0 flags.

## AT-10, question (a)

Question: the facts
Probability: 0.99
Reason: No file may show this fact of the Then line: "Jacobs Out (finger)"." (shown at 0.01).
Action: disagree: "J. Jacobs Out (finger)" is the shape in the Then line; the AT-1 stream has `cannot_play` L. Jackson IR Thumb, and the shots show its line.

## AT-14, question (a)

Question: the facts
Probability: 0.95
Reason: No file may show this fact of the Then line: "Start or sit is first." (shown at 0.05).
Action: recorded again: `output.txt` now holds the source of the test that asserts Start or sit first; the second run gives 0 flags.

## AT-15, question (a)

Question: the facts
Probability: 0.90
Reason: No file may show this fact of the Then line: "The first fact has the shape "1 can't play, 1 Q"." (shown at 0.10).
Action: disagree: `pytest.txt` shows the fact "1 can't play, 2 Q", the Then shape with its own counts, and the live Suggestions show "Next kickoff".

## AT-18, question (d)

Question: the Observation
Probability: 0.72
Reason: No file may show this sentence of the Observation: "The free answer stream (22:19:34 UTC) has no data-block." (shown at 0.24, a result of the Then line at 0.95).
Action: disagree: the stream file has no `data-block` line at all, so the absence is in the file.

## AT-20, question (a)

Question: the facts
Probability: 0.88
Reason: No file may show this fact of the Then line: "The Answer is the honest miss, with no lineup and no Swap." (shown at 0.12).
Action: recorded again: `output.txt` now holds the source of both tests, which assert no `data-block` and one `data-miss`; the second run gives 0 flags.

## AT-32, question (a)

Question: the facts
Probability: 0.84
Reason: No file may show this fact of the Then line: "A roster with no clear sell shows its plain line." (shown at 0.16).
Action: disagree: `vitest.txt` shows the passed test "shows the plain line of a roster with no clear sell", as revised evidence for that case.

## AT-33, question (d)

Question: the Observation
Probability: 0.79
Reason: No file may show this sentence of the Observation: "Each offer has its sides with the rest-of-season points, a case, and bullets." (shown at 0.17, a result of the Then line at 0.95).
Action: disagree: the stream holds the `trade` block, whose sides carry `points` and `total` (87.5 and 65.2), with a headline and bullets per offer.

## AT-38, question (a)

Question: the facts
Probability: 0.99
Reason: No file may show this fact of the Then line: "Each block renders with no overflow and no overlap." (shown at 0.01).
Action: disagree: the facts are in the shots; the flag reads text only, and the shot lines describe each block at 375 and 1280 px.

## AT-45, question (b)

Question: motion
Probability: 0.82
Reason: The Then line may ask for motion (at 0.83), and the files hold no video, no timed frames, and no log of animation values (a log at 0.01).
Action: disagree: the Then line asks for the place and the rows of the sheet, not for motion; the shots show both.

## AT-46, question (a)

Question: the facts
Probability: 0.73
Reason: No file may show this fact of the Then line: "The focus goes to the sheet on open and back to the menu button on close." (shown at 0.27).
Action: recorded again: `output.txt` now holds `expectClosed`, which checks the focus is back on the menu button in each close case; the second run gives 0 flags.
