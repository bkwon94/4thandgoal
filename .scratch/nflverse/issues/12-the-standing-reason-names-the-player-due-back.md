# 12 — The standing reason names the player due back

Spec: `.scratch/nflverse/PRD.md`, "The trade rubric". Found in the ticket 10 review on 2026-10-24.

**What to build:** `_standing` in `src/cornerstone/adjusters.py` says "the best lineup gains now" when a contender's
best lineup gains. After ticket 10 the gain can come from a player due back, whose projection ahead makes the
lineup value. "Now" is then wrong, because he does not play this week. When a player due back is in the side's
lineup gain, the reason names him and says the lineup gains after his return in week N. When no player due back is
in the gain, the reason stays as today.

**Why:** A manager reads "gains now" and expects a start this week.

**Blocked by:** None.

**Status:** open

- [x] A contender whose lineup gain comes from a player due back in week 9 reads "and the best lineup gains after Josh Jacobs returns in week 9."
- [x] A contender whose lineup gain comes from a healthy player reads "and the best lineup gains now." as today.
- [x] Every existing adjuster test passes unchanged.
