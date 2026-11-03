# Next-week storylines

**Status:** ready-for-agent
**Date:** 2026-10-27
**Glossary:** "Must Watch", "Storyline", "Streak on the line", "Shootout", "Rematch" in `GLOSSARY.md`

## Problem Statement

The next-week preview marks two games Must Watch and gives a reason. The reason reads "1st vs 5th, near the
playoff cut" every week, because the pick reads two signals only: the gap in the table and the playoff cut.
The league has more to say: a 4-game win streak on the line, the two best projected lineups in one game, a
rematch of a week 3 thriller. The data for all of it is in the build already.

## Solution

Each next-week game gets storylines from a fixed set of six, each with a weight. The game's score is the sum.
The top two games are Must Watch. The reason names the game's top two storylines in one plain sentence with
the numbers. Every game's storylines are facts the writer can cite, so the preview blurb can mention a streak
in any game. The page keeps its shape: the reason string on the two Must Watch rows, as today.

## User Stories

1. As a reader, I want the Must Watch reason to say why this game matters this week, so that it is not
   the same sentence every week.
2. As a reader, I want a streak on the line named with its length and kind, so that "4 straight wins" is
   a sentence I can check.
3. As a reader, I want a shootout named with both projected totals, so that I know why to watch the score.
4. As a reader, I want a rematch to name the earlier week and result, so that I remember the first game.
5. As a reader, I want the near-the-cut and top-of-the-table reasons kept, so that stakes still count.
6. As the writer, I want one fact per storyline per game, so that the blurb can cite any of them.
7. As the writer, I want the preview blurb to mention a storyline on a non-Must-Watch game when it is the
   best one, so that a 5-game streak never goes unsaid.
8. As a reader, I want the two Must Watch games chosen by the sum of storyline weights, so that the pick
   is explainable.
9. As a reader, I want ties broken by the smaller gap in the standings, then the schedule order.
10. As the commissioner, I want the six weights in the tunables, so that a change is one edit.
11. As a reader, I want the page unchanged in shape, so that nothing on the site breaks.

## Implementation Decisions

- **The storyline set and weights**, as tunables: near the cut 3, streak on the line 3, shootout 2, top of the
  table 2, rematch 1, revenge 1. Revenge applies only with rematch, to the loser of the earlier game.
- **Streak on the line**: head-to-head games only, from the saved weeks, newest back, 3 or more in a row, win
  or loss. A team with a streak gives the game one storyline per team with a streak; each names the team,
  the length, and the kind.
- **Shootout**: each roster's best projected lineup for next week by `pick_lineup` on the week N+1
  projections, as the odds inputs do. Both teams in the top four of twelve. The fact names both totals,
  rounded to one decimal.
- **Rematch**: the earliest week this season in which the two met, with the winner and the margin. Revenge
  names the loser of that game.
- **Near the cut**: either team within one game of the cut, as `_stakes_signal` reads today.
- **Top of the table**: both teams ranked 1 to 4 in the standings.
- **The pick**: score = sum of the weights of the game's storylines; top two are Must Watch; ties by the
  smaller gap in the standings, then schedule order. The table-gap signal and `WEIGHTS["table"]` for the
  preview go away; the matchup-of-the-week pick for this week's games keeps its own signals and weights.
- **The reason**: the game's top two storylines by weight, in one sentence of 25 words or fewer, in the
  glossary's words, with the numbers. One storyline gives one clause. Example: "Return of T Mac puts a
  4-game win streak on the line, and both sit near the cut."
- **Facts**: one fact per storyline per game, id `NX.<a>v<b>.<kind>` with kinds `streak`, `shootout`,
  `rematch`, `revenge`, `cut`, `table`; numbers through `Nums`. The next-week chapter's facts include all of
  them; the swing facts stay as they are.
- **The writer prompt**: the next-week rule gains one line: name the Must Watch reasons, and mention the
  best storyline of any other game when it is a streak of 4 or more or a shootout.
- **The page**: `next` rows keep `a`, `b`, `must_watch`, `reason`. No site change.
- **Prose rules**: "Must Watch", "storyline", "streak on the line", "shootout", "rematch" per the glossary.
  No "angle", "narrative", "hook".

## Testing Decisions

- A good test gives a saved week and a standings table and checks the storylines, the pick, the reason,
  or the facts. It never reads a private helper.
- **The facts seam**: `next_week` and the next-week facts on the week 6 fixture and on hand-made weeks: a
  3-game streak gives the streak storyline and a 2-game streak does not; a shootout when both are top four
  and not when one is fifth; a rematch names the week and the result and the loser gets revenge; near the
  cut and top of the table as today; the top two by score are Must Watch; the tie rule; the reason names the
  top two storylines in one sentence; every storyline has a fact with its numbers. Prior art: the
  next-week tests in the facts tests and the swing fact tests.
- **The real-data check**: the saved week 7 of 2026 gives its two Must Watch games and their reasons; the
  report names them. The writer's next-week chapter rebuilds and verifies clean.

## Out of Scope

- A change to this week's matchup of the week pick or its labels.
- A site change. The reason string carries the words.
- Storylines that need a new source: injuries, weather, Vegas lines.
- The median race and the points-for race, as later storylines.

## Further Notes

- The week 7 raw has `matchups_next` and the week N+1 projections, so the shootout reads with no fetch.
- The saved history holds every past matchup, so rematch reads with no fetch.
