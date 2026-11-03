# Power rankings: a weekly rank per team, with movement and a blurb

Status: ready-for-agent
Date: 2026-10-22
Spans: this repo (the compute, the facts, the chapter, the season file, the publish copy) and the site
repo `cpcfantasyfootball` (the reader, the route, the home row). The site ticket folder is
`.scratch/rankings/site/issues/` in the site repo.
Depends on: `.scratch/tone/PRD.md`. The rankings blurb writes under the new voice.
Ships before: the week 7 build on Tuesday 2026-10-27 08:00, so week 7 lands with a rank.

## Problem Statement

The standings table sorts by record, then points for. A league member reads 7-5 and learns little:
a 7-5 team that beat three of the top four is not the 7-5 team with the softest schedule in the
league. The page has no view of who is good right now. Streaks, schedule played, and scoring sit
in the facts and in the writer's blurbs, but no one ranks the teams by them, and nothing on the
site shows movement week to week.

Brian wants power rankings: the thing every league argues about on Tuesday. The rank must be
explainable, so no reader can call it a vibe. It must never use or show a trade value.

## Solution

A power rank per team per week, from a formula with four equal components, each shown as a rank
of 1 to 12 next to the team:

1. Standing: the place by record and points for, the same order as the standings table.
2. Form: the last 3 weeks. The streak with the median game, the record with the median game, and
   the all-play rate over those weeks.
3. Schedule played: the record of past opponents, and wins against the teams now in the top 4.
4. Scoring: the points-for share, the all-play rate, and the mean head-to-head margin, over the season.

The pipeline computes every week from 1 to the current week on each build, from the saved
history, and writes one season file. The site gets a route, `/rankings`, with one table of twelve
rows: rank, movement since last week, team, record, the four component ranks, and an expandable
blurb. The home page gets one row below the Tools chapter: the top three and the biggest mover,
with a link to the page. One writer call per week writes all twelve blurbs in the group chat
voice, and the verifier checks them like any chapter.

## User Stories

1. As a league member, I want a power rank for every team, so that I know who is good right now and not just who has the record.
2. As a league member, I want the movement since last week next to each rank, so that I see who rose and who fell.
3. As a league member, I want the four component ranks next to each team, so that I can argue with the formula and not with a vibe.
4. As a league member, I want the record next to the team, so that I see the gap between the record and the power rank.
5. As a league member, I want a short blurb per team, so that the rank comes with a reason and a joke.
6. As a league member, I want the blurb collapsed by default, so that the table fits on my phone.
7. As a league member, I want the blurb to open with one tap, so that I read the reason without a new page.
8. As a league member, I want the top three and the biggest mover on the home page, so that I see the headline without a click.
9. As a league member, I want a link from the home row to the full page, so that one tap gets me the table.
10. As a league member, I want the rankings page to work on a phone at 390 wide with no sideways scroll, so that I read it in the chat.
11. As a league member, I want the component ranks to fold into the expanded row on a phone, so that the table stays readable.
12. As a league member, I want the team avatar and the team name on each row, so that the row reads like the standings.
13. As a league member, I want the schedule component to reward wins against top teams, so that a 7-5 team with hard wins can rank above a 9-3 team with soft ones.
14. As a league member, I want the form component to reward a streak, so that a team on 3 wins in a row climbs.
15. As a league member, I want the scoring component to count the all-play record, so that a team that outscores most of the league ranks well even with a bad head-to-head record.
16. As a league member, I want the median game to count in the standing and in the form streak, the way Sleeper counts it, so that a median win extends a streak. The streak fact on the page stays head to head only.
17. As a league member, I want no trade value on the page in any form, so that the chart stays off the site.
18. As a league member with motion off, I want the blurb to open with no animation, so that the page respects my setting.
19. As Brian, I want the rank to come from a formula with equal weights, so that I can explain it in one line in the chat.
20. As Brian, I want the weights in one place, so that I can tune them after week 8.
21. As Brian, I want every past week ranked on the first build, so that week 6 shows movement on day one.
22. As Brian, I want one season file that holds every week, so that a rank trend is a site-only change later.
23. As Brian, I want the build to recompute every week from history, so that a formula change reaches every week on the next build.
24. As Brian, I want a `rankings` command that writes the season file for a saved week without a full build, so that I can rebuild week 6 without twelve writer calls.
25. As Brian, I want the publish command to copy the season file to the site, so that one publish ships the page and the rank.
26. As Brian, I want the build to log a warning and skip the rank when the history is not complete, so that a missing past week never blocks the page.
27. As Brian, I want one writer call for all twelve blurbs, so that the Tuesday build grows by one call and one verifier pass.
28. As Brian, I want the rankings blurb to run under the tone prompts, so that it reads like the rest of the page.
29. As Brian, I want the glossary to define power rank, power score, the four components, all-play record, quality win, and movement, so that the words mean one thing.
30. As the writer, I want one fact per team with its rank, its movement, and its four component ranks, so that every sentence has a fact to cite.
31. As the writer, I want each team's standing, streak, and trend facts in the chapter, so that the blurb has more than the rank to work with.
32. As the writer, I want to tag each sentence with its roster, so that the page shows the right sentences under the right team.
33. As the verifier, I want the code check to reject a rankings sentence with no roster tag, so that no sentence lands under the wrong team.
34. As the verifier, I want the code check to reject a rankings blurb that gives a team no sentence or more than 2, so that every team gets a blurb and no team gets an essay.
35. As the verifier, I want the first sentence of each team to cite that team's rank fact, so that the rank in the blurb is the rank in the table.
36. As the site build, I want a reader for the season file with its own schema version, so that a mismatch fails the build loud.
37. As the site build, I want the home row hidden and the route to show a short empty state when the file is missing, so that a season with no rank still builds.
38. As a maintainer, I want the formula tested as a pure function over a fixture history, so that a weight change shows its effect in one test.
39. As a maintainer, I want the site components tested with a fixture file, so that the table and the home row render with no network.

