# Cornerstone site

The Next.js site. It builds one client, named by the env value `CLIENT`. The build copies `clients/$CLIENT/published/`
into `public/`, and the site renders each `public/<season>/week-NN/page.json` and its images.
The root CLAUDE.md holds the style, the flow, and the tracker.

## Commands

Run these in `apps/site/`.

- Install: `pnpm install`
- Dev server: `CLIENT=cpc pnpm dev`
- Build the static export: `CLIENT=cpc pnpm build`. The `prebuild` step checks `client.toml` and writes the generated files.
- Test: `pnpm test`. The tests read the generated files, so run `pnpm check:fast` or a build first.
- Check the export: `CLIENT=cpc pnpm check:export`. Run it after `pnpm build`, with the same `CLIENT`.
- Check all: `pnpm check`. It runs the fast check, then the build and `check:export` of each client under `clients/`. CI runs it on every push.
- Fast check: `pnpm check:fast`. It runs the client build of `cpc`, typecheck, and test. The hook runs it.

## Rules

- The hook does not run `pnpm install`. In a new worktree with no `node_modules`, run `pnpm install` first.
- The pipeline owns the shape of each published file. Change the schema in `src/lib/schemas/` and the pipeline writer together (ADR 0013).
- Never edit a file with a `GENERATED` first line. Change `client.toml` or `scripts/client-build.mjs`, and build again.
- A component takes data and returns markup. It reads no file, no env, and no config (ADR 0012).
- Each package folder holds a README with the headings Knows, Ports, and Does not do (ADR 0016).
