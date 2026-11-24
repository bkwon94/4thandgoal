# The Race: each team's paths to a playoff spot, a bye, or a seed, and a League board of every team

Status: ready-for-agent
Date: 2026-11-24
Apps: all three. The pipeline finds the Finishes, the Paths, the Week plans, the Score to beat, and the Clinch lines, and writes them into `week-NN/sim.json`. It also pins the playoff race Topic as the first Suggestion. The API finds the same parts again after a What-if. The site redesigns the sim page as The Race, adds the League board, adds live names on every page, and shows an Announcement.
Spec branch: `playoff-paths`.
Source: the map `.scratch/playoff-paths/MAP.md` and decision tickets 01 to 07. ADR 0037 (the sim is the one odds engine, and each new interactive part uses ui-sdk). The prototype is on the branch `playoff-paths-prototype`, with a copy in `~/plans/playoff-paths-prototype/`.
Tickets: 01 to 10, in `issues/`.

## Problem Statement

Three regular weeks are left, weeks 12 to 14. Each manager asks: what must happen for me to make the playoffs, get a bye, or reach a seed? The sim page answers part of it. It gives the more wins you need, the four results of this week, and up to 3 games to root for after a loss. It does not say what score you need, which of the other games matter, or what help you need from the other teams over the rest of the season.

A manager at 11-11, outside the playoff spots, sees only a low percent. They do not see that "win 2 of 3 and beat the median twice, and Omarion Himpton ends 14-14 or worse" still gets them in most of the time. No page shows every team's race at once, so a manager cannot see who clinches or goes out this week.

The site also shows team names from the Tuesday fetch. A manager who renames a team on Wednesday keeps the old name on every page for up to a week. Week 11 shows "Puka Deez..." for a team that Sleeper now calls "Teez Nuts".

## Solution

The sim page becomes **The Race**, at the same route `/sim/<season>/`. It opens on one Goal at a time: a playoff spot, a bye, or one seed. In order, it shows:

1. The Goal switch: Spot, Bye, or Seed with a seed picker.
2. The Your team card, which opens in place. It holds the Finish list, a bar for each final record with its odds of the Goal. A tap on a Finish shows its Paths, and a tap on a Path opens its Week plan with "Try it". Then the week card: the Score to beat, the four results, and every other game of the week to root for.
3. The League board: one bar per team with its odds of the Goal, a status pill for Clinched or Out, and the Clinch lines of this week. A tap on a team opens its own Finish list and Week plan.

A What-if from "Try it" or a result tile reruns the sim on the API, and every part updates. Every page except the midseason report shows live team names and avatars from Sleeper. An Announcement and the front door push each manager to The Race.

## User Stories

### The Goal

1. As a manager, I want to choose a Goal of a playoff spot, a bye, or one seed, so that I see my odds of what I aim at.
2. As a manager, I want the page to open on the best Goal that I can still reach with real odds, so that I see the race that matters to me first.
3. As a manager in first place, I want the page to open on the bye, so that I do not read a playoff spot that I have nearly locked.
4. As a manager, I want a seed picker from 1 to 6, so that I can see what I need for a specific seed.
5. As a manager, I want every part of the page to follow the Goal I choose, so that the Finish list, the Paths, the board, and the root-for list agree.
6. As a NorCal manager, I want the page to fit a league of 6 spots with no median game, so that the numbers match my league.

### The Your team card

7. As a manager, I want the card to show my avatar, name, record, the odds of the Goal, and my status pill, so that I see where I stand at a glance.
8. As a manager, I want the card to open in place, not in a sheet, so that my own answer stays on the page with the board.
9. As a manager, I want to make any team Your team from its sheet, so that I can use the page on a new browser.

### The Finish list

