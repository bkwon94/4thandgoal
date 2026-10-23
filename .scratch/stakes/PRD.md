# Playoff odds and the swing line

**Status:** ready-for-agent
**Date:** 2026-10-23

## Problem Statement

The report says where a team stands, but not where it is headed. A standing fact reads "7th with a
6-6 record, 1 spot outside the playoff spots". A manager wants to know what that record is worth:
a coin flip, a lock, or a lost cause. The next-week chapter names the Must Watch games, but it
cannot say what the game is worth to either side. So the stakes stay in the reader's head, and the
writer has no fact to cite when it wants to say "this one matters".

## Solution

An odds engine plays the rest of the season many times and counts how often each team makes the
playoffs, gets a bye, and lands on each seed. The odds become facts. The standings chapter cites
them for the teams where they matter. The next-week chapter cites a swing line per Must Watch
game: the odds after a win and after a loss. The rankings page gets a `Playoff %` column. A plain
check marks a team as clinched or out, so those two words are always true.

## User Stories

1. As a manager, I want my playoff odds in the standings chapter, so that I know what my record is worth.
2. As a manager, I want the odds as a whole percent, so that I read one number and move on.
3. As a manager, I want "clinched" the week it happens, so that I can relax.
4. As a manager, I want "out" the week it happens, so that I know to sell.
5. As a manager, I want a clinch or an out only when the math is certain, so that the word is never wrong.
6. As a manager, I want my bye odds beside my playoff odds, so that I know if the 2 seed is in reach.
7. As a manager, I want my most likely seed, so that I can guess my first-round opponent.
8. As a manager, I want the seed only when I am likely in, so that a seed for a long shot does not mislead me.
9. As a manager, I want the swing line on the Must Watch games, so that I know what the game is worth.
10. As a manager, I want the swing as "a win puts X at 71%, a loss at 38%", so that both outcomes are plain.
11. As a manager, I want a `Playoff %` column on the rankings page, so that I see every team at a glance.
12. As a manager, I want the column after the record, so that the odds sit beside the wins that drive them.
13. As a manager, I want the column on my phone, so that the glance works where I read the page.
14. As a manager, I want past weeks to open without an odds column, so that the page never looks broken.
15. As a manager, I want the odds to count the median game, so that they match how the league plays.
16. As a manager, I want the odds to use the real remaining schedule, so that a soft or hard run shows.
17. As a manager, I want the odds to lean on recent weeks, so that a team on a run gets credit.
18. As a manager, I want the odds built from scores this season, so that last year's roster does not count.
19. As a manager, I want the same odds on the page and in the report, so that the two never disagree.
20. As a reader, I want the writer to cite odds only when they change the story, so that the chapter is not a list of 12 percents.
21. As a reader, I want "about" before an odds number, so that the voice admits it is an estimate.
22. As a reader, I want no odds number below 1 or above 99 unless clinched or out, so that the number is honest.
23. As a reader, I want the swing line beside the record line, so that the preview still reads as one thought.
24. As a commissioner, I want the odds to rebuild to the same numbers for the same week, so that a rebuild never changes the page.
25. As a commissioner, I want the odds to need no new Claude call, so that the build cost holds.
26. As a commissioner, I want the odds to run in seconds, so that the Tuesday build stays short.
27. As a commissioner, I want the remaining schedule saved with the week's raw data, so that a build replays from the cache.
28. As a commissioner, I want the seed order to match Sleeper, so that the sim and the bracket agree.
29. As a commissioner, I want the odds to stop at week 14, so that playoff weeks keep the final answer.
30. As a developer, I want the run count, the recency weights, and the seed threshold as tunables, so that one place holds them.
31. As a developer, I want the odds behind one function, so that a test feeds a small league and reads the result.
32. As a developer, I want the odds facts to pass the verifier as any fact does, so that no new check is needed.
33. As a developer, I want the site to read the odds as an optional field, so that the site ships first and old files still load.
34. As a developer, I want a rewrite to reuse the saved odds, so that a rewrite never reruns the sim.

