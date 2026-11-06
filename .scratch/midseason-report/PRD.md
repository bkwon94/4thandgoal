# Midseason report: one edited moment per season that a manager reads end to end

Status: ready-for-agent
Date: 2026-11-06
Apps: both. The pipeline computes the facts of each chapter, runs the sim, writes the prose, and publishes two season files. The site renders the report at `/midseason/2026`, the sim replay inside it, the home takeover, and the home tile.
Spec branch: `midseason-report`.
Source: the map `.scratch/midseason-report/MAP.md` and decision tickets 01 to 17. Tickets 14 to 17 hold the redesign after the first build. ADRs 0010, 0011, 0013, 0015, 0022, and 0023.
Tickets: 01 to 19, in `issues/`. Tickets 15 to 19 build the redesign.

## Problem Statement

The site gives a manager one week at a time. Halfway through the season, no page tells the story of the season so far: who got lucky, whose draft paid off, which trade was a robbery, and who is likely to win the title. Brian wants one report per season that blows a manager away, in the redesign look, with a roast of every bad football decision.

A manager also cannot see how the rest of the season may play out. The weekly playoff odds give a number, but not a season that a manager can watch play out to a champion.

The first build of the report, on 2026-11-06, did not meet the bar. Brian found the look below the redesigned pages, the text too wordy, the rows cluttered with big red tags, the swap grid hard to read, and "The roast" as its own block lame.

## Solution

Brian runs one build by hand for the week that he names. The build computes the facts of 13 chapters from the league's own data, runs a sim of the rest of the season, and the writer writes the prose. Brian reviews the draft, then publishes it.

The site shows the report at `/midseason/2026` as three lean acts on one scroll. Each chapter is a headline, one visual or table, and 40 words of prose or fewer. The rows are quiet, and a tag is a plain word. The roast is the voice of the whole paragraph, at the level each client sets. The opener is the title race. The report ends on the sim: each press of a button replays one stored season in the look of a sports broadcast, through the playoffs to a champion. The home page shows the report as a takeover for a short time. A home tile then stays for the rest of the season.

Both clients turn the report on. The sim is its own package, so a weekly page or a standalone sim page can use it later.

## User Stories

The opener and the shape

1. As a league manager, I want the report to open on the title race, so that I see at once that my team still has a chance.
2. As a league manager, I want the report in three acts, "How we got here", "The moves", and "What comes next", so that a long report reads as one story.
3. As a league manager on a phone, I want a dark title page at the start of each act, so that I feel progress as I scroll.
4. As a league manager, I want a chapter rail that stays at the top, so that I can jump to an act or a chapter.
5. As a league manager, I want every team to get at least one headline, so that the report is about the whole league and not one team.
6. As a league manager, I want no team to take over the report, so that one extreme team does not crowd out the rest.
7. As a league manager, I want the report in the same look as the rest of the redesigned site, so that it feels like part of the site.
8. As a league manager, I want the report to work on a phone and on a desktop, so that I can read it anywhere.

Act I: How we got here

9. As a league manager, I want the standings with the full record, points for and against, the streak, and the playoff odds, so that I know where each team stands.
10. As a league manager, I want each team's arc, such as a Turnaround or a Collapse, so that I read the shape of a season in one word.
11. As a league manager, I want an arc to cite the numbers behind it, so that I trust the label.
12. As a league manager in CPC, I want an arc of the start and now windows to count the median game, so that the arc agrees with the standings.
13. As a league manager, I want to see my Schedule luck, so that I know how many wins my schedule gave or took.
14. As a league manager, I want my luck explained in plain words, with a worked example from a real team, before any number, so that I understand it. The page never says "All-play".
15. As a league manager, I want the Schedule swap as one line of text per team, with my real record, my best schedule, and my worst schedule, so that I see what another schedule would have given me.
16. As a league manager, I want the best schedule that I missed called out, so that I can complain with a fact.
17. As a league manager, I want points against and my close-game record beside my luck, so that I see why the luck happened.
18. As a league manager, I want the Injury toll of each team in the Quick hits, so that I know who lost the most starter games.
19. As a league manager, I want the Position top 10 for QB, RB, WR, and TE, and DEF in CPC, so that I see the best players of the season in my league's scoring.
20. As a league manager, I want the Position top 10 to show who has each player, or a "Free agent" tag, so that I see who missed a good player on the waiver wire.
21. As a league manager on a phone, I want one position at a time with a text switch, so that the chapter is not 50 rows long.

