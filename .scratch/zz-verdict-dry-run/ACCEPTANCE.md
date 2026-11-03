# Dry run: the pipeline README names the verdict check: acceptance tests

Spec: `.scratch/zz-verdict-dry-run/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

## Tests

AT-1: The pipeline README names the verdict check
App: pipeline
Stories: 1
Given: the Spec branch `zz-verdict-dry-run`
When: `grep -n 'verdict' apps/pipeline/README.md`
Then: the output holds one line that names the check `verdict` and ADR 0020 (dry run)
Evidence: the command output.

AT-2: The home page stays as it is
App: site
Stories: 2
Given: the site built from `2026` week 8
When: the reader opens the home page
Then: the home page shows the week 8 report, with no new text (dry run)
Evidence: screenshots of the home page at 375, 768, and 1280 px, each in the light theme and the dark theme.

## Trace

Story 1: AT-1
Story 2: AT-2
Out of scope "A change to any page of the site": AT-2

## Revisions

None yet.
