# 13: Start or sit by projection

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-7, AT-8, AT-9, AT-10, AT-12, AT-53.

**App:** both

**What to build:** A new personal Topic, Start or sit (`start_sit`), gives Your team its Week lineup for the live week from live Sleeper data, by projection only. The lineup block lists the slots in Sleeper order with the slot, the player, his team, the opponent, the kickoff, and the projection in league points. A Q row shows the body part, the practice level or "No practice report yet", and the Pivot line. OUT, IR, and bye players sit in the "Can't play" line. The game lock reads the Sleeper `scores` query, with the ESPN scoreboard as the fallback. An open row does not move the other rows.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The cpc lineup shows QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF in order (AT-1).
- [ ] The norcal lineup shows three FLEX and no DEF (AT-2).
- [ ] One projection equals its stat line scored with the cpc scoring, to 0.1 point (AT-3).
- [ ] A Q row shows the body part, the practice level, and the Pivot line, and a null practice level reads "No practice report yet" (AT-7, AT-8).
- [ ] An open row keeps the rows above it still, and the "Can't play" line names each such player (AT-9, AT-10).
- [ ] A player whose game has started is locked, and Start or sit calls only Sleeper, ESPN, TypeSafe, and Anthropic (AT-12, AT-53).
- [ ] The design bar of the spec ran, and `critique` and `polish` found nothing open.