Act II: The moves

22. As a league manager, I want the top 5 draft steals and busts of my league's own draft, so that I can brag or roast.
23. As a league manager in CPC, I want draft value to read the auction dollars, so that a $2 steal shows as one.
24. As a league manager in NorCal, I want draft value to read the pick number, so that the snake draft is graded fairly.
25a. As a league manager, I want the letdowns of the draft, a high price that is good on paper but has gone cold, so that Bijan at $81 gets his due.
25. As a league manager, I want a bust tagged "hurt" or "just bad", so that an injured pick is not roasted like a bad pick.
26. Removed by decision 15. No "the one that got away" line, in the draft or in the waivers.
27. As a league manager, I want the top 5 waiver hits by Points over the line, so that I see which pickups won games.
28. As a league manager, I want the top 5 waiver misses, so that a big bid that gave nothing is roasted.
29. As a league manager, I want the outbid list, so that I see the hit that I lost by a few dollars.
30. As a league manager, I want every trade with its Trade result, so that I know who won each trade so far.
31. As a league manager, I want the top 3 trades as full cards, so that the biggest robberies stand out.
32. As a league manager, I want a trade card to show the record of each team since the trade, so that I have context.
33. As a league manager, I want each result with a winner to name the team, such as "Slight edge to <team>", so that I know who won. The page shows no "hurt on arrival" tag. The pipeline keeps the field.
34. As a league manager, I want my bench points and the weeks where my best lineup would have won, so that I see my lineup mistakes.
35. As a league manager, I want the record book, so that the highest score, the lowest score, the biggest margin, and the closest game are on record.
36. As a league manager, I want seven midseason awards, each with its fact, so that the season gets its moments.
37. As a league manager, I want an award that is the same game as a record-book entry to show once, so that the report does not repeat itself.

Act III: What comes next

38. As a league manager, I want my remaining schedule with my opponents' records, so that I know how hard my path is.
39. Removed by decision 15. No Players to watch chapter.
40. As a league manager, I want the sim as the finale, so that the report ends on the most fun part.

The sim replay

41. As a league manager, I want to press one button and watch one season play out, so that I see one way the season can end.
42. As a league manager, I want the regular season and the playoffs clearly split, so that I know when the bracket starts.
43. As a league manager, I want a lower third with the scores each week and the standings to reorder, so that the replay feels like a broadcast.
44. As a league manager, I want a red PLAYOFFS wipe after week 14, then the final standings with the cut and the byes, so that the split is clear.
45. As a league manager, I want the bracket to draw in and each winner to slide forward, so that I can follow the playoffs.
46. As a league manager in CPC, I want the bracket to reseed after round 1, so that the replay follows our league's rules.
47. As a league manager, I want a big champion card with the title odds of all runs, so that I know how likely that champion is.
48. As a league manager, I want the odds of all 10,000 runs with the replay, so that one run is not mistaken for the forecast.
49. As a league manager, I want to skip to the end, so that I can see the result now.
50. As a league manager, I want to press again for a new run, so that I can see other endings.
51. As a league manager who turns motion off, I want the replay to fade between beats with no movement, so that I can still follow it.

The roast

