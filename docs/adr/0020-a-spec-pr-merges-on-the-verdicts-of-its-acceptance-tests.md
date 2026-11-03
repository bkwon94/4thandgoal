# A spec PR merges on the verdicts of its acceptance tests

Agents write most of the diff, and one human reads it later and with less context than the
agent had. A diff review by that human is slow, and it checks the code more than the behavior.
We decided that a spec pull request merges on the verdicts of its acceptance tests, not on a
review of the diff.

## The steps

1. An agent runs `code-review` on the spec branch and fixes the findings.
2. An agent runs each acceptance test and records the evidence. The agent gives no verdict.
3. Brian gives PASS, FAIL, or BLOCKED for each `AT-<n>` in one comment on the pull request.
4. A check blocks the merge until every test has PASS.

The agent never gives a verdict, because the agent wrote the code and would grade its own work.

## The evidence

- **Site:** screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.
- **Pipeline:** the command output and the changed `page.json` fields, for a real week.

The evidence uses real data and a real build. It uses no mock.

## The risk

A test can miss a bug. A spec with weak tests then merges a defect with a clean record. The agent
`code-review` covers part of this risk, because it reads the diff against the repo standards and
the spec. It does not cover all of it. The `check` command also still runs on every push, so the
rule tests catch what they encode. We accept the rest of the risk, and a miss means we add a test
and a rule.

We rejected three alternatives:

- **A human diff review of every pull request.** It is the slow step that this rule removes.
- **An agent verdict.** The author would grade its own work.
- **No gate on the pull request.** The spec would then have no proof that it works.