10. As a manager, I want one bar for each final record from here, such as 6-0 to 0-6, so that I see the odds of the Goal at each record.
11. As a manager, I want each Finish to show how likely it is and the final record it gives, such as "ends 15-13", so that I know which Finishes are real.
12. As a manager, I want the median results to count in each Finish, so that the Finish matches how my league scores a week.
13. As a NorCal manager, I want a Finish list of head-to-head games only, so that it matches a league with no median.
14. As a manager, I want "You're in whatever the others do." on a sure Finish, so that I know I need no help at that record.
15. As a manager, I want "No way in at this record." on a Finish under 0.5%, so that I do not chase a false hope.

### The Paths

16. As a manager, I want a tap on a Finish to show its Paths, so that I see what help I need at that record.
17. As a manager, I want each Path to name up to 3 other teams by the final record they must end at or below, such as "Omarion Himpton ends 14-14 or worse", so that I read it like the standings.
18. As a manager, I want each Path to say how likely it is and my odds if it happens, such as "Happens 17% · you're in 99%.", so that I can weigh each Path.
19. As a manager whose Finish has no Path that reaches 90%, I want the best Path under the header "Best chance", so that I know it is not a sure thing.
20. As a manager, I want no repeated Path, so that the list is short and plain.

### The Week plan

21. As a manager, I want a tap on a Path to open its Week plan, so that I know what must happen each week.
22. As a manager, I want one row per week left, with my result, the Score to beat, and the games to root for, so that each week has a clear job.
23. As a manager, I want the header "Your plan to 15-13 · you're in 81%", so that I know where the plan ends and what it gives me.
24. As a manager, I want the line "Any 4 wins of your 6 work. This is the most common order." when the order does not matter, so that I do not think one order is required.
25. As a manager, I want "Try it" to set the results of my plan as a What-if, so that I can see the live odds of the plan.
26. As a manager, I want a loss in the plan to read "Lose, but beat the median" or "Lose and miss the median", so that a loss in the plan is plain.

### The week card

27. As a manager, I want the Score to beat my opponent and the median, "Score 109 to win, 127 to be sure", so that I know the points I need this week.
28. As a manager, I want "to be sure" to mean an 80% chance, so that I have a safe target too.
29. As a manager, I want the four result tiles with the odds of the Goal after each, so that I can weigh this week's results.
30. As a manager, I want a tap on a result tile to set it as a What-if, so that I can see the rest of the season after that result.
31. As a manager, I want every other head-to-head game of the week in the root-for list, not only the top 3, so that I know who to root for in each game.
32. As a manager, I want the root-for list to follow the result I choose, including a win, so that I know who to root for in each case.
33. As a manager, I want each root-for row to show both results with their odds, "Immaculate Concepcion beats Bengals Buddies → 55%" and "Bengals Buddies wins → 47%", so that I see the cost of each result.
34. As a manager, I want a game that moves my odds by less than 1 point to show a gray "Doesn't matter" tag, so that I can ignore it.
35. As a manager, I want median rooting only for the 1 or 2 teams that matter most, "Bo Girds misses the median → 58%", so that the list stays short.
36. As a manager, I want the tiebreak gap on points when it is close, so that I know when my points can decide a tie.

### The League board

37. As a manager, I want one bar per team in odds order for the Goal, so that I see the whole race in one look.
38. As a manager, I want my own bar in the client accent and every other bar in ink, so that I find my team at once.
39. As a manager, I want a quiet green pill for a team that has Clinched, naming the best Goal it has locked, so that I see who is safe.
40. As a manager, I want a quiet red pill for a team that is Out, so that I see who is done.
41. As a manager, I want no pill for a team In the hunt, so that the pills stand out as teams lock in.
42. As a manager, I want a Clinch line under a team when a result this week clinches a Goal or ends it, such as "Clinches a spot with a win, a median win, and a Teez Nuts loss to Bo Girds.", so that I know what to watch this week.
43. As a manager, I want each Clinch line to name the Goal of the view, so that "Clinches a bye" and "Clinches a spot" are not mixed.
44. As a manager, I want a Clinch line to name at most 2 other results, then "and 1 more result", so that it fits a phone.
45. As a manager, I want a tap on another team to open its Finish list and Week plan in a sheet, so that I can see the race of any team.
46. As a manager, I want no Clinch line on a Seed Goal, so that the board stays readable.

