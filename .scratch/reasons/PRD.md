# Rankings reasons

**Status:** ready-for-agent
**Date:** 2026-10-23

## Problem Statement

The rankings blurb says where a team is and how far it moved. It cannot say why. The writer gets
the power rank, the movement, the four component ranks, the standing, the streak, the trend, and
the odds line. None of those is a cause. "Up 3 places" with no game behind it reads as noise, and a
4-8 team at 37% playoff odds reads as a bug when the reader cannot see the projections behind it.

## Solution

Two "why" facts per team. The rank why names the component that moved most since last week and the
game behind it. The odds why names the two inputs that drive the odds: the projected average for the
weeks left against the season average, and the remaining schedule. The rankings writer cites the
rank why for every real mover and the odds why when the odds and the record disagree.

## User Stories

1. As a reader, I want to know why a team moved in the power rankings, so that the move means something.
2. As a reader, I want the game behind a move, with the opponent and the margin, so that I remember it.
3. As a reader, I want the component that moved named, so that I learn how the rankings work.
4. As a reader, I want a held rank explained when a team stays put, so that a 7th place is not a shrug.
5. As a reader, I want to know why a 4-8 team sits at 37%, so that the odds read as reasoned and not random.
6. As a reader, I want the projected pace against the season pace in plain points, so that I see the gap.
7. As a reader, I want the remaining schedule ranked easy to hard, so that I know who has the soft run.
8. As a reader, I want the why only when a number asks for it, so that the blurb stays short.
9. As a manager, I want the why in my team's open row on the rankings page, so that I see it where I look.
10. As a commissioner, I want no new Claude call, so that the build cost holds.
11. As a developer, I want the thresholds as tunables, so that one place holds them.
12. As a developer, I want the why facts to pass the verifier as any fact does, so that no new check is needed.

## Implementation Decisions

### The rank why

- One fact per team, `PR.{roster_id}.why`. It needs last week's power rows, which the power rankings
  helper gives for week N-1 from the same history, and last week's head-to-head game from the history
  pairs and scores, plus the opponent's standing rank before this week.
- The moved component is the one whose rank changed most between week N-1 and week N, ties to the
  first in component order. The margin is this team's score minus the opponent's, last week.
- Text for a mover: "{team} moved up 3 places after a 61-point win over {opponent}, the 1st-place
  team: form rose from 9th to 3rd." A loss reads "after a 14-point loss to". A tie in the
  head-to-head game reads "after a tie with".
- Text for no move: "{team} held 7th: scoring sits 4th, schedule played 11th." It names the best and
  the worst component.
- Week 1 of the rankings has no last week, so no fact.
- Every digit goes through the number recorder, so the verifier sees every number.

### The odds why

- One fact per team, `ODDS.{roster_id}.why`, built beside the odds facts from the same inputs the
  engine takes: the projected best-lineup totals for the weeks left, the season scores, and the
  remaining pairs.
- The projected pace is the mean of the projected totals over the weeks left. The season pace is the
  mean of the played-week scores. Both round to whole points.
- The remaining schedule is the mean season pace of the opponents left, ranked 1 to 12 with 1 the
  easiest, ties by roster id.
- Text: "{team} projects 112 a week from here against a 101 pace, with the 3rd easiest remaining
  schedule." A team with no projections gets no fact.
- The fact exists only when the odds facts exist, under the same gate and guard.

### The writer

- The rankings chapter lists both why families. Its prompt gains one rule. Cite the rank why for
  every team that moved `WHY_MOVE_AT` (2) or more places either way. Cite the odds why for a team
  under .500 with playoff odds at or above `WHY_ODDS_AT` (25), and for a team over .500 with odds
  under it. The writer may cite either why for any other team when it helps.
- The per-team cap in the rankings rule rises from 2 sentences to 3. The chapter range rises to
  match: 12 to 36.
- Glossary entries: **Rank why**, **Odds why**, **Projected pace**, **Season pace**.
- The site needs no change. The rankings blurb row shows each team's sentences by roster tag.

## Testing Decisions

- A good test feeds inputs at a seam and asserts the output. It never asserts how a helper is built.
- Rank why seam: the week 6 fixture bundle. Cases: a mover names its game and its margin; a held team
  names its best and worst component; the opponent's place is the standing rank before this week; a
  team that tied last week reads "a tie with". Prior art: the power rankings fact tests.
- Odds why seam: the week 6 fixture bundle. Cases: the pace numbers match the mean of the inputs; the
  schedule rank is 1 for the easiest; a team with no projections has no fact; no odds means no why.
  Prior art: the odds facts tests.
- The existing bundle checks cover the number recorder and the fact id lists.
- One prompt text test pins the new rule and the raised cap.

## Out of Scope

- A why for the median or the recap chapters.
- A why line in the site table outside the blurb row.
- A per-component history chart.

## Further Notes

- Brian asked for this on 2026-10-23 after he saw a 4-8 team at 37% with no reason on the page.
- The projections ahead are as of the build. The pace from them changes a little from one fetch to
  the next, as the odds do.
