# 08: What steps fill the Ready halo?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The Ready halo on the submit button of the Stack gets brighter as the trade fills. The spec must name the steps, for example teams chosen, then players added on each side, and the level of glow at each step. It must also say how the halo looks with reduced motion and in the light theme.

## Decision

The spec records it under Ready halo, approved by Brian on 2026-11-07. Each side has three checks: a team, at least one player it gets, and at least one player it gives. The level is the passed checks over three times the count of sides. The glow reaches full only when the ready rule passes. It uses the accent role, so it works in both themes. Reduced motion keeps the brightness change and drops any pulse.
