# Fast cycle: acceptance tests

Spec: `.scratch/fast-cycle/PRD.md`.

The Test verdict: only Brian gives one for this spec. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict. The check `verdict` reads `scripts/verdict.py` from `main`, so the rule of ADR 0026 applies only to the specs after this one (decision 13).

The `cpc` skills load from the main checkout. So each direct run of a changed skill stage reads the skill files of the worktree `.claude/worktrees/fast-cycle`, and its brief names those paths. A throwaway branch or worktree of a test is removed after the test, and its branch is never pushed, except the throwaway branch of AT-3 and AT-27, which is deleted on `origin` after the run.

The CI times come from `gh run view <id> --json jobs`. The local times come from the Mac of Brian, with `time`.

## Tests

AT-1: The CI check takes 10 minutes or less
App: both
Stories: 1, 25
Given: The spec branch `fast-cycle` with every ticket merged, pushed with its PR open, after one run that filled the Chromium cache.
When: A push to the PR starts the workflow `Check`.
Then: The gate job `check` is green, and the run takes 10 min or less from the start of the first job to the end of `check`.
Evidence: The run URL, the start and end time of each job, and the total.

AT-2: The jobs of each member run at the same time
App: both
Stories: 25, 27
Given: The run of AT-1.
When: The reader reads the jobs of the run.
Then: The jobs `scripts`, `site`, `pipeline`, `api`, and `packages` each start within 1 min of the first job, and the job `check` lists all five under `needs`.
Evidence: The start time of each job from `gh run view`, and the `needs` line of `check` in `check.yml`.

AT-3: A red member turns the gate red
App: both
Stories: 2, 27, 28
Given: A throwaway branch from `fast-cycle` with one planted failed test in the API, such as `assert 1 == 2`, pushed with a draft PR.
When: The workflow `Check` runs on it.
Then: The job `api` fails, the job `check` fails, and the conclusion of the run of `Check` is `failure`.
Evidence: The run URL, the result of each job, and the conclusion of the run. The draft PR is closed and the branch is deleted after the run.

AT-4: Chromium comes from the cache
App: site
Stories: 26
Given: Two runs of `Check` on `fast-cycle` with no change to `pnpm-lock.yaml` between them.
When: The second run reaches the Chromium step of the job `site`.
Then: The cache step reports a hit, and the Chromium step takes 2 min or less. The last run before this spec took 6 min 17 s.
Evidence: The step times of the job `site` of both runs, and the cache line of the second run.

AT-5: The deploy triggers do not change
App: both
Stories: 28, 29
Given: The spec branch `fast-cycle` with every ticket merged.
When: The reader runs `git diff main...fast-cycle -- .github/workflows/deploy-sites.yml .github/workflows/deploy-api.yml`.
Then: The diff is empty. The run of AT-1 has the conclusion `success`, and the run of AT-3 has the conclusion `failure`, so `workflow_run` of `Check` still carries the result of every job.
Evidence: The empty diff output, and the conclusions of the runs of AT-1 and AT-3.

AT-6: The pipeline tests run in parallel
App: pipeline
Stories: 2, 23
Given: The spec branch `fast-cycle` on the Mac of Brian, before the merge of PR #13.
When: The agent runs `make -C apps/pipeline test`, then the serial run `uv run --exact --package cornerstone pytest -q -p no:xdist`.
Then: `make -C apps/pipeline test` passes 1579 tests in 90 s or less. The serial run passes the same count.
Evidence: The output and the time of both runs.

AT-7: The API tests run in parallel
App: pipeline
Stories: 2, 24
Given: The spec branch `fast-cycle` on the Mac of Brian.
When: The agent runs the test target of `apps/api`, then the same tests serially with `-p no:xdist`.
Then: The test target passes 163 tests in 40 s or less. The serial run passes the same count.
Evidence: The output and the time of both runs.

AT-8: No check gets weaker
App: both
Stories: 2, 3
Given: The spec branch `fast-cycle` with every ticket merged.
When: The agent searches the added lines of `git diff main...fast-cycle` for `skip`, `xfail`, `deselect`, `.only`, and `-m 'not`, and lists the deleted test files. Then it counts the tests of each member on `main` and on `fast-cycle`.
Then: No added line holds one of those words, except in a comment that names this rule, and no test file is deleted. Each member has at least as many tests as on `main`.
Evidence: The search command and its output, the list of deleted files, and a table of the test count of each member on both branches.

AT-9: The commit hook does not change
App: both
Stories: 22
Given: The spec branch `fast-cycle` with every ticket merged, on the Mac of Brian.
When: The agent runs `make check-fast` at the root, then `git diff main...fast-cycle -- prek.toml`.
Then: `make check-fast` passes in 30 s or less and prints the same `==>` lines as on `main`. The diff of `prek.toml` is empty.
Evidence: The output and the time of `make check-fast` on both branches, and the empty diff.