## Implementation Decisions

### The formula

- Every week from 1 to the current week is computed as of that week, from the saved history. The
  history must be complete. If it is not, the build logs a warning and skips the rank.
- Each component is a number from 0 to 1 for each team. Each also gets a rank from 1 to 12, best
  first, ties broken by the standing rank. The page shows the component ranks, never the decimals.
- Standing: the place in the standings of that week, by record then points for, with the median
  game counted. Scaled so first is 1 and twelfth is 0.
- Form: the last 3 weeks, or every week when fewer than 3 exist. Three equal parts over those weeks:
  1. The form streak: wins or losses in a row, newest week back, counted over both games each week,
     the head-to-head and the median, the way Sleeper counts it. The median game is the newer game
     of its week. A loss or a tie breaks a win streak. Scaled from -6 to 6 onto 0 to 1, with 0 at 0.5.
  2. The record over those weeks, both games per week, wins over decided games.
  3. The all-play win rate over those weeks.
  The streak fact on the page stays head to head only. The form streak is its own number.
- Schedule played: half the mean head-to-head win rate of every past opponent, as of that week,
  with the median game not counted. Half the quality win rate: wins against teams in the top 4 of
  the standings of that week, over games against those teams. No such game gives a neutral 0.5.
- Scoring: three equal parts over the season. The points-for share, scaled so the top team is 1
  and the bottom is 0. The all-play win rate. An all-play week scores one win per team outscored and
  one loss per team that outscored this team, 11 games a week, a tie as neither. The mean
  head-to-head margin per game, points for minus points against, scaled so the best is 1 and the
  worst is 0.
- Power score: the mean of the four components. Power rank: by power score, best first, tie by the
  standing rank. Movement: last week's power rank minus this week's. Week 1 has no movement.
- The four weights live in one tunable, equal at 0.25 each. The page never shows the score.
- No trade value, no chart read, and no value sum enters the formula or the file.

### The facts and the chapter

- One new fact per team, with the ID prefix `PR.` and the roster ID: the power rank, the movement,
  and the four component ranks, as ordinals. The numbers list holds them all.
- The chapter `rankings` is scope all 12 teams, so the one-name rule of the two-team chapters does
  not apply. Its facts: the twelve `PR.` facts, each team's standing fact, each team's streak fact,
  and each team's trend fact. The sentence range is 12 to 24.
- Each sentence in the rankings chapter carries a roster ID. The sentence model gains an optional
  roster field that other chapters leave empty. The writer rule for this chapter: tag every sentence,
  give every team 1 or 2 sentences, cite the team's `PR.` fact in its first sentence, and order the
  teams from rank 1 to 12.
- The code check enforces the tags for the rankings chapter: a missing tag fails, a team with no
  sentence fails, a team with 3 or more fails, and a first sentence that does not cite the team's
  `PR.` fact fails. The reaction sentence from the tone spec is allowed, tagged, and counts toward
  the team's 2.
- The blurb writes under the tone prompts. The rankings spec adds no tone rule.

### The season file

