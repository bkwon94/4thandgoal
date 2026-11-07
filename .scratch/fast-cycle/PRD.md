# Fast cycle: half the time from the first ticket to a green PR, with the same guardrails

Status: ready-for-agent
Date: 2026-11-06
Apps: both. The pipeline and the API run their tests in parallel. The site check gets its own CI job with a cached Chromium. The root CI, `scripts/verdict.py`, and the `cpc` skills change for both apps.
Spec branch: `fast-cycle`.
Source: the map `.scratch/fast-cycle/MAP.md` and decision tickets 01 to 13. ADR 0026 supersedes ADR 0020.
Tickets: 01 to 07, in `issues/`.

## Problem Statement

Brian finds the cycle from an idea to a merged spec too slow. On `midseason-report`, the build and the merge-back of 14 tickets took 3.6 h. The review fixes took 1.7 h. The CI check took 26 min per push, near its 20 min job timeout. One failure that CI found cost about 8 h of wall time overnight.

The time goes to three causes. The first cause is the round trips for merge conflicts and fixes. The second cause is a CI job that runs every app in sequence. The third cause is the Test verdict comment that Brian must write at the end. Brian wants the cycle faster, and he wants the same guardrails.

## Solution

A spec the size of `midseason-report` goes from the `cpc:implement` start to a green PR in half the time or less:

| Stage | Now | Target |
| --- | --- | --- |
| Build and merge-back | 3.6 h | 2 h or less |
| Review fixes | 1.7 h | 40 min or less |
| CI `check` | 26 min | 10 min or less |
| Hook | 23 s | no change |

Every check that runs today still runs, and none gets weaker. The changes:

1. The orchestrator resolves a merge conflict itself. It sends no ticket back.
2. The review fixes run in parallel fix groups.
3. CI runs one job per app and package, and the pipeline and API tests run under `pytest-xdist`.
4. One local `make check` runs in the background during the evidence stage, so CI rarely finds a failure.
5. The Judge gives each Test verdict. Brian posts no comment unless he wants to give a FAIL. Brian still merges.

## User Stories

1. As Brian, I want a spec to reach a green PR in half the time, so that the cycle stops getting in my way.
2. As Brian, I want every check of today to still run, so that a faster cycle does not ship more defects.
3. As Brian, I want no test skipped, weakened, or marked `xfail` for speed, so that the speed comes from how checks run.
4. As Brian, I want to merge a spec PR with no Test verdicts comment, so that the end of a spec costs me no writing.
5. As Brian, I want to check the work on the local dev server when I choose, so that my own look stays possible.
6. As Brian, I want one PR comment with `AT-<n>: FAIL` to block the merge, so that I can stop a defect that I find.
7. As Brian, I want a FAIL of mine to count until I post a newer Test verdicts comment that has no FAIL for that test, so that the block is clear.
8. As Brian, I want the Judge to be an agent that did not build the work, so that no agent grades its own work.
9. As Brian, I want the Judge to see only the acceptance tests and the evidence, so that its verdict reads the behavior, not the intent of the builder.
10. As Brian, I want a FAIL from the Judge to get one fix round, so that a small miss does not stop the spec.
11. As Brian, I want a second FAIL to set the test to BLOCKED and open no PR, so that a loop cannot run without end.
12. As Brian, I want to hear the BLOCKED test and its reason, so that I can decide the next step.
13. As Brian, I want the check `verdict` to go red if the evidence or the acceptance tests change after the Judge read them, so that an old verdict never covers new work.
14. As Brian, I want each change to the Judge's verdicts to show as its own commit, so that an edit by the orchestrator leaves a trace.
15. As Brian, I want PR #13 to keep my Test verdicts, so that the open midseason work needs no special case.
16. As the orchestrator, I want to resolve a merge conflict in the spec worktree, so that a conflict costs minutes and not a round trip.
17. As the orchestrator, I want a red `make check-fast` after a resolved conflict to reset the spec branch, so that a red check never stays on it.
18. As the orchestrator, I want to sort the review findings into groups that share no file, so that the fix subagents run in parallel.
19. As the orchestrator, I want each fix group to merge back under the same rule as a ticket, so that one rule covers every merge.
20. As the orchestrator, I want one background `make check` during the evidence stage, so that a failure gets fixed before the push.
21. As the orchestrator, I want the background run to add no wall time, so that the evidence stage does not wait for it.
22. As a ticket subagent, I want only `make check-fast` in a ticket build, so that a ticket does not wait for the full suite.
23. As a developer, I want `make -C apps/pipeline test` to run in parallel, so that the local full suite takes about 1 min.
24. As a developer, I want the API tests to run in parallel, so that they take about 20 s.
25. As a developer, I want the CI jobs of each app to run at the same time, so that CI takes the time of the slowest app.
26. As a developer, I want Chromium to come from a cache on CI, so that the site job does not spend 6 min on an install.
27. As a developer, I want a gate job named `check`, so that the check name of the PR and the deploy triggers stay the same.
28. As a deploy workflow, I want `workflow_run` of `Check` to keep its meaning, so that a deploy still starts only after every job is green.
29. As a deploy dispatch, I want the call of `check.yml` to still run every job, so that a manual deploy still checks its ref.
30. As a developer, I want the midseason tests to share one build per set of inputs, so that they stop building the same report 45 times.
31. As a developer, I want each midseason assertion and the full sim count to stay, so that the shared build is a cache and not a weaker test.
32. As an agent new to the repo, I want the glossary to define the Judge and the Test verdict, so that I use one word for one meaning.