### The What-if

47. As a manager, I want a What-if to update the Finish list, the Paths, the Week plans, the week card, and the board, so that the whole page agrees with it.
48. As a manager, I want a line that lists what is set, with a Reset, so that I know what the page assumes.
49. As a manager, I want the page to show the numbers of the week when the API is down, so that the page never goes blank.
50. As a manager, I want the same set results to give the same numbers each time, so that the page does not flicker.

### Live names

51. As a manager, I want every page to show the team names that Sleeper shows now, so that a renamed team is right everywhere.
52. As a manager, I want a changed avatar to show too, so that each team looks as it does on Sleeper.
53. As a manager, I want the old name in a blurb or a fact to change to the new name, so that a row and its blurb agree.
54. As a manager, I want the page to show at once with the published names and change only a renamed team, so that the page never waits on Sleeper.
55. As a manager, I want the page to keep the published names when Sleeper is down, so that I see no error.
56. As a reader of the midseason report, I want its names to stay as published, so that the report stays a record of its week.

### The ways in

57. As a manager, I want the menu item and the short label to read "The Race" and "Race", so that the name matches the page.
58. As a manager, I want an Announcement once in each browser after the release, "The Race is on", so that I find the page.
59. As a manager on the front door, I want the playoff race Suggestion first each week until week 14 is final, so that the race is the first thing I can ask about.
60. As a manager, I want the race Answer to show my top 3 Finishes, my status pill, and "Open The Race", so that I get the short answer in chat and the full page in one tap.
61. As a manager, I want the Sim tile of each week page to link to The Race, so that I reach it from the week.

### The tiebreak

62. As a manager, I want the sim to order tied teams the way Sleeper does, by Points For, then the higher Points Against, so that a Finish and a Path match the real seeds.

### The playoffs

63. As a manager in a playoff week, I want the page to keep the bracket view of the season sim, so that the page still works after the race ends.

## Implementation Decisions

### The sim package: the tiebreak

- The order of the standings is wins with the median game counted, then Points For, then the higher Points Against, then the roster ID as a fixed stand-in for Sleeper's coin flip (decision 02).
- The new key goes into all three places that sort teams now: the seed order of the season draw, the order of the page block, and the order of the standings table. The records of a team gain Points Against.
- The case of NorCal week 8 is the test: rosters 1 and 9 tie at 5-3 with 1010.86 Points For, and Sleeper seeds roster 9 higher.
- A tied game is out of scope. The order assumes no tied games.

### The sim package: the Goals and the status

- A Goal is a playoff spot (seeds 1 to the playoff spots), a bye (seeds 1 to the bye count), or one seed N. The sim already counts each seed in each run, so each Goal is a split of the runs.
- The open Goal of a team is the best Goal it can still reach with odds of 5% or more, in the order 1 seed, bye, spot. The 5% bar is a call made without Brian; see Further Notes.
- The status of a team for a Goal is Clinched, In the hunt, or Out, by the plain check on wins (the glossary terms Clinched and Out) for that Goal. For a bye or a seed, the check uses the wins of the last seed of the Goal.
- The best Clinched label names the highest Goal locked: "Clinched 1 seed", then "Clinched bye", then "Clinched spot".

### The sim package: the Finish list, the Paths, and the Week plan

