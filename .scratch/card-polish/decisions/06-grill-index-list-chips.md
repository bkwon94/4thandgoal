# 06: What do the chips of the Index list filter on?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The Index list puts chips above the list of team names. A tap on a chip filters the list. Choices include the Roster grade letter, the record (in the playoff spots or out), and the division if a league has divisions. The spec needs one set of chips that works for both clients.

## Decision

Brian decided on 2026-11-07. The chips filter on the playoff race: **All · In · Bubble · Out**.

- In: clinched, or playoff odds of 75% or more.
- Bubble: playoff odds from 25% to 75%.
- Out: eliminated, or playoff odds under 25%.

The odds and the status word come from the page week of `rankings.json`. All is the default.

Why: it answers the question a manager asks in midseason, "who am I in a race with?", and it changes each week. Neither league has divisions. A filter by grade letter splits badly: half of each league is an A, and CPC has no B. Story tags (hot, cold, busy) each need a rule of their own.

The spec decides how a chip with no team looks, for example Out in week 2, and whether each chip shows its count. The spec adds In, Bubble, and Out to `GLOSSARY.md` if the words need one meaning across the site.