52. As a league manager, I want the roast to have no limit on heat for football decisions, so that the report is fun.
53. As a league manager, I want the roast to stay off life outside fantasy, with no profanity or slurs at any level, so that nobody is hurt.
54. As a league manager, I want each paragraph to cite real facts, so that a roast is earned.
55. As Brian, I want a `roast` setting per client with four levels, `off`, `warm`, `hot`, and `savage`, so that each league chooses its voice.

The home page

56. As a league manager, I want the home page to show the report when it comes out, so that I do not miss it.
57. As a league manager, I want a home tile with one big fact after the takeover ends, so that I can still find the report.
58. As a league manager, I want no new item in the dock, so that the menu stays the same.

Brian's build and review

59. As Brian, I want one command that builds the report for the week I name, so that I can run it once by hand.
60. As Brian, I want to run the build again later, so that I can rebuild after a stat correction.
61. As Brian, I want a review file with every blurb and the facts it cites, so that I can read the draft before it goes live.
62. As Brian, I want to edit a blurb in the draft, so that I can fix a line the writer got wrong.
63. As Brian, I want the publish to check every blurb again, so that an edit cannot add an uncited number.
64. As Brian, I want the publish to be the one step that puts the report live, so that nothing goes live by accident.
65. As Brian, I want each client to turn the report on with one line, so that NorCal gets the same report as CPC.

The sim as a module

66. As Brian, I want the sim to be its own package, so that I can add it to a weekly page or a standalone page later with no rewrite.
67. As Brian, I want the sim's odds to agree with the weekly playoff odds, so that two pages never give two different numbers.

The redesign

68. As a league manager, I want each chapter to hold a headline, one visual or table, and 40 words of prose or fewer, so that the report reads fast.
69. As a league manager, I want lineup choices and the injury toll in one Quick hits block, so that the small chapters do not slow the report.
70. As a league manager, I want a "See the sim" link in the opener, so that I can jump to the finale.
71. As a league manager, I want a tag as a small plain word with no box, so that tags do not take over a row.
72. As a league manager, I want cards with small corners and no full pills, so that the report looks like the rest of the site.
73. As a league manager, I want the awards as lines, "MVP — player, team — fact", so that I read them at a glance.
74. As a league manager, I want player points with 1 decimal place and team scores with 2, so that the numbers are consistent.
75. As a league manager, I want the roast in the voice of the whole paragraph, not in a block or a last line, so that the writing reads naturally.
76. As a league manager in a league that sets `savage`, I want a full roast from the first word to the last, so that the report is merciless.
77. As a league manager, I want a paragraph to call back to a fact from another chapter, so that the writing is sharp.
78. As a league manager, I want each number to name its unit, such as points over the line, so that I do not misread it.

## Implementation Decisions

### Two new packages

The feature adds two packages under ADR 0023. Each has a Python part, a site part, and a README with Knows, Ports, and Does not do.

- **`sim`** owns the season sim. Its Python part draws the rest of the regular season and the playoff bracket. Its site part is the replay. It imports only `league` and `facts`. It knows nothing of the report.
- **`midseason`** owns the report. Its Python part computes the facts of each chapter and the prose blocks. Its site part is the report page, the takeover part, and the home tile. It imports only `league` and `facts`. It never imports `sim`.

The apps wire the two together, as they wire `rankings` into the week today.

- The pipeline app runs the sim, then hands its result to the report through a port that `midseason` declares. The sim facts reach the report as data, not as an import.
- The site app mounts the replay of `sim` in the slot that the report page leaves for it. The report page takes the replay as a child.

A client turns the report on with `midseason` in its package list. The report needs `sim`, so the client takes both. The config check fails a client that takes `midseason` without `sim`. Neither package adds a menu item.

### The sim engine

Ticket 07 decided the model. The sim keeps the draw of the weekly odds: a level per team shrunk to the league mean, a normal weekly score, and the pull toward the projected best lineup. It adds:

