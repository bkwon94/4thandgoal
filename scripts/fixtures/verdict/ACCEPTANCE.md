# Bye week on the manager page: acceptance tests

Spec: `.scratch/bye-week/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

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

AT-3: Retired. The roster list test moved to AT-2, because the spec dropped the roster list.
App: site
Stories: none

## Trace

Story 1: AT-1
Story 3: AT-2

## Revisions

- 2026-11-03: AT-3 retired.
