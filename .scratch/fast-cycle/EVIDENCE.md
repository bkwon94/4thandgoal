# Fast cycle: evidence

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests: `.scratch/fast-cycle/ACCEPTANCE.md`.
Built from: `0a70f1a3`, on 2026-11-06. The agent gives no Test verdict. For this spec, Brian gives each Test verdict in one PR comment (decision 13).
Round time: 0 min for 0 site tests. This spec has no screenshot test.

## AT-1: The CI check takes 10 minutes or less

App: both
Then: The gate job `check` is green, and the run takes 10 min or less from the start of the first job to the end of `check`.
Files: `evidence/AT-1/run.json`, `evidence/AT-1/times.txt`
Observation: CI_PENDING

## AT-2: The jobs of each member run at the same time

App: both
Then: The jobs `scripts`, `site`, `pipeline`, `api`, and `packages` each start within 1 min of the first job, and the job `check` lists all five under `needs`.
Files: `evidence/AT-2/times.txt`, `evidence/AT-2/needs.txt`
Observation: CI_PENDING

## AT-3: A red member turns the gate red

App: both
Then: The job `api` fails, the job `check` fails, and the conclusion of the run of `Check` is `failure`.
Files: `evidence/AT-3/run.json`, `evidence/AT-3/planted-test.txt`, `evidence/AT-3/cleanup.txt`
Observation: CI_PENDING

## AT-4: Chromium comes from the cache

App: site
Then: The cache step reports a hit, and the Chromium step takes 2 min or less. The last run before this spec took 6 min 17 s.
Files: `evidence/AT-4/steps.txt`
Observation: CI_PENDING

## AT-5: The deploy triggers do not change

App: both
Then: The diff is empty. The run of AT-1 has the conclusion `success`, and the run of AT-3 has the conclusion `failure`, so `workflow_run` of `Check` still carries the result of every job.
Files: `evidence/AT-5/diff.txt`, `evidence/AT-1/run.json`, `evidence/AT-3/run.json`
Observation: The diff of `deploy-sites.yml` and `deploy-api.yml` against `origin/main` has 0 lines. CI_PENDING

## AT-6: The pipeline tests run in parallel

App: pipeline
Then: `make -C apps/pipeline test` passes 1579 tests in 90 s or less. The serial run passes the same count.
Files: `evidence/AT-6/output.txt`
Observation: `make -C apps/pipeline test` passed 1578 tests under `-n auto` and then the 1 `serial` test alone, 1579 in all, in 55 s of wall time. The serial run `pytest -q -p no:xdist` passed 1579 tests in 245 s.

## AT-7: The API tests run in parallel

App: pipeline
Then: The test target passes 163 tests in 40 s or less. The serial run passes the same count.
Files: `evidence/AT-7/output.txt`
Observation: `make -C apps/api test` ran `pytest -q -n auto` and passed 163 tests in 19 s of wall time. The serial run with `-p no:xdist` passed 163 tests in 67 s.

## AT-8: No check gets weaker

App: both
Then: No added line holds one of those words, except in a comment that names this rule, and no test file is deleted. Each member has at least as many tests as on `main`.
Files: `evidence/AT-8/search.txt`, `evidence/AT-8/counts.md`
Observation: The search finds 3 added lines. Line 195 is skill text about a test that the evidence stage skips for a blocked ticket. Line 347 is a CI comment about a skipped gate job. Line 438 is the Makefile line `pytest -q -n auto -m 'not live and not serial'`: it holds `-m 'not` and is not a comment. The next Makefile line runs the one `serial` test alone with `-m 'serial and not live'`, so the test still runs with its 5 s limit (`evidence/AT-6/output.txt` shows "1 passed, 1586 deselected"). No file is deleted. The collected count of each member is the same on both branches, except the scripts, which go from 38 to 45 tests.

## AT-9: The commit hook does not change

App: both
Then: `make check-fast` passes in 30 s or less and prints the same `==>` lines as on `main`. The diff of `prek.toml` is empty.
Files: `evidence/AT-9/output.txt`
Observation: `make check-fast` passed in 37 s on `fast-cycle` and in 36 s on `main` (at `origin/main` `197fb328`), one after the other on the same Mac. Both times are over 30 s. The `==>` lines of the two branches have no difference, and the diff of `prek.toml` has 0 lines.

## AT-10: A full PASS of the Judge passes the check

App: both
Then: The script exits 0 and prints that AT-1, AT-2, and AT-3 have PASS.
Files: `evidence/AT-10/output.txt`
Observation: The unit test `test_at_10_a_full_pass_of_the_judge_exits_0` passes. The direct run of `scripts/verdict.py` on the fixtures prints "0 offenses. AT-1, AT-2, and AT-3 have PASS." and exits 0.

## AT-11: A stale evidence file fails the check

