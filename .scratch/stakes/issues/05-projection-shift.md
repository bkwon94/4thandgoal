# 05 — Projection shift in the score draw

**What to build:** the odds know each team's roster for the weeks ahead. The week fetch saves the
Sleeper per-player projections for weeks N+1 to 14 beside the other raw files, filtered to the
players on any roster. The engine takes, per team and per remaining week, the projected total of
the best lineup from the current roster, built with the existing best-lineup helper. Each drawn
past score then shifts by `PROJECTION_WEIGHT` times the gap between that projected total and the
team's season average. A team with its RB1 out next week draws lower that week. A team with a
bye-free slate of healthy starters draws higher. The facts and the page do not change shape.
Demo: the week 6 sanity run, before and after, side by side.

Spec: `.scratch/stakes/PRD.md`, "The engine" (the projection shift) and "The schedule" (the
projections file).

**Blocked by:** 03 — Odds facts and chapters.

**Status:** done

- [x] The week fetch saves `projections_ahead.json` with weeks N+1 to 14, one entry per week, each with the half-PPR projection per player, only for players on any roster.
- [x] A fetch for week 14 saves one week, and a cached week without the file still parses.
- [x] A parsed week exposes the projections ahead as a dict of week to player id to points.
- [x] A helper gives the projected best-lineup total per roster per remaining week, with the existing best-lineup helper and the league roster slots; a player with no projection that week counts 0.
- [x] The engine takes the projected totals as an input and shifts each drawn score by `PROJECTION_WEIGHT` times the gap between that week's projected total and the team's season average.
- [x] `PROJECTION_WEIGHT = 0.7` joins the tunable table with a one-line why. At 0 the odds equal the odds before this ticket.
- [x] The facts step passes the projected totals to the engine. A rewrite still never calls the engine.
- [x] The week 6 test fixture gains a `projections_ahead.json` built from the live data, weeks 7 to 14, filtered to rostered players.
- [x] Tests: the fetch saves and filters the file; the parse gives 8 weeks for the fixture; the lineup total counts 0 for a missing projection; the engine at weight 0 matches the prior odds on the 4-team fixture; the engine at weight 1 centers a team on its projection; a missing projections file gives no shift.
- [x] Ruff clean on the touched files, the full suite passes.
