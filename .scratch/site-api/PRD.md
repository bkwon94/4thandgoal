# Site API: the trade analyzer as the first route

Status: ready-for-agent
Date: 2026-10-21
Depends on: `.scratch/trade-recap/PRD.md` (the grade left the weekly page)
Consumed by: the React site, `cpcfantasyfootball` repo, `.scratch/site-react/PRD.md`

## Problem Statement

A manager with a trade offer wants to know whether to accept it before the trade happens. Today
nothing in the league gives that answer. The weekly page once graded trades after the fact, with a
writer rule and no rubric, so two similar trades could get different letters for no stated reason.
The grade has now left the weekly page.

The site is static on GitHub Pages, so no page can call Claude. Brian also wants the site to grow
a live page and other data features later. Each of those needs the same backend.

## Solution

A small Python web service, the site API, deployed on Fly.io at `api.cpcfantasy.com`. It imports
the same modules as the weekly build. Its first route grades a proposed trade.

A proposed trade is two rosters, the players each gives, and which side asked. The rubric grades
each side: code sets a start letter from the trade value chart, applies named adjusters with caps,
and produces a breakdown. Claude reads the breakdown and the facts, writes an analysis paragraph
per side, and gives a verdict for the asker: accept, counter, or decline. The response is one JSON
document the site renders. One shared passphrase, a cache per trade, and a rate limit keep the
Claude bill to the league's use.

## User Stories

1. As a manager, I want to submit a trade offer and get a grade for each side, so that I know
   whether it is fair before I accept.
2. As a manager, I want a breakdown per side, the start letter and each adjuster that fired with
   its direction, so that I see why the grade is what it is.
3. As a manager, I want an analysis paragraph per side, so that I read the fit, the need, the
   standing, the schedule, and the injury picture in plain words.
4. As a manager, I want a verdict for my side, accept, counter, or decline, with one reason, so
   that I know what to do.
5. As a manager, I want the grade to start from the half-PPR trade value chart, so that the grade
   reflects what the league would pay.
6. As a manager, I want an RB valued above a WR, a WR above a TE, and a TE above a QB at equal
   rank, so that scarcity at the position counts.
7. As a manager, I want a two-for-one trade to need a solid margin on the depth side, so that two
   good players do not beat one great one on a plain sum.
8. As a manager, I want roster fit to count, so that a player who starts for me grades above one
   who sits.
9. As a manager, I want my standing to count, so that a contender's win-now move and a bottom
   team's future bet each earn credit.
10. As a manager at the top, I want credit for a bet on a suspended or injured star due back, so
    that an upside move is not graded as a loss.
11. As a manager, I want trend and usage to count, so that a rising player grades above a fading
    one with the same season points.
12. As a manager, I want injury history to count, so that a player who misses weeks grades lower.
13. As a manager, I want a handcuff treated as insurance, so that a backup to my own starter is
    never graded as a player with no stats.
14. As a manager, I want byes and the playoff weeks to count a little, so that schedule breaks a
    tie but never moves a letter on its own.
15. As a manager, I want a player with no chart value handled, so that the grade still comes
    from the adjusters.
16. As a manager, I want the data as-of line on the result, so that I know which week's chart and
    stats the grade used.
17. As a manager, I want the same trade to return the same breakdown every time, so that two
    managers never see two different letters for one offer.
18. As a manager, I want the result in under about 20 seconds, so that I wait once and read.
19. As a manager, I want the list of teams and their players from the API, so that the page form
    needs no other source.
20. As the commissioner, I want one shared passphrase for the league, so that strangers cannot run
    up the Claude bill.
21. As the commissioner, I want a repeat of the exact same trade served from a cache, so that a
    repeat costs no Claude call.
22. As the commissioner, I want a rate limit per address, so that one browser cannot loop the API.
23. As the commissioner, I want the service to cost about nothing when idle, so that the bill
    matches the league's use.
24. As the commissioner, I want the chart, the NFL stats, the injuries, the schedules, and the
    depth charts refreshed daily on their own, so that no hand step keeps the API current.
25. As the commissioner, I want rosters and standings read live from Sleeper, so that a trade
    made an hour ago shows in the form.
26. As the commissioner, I want the rubric and its numbers in one place, so that I can tune a band
    or a cap without a code hunt.
27. As the commissioner, I want a command that grades a proposed trade from my terminal, so that I
    can check the rubric with no browser.
