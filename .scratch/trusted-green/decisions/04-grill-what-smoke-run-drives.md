# 04: What a smoke run drives

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** open

## Question

A smoke run boots the site and the API and drives the flow that a change touches. Brian decides how `verify` picks the flows from a diff: a list of flows with paths and expected results, as the article suggests, or the routes the diff touches. Brian also decides if `verify` reuses the evidence runner (`apps/site/e2e/evidence.ts`) and `make -C apps/api api-evidence`, and which files go to the Judge.

## Decision

None yet.
