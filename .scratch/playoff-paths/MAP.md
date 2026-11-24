# Playoff paths: map

App: both.
Spec branch: `playoff-paths`.

## DESTINATION

The sim page gives each team its paths to each Goal: a playoff spot, a bye, or one seed. For each week left, it shows the results, the Score to beat, and every other game to root for, each with its odds. A League board on the same page shows the Clinch lines of all teams. An Announcement and the front door push each manager to the page.

## DECISIONS SO FAR

- The spec extends the sim page of `season-sim`, not a separate page. A redesign of the page is allowed. Brian, 2026-11-24, grill Q1.
- Each new part uses ui-sdk through its wrapper (ADR 0037). A part that `@ui-sdk/react` does not ship, such as a bar chart of the odds of each team, comes from `@ui-sdk/core`. Each part gets a detailed brief: how it looks, how it feels, and what it does. Brian, Q1 and Q11.
- The page answers three Goals: a playoff spot (seeds 1 to 6), a bye (seeds 1 and 2), and one seed that the manager taps. It opens on the best Goal with real odds. Clinched and Out extend to each Goal, by a plain check on wins. Brian, Q2.
- The sim already gives the odds of each seed and each final win total, so the Goals need no new sim model. Fact, `packages/sim/python/src/sim/season.py`.
- The Score to beat shows the score that beats the opponent and the median, at 50% and at 80%. The tiebreak gap on points shows only when it is close, such as within 1 win and 50 points of the Goal. Brian, Q3.
- The root-for list shows all other head-to-head games of the week, ordered by the move of the odds of the Goal, each result with "→ Y%". A game that moves the odds by less than 1 point is gray and marked "Doesn't matter". The list follows each of the results of Your team. Median rooting shows only for the 1 or 2 teams that matter most. Brian, Q4.
- The Finish list is the main view: each final record from here with its odds of the Goal. Each Finish shows its top Paths. Brian, Q5.
- A tap on a Finish or a Path opens its Week plan: one row per week left with the results, the Score to beat, and the 1 or 2 games to root for. "Try it" sets the results of Your team as a What-if. The plan picks the most common order of the results, and says "any 5 of 6 works" when the order does not matter. Brian, Q6.
- The build writes the Finish list, the Paths, and the Week plans with no set result into `sim.json`. The API finds them again after a What-if. If the cost on Fly is too high, the fallback is no Paths after a What-if. Brian, Q7.
- The spec ships as soon as possible, as one spec, with no fixed date. Brian, Q8.
- The words are Goal, Finish, Finish list, Path, Week plan, Score to beat, League board, and Clinch line. "Ladder" and "Target" already have other meanings. Brian, Q9.
- The League board is in scope: a view on the sim page beside Your team. It has one row per team in standings order, with the odds of each Goal and the Clinch lines of this week. A tap on a row opens the Finish list and Paths of that team. Brian, Q10 and Q11.
- The release gets an Announcement that links to the sim page, and the front door pushes visitors to the page. Brian, Q11.
- NorCal has no median game, so the page must fit 2 results per week and a 3-0 to 0-3 Finish list. Fact, `clients/norcal/data/2026/league.json`.
- Sleeper seeds by record (median counted), then Points For, then the higher Points Against, then a coin flip. The sim lacks Points Against, so the spec adds it as the third key in all three sort places, with `rid` for the coin flip. Tied games stay out. `decisions/02-research-tiebreak-rules.md`.
- The page takes the name "The Race", short label "Race". The route `/sim/<season>/` and the package name `sim` stay. `decisions/01-grill-the-page-name.md`.
- Paths come from a greedy cover that stops at 90% or 3 teams, with a floor of 400 runs. Clinch lines come from an exact count in the weekly build. The API keeps Paths after a What-if on `shared-cpu-1x`, with a sim loop that writes each run's results, near 2.0 to 2.1 s on Fly. `sim.json` takes the small shape, about 44 KB gzip. `decisions/03-research-path-search-cost.md`.
- Variant D: the Goal switch, the Your team card that opens in place with the Finish list and the week card, and the League board as one bar chart. Ink bars, the accent only for Your team. A pill only for Clinched (green, names the best Goal) and Out (red). Each part from `@ui-sdk/react`, the bar chart from `@ui-sdk/core`. `decisions/04-prototype-the-page-redesign.md`.
- The playoff race Topic is the first Suggestion of the front door until week 14 is final. Its Answer adds the top 3 Finishes, the status pill, and "Open The Race". `decisions/05-grill-the-front-door-push.md`.

## NOT YET SPECIFIED

- How does The Race show live team names, and on which pages? `decisions/07-grill-live-team-names.md`.
- What is the copy of a Path, a Week plan, and a Clinch line? `decisions/06-grill-path-and-clinch-copy.md`.

## OUT OF SCOPE

- The rank of a tied game in the seeds. No stored week has one, and Sleeper does not document it.
- Paths in the playoff weeks. A bracket plays one game at a time, so the bracket view of `season-sim` stays.
- A Path of 4 or more teams in full. The row shows "and 2 more results", because a long Path is hard to read on a phone.
- Notifications, such as "your Path is alive". The site has no push channel.