- A Finish is the count of wins of a team in the results left, with the median results counted. Each Finish has its chance and its odds of the Goal. Its final record is the current record plus the Finish.
- The Paths of a Finish come from a greedy cover over the runs of that Finish (decision 03). The cover adds the condition on another team that lifts the odds most, as "team X ends at most k wins", and stops when the odds reach 90% or the Path names 3 teams. A Path needs 400 runs or more. The top Paths of a Finish skip a Path with the same conditions as one before it.
- A Finish with odds of 99.5% or more has no Path. A Finish under 0.5% has no Path. A Finish whose best Path stays under 90% keeps that one Path, marked as the best chance.
- A Week plan belongs to one Path. It picks the most common order of the results of Your team in the runs of the Path, and it marks "any order" when no order holds more than a share that the ticket sets. Each row holds the week, the result, the Score to beat, and the 1 or 2 games to root for in that week, ranked by the lift. It also holds the odds of "Try it": the What-if odds of those results.
- The sim loop writes the results of each run as it draws them, so the Path search does not read the stored runs again (decision 03).

### The sim package: the week card

- The Score to beat holds two scores against the opponent and two against the median: the score with a 50% chance and the score with an 80% chance, from the score draws of the runs.
- The root-for list holds every other head-to-head game of the week, for each of the four results of Your team. Each row holds the winner, the loser, and the odds of the Goal after each result. A row whose lift is under 1 point is marked "doesn't matter". The rows round to whole points, rank by the lift, and break a tie by the standings, as now.
- The median rooting holds the 1 or 2 other teams whose median result moves the odds most, with the odds after a miss.
- The tiebreak gap shows when another team is within 1 win and 50 points of Your team at the edge of the Goal.

### The sim package: the Clinch lines

- The Clinch lines come from an exact count of every set of results of this week, in the weekly build only (decision 03). For each team and each Goal but a seed, the count finds the sets that make the team Clinched or Out by the plain check.
- A line shows the most likely set, names at most 2 results beyond the team's own, and adds "and N more results" past that. The sheet lists every set.
- cpc has 9,024 sets of results and takes 1.3 s. NorCal has 64.

### The page block and `sim.json`

- The page block of `season-sim` grows. For each team it holds the open Goal, the status of each Goal, and, for the spot and bye Goals, the Finish list with its Paths and Week plans. For each seed it holds the Finish list only, with a Week plan for each Finish, which keeps `sim.json` near 44 KB gzip at cpc week 10 (decision 03). The ticket sets the field names.
- A new `board` block holds, for each team: the odds of each Goal, the status of each Goal, and the Clinch lines of this week.
- The API response and `sim.json` share both blocks, so the page reads one shape before and after a What-if. The response holds no Clinch lines, because they come from the build only.

### The API

- The What-if route of `season-sim` returns the grown page block for Your team and the board odds after the set results. It still reads the Tuesday inputs and never calls Sleeper.
- The machine stays `shared-cpu-1x` at no extra cost. A What-if at cpc week 10 must stay at or under 2.5 s on Fly, the bar of AT-22 of `season-sim`. If it does not, the first fallback finds the Paths only for the Goal on screen, and the second shows no Paths after a What-if.

### The Race page

- The page keeps the route `/sim/<season>/` and the package name `sim`. Its title is "The Race", and its short label is "Race" (decision 01).
- The layout is variant D of the prototype (decision 04): the title line, the Goal switch, the Your team card that opens in place, then the League board.
- The Goal switch is a `SegmentedControl` from `@ui-sdk/react`, with the seed picker as a `ToggleGroup`.
- The Your team card opens with a `Collapsible`. Open, it shows the Finish list, then the week card.
- The Finish list and the League board use one new bar chart part built from `@ui-sdk/core` and kept in `packages/design`. It has one tab stop and arrow keys between bars. Each bar is ink at 80% strength. Only Your team's bars take the client accent.
- A tap on a Finish shows its Paths in place. A tap on a Path opens the Week plan in a `Sheet`. A tap on another team opens its Finish list in a `Sheet`, and its Week plan sheet stacks on it.
- The four result tiles are a `ToggleGroup`. A tap sets a What-if and starts a call at once. A new tap cancels the call before it. A line at the top lists what is set, with a Reset, as now.
- The status pill is a quiet tint with text: green for Clinched, red for Out. The design package gains the green and red tint tokens, checked at 4.5:1 or more in light and dark mode. Light mode keeps the gray `page` behind white `card`.
- The replay of `season-sim` stays. "Sim week N" and "Sim the season" sit at the end of the Your team card, in the flow. The week switch of `season-sim` goes, because the Week plan covers the later weeks. This is a call made without Brian; see Further Notes.
- In the playoff weeks and after the final, the page shows the bracket view of `season-sim`, with no Goal switch and no League board.
- Each new part follows the design bar: transitions-dev, scrolltide, apple-design, animate, critique, and polish. Under reduced motion, every change is a fade or none.

