# The waiver wire page

**Status:** ready-for-agent
**Date:** 2026-10-23

## Problem Statement

Claims clear on Wednesday morning. On Tuesday night a manager opens Sleeper, scrolls a flat list
of free agents sorted by a one-week projection, and sees Kenny Gainwell at the top. The list says
nothing about why a player matters this week, nothing about what the experts say, and nothing
about the bid it takes to win him in this league. The manager then opens three tabs, reads a
column, checks the injury report, guesses a bid, and still does not know who can outbid him.

The data to answer all of that already lives in the pipeline or one call away. Nothing shows it.

## Solution

A waiver wire page on the site, built once a week on Tuesday with the report. It shows the free
agent pool in five buckets: best adds, trending, sneaky, stashes, and drops. A board engine ranks
the pool from usage trend and team environment first, projection as a tiebreak, and tags each
player with the facts that put him there. A research step adds what the experts say, every claim
with a source. The page is a black card. The ranked players drift in a field, each with a price on
his headshot. The twelve FAAB budgets sit above as a bar ring. A manager picks his team once, and
his bar turns red. Tap a player, and a sheet shows why he matters, the bid to win, what the last
one like him cost, and how many teams can outbid you.

## User Stories

### A manager on Tuesday night

1. As a manager, I want the best adds in one glance, so that I know who to claim before I read a word.
2. As a manager, I want the players who are trending across Sleeper, so that I see who everyone else is about to claim.
3. As a manager, I want sneaky adds, players whose usage rose before their projection did, so that I beat the room to them.
4. As a manager, I want stashes, players out now with a return in sight, so that I use a bench spot on next month.
5. As a manager, I want drop candidates from the rosters in this league, so that I know who to cut to make room.
6. As a manager, I want one bucket on screen at a time with tabs, so that the page fits a phone.
7. As a manager, I want each player to carry three short facts, so that I know why he is on the list.
8. As a manager, I want one fact about his usage, so that I see the trend with numbers.
9. As a manager, I want one fact about his team, so that I see the offense he plays in.
10. As a manager, I want one fact about the story, an injury ahead of him or a quote, so that I know what changed.
11. As a manager, I want what the experts say, with a source I can open, so that I can check the claim myself.
12. As a manager, I want the page to say when an expert disagrees with the engine, so that I weigh both.
13. As a manager, I want the rest of season projection beside the week projection, so that a stash and an add read apart.
14. As a manager, I want the injury status and the return week when there is one, so that a stash is not a surprise.
15. As a manager, I want the bye week, so that I do not claim a player who sits this week.

### FAAB

16. As a manager, I want every team's budget left, so that I know the room.
17. As a manager, I want my own budget in red, so that I find it in a glance.
18. As a manager, I want a bid to win on every player, so that I have a number to start from.
19. As a manager, I want the bid to win to count the budgets left, so that a number no rival can pay never shows.
20. As a manager, I want the bid to win to count positional need, so that a team with four healthy RBs does not raise the price.
21. As a manager, I want to see what the last player like him cost in this league, so that I know the going rate.
22. As a manager, I want to know how many teams can outbid me at my budget, so that I know when to go all in.
23. As a manager, I want the waiver order shown when the bids tie, so that I know who wins a tie.
24. As a manager, I want the bid to win to be a whole dollar, so that I type it into Sleeper as is.

### The look

25. As a manager, I want a black card with the red glow, so that the page feels like the trade chips and the rankings.
26. As a manager, I want the headshots to drift in the field in slow motion, so that the page feels alive.
27. As a manager, I want the size of a headshot to follow the rank, so that the top add is the biggest.
28. As a manager, I want the price on every headshot, so that I read the cost without a tap.
29. As a manager, I want a tap on a headshot to fill the sheet, so that the why is one touch away.
30. As a manager, I want the sheet to hold its content when I switch tabs, so that I can compare two players.
31. As a manager, I want the drift to stop when my phone asks for reduced motion, so that the page respects my setting.
32. As a manager, I want the drift to stop when the tab is hidden, so that it does not drain my battery.
33. As a manager, I want the page to work at 390 pixels wide, so that it fits my phone.
34. As a manager, I want no headshot to cover another, so that every player is tappable.
35. As a manager, I want a missing headshot to show the default, so that a rookie still has a face.
36. As a manager, I want a list below the field, so that I can read every player in order when the field is too busy.

### The team pick