AT-10: A full PASS of the Judge passes the check
App: both
Stories: 4
Given: An `ACCEPTANCE.md` with AT-1 to AT-3, an `EVIDENCE.md`, and a `VERDICTS.md` with PASS for each test and the blob SHA of both files.
When: The agent runs `scripts/verdict.py` on them with no comment of Brian.
Then: The script exits 0 and prints that AT-1, AT-2, and AT-3 have PASS.
Evidence: The unit test of this case in `scripts/test_verdict.py`, and its output.

AT-11: A stale evidence file fails the check
App: both
Stories: 13
Given: The files of AT-10, then one changed line in `EVIDENCE.md`, so its blob SHA no longer matches `VERDICTS.md`.
When: The agent runs `scripts/verdict.py` on them.
Then: The script exits 1 with a rule id that names `EVIDENCE.md` as stale.
Evidence: The unit test of this case and its output.

AT-12: A FAIL of Brian overrides the Judge
App: both
Stories: 6
Given: The files of AT-10, and a comment of Brian with the line `Test verdicts` and the line `AT-2: FAIL`.
When: The agent runs `scripts/verdict.py` on them.
Then: The script exits 1, and its report names AT-2 and the FAIL of Brian.
Evidence: The unit test of this case and its output.

AT-13: A newer comment of Brian clears his FAIL
App: both
Stories: 7
Given: The files and the comment of AT-12, and a newer comment of Brian with the line `Test verdicts` and no FAIL for AT-2.
When: The agent runs `scripts/verdict.py` on them.
Then: The script exits 0.
Evidence: The unit test of this case and its output.

AT-14: The Judge agrees with Brian on real evidence
App: both
Stories: 8, 9
Given: The `ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/` of `faster-evidence` at `197fb328`. Brian gave PASS to all 14 tests.
When: The orchestrator starts the Judge with the brief of the evidence stage of the `fast-cycle` worktree, on a throwaway copy of those files.
Then: The Judge writes a `VERDICTS.md` with PASS for each of the 14 tests.
Evidence: The `VERDICTS.md` that the Judge wrote.

AT-15: The Judge catches a false observation
App: both
Stories: 8, 9
Given: The throwaway copy of AT-14, with the Observation of `faster-evidence` AT-2 changed to say that `1280-light.png` shows a dark background. The image stays the same.
When: The orchestrator starts a fresh Judge on the copy.
Then: The Judge gives FAIL to AT-2, with a reason that names the mismatch of the Observation and the image. Each other test has PASS.
Evidence: The changed Observation line, and the `VERDICTS.md` that the Judge wrote.

AT-16: The Judge sees only the evidence
App: both
Stories: 9
Given: The run of AT-14.
When: The reader reads the brief that the orchestrator gave the Judge.
Then: The brief names only the paths of `ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/`. It holds no diff, no ticket, no PRD, and no build note.
Evidence: The full text of the brief.

AT-17: A second FAIL sets BLOCKED and opens no PR
App: both
Stories: 10, 11, 12
Given: A throwaway feature, copied from the files of AT-15, whose AT-2 asks for a result that the work cannot show. The fix round cannot make it true.
When: The orchestrator runs the Judge step of the `fast-cycle` worktree: the first Judge, one fix round, and a second Judge.
Then: `VERDICTS.md` gives BLOCKED to AT-2. No `gh pr create` runs. The message to Brian names AT-2 and the reason of the Judge.
Evidence: Both rounds of `VERDICTS.md`, the shell log of the run with no `gh pr create`, and the message to Brian.

AT-18: Each Judge round is one commit
App: both
Stories: 14
Given: The throwaway feature of AT-17 after both rounds.
When: The agent runs `git log --stat` on its branch.
Then: Each round is one commit named "Record the Test verdicts of the Judge", and each such commit changes only `VERDICTS.md`.
Evidence: The `git log --stat` output.

AT-19: The orchestrator resolves a merge conflict itself
App: both
Stories: 16
Given: A throwaway worktree at the head of `midseason-report` before one merge-back that conflicted, such as the merge of ticket 03 at 19:17 on 2026-11-05, and the ticket branch at its commit before that merge.
When: The orchestrator follows the merge step of `build.md` in the `fast-cycle` worktree.
Then: The merge has a conflict. The orchestrator resolves it in that worktree with `resolving-merge-conflicts` and starts no ticket subagent. `make check-fast BASE=main` is green, and the merge commit stays.
Evidence: The commits used, the conflicted files, the shell log of the merge and the check, and the list of subagents started, which is empty.

AT-20: A red check after a resolve resets the spec branch
App: both
Stories: 17
Given: The throwaway worktree of AT-19, with a resolve that keeps a side of the conflict that breaks `make check-fast`.
When: The orchestrator follows the merge step of `build.md` in the `fast-cycle` worktree.
Then: `make check-fast` fails. The head of the branch is the head before the merge, and the ticket goes back to its subagent with the failure.
Evidence: The head before the merge, the red check output, the head after the reset, and the message to the subagent.

AT-21: The review fixes sort into groups that share no file
App: both
Stories: 18, 19
Given: The 35 review findings of `midseason-report`, from the commits K-1 to K-15, S-1 to S-11, and P-4 to P-6, each with its file list from `git show --name-only`.
When: The orchestrator follows the review step of `build.md` in the `fast-cycle` worktree, on that list.
Then: Each finding is in one group, and no two groups share a file.
Evidence: The table of the groups, with the findings and the files of each, and a check script output that finds no shared file.

