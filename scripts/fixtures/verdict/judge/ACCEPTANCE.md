# Bye week on the manager page: acceptance tests

Spec: `.scratch/bye-week/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. A FAIL of Brian in a PR comment overrides it (ADR 0026).

## Tests

AT-1: The managers file holds the bye week of each listed player
App: pipeline
Stories: 1, 2
Given: the saved week `2026` week 8
When: `make -C apps/pipeline page-json WEEK=8`
Then: each top performer of The Blue Tent in `managers.json` has a `bye_week` number
Evidence: the command output, and the `bye_week` fields of The Blue Tent in `managers.json`.

AT-2: A top performer row shows a coming bye
App: site
Stories: 3
Given: the site built from `2026` week 8
When: the reader opens the manager page of The Blue Tent
Then: the row of a top performer reads "Bye <week>" on one line
Evidence: screenshots of the manager page of The Blue Tent at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-3: The league page shows the bye count of each team
App: site
Stories: 4
Given: the site built from `2026` week 8
When: the reader opens the league page
Then: each team row reads "<n> on bye"
Evidence: a screenshot of the league page at 1280 px.

## Trace

Story 1: AT-1
Story 3: AT-2
Story 4: AT-3
