# 15: Which questions does Jev answer for each shape?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** 13

**Status:** done

## Question

Code gives the chart values and the sum of each side. Jev judges from those facts (handoff ruling 3). Decide the questions for each shape:

1. Fairness of the trade.
2. The consolidation premium: does the team that gets more players get more total value? It should, because the single player is the better one.
3. The lineup gain of each side.
4. Whether the gain check of decision 09 stays as a clear-no drop.
5. Whether need moves from the gate to a reason in the Case (handoff ruling 6).

Use `typesafe:typesafe-ai` to word the questions and the state. Each change still passes the backtest bar of decision 05.

## Decision

Brian decided each part on 2026-11-19. Two live probes informed it: `decisions/15-grill-jev-questions-per-shape.notes.md`. Together they cost $0.004.

1. **No Jev question for the consolidation premium.** It is a sum of chart values, and the Value screen of decision 14 already holds it as a code rule. Jev gets only judgments that code cannot make.
2. **The state gets the chart facts.** Each player gets his `chart_value`. Each side under `offers.<n>.sides` lists its players and its `chart_sum`. These sit next to the facts of today: name, position, NFL team, Season rank, and injury status.
3. **Two steps.**
   - Step 1 asks `fair` of every offer. A clear no, below 0.3, drops the offer.
   - Step 2 asks `need` and `gain` of each side, for the offers that pass step 1. Decision 16 decides how many reach step 2.
4. **The fair wording is B.** On the 34 offers inside the screen, B gave 17 yes, 12 unsure, and 5 no. Today's `FAIR` text gave 9, 21, and 4. On the 10 offers just outside the screen, B gave 7 clear no and A gave 5.
   - Text: ``Is the trade in `offers.{n}` close to fair by chart value: {gives}?``
   - Yes: ``Each team gives about as much chart value as it gets, by the sums in `offers.{n}.sides`.``
   - No: ``One team gives a clearly larger chart sum in `offers.{n}.sides` than it gets back.``
5. **Both side orders.** Jev reads an offer as more fair when the team named first gets the larger sum. With the asker first, the gap between the two directions was a mean of 0.78 against 0.46. With the sides swapped it was 0.63 against 0.57. So step 1 asks B once in each order. Code takes the mean of the two answers, and a clear no on the mean drops the offer.
6. **The gain check of decision 09 stays.** In step 2, a clear no on the gain of either side drops the offer. It keeps Backtest marks 1 and 2 right, under the bar of decision 05.
7. **Need is a reason, not a gate.** No `need` answer drops an offer. The Case can name a need, and decision 16 decides whether need helps the order.
8. **The Spares tree builds no offers.** All 8 Spares tree offers of the probe and both Backtest marks got a clear no on fair in both orders, at most 0.18. So the Spares tree stops building its own offers. Its "can spare" answers become a reason in the Case of a Value offer. This keeps ruling 6, with the Spares tree as a source of reasons. The spec updates the glossary entry of the Spares tree, which still says that a side stops on it.
