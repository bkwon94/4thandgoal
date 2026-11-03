# Cornerstone site

The Next.js site. It renders each `public/<season>/week-NN/page.json` and its images, which the pipeline publishes.
The root CLAUDE.md holds the style, the flow, and the tracker.

## Commands

Run these in `apps/site/`.

- Install: `pnpm install`
- Dev server: `pnpm dev`
- Build the static export: `pnpm build`
- Test: `pnpm test`
- Check the export: `pnpm check:export`. Run it after `pnpm build`.
- Check all: `pnpm check`. It runs typecheck, test, build, and `check:export`. CI runs it on every push.
- Fast check: `pnpm check:fast`. It runs typecheck and test. The hook runs it.

## Rules

- The hook does not run `pnpm install`. In a new worktree with no `node_modules`, run `pnpm install` first.
- The pipeline owns the shape of each published file. Change the schema in `src/lib/schemas/` and the pipeline writer together (ADR 0013).
- A component takes data and returns markup. It reads no file, no env, and no config (ADR 0012).
- Each package folder holds a README with the headings Knows, Ports, and Does not do (ADR 0016).
