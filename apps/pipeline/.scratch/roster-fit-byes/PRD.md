# A bye is not a hole, except this week for a middle team

**Status:** ready-for-agent
**Date:** 2026-10-27
**Decision record:** `docs/adr/0004-a-bye-is-not-a-hole-except-this-week-for-a-middle-team.md`
**Glossary:** "Hole", "Return window", "Middle team", "Contender", "Seller", "The line" in `GLOSSARY.md`
**Supersedes:** the bye rule of `.scratch/roster-fit-depth/`, ticket 03

## Problem Statement

Brian grades a trade in week 8. Roster fit says FLEX1 is a hole because Luther Burden has his bye in
week 10. The grade steps down for a week he can plan around. A bye is something a team handles: it sets
a lineup, streams a player, or eats one week. The grade should not sway on it. On week 7 live data, 13
of the 33 holes across 12 rosters were uncovered byes, and the trade finder went from 5 win-win trades
to 0. The one bye that costs a team is the one it cannot plan around: a team in the race for the last
playoff spot trades for a player who starts for it and sits out this week.

## Solution

A bye is never a hole, with one exception. For a middle team, a player it gets who starts after the
trade and has his bye in the trade week is a new hole. No bench cover cancels it. The roster fit step
rule runs as for any new hole: one step down with no lineup gain, no step with a gain, and it blocks
the step up. A contender or a seller reads no bye hole. A player a side gives on bye counts for nothing.

The due-back rules do not change. A starter due back inside the return window, the trade week and the
next two weeks, needs a bench cover above the line. One due back after the window is a hole. One out
with no return week on file is a hole. The window loses its "bye" name and reads returns only.

The schedule adjuster keeps its byes left lean. It reads a season fact for both sides. The new roster
fit read is one Sunday cost for one team.

## User Stories

1. As a trade asker, I want a starter's bye in a later week to leave roster fit alone, so that the
   grade reads the trade and not my schedule.
2. As a trade asker, I want a starter's bye in the trade week to leave roster fit alone when my team is
   a contender, so that a safe playoff spot does not read as a hole.
3. As a trade asker on a seller, I want a player on bye this week to leave roster fit alone, so that the
   grade reads my future and not this Sunday.
4. As a trade asker on a middle team, I want roster fit to flag a player I get who starts for me and sits
   out this week, so that I see the cost of a week I need to win.
5. As a trade asker on a middle team, I want that flag to read the week and my race, so that I know why
   this bye counts when others do not.
6. As a trade asker on a middle team, I want a player I get on bye this week who sits on my bench to be
   no hole, so that a depth piece does not cost me a step.
7. As a trade asker on a middle team, I want a lineup gain to cancel the bye hole to no step, so that the
   bye reads like any other new hole.
8. As a trade asker on a middle team, I want the bye hole to block the step up for the highest-value
   player, so that the rule is the same as for any other new hole.
9. As a trade asker, I want a player I give on bye this week to count for nothing, so that the reason
   stays about the players I get.
10. As a trade asker, I want a starter due back inside the return window with no cover to stay a hole,
    so that a missing starter still reads.
11. As a trade asker, I want a starter due back after the return window to stay a hole, so that a long
    absence still reads.
12. As a trade asker, I want a starter out with no return week to stay a hole, so that an unknown
    absence still reads.
13. As a trade asker, I want the schedule adjuster to keep its byes left lean, so that the season view
    of byes is not lost.
14. As a trade asker with no schedule map on file, I want no bye hole to read and the reason to name the
    missing schedules, so that a data gap is visible.
15. As the finder, I want the bye read gone from the cover logic, so that I offer the win-win trades the
    old rule hid.
16. As a reader of the rubric prompt, I want the prompt to state the bye exception in plain words, so
    that the chapter writer reads the same rule the grader runs.
17. As a reader of the glossary, I want "Hole" and "Return window" to say the rule, so that one
    definition stands.
18. As a reader of the API, I want cached grades to refresh on deploy, so that no old bye hole lingers.
19. As Brian, I want the hand-worked week 6 trades to grade the same letters as today, so that this
    change moves no settled grade.

## Implementation Decisions

