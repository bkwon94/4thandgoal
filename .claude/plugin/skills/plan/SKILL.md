---
name: plan
description: Take an idea for this repo to a map, decision tickets, a spec, acceptance tests, and tickets in the local tracker. Use when Brian gives an outcome statement for a new feature, or names a feature under .scratch/ whose fog is not clear yet.
argument-hint: '<outcome statement> | <feature slug> [decision ticket number]'
---

# Plan

An idea arrives with fog: parts of the feature that are not specified yet. This skill writes a map of the fog, turns each fog item into a decision ticket, and clears one decision ticket per session. When no fog is left, it hands off to `4ag:to-spec`, `4ag:to-acceptance`, and `4ag:to-tickets`.

A decision ticket records a choice. It writes no product code. If you want to build something, you are at the edge of the map: that is the spec.

## Before you start

1. Check that these global skills are in the available skill list: `grilling`, `domain-modeling`, `research`, `prototype`. The `4ag` skills ship with this skill, so do not check them.
2. If one is missing, stop. Tell Brian the name of the missing skill. Do not guess its steps.
3. Read `docs/agents/issue-tracker.md` and the Workflow section of `GLOSSARY.md`.

## Invocation

| Command | Stage |
| --- | --- |
| `/4ag:plan <outcome statement>` | Stage 1: write the map. |
| `/4ag:plan <feature slug>` | Stage 2: clear the next open decision ticket, or hand off. |
| `/4ag:plan <feature slug> <NN>` | Stage 2, for the decision ticket that Brian names. |

## The human side

Grill and prototype tickets need Brian. Never answer a question for Brian. Wait for the answer from Brian, then record it.

## Stage 1: write the map

The outcome statement has two parts: what the feature does, and the goal that it serves. If one part is missing, ask for it first.

1. Load the skill `grilling` and the skill `domain-modeling`. Settle the destination with Brian: the one spec this feature ends in.
2. Grill again, breadth first. Ask which app the feature touches: `site`, `pipeline`, or both. Ask which seam moves. Ask which term conflicts with `GLOSSARY.md`.
3. Choose a feature slug of two to four lowercase words with hyphens. Check that `.scratch/<slug>/` does not exist.
4. Make the Spec branch `<slug>` from `main` in its own worktree. Run this in the main checkout: `git worktree add .claude/worktrees/<slug> -b <slug> main`. Write every file of the feature there.
5. If no fog is left, skip the map. Ask Brian to confirm. Then go to [`build-out.md`](build-out.md).
6. Write `.scratch/<slug>/MAP.md` in the format of [`formats.md`](formats.md).
7. Write one decision ticket for each fog item at `.scratch/<slug>/decisions/<NN>-<kind>-<slug>.md`. Number from `01`. See [`formats.md`](formats.md) for the kind and the format.
8. Do not add a row to `docs/agents/state.md`. The tracker rule fails a row for a feature with no open ticket. `4ag:to-tickets` adds the row.
9. Commit the map and the decision tickets on the Spec branch. Then stop. Stage 1 clears no decision ticket.

## Stage 2: clear one decision ticket

1. Work in the worktree of the Spec branch `<slug>`. Read `.scratch/<slug>/MAP.md`. Read the Kind, Blocked by, and Status lines of each decision ticket: `grep -H '^\*\*' .scratch/<slug>/decisions/*.md`.
2. Choose the decision ticket that Brian names. Otherwise choose the lowest open number whose blockers are done. A `spec` ticket comes last.
3. If no ticket is open except `spec` tickets, go to [`build-out.md`](build-out.md).
4. Clear the ticket by its kind:
   - `grill`: load the skill `grilling` and the skill `domain-modeling`.
   - `research`: load the skill `research`. Tell it to write its findings beside the ticket, at `.scratch/<slug>/decisions/<NN>-research-<slug>.notes.md`.
   - `prototype`: load the skill `prototype`. Record what the prototype answered, then delete the prototype code.
5. Write the decision under `## Decision` of the ticket. Set its Status to `done`.
6. Move the fog item from NOT YET SPECIFIED to DECISIONS SO FAR on the map, as one line with the gist and the ticket path.
7. If the decision shows new fog, add it to the map and add a decision ticket for it. If it shows work past the destination, add it to OUT OF SCOPE with the reason.
8. If a decision needs an ADR or a glossary term, write it with `domain-modeling` now.
9. Commit the ticket, the map, and any record on the Spec branch. Then stop. Clear one decision ticket per session. A research ticket may run in the background while you clear the next one.
