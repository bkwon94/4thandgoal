# 02: A hole steps the grade

Spec: `.scratch/roster-fit-depth/PRD.md`, "The line and the bounds", "The side reads", "The hole kinds", "The
step", "The fit reason", "The rubric prompt", "Prose rules". Glossary: "The line", "Hole", "Handcuff".
Decision record: ADR 0003.

**What to build:** Roster fit reads the side's starting slots before and after the trade, each with its player and
his rank. The line is rank 36 at RB and WR and rank 24 at QB and TE, as two tunables. A slot that holds a player
below the line, or holds no player, is a hole. A FLEX slot reads the line of the player's own position. K and DEF
slots are never holes. A hole in the after set and not in the before set is new. A new hole is one step down and
blocks the step up for a lineup gain and for the highest-value rule. A hole both before and after gives no step.
The handcuff block narrows: it blocks a step down for a lineup loss and never for a hole. The one-for-two rule
stays. The fit reason for a new hole is one sentence with the slot, the player, and his rank. The other sentences,
the due-back notes, and the in-progress label stay as today. The rubric prompt's roster fit section states the
reads, the line, the hole kinds, and the step rule in the glossary's words, and the handcuff section drops the
sentence that the block is broad. The vocabulary ban gains "replacement", "tier", "floor", and "gap". The build
report of this ticket lists every week 6 hand-worked trade whose letter moves, with old and new.

**Blocked by:** 01 (The rank table and the cache key).

**Status:** ready-for-agent

- [ ] A side that gives two backs and gets two receivers, with its RB2 slot then below the line, steps down and the reason names the slot, the player, and his rank.
- [ ] A side that gets a back who fills a hole at RB2 and gains in the lineup steps up.
- [ ] A side with the same hole before and after gets no step for it and the reason does not name it as new.
- [ ] A side that gets the highest-value player and opens a new hole gets no step up.
- [ ] A side that gives its starter for his handcuff and opens a hole steps down.
- [ ] A side that gets a handcuff with a lineup loss and no hole still gets no step down.
- [ ] A FLEX slot with a WR below 36 is a hole; a FLEX slot with a TE at 20 is not.
- [ ] A DEF slot never makes a hole.
- [ ] The rubric prompt states the step rule and the narrowed handcuff block, and `ste` passes on the new text.
- [ ] No reason or prompt uses "replacement", "tier", "floor", or "gap".
- [ ] Every existing fit test passes unchanged or with a named reason change in the build report.
- [ ] The build report lists every hand-worked trade whose letter moves, with old and new letters.
