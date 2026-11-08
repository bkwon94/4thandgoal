# 07: Which heroes get a scene, and what each scene shows

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

Decision 06 proved the scene on the Matchup of the Week and on the manager hero. Which other heroes get a scene, and what does each one show?

The six hero slots cover all 11 heroes, with or without a scene. This ticket decides the art only.

## Decision

Brian decided on 2026-11-07, in the session after decision 06.

| Hero | Scene | What the lights show |
| --- | --- | --- |
| Matchup of the Week, on the home page and on the week page | Yes | The scene of decision 06: 12 teams by the points of the week, the median, and the two teams of the Matchup in red. |
| Manager hero | Yes | The scene of decision 06: one light per played week, bright for a win, dim for a loss, and the median of each week. |
| Power rankings, the top of `/rankings` | Yes | 12 lights in the order of the power rank, each at its playoff odds. The rank-1 team flares red and carries the label at rest. |
| Analyzer form, the top of `/analyze` | Yes | Before a trade, the lights drift and do not settle. When the verdict arrives, they settle into two groups, one per side of the trade. The bigger group sits on the side that gets more. |
| Midseason opener and takeover | Yes | 12 lights at the season total points, settled in the order of the standings. |
| 404 | Yes | A scatter of lights that drifts and never settles. |
| Analyzer result | No | It shows on the same page as the analyzer form, so the scene of the form covers it. |
| Each act title of the midseason report | No | An act title is a break inside the report, not the first hero of a page. |

The `scene` prop on `Hero` takes the data of a scene. A hero with no `scene` keeps the static grid. The page sets it on its first hero only.

The scene of the analyzer form changes state with the response of the API, so it is the largest scene. The spec puts it in the last ticket, so it can leave the spec alone. If it leaves, the analyzer form takes the drift of the 404 with no settle.

The session first placed the power-rankings hero on the home page. That was wrong: its hero is the top of `/rankings`, in `packages/rankings/site/chapters/rankings-screen.tsx`.
