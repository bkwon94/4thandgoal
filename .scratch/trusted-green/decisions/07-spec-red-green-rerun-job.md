# 07: How the re-run job finds its loop

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** open

## Question

A CI job reads its script from `main`, like `verdict.yml`. It runs the command of each Red block at the red commit and of each Green block at the fix commit. The spec sets how the job finds the quick file of the PR, the command, and the two commits. It also sets the setup that a site loop needs, such as a client build, and what the job does with a PR that has no quick file.

## Decision

None yet.