- the bracket of weeks 15 to 17, with 6 seeds and byes for seeds 1 and 2;
- the reseed after round 1 for a league whose bracket reseeds, as CPC does. NorCal has a fixed bracket. The reseed rule reads the league's bracket settings, not the client name;
- the projected totals through week 17;
- full counts: playoff, bye, title, each seed, and each final win total;
- 10,000 runs with a fixed seed from the season and the week, so one input gives one output.

The sim does not import `rankings`. So for now the draw lives in two packages. A parity test guards it (Testing Decisions). A later spec may move the weekly odds onto `sim`.

### The published files

Each package publishes one season-level file, beside `rankings.json` and `managers.json`. The pipeline owns each shape with pydantic, and the site reads each with a hand-written Zod schema (ADRs 0011 and 0013).

- **`sim.json`** holds the week of the run, the parameters, the odds of all runs per team, the seed odds, the final-win odds, and a sample of 200 runs. A run holds every team's score for each week left, so the site replays the table and the bracket with no draw of its own. The file stays under about 50 KB gzip.
- **`midseason.json`** holds the week of the report, the takeover end week, the opener, the three acts and their chapters with the facts and the blurbs, and the facts of the home tile.

### The report: chapters and rules

The order, from tickets 09, 14, and 15:

1. Act I, "How we got here": the state of the league; arcs; schedule luck with the schedule swap; Position top 10.
2. Act II, "The moves": draft steals and busts; waiver hits and misses; the trade report card; the record book with the awards; the Quick hits, with lineup choices and the injury toll.
3. Act III, "What comes next": the look ahead; the sim as the finale.

The opener is the title race: the title odds of the leaders and the record leader's title odds. It has a "See the sim" link that jumps to the finale. The rules of each chapter are those of its decision ticket. The spec repeats only what a builder needs at hand:

- **Arcs** (ticket 05): eight arcs. The start window is weeks 1 to 4, and now is the last 4 weeks played. Good is 60% or more, and bad is 40% or less. Window arcs count the full record, and streak arcs count head to head only. Snakebit and Smoke and mirrors read Schedule luck at −1.5 and +1.5. A team has at most 2 arcs, and the page orders them by the size of the swing on a 0 to 1 scale. A team with no arc gets no row. When no team has an arc, the chapter says so in one line.
- **Schedule luck and the swap** (tickets 06 and 16): Schedule luck is head-to-head wins minus All-play wins. The swap keeps the self-meet rule, and CPC records keep the team's own median results. A tie counts half. The page shows the swap as one text row per team, sorted by the spread between best and worst: the real record, the best record and whose schedule gives it, and the worst record and whose schedule gives it, each with its change in wins as a muted word. A tie of schedules reads "or" for 2 teams and "and N others" for more. The page has no grid and no bar.
- **The words of luck** (ticket 16): the page never says "All-play". The columns are "Real wins", "Wins if you played everyone", and "Luck (gap)". A short card above the table explains the idea with a worked example from one real team. Each luck number has a word: "lucky" above 0, "unlucky" below 0, and "even" for a gap smaller than 0.5. The word takes the accent color at +1.5 or more, or −1.5 or less. The luck table counts head to head only, and the swap counts all games. Each says its count in plain words.
- **Position top 10** (ticket 10): total league points, every NFL player, one position at a time, opening on RB.
- **Draft value** (ticket 02): the cost rank at the position against the points rank at the position, among the drafted players of that position. The top 5 steals and the top 5 busts. No "the one that got away" line (ticket 15). The letdowns (ticket 20): a pick with a top 10 price of the whole draft, not a bust, with no week in the top 17 of his position in the last 4 weeks played. Each row names the price, the season rank at the position, and the last week in the top 17.
- **Waivers** (ticket 03): the top 5 hits by Points over the line, the top 5 misses, the top 3 outbid, and the streaming king. A claim with no game after it is never a miss. No "the one that got away" line (ticket 15).
- **Trades** (ticket 04): the Trade result from the gap of net Points over the line. The lines are tunables: Robbery at a gap of 90 or more, Clear win at 60 or more, Slight edge at 10 or more, Even below 10, and Too soon under 2 weeks. On the CPC week 8 data, these give 2 Robberies and 2 Clear wins, as ticket 04 asks. Each result with a winner reads "<result> to <team>". Each trade after the top 3 is two quiet lines: the week, the teams, and the result, then the players of each side, muted.
- **Awards** (ticket 10): MVP, Streaming king, Bench crime of the year, Heartbreak of the year, Beatdown of the year, Most active, and Set and forget. Heartbreak and Beatdown show inside the record book, so each game shows once. The MVP may also be a Position #1. It answers a different question: the best player across positions.
- **Points for** is the sum of the weekly scores, the same sum as the standings. The season total from Sleeper can differ after a stat correction.
- **Long lists** show their first 5 rows, with a "Show all" control. The counts of tickets 02 and 03 stand.

