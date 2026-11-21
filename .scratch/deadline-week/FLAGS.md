# deadline-week: Evidence flags

The agent sets the action of each entry: `recorded again`, `fix group`, `disagree: <one line>`, or `open`. The Judge never reads this file.

## AT-8, question (d)

Question: the Observation
Probability: 0.84
Reason: No file may show this sentence of the Observation: "At each size and theme the top padding and the bottom padding are each 8 px (difference 0), and the eyebrow and the countdown both start at x 32 (difference 0) (measure.jsonl)." (shown at 0.13, a result of the Then line at 0.96).
Action: disagree: measure.jsonl has topPadding 8, bottomPadding 8, eyebrowX 32, countdownX 32 on each of its 6 lines.

## AT-9, question (d)

Question: the Observation
Probability: 0.73
Reason: No file may show this sentence of the Observation: "The button name is "Open the Trade Wire, final." (shown at 0.02, a result of the Then line at 0.75).
Action: disagree: measure.jsonl bannerAriaSnapshot holds the button name "Open the Trade Wire, final. The trade deadline has passed." on each line.

## AT-12, question (d)

Question: the Observation
Probability: 0.71
Reason: No file may show this sentence of the Observation: "`search.txt` lists 15 text dumps: the front door, the open Trade Wire sheet, and the analyzer at the three times on `19371052`, and the analyzer in Find mode and the sheet with the flag on at the three times on `0807c881`." (shown at 0.23, a result of the Then line at 0.92).
Action: disagree: search.txt has 15 lines, one per text dump, each with 0 hits; the commit of each dump is in the Commit line, not in the file.

## AT-15, question (a)

Question: the facts
Probability: 0.92
Reason: No file may show this fact of the Then line: "The log shows one Sleeper read for the first two calls and a second Sleeper read for the call at 6 s." (shown at 0.08).
Action: disagree: output.txt shows two httpx Sleeper reads after the call at 0.33 s, none after the call at 2.20 s, and two after the call at 6.21 s.

## AT-21, question (a)

Question: the facts
Probability: 0.70
Reason: No file may show this fact of the Then line: "The sheet shows the live dot and "Updated 3s ago"." (shown at 0.30).
Action: recorded again

## AT-36, question (b)

Question: motion
Probability: 0.73
Reason: The Then line may ask for motion (at 0.75), and the files hold no video, no timed frames, and no log of animation values (a log at 0.03).
Action: disagree: the Then line asks for one line at a time that holds until the next step, and measure.jsonl gives each line text with its time; it asks for no motion value.

## AT-37, question (b)

Question: motion
Probability: 0.73
Reason: The Then line may ask for motion (at 0.96), and the files hold no video, no timed frames, and no log of animation values (a log at 0.24).
Action: disagree: the Then line asks for the order of the lit avatars, and measure.jsonl gives each lit set with its time and the stream order.

## AT-37, question (d)

Question: the Observation
Probability: 0.78
Reason: No file may show this sentence of the Observation: "In each press the avatars light one by one, in the order of the stream parts `data-team` (for example 1, 5, 3, 2, 10, 11, 7, 9, 12, 8, 4), all within about 0.2 s, about 2.6 to 4.8 s after the tap (measure.jsonl: lit avatars with seconds, and the stream order)." (shown at 0.20, a result of the Then line at 0.98).
Action: disagree: measure.jsonl litAvatarsWithSecondsFromTap and teamPartsOfStreamInOrder hold the order and the times of the Observation.

## AT-41, question (a)

Question: the facts
Probability: 0.80
Reason: No file may show this fact of the Then line: "Each press ends in 30 s or less, with one pick call and no id retry." (shown at 0.20).
Action: disagree: output.txt shows wall times 23.93, 22.76, 27.97 s, one FinderPickOut call per press, claude_calls=1, and no repair or retry line.

## AT-42, question (a)

Question: the facts
Probability: 0.99
Reason: No file may show this fact of the Then line: "The log shows no Partner filter step, and the Shortlist holds 2 or more offers." (shown at 0.01).
Action: disagree: the gain check of ticket 09 drops each offer that gets a clear no; a code floor on the count would be a math filter (no-math-filters). The Judge reads the files.

## AT-43, question (a)

Question: the facts
Probability: 0.85
Reason: No file may show this fact of the Then line: "The best offer of each player of Bo Girds and the best offer of each partner come before a second form of any trade." (shown at 0.15).
Action: disagree: varied() follows the Shortlist rule of the PRD, proved by the replay of fix group h; Brian approved the new AT-43 text.