28. As the commissioner, I want Claude's final letter allowed to differ from the code's by one
    step at most, with a stated reason, so that the prose and the letter never contradict.
29. As the commissioner, I want no chart value, chart name, or tier in the prose or the response,
    so that the chart author's table is never republished.
30. As the maintainer, I want the service to hold more routes later, so that the live page and
    the news features reuse the same deploy.
31. As the maintainer, I want the fetchers and the Claude call each to take a callable, so that
    tests run with no network and no Claude.
32. As the maintainer, I want one response fixture shared with the site repo, so that the API and
    the page agree on the contract.

## Implementation Decisions

### The service

- A FastAPI app in this repo, in its own package beside the pipeline, with one module per route
  group. The first group is the analyzer. The app serves CORS to `cpcfantasy.com` and localhost.
- Routes: a health check; the league's teams with their players, positions, NFL teams, and
  headshot URLs, for the form; and the analyze route, which takes a proposed trade and returns the
  result document.
- Every route except health requires the passphrase in a request header. The passphrase is a Fly
  secret. A wrong or missing passphrase returns 401 with no body.
- A rate limit per client address, in memory, with the limit in the tunable table. Past the limit
  the route returns 429 with a retry-after.
- The result cache key is the sorted set of players per side, the roster ids, the asker, and the
  data as-of stamps. A hit returns the stored document with no Claude call. The cache lives on
  the data volume so it survives an auto-stop.
- Deploy: a Dockerfile and a Fly app in the New York region, one shared CPU, auto-stop and
  auto-start, one small volume for the data cache and the result cache. The Claude key, the
  passphrase, and the Sleeper league id are secrets. The first deploys run by hand.
- The weekly build and the Tuesday job do not change and do not call the API.

### The proposed trade

- Input: season, the two roster ids, the player ids each side gives, and the asker's roster id.
  Two sides only. Players only, no picks. Each given player must be on the giving roster now,
  else 422 with the offending id.
- The data snapshot the grade reads: rosters, users, and standings live from Sleeper at request
  time; the NFL state for the current week; the chart for the current trade window week; season
  stats through the last completed week; snap, target, and red-zone use from nflverse; the
  injury report; schedules for byes and the week 15 to 17 opponents; depth charts for the
  handcuff test; and points allowed per position per defense, computed from the weekly stats.
- The slow sources refresh in a daily job inside the service at 06:00 Eastern, and on the first
  request when the cache is older than a day. The chart read reuses the chart module and its
  per-week cache. Schedules and depth charts are new nflverse fetches in the same shape as the
  injuries fetch.

### The rubric

- The rubric is one markdown file in the prompts directory. It states the criteria, their order,
  their caps, the letter meanings, and the verdict rule, in plain words. The Claude call includes
  it. A tunable table in code holds every number the rubric names, and the file points at it.
- Start letter. Per side, the ratio of trade value got over trade value gave from the chart.
  Bands, lower bound inclusive: 1.25 and up A, 1.10 B, 0.90 C, 0.75 D, below 0.75 F.
- Consolidation. When one side gives exactly one player and gets two or more, the depth side's
  sum is divided by the consolidation margin, 1.25, in both sides' ratios. A three-for-two trade
  gets no discount.
- Unlisted. A player with no chart row has no trade value. If any player in the trade is unlisted,
  neither side gets a start letter; both start at C and the breakdown says so. Exception: a
  handcuff with no chart row counts as 0 and keeps the start letter.
- Adjusters, each capped at one step, in this order:
  1. Roster fit. The side's best lineup before and after the trade, from the league's roster slots
     and each player's points per game over the last four weeks. A lineup gain at or above the fit
     threshold is one step up. A lineup loss at or above it is one step down. The side that got the
     single highest-value player, with no lineup loss, gets the step up. The depth side gets the
     step up only when every player it got starts.
  2. Standing. A contender is in a playoff spot by record. A seller is more than two games out of
     the last spot. A contender gets a step up for a lineup gain now or for a player with a
     return week at or before week 14, and a step down for a lineup loss now in return for a
     player who returns after week 14 or not at all. A seller gets a step up when it gets the
     highest-value player in the trade, and a step down when it gives that player for a lineup
     gain now. A team in the middle gets no step.
  3. Trend and usage. Snap share and target share over the last two weeks against the two before,
     from the history helpers. Got players up and gave players down is a step up. The reverse is a
     step down. Mixed is no step. Red-zone use breaks a tie inside this adjuster.
  4. Injury. A got player listed Out or on IR now, with no return within two weeks, or on the
     report in three or more weeks this season, is a step down. It never fires for a player the
     standing adjuster credited as a return bet.
  5. Handcuff. A got player who is second or lower on the depth chart of the NFL team whose
     starter is on the same fantasy roster. The fit and trend adjusters cannot step down because of
     him. He counts as 0 in the sums.
  6. Schedule. Byes left against byes done for the players got and gave, and the rank of the week
     15 to 17 opponents in points allowed to the position. It never moves a letter. The breakdown
     shows it as for, against, or even, and the verdict rule and the prose may use it.
