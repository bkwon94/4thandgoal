# 01: Does a side that gets a superstar get a step up?

Map: `.scratch/uneven-trade/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Brian asks for a superstar step: a side that gets a player worth 55 or more gets one step up. No adjuster does this now. Only the 1.25 Consolidation margin pays for a star, and only in a trade of one player for two or more.

The trade that raised it: client `cpc`, week 9. Roster 6, Bo Girds, gives Parker Washington and Kenneth Walker III to roster 12, Teehee. Teehee gives Tee Higgins, Bhayshul Tuten, and Tony Pollard. Walker is 64.0 on the week 9 chart, and the only player at 55 or more.

The spec needs these four answers:

1. The threshold: a fixed chart value such as 55, or a rank such as a top-5 value. Chart values change with the format, such as `1QB0.5PPR4pt`.
2. The giver: does the side that gives the superstar get a step down?
3. The double count: does the step apply in a one-for-many trade, where the 1.25 margin already pays for the star?
4. Two superstars: what happens when both sides get a player above the threshold?

## Decision

Brian decided it in a grill on 2026-11-05.

1. A superstar is a player in the top 8 chart values of the week, over all positions. `SUPERSTAR_RANK = 8` in `tunables.py` sets it. A fixed rank works the same in every chart format. A fixed value such as 55 does not.
2. A side that gets a superstar gets one step up. Two superstars to one side still give one step.
3. The side that gives a superstar gets no step. Each adjuster reads only what a side gets, and the chart ratio already charges the giver.
4. The step applies in an even count and with the 1.10 margin. It does not apply with the 1.25 margin of one for many, because that margin already pays for the star.
5. Each side that gets a superstar gets the step, so one trade can give the step to both sides.
6. With no chart in the week, the check reads the chart of the week before.
7. Superstar is a new glossary term beside Star. Star is a rank inside one position. Superstar is a rank over all positions.

The spec sets the place of the step in the adjuster order and its reason text. The place matters, because the fairness reason shows the first up step.