### The copy

The copy of decision 06 holds in full. In short:

- A Path condition: "Omarion Himpton ends 14-14 or worse."
- A Path: the Finish line "4-2 · ends 15-13 · 26% likely", the conditions as "If …, …, and …", then "Happens 17% · you're in 99%."
- A Finish: "You're in whatever the others do.", a Path, "Best chance" with a Path, or "No way in at this record."
- A Week plan: the header "Your plan to 15-13 · you're in 81%", the order line, and rows such as "Win and beat the median." and "Score 109 to win, 127 to be sure. Score 108 to beat the median, 114 to be sure."
- A Clinch line: "Clinches a spot with a win and a median win.", "Out with a loss and a median miss.", "Out with any loss."
- A number shows "about" under `ABOUT_RUNS`. A Path never does.
- Write "manager" or "another manager", never "rival". Never name Brian. Never show Jev, Advisor, Finder, or front door.

### Live names

- One shared part of the site reads two public Sleeper calls in the browser: the rosters of the league, for the owner of each roster, and the users of the league, for each team name and avatar (decision 07). Both allow any origin.
- The page renders the published names first. When the calls return, the part swaps each renamed team in place, with no animation: in each name slot, and on each full old name in the text of the build, such as blurbs, facts, and front door Answers. It swaps only a team that the calls show as renamed.
- A changed avatar loads from Sleeper's CDN. The local image stays until the new one loads.
- The browser keeps the live names for 5 minutes in `sessionStorage`. A failed call or a wait over 3 seconds keeps the published names, with no error.
- Every page with a team name uses the part: the week page, rankings, managers, the front door, the analyzer, and The Race. The midseason report does not.
- A component still takes data and returns markup (ADR 0012). The part sits at the data edge of each page and hands the names down.

### The front door

- The playoff race Topic is the first of the 3 Suggestions in each week of the regular season, for every manager (decision 05). The pin stops when week 14 is final.
- The race Answer keeps its odds and its near rows. It adds Your team's top 3 Finishes for a playoff spot, the status pill, and the link "Open The Race".

### The Announcement and the ways in

- The general Announcement of `season-sim` introduces The Race once in each browser, for 1 week after the release.
- The copy: the eyebrow "New: The Race", the title "The Race is on", one line, "See what you need each week, and who to root for.", the link "Open The Race", and "Not now". The art shows the League board rows around Your team, with its pill. The copy past the title is a call made without Brian.
- The menu item reads "The Race", and the Sim tile of each week page reads "The Race".

### The glossary

The spec uses the terms The Race, Goal, Finish, Finish list, Path, Week plan, Score to beat, League board, Clinch line, In the hunt, and Live name, all added on the spec branch.

## Testing Decisions

A good test checks the behavior at a seam, with real inputs, and never the inner steps. The spec uses the seams of `season-sim` and adds one for live names.