- The sum of the adjuster steps is clamped to one either way. The final letter is the start letter
  plus the sum, clamped to A through F.
- Verdict rule, the code's default: accept when the asker's letter is B or better, or C with the
  other side at C or worse; decline when the asker's letter is D or worse; counter otherwise.
  Schedule for the asker turns a counter into an accept and against turns an accept at C into a
  counter.

### The Claude call

- The call takes the rubric, the breakdown for both sides, and a fact sheet built from the grade
  input builders the weekly build no longer uses: points per game, position rank, usage, injury,
  team record and standing, roster need, and the values. The model is the writer's model. The
  call uses the same client and parse path as the writer.
- Structured output: per side a final letter, a one-line reason when it differs from the code's
  letter, and an analysis paragraph of three to five sentences with cited fact ids; a verdict with
  one reason, and a flag when it differs from the code's default.
- A final letter more than one step from the code's letter is a parse failure. The call retries
  once, then the code's letters and verdict stand with the analysis text "Analysis unavailable".
- The code number check from the verifier runs on the prose: every number must appear in a cited
  fact or the breakdown. A chart value, sum, or ratio in the prose fails the check. The Claude
  verifier pass does not run.

### The response

- One JSON document: the proposed trade echoed with names and headshots; per side the start
  letter, each adjuster with its step and a one-line reason, the final letter, and the analysis;
  the verdict with its reason; and the as-of stamps: chart week, stats through week, rosters
  fetched at. No chart value, no sum, no ratio, and no chart name appear in it.
- A fixture response document is checked into this repo and copied into the site repo. The Python
  test asserts the live route's output has the fixture's shape, and the site's tests render it.

### The command

- A `cornerstone analyze` command takes the same inputs as the route and prints the breakdown and
  the verdict, with a flag to skip the Claude call.

## Testing Decisions

- A good test feeds inputs at a seam and asserts the breakdown, the letter, or the document. It
  never asserts how a helper is built.
- Seams, two new:
  1. The grade function: a proposed trade plus a snapshot in, a breakdown per side out. The
     snapshot is a plain model built from fixtures. The six real week 6 trades, with the week 6
     chart values fixture, form the base cases, with the expected start letter, adjusters, and
     final letter worked out by hand from the rubric. Each adjuster gets a case that fires up, one
     that fires down, and one at the cap. The consolidation, unlisted, and handcuff rules each get
     a case. The clamp gets a case.
  2. The analyze route: the FastAPI test client with the Sleeper fetch, the slow-source fetchers,
     and the Claude call patched to callables. Cases: a good request returns the document in the
     fixture's shape; a wrong passphrase is 401; a player not on the giving roster is 422; a repeat
     is a cache hit with no second Claude call; the rate limit returns 429; a Claude letter two
     steps off is a parse failure that falls back.
- Prior art: the chart tests, which patch the fetch and the read; the pipeline tests, which patch
  the fetchers; the trade tests on the week 6 fixture.

## Out of Scope

- Draft picks in a proposed trade.
- Accounts or per-manager auth. One shared passphrase.
- A GitHub Actions deploy for Fly. The first deploys run by hand.
- The live page, news, or any second route group. The service is built so they fit.
- The Claude verifier pass on the analysis.
- Trades of three rosters.
- The weekly page and the Tuesday build.

## Further Notes

- The trade deadline is week 11. After it the route still grades, which is fine for a what-if.
- The chart author's table is never republished: only traded players' values reach the fact
  sheet, and none reach the response.
- A handcuff test needs the depth chart. When the depth chart fetch fails, the handcuff adjuster
  does not fire and the breakdown notes the source was missing.
