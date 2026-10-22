# Win-win trades

**Status:** ready-for-agent
**Date:** 2026-10-22

## Problem Statement

The analyzer serves the side that asked. It grades both sides, but the decision, the reason, and the
suggested counters all answer one question: is this trade good for me? A manager who wants a trade
that the other side will take has no signal for that. A trade that grades A for the asker and F for
the other side reads as a win on the page, and then dies in the group chat. Managers want trades
that go through, and a trade goes through when both sides win.

## Solution

Two phases. Phase 1 adds a fairness line to the result page under the decision. It names the trade
as good for both, fair, or lopsided, with one reason per side. Phase 2 adds a finder: a manager picks
a partner team, the code grades every small swap between the two rosters, and the page shows the top
three trades that are good for both, with one reason each.

A trade is a win-win when both sides' final letters are B or better. Trade value is zero-sum on the
chart, so a win-win comes from the adjusters: roster fit, standing, trend, injury, and schedule. The
adjusters clamp to one step either way, so a win-win needs a chart start near even and a step up on
each side, or an A start on one side with the other side at C that gains a step. The flag fires
rarely and means something when it does.

## User Stories

1. As a manager, I want a fairness line on the result, so that I know if the other side will take it.
2. As a manager, I want "good for both" when both sides grade B or better, so that I send that trade.
3. As a manager, I want "lopsided" when either side grades D or worse, so that I do not send it.
4. As a manager, I want "fair" for the rest, so that a C and C trade reads as neither a win nor a loss.
5. As a manager, I want the lopsided line to name the side that gives more, so that I know who loses.
6. As a manager, I want one reason per side under the fairness line, so that I see what each side gains.
7. As a manager, I want the reason to come from the factors already shown, so that it matches the breakdown.
8. As a manager, I want my decision to stay the lead of the page, so that my own answer comes first.
9. As a manager, I want the fairness line on a cached result too, so that an old result reads the same.
10. As a manager, I want the fairness line with no new wait, so that the result is as fast as today.
11. As a manager, I want the fairness line to use plain words, so that I never see a letter grade.
12. As a manager, I want to pick a partner team, so that the finder looks at one roster I can trade with.
13. As a manager, I want the finder to try every one-for-one swap, so that no simple trade is missed.
14. As a manager, I want the finder to try every two-for-one swap both ways, so that depth trades count.
15. As a manager, I want only trades that are good for both, so that each one has a real chance.
16. As a manager, I want the top three, so that I read a short list and not every swap.
17. As a manager, I want the three ranked by what both sides gain, so that the best one is first.
18. As a manager, I want one reason per finder trade, so that I can paste it into the group chat.
19. As a manager, I want each finder trade to link to its full result, so that I see the breakdown.
20. As a manager, I want the finder to say when no swap is good for both, so that I stop looking there.
21. As a manager, I want the finder to use the same rubric as the analyzer, so that the two never disagree.
22. As a manager, I want the finder to skip a handcuff and an injured player, so that the list is real.
23. As a commissioner, I want the finder to count as one grade against the daily limit, so that the bill holds.
24. As a commissioner, I want the finder to make one Claude call at most, so that the cost is one result.
25. As a commissioner, I want the finder to cache per pair and per week, so that a repeat is free.
26. As a commissioner, I want the as-of line on the finder page, so that managers know the data week.
27. As a developer, I want the fairness rule in the rubric file, so that the prompt and the code agree.
28. As a developer, I want the fairness numbers in the tunable table, so that one place holds them.
29. As a developer, I want the fixture document shared with the site to carry the new block, so that the site tests render it.

## Implementation Decisions

### Phase 1: the fairness line

- Fairness is a code rule beside the verdict rule, in the rubric module. It reads the two final
  letters and the adjusters of each breakdown. It never calls Claude.
- Three states: `win_win` when both final letters are at or above `WIN_WIN_AT_OR_ABOVE`, which is
  B; `lopsided` when either final letter is at or below `LOPSIDED_AT_OR_BELOW`, which is D; `fair`
  for the rest. Both bounds live in the tunable table. The rubric file names them and never repeats
  their values.
- A reason per side. The reason is the one-line reason of the first adjuster with a step up on that
  side, in rubric order. A side with no step up gets the reason of the start letter. The lopsided
  state names the side that gives more: the side with the lower final letter. At equal letters the
  side with the lower start letter gives more.