### The look of the report

Tickets 14 and 15 decided it, on the boards of the Design canvas. The report keeps the shared look of ADR 0024 and these rules:

- **Lean chapters.** Each chapter is a headline, one visual or table, and 40 words of prose or fewer. The page may stay long, about 10,000 px on a phone. No chapter closes by default.
- **Quick hits.** Each of the two parts of Quick Hits has 20 words or fewer.
- **Tags.** A tag has no box and no fill. A fact that describes the player goes in the second line, such as "Free agent · QB · MIN". Any other tag is a small mono caps word in a muted color. "Just bad" uses the accent color.
- **Corners.** Cards have 8 px corners. The report has no full pill.
- **The position switch** is plain text segments with a 2 px accent underline that slides to the chosen position.
- **"Show all"** is a mono text control with a chevron and no border. It changes to "Show top 5", and the chevron turns.
- **The awards** are lines: "MVP — Jahmyr Gibbs, Maye d'force B with U — 135.1 points over the line in his starts."
- **Decimals.** Player points show 1 decimal place. Team scores show 2.

### The spread rule

Ticket 09 decided it, and Brian changed two points of it during the build. Each team gets at least one headline: a callout, an award, or an arc. The opener is not a headline, because it is about the title race of the whole league. No team holds more than 3 headlines. When a team is #1 in a fourth place, the callout names the next team, and the table still shows every team. Arcs and awards never move, because each is a fact about its team. Only a callout moves.

The build applies the rule before the writer runs. Brian chose the loose rule: a blurb may name a team that the rule moved off a callout, but it must not call that team #1 of that callout. The callout fact of each chapter names the holder and each moved team, so the writer and the verifier know it.

A team with no headline takes the callout where it ranks best from a team that keeps one or more. When no such callout exists, it takes a callout from a holder of 1 headline, and that holder takes another callout in its place. The build does not fail on a break of the rule. When the arcs and the awards of a team alone are more than 3, or no callout can reach a team, the review file names the team in a warning line.

Brian approved this order with the acceptance tests on 2026-11-05.

### The sim replay on the site

Tickets 08 and 13 decided it. A press plays one stored run from the 200. The motion is the Broadcast set of ticket 13: a lower third each week, a red PLAYOFFS wipe, the final standings with the cut and the byes, a bracket that draws in, winners that slide along the lines, and a full champion card. A run lasts about 20 seconds. "Skip to the end" jumps to the final state, and a press during a run starts a fresh run. With reduced motion, each beat fades with no movement. The first press plays a random run of the 200, so two managers see different endings.

The replay takes `sim.json` and nothing of the report. So a weekly page or a standalone page can mount it later.

### The prose and the roast

Ticket 17 decided it. The report's prose blocks go through the writer and the verifier of `facts`, as the weekly report does. Each chapter has one prose block of 40 words or fewer. The separate roast block, its "The roast" heading on the site, and the `roast` field of each chapter in `midseason.json` go.

