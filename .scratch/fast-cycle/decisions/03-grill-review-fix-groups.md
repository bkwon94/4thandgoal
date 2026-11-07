# 03: How the review fixes run

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

On `midseason-report`, one `code-review` gave about 35 findings. The fixes took 1.7 h, one commit at a time, then on fix branches that the agent improvised.

## Decision

Brian decided on 2026-11-06, in a grill.

Keep one `code-review` on the whole spec branch. The orchestrator sorts the findings into groups that share no file. One subagent per group fixes its findings on a fix branch, one commit per finding, with the hook. Each group merges back under the rule of decision 02.

A review per ticket was rejected for now: it changes more and starts more subagents.
