# Season sim: a page for each manager's path to the playoffs, with a live What-if

Status: ready-for-agent
Date: 2026-11-18
Apps: all three. The pipeline runs the sim each week, writes `week-NN/sim.json`, and takes the playoff odds from the sim. The API runs a What-if live. The site builds the sim page, the Sim tile, and the Announcement.
Spec branch: `season-sim`.
Source: the map `.scratch/season-sim/MAP.md` and decision tickets 01 to 07. ADR 0037. The prototypes are in `~/plans/season-sim-prototype/`.
Tickets: 01 to 11, in `issues/`.

## Problem Statement

Four regular weeks are left, weeks 11 to 14, then the playoffs in weeks 15 to 17. Each manager asks the same questions each week: can I still make it, what do I need, and what do I root for. The site gives part of the answer in three places. The rankings page shows the playoff odds. The week page shows a swing for the Must Watch games. The midseason report has a replay of one sim run. No page answers the questions for Your team, and no page lets a manager try a result and see the odds move.

The site also has two odds engines of one model: `rankings/odds.py` and the sim package. Sample noise lets two pages show two numbers for one team.

## Solution

Each client gets a sim page at `/sim/<season>/`, which the weekly build rebuilds. The page opens on Your team and answers, in order:

1. How many more wins do I need? A win of the head-to-head game and a win over the median each count.
2. What happens this week? Four results, each with the odds after it.
3. If I lose, what do I root for?
4. Sim it: a replay of the week, or of the rest of the season and the playoffs.

A tap on a result sets a What-if. The API runs the sim live with that result held, and the page updates. The page reads `sim.json` first, so it shows at once and still works when the API is down.

Each week page gets a Sim tile after Standings, with Your team's odds. An Announcement introduces the page to each browser once, in the first week after the release. The sim becomes the one source of the playoff odds, so the rankings page, the week page, and the sim page show one number.

## User Stories

### The sim page

1. As a manager, I want the sim page to open on Your team, so that I see my own odds first.
2. As a manager, I want the header to show my avatar, name, record, the weeks left, and my playoff odds, so that I know where I stand at a glance.
3. As a manager, I want one sentence that says how many more wins I need, such as "Win 6 of the 8 left and you're in", so that I know my target.
4. As a manager, I want the median game to count in that sentence, so that the target matches how my league scores a week.
5. As a manager, I want to tap the sentence and see the full ladder, so that I see the odds and the chance of each count of more wins.
6. As a manager, I want a week switch from the current week to week 14, then Playoffs, so that I can look at one week at a time.
7. As a manager, I want the card of this week to name my opponent, so that I know which game matters.
8. As a manager, I want four tiles for this week, so that I see the odds after a win or a loss, above or below the median.
9. As a manager, I want each tile to show how likely the result is and the wins it adds, so that I can weigh the four results.
10. As a manager in a league with no median game, I want two tiles, so that the card fits my league.
11. As a manager, I want a header that says "If you lose, you drop to X%", so that I know what a loss costs.
12. As a manager, I want up to 3 results of other games to root for after a loss, each with "→ Y%", so that I know which games help me.
13. As a manager, I want a short reason on each root-for row, such as "1 win ahead of you", so that I know why the result helps.
14. As a manager, I want a long team name to wrap or shorten in a root-for row, so that the name of the loser stays readable.
15. As a manager, I want a number with a small sample to show "about", so that I do not trust a noisy number too much.

### The What-if

16. As a manager, I want to tap a result tile to set that result, so that I can see the odds if it happens.
17. As a manager, I want the odds, the sentence, and the root-for list to update after a set result, so that the whole page agrees with it.
18. As a manager, I want the next week to open after I set a result, so that I can set the season one week at a time.
19. As a manager, I want a line at the top that lists each set result, with a Reset, so that I know what the page assumes and can clear it.
20. As a manager, I want each tap to start a new call at once, and a new tap to cancel the call before it, so that the page follows my last tap.
21. As a manager, I want the same set results to give the same numbers each time, so that the page does not flicker between two answers.
22. As a manager, I want a What-if to work with no passphrase, so that I can use it from any link.
23. As a manager, I want the page to still show the odds of the week when the API is down, so that the page never goes blank.
24. As a manager, I want a What-if with no set result to show the numbers of the week, so that the page and the text of the build agree.

