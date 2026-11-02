# 01: Storylines, the Must Watch pick, and the reason

Spec: `.scratch/next-week-storylines/PRD.md`, all sections. Glossary: "Must Watch", "Storyline", "Streak on
the line", "Shootout", "Rematch".

**What to build:** Each next-week game gets its storylines from the six-kind set with the weights as tunables.
The top two games by the sum are Must Watch, ties by the smaller standings gap then schedule order. The reason
names the game's top two storylines in one sentence with the numbers. The old table-gap signal for the preview
goes away. The page rows keep their shape.

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] A team on 3 straight head-to-head wins gives its game the streak storyline; 2 straight does not; the median game never counts.
- [ ] Both teams in the top four projected lineups give a shootout with both totals; one team fifth gives none.
- [ ] Two teams that met in week 3 give a rematch that names week 3, the winner, and the margin; the loser gets revenge.
- [ ] Near the cut and top of the table read as the spec says.
- [ ] The top two games by storyline score are Must Watch; the tie rule holds.
- [ ] The reason is one sentence of 25 words or fewer that names the top two storylines with their numbers.
- [ ] The six weights live in the tunables.
- [ ] Every existing next-week and swing test passes, or changes with a named reason.

## Comments

- 2026-11-02: `main` holds the merge 3fe2bf4. Status set to done by the state-file sweep of agent-habits 02.