37. As a manager, I want to pick my team once on my phone, so that I do not pick again next week.
38. As a manager, I want the pick with the same team list as the analyzer, so that it looks familiar.
39. As a manager, I want a chip in the masthead with my team and a Change link, so that a wrong pick is one tap to fix.
40. As a manager, I want the page to render with no pick, so that a first visit is not a wall.
41. As a manager, I want no login, so that the page opens as every other page does.
42. As a commissioner, I want a flag that hides the page, so that the code ships before the page is ready.

### Freshness

43. As a manager, I want the page built with the Tuesday report, so that it is fresh for Wednesday claims.
44. As a manager, I want the build time on the page, so that I know how old the data is.
45. As a manager, I want the page to say when the research step was skipped, so that I know the experts are missing.
46. As a manager, I want last week's page to stay at its own URL, so that I can see what I missed.

### The commissioner

47. As a commissioner, I want the page to need no new secret, so that the build runs as it does today.
48. As a commissioner, I want the research step to cost a few dollars a week at most, so that the budget holds.
49. As a commissioner, I want the research cached for the week, so that a rewrite never pays twice.
50. As a commissioner, I want the build to finish without the research step when the search fails, so that the page still ships.
51. As a commissioner, I want the page published by `cornerstone publish` and nothing else, so that the publish rule holds.
52. As a commissioner, I want the board to rebuild to the same ranks from the same raw data, so that a rebuild never changes the page.

### The developer

53. As a developer, I want the board engine behind one function with no network and no Claude, so that a test feeds a fixture and reads the buckets.
54. As a developer, I want the research step behind one function with the search call injected, so that a test uses a fake.
55. As a developer, I want every number on the page to come from a fact with an id, so that the verifier's rule holds without a new check.
56. As a developer, I want every expert claim to carry a source URL, so that the verifier treats the URL as the citation.
57. As a developer, I want the thresholds of each bucket as tunables, so that one place holds them.
58. As a developer, I want the week file optional, so that the site ships first and old weeks still load.
59. As a developer, I want the page in the site's motion pattern, so that the reduced-motion test covers it.

## Implementation Decisions

### The pool and the data

- The pool is every player in the players file with a team, status active, and a position of QB,
  RB, WR, TE, K, or DEF, who is on no roster in this league. The drops bucket draws from the
  rostered players instead.
- The projections ahead fetch lifts its roster filter, so the raw file holds every player with a
  projection. Rest of season projection is the sum from week N+1 to week 17 with the bye as 0.
- The week fetch gains one call to Sleeper's trending adds endpoint, lookback 24 hours, top 50,
  saved as one raw file beside the others. The count of adds per player is the trending signal.
- The budgets come from each roster's used budget against the league's budget setting. The
  waiver order comes from the roster settings. Both are already in the raw files.
- The nflverse module gains per-player per-week usage from the play by play and the FTN charting:
  offensive snaps, snap share, targets, target share, carries, red zone touches, and routes where
  the charting has them. It gains per-team per-week environment: plays per game, neutral pass
  rate, pass rate, and rush success rate. Both read through the existing cache with the same max
  age. The depth chart slot and the injury status come from the files already pulled.
- The bid history reads the waiver claims of every week in the history, with the bid, the player,
  the position, the week, and whether the claim won. The week 6 history holds a handful of claims
  with the largest at $2, so the price model leans on budgets and need until the history fills.

### The board engine

- A new module holds the board engine. In: the pool, the usage weeks, the team environment, the
  trending counts, the injuries, the depth charts, the projections, the rosters, the budgets, the
  waiver order, the bid history, the week. Out: the five buckets in rank order, each player with
  his facts, his price, and his bucket reason; the budget table; the build time. It calls no
  network and no Claude.
- Each player gets three scores from 0 to 1: usage trend, environment, and projection. Usage
  trend is the change in snap share and target or carry share over the last `USAGE_WEEKS` (2)
  weeks, scaled by position. Environment is the team's rank in plays per game and neutral pass
  rate for a QB, WR, or TE, and in rush success and plays per game for an RB. Projection is the
  rest of season projection ranked within the position. The board score is the weighted sum with
  `BOARD_WEIGHTS`, usage 0.5, environment 0.3, projection 0.2. Brian chose on 2026-10-23 that
  usage leads and projection is a tiebreak, because the projection lags the usage.
- Best adds: the top `BUCKET_SIZE` (8) of the pool by board score, from QB, RB, WR, and TE, at most
  `PER_POSITION` (3) per position so one position does not fill the bucket. Kickers and defenses
  stay in the pool and out of this bucket, Tina's call on 2026-10-23 after ticket 01: they have no
  usage or environment score, so a position-relative projection score puts the top of each in
  best adds every week.
