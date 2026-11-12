# The PR

Stage 5 of `4ag:implement`. One PR goes from the Spec branch `<slug>` to `main`. Brian merges it as a squash, when the check `verdict` is green. The check reads the Test verdicts of the Judge in `VERDICTS.md` (ADR 0026).

## The agent marker

The `gh` CLI of the agent and Brian share one GitHub account. So the marker `<!-- cpc:agent -->` is the only sign that an agent wrote a comment. End each PR comment that an agent writes with the marker on its own last line. The verdict check ignores each comment with the marker.

Never write the line `Test verdicts` in a comment. Never write `AT-<n>: PASS`, `FAIL`, or `BLOCKED` in a comment.

## Close the tickets

Do this before the push. The squash merge of the PR then puts `done` on `main`.

1. Set the Status of each `in-review` ticket to `done`.
2. Add the close comment under `## Comments` of each ticket, per the close comment rule in `docs/agents/issue-tracker.md`. The text is "Closes with the squash merge of the spec PR."
3. If no ticket of the feature is open now, remove its row from `docs/agents/state.md`. If a ticket is still open, set Next ticket to the lowest open number.
4. Run the tracker rule tests: `apps/pipeline/tests/test_rule_tracker.py` and `apps/site/src/tracker-rule.test.ts`.
5. Commit with the message `Close the <slug> tickets`.

A `blocked` ticket stays open, so its feature keeps its row.

## Open the PR

1. Push the Spec branch: `git push -u origin <slug>`.
2. Get the base of the links: `gh repo view --json url --jq .url`, then `<url>/blob/<short sha>/.scratch/<slug>/`. The sha is the head after the last commit of stage 4.
3. Write the body below to a file in the scratchpad.
4. Run `gh pr create --base main --head <slug> --title "<the PRD title>" --body-file <file>`. Add `--draft` if a ticket is `blocked`.

The body:

````markdown
## The spec

<two or three sentences from the Problem Statement and the Solution of the PRD.>

Spec: `.scratch/<slug>/PRD.md`. Acceptance tests: `.scratch/<slug>/ACCEPTANCE.md`. Evidence: [EVIDENCE.md](<link base>EVIDENCE.md). Test verdicts of the Judge: [VERDICTS.md](<link base>VERDICTS.md).

## The Evidence flags

<one line of counts of the `evidence-flags` run, from `.scratch/<slug>/FLAGS.md`, such as "9 flags: 5 new recordings, 1 fix group, 3 disagreements". Write "0 flags." if the file has no entry or does not exist.>

## The tickets

| Ticket | Status | Commits | Tests |
| --- | --- | --- | --- |
| 01 <title> | done | `abc1234` | AT-1, AT-2 |

## The review

<"code-review found no finding.", or each finding that is not fixed: the id, the finding, and the reason.>

## The acceptance tests

- AT-1: <title>. Evidence: [AT-1](<link base>evidence/AT-1/)
- AT-2: <title>. Evidence: [AT-2](<link base>evidence/AT-2/)

## The Test verdicts

The Judge, a fresh subagent that did not build the work, gave each Test verdict in [VERDICTS.md](<link base>VERDICTS.md). The check `verdict` passes when each test has PASS. Brian needs to post no comment.

To block the merge, Brian posts one comment with the heading `Test verdicts` and a line `AT-<n>: FAIL <note>` for each failed test. Then run `4ag:review <PR number>`.
````

## The full check

The CI check `Check` runs `make check` on the PR. It is the one full check of the Spec branch.

1. Wait for it: `gh pr checks <PR number> --watch`.
2. If it fails, read the log with `gh run view <run id> --log-failed`. Fix the cause on the Spec branch in its own commit, then push.
3. Wait for the check again.

**Stop rule of stage 5.** If the push or `gh pr create` fails, stop. Tell Brian the command and its error. If the check `Check` fails two times, stop. Tell Brian the failed test and the commit that broke it.

## A second start

The Spec branch has an open PR when `gh pr list --head <slug> --state open` lists one.

1. If no ticket is `blocked`, stop. Tell Brian to run `4ag:review <PR number>`.
2. Otherwise, read the PR comments for the decision of Brian on each blocked ticket. If a blocked ticket has no decision, stop and ask Brian.
3. Build each blocked ticket and each ticket behind it with stage 1. A ticket branch that exists gets its worktree with `git worktree add .claude/worktrees/<slug>-<NN> <slug>-<NN>`, then a merge of `<slug>` into it.
4. Run stage 2 with the fixed point at the head of the previous push.
5. Run stage 3 for the tests of the new tickets only. Add their entries to `EVIDENCE.md`.
6. Run stage 4 for the tests of the new tickets only, with the lines of "Some tests only" of [`judge.md`](judge.md#some-tests-only). A FAIL gets its one fix round. If a test has BLOCKED, stop. Push nothing, and tell Brian the test and the reason of the Judge.
7. Close the new tickets with [Close the tickets](#close-the-tickets).
8. Push. Post one comment that lists the new commits and the new evidence links, with the agent marker.
9. If no ticket is `blocked` now, run `gh pr ready <PR number>`.