App: both
Then: The script exits 1 with a rule id that names `EVIDENCE.md` as stale.
Files: `evidence/AT-11/output.txt`
Observation: Both unit tests of AT-11 pass. The direct run on a copy with one changed line of `EVIDENCE.md` prints `verdict/stale-evidence` with "EVIDENCE.md is stale: it changed after the Judge read it (2c9190e to 008da98)" and exits 1.

## AT-12: A FAIL of Brian overrides the Judge

App: both
Then: The script exits 1, and its report names AT-2 and the FAIL of Brian.
Files: `evidence/AT-12/output.txt`
Observation: The unit test passes. The direct run with `comments-fail.json` prints `verdict/brian-fail` and "AT-2 has FAIL from Brian." at comment 11, and exits 1.

## AT-13: A newer comment of Brian clears his FAIL

App: both
Then: The script exits 0.
Files: `evidence/AT-13/output.txt`
Observation: The unit test passes. The direct run with `comments-cleared.json` prints "0 offenses. AT-1, AT-2, and AT-3 have PASS." and exits 0.

## AT-14: The Judge agrees with Brian on real evidence

App: both
Then: The Judge writes a `VERDICTS.md` with PASS for each of the 14 tests.
Files: `evidence/AT-14/VERDICTS.md`
Observation: The Judge ran on a copy of the files of `faster-evidence` at `197fb328`, with the brief of `evidence/AT-16/brief.txt`. Its `VERDICTS.md` has PASS for 13 tests and FAIL for AT-14 of `faster-evidence`, with the reason that no file shows that another session made the four new worktrees.

## AT-15: The Judge catches a false observation

App: both
Then: The Judge gives FAIL to AT-2, with a reason that names the mismatch of the Observation and the image. Each other test has PASS.
Files: `evidence/AT-15/changed-observation.diff`, `evidence/AT-15/VERDICTS.md`
Observation: The diff shows the one changed Observation line: `1280-light.png` now "shows the CPC home page on a near-black page with dark cards". A fresh Judge gave FAIL to AT-2: "the Observation says `1280-light.png` shows a near-black page with dark cards, but the file shows a light background". It also gave FAIL to AT-6 of `faster-evidence` (the folder also holds 375 files) and PASS to the other 12 tests, AT-14 included.

## AT-16: The Judge sees only the evidence

App: both
Then: The brief names only the paths of `ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/`. It holds no diff, no ticket, no PRD, and no build note.
Files: `evidence/AT-16/brief.txt`
Observation: The brief is the text of `judge.md`, filled with the paths and the two SHAs of the copy. It names the three input paths and the output path of `VERDICTS.md`, and holds no diff, ticket, PRD, or build note. The brief of AT-15 differs only in the folder `at15` and the SHA of `EVIDENCE.md`.

## AT-17: A second FAIL sets BLOCKED and opens no PR

App: both
Then: `VERDICTS.md` gives BLOCKED to AT-2. No `gh pr create` runs. The message to Brian names AT-2 and the reason of the Judge.
Files: `evidence/AT-17/VERDICTS-round1.md`, `evidence/AT-17/reply-round2.txt`, `evidence/AT-17/VERDICTS-round2.md`, `evidence/AT-17/shell-log.txt`, `evidence/AT-17/message-to-brian.txt`
Observation: The throwaway repo holds the AT-15 files, with AT-2 changed to ask for a purple background. Round 1 gave FAIL to AT-2 and AT-6. The fix round recorded AT-6 again with the whole folder list, and AT-2 got no fix. Round 2, a fresh Judge on AT-2 and AT-6 only, gave BLOCKED to both. The shell log has no `gh pr create` command, only the note line "(no gh pr create runs in this log)", and the repo has no remote. The message to Brian quotes both BLOCKED lines.

## AT-18: Each Judge round is one commit

App: both
Then: Each round is one commit named "Record the Test verdicts of the Judge", and each such commit changes only `VERDICTS.md`.
Files: `evidence/AT-18/git-log-stat.txt`
Observation: The log has two commits named "Record the Test verdicts of the Judge", `ea0d3244` and `2803599f`. Each changes only `.scratch/throwaway/VERDICTS.md`. The fix round sits between them as its own commit, "Record the evidence of throwaway again".

## AT-19: The orchestrator resolves a merge conflict itself

App: both
Then: The merge has a conflict. The orchestrator resolves it in that worktree with `resolving-merge-conflicts` and starts no ticket subagent. `make check-fast BASE=main` is green, and the merge commit stays.
Files: `evidence/AT-19/summary.txt`, `evidence/AT-19/merge.log`, `evidence/AT-19/commit.log`, `evidence/AT-19/check.log`, `evidence/AT-19/subagents.txt`
Observation: The replay merges ticket side `7306d8f5` into spec head `41fb6242`, the real merge-back `ed42aea9` of 2026-11-05 19:17. Three files conflict: `pipeline.py`, `test_layers.py`, and `test_midseason_publish.py`. The resolve kept both sides, the merge commit `8963ae2b` passed the hook, and `make check-fast BASE=main` exited 0 in 49.7 s. The list of subagents started is empty.

