# 04: Which Advisor arm Brian agrees with most

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** prototype

**Blocked by:** none. The `jev` spec is on `main`, with ADR 0029. Merge `main` into this branch first.

**Status:** done

## Question

Run three arms on the test set of ticket 01, with the cpc playbook: Jev alone with one yes or no, Jev atomic questions with a code table, and Claude that reads the facts and the Jev answers. Each arm gives a lean and a case per trade. Brian marks agree or disagree where the arms disagree or a read looks wrong, and the arm he agrees with most wins. Claude expects the Claude arm to win, and Brian asked for the data. The prototype also sets the exact Jev questions for each side and each partner, the shortlist table and its size, and the fact sheet. Load the `typesafe:typesafe-ai` skill first. Ask Brian before any live call, with a budget, within the rate limits of decision 03: 80 requests and 100,000 tokens per second. Measure the cost and the time of the finder with targets, and show Brian the targets of each side.

## Decision

The prototype ran on 2026-11-09 for $3.48 of a $5 budget. Brian marked 24 of 28 trades. The notes, the questions, and the prompt shapes are in `04-prototype-judge-arms.notes.md`. The script is deleted.

1. **The Claude arm wins.** Brian agreed with Claude on 20 of 24 trades, with Jev alone on 17, and with Jev atomic on 16. On the 11 trades where the arms split, the counts are 8, 5, and 4. The roles of ADR 0030 stand: Claude makes the call, and the Jev atomic answers go to it as inputs.
2. **The misses of Claude show what the sheet lacks:**
   - Trade 6: Claude missed the RB room after the trade. Brian: "Giving up your best RB and leaving with no reliable RB at all is not good, especially when rb is scarce." The sheet states the RB depth after the trade plainly, and the playbook tip on RB scarcity gets stronger.
   - Trades 15, 16, and 19: Claude was one lean too warm. Brian wanted Lean no on 15 and 16, and Gut call on 19.
   - Trade 24 (all arms missed): "hampton is just awful on an awful team." The sheet gets the quality of the NFL team as a measure, from the nflverse team stats.
   - Finder: "Taylor is on the colts who are trash. He is in trade rumors." News is new fog, in decision 08.
   - Finder: "Would this ever happen? idk because lil fridge is shallow at WR." The read of "would he accept" weighs the depth of the other team.
3. **The finder works, with these settings:** the partner filter with the weak slot of the asker in the state; targets at p 0.6 or more, at most 4 per side; offers from targets only; a shortlist of the 10 offers that Jev rates highest, by the product of "close to fair for both" and "fills a starting need" for each side; the Advisor picks up to three. Wording "a" of the fairness and need questions won the probe. Brian agreed with the targets and the picks of both askers he marked.
4. **The partner filter stays,** on Brian's call: "no keep it i think". It passed 9 or 10 of 11 partners, so it cuts little now. The spec may tune its questions.
5. **Cost and time per press:** about $0.10 to $0.12 and 19 to 25 s. The Claude pick is almost all of it. Jev costs about $0.01 over about 30 requests in 3 to 4 s, inside the rate limits.
6. **The checks:** no invented number got through in about 36 Claude calls. Three bullets used the inner word "trade value". The retry of the real build catches those.
7. **The test set** is now 28 trades: 8 real trades of weeks 6 and 7 on full snapshots, with each roster set back to before the trade, and the 20 week 8 trades.