### The replay

25. As a manager, I want "Sim week N", so that I can watch one possible week play out.
26. As a manager, I want "Sim the season", so that I can watch one possible rest of the season and the playoffs.
27. As a manager, I want the replay to follow my set results, so that the replay shows a season where my What-if holds.
28. As a manager, I want the replay on one stage that never scrolls, so that I can watch it on a phone.
29. As a manager, I want the season screen to show the standings in the Race style, so that I see only the rows that matter.
30. As a manager, I want the playoff screen to play one round at a time, so that I can follow the bracket.
31. As a manager, I want a champion screen that says where my team finished, so that the replay has an end.
32. As a manager, I want the week replay in two parts, "Games" then "Standings", so that I see the results before the table.
33. As a manager, I want play or pause, Skip, Sim again, and Done in their own row, so that no control covers the stage.
34. As a manager who prefers reduced motion, I want the replay to use fades only, so that the motion does not bother me.

### The playoffs and the end of the season

35. As a manager still in the playoffs, I want my title odds and my game of this round, with the odds after a win or a loss, so that I know what this game means.
36. As a manager in the playoffs, I want to set the result of a bracket game whose teams are set, so that I can try a path to the title.
37. As a manager out of the playoffs, I want the bracket with the title odds of each team left, under "Out of the playoffs", so that I can still follow the race.
38. As a manager after the final, I want the page to show the final bracket and the champion, so that the page is a record of the season.

### The Sim tile and the ways in

39. As a manager, I want a Sim tile on each week page right after Standings, with Your team's odds and what I need, so that I see my number where I read the table.
40. As a manager with no team set, I want the Sim tile to show one league fact, so that the tile still says something true.
41. As a manager in the playoff weeks, I want the Sim tile to show my title odds, or a league fact if I am out, so that the tile fits the week.
42. As a manager, I want the week 17 Sim tile to show the champion, so that the report closes the season.
43. As a manager, I want the Playoff race ladder of the home page to link to the sim page, so that I can go from the odds to the page.
44. As a manager, I want "Season sim" in the menu, so that the page is one tap away from any page.

### The Announcement

45. As a manager, I want an Announcement to introduce the sim page once, so that I learn the feature exists.
46. As a manager, I want the Announcement to show a small live preview of my standings with a What-if chip that I can tap, so that I see what the page does before I open it.
47. As a manager, I want the chip to turn on once by itself after the sheet settles, so that I see the odds move without a tap.
48. As a manager, I want to close the Announcement by a drag down, "Not now", Escape, or a tap on the dim, so that it is easy to dismiss.
49. As a manager, I want a dismiss or a press of its link to hide the Announcement for good in this browser, so that it never comes back.
50. As a manager, I want the Announcement to open only on page load, never while another sheet is open, and never on the sim page, so that it never interrupts me.
51. As a new visitor, I want the Announcement to skip the load where the team picker opens, and show on my next load, so that I see one sheet at a time and still get the note.
52. As a manager, I want the Announcement to stop 1 week after the release, so that the site does not keep old news.
53. As the commissioner, I want the Announcement to be a general component with an art slot, so that the next feature can reuse it.

### The odds engine

54. As a manager, I want one playoff odds number for my team across the rankings page, the week page, and the sim page, so that the site never contradicts itself.
55. As the commissioner, I want the recaps that Claude writes to quote the odds of `sim.json`, so that the text and the page agree.
56. As the commissioner, I want the odds of past weeks to stay as they are, so that the record does not change.
57. As the commissioner, I want one engine for the odds and the swings, so that a change to the model changes one place.

### Speed and cost

