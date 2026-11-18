# 07: How the re-run job finds its loop

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

A CI job reads its script from `main`, like `verdict.yml`. It runs the command of each Red block at the red commit and of each Green block at the fix commit. The spec sets how the job finds the quick file of the PR, the command, and the two commits. It also sets the setup that a site loop needs, such as a client build, and what the job does with a PR that has no quick file.

## Decision

Recorded in `PRD.md` under Implementation Decisions, approved by Brian on 2026-11-18. The re-run job finds the quick file of the PR, runs Red at the red commit and Green at the fix commit, and passes a PR with no quick file.
