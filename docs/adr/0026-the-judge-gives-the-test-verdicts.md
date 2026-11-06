# The Judge gives the test verdicts of a spec PR

ADR 0020 made Brian give a test verdict for each acceptance test in one PR comment. That comment
is the slow step at the end of each spec, and Brian checks most work on the local dev server
anyway. We decided that a subagent, the Judge, gives each test verdict. Brian still merges.

## The steps

1. An agent runs `code-review` on the spec branch and fixes the findings.
2. An agent runs each acceptance test and records the evidence.
3. A fresh subagent, the Judge, reads only `ACCEPTANCE.md`, `EVIDENCE.md`, and the evidence files.
   It gets no build context. It gives PASS or FAIL for each `AT-<n>`.
4. After a FAIL, the agent fixes the work and records the evidence of the failed tests again. A
   fresh Judge checks only those tests. A second FAIL sets the test to BLOCKED, and the agent opens no PR.
5. The check `verdict` blocks the merge until every test has PASS from the Judge.
6. A FAIL from Brian for a test, in a PR comment, overrides the Judge and turns `verdict` red.
   Brian never needs to post PASS.

## Why a Judge and not the builder

ADR 0020 kept the agent from a test verdict, because the author would grade its own work. The
Judge keeps that rule: it did not build the work and sees only the behavior that the evidence shows.

## The risk

The Judge reads the evidence, not the running site, so weak evidence can pass a defect. Brian's
own check on the dev server and his FAIL override cover part of this risk. A miss means we add a
test and a rule, as before.

We rejected two alternatives:

- **No gate on the pull request.** The spec would then have no proof that it works.
- **The builder gives the verdict.** The author would grade its own work.