58. As a manager, I want a What-if to answer in about 1 to 2 s, so that the page feels live.
59. As the commissioner, I want the API to stay on the machine size it has now, so that the feature costs nothing more.
60. As the commissioner, I want a rate limit for each visitor on the What-if, so that one visitor cannot use up the CPU.
61. As the commissioner, I want the server to stop the work of a cancelled call, so that fast taps do not use CPU on answers nobody reads.

## Implementation Decisions

### The sim package

- The sim package is the one odds engine (ADR 0037). It gives the playoff odds, the bye odds, the seeds, the title odds, and the swing of each game next week. `rankings/odds.py` and its parity test go away.
- The weekly build runs 10,000 runs, in place of the 5,000 of the old engine.
- The draw of the level does not change. A season-ending injury reaches the sim only through the projected best-lineup total, at `PROJECTION_WEIGHT = 0.5`. Sleeper blanks each week of an expected absence, so the projection already sees a long injury (decisions 01 and 03).
- A set result holds one week of Your team: a win or a loss, and above or below the median. The sim holds it with the "Your score first" draw with a weight (decision 07). Your team beats the median exactly when its score is above r6 after a win, or above r5 after a loss, where r1 to r10 are the other 10 scores, high to low. The sim draws Your score cut to its side of that line, then the opponent's score cut to its side of Your score. The weight of the run is the product of the two chances. The weights of set results of other weeks multiply.
- A swing, a pick of the winner of one game, uses the conditional draw with a weight of decision 01. The sim gives a swing by a split of its own runs.
- In a league with no median game, a set result is a win or a loss only.
- In a playoff week, a set result holds the result of a bracket game whose two teams are set. A tie in a bracket game goes to the higher seed, as now.
- One weighted sim per call gives each number of the page by a split of its runs: the ladder, the results of each week, the odds after a loss, and the root-for rows. The sim keeps the fixed seed of `season_sim`, so the same set results give the same numbers on each call.
- The sim returns `effective_runs`, the effective sample size of the weights. A number shows "about" when its chance times `effective_runs` is under 400 runs.
- Each run follows the set results by its draw, so each stored run is a season where the What-if holds. The replay picks a stored run with a chance in proportion to its weight.

### The page block

`sim.json` and the response of the API share one `page` block, so the page reads one shape before and after a What-if. The schema lives in the site schema of the sim package, next to `sim.ts`. The ticket sets the field names. The block holds:

- Your team, its odds, its record, and the weeks left.
- The ladder: each count of more wins, its playoff odds, and its chance. The sentence names the smallest count with playoff odds of 90 % or more.
- For each week left: the opponent, and the four results (two with no median game). Each result holds its odds after, its chance, the wins it adds, and its "about" flag.
- For each week left: the odds after a loss, and up to 3 root-for rows.
- A root-for row holds the winner, the loser, a reason, and the odds after a loss and that result. A row stays only when it lifts the odds by 1 point or more. The rows round to whole points, rank by the lift, and break a tie by the standings. The reasons are "2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you", and "In the race for the last spot".
- In the playoff weeks: the title odds, the game of this round, and the odds after a win or a loss. For a team that is out: the bracket with the title odds of each team left.
- After the final: the final bracket and the champion.

### The weekly build

- The weekly build writes `week-NN/sim.json` in each week folder. It holds `teams`, `sample` (200 stored runs), the inputs of the draw, and a `pages` block with one `page` for each team.
- The sim page reads the latest week. The season file `2026/sim.json` stays as the frozen week 8 file of the midseason report.
- `rankings.json` takes its odds from the sim. The odds of weeks 1 to 10 came from the old engine, and they stay as they are.
- The build writes one league fact for the Sim tile of a manager with no team set. In the regular season, it is the race for the last spots, for example "3 managers fight for the last 2 spots". In the playoffs, it is the favorite, for example "4 teams left, Teehee is the favorite at 38%". After the final, it is the champion.
- The text of the build quotes the odds of `sim.json`: the recaps, the rankings page, and the facts.

### The API

