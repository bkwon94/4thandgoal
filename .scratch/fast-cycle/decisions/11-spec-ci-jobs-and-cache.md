# 11: The CI jobs, the Chromium cache, and the deploy triggers

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** spec

**Blocked by:** 04, 09

**Status:** done

## Question

The spec must set the job list, the needs of the gate job `check`, the cache key of Chromium, the job timeouts, and how `deploy-api.yml` and `deploy-sites.yml` still start from `workflow_run` of the workflow `Check`.

Decision 09 adds one rule: two `uv run --exact --package` runs of different members in one checkout break each other. Each CI job runs one member, or runs the members one after another. The background `make check` of decision 05 runs alone in its worktree.

## Decision

The spec decided it on 2026-11-06. See "CI (decisions 04, 09, and 11)" under Implementation Decisions of `.scratch/fast-cycle/PRD.md`.
