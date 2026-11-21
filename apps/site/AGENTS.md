# Cornerstone site

The Next.js site. It builds one client, named by the env value `CLIENT`. The build copies `clients/$CLIENT/published/`
into `public/`, and the site renders each `public/<season>/week-NN/page.json` and its images.
The root AGENTS.md holds the style, the flow, and the tracker.

## Commands

Run these in `apps/site/`.

- Install: `pnpm install`
- Dev server: `CLIENT=cpc pnpm dev`
- Build the static export: `CLIENT=cpc pnpm build`. The `prebuild` step checks `client.toml` and writes the generated files.
- Test: `pnpm test`. It runs `pnpm test:bun`. The tests read the generated files, so run `pnpm check:fast` or a build first.
- Test on Bun: `pnpm test:bun [<bun test flag> ...]`. `scripts/bun-test.mjs` runs `bun test --isolate` from `apps/site` on `src/`, `scripts/`, `test/`, and the `site/` folder of each package. With `--isolate`, each file has its own global and module registry. The preload `test/preload.ts` gives happy-dom, and `bunfig.toml` of `apps/site` loads it. `bunfig.toml` does not read `isolate`, so a direct `bun test` call needs the flag.
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
- Fast check: `pnpm check:fast`. It runs the lint, the format check, the client build of `cpc`, typecheck, and `pnpm test:bun`. The hook runs it and lints and checks the format of only the staged site files. `bun test` runs every test file, also in the hook.

## Write a test for `bun test`

Each site test runs on `bun test` with happy-dom (ADR 0038). No test runs on Vitest. A test imports only from `bun:test`, and these rules replace the `vi` calls of Vitest.

1. Use `mock` for a fake function, `spyOn` for a spy, and `mock.module` for a fake module.
2. In a test of the app, use `stubGlobal` and `stubEnv` of `apps/site/test/stubs.ts`.
3. In a test of a package, use `spyOn(globalThis, "x").mockImplementation(fake)`. A package imports nothing from the app.
4. Restore nothing by hand. The preload restores each spy and each stub after each test.
5. Put each spy and each stub in `beforeEach`. The restore after the first test removes a spy or a stub at the top level of a file.
6. Use `resetModules()` of `apps/site/test/reset-modules.ts` for a module that reads an env or `process.cwd` value when it loads. Then import the module again.
7. Use an import with a side effect that runs first, such as `@/fixtures/cpc-site`, for a setup that must run before the other imports. Bun has no `vi.hoisted`.
8. Use `setSystemTime` to fix only `Date`. Use `setDefaultTimeout` to change the time limit of each test of a file.
9. Run `pnpm test:bun` in full before the merge.

The preload unmounts each React Testing Library render after each test, so a file needs no `cleanup` of its own. The preload also marks the `finished` promise of a canceled animation as handled, as a browser does, so a Framer Motion part ends with no `AbortError`. happy-dom has a desktop-wide window, so a test of a page that opens the menu sheet calls `stubPhone` of `test/phone.ts` in `beforeEach`. If a test needs a real jsdom feature, the ticket names it for Brian.

The preload makes happy-dom act as a browser in five more ways. `test/dom.test.ts` proves each one.

- `TransformStream` and `WritableStream` are the web stream classes of Bun. happy-dom sets them to the Node classes `Stream.Transform` and `Stream.Writable`, so the native `pipeThrough` refused them, and each streamed Answer showed "The question did not go through".
- A failed expect prints a node as its markup. Bun prints each own property of an object, and a happy-dom node reaches the whole window. With no fix, each failed check of a `waitFor` on a node prints megabytes, and one test stalls for minutes.
- `requestAnimationFrame` runs about 60 frames each second. Each callback of one frame gets the same time. The frame timer keeps the real `setTimeout`. A test that fakes `setTimeout` leaves the frames running. Never use `jest.useFakeTimers` in a test that renders Framer Motion, because it drops each timer that is pending when it ends.
- The page URL is `http://localhost:3000/`, so a relative `img` src resolves and fires no `error`.
- A `spyOn(Storage.prototype, "getItem")` acts on `localStorage` and `sessionStorage`, also after the first call. Never spy on the storage object itself, because its Proxy keeps the spy as data.

happy-dom differs from jsdom in these ways too. The preload does not change them, so each test that depends on them has its own fix.

- The window is 1024 pixels wide, and `matchMedia` answers each width query. jsdom has no `matchMedia`, so a test there saw the phone tier. For the phone tier, spy on `matchMedia` in `beforeEach` with a stub that matches no query.
- `IntersectionObserver` exists, but it never reports an entry. A part that waits on `inView` of Framer Motion never starts. jsdom has none, so the part ran its fallback.
- `Element.prototype.animate` exists, so Framer Motion runs `opacity`, `transform`, `filter`, `clipPath`, and `backgroundColor` as a Web Animation. The inline style then holds no middle value. In jsdom, Framer Motion wrote each frame to the inline style.
- `bun test` runs each file in one process, with one module registry and one window. Framer Motion reads `(prefers-reduced-motion)` once per run, and it decides once per run if it uses `Element.prototype.animate`. A spy on `matchMedia` in a later file does not change reduced motion. A file can pass alone and fail in the full run, so run `pnpm test:bun` in full before the merge.

## Rules

- The hook does not run `pnpm install`. In a new worktree with no `node_modules`, run `pnpm install` first.
- The pipeline owns the shape of each published file. Change the schema in `packages/<package>/site/schema/` and the pipeline writer together (ADR 0013).
- Never edit a file with a `GENERATED` first line. Change `client.toml` or `scripts/client-build.mjs`, and build again.
- A component takes data and returns markup. It reads no file, no env, and no config (ADR 0012).
- Each package folder holds a README with the headings Knows, Ports, and Does not do (ADR 0016).
