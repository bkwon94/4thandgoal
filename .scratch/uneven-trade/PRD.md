# Uneven trade: a fair start for an uneven count, a superstar step, and a fairness reason that agrees

Status: ready-for-agent
Date: 2026-11-05
Apps: both. The pipeline changes the trade grade: the start letters, a new adjuster, and the fairness reason. The site changes one line of the trade form and one line of the trade finder.
Spec branch: `uneven-trade`.
Source: the map `.scratch/uneven-trade/MAP.md` and decision tickets 01 to 02. The session of 2026-11-05 and the handoff `.handoff/2026-11-05-uneven-trade-discount.md`.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

A manager grades a 3-for-2 trade. Brian's trade of week 9 is the example. Bo Girds gives Parker Washington and Kenneth Walker III to Teehee. Teehee gives Tee Higgins, Bhayshul Tuten, and Tony Pollard.

The grade has three faults:

1. The start letters count the third player at full value. Only one player for two or more gets the Consolidation margin, so a 3-for-2 trade starts both sides at C.
2. Walker is the second-best player on the chart, but the grade gives no credit to the side that gets him.
3. The fairness line reads "Lopsided: Teehee gives more", and Teehee's reason under it reads "about even". The reason shows only an up step or the deal row, so it never names the roster loss that moved Teehee down.

The form also says "This can take up to a minute on a new chart week." while the analyzer runs. The grade bans the word "chart" in what a manager reads, and the form does not follow that rule.

## Solution

1. In any uneven count of two or more players for two or more, the sum of the side with more players is divided by 1.10. One player for two or more keeps the 1.25 margin.
2. A side that gets a superstar, a player in the top 8 trade values of the week, gets one step up.
3. The fairness reason of each side names what moved its letter. When an up step and a down step cancel, the reason names both.
4. While the analyzer runs, the form and the finder read "This can take up to a minute early in the week."

With all four changes, Brian's trade reads:

```
Fairness: Fair.
  Bo Girds: You go from 3 RBs in the top 36 to 4 and keep 3 WRs in the top 36, and your lineup scores more.
  Teehee: Kenneth Walker III is a superstar, a top 8 trade value this week, but you go from 2 RBs in the top 36 to 1 and keep 4 WRs in the top 36.
```

Bo Girds starts at D, 76.8 against 91.5, and ends at C. Teehee starts at B, 91.5 against 76.8, and ends at B.

## User Stories

1. As a manager, I want a 3-for-2 trade to discount the third player, so that a pile of depth does not beat two better players on a plain sum.
2. As a manager, I want a 4-for-3 trade to use the same discount, so that every uneven count follows one rule.
3. As a manager, I want a one-for-two trade to keep the 1.25 margin, so that a great player keeps his full premium.
4. As a manager, I want an even count, such as 2-for-2, to get no discount, so that the grade does not change for a trade that has no extra player.
5. As a manager, I want the start reason to say that the extra player counts at a discount, so that I know why the letter is not even.
6. As a manager, I want the side that gets a superstar to get a step up, so that the grade gives credit for a player who wins a week alone.
7. As a manager, I want the superstar step to name the player, so that I know who earned it.
8. As a manager, I want a superstar to be a top 8 trade value over all positions, so that the rule means the same in every league format.
9. As a manager, I want two superstars to one side to give only one step, so that the step stays in line with the other adjusters.
10. As a manager, I want the side that gives a superstar to get no step down, so that the loss counts once, in the trade values.
11. As a manager, I want no superstar step in a one-for-many trade, so that the 1.25 margin and the step do not count the same star twice.
12. As a manager, I want the superstar step in a 3-for-2 trade, so that the 1.10 margin pays only for the extra roster spot and the star still counts.
13. As a manager, I want each side that gets a superstar to get the step, so that my grade depends only on what I get.
14. As a manager, I want the superstar check to read the week before when this week has no trade values, so that a star still counts early in the week.
15. As a manager, I want the superstar reason to say "last week" when it reads the week before, so that I know the source of the rank.
16. As a manager, I want my fairness reason to name my first up step when my letter went up, so that I see what I gain.
17. As a manager, I want my fairness reason to name my first down step when my letter went down, so that "lopsided" never sits next to "about even".
18. As a manager, I want my fairness reason to name my up step and my down step when they cancel, so that I see why my letter held.
19. As a manager, I want my fairness reason to show the deal row when no adjuster moved, so that the reason still says how the values compare.
20. As a manager at the top of the scale, I want my up step to show even when my letter cannot go above A, so that my gain is not hidden.
21. As a manager, I want the form to name no chart while the analyzer runs, so that the form uses the same words as the grade.
22. As a manager who uses the finder, I want the same wait text, so that both tools read alike.
23. As Brian, I want the 1.10 margin and the superstar rank as named values in the tunables, so that I can tune each in one place.
24. As Brian, I want the rubric text and the glossary to match the code, so that the Claude call and a reader use the same rules.
25. As Brian, I want the finder to stay inside its speed bound, so that the new adjuster does not slow the search past its test.