- The pipeline writes one file per season beside the week folders, `rankings.json`, with its own
  schema version starting at 1. Keys: the schema version, the season, and a list of weeks. Each week
  has the week number and twelve rows. Each row has the roster ID, the team name, the record, the
  power rank, the movement or null, the four component ranks, and the blurb sentences for that team.
- The file is rewritten in full on every build. Weeks before the current one keep the blurb they had
  in the last file, since the writer runs for the current week only. Weeks with no saved blurb get
  an empty list.
- The build writes the file after the page. The `rankings` command writes it for a saved week
  from the saved facts and blurbs, with one writer call for the current week only. The `page-json`
  command does not touch it.
- The publish command copies the season file next to the week folder it copies, in the same
  commit.

### The site

- A reader loads the season file for the latest season, checks the schema version, and throws on a
  mismatch, the way the week reader does. A missing file returns null.
- A new route, `/rankings`, static. It shows the last week in the file. The table: rank, movement
  as an arrow with the count, avatar and team name, record, the four component ranks, and a row
  control that opens the blurb. On a phone, the four component ranks move into the expanded row
  above the blurb. No sideways scroll at 390.
- The expand uses the motion helper. With motion off, the row opens with no transition. The rows
  use the existing reveal with the existing stagger.
- The home page gets a chapter below Tools and above Weekly reports, labelled "Power rankings":
  the top three with their ranks, the biggest mover with its arrow, and a link to the route. The
  analyzer stays first. A missing file hides the chapter.
- New tokens, if any, go in the class helper's group list. The dataviz skill is read before any
  arrow or color choice, so the movement color works in both themes.
- The site reader and its fixture land before the pipeline writes the file, the same rule as the
  page schema.

### Glossary

- Power rank: the place from 1 to 12 by power score, for one week.
- Power score: the mean of the four components.
- Component: one of standing, form, schedule played, scoring. Each has a rank of 1 to 12.
- All-play record: wins and losses as if a team played every other team that week.
- Quality win: a head-to-head win against a team in the top 4 of the standings of that week.
- Movement: last week's power rank minus this week's. Positive is up.
- Schedule played is distinct from the existing next opponent win rate, which covers next week only.

## Testing Decisions

A good test gives a history and asks for the rankings, or gives a file and asks for the page, and
checks the result. A test never checks how a component is coded.

- The formula is a pure function from a history and a week to the twelve rows. Tests use the
  fixture history. Prior art: the standings and schedule strength tests that read from history.
  Tests: twelve rows, ranks are a permutation, movement is null in week 1, a 3-win streak lifts the
  form rank, a win against a top-4 team lifts the schedule rank, the components are ranks of 1 to
  12, and a weight change moves the result.
- The `PR.` facts and the rankings chapter are tested at the sheet level. Prior art: the sheet
  tests. Tests: twelve facts, the chapter holds every team, the numbers list holds every ordinal.
- The roster tags are tested at the code check. Prior art: the sentence count test. Tests: a
  missing tag fails, a team with no sentence fails, three sentences for one team fails, a first
  sentence without the `PR.` fact fails, a good blurb passes.
- The season file is tested at the render seam. Prior art: the page JSON render test. Tests: the
  schema version, twelve rows per week, past weeks keep their blurbs, the current week gets the new
  ones.
- The publish copy is tested with the existing publish test. Prior art: the test that the publish
  copies one week only. Test: the season file lands beside the week.
- On the site, the reader is tested like the week reader: reads the fixture, throws on the wrong
  version, returns null on no file. The table and the home chapter are tested like the standings
  component: render the fixture, check the rows and the arrows, open a blurb, check the phone
  layout folds the components. The motion-off path is tested like the reveal test.
- No new seam. Every test uses a seam that exists.

## Out of Scope

- A rank trend chart or a week picker. The file holds every week for that later.
- Trade values in any form.
- A writer rank from a Claude call. The rank is the formula.
- Luck, playoff odds, manager pages, and the home page redesign. Each is its own grill.
- A change to the standings table on the week page.
- The GitHub Actions build. Builds stay on Brian's Mac.

## Further Notes

- Weeks 1 to 6 are complete in the history, with twelve rows per week, points, and the pairing.
  Every input exists. No fetch is needed.
- The existing code already computes the rank before this week, the head-to-head streak, and the
  3-week trend. The formula reuses the season records function and the streak function.
- The site has only week 6 published. The season file gives it weeks 1 to 6 at once.
- The week 6 rebuild for the tone spec and the first rankings file are one `rankings` run after
  the twelve rewrites. Brian publishes once.
- Component ranks on the page are a safer read than decimals. A reader sees "9th hardest schedule"
  and no one argues over a 0.63.