1. **The sim package seam.** Call the sim with the inputs of a league and a list of set results, and read the page block and the board block. Tests:
   - The tiebreak orders NorCal week 8 as Sleeper did, and the other stored brackets still match.
   - Each Goal gives the odds of its seeds. The status of each Goal follows the plain check, also for a bye and a seed.
   - The Finish list sums to 100% and gives the right final records, with and without a median game.
   - A Path reaches 90% or names 3 teams, has 400 runs or more, and never repeats. A sure Finish and a Finish under 0.5% have no Path.
   - A Week plan gives its results in the most common order, and "Try it" odds equal a What-if of those results.
   - The Score to beat and the root-for list give the expected rows on a fixture league, with "doesn't matter" under 1 point.
   - The Clinch lines of a fixture week agree with a brute-force check.
   - Prior art: `packages/sim/python/tests/test_season.py`.
2. **The weekly build seam.** Run the sim step of the build on the saved cpc week 11 and NorCal week 10, and read `week-NN/sim.json`. The file holds a page for each team and the board, and its size stays under the note in the tunables. Prior art: `apps/pipeline/tests/test_sim.py`.
3. **The Topic seam.** Build the Suggestions and the race Answer for a fixture week. The race Topic is first in a regular week and ranks as usual after week 14. The Answer holds the top 3 Finishes, the pill, and the link. Prior art: `apps/pipeline/tests/test_topics.py` and `apps/api/tests/test_suggestions.py`.
4. **The API seam.** Call the What-if route over HTTP with the FastAPI test client. The response holds the grown page block and the board odds, and a call with no set result equals the page of the file. Prior art: `apps/api/tests/test_api.py`.
5. **The site component seam.** Render The Race, the Sim tile, the menu, and the Announcement from a fixture `sim.json` with `bun test` and happy-dom (ADR 0038). Render the live names part with a stubbed `fetch`: a renamed team swaps in a slot and in text, an unchanged team does not, a failed call keeps the published names, and the cache serves a second page. Prior art: `apps/site/src/app/_routes/sim/your-sim-page.test.tsx`.
6. **The browser seam.** Run Playwright WebKit on the built site at 390x660, 810x980, 1080x740, and 1280x800, in light and dark mode. Check each state of The Race, the sheets, and the Announcement, with the overlap assert. Prior art: `apps/site/e2e/floor.spec.ts`.
7. **The live seam.** Time real What-if calls on Fly after the deploy of the merged branch, at cpc week 11. Record the times against the 2.5 s bar. Never deploy an unmerged branch to Fly for evidence; use the local evidence API.

Brian checks these seams with the spec.

## Out of Scope

- Paths in the playoff weeks. A bracket plays one game at a time, so the bracket view of `season-sim` stays.
- A Path of 4 or more teams in full. The row shows "and N more results", because a long Path is hard to read on a phone.
- Notifications, such as "your Path is alive". The site has no push channel.
- The rank of a tied game in the seeds. No stored week has one, and Sleeper does not document it.
- Clinch lines after a What-if. They come from the build only.
- Live names in the midseason report. It is a record of one week.
- Live scores, injuries, or projections. Only the names and the avatars are live.
- A bigger API machine. Brian wants no extra cost.

## Further Notes

- Brian wants the release as soon as possible. Week 12 starts Thursday 2026-11-26, and the race ends after week 14.
- Decision 03 measured on the Mac under load. The Fly time is an estimate from the measured 1.73 s of AT-22 of `season-sim`, so the live seam must measure it.
- The prototype data showed that with 2 weeks left after this one, 10 of 12 cpc teams are In the hunt and few Clinch lines exist. The board shows more pills and lines as the weeks pass.
- The prototype worktree `.claude/worktrees/playoff-paths-prototype` and its dev server on port 3311 stay up until Brian says to remove them.

**Calls I made without Brian.** Check these with the spec.

1. The open Goal is the best Goal with odds of 5% or more, in the order 1 seed, bye, spot.
2. The week switch of `season-sim` goes, because the Week plan covers the later weeks. The replay buttons stay at the end of the Your team card.
3. The line and the art of the Announcement: "See what you need each week, and who to root for.", with the board rows around Your team.
4. The page shows no Goal switch and no League board in the playoff weeks.
5. A What-if updates the odds on the League board, but not its Clinch lines.
