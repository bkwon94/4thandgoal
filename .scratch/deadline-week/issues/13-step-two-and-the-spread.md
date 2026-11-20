# 13: Step 2 and the spread of the Shortlist

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-43, AT-45, AT-46, AT-47, AT-59, AT-60, AT-61, and AT-62.

**App:** api

**What to build:** The offers that pass step 1 group by partner and by shape direction, and the best of each group, by the fair mean, goes to step 2. Step 2 asks the need Noul and the gain Noul of each side. A clear no on the gain of either side drops the offer, an unsure answer stays, and a failed call is an error, never a drop. No need answer drops an offer. The Spares tree still runs once per pair and builds no offer. A "yes" for a player that the asker gets becomes a pick sheet fact, such as "fills the weak slot QB, and the partner can spare him." The score of an offer is the fair mean alone. `varied()` puts first the best offer for each shape direction, then for each partner, then for each player the asker gives, and the rest follow by score, in a Shortlist of 10 (decisions 15 and 16). `GLOSSARY.md` updates the entries Target, Offer, and Spares tree to match: no targets step, an Offer comes from the Value screen only, and the Spares tree gives reasons, not a gate.

**Blocked by:** 12

**Status:** ready-for-agent

- [x] A real press for Bo Girds sends at most one offer per partner and shape direction to step 2, no more than 77, each the highest fair mean of its group.
- [x] Tests with fixed answers show that a gain of 0.2 drops an offer, 0.5 keeps it, a failed call raises an error, and need answers of 0.1 on both sides drop nothing.
- [x] A test shows a Spares tree "yes" as a pick sheet fact on a Value offer, with the same count of offers.
- [x] The Shortlist of a real press puts the best offer of each shape direction first, then of each partner, then of each player, and the rest by fair mean.
- [x] Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is on the Shortlist of a real press, and the backtest command passes its bar.
