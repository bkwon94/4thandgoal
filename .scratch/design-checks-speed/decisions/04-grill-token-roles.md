# 04: The role name of each token that is not a role

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The color tokens already name a role, such as `--color-accent` and `--color-card`. Some tokens do not:

1. The spacing steps, such as `--spacing-sp-2` and `--spacing-sp-6`.
2. The timings of one component each, such as `--es-dur` and `--oc-dur`.
3. The repeated arbitrary values that ticket 03 removes, such as `color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))`. Each one needs a new token.

Decide the role name of each one, or decide that a scale step stays a scale step. The look tokens live in `apps/site/src/app/globals.css` (ADR 0024). The skill `token-mapping` can give a report first.

## Decision

Brian decided on 2026-11-20 in a grill:

1. The look tokens have two tiers. A scale step, such as `--spacing-sp-2`, names one size and has no role. A role token, such as `--spacing-gutter`, names a role and may point at a step. The spacing scale `--spacing-sp-0` to `--spacing-sp-6` stays a scale, with about 1,200 uses. The design rule is: a part uses a role token where one exists, and a scale step for the rest.
2. `--oc-dur` and `--es-dur` are not tokens. The part writes each one at runtime from its spring sampler, and writes `0s` for reduced motion. They stay as they are.
3. Three role tokens replace the chip washes of `apps/site/src/app/front-door/site-answer.tsx`. Each dark value lives in the dark block of `apps/site/src/app/globals.css`, so the `dark:bg-[...]` classes go away.

| Token | Light | Dark |
| --- | --- | --- |
| `--color-accent-wash` | `--color-accent` 10% into `--color-card` | `--color-raised` |
| `--color-accent-wash-chosen` | `--color-accent` 20% into `--color-card` | `--color-accent` 24% into `--color-raised` |
| `--color-accent-wash-hover` | `--color-accent` 28% into `--color-card` | `--color-accent` 34% into `--color-raised` |

4. The blurs and the safe-area `calc` are one-offs. Each keeps a one-line ignore comment with a reason.
5. The `color-mix` of `packages/design/site/ui/button.tsx` uses the shadcn names `--secondary` and `--foreground`. Ticket 03 decides whether the check covers `ui/`.

The reason: a rename of the scale buys little, because most gaps are only a small gap. The two tiers are the common shape of a design system. `GLOSSARY.md` now has the terms **Role token** and **Scale step**.
