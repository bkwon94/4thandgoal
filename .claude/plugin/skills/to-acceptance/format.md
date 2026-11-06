# The acceptance file

`.scratch/<slug>/ACCEPTANCE.md`. Write labelled lines and flat lists, as below.

```markdown
# <Feature title>: acceptance tests

Spec: `.scratch/<slug>/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

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

Number the tests from `AT-1`, with no leading zero. A test of an Out of Scope item has the line `Stories: none`.
