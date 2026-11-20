# Cornerstone site

The Next.js site. It builds one client, named by the env value `CLIENT`. The build copies `clients/$CLIENT/published/`
into `public/`, and the site renders each `public/<season>/week-NN/page.json` and its images.
The root AGENTS.md holds the style, the flow, and the tracker.

## Commands

Run these in `apps/site/`.

- Install: `pnpm install`
- Dev server: `CLIENT=cpc pnpm dev`
- Build the static export: `CLIENT=cpc pnpm build`. The `prebuild` step checks `client.toml` and writes the generated files.
- Test: `pnpm test`. The tests read the generated files, so run `pnpm check:fast` or a build first.
- Check the export: `CLIENT=cpc pnpm check:export`. Run it after `pnpm build`, with the same `CLIENT`.
- Check the readability floor: `CLIENT=cpc pnpm check:floor`. Run it after `pnpm build`, with the same `CLIENT`. Add `-g <route>` to check one page. It runs the parallel pass, then the tests tagged `@timing` alone with one worker.
- Test the rules of the floor, the evidence runner, and the smoke run: `pnpm test:floor`. It needs Chromium and WebKit once: `pnpm exec playwright install chromium webkit`.
- Flow pick: `pnpm pick [--base <ref>] [<file> ...]`. It prints the flows that the diff since the merge base picks. The default base is `main`.
- Smoke run: `pnpm smoke --out <dir> [<flow name> ...]`. It drives the flows of `.claude/skills/verify/flows.json` at 390x660 WebKit and 1280x800. A layout flow adds 810x980 and 1080x740. A flow that calls Claude runs once, at 390x660. It starts its own site server and its own local API, each on a free port, and stops both at the end. Add `--no-api` for a run with the local API stopped. The `verify` skill says how.
- Check all: `pnpm check`. It runs the fast check, the rules of the floor, then the build, `check:export`, and `check:floor` of each client under `clients/`. For a client with the finder on, it also builds it a second time against the local API URL and runs the grade-bar project on that export. Then it builds the fixture client of the midseason report and runs the floor of the report on it. CI runs it on every push.
- Type check: `pnpm typecheck`. It runs `next typegen`, then `bun check --no-script`. The flag stops `bun check` from running the script `check` of this app. It needs Bun 1.4.5 or later.
- Run one shard of each Playwright run: set `PLAYWRIGHT_SHARD=<i>/<n>`, such as `PLAYWRIGHT_SHARD=2/5 CLIENT=cpc pnpm check:floor`. CI runs the browser check in a matrix of 5 shards. The projects `floor-timing` and `eggs` keep one worker.
- Lint: `pnpm lint`. Oxlint runs the config `.oxlintrc.json` of the repo root on all site code. Set `LINT_FILES` to paths from the repo root to lint only those files.
- Format: `pnpm fmt`. `bun fmt` rewrites all site code and package code. The config is `bunfig.toml` at the repo root. It sorts the Tailwind classes. Set `FMT_FILES` to paths from the repo root to format only those files.
- Format check: `pnpm fmt:check`. It exits 1 and names each file that is out of format. It takes `FMT_FILES` as well. The hook and CI run it.
- Bun version: `.bun-version` at the repo root pins it, and CI installs that version. `bun check` and `bun fmt` need 1.4.5 or later.
- Fast check: `pnpm check:fast`. It runs the lint, the format check, the client build of `cpc`, typecheck, and test. The hook runs it and lints and checks the format of only the staged site files.

## Rules

- The hook does not run `pnpm install`. In a new worktree with no `node_modules`, run `pnpm install` first.
- The pipeline owns the shape of each published file. Change the schema in `packages/<package>/site/schema/` and the pipeline writer together (ADR 0013).
- Never edit a file with a `GENERATED` first line. Change `client.toml` or `scripts/client-build.mjs`, and build again.
- A component takes data and returns markup. It reads no file, no env, and no config (ADR 0012).
- Each package folder holds a README with the headings Knows, Ports, and Does not do (ADR 0016).
