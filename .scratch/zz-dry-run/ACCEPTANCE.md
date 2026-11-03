# Bye week on the manager page: acceptance tests

Spec: `.scratch/zz-dry-run/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

## Tests

AT-1: The managers file holds the bye week of each listed player
App: pipeline
Stories: 1, 2, 4
Given: the saved week `2026` week 8
When: `make -C apps/pipeline page-json WEEK=8`
Then: each entry of `top_performers` and `best_adds` of each manager in `managers.json` has a `bye_week` number, and Brock Purdy of The Blue Tent has the bye week of San Francisco (dry run)
Evidence: the command output, and the `bye_week` fields of The Blue Tent in `managers.json`.

AT-2: A top performer row shows a coming bye
App: site
Stories: 1, 5, 6
Given: the site built from `2026` week 8, and a top performer of The Blue Tent whose bye is after week 8 (dry run)
When: the reader opens the manager page of The Blue Tent
Then: the row of that player reads "Bye <week>" on one line
Evidence: screenshots of the manager page of The Blue Tent at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-3: A best add row shows a passed bye as done
App: site
Stories: 2, 3
Given: the site built from `2026` week 8, and the best add Dallas Goedert of The Blue Tent, whose bye is before week 8 (dry run)
When: the reader opens the manager page of The Blue Tent
Then: the row of Dallas Goedert reads "Bye done"
Evidence: screenshots of the best adds of The Blue Tent at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-4: The manager page gets no roster list
App: site
Stories: none
Given: the site built from `2026` week 8
When: the reader opens the manager page of The Blue Tent
Then: the page shows no list of the full roster
Evidence: screenshots of the full manager page at 375, 768, and 1280 px, each in the light theme and the dark theme.

## Trace

Story 1: AT-1, AT-2
Story 2: AT-1, AT-3
Story 3: AT-3
Story 4: AT-1
Story 5: AT-2
Story 6: AT-2
Out of scope "A roster list on the manager page": AT-4

## Revisions

None yet.
