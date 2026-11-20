# 03: Which design rules ship, and which tool runs each one

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** open

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

None yet.