- Trending: the top 8 of the pool by trending count, with the count as the fact. A player in both
  best adds and trending shows in both.
- Sneaky: the pool players whose usage trend score is in the top quarter and whose projection
  score is in the bottom half, or who sit one slot below an injured player on the depth chart.
  Top 8 by usage trend. A player in best adds is not sneaky.
- Stashes: the pool players with an injury status of out or IR, a return week inside the season
  from the hand-kept returns file or the injury file, and a rest of season projection in the top
  half of their position. Plus the handcuff rule: a player one slot below a starter on the depth
  chart whose rest of season projection on that starter's injury would be in the top half. Top 8
  by rest of season projection.
- Drops: the rostered players whose snap share fell for `DROP_WEEKS` (3) weeks in a row and whose
  rest of season projection is below the best pool player at their position. Top 8 by the gap.
  Each row names the roster that holds him. A manager with a team pick sees his own drops first.
- A player's facts: one usage fact, "{name} played {share}% of snaps and took {targets} targets
  last week, up from {share_before}% and {targets_before}". One environment fact, "{team} runs
  the {rank} fastest offense and passes on {rate}% of neutral downs". One story fact, from the
  injury file and the depth chart, "{starter} is {status}, and {name} is next on the depth chart".
  Every digit in a fact's text is in the fact's numbers, as every fact does today. The story fact
  may be empty, and then the research claim takes its place on the sheet.
- The price: the bid to win is the smallest whole dollar that beats the highest bid the model
  expects from any rival. Each rival's expected bid is his budget left times a need factor for the
  position, from `NEED_SHARE`: 0.35 when the rival has fewer healthy starters at the position
  than the lineup needs, 0.12 otherwise, capped at his budget left. Past claims for the position
  this season raise the floor to the largest winning bid plus one. The price never exceeds the
  highest budget left among the rivals. Every price is a fact with the inputs in its numbers.
- The last like him: the most recent winning claim of the same position and the same bucket tier
  this season, with the team and the week. Empty when none.
- Can outbid you: the count of rivals whose budget left exceeds the price. It uses the viewer's
  pick only on the site. The file holds the count per budget level, so the site computes it with
  no engine call.
- The engine runs in the facts step of the build from the first week it ships. A rewrite reads
  the saved board and never reruns it. The random parts are none, so the same raw gives the same
  board.

### The research step

- A new module holds the research step. In: the ranked players of the best adds, trending,
  sneaky, and stashes buckets, up to `RESEARCH_PLAYERS` (32), with their facts. Out: per player up
  to `CLAIMS_PER_PLAYER` (2) claims, each one sentence with a source URL, a source name, and a
  date. It takes the search call as a parameter, so a test injects a fake.
- The search call is one Claude call per player with the web search tool, a system prompt that
  asks for waiver takes and news from the last 7 days, Yahoo Fantasy first with the writers Brian
  follows there, then the wider web. The prompt names the engine's facts, so the claim either
  backs them or disputes them, and the output says which. A claim with no URL is dropped.
- The claims land in the saved facts as a fact family with the URL in the fact and the sentence
  as the text. The verifier treats a sentence with a URL as cited. The code check still bans the
  banned words.
- The research runs once in the build, after the engine. The results save with the week, so a
  rewrite reads them. A search failure for one player logs and leaves that player with no claim.
  A failure of every player logs a warning and the page carries a line that the experts are
  missing this week.
- The cost cap: `RESEARCH_PLAYERS` times one search call. At the Claude list price with web search
  that is a few dollars a week. The number is the one knob.

### The week file

- The build writes one `waiver.json` beside `page.json` in the week folder. It holds the schema
  version, the build time, the five buckets, the budget table with the waiver order, and the
  research claims per player. Each player carries his id, name, position, team, bye, injury
  status, return week, week projection, rest of season projection, trending count, facts, price,
  the last like him, and the outbid counts per budget level. The headshots of the ranked players
  save to the week's headshot folder as the report does.
- The publish copies the week folder as it does, so the file ships with the week. No new publish
  path.

### The site

- A build-time flag hides the page, as the finder flag does today: one env var read in the config
  module, off by default. Off, and the route does not build and the masthead has no link. Brian asked
  for the flag on 2026-10-23, so the code ships before the page shows.
- A new route for the waiver page per season and week, static, beside the week page. The route of
  the current week is the one the masthead links. A week folder with no waiver file has no route.