- One What-if route per client. It takes Your team and a list of set results, and it returns `schema_version`, `season`, `week`, `runs`, `effective_runs`, `you`, `set`, `teams`, `sample`, and one `page` block. `teams` and `sample` reuse the schemas of `sim.ts`.
- The route runs on the Tuesday inputs: the inputs of the draw in the latest published `week-NN/sim.json`. It never calls Sleeper. A call with no set result gives the numbers of that file (decision 03).
- The route is a sync `def`, so FastAPI runs it in the thread pool and the event loop does not block.
- The route needs no passphrase. It has its own rate limit for each address, apart from the other routes, as the egg board has. The ticket sets the number, so that a manager who taps fast stays under it.
- The server stops the work of a call whose client went away. The sim checks for a cancel between blocks of runs.
- The API turns on `GZipMiddleware`. The response is about 44 KB gzip with 200 stored runs.
- The API image adds the `sim` package.
- The machine stays `shared-cpu-1x` with 1 GB, at 10,000 runs (decision 03). One call takes about 1.2 to 2.2 s while the burst balance lasts.

### The sim page

- The page is `/sim/<season>/` for each client that takes the `sim` package. It uses layout D, "Cards" (decision 04).
- The header shows Your team: avatar, name, record, the weeks left, and the playoff odds. The sentence of more wins sits under it. A tap opens the ladder.
- A week switch follows: the current week to week 14, then Playoffs. Each week page holds the week card and the root-for card, then "Sim week N" and "Sim the season" in the flow, never fixed over content.
- On a phone, the root-for card opens from one row. From tablet width up, it always shows. At desktop width, the week card sits beside it. On a tablet, the content is capped and centered.
- A tap on a result tile sets that result and opens the next week. A line at the top lists the set results, with a Reset. The page has no grid of every game.
- Each tap starts a call at once. A new tap cancels the call before it. With no set result, the page shows `sim.json` and makes no call.
- In the playoff weeks and after the final, the page acts as the playoff and season-end parts of the page block say.
- The replay is three screens on one stage that never scrolls: Season, Playoffs, and Champion. It opens as a fixed layer under the site header, with a header row, a body, and a control bar in its own row. It uses `100dvh` and the safe-area inset. The season screen uses the Race style of the standings. "Sim the week" plays "Games", then "Standings". Under reduced motion, the replay uses fades only. The full detail is in decision 04.
- The midseason report and its replay stay as they are.

### The Sim tile and the ways in

- The Sim tile sits on each week page, right after Standings and before Next week, for each client that takes the `sim` package.
- The tile reads the `page` block of Your team from `sim.json` in the browser, because the week page is the same for each manager. With no team set, it shows the league fact of the build.
- In the playoff weeks, the tile shows the title odds for a team still in, and the league fact for a team that is out. The week 17 tile shows the champion.
- The Playoff race ladder of the home page links to the sim page.
- The sim package adds a "Season sim" menu item.

### The Announcement

- The Announcement is a general component on the shared `Sheet` of `packages/design`, with `initialFocus="content"` (decision 05). It does not fork the Sheet.
- From top to bottom it holds: an art slot, an eyebrow, a title, one line, the link (the one solid accent control), and "Not now". The use fills the art slot and the copy. The site name comes in as a prop (ADR 0012).
- The copy of the sim: "New: Season sim", "See your path to the playoffs", "Pick this week's results and watch your playoff odds move.", "Open the sim", and "Not now".
- The art of the sim: Your team's name and playoff odds, three standings rows (the team above Your team, Your team, and the team below) with the playoff line, and a What-if chip, "What-if: <team> win both". The chip is a button. A tap turns it on or off, and the odds count to the new number. The chip turns on once by itself, after the sheet settles. The numbers come from `sim.json`.
- It opens about 0.7 s after page load. It does not open while another sheet is open, on the page it links to, or while no team is set.
- A dismiss or a press of its link hides it for good in this browser. A skipped open does not count, so it shows on the next load.
- It stops 1 week after the release. Each Announcement has an id and an end date.
- Under reduced motion, the rows and the odds show at once, with no count and no automatic chip.

### Copy

- Write "manager" or "another manager", never "rival".
- Never name Brian. Write "the commissioner" if needed.
- Never show the words Jev, Advisor, Finder, or front door.

