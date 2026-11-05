# The PR

Stage 4 of `cpc:implement`. One PR goes from the Spec branch `<slug>` to `main`. Brian merges it as a squash, on his Test verdicts.

## The agent marker

The `gh` CLI of the agent and Brian share one GitHub account. So the marker `<!-- cpc:agent -->` is the only sign that an agent wrote a comment. End each PR comment that an agent writes with the marker on its own last line. The verdict check ignores each comment with the marker.

Never write the line `Test verdicts` in a comment. Never write `AT-<n>: PASS`, `FAIL`, or `BLOCKED` in a comment.

## Open the PR

1. Push the Spec branch: `git push -u origin <slug>`.
2. Get the base of the links: `gh repo view --json url --jq .url`, then `<url>/blob/<short sha>/.scratch/<slug>/`. The sha is the head after the evidence commit.
3. Write the body below to a file in the scratchpad.
4. Run `gh pr create --base main --head <slug> --title "<the PRD title>" --body-file <file>`. Add `--draft` if a ticket is `blocked`.

The body:

````markdown
## The spec

<two or three sentences from the Problem Statement and the Solution of the PRD.>

Spec: `.scratch/<slug>/PRD.md`. Acceptance tests: `.scratch/<slug>/ACCEPTANCE.md`. Evidence: [EVIDENCE.md](<link base>EVIDENCE.md).

## The tickets

| Ticket | Status | Commits | Tests |
| --- | --- | --- | --- |
| 01 <title> | in-review | `abc1234` | AT-1, AT-2 |

## The review

<"code-review found no finding.", or each finding that is not fixed: the id, the finding, and the reason.>

## The acceptance tests

- AT-1: <title>. Evidence: [AT-1](<link base>evidence/AT-1/)
- AT-2: <title>. Evidence: [AT-2](<link base>evidence/AT-2/)

## Your Test verdicts

The agent gives no Test verdict. Brian, write one new comment on this PR in this shape. Put PASS, FAIL, or BLOCKED after each id, then an optional note:

```text
Test verdicts
AT-1:
AT-2:
```

The check `verdict` reads your latest comment that holds the line `Test verdicts`. It passes when every test has PASS. Then run `cpc:review <PR number>` for a FAIL, a BLOCKED, or a review comment.
````

## The full check

The CI check `Check` runs `make check` on the PR. It is the one full check of the Spec branch.

1. Wait for it: `gh pr checks <PR number> --watch`.
2. If it fails, read the log with `gh run view <run id> --log-failed`. Fix the cause on the Spec branch in its own commit, then push.
3. Wait for the check again.

**Stop rule of stage 4.** If the push or `gh pr create` fails, stop. Tell Brian the command and its error. If the check `Check` fails two times, stop. Tell Brian the failed test and the commit that broke it.

## A second start

The Spec branch has an open PR when `gh pr list --head <slug> --state open` lists one.

1. If no ticket is `blocked`, stop. Tell Brian to run `cpc:review <PR number>`.
2. Otherwise, read the PR comments for the decision of Brian on each blocked ticket. If a blocked ticket has no decision, stop and ask Brian.
3. Build each blocked ticket and each ticket behind it with stage 1. A ticket branch that exists gets its worktree with `git worktree add .claude/worktrees/<slug>-<NN> <slug>-<NN>`, then a merge of `<slug>` into it.
4. Run stage 2 with the fixed point at the head of the previous push.
5. Run stage 3 for the tests of the new tickets only. Add their entries to `EVIDENCE.md`.
6. Push. Post one comment that lists the new commits and the new evidence links, with the agent marker.
7. If no ticket is `blocked` now, run `gh pr ready <PR number>`.