## Implementation Decisions

### The guardrail rule (decision 01)

- A check can move to a different place, run in parallel, or use a cache. A check never disappears and never gets weaker.
- CI always runs the full check of every app. A CI run of only the changed apps is out.
- A smaller sim sample is allowed only with the same assertion and a fixed seed. Decision 10 found that the midseason tests need none.

### The build stage of `cpc:implement` (decision 02)

- On a merge conflict of a ticket, the orchestrator resolves it in the spec worktree with `resolving-merge-conflicts`. Then it runs `make check-fast BASE=main`.
- A red check resets the spec branch to the head before the merge, as now. Only after a reset does the ticket go back to its subagent, with the failure.
- The rest of the merge rule stays: one merge at a time, `git merge --no-edit`, and `make check-fast` on the merged result.

### The review stage of `cpc:implement` (decision 03)

- One `code-review` runs on the whole spec branch against `main`, as now.
- The orchestrator sorts the findings into groups that share no file. One subagent per group fixes its findings on a fix branch `<slug>-fix-<letter>`, with one commit per finding and the hook.
- Each fix branch merges into the spec branch under the rule of the build stage.

### The evidence stage of `cpc:implement` (decision 05)

- When the evidence stage starts, the orchestrator starts one `make check` in the background in the spec worktree.
- No other `uv run --exact --package` runs in that worktree while it runs. Two runs of different members in one checkout share one `.venv` and break each other (decision 09). The evidence runner of the site does not use `uv run`.
- A red run gets fixed before the push. A fix runs the failed app's check again, not the full run.

### The Judge (decisions 06, 07, 08, and 12)

- After the evidence stage, the orchestrator starts a fresh subagent, the Judge. Its brief holds only the paths of `ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/`. It gets no build context, no diff, and no ticket.
- The Judge writes `.scratch/<slug>/VERDICTS.md`. The file has one line per test, `AT-<n>: PASS` or `AT-<n>: FAIL <reason>`, under the heading `Test verdicts`.
- The file also names the git blob SHA of `ACCEPTANCE.md` and of `EVIDENCE.md` that the Judge read.
- The orchestrator commits the file alone, in a commit named "Record the Test verdicts of the Judge". Each new round is a new commit, so an edit leaves a trace.
- After a FAIL, the orchestrator fixes the work and records the evidence of the failed tests again. A fresh Judge checks only those tests, and writes their new lines.
- A second FAIL sets the test to BLOCKED in `VERDICTS.md`. The orchestrator opens no PR and tells Brian the test and the reason.

### The check `verdict` (decision 12)

- `verdict.yml` keeps its name, its trigger, and its rule: it reads `scripts/verdict.py` from `main`, and it reads the PR files as data through the API.
- `scripts/verdict.py` reads `VERDICTS.md` at the PR head. It passes only if every live test of `ACCEPTANCE.md` has one PASS line, and no line names a test that is not live.
- It fails if the blob SHA of `ACCEPTANCE.md` or `EVIDENCE.md` at the PR head differs from the SHA in `VERDICTS.md`. The rule id names the stale file.
- It reads the latest Test verdicts comment of Brian, with no agent marker, as now. A FAIL or BLOCKED line in that comment fails the check for that test, whatever the Judge gave. A PASS line of Brian changes nothing.
- A spec PR with no `ACCEPTANCE.md` still passes, as now.
- The rule text changes from "a PASS Test verdict from Brian" to "a PASS Test verdict from the Judge and no FAIL from Brian".

### `cpc:review` (decision 08)

- A FAIL of Brian is one finding. `cpc:review` fixes it, records its evidence again, and runs a fresh Judge on that test.
- Brian clears his FAIL with a newer Test verdicts comment that has no FAIL for that test.

