# 03: The team pick

Spec: `.scratch/waiver/pipeline/PRD.md` in the pipeline repo.

**What to build:** A manager picks his team once on the waiver page with the same team list the
analyzer uses, one list, no second picker. The pick saves on the phone under its own key with the
guarded storage pattern of the passphrase. The masthead shows the pick as a chip with a Change link.
With a pick, his bar in the ring turns red and the sheet says how many teams can outbid him at his
budget, from the outbid counts in the file. With no pick, the page renders with no red bar and no
outbid count. The pick never touches the analyzer's two sides.

**Blocked by:** 02 The War chest look.

**Status:** done

- [x] The picker renders the team list and a pick collapses it to the chip.
- [x] The pick survives a reload, and a storage throw leaves the page working for the visit.
- [x] With a pick, the matching bar is red and the sheet shows the outbid count for that budget.
- [x] With no pick, no bar is red and the sheet has no outbid line.
- [x] Change opens the list again and a new pick replaces the old.
- [x] The analyzer tests still pass with no change to its sides.

## Comments

- The chip sits at the top of the dark chapter under the masthead, because the masthead is a server component.