## AT-46, question (a)

Question: the facts
Probability: 0.95
Reason: No file may show this fact of the Then line: "Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is on the Shortlist or among the 3 trades." (shown at 0.05).
Action: disagree: Brian's Backtest mark 2 records Flowers for Goff as a known wrong keep; a fix needs a change of the IR projection, a follow-up out of this spec.

## AT-47, question (a)

Question: the facts
Probability: 0.99
Reason: No file may show this fact of the Then line: "The output lists each mark with its result, and every mark is right." (shown at 0.01).
Action: disagree: the backtest sets the floor at 1 of 5 by design; the PRD asks for the count to hold or rise, not for every mark to pass now.

## AT-9, question (d)

Question: the Observation
Probability: 0.72
Reason: No file may show this sentence of the Observation: "The button name is "Open the Trade Wire, final." (shown at 0.03, a result of the Then line at 0.74).
Action: disagree: measure.jsonl bannerAriaSnapshot holds the button name "Open the Trade Wire, final. The trade deadline has passed." on each line (cacd779f).

## AT-18, question (d)

Question: the Observation
Probability: 0.97
Reason: No file may show this sentence of the Observation: "With the flag on and trade W served, the DOM order and the top of each part inside the sheet are: "Grade a trade" and "Find a trade" (index 3 and 4, side by side), the eyebrow "Trade deadline ~2d 14h 05m" (index 6, shown upper case), "Trade Wire" (8), the live dot with "Updated 0s ago" (9), and trade W (14), each lower on the screen than the one before (measure.jsonl)." (shown at 0.02, a result of the Then line at 0.99).
Action: recorded again

## AT-36, question (d)

Question: the Observation
Probability: 0.71
Reason: No file may show this sentence of the Observation: "The wait shows one line at a time, each held until the next step starts: "1 of 5 · Reading every team" from the tap, "2 of 5 · Looking for players who fit" at 3.1 to 16.4 s, "3 of 5 · Building offers" and "4 of 5 · Making a shortlist" 0.3 to 1.2 s later, and "5 of 5 · Picking the best 3" at 4.3 to 18.4 s, which holds until the answer (measure.jsonl)." (shown at 0.24, a result of the Then line at 0.93).
Action: disagree: the lineTextWithSecondsFromTap rows of measure.jsonl give 2 of 5 at 3.12 to 16.42 s, 3 and 4 of 5 0.35 to 1.21 s later, and 5 of 5 at 4.26 to 18.43 s.

## AT-37, question (b)

Question: motion
Probability: 0.84
Reason: The Then line may ask for motion (at 0.98), and the files hold no video, no timed frames, and no log of animation values (a log at 0.14).
Action: disagree: the Then line asks for the order of the lit avatars, and measure.jsonl gives each lit set with its time and the stream order (cacd779f).

## AT-9, question (d)

Question: the Observation
Probability: 0.78
Reason: No file may show this sentence of the Observation: "The button name is "Open the Trade Wire, final." (shown at 0.02, a result of the Then line at 0.80).
Action: disagree: the quote cuts at the period inside the name; measure.jsonl bannerAriaSnapshot holds "Open the Trade Wire, final. The trade deadline has passed." on each line (98d79f98).

## AT-15, question (a)

Question: the facts
Probability: 0.92
Reason: No file may show this fact of the Then line: "The log shows one Sleeper read for the first two calls and a second Sleeper read for the call at 6 s." (shown at 0.08).
Action: disagree: output.txt shows two httpx Sleeper reads after the call at 0.44 s, none after the call at 2.22 s, and two after the call at 6.32 s (98d79f98).

## AT-36, question (b)

Question: motion
Probability: 0.79
Reason: The Then line may ask for motion (at 0.81), and the files hold no video, no timed frames, and no log of animation values (a log at 0.03).
Action: disagree: the Then line asks for one line at a time with its hold, and measure.jsonl gives each line with its start and hold time; it asks for no animation value (98d79f98).

## AT-37, question (b)

Question: motion
Probability: 0.76
Reason: The Then line may ask for motion (at 0.97), and the files hold no video, no timed frames, and no log of animation values (a log at 0.22).
Action: disagree: the Then line asks for the order of the lit avatars, and measure.jsonl gives each lit set with its time and the stream order (98d79f98).

## AT-38, question (a)

Question: the facts
Probability: 0.71
Reason: No file may show this fact of the Then line: "Up to 5 cards show in one list under the hero, each with a Lean of Send it, Lean yes, or Gut call, a Case of at most 3 lines, folded Bullets, and no headline." (shown at 0.29).
Action: disagree: measure.jsonl gives 4 or 5 cards per result, each Lean, renderedLines 2 or 3 with clamp 3, bulletsFolded true, and the Lean as the only heading (98d79f98).

