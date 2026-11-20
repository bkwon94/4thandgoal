# 01: Notes on what the latest Bun does for each job of the swap

Ticket: `01-research-bun-latest.md`. Date: 2026-11-20.

The latest stable Bun is **v1.4.5**, released 2026-11-19 ([release](https://github.com/oven-sh/bun/releases/tag/bun-v1.4.5), [blog](https://bun.com/blog/bun-v1.4.5)). It is a security release with no new tools. The trial binary is `bun-darwin-aarch64.zip` from that release, with its SHA-256 checked against `SHASUMS256.txt`. It sits in the scratchpad. `~/.bun` did not change.

`bun --help` of 1.4.5 lists `test`, `check`, and `fmt`. It does not list `lint`:

```
  test                           Run unit tests with Bun
  check                          Type check a TypeScript project
  fmt                            Format JavaScript and TypeScript, like Prettier
```

```
$ bun lint --help
error: Script not found "lint"
```

## 1. `bun install`

**What exists.** `bun install` runs a workspace and migrates a pnpm project. It converts `pnpm-lock.yaml` to `bun.lock` and copies the `packages` list of `pnpm-workspace.yaml` into a `workspaces` field of the root `package.json` ([install docs, "pnpm migration"](https://bun.com/docs/pm/cli/install#pnpm-migration)). `bun.lock` replaces `pnpm-lock.yaml`. The docs say `pnpm-lock.yaml` stays as it is, so the spec must delete it.

**What it does here.** A trial on a copy of the lock and the 11 `package.json` files gave these results:

1. With no root `package.json`, the install fails: `error: Bun could not find a package.json file to install from`. The repo has no root `package.json` now.
2. With a minimal root `package.json`, Bun copied the workspace list, but the lock migration failed: `error: pnpm-lock.yaml missing root package entry (importers['.'])`. Bun then ignored the lock and resolved fresh versions. It saved `bun.lock` with 472 packages in 2.3 s.
3. A full `bun install` then took 4.8 s. It used the isolated linker, with `node_modules/.bun/` and a symlink per workspace package, such as `apps/site/node_modules/@cpc/design -> packages/design/site`. A new workspace gets the isolated linker by default ([isolated installs](https://bun.com/docs/pm/isolated-installs)).
4. Bun blocked one postinstall: `unicode-animations@1.0.3`. Add it to `trustedDependencies` if it needs its script ([lifecycle](https://bun.com/docs/pm/lifecycle)).

To keep the versions that pnpm locked, add the root `package.json` first and run `pnpm install` once. That gives the pnpm lock an `importers['.']` entry, and Bun can then migrate it. This order is an inference from the error text. The trial did not test it.

**The script command.** `pnpm --dir apps/site <script>` becomes `bun run --cwd apps/site <script>`, or `bun --filter 4thandgoal-site <script>` ([filter docs](https://bun.com/docs/pm/filter)). `--cwd` and `--filter` are in `bun --help` of 1.4.5. `bun install --frozen-lockfile` is the CI form (`bun install --help`).

**Fallback.** None needed. Install exists.

## 2. `bun test` on the 179 site test files

The Vitest list now has **183** files, not 179 (`vitest list --filesOnly`).

**What exists.**

- **DOM.** The Bun docs set up `happy-dom` with `@happy-dom/global-registrator` in a `[test] preload` of `bunfig.toml` ([DOM testing](https://bun.com/docs/test/dom)). The docs name no jsdom setup. A jsdom preload must copy the window globals by hand or use a package for it.
- **React Testing Library.** The same page shows RTL with that preload ([DOM testing](https://bun.com/docs/test/dom#react-testing-library)).
- **`vi` and `import ... from "vitest"`.** `bun:test` gives a `vi` object. The docs name `vi.fn`, `vi.spyOn`, `vi.mock`, `vi.restoreAllMocks`, `vi.resetAllMocks`, and `vi.clearAllMocks` ([mocks, "Vitest Compatibility"](https://bun.com/docs/test/mocks#vitest-compatibility)). An import from `"vitest"` resolves to `bun:test` with no `vitest` package installed. A probe of 1.4.5 printed all keys of `vi`:

  ```
  advanceTimersByTime,advanceTimersToNextTimer,clearAllMocks,clearAllTimers,fn,getTimerCount,isFakeTimers,mock,resetAllMocks,restoreAllMocks,runAllTimers,runOnlyPendingTimers,spyOn,useFakeTimers,useRealTimers
  ```
- **The `@` alias.** Bun reads `paths` from `tsconfig.json`. `@/*` in `apps/site/tsconfig.json` resolved in the trial with no extra config.
- **Setup files.** `apps/site/vitest.config.mts` has no setup files. The one setup that `bun test` needs is the DOM preload.

**The gap: missing `vi` calls.** The site tests use these calls that Bun 1.4.5 does not have. The count is the number of uses across the 163 tracked test files.

| Call | Uses |
| --- | --- |
| `vi.stubGlobal` | 47 |
| `vi.unstubAllGlobals` | 31 |
| `vi.resetModules` | 28 |
| `vi.hoisted` | 24 |
| `vi.setSystemTime` | 7 |
| `vi.stubEnv`, `vi.unstubAllEnvs` | 11 |
| `vi.doMock`, `vi.doUnmock` | 4 |
| `vi.advanceTimersByTimeAsync` | 2 |
| `vi.importActual` | 1 |

`bun:test` has a near form for some of them: `setSystemTime` and `mock.module` ([dates and times](https://bun.com/docs/test/dates-times), [mocks](https://bun.com/docs/test/mocks)). Each other call needs a small shim in the preload or an edit to the test.

**Fails in the 20-file sample.** 11 files pass. 9 files fail. The reasons:

| File | Reason |
| --- | --- |
| `packages/analyzer/site/form/trade-finder.test.tsx` | `vi.stubGlobal` and `vi.unstubAllGlobals` are not functions. 19 tests fail. |
| `apps/site/src/app/_routes/managers/page.test.tsx` | `vi.resetModules` is not a function. 12 tests fail. |
| `apps/site/src/lib/routes.test.ts` | `vi.unstubAllEnvs` is not a function. 8 tests fail. |
| `packages/sim/site/lib/what-if-api.test.ts` | `vi.stubGlobal` is missing, so the real `fetch` runs: `ECONNREFUSED 127.0.0.1:9` and a 5 s timeout. |
| `apps/site/src/app/_routes/waiver/war-chest.test.tsx` | happy-dom differs from jsdom. An avatar `src` falls back to `/images/avatar-default.svg`. Motion animations reject 532 times with `AbortError: The animation was canceled.` |
| `packages/design/site/shell/theme-button.test.tsx` | `vi.stubGlobal` at the top level throws, so the file does not load. |
| `apps/site/src/app/front-door/feed-block.test.tsx` | `vi.hoisted` is not a function. The file does not load. |
| `apps/site/src/app/not-found.test.tsx` | `vi.hoisted` is not a function. The file does not load. |
| `apps/site/src/app/page-site.test.tsx` | `vi.hoisted` is not a function. The file does not load. |

A hand-made jsdom preload made `war-chest.test.tsx` pass 34 of 35 tests with no `AbortError`. The one fail came from the preload, which skipped the jsdom `Event` because Bun has its own. A complete jsdom preload is likely closer to Vitest than happy-dom is.

Two more facts for the setup:

- Run `bun test` from `apps/site`. From the repo root, `component-rule.test.ts` and `ui-sdk-rule.test.ts` fail, because they find their tree from the working directory.
- `bun test -c <scratch>/bunfig.toml` did not apply the `preload` of that file. `--preload` on the command line worked. A `bunfig.toml` in `apps/site` is the normal place.

**Fallback.** The map names no fallback for test, because Vitest is the tool now. Keep Vitest until the `vi` gap closes, or shim it.

## 3. Shard and `--changed`

**What exists.** Both exist in 1.4.5. From `bun test --help`:

```
      --changed=<val>                 Only run test files affected by changed files according to git. Optionally pass a commit or branch to compare against.
      --parallel=<val>                Run test files in parallel using N worker processes. Implies --isolate. Defaults to CPU core count.
      --shard=<val>                   Run a subset of test files, e.g. '--shard=1/3' runs the first of three shards. Useful for splitting tests across multiple CI jobs.
      --timings=<val>                 JSON file(s) of per-file durations (ms); several are merged, e.g. one per CI shard. Balances --shard by total time and makes --parallel start the slowest files first.
```

- `--shard=i/n` sorts the files by path and takes a fixed slice. With `--timings`, Bun balances the shards by time. The docs give a GitHub Actions matrix of 4 shards with `--update-timings` ([parallel docs, "--shard"](https://bun.com/docs/test/parallel#splitting-a-suite-across-ci-machines-with---shard), [large codebases](https://bun.com/docs/test#large-codebases)).
- `--changed` asks git for the changed files, builds the import graph of each test file, and runs each test that imports a changed file. The source calls it "vitest-compatible" ([`ChangedFilesFilter.rs`](https://github.com/oven-sh/bun/blob/bun-v1.4.5/src/runtime/cli/test/ChangedFilesFilter.rs), [flag in `Arguments.rs`](https://github.com/oven-sh/bun/blob/bun-v1.4.5/src/runtime/cli/Arguments.rs)). The docs pages do not describe `--changed`. Only the help text and the source do.
- By default `bun test` runs all files in one process with one global. `--parallel` gives each file a fresh global, as Vitest does ([parallel docs](https://bun.com/docs/test/parallel)).

**Fallback.** None needed.

## 4. `bun check`, `bun lint`, and `bun fmt`

### `bun check`: exists in 1.4.5

It first shipped in v1.4.3 ([blog v1.4.3](https://bun.com/blog/bun-v1.4.3)). It is a port of typescript-go and "passes 100% of TypeScript 7.0.2's conformance test suite". It reads `tsconfig.json`, uses all cores, and reports the same errors as `tsc` 7 ([check docs](https://bun.com/docs/runtime/check)). It emits no files, ignores the `plugins` compiler option, and has no language server.

On the site, one run each, with no other check running:

| Command | Wall time |
| --- | --- |
| `tsc --noEmit --incremental false` (7.0.2) | 1.16 s |
| `tsc --noEmit` with the warm `tsconfig.tsbuildinfo` | 0.50 s |
| `bun check --no-script` | 0.22 s, "No type errors in 581 files" |

Two traps for the spec:

- `apps/site/package.json` has a `check` script. `bun check` runs that script, not the type checker, unless you pass `--no-script` ([check docs](https://bun.com/docs/runtime/check)). `bun fmt` and `bun lint` act the same way ([issue 47714](https://github.com/oven-sh/bun/issues/47714)).
- `typecheck` runs `next typegen` before `tsc`. `bun check` does not run `next typegen`, so keep that step.

**Fallback if not used.** `tsc` from TypeScript 7.

### `bun lint`: not in 1.4.5

The linter merged on `main` in [PR 44805](https://github.com/oven-sh/bun/pull/44805). [PR 46438](https://github.com/oven-sh/bun/pull/46438) kept it out of release builds, and v1.4.4 shipped that way. [PR 46439](https://github.com/oven-sh/bun/pull/46439) puts it back in release builds and says "the next release is the first one that has `bun lint`". But v1.4.5 came from a branch without PR 46439: a compare of that commit with the tag shows `diverged`. The binary confirms it. `bun lint` in 1.4.5 prints `error: Script not found "lint"`.

The canary build `1.4.6-canary.1+7bb427f3b` has it:

```
Usage: bun lint [flags] [...files, directories or patterns]
  Find and fix problems in JavaScript and TypeScript.
      --fix                   Fix problems and write the files
      --staged                Only lint files that are staged in git
      --changed=<val>         Only lint files that differ from a branch or commit (default: the default branch)
      --type-aware            Also run the rules that need types
```

**Custom rules: yes, on canary.** `bun lint` loads ESLint plugins, from npm or from a local file, with `plugins = ["./lint/plugin.js"]` in `[lint]` of `bunfig.toml`. Rules get the ESLint `context`, `sourceCode`, scopes, and fixers. It also reads `jsPlugins` in `.oxlintrc.json` ([lint plugins docs](https://bun.com/docs/lint/plugins), [lint docs](https://bun.com/docs/lint)). So the design rules of ticket 03 can be one ESLint-style plugin file. The same file then runs in Oxlint through `jsPlugins`. A JavaScript rule is slower than a native rule.

The docs on bun.com describe `bun lint` with no note that it is canary only. The docs follow `main`, not the release.

**Fallback.** Oxlint, until a stable Bun ships `bun lint`.

### `bun fmt`: exists in 1.4.5

It first shipped in v1.4.4 ([blog index](https://bun.com/blog)). It formats JavaScript, TypeScript, JSX, CSS, HTML, JSON, YAML, Markdown, and more, with "the same output as Prettier". It reads Prettier and oxfmt configs. It has `--check`, `--staged`, and `--changed`, plus Tailwind class sort, which reads the installed `tailwindcss` ([format docs](https://bun.com/docs/format)). `bun fmt --help --all` in 1.4.5 lists `--sort-tailwindcss` and `--sort-imports`.

**Fallback if not used.** `oxfmt`.

## 5. Measure: `bun test` beside Vitest

**Setup.**

- Bun 1.4.5 from the scratchpad. Vitest 5.0.5 with the real `apps/site/vitest.config.mts`. Node v24.15.0. An Apple silicon Mac with 10 cores.
- Bun used `--preload happydom.ts`, which calls `GlobalRegistrator.register()` as the [DOM docs](https://bun.com/docs/test/dom) say. `@happy-dom/global-registrator` 21.0.4 sat in the scratchpad, not in the repo.
- The sample is every 9th file of the sorted list of 183, which gives 20 files. Each command ran from `apps/site`, three rounds, in turn.
- Before each run, a script waited until `pgrep -f 'vitest|check-fast'` found nothing. Another worktree ran `make check-fast` at the start, so the script waited 60 s. One `bun-serial` run in round 2 saw 2 other processes start at its end.

**Commands.**

```
vitest local:  ./node_modules/.bin/vitest run <20 files>            # maxWorkers 2
vitest CI:     CI=1 ./node_modules/.bin/vitest run <20 files>       # default workers
bun serial:    bun test --preload happydom.ts <20 files>
bun parallel:  bun test --parallel --preload happydom.ts <20 files>
```

**All 20 files.** Bun fails 9 files, see item 2. The Bun times include a 5 s timeout in `what-if-api.test.ts` and the abort errors in `war-chest.test.tsx`, so they are not a fair speed figure.

| Command | Round 1 | Round 2 | Round 3 | Median | Result |
| --- | --- | --- | --- | --- | --- |
| Vitest local | 9.08 s | 8.30 s | 8.39 s | 8.39 s | 20 files pass |
| Vitest CI | 4.64 s | 4.12 s | 4.90 s | 4.64 s | 20 files pass |
| `bun test` | 7.57 s | 6.32 s | 6.34 s | 6.34 s | 98 pass, 49 fail |
| `bun test --parallel` | 5.77 s | 5.93 s | 5.66 s | 5.77 s | 98 pass, 49 fail |

**The 11 files that pass in Bun.** This is the fair figure. Each runner ran the same 64 tests, and all passed.

| Command | Round 1 | Round 2 | Round 3 | Median |
| --- | --- | --- | --- | --- |
| Vitest local | 3.68 s | 3.14 s | 3.25 s | 3.25 s |
| Vitest CI | 1.73 s | 1.85 s | 1.86 s | 1.85 s |
| `bun test` | 0.73 s | 0.60 s | 0.60 s | 0.60 s |
| `bun test --parallel` | 0.47 s | 0.49 s | 0.50 s | 0.49 s |

On the files that pass, `bun test --parallel` is about 3.8 times faster than Vitest with all cores. It is about 6.6 times faster than Vitest with the local cap of 2 workers. Vitest spent 58 to 64% of its time on the jsdom environment. A serial run with the hand-made jsdom preload took 0.96 s on the same 11 files, against 0.60 s with happy-dom.

## What the spec needs to know

1. Add a root `package.json`. Run `pnpm install` once so the lock gets `importers['.']`, then run `bun install` to keep the pnpm versions. Delete `pnpm-lock.yaml` after that.
2. `bun test` cannot run the suite as it is. Bun 1.4.5 lacks `vi.stubGlobal`, `vi.resetModules`, `vi.hoisted`, `vi.stubEnv`, and 7 more calls, with about 155 uses. The spec needs a `vi` shim in the preload or a rewrite of those tests. It also needs a choice between happy-dom and a full jsdom preload.
3. `--shard`, `--timings`, `--parallel`, and `--changed` all exist in `bun test`, so the 4 CI shards and the diff-only run need no extra tool.
4. `bun check` and `bun fmt` exist in 1.4.5. `bun lint` is on canary only, so use Oxlint as the map says. Write the design rules as one ESLint-style plugin, which Oxlint `jsPlugins` runs now and `bun lint` runs later.
5. The site `check` script shadows `bun check`. Pass `--no-script` or rename the script, and keep `next typegen` before the type check.