- The site types mirror the file. The loader accepts a week with or without the file.
- The page is one client component with the War chest look from the mockup of 2026-10-23: the
  masthead with the week and the build time, the budget ring, the bucket tabs, the drift field,
  the sheet, and the list below the field. The ring is twelve avatars with a bar each, in budget
  order, the viewer's in red. The field places the top 6 of the open bucket by rank with the size
  from the rank, and the rest go in the list. Each headshot wears its price. The sheet opens on
  the top player and changes on a tap. The tabs change the bucket.
- The drift is a slow translate on each headshot with Framer Motion, a different period per
  headshot, and it turns off through the one reduced-motion switch and the page visibility
  state. The positions in the field come from a fixed layout per rank, so no two overlap at 390
  pixels and no random part changes the page between renders.
- The team pick reuses the team picker from the analyzer with one list and no second picker. The
  pick saves in local storage under its own key with the guarded pattern of the passphrase. The
  masthead shows the pick as a chip with a Change link. No pick shows no red bar and no outbid
  count. The pick never touches the analyzer's two sides.
- The chip, the sheet, the price, and the ring use the tokens in the global stylesheet. New sizes
  and colors go there, never in a component.
- Glossary entries: **Waiver pool**, **Board score**, **Bucket**, **Bid to win**, **Research
  claim**, with the page words.

## Testing Decisions

- A good test feeds inputs at a seam and asserts the output. It never asserts how a score is
  weighted or how a layout is placed.
- Engine seam: a fixture pool of about 20 players on the week 6 raw with hand-set usage, trending,
  injuries, depth charts, projections, budgets, and a small bid history. Cases: a player with a
  rising snap share and a flat projection lands in sneaky and not in best adds; a player out with
  a return week and a top-half projection lands in stashes; a rostered player with three falling
  weeks and a better pool player lands in drops with his roster named; one position never takes
  more than the per-position cap in best adds; the trending bucket follows the counts; the price
  never exceeds the highest rival budget; a past winning claim raises the price floor; the same
  fixture gives the same board twice; every number in a fact's text is in its numbers. No test
  pins a rank from the real week 6 data. Prior art: the odds engine tests and the power rankings
  tests.
- Research seam: a fake search call returns claims with and without URLs. Cases: a claim with no
  URL is dropped; the per-player cap holds; a failure for one player leaves the others; a failure
  for every player sets the missing flag. Prior art: the writer tests with a fake call.
- Fetch seam: the week fetch saves the trending file from a fake client, and the projections
  ahead file holds an unrostered player. Prior art: the Sleeper fetch tests.
- Usage seam: the nflverse reader returns snap share, targets, carries, and the team environment
  from a small play by play fixture. Prior art: the drops reader tests.
- Week file seam: the build on the fixture writes the file with the schema version, five buckets,
  and the budget table. Prior art: the rankings file tests.
- Site: the loader test reads a week with and without the file. The component test renders the
  tabs, the ring with the viewer's bar marked, the field with the prices, the sheet on a tap, and
  the list. The reduced-motion test covers the drift. The team pick test saves and reads the key
  and survives a storage throw. Prior art: the power rankings component tests, the reduced-motion
  tests, the team picker tests, and the passphrase tests.
- One prompt text test pins the research prompt's source order and the 7-day rule.

## Out of Scope

- The waiver chapter in the weekly report. Brian kept it separate on 2026-10-23.
- A live page off the API that refreshes before Wednesday. Weekly static first.
- A per-team view that filters the buckets by roster fit. The team pick only marks the budget
  and the outbid count.
- The price slider from mockup F. A later ticket, noted on 2026-10-23.
- ESPN ownership data. Sleeper's trending adds cover it.
- Kicker and defense ranks beyond the pool filter. They sit in the pool but no bucket rule
  targets them.
- A bid the page places for you. The page shows a number. Sleeper takes the claim.

## Further Notes

- The mockups of 2026-10-23 live in `.superpowers/brainstorm/` in this repo, with the War chest
  look as `look-faab.html`, option D. The site prototype was skipped because the mockups did its job.
- The real week 6 pool by Sleeper's one-week projection is Gainwell, Najee Harris, and Mark
  Andrews. That list is the reason the engine leads with usage. A test that pins ranks from the
  real raw would pin the wrong thing.
- The research prompt names Yahoo's waiver column and the writers Brian reads there. The first
  ticket on the research step starts with a research task on which Yahoo columns and feeds hold
  those writers, so the prompt names real URLs.
- Brian's own examples of great adds: Tyler Shough on pace and neutral pass rate, Mahomes on a
  new coordinator and a run game, Germie Bernard on target share plus a quote plus two injuries
  ahead of him. The three score kinds come from those three.
