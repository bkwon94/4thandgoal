# 09: The result shows the players once, and Edit moves

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-30, AT-31, and AT-32.

**App:** site

**What to build:** Under a result, the hero is the one place that shows the players. The "The Trade" chapter with the swap card leaves the result, and the swap card stays in the Finder. Each panel of "The Sides" keeps its bullets and its week lines, and drops its player lists. In the fairness block, a reason longer than about 3 lines folds, with a "More" control that opens it. The `FoldLine` card leaves the page, in the wait and under a result. Edit becomes a text button with a pencil icon at the right of the "The Sides" header, with a touch target of at least 44 px. A tap opens the Stack with the graded trade and scrolls to it. Follow the decision in `decisions/06-prototype-compact-stage-and-edit.md` and the design bar of the spec.

**Blocked by:** 08

**Status:** done

- [x] The result of trade T has no "The Trade" chapter, and below the hero it has no player chip, no headshot, and no `FoldLine` card.
- [x] The Finder still shows its swap card.
- [x] A tap on Edit in the header of "The Sides" opens the Stack with trade T, in view.
- [x] The Edit target is 44 px or more on each side.
- [x] A fairness reason past 3 lines at 375 px shows 3 lines and "More", and a tap shows it in full.

## Comments

The merge: `d65298a4` merged into `analyzer-stage` on 2026-11-17; review fixes `a8f2b48d` and `4eb5bef2`; Judge fix round `7b1d09c7`.
The proof: `make check-fast` passed at each merge, the full check passed on 2026-11-17, and the Judge gave PASS to AT-1 to AT-34 after one fix round.
The note: A grade that the Finder starts has no screen-reader status after fix AT-9 `367ac9b0`; the Finder is on only in norcal. The rank lines of the result are gone, and a later ticket can bring them back on a tap of a token.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/analyzer-stage/PRD.md, .scratch/analyzer-stage/ACCEPTANCE.md, .scratch/analyzer-stage/issues/09-the-result-shows-the-players-once.md.
Closes with the squash merge of the spec PR.
