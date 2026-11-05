# Uneven trade: map

App: both.
Spec branch: `uneven-trade`.

## DESTINATION

One spec for the trade grade. An uneven trade starts from values that discount the extra player, a superstar counts for the side that gets him, the fairness line explains each side by what moved its letter, and the form names no chart while the analyzer runs.

## DECISIONS SO FAR

- In an uneven count of two or more players, such as 3-for-2 or 4-for-3, divide the sum of the side with more players by `1.10`. One player for two or more keeps `CONSOLIDATION_MARGIN = 1.25`. Brian chose 1.10 over 1.15, because at 1.15 a 3-for-2 trade that is even in raw value starts the side that gets 3 at D. The handoff `.handoff/2026-11-05-uneven-trade-discount.md` holds the trade that showed it.
- The glossary term Consolidation widens to any trade where one side gets more players. It has two margins: 1.25 for one for many, and 1.10 for many for more. Brian decided it on 2026-11-05.
- The fairness reason of a side names what moved its letter: the first up step when the letter went up, the first down step when it went down. Brian approved it on 2026-11-05.
- A side that gets a top-8 chart value, a superstar, gets one step up. No step for the giver, none with the 1.25 margin, and the chart of the week before when the week has none. `decisions/01-grill-superstar-step.md`.
- The net sum of the steps picks the fairness reason: the first up step, the first down step, both joined by "but" at a net of zero, or the deal row with no steps. `decisions/02-grill-reason-when-steps-cancel.md`.
- While the analyzer runs, the form reads "This can take up to a minute early in the week." It names no chart. The line is in `packages/analyzer/site/form/trade-form.tsx` and `trade-finder.tsx`. Brian chose it on 2026-11-05.

## NOT YET SPECIFIED

- Where does the superstar step sit in the adjuster order, and what is its reason text? The spec records it.

## OUT OF SCOPE

- A change to `CLAMP_STEPS = 1`. The chart weighs more than the adjusters, and no trade so far shows a need to change it.
- A change to the fairness block of the site. The fairness line reaches the site as text.
