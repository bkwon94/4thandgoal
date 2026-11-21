# 13: Step 2 and the spread of the Shortlist

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-43, AT-45, AT-46, AT-47, AT-59, AT-60, AT-61, and AT-62.

**App:** api

**What to build:** The offers that pass step 1 group by partner and by shape direction, and the best of each group, by the fair mean, goes to step 2. Step 2 asks the need Noul and the gain Noul of each side. A clear no on the gain of either side drops the offer, an unsure answer stays, and a failed call is an error, never a drop. No need answer drops an offer. The Spares tree still runs once per pair and builds no offer. A "yes" for a player that the asker gets becomes a pick sheet fact, such as "fills the weak slot QB, and the partner can spare him." The score of an offer is the fair mean alone. `varied()` puts first the best offer for each shape direction, then for each partner, then for each player the asker gives, and the rest follow by score, in a Shortlist of 10 (decisions 15 and 16). `GLOSSARY.md` updates the entries Target, Offer, and Spares tree to match: no targets step, an Offer comes from the Value screen only, and the Spares tree gives reasons, not a gate.

**Blocked by:** 12

**Status:** done

- [x] A real press for Bo Girds sends at most three offers per partner and shape direction to step 2, no more than 231, each among the three highest fair means of its group.
- [x] Tests with fixed answers show that a gain of 0.2 drops an offer, 0.5 keeps it, a failed call raises an error, and need answers of 0.1 on both sides drop nothing.
- [x] A test shows a Spares tree "yes" as a pick sheet fact on a Value offer, with the same count of offers.
- [x] The Shortlist of a real press puts the best offer of each shape direction first, then of each partner, then of each player, and the rest by fair mean.
- [x] Neither "Kenneth Walker III for Patrick Mahomes" nor "Zay Flowers for Jared Goff" is on the Shortlist of a real press, and the backtest command passes its bar.

## Comments

- 2026-11-20: Brian chose the top 3 offers of each partner and shape direction for step 2, because the gain check left the Shortlist thin.

The merge: `deadline-week-13` merged into `deadline-week` as a fast-forward before `268e92a8` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/13-step-two-and-the-spread.md.
Closes with the squash merge of the spec PR.
