# 16: How do the two sources merge, and how does the Shortlist spread them?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** 14, 15

**Status:** done

## Question

The Spares tree stays as one source of ideas, next to the value pairs (handoff ruling 6). Variety spreads the ideas across shapes and partners (ruling 5). Decide:

1. How the "can spare" answers of the Spares tree attach to a Value offer as a reason. Decision 15 ended the Spares tree offers.
2. How `varied()` spreads the Shortlist across shapes and partners, and how it keeps each best offer first (AT-43).
3. The size of the Shortlist, the number of offers per partner and per shape, and how many offers reach step 2 of decision 15.
6. The score that orders the Shortlist. Today it is fair times need. Decision 15 makes fair the mean of two side orders and makes need a reason, not a gate.
4. Whether a cap after the Value screen comes back, if the preview shows too many waves per press (decision 14).
5. Whether one pacer for the whole API process replaces one pacer per press. Two presses at once can pass the account limit of 100,000 tokens per second, because each pacer counts only its own press. The Fly config runs one uvicorn process per machine. Check the machine count.

## Decision

Brian decided each part on 2026-11-19.

1. **The Value screen is the one source of offers.** The targets step and the wider pass go. A search around one player keeps working: the anchor becomes a hard rule, so each Value offer holds him. The keep and aim choices of a manager also become hard rules on Value offers.
2. **Spares tree answers are facts.** The Spares tree still runs once per pair. A Value offer that brings the asker a player with a "yes" from the Spares tree gets a pick sheet fact, such as "fills the weak slot QB, and the partner can spare him." It drops no offer and changes no order.
3. **Step 2 gets the best offer of each group.** The offers that pass step 1 group by partner and by shape direction, up to 11 × 7 = 77 groups. The best offer of each group, by the fair answer, goes to step 2. So no shape and no partner disappears before the gain drop.
4. **The score is the fair answer alone,** the mean of the two side orders. The pick call weighs need, gain, and the Spares tree facts as reasons. A product with need would bring back the need-first order.
5. **The spread.** `varied()` puts first the best offer for each shape direction, then for each partner, then for each player the asker gives. The rest follow by score. The Shortlist stays at 10, so the cost of the pick call stays the same, and AT-43 still holds.
6. **One pacer for the API process.** The Fly app `cpcfantasy-api` runs one machine with one process (`fly machines list`, 2026-11-19). One shared pacer covers every press, so two presses at once stay under 100,000 tokens per second. A second machine needs a new decision. No cap follows the Value screen, per decision 14.

**For the spec.** The glossary entries Target, Offer, and Spares tree change when the build lands: no targets step, an Offer comes from the Value screen only, and the Spares tree gives reasons, not a gate.
