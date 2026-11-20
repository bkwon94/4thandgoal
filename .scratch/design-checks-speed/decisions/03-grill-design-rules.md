# 03: Which design rules ship, and which tool runs each one

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

The spec needs the final list of design rules and the tool of each. The candidates:

1. No `@ui-sdk/*` import outside `packages/design/site/ui/` (ADR 0035). `apps/site/src/ui-sdk-rule.test.ts` checks this now. Decide whether it moves to the linter.
2. No raw color in a `.tsx` or `.css` file.
3. No raw `<button>` or `<dialog>` outside `ui/`. Eight files use a raw `<button>` today.
4. No arbitrary Tailwind value where a token exists. Fourteen exist today, most of them a `color-mix` of `--color-accent`.
5. Each part file of `ui/` and `parts/` has the "Use it when" and "Do not use it when" lines in its top docstring.
6. The three timing rules of landmines, from `.scratch/landmines/research.notes.md`.

The tool is `bun lint` if ticket 01 finds custom rules in it. Otherwise it is Oxlint with a small plugin, or a script in `scripts/` like `retry_rule.py`.

## Decision

Brian decided on 2026-11-20 in a grill:

1. One Oxlint config runs the rules, with one local ESLint-style plugin at `packages/design/lint/`. Oxlint `jsPlugins` and canary `bun lint` run the same plugin file, so it moves to `bun lint` with no rewrite.
2. The `@ui-sdk/*` import rule moves to the built-in `no-restricted-imports`, with `packages/design/site/ui/` as the one allowed path. `apps/site/src/ui-sdk-rule.test.ts` goes away, so all design rules live in one place.
3. The landmines timing rules stay out. They know Vitest names that this spec removes. The Quick Win in the queue runs after this spec merges.
4. The rule set. "All site code" means `apps/site/src` and `packages/*/site`. Test files are exempt from the element and value rules.

| Rule | Source | Scope | Fails on 2026-11-20 |
| --- | --- | --- | --- |
| `@ui-sdk/*` import only in `ui/` | built-in `no-restricted-imports` | all site code | 0 |
| no raw color literal: hex, `rgb()`, `hsl()`, `oklch()` | plugin | `.tsx` files | 0 |
| no raw `<button>` or `<dialog>` | plugin | all site code except `ui/` | 8 files |
| no arbitrary value in the color and spacing groups | plugin | all site code, `ui/` included | 32 uses |
| each exported part has the "Use it when" and "Do not use it when" lines | plugin | `ui/` and `parts/` | about 33 files |

5. The value rule fails only the prefixes `bg-`, `text-`, `border-`, `ring-`, `fill-`, `stroke-`, `shadow-`, and the padding, margin, gap, and inset prefixes. Variants such as `data-[...]`, layout values such as `grid-cols-[...]`, and motion values such as `transition-[...]` stay allowed. There are 259 arbitrary values in all.
6. Each of the 32 uses gets a fix or a one-line ignore with a reason. A `calc` that equals a token becomes the token, such as `top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]`, which is `--spacing-band-height`.
7. The `.css` files hold raw values in the token definitions of `globals.css`, so the raw color rule covers only `.tsx`.
8. `make check-fast` gets a lint step on the staged files only, so the hook stays fast. CI runs the full lint in the site-unit job. `bun fmt` runs in check mode in both places.
