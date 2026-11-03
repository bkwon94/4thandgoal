# The acceptance file

`.scratch/<slug>/ACCEPTANCE.md`. Write labelled lines and flat lists, as below.

```markdown
# <Feature title>: acceptance tests

Spec: `.scratch/<slug>/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

## Tests

AT-1: <The behavior, as a title>
App: site
Stories: 1, 2
Given: <the real week and the state>
When: <one action of the reader>
Then: <one result that the reader sees>
Evidence: screenshots of <the page> at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-2: <The behavior, as a title>
App: pipeline
Stories: 3
Given: <the real week, such as 2026 week 8>
When: <the command, such as `make -C apps/pipeline page-json WEEK=8`>
Then: <the field and its value in page.json>
Evidence: the command output and the changed `page.json` fields.

## Trace

Story 1: AT-1
Story 4: no test. Reason: <why>
Out of scope "<item>": AT-<n>

## Revisions

None yet.
```

Number the tests from `AT-1`, with no leading zero.