AT-22: The background full check adds no wait
App: both
Stories: 20, 21
Given: The evidence stage of this spec, `fast-cycle`, run with the evidence step of the `fast-cycle` worktree.
When: The orchestrator starts the evidence stage.
Then: `make check` starts within 1 min of the stage start. It ends green before the push of the PR. The push waits 0 min for it, because it ended before the last evidence file.
Evidence: The start and end time of the stage, of `make check`, and of the push, and the last lines of the `make check` output.

AT-23: The midseason tests share a build
App: pipeline
Stories: 30
Given: PR #13 merged into `main`, and `main` merged into `fast-cycle`, with the ticket of the shared fixture merged.
When: The agent runs `make -C apps/pipeline test` on `fast-cycle`, then on `main`.
Then: Both runs pass the same count of tests. The run on `fast-cycle` takes less time.
Evidence: The output and the time of both runs.

AT-24: The full sim count stays
App: pipeline
Stories: 31
Given: The spec branch of AT-23.
When: The agent compares the sim run count of `test_midseason.py` near line 279 and line 562, and of `test_sim.py` near line 70, on `main` and on `fast-cycle`.
Then: Each count is the same on both branches.
Evidence: The lines of each count on both branches.

AT-25: The glossary defines the Judge
App: both
Stories: 32
Given: The spec branch `fast-cycle`.
When: The reader reads the Workflow section of `GLOSSARY.md`, and the head of ADR 0020.
Then: The glossary defines **Judge**, and **Test verdict** as the word of the Judge that a FAIL of Brian overrides. ADR 0020 says that ADR 0026 supersedes it.
Evidence: The two glossary entries and the line of ADR 0020.

AT-26: PR #13 merges before this spec
App: both
Stories: 15
Given: The PR of `fast-cycle` with every other test recorded.
When: The agent runs `gh pr view 13 --json state,mergedAt`.
Then: PR #13 has the state `MERGED`.
Evidence: The command output.

AT-27: CI runs every member for a small change
App: both
Stories: none
Given: A throwaway branch from `fast-cycle` that changes only one line of one doc in `docs/`, pushed with a draft PR.
When: The workflow `Check` runs on it.
Then: All five jobs run their check. No job skips its member because of the changed paths.
Evidence: The run URL and the steps of each job. The draft PR is closed and the branch is deleted after the run.

AT-28: The spec adds no ruleset
App: both
Stories: none
Given: The spec branch `fast-cycle` with every ticket merged.
When: The agent runs `gh api repos/{owner}/{repo}/rulesets` and `gh api repos/{owner}/{repo}/rules/branches/main`.
Then: Both return an empty list, as before this spec.
Evidence: The output of both commands.

AT-29: The build stage starts no review per ticket
App: both
Stories: none
Given: The spec branch `fast-cycle` with every ticket merged.
When: The reader reads stage 1 of `build.md` in `.claude/plugin/skills/implement/`.
Then: Stage 1 calls no `code-review`. The only `code-review` call is in stage 2, on the whole spec branch.
Evidence: The output of `grep -n code-review` on `build.md`, with the heading of each match.

AT-30: The tickets get no overlap edges
App: both
Stories: none
Given: The spec branch `fast-cycle` with every ticket merged.
When: The agent runs `git diff main...fast-cycle -- .claude/plugin/skills/to-tickets`.
Then: The diff is empty.
Evidence: The empty diff output.

## Trace

Story 1: AT-1. The build target and the review target have no test. Reason: they are goals, measured on the next real spec, because no direct run can measure them now.
Story 2: AT-3, AT-6, AT-7, AT-8
Story 3: AT-8
Story 4: AT-10
Story 5: no test. Reason: nothing about the local dev server changes.
Story 6: AT-12
Story 7: AT-13
Story 8: AT-14, AT-15
Story 9: AT-14, AT-15, AT-16
Story 10: AT-17
Story 11: AT-17
Story 12: AT-17
Story 13: AT-11
Story 14: AT-18
Story 15: AT-26
Story 16: AT-19
Story 17: AT-20
Story 18: AT-21
Story 19: AT-21
Story 20: AT-22
Story 21: AT-22
Story 22: AT-9
Story 23: AT-6
Story 24: AT-7
Story 25: AT-1, AT-2
Story 26: AT-4
Story 27: AT-2, AT-3
Story 28: AT-3, AT-5
Story 29: AT-5
Story 30: AT-23
Story 31: AT-24
Story 32: AT-25
Out of scope "A Blocked by edge between tickets that touch the same file": AT-30
Out of scope "A review per ticket": AT-29
Out of scope "A CI run of only the changed apps": AT-27
Out of scope "A ruleset or branch protection on main": AT-28
Out of scope "A cache of node_modules for a new worktree": no test. Reason: an agent is unlikely to build it by mistake.

## Revisions

None yet.
