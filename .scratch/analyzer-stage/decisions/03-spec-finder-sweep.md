# 03: Does the Finder wait take the new loader

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** spec

**Blocked by:** 01

**Status:** done

## Question

The grade wait and the Finder wait share `Sweep` in `packages/analyzer/site/form/sweep.tsx`. If decision 01 replaces `Sweep` in the hero, the spec must say if the Finder wait takes the new loader or keeps `Sweep`. The Finder is off in cpc now, so a change there has a small reach.

## Decision

Recorded in the spec `PRD.md`, under "The Finder", approved by Brian on 2026-11-16. The Finder wait keeps `Sweep`, because a Finder search has no trade on stage for the mesh to weigh. The grade wait no longer uses `Sweep`.