- The fairness text holds no letter, no trade value, no sum, no ratio, and no chart name. The
  existing prose rules on the breakdown cover it, since it reuses breakdown reasons.
- The response document gains a `fairness` block: the state, and per side the roster id and the
  reason. The block is computed at response time from the sides in the document, so a cached
  document gets it too. The result cache key does not change.
- The page shows the fairness line under the decision block and above the swap card. Page words:
  "Good for both", "Fair", "Lopsided". The lopsided line reads "Lopsided: <team> gives more." The
  two reasons sit under the line, one per side, with the asker's side first.
- The Claude analysis prompt does not change in phase 1. The verdict rule does not change.
- Glossary entries: **Fairness** for the code term and the three states; **Good for both** as the
  page word for `win_win`. Use "fairness" in code and on the page as the block title.

### Phase 2: the finder

- A finder function in a new module: the asker's roster, the partner's roster, and the snapshot in;
  a ranked list of win-win trades out. It calls the grade function for every candidate and keeps the
  trades with the `win_win` state. The highest existing seam is the grade function, and the finder
  sits one level above it.
- Candidates: every one-for-one swap, and every two-for-one swap in both directions. No three-player
  sides. A handcuff on either roster is never a candidate. A player who is out now with no return
  week on file is never a candidate. A kicker and a defense are never candidates.
- Rank: the sum of the adjuster steps up on both sides, highest first. Ties break by the higher of
  the two lower final letters, then by the smaller gap between the two sides' final letters, then by
  the asker's letter. The list holds three at most.
- The finder is a new route with the same passphrase, the same minute and day limits, and a cache
  keyed by the pair of rosters and the chart week. A finder call counts as one grade. One Claude
  call writes the three reasons in one response, with the same prose checks as the analysis. When
  the call fails twice, the three trades stand with the code's fairness reasons.
- The finder document: the two teams, the as-of stamps, and the list. Each item holds the two sides
  with player ids and names, the fairness block, and the reason. An empty list carries one line:
  no swap between these rosters is good for both.
- The page: a partner picker on the analyze page, a "Find a trade" action, and a result list of
  three cards. Each card links to the full result for that trade, which reuses the analyze route.
- The counters ticket stays parked. The finder replaces the need for counters that lift one side.

## Testing Decisions

- A good test feeds inputs at a seam and asserts the output. It never asserts how a helper is
  built.
- Phase 1 seam: the fairness rule. Fixture breakdowns in, a state and two reasons out. Cases: both B,
  one A and one B, both C, one C and one D, one A and one F, equal letters with different starts, a
  side with no step up. Prior art: the verdict rule tests with fixture breakdowns.
- Phase 1 document: the fixture response document gains the block and stays byte-identical with the
  site's copy. The site's result component test renders the three states. Prior art: the fixture
  shape test and the analyze-result component tests.
- Phase 1 cache: a cached document without the block gets it at response time. Prior art: the
  result cache tests.
- Phase 2 seam: the finder function. Two fixture rosters and the week 6 snapshot in, a ranked list
  out. Cases: a pair with three or more win-wins returns three; a pair with one returns one; a pair
  with none returns the empty list; a handcuff never appears; a two-for-one appears in both
  directions; the rank order holds on a tie. Prior art: the grade tests on the six real week 6
  trades.
- Phase 2 route: the limit counts one grade, the cache hit is free, and the Claude failure falls
  back to the code reasons. Prior art: the grade limits tests and the analysis fallback tests.
- Prompt text tests do not apply in phase 1. In phase 2, one test pins the finder prompt lines.

## Out of Scope

- Suggested counters, ticket 15 in the site API tracker. Parked.
- The finder across all eleven partners. A later toggle once the one-partner result quality is known.
- Three-for-one and larger trades in the finder.
- Draft picks in the finder.
- Any change to the verdict rule, the letter bands, or the adjusters.
- A Claude call in phase 1.

## Further Notes

- Decided on 2026-10-22: win-win means both sides at B or better; three states, not two; the
  decision stays the lead; code writes the phase 1 reasons.
- With the clamp at one step, both at B from a C and C start needs a step up on each side. The
  adjusters that can give it are roster fit, standing, trend, and injury. Schedule never moves a
  letter, so it never makes a win-win.
- The finder grades about 225 one-for-one swaps and a few thousand two-for-ones per pair, all in
  code. Measure the time on the week 6 snapshot before the route ships. If it passes a few seconds,
  cap the candidate pool at the top players by points per game on each roster.