## Implementation Decisions

### The engine

- A new module holds the odds engine. In: the past weeks of this season, the remaining pairings
  for weeks N+1 to 14, the week, and the playoff settings. Out: per team the playoff odds, the bye
  odds, the most likely seed, and the status; per remaining matchup of week N+1 the odds after a
  head-to-head win and after a loss. It calls no network and no Claude.
- Monte Carlo. One run plays every remaining week once and sorts the final standings. The odds are
  the share of runs. The run count is the tunable `SIM_RUNS`, 5,000. The random seed derives from
  the season and the week, so the same inputs give the same odds.
- Score draw: each simulated week draws one of the team's own weekly scores this season, with
  the last `RECENT_WEEKS` (3) weeks weighted `RECENT_WEIGHT` (1.25) times. No fit, no league pool.
- Projection shift: the drawn score then moves toward that week's projection. The shift is
  `PROJECTION_WEIGHT` (0.7) times the gap between the team's projected best-lineup total for that
  week and the team's season average score. At 0 the draw is the plain past score. At 1 the draw
  centers on the projection with the team's own spread. The projected total is the sum of the
  Sleeper half-PPR projections over the best lineup of the current roster for that week, with the
  existing best-lineup helper; a player with no projection that week counts 0, which covers byes
  and injuries. Brian chose this on 2026-10-23 so the sim knows the roster for each week ahead.
- Each simulated week plays both games. The head-to-head game settles by the pair. The median game
  settles each team against the median of the 12 drawn scores, with the existing median rule: the
  mean of the 6th and 7th scores, an exact tie is neither a win nor a loss.
- Seed order at the end of a run: wins, then points for, then roster id. The top `PLAYOFF_SPOTS`
  are in. The top 2 get a bye. Points for in a run is the real points for plus the drawn scores.
- Most likely seed: the seed a team takes most often across the runs where it makes it. It shows
  only when the playoff odds are at or above `SEED_SHOW_AT` (50).
- Status: `in`, `out`, or `open`. A plain check decides, not the sim. A team is `in` when no team
  outside the top 6 can reach its win total with 2 wins in every remaining week. A team is `out`
  when it cannot reach the 6th team's win total with 2 wins in every remaining week. Both are
  sufficient conditions, so the word is always true. Odds show as 100 for `in` and 0 for `out`.
  Every other team's odds clamp to 1 to 99 after the round to a whole percent.
- The swing: the runs split by the result of the head-to-head game of week N+1, and each half
  gives its own playoff odds for both teams. The median game does not split the runs.
- At week 14 no weeks remain. The engine skips the runs, the check sets every team `in` or `out`,
  and the bye and seed come from the final standings. Weeks after 14 keep the week 14 result.

### The schedule

- The week fetch gains the pairings for weeks N+2 to 14, one call per week, saved as one raw file
  `schedule.json` beside the other raw files. The engine reads only `matchup_id` and `roster_id`
  from it. A past week never needs it.
- The week N+1 pairings come from the existing next-week fetch.
- The week fetch also gains the per-player projections for weeks N+1 to 14, one call per week,
  saved as one raw file `projections_ahead.json`, filtered to the players on any roster so the
  file stays small. The engine reads the projected totals from it. A past week never needs it.

### Facts and chapters

- A new fact family `ODDS.{roster_id}`, one per team. Text for `open`: "{team} makes the playoffs
  in about {p}% of runs, with a bye in {b}%, most often as the {s} seed." The seed clause drops
  below `SEED_SHOW_AT`. Text for `in`: "{team} has clinched a playoff spot." Text for `out`:
  "{team} is out of the playoff race." Every digit in the text is in the fact's numbers.
- A new fact family `SW.{a}v{b}`, one per Must Watch game of week N+1, in the same pair order as
  the `NX.` fact. Text: "A win puts {team a} at {w}%, a loss at {l}%. A win puts {team b} at
  {w}%, a loss at {l}%." Two sentences, one per side.