- The absence read on a starting slot keeps one kind, "due back". The "bye" kind goes away. A due-back
  absence inside the return window is covered or not, as today.
- The cover logic drops the bye checks. A cover is a bench player above the line at an allowed position
  who is not out himself. The check that a bench player's own bye blocks a cover goes away, since no bye
  reads a cover now.
- The hole read reuses the injury read's tunable for the return window, trade week plus two, and the bye
  window tunable goes away. One window, one word. Every comment, docstring, and prompt that says "bye
  window" says "return window".
- The week-N bye exception is a new read on the side, not on the slot's absence. It needs the side's
  race, which the standing read already gives as contender, seller, or middle. The read applies to the
  players the side gets that start after the trade, whose team's bye is the trade week. It runs only
  when the side's race is middle.
- A slot that holds such a player is a hole after the trade. It was not a hole before the trade, since
  the player was not on the roster, so the new-hole match counts it as new in the normal way.
- The hole sentence for the exception reads: "<slot> is a hole after the trade: <name> has his bye in
  week <N>, and a middle team needs the win." The lead and the slot name match the other hole sentences.
- The roster fit step rule does not change. A new hole with a lineup gain is no step. A new hole with the
  highest-value player and no lineup loss is no step. A new hole otherwise is one step down.
- With no schedule map, no bye reads. The reason still names the missing schedules as today.
- The schedule adjuster does not change.
- The grade cache document version moves from 9 to 10, since cached grades change.
- The rubric prompt, the glossary, and ADR 0004 are already written. The code must match their words. The
  prompt test that pins the old bye paragraph moves to the new words.
- This change reaches the API only. No weekly report rebuild.

## Testing Decisions

- The seam is the rubric grade: `grade(trade, snapshot)` and the roster fit adjuster it returns. Every
  test reads the adjuster's step and reason, never the internals of the slot or the cover read. The
  existing bye and return tests in the rubric test file are the prior art, with their helpers that drop
  a player from a roster, move a team's bye week, and set trade values.
- Tests to change: the bye tests that assert a hole for a bye in weeks N+1 and N+2 now assert no hole.
  The test that gives away the only cover for a bye now asserts no hole. The tests for a starter due back
  inside and after the window keep their assertions. The test that pins the rubric prompt moves to the
  new paragraphs and the new tunable name.
- Tests to add, each through the grade seam on the slow snapshot, which has the schedules:
  1. A middle team gets a player who starts for it and has his bye in week N. The reason names the slot,
     the player, week N, and the race. The step is -1 with no lineup gain.
  2. The same trade for a contender reads no hole.
  3. The same trade for a seller reads no hole.
  4. The same trade with the bye in week N+1 reads no hole.
  5. The same trade where the player lands on the bench reads no hole.
  6. The same trade with a lineup gain reads no step and names the hole.
  7. A middle team gives a player with his bye in week N and the reason does not name him.
  8. With no schedule map, the middle team trade reads no hole and the reason names the schedules.
- The fixture trade week is 6. Rosters 7, 8, 10, 11, and 12 are middle teams. Roster 4 is a seller. Rosters 1,
  5, and 6 are contenders. The bye helper moves a team's bye to week 6 to make the case.
- The hand-worked table must pass with its letters unchanged. If a row moves, stop and report the row to
  Brian before any further change.
- The finder timing test must stay green, under 5 seconds.
- The full suite and ruff must pass before merge.

## Out of Scope

- Any change to the lineup value of a player on bye in week N. The best lineup still fills by points per
  game over the lineup weeks.
- A "needs the win" term finer than the middle team race, such as a team within one game of the cut.
- A plus for a player a side gives who has his bye this week.
- A change to the schedule adjuster or its byes left count.
- A change to depth, strength, or the handcuff block.
- A weekly report rebuild or a site change.

## Further Notes

- Brian approved build, publish, and deploy with no confirm. Run the build check first, then deploy
  the API.
- Branch before code. The glossary, the ADRs, and the rubric prompt are already changed on main and
  uncommitted. Commit them with the code, not before, since the prompt test fails until the code lands.
- The handoff that started this work is `.handoff/cornerstone-roster-fit-byes.md`.
