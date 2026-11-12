---
name: implement
description: Build the tickets of one feature of this repo on its Spec branch, one Ticket branch and worktree per ticket, then review the change, record the evidence of each acceptance test, and open one PR to main. Use after 4ag:to-tickets, when Brian names a feature under .scratch/ with a PRD, an ACCEPTANCE.md, and tickets.
argument-hint: '<feature slug>'
---

# Implement

Build one spec and open its PR. The Spec branch `<slug>` holds the work. Each ticket builds on its own Ticket branch `<slug>-<NN>` and merges into the Spec branch. One PR goes from the Spec branch to `main`. Brian merges it when the check `verdict` is green (ADR 0019, ADR 0026).

The agent records the evidence of each acceptance test. The agent never gives a Test verdict, because the agent wrote the code. A fresh subagent, the Judge, gives each Test verdict.

## Before you start

1. Check that these global skills are in the available skill list: `tdd`, `code-review`, `resolving-merge-conflicts`, `agent-browser`. The `cpc` skills ship with this skill, so do not check them.
2. If one is missing, stop. Tell Brian the name of the missing skill. Do not guess its steps.
3. Check that the sandbox allows a write to `.git` and a call of `gh`. Each probe is a read that changes nothing. Run these two commands in the main checkout:
   - `test -w "$(git rev-parse --git-common-dir)"`
   - `gh api repos/{owner}/{repo} --jq .name`
4. If one fails, stop. Tell Brian that the session needs the permission profile `4ag` of `.codex/config.toml`. Quote the error. Make no worktree and no branch.
5. Run `gh auth status`. If it fails, stop. Tell Brian to run `gh auth login`.
6. Check that `.scratch/<slug>/PRD.md`, `.scratch/<slug>/ACCEPTANCE.md`, and `.scratch/<slug>/issues/` exist on the Spec branch or on `main`. If one is missing, stop. Name the skill that writes it: `4ag:to-spec`, `4ag:to-acceptance`, or `4ag:to-tickets`.
7. Read the PRD, `ACCEPTANCE.md`, each ticket, `docs/agents/issue-tracker.md`, and the Workflow section of `GLOSSARY.md`.

## The stages

Do the stages in order. Each stage has a stop rule. When a stop rule fires, do not go to the next stage.

1. **The build.** Make the worktrees, build each ticket with a subagent, and merge each ticket into the Spec branch. See [`build.md`](build.md).
2. **The review.** Run `code-review` on the Spec branch against `main`, and fix the findings. See [`build.md`](build.md#stage-2-the-review).
3. **The evidence.** Record the evidence of each `AT-<n>` and write `EVIDENCE.md`. See [`evidence.md`](evidence.md).
4. **The Judge.** Start a fresh Judge, commit its `VERDICTS.md`, and do one fix round after a FAIL. See [`judge.md`](judge.md).
5. **The PR.** Push the Spec branch and open one PR to `main`. See [`pr.md`](pr.md).

## The rules

- Run each `git worktree` command in the main checkout. Commit only in a worktree, never on `main`.
- Never use `--no-verify`. Never force-push. Never merge to `main`. Brian merges the PR.
- Set a ticket to `in-review` after its merge into the Spec branch. Before the push of stage 5, set each `in-review` ticket to `done` and remove the feature row from `docs/agents/state.md`, in one commit. A `blocked` ticket stays open. See [`pr.md`](pr.md#close-the-tickets).
- The squash merge puts `done` on `main`. A PR that never merges never puts `done` on `main`.
- Never write a Test verdict. Never change a line of `VERDICTS.md`: only the Judge writes it. See [`judge.md`](judge.md).
- Never write the line `Test verdicts` in a PR comment. See [`pr.md`](pr.md#the-agent-marker).

## A second start

If the Spec branch already has an open PR, read [`pr.md`](pr.md#a-second-start).

## The end

Give Brian the PR address and the Test verdicts of the Judge. Brian needs to post no comment. He may check the work on the local dev server. A FAIL from Brian in a PR comment blocks the merge. Tell Brian to run `4ag:review <PR number>` for a FAIL or a review comment.

If stage 4 ends with a BLOCKED test, no PR opens. Give Brian each BLOCKED test and the reason of the Judge.
