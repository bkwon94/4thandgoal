---
name: implement
description: Build the tickets of one feature of this repo on its Spec branch, one Ticket branch and worktree per ticket, then review the change, record the evidence of each acceptance test, and open one PR to main. Use after cpc:to-tickets, when Brian names a feature under .scratch/ with a PRD, an ACCEPTANCE.md, and tickets.
argument-hint: '<feature slug>'
---

# Implement

Build one spec and open its PR. The Spec branch `<slug>` holds the work. Each ticket builds on its own Ticket branch `<slug>-<NN>` and merges into the Spec branch. One PR goes from the Spec branch to `main`. Brian merges it on his Test verdicts (ADR 0019, ADR 0020).

The agent records the evidence of each acceptance test. The agent never gives a Test verdict, because the agent wrote the code.

## Before you start

1. Check that these global skills are in the available skill list: `tdd`, `code-review`, `resolving-merge-conflicts`, `agent-browser`. The `cpc` skills ship with this skill, so do not check them.
2. If one is missing, stop. Tell Brian the name of the missing skill. Do not guess its steps.
3. Run `gh auth status`. If it fails, stop. Tell Brian to run `gh auth login`.
4. Check that `.scratch/<slug>/PRD.md`, `.scratch/<slug>/ACCEPTANCE.md`, and `.scratch/<slug>/issues/` exist on the Spec branch or on `main`. If one is missing, stop. Name the skill that writes it: `cpc:to-spec`, `cpc:to-acceptance`, or `cpc:to-tickets`.
5. Read the PRD, `ACCEPTANCE.md`, each ticket, `docs/agents/issue-tracker.md`, and the Workflow section of `GLOSSARY.md`.

## The stages

Do the stages in order. Each stage has a stop rule. When a stop rule fires, do not go to the next stage.

1. **The build.** Make the worktrees, build each ticket with a subagent, and merge each ticket into the Spec branch. See [`build.md`](build.md).
2. **The review.** Run `code-review` on the Spec branch against `main`, and fix the findings. See [`build.md`](build.md#stage-2-the-review).
3. **The evidence.** Record the evidence of each `AT-<n>` and write `EVIDENCE.md`. See [`evidence.md`](evidence.md).
4. **The PR.** Push the Spec branch and open one PR to `main`. See [`pr.md`](pr.md).

## The rules

- Run each `git worktree` command in the main checkout. Commit only in a worktree, never on `main`.
- Never use `--no-verify`. Never force-push. Never merge to `main`. Brian merges the PR.
- Set a ticket to `in-review` after its merge into the Spec branch. Only Brian sets a ticket to `done`.
- Never write a Test verdict. Never write the line `Test verdicts` in a PR comment. See [`pr.md`](pr.md#the-agent-marker).

## A second start

If the Spec branch already has an open PR, read [`pr.md`](pr.md#a-second-start).

## The end

Give Brian the PR address. Tell Brian to write the Test verdicts comment, then to run `cpc:review <PR number>` for a round of feedback.