## AT-20: A red check after a resolve resets the spec branch

App: both
Then: `make check-fast` fails. The head of the branch is the head before the merge, and the ticket goes back to its subagent with the failure.
Files: `evidence/AT-20/summary.txt`, `evidence/AT-20/bad-resolve.diff`, `evidence/AT-20/check.log`, `evidence/AT-20/reset.log`, `evidence/AT-20/message-to-subagent.txt`
Observation: The bad resolve kept only one side of `pipeline.py`, so `make check-fast BASE=main` exited 2 with ruff `F821 Undefined name 'odds'`. After `git reset --hard 41fb6242`, the head is `41fb62424dd9`, with a clean tree and no `MERGE_HEAD`. The message to the subagent is written after the reset. It is not sent, because the replay starts no subagent.

## AT-21: The review fixes sort into groups that share no file

App: both
Then: Each finding is in one group, and no two groups share a file.
Files: `evidence/AT-21/group_findings.py`, `evidence/AT-21/output.md`
Observation: The commits of `midseason-report` name 29 findings, not 35: K-1 to K-15, S-1 to S-11, and P-4 to P-6. S-8 and S-9 have no fix commit, so 27 go into groups. The script sorts them into 6 groups, and its check prints "Each finding in exactly one group: True" and "Pairs of groups that share a file: 0". Group a holds 18 of the 27 findings.

## AT-22: The background full check adds no wait

App: both
Then: `make check` starts within 1 min of the stage start. It ends green before the push of the PR. The push waits 0 min for it, because it ended before the last evidence file.
Files: `evidence/AT-22/output.txt`
Observation: The stage started at 13:08:43, and `make check` started at 13:08:43, 0 min later. It ended at 13:10:37 with exit 2: the site rules test at `evidence-rules.spec.ts:365` hit `EADDRINUSE 127.0.0.1:4173`, because a preview server of another session held that port. The members that it did not reach passed one at a time by 13:13:29. A second site run at 13:24 hit the same port error, because the other session started its server again at 13:18:55. The first push was at 13:27:24, so the push did not wait, but the full check did not end green before it.

## AT-23: The midseason tests share a build

App: pipeline
Then: Both runs pass the same count of tests. The run on `fast-cycle` takes less time.
Files: none
Observation: Not recorded: ticket 07 is blocked until PR #13 merges into `main`.

## AT-24: The full sim count stays

App: pipeline
Then: Each count is the same on both branches.
Files: none
Observation: Not recorded: ticket 07 is blocked until PR #13 merges into `main`.

## AT-25: The glossary defines the Judge

App: both
Then: The glossary defines **Judge**, and **Test verdict** as the word of the Judge that a FAIL of Brian overrides. ADR 0020 says that ADR 0026 supersedes it.
Files: `evidence/AT-25/output.txt`
Observation: The Workflow section defines **Test verdict** as "The word PASS, FAIL, or BLOCKED that the Judge gives to one acceptance test ... A FAIL from Brian overrides it." It defines **Judge** as "The subagent that reads only the acceptance tests and their evidence". The head of ADR 0020 says "Superseded by ADR 0026".

## AT-26: PR #13 merges before this spec

App: both
Then: PR #13 has the state `MERGED`.
Files: `evidence/AT-26/output.txt`
Observation: `gh pr view 13` gives `{"mergedAt":null,"state":"OPEN"}`. Ticket 07, which owns this test, is blocked until PR #13 merges.

## AT-27: CI runs every member for a small change

App: both
Then: All five jobs run their check. No job skips its member because of the changed paths.
Files: `evidence/AT-27/run.json`, `evidence/AT-27/steps.txt`, `evidence/AT-27/cleanup.txt`
Observation: CI_PENDING

## AT-28: The spec adds no ruleset

App: both
Then: Both return an empty list, as before this spec.
Files: `evidence/AT-28/output.txt`
Observation: `gh api repos/{owner}/{repo}/rulesets` returns `[]`, and `gh api repos/{owner}/{repo}/rules/branches/main` returns `[]`.

## AT-29: The build stage starts no review per ticket

App: both
Then: Stage 1 calls no `code-review`. The only `code-review` call is in stage 2, on the whole spec branch.
Files: `evidence/AT-29/output.txt`
Observation: `grep -n code-review build.md` finds one line, line 85. The headings put line 85 under "## Stage 2: the review", which starts at line 83. Stage 1 runs from line 12 to line 82.

## AT-30: The tickets get no overlap edges

App: both
Then: The diff is empty.
Files: `evidence/AT-30/output.txt`
Observation: The diff of `.claude/plugin/skills/to-tickets` against `origin/main` has 0 lines.
