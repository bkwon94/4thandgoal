# 06: What does the weekly tile show, and how does the page act in the playoffs and after the season?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** grill

**Blocked by:** 04

**Status:** done

## Question

Brian decides:

1. The one big fact on the tile of each weekly report, and where the tile sits on the page.
2. What the page shows in each playoff week, when only the bracket is left.
3. What the page shows after the final, and whether the Announcement or the tile stops then.

## Decision

Brian, 2026-11-18.

**1. The tile shows Your team's odds.** For example: "58% to make the playoffs. 2 more wins likely gets you in." The tile reads the `page` block of Your team from `sim.json` in the browser, because the week page is the same for each manager and Your team lives only in the browser. With no team set, the tile shows one league fact that the build writes, for example "3 managers fight for the last 2 spots".

**2. The tile sits right after Standings, before Next week.** The week page then reads in order: what happened, where you stand, what you need, and which games decide it. The home page "Playoff race" ladder (`apps/site/src/app/front-door/standings-ladder.tsx`) also gets a link to the sim page.

**3. In the playoff weeks, the page answers for Your team first.** A team still in sees its title odds and its game of this round, with the odds after a win or a loss. For example: "Win and you reach the final. 31% to win it all." A team that is out sees the bracket with the title odds of each team left, under one line: "Out of the playoffs". The tile follows the page: title odds for a team still in, and a league fact for a team that is out, for example "4 teams left, Teehee is the favorite at 38%". "More wins needed" and the median game do not show in the playoffs.

**4. After the final, the page stays as the record of the season.** `/sim/<season>/` shows the final bracket with the champion, with no What-if and no replay. The week 17 report has a tile that shows the champion and links to the page. The Announcement already stops 1 week after the release.

**5. The sim page gets a menu item.** `apps/site/src/app/_routes/sim/menu.ts` returns a link to the page, so it stays one tap away after the Announcement stops. The old comment there says the sim has no page, which is no longer true.

**Out of scope.** A chart of how the odds of each team moved by week, from the past `sim.json` files, is an idea for a later spec. It is a new chart and a new data read for one week of use.
