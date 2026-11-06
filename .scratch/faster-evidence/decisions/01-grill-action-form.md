# 01: The form of the action before a shot

Map: `.scratch/faster-evidence/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Some site tests need a click or an input before the shot, such as a trade in the analyzer or an open menu. The script needs one form for these steps. Examples: a JSON list of steps, or a small JS function in a file for each test. The form decides what the agent writes for each test and what `evidence.md` teaches.

## Decision

Brian decided on 2026-11-05, in a grill.

1. A test names its steps as a JSON list with a fixed set of six verbs: `click`, `fill`, `scroll`, `wait`, `shot <name>`, and `url`. Example: `[{"click":"text=Week 7"},{"wait":"url"},{"shot":"after-tap"},{"url":true}]`. A test that needs a step outside the six verbs uses `agent-browser` for that one test.
2. The list lives in `evidence/AT-<n>/steps.json`. `cpc:implement` writes it at the evidence stage and commits it with the shots. `cpc:review` runs the same file again after a fix. One script run takes every `steps.json` of the feature.
3. A `steps.json` holds `route` and `steps`, and optional `widths` and `themes`. The default is all 3 widths x 2 themes. The agent narrows them only to match the Evidence line of the test.

The reasons:

- Six verbs cover every action of the site-redesign tests: taps (AT-7, 10, 17, 29, 30), scrolls with a shot before and after (AT-8, 9, 11), more than one shot (AT-19), the analyzer steps with a wait on the API (AT-20 to 22), and the URL after a tap (AT-10).
- Data cannot fail with a syntax error or a missed `await`. A JS file for each test lets each test grow its own code, and that code written fresh for each test made the 40 calls.
- A selector exists only after the build, so `cpc:to-acceptance` cannot write the steps. The steps stay out of `ACCEPTANCE.md`, which holds plain behavior.
- The Evidence line of a test is the contract. Extra shots add files to look at before a verdict, and they add time on the analyzer tests.
