# 04: Depth, strength, and slot facts for Claude

Spec: `.scratch/roster-fit-depth/PRD.md`, "The facts", "The side reads", "The document". Glossary: "Depth",
"Strength". Decision record: ADR 0003.

**What to build:** The trade fact sheet gains, per side: one slot fact per player the side gets, with the slot he
takes and the player he pushes out or that he sits on the bench; one depth fact per position whose count above
the line changes, with the count before and after; and one strength fact when the count of RB1, RB2, WR1, and
WR2 inside the top 24 changes, with the strength bound as a tunable. Each fact carries its numbers, so the
analysis checker accepts them in the prose. Claude's side analysis can then say "both backs were top 24 before
the trade and one is after" in its own words. The result document keeps its shape. The site needs no change.
Depth and strength never move the step.

**Blocked by:** 02 (A hole steps the grade).

**Status:** done

- [ ] The fact sheet for a trade names, per player a side gets, the slot he takes and the player he pushes out.
- [ ] A player the side gets who starts in no slot gets a fact that says he sits on the bench.
- [ ] A trade that drops a side's RB depth from three to one gives a depth fact with both counts.
- [ ] A position whose depth count does not change gets no depth fact.
- [ ] A trade that drops the top-24 starter count from four to three gives a strength fact with both counts.
- [ ] The analysis checker accepts a sentence that quotes a cited depth count or strength count.
- [ ] The result document has no new field and the site renders the grade with no change.
- [ ] Every existing analysis test passes unchanged.

## Comments

- 2026-11-02: `main` holds the merge 84d9349. Status set to done by the state-file sweep of agent-habits 02.