- The standings chapter cites `ODDS.`. Its prompt gains one rule: cite the odds for a team only
  when they change what the reader should feel, such as a clinch, an out, or a team near 50%; do
  not list odds for all 12.
- The next-week chapter cites `SW.`. Its sentence cap rises from 2 to 3. Its prompt gains one rule:
  state the swing for the Must Watch games, with the fact's numbers as given.
- The rankings chapter may cite `ODDS.` as it does `S.`.
- The engine runs in the facts step of the build, once per week, from week 7 on. The odds land in
  the saved facts and in the rankings file in that step. A rewrite reads the saved facts and never
  reruns the engine.

### The rankings file and the site

- Each row of the rankings file gains an optional `odds` object: `playoff` and `bye` as whole
  numbers, `seed` as a number or null, `status` as `in`, `out`, or `open`. The schema version stays
  1. Rows for weeks before the engine ran have no `odds` key.
- The site types mirror the optional object. The loader accepts a row with or without it.
- The power rankings table gains a `Playoff %` column after `W-L`, in the header and in each row,
  at every width. The cell shows the playoff number for `open`, "In" for `in`, "Out" for `out`,
  and stays blank when the row has no `odds`. The open row of a team may show the bye and seed line
  beside the component cells.
- Glossary entries: **Playoff odds**, **Swing**, **Clinched**, **Out**, with the page words.

## Testing Decisions

- A good test feeds inputs at a seam and asserts the output. It never asserts how a helper draws a
  score or sorts a run.
- Engine seam: a fixture league of 4 teams, 2 weeks played, a 2-week remaining schedule, 2 playoff
  spots, 200 runs, a fixed seed. Cases: the same seed gives the same odds twice; a different seed
  gives odds within a few points; a team with a 4-win lead and 1 week left is `in`; a team 5 wins
  back with 2 weeks left is `out`; a team that wins every drawn game lands at the 1 seed; the odds
  change when the median game flips a week, so both games count; the swing halves differ when the
  game matters; the odds of every team sum to the number of spots times 100 within rounding. No
  test pins an odds value from the real week 6 data. Prior art: the power rankings tests on the
  week 6 fixture and the rubric tests on fixture breakdowns.
- Fact sheet seam: the bundle on the week 6 fixture holds one `ODDS.` fact per team and one `SW.`
  fact per Must Watch game, and the existing checks hold: every number is in its text, every
  chapter fact id exists. The `in` and `out` texts hold no digit. Prior art: the standings cut
  phrase tests.
- Fetch seam: the week fetch saves `schedule.json` with the pairings for weeks N+2 to 14 from a
  fake client. Prior art: the Sleeper fetch tests.
- Rankings file seam: the current week's rows carry `odds` and past rows do not. Prior art: the
  rankings file tests with the fixture history.
- Site: the loader test accepts a row with and without `odds`. The component test renders the
  number, "In", "Out", and the blank cell. The rankings fixture gains `odds` on the current week
  only. Prior art: the rankings data and power rankings component tests.
- One prompt text test pins each new prompt rule.

## Out of Scope

- The rivalry line: head-to-head record and all-time margin. Brian skipped it on 2026-10-23.
- The waiver chapter. Its own spec after this one.
- A fit or a league-pool noise model for the score draw. The tunables leave room for a later change.
- Odds for weeks before the engine first ran. Old rows stay without the field.
- Odds in the matchup recap or the awards chapter.
- A playoff bracket sim for weeks 15 to 17. The engine stops at the seeds.

## Further Notes

- Research with sources is in `research.md` beside this file. The live Sleeper check on
  2026-10-23 showed the matchups endpoint returns pairings for any week, with points at zero.
- The schedule is an 11-week round robin and weeks 12 to 14 repeat weeks 1 to 3. The engine must
  not assume that; it reads the fetched pairings.
- Six weekly scores per team at week 7 is a thin draw. The odds firm up by 12 scores a week. The
  "about" word and the 1 to 99 clamp are the guard.
- The sum-of-odds test holds because exactly 6 teams make it in every run.
- The week 7 build on 2026-10-27 may land before this ships. That is fine; the field is optional.