## Implementation Decisions

### The uneven-count margin

- The tunables get one new named value, `UNEVEN_MARGIN = 1.10`, beside `CONSOLIDATION_MARGIN = 1.25`.
- The start letters pick the margin from the counts of each side. One player for two or more uses `CONSOLIDATION_MARGIN`. Two or more for a larger count uses `UNEVEN_MARGIN`. An even count uses none.
- The margin divides the sum of the side with more players. Both sides use the divided sum in their ratios, as the 1.25 margin does now.
- Each side reads its own gives and gets, so in a two-side trade both sides use the same margin or neither does. A trade of three or more sides keeps the rule of each side on its own counts.
- The start reason names the margin. The deal row of a Consolidation trade keeps its present ending for both margins.
- The glossary term Consolidation covers both margins. The Spec branch already has the wider term, from decision ticket 01.

### The superstar step

- A new adjuster, Superstar, sits after Upside in rubric order: fit, standing, trend, injury, upside, superstar, handcuff, schedule, then the expected gap when it is on.
- A superstar is a player in the top `SUPERSTAR_RANK = 8` trade values of the week, over all positions. A tie at the edge makes every tied player a superstar, as the Star rank does.
- The step is +1 when the side gets one or more superstars. The step is never negative. Two superstars give one step.
- The step is 0 when the trade uses `CONSOLIDATION_MARGIN`. The reason then says that the margin already counts the superstar.
- The step reads only the players a side gets. A player out for the season gets no step, as the sums count him at zero.
- When the snapshot has no chart for the week, the check reads the newest saved chart read of the week before, within the `STAND_IN_WEEKS` weeks the chart fallback uses. The snapshot gets a field for that earlier read. The start letters do not use it, so with no chart both sides still start at C.
- Reason text with a step: "{name} is a superstar, a top 8 trade value this week." From the week before, "this week" becomes "last week". With two superstars, the reason names both.
- Reason text with no step: "No player it gets is a superstar." With the 1.25 margin: "{name} is a superstar, but the one-for-many margin already counts him."
- The reason text never uses the word "chart". The present word rule of the analyzer checks it.
- The rubric prompt gets a Superstar section. The Claude call reads it, as it reads the other adjusters.

### The fairness reason

- The reason of each side comes from the net sum of its adjuster steps, before the clamp. "First" means first in rubric order.
- A net above zero shows the first up step. A net below zero shows the first down step.
- A net of zero with steps shows the first up step, then ", but ", then the first down step. The joined reason starts with the up reason as it is. The down reason follows with its first letter in lower case, unless that word is a name.
- No steps at all shows the deal row.
- The fairness state and the side that gives more do not change.

### The wait text

- The trade form and the trade finder read "This can take up to a minute early in the week." The finder keeps its first sentence, "The search tries every small swap."

## Testing Decisions

- A good test reads the grade of a trade from the outside: the start letters, the adjusters, the final letters, and the fairness block. It does not call a private helper.
- The seam is the grade of one trade, through the rubric tests of the pipeline. The prior art is the Consolidation cases and the fairness cases of the rubric tests, which build a snapshot and grade a trade.
- The first test of each pipeline ticket is Brian's week 9 trade, at the numbers in the Solution. The fixture copies the five trade values from the week 9 chart.
- The rubric tests add these cases: a 3-for-2 and a 4-for-3 at 1.10, a one-for-two at 1.25 with no superstar step, a 2-for-2 with no margin, two superstars to one side, a superstar to each side, a tie at rank 8, and the fallback to the week before.
- The fairness tests add one case for each of the four reason rules, and the side at A with an up step.
- The finder speed test keeps its 5 second bound. CI runs about 3.5 times slower than the Mac, so the Mac run must stay well under it.
- The site seam is the existing test of the trade form. It checks the wait text. The finder gets the same check.
- The word rule of the analyzer covers the new reason text, with no new test.
- The acceptance evidence is the output of `make -C apps/pipeline analyze` for Brian's trade, and a screenshot of the form while it runs.

## Out of Scope

- A change to `CLAMP_STEPS = 1`. The chart weighs more than the adjusters, and no trade so far needs a change.
- A change to the fairness block of the site. The fairness reason reaches the site as text.
- A superstar rank that grows with the league size. `SUPERSTAR_RANK` is fixed. A later client with more teams may need its own rank.
- A down step for the side that gives a superstar.

## Further Notes

- The handoff quotes the roster text "RB2 is a hole after the trade". That text came from a run with the Claude call. The run with no Claude call gives "You go from 2 RBs in the top 36 to 1 and keep 4 WRs in the top 36."
- Upside also names stars, through the Star rank of each position. A player can earn both the upside step and the superstar step. The clamp keeps the sum to one step.
- With the superstar step, the fairness state of a trade with a superstar moves up more often. Brian's trade moves from "Lopsided" to "Fair".