### CI (decisions 04, 09, and 11)

- The workflow `Check` keeps its name and its triggers: a push to `main`, a pull request, a dispatch, and a `workflow_call` with `ref`.
- It runs these jobs at the same time: `scripts`, `site`, `pipeline`, `api`, and `packages`. Each job sets up only the tools that its member needs.
- A gate job named `check` needs every job and fails if one of them fails or is cancelled. Its name keeps the check name on the PR.
- The `workflow_run` event of `Check` fires once, when every job ends. Its conclusion is success only if each job succeeded, so `deploy-sites.yml` and `deploy-api.yml` need no change. The dispatch path of each deploy calls `check.yml`, so it runs every job too.
- The root Makefile gets one target per member that the CI job calls. `make check` still runs every member in sequence, for the local background run.
- The pipeline and the API run `pytest -n auto` from `pytest-xdist`, in `make test` and in `make check`. `pytest-xdist` becomes a dev dependency of each member, in `uv.lock`. `make check-fast` keeps its rule tests and needs no change.
- The `site` job caches the Playwright browser folder. The key is the OS and the Playwright version from `pnpm-lock.yaml`. On a hit, the job installs only the system packages of Chromium. On a miss, it installs Chromium with its packages, as now.
- Each job has a timeout of 15 min. The gate job has a timeout of 2 min.

### The midseason tests (decision 10)

- The read-only midseason tests share one build per set of inputs through a session fixture. A test that writes or changes the build keeps its own build in `tmp_path`.
- Each assertion stays the same. The full sim count stays, because three tests need it.
- These tests live on `midseason-report`. The ticket for this fixture starts after PR #13 merges into `main` and `fast-cycle` merges `main`.

### PR #13 (decision 13)

- PR #13 keeps the old rule: Brian posts its Test verdicts.
- `fast-cycle` merges to `main` only after PR #13 merges. The rule in `scripts/verdict.py` changes for every later spec.

## Testing Decisions

A good test checks behavior that a reader can see: a check result, a run time, a commit status, or a file that a skill writes. It does not check how a skill phrases a step.

The seams, from the highest:

1. **The CI run itself.** A push of the spec branch runs `Check`. The test reads the job list, the time of each job, the gate result, and the step time of the Chromium install. A planted red test in one member must turn the gate red. Prior art: the CI run history of `check.yml`.
2. **`scripts/verdict.py`.** Its unit tests in `scripts/test_verdict.py` cover each rule: a full PASS, a missing line, a Judge FAIL, a stale `EVIDENCE.md`, a stale `ACCEPTANCE.md`, a FAIL of Brian over a Judge PASS, and a newer comment of Brian that clears it. Prior art: the tests of the current rule in the same file.
3. **A direct run of each changed stage of the `cpc` skills.** Per the rule of no calendar waits, each stage is proven by a run now, not on the next real spec:
   - The Judge runs on the evidence of `faster-evidence`, where Brian gave PASS to all 14 tests. Its verdicts must match. A copy with one planted false observation must get a FAIL.
   - The conflict step replays a conflicted merge-back of `midseason-report` in a throwaway worktree. The orchestrator resolves it, and `make check-fast` runs.
   - The fix groups run on a recorded list of findings and show groups that share no file.
4. **The test times.** `make -C apps/pipeline test` and the API test run locally, serial and with `-n auto`, with the same pass count. The midseason fixture shows the same pass count and a lower time under `-n auto`.

The targets for the build and the review stages are measured on the first real spec after this one. They are a goal of the spec, not an acceptance test, because no direct run can measure them now.

## Out of Scope

- A "Blocked by" edge between tickets that touch the same file. Brian chose the smaller change of decision 02 first.
- A review per ticket. It changes more and starts more subagents than decision 03.
- A CI run of only the changed apps. Decision 01 keeps the full check on CI.
- A ruleset or branch protection on `main`. See Further Notes.
- A cache of `node_modules` for a new worktree. See Further Notes.

## Further Notes

- `main` has no ruleset and no branch protection. GitHub therefore does not enforce `check` or `verdict`. The gate holds only because Brian waits for green before the merge. A ruleset with both checks is a later decision for Brian.
- A new worktree has no `node_modules`, so its first commit hook fails until `pnpm install` runs. This costs about 1 min per ticket worktree. `build.md` may need one line for it. This is a candidate for a later spec.
- The memory `check-fast-only` still holds: a ticket build and a merge-back run only `make check-fast`. The one background `make check` per spec does not break it.
- The CI estimate of about 3 min for the pipeline comes from local runs on 10 cores. The CI run of this spec measures the real number on 4 cores.