## Testing Decisions

A good test checks the behavior at a seam, with real inputs, and never the inner steps. The spec uses the highest seam that each app has.

1. **The sim package seam.** Call the sim with the inputs of a league and a list of set results, and read the page block. Tests:
   - Each set result agrees with an exact rejection reference on a small league, within the gaps that decisions 01 and 07 measured.
   - The same inputs give the same output.
   - The ladder sentence, the four results, the odds after a loss, and the root-for rules give the expected rows on a fixture league.
   - The "about" flag turns on under 400 effective runs.
   - The playoff page and the season-end page have the right shape.
   - The cases of the old odds test that still apply move to the sim: the odds, the status, the seed, and the swing.
   - Prior art: `packages/sim/python/tests/test_season.py` and `apps/pipeline/tests/test_odds.py`.
2. **The weekly build seam.** Run the build step of the sim on a saved week, and read `week-NN/sim.json` and `rankings.json`. The file holds a page for each team, and the rankings odds equal the odds of the sim. Prior art: `apps/pipeline/tests/test_sim.py`.
3. **The API seam.** Call the What-if route over HTTP with the FastAPI test client. Tests: the response shape, no passphrase needed, a 429 past the limit, a gzip response, a 422 on a bad set result, and a call with no set result that equals the page of the file. Prior art: `apps/api/tests/test_api.py` and `apps/api/tests/test_eggs.py`.
4. **The site component seam.** Render the sim page, the Sim tile, and the Announcement from a fixture `sim.json` in Vitest with jsdom. Tests: the parts of the page, the week switch, a set result with a stubbed API answer, the Reset, the Sim tile with and without a team, and each rule of the Announcement. Prior art: `packages/sim/site/replay/*.test.tsx`.
5. **The browser seam.** Run Playwright WebKit on the built site at 390x660 (iPhone 15), 810x980 and 1080x740 (iPad), and 1280x800. Check each screen of the page, the replay, the Sim tile, and the Announcement. Assert that no text overlaps other text and no bar covers content. Prior art: `apps/site/e2e/floor.spec.ts`.
6. **The live seam.** Time real What-if calls on Fly after the deploy, and again just after a later deploy. Record the times. If the calls are slow, the spec decides then (decision 03).

## Out of Scope

- A TypeScript copy of the sim in the browser. The API runs the one Python copy, so no parity test is needed.
- A change to the midseason report. It is a published one-time page.
- A set result of a bracket game whose teams are not set. A tree of choices is hard to show on a phone.
- A record of a dismissed Announcement on the server. The site has no accounts.
- A grid to pick any game of any week. The job of the page is what Your team needs.
- A cache of live sim answers. The cost is under 10 minutes of CPU each week.
- A bigger API machine. The shared machine is enough, and Brian wants no extra cost.
- A refetch of the injuries and the projections from Sleeper on a What-if.
- A lower level for a team with a season-ending injury.
- A chart of how the odds of each team moved by week, after the final. Keep it for a later spec.

## Further Notes

- Brian wants the release about the week of 2026-11-18, so the page is live for most of weeks 11 to 14.
- The prototypes and their screenshots are in `~/plans/season-sim-prototype/`: `final/` for the page and `announcement/` for the Announcement.
- The glossary term What-if changes with this spec. Decision 04 made a What-if a set of results of Your team, not a set of game winners.
- The glossary gets the term Sim tile.

**Calls I made without Brian.** Check these with the spec.

1. A What-if sets only the results of Your team. The root-for rows do not take a tap. Decision 04 says "the page has no grid of every game", but it does not say if a root-for row is a button.
2. The API reads the inputs of the draw from the latest published `week-NN/sim.json`. That file already holds them, and it pins the Tuesday inputs of decision 03.
3. The replay picks a stored run with a chance in proportion to its weight.
4. Decision 05 leaves open what the Announcement does on a later load with no team set. The spec says it does not open until a team is set, and that load does not count as seen.
5. The term "Sim tile" for the tile of the week page. "Report tile" already names the home tile of the midseason report.