The **Roast setting** is the voice of the whole paragraph, not a sentence or a block. It is a package value of `midseason` with four levels. The default is `savage`.

- `off`: a sharp, clean sports writer. Lively, with no jabs.
- `warm`: a funny friend in the group chat. It teases all the way through.
- `hot`: a mean columnist. Every sentence has an edge.
- `savage`: a full roast from the first word to the last.

The writer writes each level from scratch, with the facts inside the voice. The prompt holds the rules at every level: no limit on heat for football decisions, nothing about life outside fantasy, no profanity, no slurs, and no starred-out swear words. Its examples are the samples of the P4 Voice board.

- **Facts from the whole report.** The fact sheet of each block holds the facts of its chapter and the facts of the other chapters, so a paragraph can call back across chapters. The verifier checks every number against the whole sheet.
- **Units.** The writer names the unit of a number that a reader can misread, such as points over the line.
- **No count mix.** Head-to-head numbers go with head-to-head records. A CPC record with the median games is a different count.

### The build, the review, and the publish

- `make midseason CLIENT=<slug> WEEK=<W>` builds the report for the week. It refetches each week's transactions and the draft from Sleeper, runs the sim, computes the facts, runs the writer, and writes the draft into the build folder of the season. It can run again at any time.
- The build also writes a review file in the build folder: each blurb with its prose block, the facts it cites, and the verifier result.
- Brian reads the review file. He may edit a blurb in the draft.
- `make midseason-publish CLIENT=<slug> WEEK=<W>` runs the verifier again on each blurb and refuses to publish if one fails. It then copies the two files to the published folder and commits them. It follows the publish rule of the weekly report and stages only the client's season folders.

### The provider

The Sleeper provider gets one more fetch: the draft picks of the season, with the auction amount and the drafter. The fake of the provider port gets the same method (ADR 0015). The weekly transactions fetch exists already. The build calls it for each week.

### The takeover and the home tile

- `midseason.json` holds a takeover end week: the week of the report plus 1. The home page shows the takeover in place of its usual top while the latest published week is at or before that week.
- The takeover shows the opener and a link to the report.
- After the takeover ends, the home page shows a tile with one big fact and a link, in the shape of the R3 tile of ticket 09, for the rest of the season.
- The dock and the menu do not change.

### Timing of the work

The pipeline tickets do not wait. The site tickets wait for the merge of `site-redesign` into `main`, because the report uses the redesign's parts and look.

### New glossary terms

The spec adds these terms to `GLOSSARY.md`:

- **Opener**: the top of the midseason report, the title race. It is not the Hero, which is the top of a manager page.
- **Act**: one of the three parts of the midseason report, each opened by a dark title page.
- **Takeover**: the time when the home page shows the midseason report in place of its usual top.
- **Report tile**: the home tile with one big fact and a link to the midseason report.
- **Spread rule**: each team gets 1 to 3 headlines in the midseason report.
- **Sim run**: one stored season of the sim, which the replay plays.
- **Roast setting**: the voice of a client's report prose, `off`, `warm`, `hot`, or `savage`. Ticket 17 added it.
- **Quick hits**: the block at the end of Act II that holds lineup choices and the injury toll.

## Testing Decisions

A good test checks what a manager or Brian sees: a published file, a rendered page, or a refusal of the publish. It does not check a private function or the order of internal calls. Each test uses real data of the repo or a fixture of the provider port. No test uses a mock mode, and no test patches a port.

The seams, from the highest down. The fewer, the better.