## AT-45, question (d)

Question: the Observation
Probability: 0.77
Reason: No file may show this sentence of the Observation: "In the fair step, a mean of 0.25 drops and 0.35 stays, and a failed fair request drops no offer." (shown at 0.19, a result of the Then line at 0.95).
Action: recorded again

## AT-49, question (a)

Question: the facts
Probability: 0.78
Reason: No file may show this fact of the Then line: "All 10 answers arrive with no retry line." (shown at 0.22).
Action: disagree: runs.txt and run-<n>.json give runs 1 to 10 each with the trade ideas answer and 0 retry lines; the extra 429 ask on API 1 is labeled and shows no retry line (98d79f98).

## AT-49, question (d)

Question: the Observation
Probability: 0.74
Reason: No file may show this sentence of the Observation: "All 10 runs end with the trade ideas answer in 45.6 to 78.0 s, with 0 retry lines on the page, one POST /trade-ideas that answers 200, and 0 lines "Trade stream failed" in the API log of each run (runs.txt, run-<n>.json, api-run-<n>.log)." (shown at 0.20, a result of the Then line at 0.92).
Action: disagree: runs.txt, run-<n>.json, and api-run-<n>.log of runs 1 to 10 hold each time, the POST status 200, and 0 'Trade stream failed' lines (98d79f98).

## AT-59, question (a)

Question: the facts
Probability: 0.78
Reason: No file may show this fact of the Then line: "The offer stays on the Shortlist." (shown at 0.22).
Action: recorded again

## AT-61, question (a)

Question: the facts
Probability: 0.94
Reason: No file may show this fact of the Then line: "That offer gets the fact "fills the weak slot QB, and the partner can spare him", and the count of offers stays the same." (shown at 0.06).
Action: recorded again

## AT-63, question (a)

Question: the facts
Probability: 0.92
Reason: No file may show this fact of the Then line: "The partner sends 3 or more requests, each under 64,000 tokens by the estimate, and no offer passes as unsure." (shown at 0.08).
Action: recorded again

## AT-72, question (b)

Question: motion
Probability: 0.82
Reason: The Then line may ask for motion (at 0.85), and the files hold no video, no timed frames, and no log of animation values (a log at 0.04).
Action: disagree: the Then line asks when each card shows, and measure.jsonl gives each trade part and each card count in the DOM with its time (98d79f98).

## AT-61, question (a)

Question: the facts
Probability: 0.84
Reason: No file may show this fact of the Then line: "That offer gets the fact "fills the weak slot QB, and the partner can spare him", and the count of offers stays the same." (shown at 0.16).
Action: disagree: after one new recording the flag stays; output.txt asserts the fact for the slot of each listed player with equal counts, and the live Shortlist dumps hold a QB Spares yes on each offer (98d79f98).

## AT-36, question (b)

Question: motion
Probability: 0.80
Reason: The Then line may ask for motion (at 0.82), and the files hold no video, no timed frames, and no log of animation values (a log at 0.03).
Action: disagree: the Then line asks for line timing, and measure.jsonl lineTextWithSecondsFromTap logs each line with its start and hold in seconds.

## AT-36, question (d)

Question: the Observation
Probability: 0.78
Reason: No file may show this sentence of the Observation: "The stream sent the live lines of steps 2 to 4 within 0.19 s and step 5 at 5.24 to 5.82 s (`stepEventsWithSecondsFromTap` and the stream files), so each line waits for the hold of the line before it." (shown at 0.19, a result of the Then line at 0.96).
Action: disagree: stepEventsWithSecondsFromTap of each press has the step 2 to 4 live lines within 0.19 s and step 5 at 5.24 to 5.82 s.

## AT-72, question (b)

Question: motion
Probability: 0.86
Reason: The Then line may ask for motion (at 0.89), and the files hold no video, no timed frames, and no log of animation values (a log at 0.03).
Action: disagree: the Then line asks for order and timing, and cardsInDomWithSecondsFromTap and tradeEventsWithSecondsFromTap log each card and part with times.

## AT-73, question (b)

Question: motion
Probability: 0.89
Reason: The Then line may ask for motion (at 0.92), and the files hold no video, no timed frames, and no log of animation values (a log at 0.03).
Action: disagree: the Then line asks for line timing, and step5LinesWithSecondsFromTap and step5-summary.txt log each step 5 line with its start and hold.
