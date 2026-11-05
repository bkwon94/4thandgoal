---
name: review
description: Do one round of feedback on a spec PR of this repo. Read the open review comments and the latest Test verdicts comment of Brian, then make a correction commit or a reply for each, push, and post a summary. Use when Brian finishes a round of comments on a PR that cpc:implement opened.
argument-hint: '<PR number>'
---

# Review

Do one round of feedback on one spec PR. One run is one round. Brian starts the next round when he finishes his next comments.

The agent never writes a Test verdict. Only Brian gives PASS, FAIL, or BLOCKED (ADR 0020).

## Before you start

1. Check that these global skills are in the available skill list: `tdd`, `agent-browser`. If one is missing, stop. Tell Brian the name of the missing skill. Do not guess its steps.
2. Run `gh auth status`. If it fails, stop. Tell Brian to run `gh auth login`.
3. Read the PR: `gh pr view <PR number> --json number,state,baseRefName,headRefName,headRefOid,url`. If it is not open, or its base is not `main`, stop and tell Brian.
4. The head branch is the Spec branch `<slug>`. Find its worktree with `git worktree list`. If it has none, run `git worktree add .claude/worktrees/<slug> <slug>` in the main checkout. Do the setup of the worktree in [`../implement/build.md`](../implement/build.md#the-setup-of-a-worktree).
5. Run `git pull --ff-only` in the worktree. Read `.scratch/<slug>/PRD.md` and `.scratch/<slug>/ACCEPTANCE.md`.

## Steps

1. Read the comments with the commands of [`github.md`](github.md). Find each comment that needs an action:
   - Each review thread that is not resolved, and whose last comment has no agent marker `<!-- cpc:agent -->`.
   - Each PR comment with no marker that is later than the last round comment of the agent. In the first round, each PR comment with no marker counts.
2. Judge the latest Test verdicts comment with the verdict script, as [`github.md`](github.md#the-test-verdicts) shows. Each test with FAIL or BLOCKED needs an action.
3. Act on each item with the table below.
4. Run `make check-fast BASE=main` in the worktree. If it fails, fix it before the push. If you cannot fix it, stop and tell Brian. The CI check `Check` on the PR runs the full check after the push.
5. Push with a plain `git push`. Never force-push, never squash, and never use `--no-verify`.
6. Reply to each comment, as [`github.md`](github.md#replies) shows. End each reply with the agent marker.
7. Post one round comment: the line `Feedback round <n>`, then one line for each action, then the agent marker. Give Brian the same list in the session.

| Item | Action |
| --- | --- |
| A change request | One correction commit, and a reply with the commit id. |
| A question | A reply with the answer. No change. |
| A conflict with the spec, an ADR, or an approved test | A reply that names the conflict. No change. |
| A test with FAIL | A correction commit, built with `tdd` when it changes behavior. Then new evidence with [`../implement/evidence.md`](../implement/evidence.md), committed, and a reply with the commit id and the new evidence link. |
| A test with BLOCKED | A reply that names what the test needs. If the agent can supply it, such as a missing evidence file, supply it and reply with the link. |
| A test with PASS | No action. A PASS stays valid after a correction commit. |
| A change to an approved acceptance test | A reply that tells Brian to change the test with `cpc:to-acceptance`. No change. |
| A decision for a blocked ticket | A reply that tells Brian to run `cpc:implement <slug>`. This skill builds no ticket. |

## The rules

- Record new evidence only for the tests that get a fix, or that Brian names.
- Never write the line `Test verdicts`, and never write `AT-<n>: PASS`, `FAIL`, or `BLOCKED`, in a comment or a reply.
- Brian resolves each thread. The agent does not.
- Leave the tracker as it is. Set no ticket to `done`.

## The end

The round is done when each item of steps 1 and 2 has a reply, and the round comment is on the PR. Tell Brian to write a new Test verdicts comment for each test that changed.
