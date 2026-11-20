# 04: The role name of each token that is not a role

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** open

## Question

The color tokens already name a role, such as `--color-accent` and `--color-card`. Some tokens do not:

1. The spacing steps, such as `--spacing-sp-2` and `--spacing-sp-6`.
2. The timings of one component each, such as `--es-dur` and `--oc-dur`.
3. The repeated arbitrary values that ticket 03 removes, such as `color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))`. Each one needs a new token.

Decide the role name of each one, or decide that a scale step stays a scale step. The look tokens live in `apps/site/src/app/globals.css` (ADR 0024). The skill `token-mapping` can give a report first.

## Decision

None yet.
