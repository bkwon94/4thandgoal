# 08: The compact stage

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-2, AT-20, AT-27, AT-28, and AT-29.

**App:** site

**What to build:** The stage of the analyzer hero becomes one slim row per side, asker first: the team avatar, the full team name, "gets", then up to 3 overlapped headshot tokens and a "+N" token for the rest. A headshot that fails to load shows the initials of the player. In idle, a row shows the team and a player count, such as "5 players", or a dashed empty token, and no headshot. On the pending state of the grade button, the headshots rise into each row with a stagger by row and by token, and a blur that clears. With motion off, the tokens fade in. The same rows sit on the result hero, and their mesh anchors replace the empty columns, so the dip of the reveal sits under the right row. Start from the round 2 prototype A in `~/plans/analyzer-stage-prototype/stage-06-round2/` and the decision in `decisions/06-prototype-compact-stage-and-edit.md`, but rewrite it. Follow the design bar of the spec.

**Blocked by:** none

**Status:** ready-for-agent

- [x] In idle with trade T, the rows show "2 players" and "1 player", and the hero shows no headshot.
- [x] Within 1 s of the tap on "Grade the Trade", each row of trade T shows the headshots of the players it gets.
- [x] With trade B in the wait, the stage shows 3 rows, and the row of The Blue Tent shows 3 headshots and "+2".
- [x] The result hero of trade T shows the same rows, and the mesh dips under the row of the favored side.
- [x] With reduced motion, the headshots fade in and no token moves.
- [x] The pixel scan of the floor passes on the analyzer in idle, wait, and reveal, in both clients.