1. **The build of the report, end to end, in the pipeline.** The build runs with the fixture provider and the fake writer on stored CPC and NorCal data. The test checks `midseason.json` and `sim.json`: their shape, the chapter order, and named facts. Examples: the CPC swap diagonal equals the standings, Bo Girds is Snakebit, and the spread rule holds for every team. Prior art: `test_golden.py`, `test_pipeline.py`, and the fakes of `tests/fakes.py`.
2. **The rules of each package.** Each chapter rule has one rule test, `test_rule_<topic>.py` in its package, with small hand-built leagues for the edge cases. Examples: a tie counts half, the self-meet rule, a $0 add is never a miss, Too soon under 2 weeks, the reseed after round 1, and the best and worst schedule of each team with its ties. Prior art: `test_rule_rankings.py` and `test_odds.py`.
3. **The sim parity.** With no bracket, the sim's playoff odds on the stored week 8 data of each client agree with the published weekly odds within 2 points. This guards the draw that lives in two packages.
4. **The writer and the publish.** A blurb with an uncited number makes the publish refuse. A block over 40 words fails the check. The `roast` setting takes all four levels, and the config check rejects any other value. A blurb may cite a fact of another chapter. A clean draft publishes only the client's season folders. Prior art: the verifier tests of `facts` and the publish tests of the week.
5. **The site.** Each Zod schema parses the real published files (ADR 0013). The report route renders from the package fixture at 390 px and 1280 px in the floor tests of Playwright. The replay plays a run, skips to the end, restarts, and honors reduced motion. The home page shows the takeover through the end week, then the tile. The floor tests check the look rules that a test can see: no "The roast" heading, no tag with a fill, and no "All-play" on the page. Prior art: the rankings fixture and the floor project.
6. **The layers.** `test_layers.py` checks that `midseason` and `sim` import only `league` and `facts`.

## Out of Scope

- A weekly rebuild of the report. Brian wants one edited moment per season. The build can run again by hand.
- A report for a season other than 2026. The build takes the season as input, but only 2026 ships.
- The sim on a weekly page or as a standalone page. The sim is a module so this can come later.
- A move of the weekly odds onto the `sim` package. A later spec may do it. The parity test holds the two draws together until then.
- A live sim, on a server or in the browser, and a pick of a game's winner. Ticket 08 chose a replay.
- A dock item for the report.
- An outside ADP source. Each league's own draft is the baseline.
- An injury date finer than the NFL week.
- A comparison of the Trade result with the analyzer's Grade at the time of the trade.
- The fix of the transaction history. The spec `transaction-history` shipped it.
- Players to watch, with Grab him now. Its picks were weak, all bench quarterbacks. A later spec can bring it back with a better rule.
- The four voice levels for all the writing of the site, such as the weekly recaps. It changes the weekly writer, so it is its own spec.
- Easter eggs in the report. Brian does them another time. The gift card code never goes on the site or in the repo.

## Further Notes

- **Missing injury rows.** nflverse had no injury row for A.J. Brown in weeks 2 to 5, so his bust got "just bad". When nflverse has no row, the build counts a week with no snaps and a roster status of out as a missed game. If the cause is not an injury, the tag stays "just bad".
- **The redesign boards.** The rows "Ticket 14 · the report flow", "Ticket 15 · rows and tags", "Ticket 16 · the schedule swap", and "Ticket 17 · the roast in the prose" of the Design canvas show the chosen look with real CPC week 8 data: F1 Lean acts, R1 Quiet text, S3 v2 with text rows, and P4 Voice. The builder matches these boards.
- **The prototypes.** A data run on 2026-11-05 computed every chapter on real CPC week 8 data, with all three spot checks against the site passing. The board row "Ticket 09 · the midseason report" of the Design canvas shows the R2 shape: https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. The prototype code is deleted; the decision tickets hold each rule.
- **The title odds move between runs.** One run gave six teams at 13% to 17%, and another gave five at 13.4% to 16.7%. A blurb cites the count of the published run only.
- **The NFL schedule cache.** The projections through week 17 need the bye weeks from `games.csv`, which git ignores. A build in a fresh worktree must fetch it first.
- **NorCal.** NorCal plays no median game, starts no DEF, and has a fixed bracket. Each rule reads the league settings, so no rule names a client.
