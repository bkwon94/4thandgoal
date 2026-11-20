# 01: What the latest Bun does for each job of the swap

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The spec swaps pnpm, Vitest, `tsc`, and the new linter and formatter for Bun. The local Bun is 1.3.9, and its `--help` lists no `check`, `lint`, or `fmt`. Check the latest Bun release against the Bun docs, the release notes, and the source. Answer each item with a link to the primary source:

1. `bun install`: does it run the pnpm workspace of the root and its members? What replaces `pnpm-lock.yaml`? What does `pnpm --dir apps/site <script>` become?
2. `bun test`: can it run the 179 site test files that Vitest runs now from `apps/site/vitest.config.mts`? Check the jsdom setup or the `happy-dom` preload, the `vi.*` calls, the `@` alias, the setup files, and React Testing Library.
3. `bun test`: does it have a shard flag and a `--changed` flag, or the like?
4. `bun check`, `bun lint`, and `bun fmt`: does each one exist, and what does it do? Does `bun lint` take custom rules, so the design rules of ticket 03 can run in it?
5. Measure: run `bun test` on a sample of the site tests with the real setup, and give the wall-clock time beside Vitest on the same files.

If an item does not exist, say so and name the fallback that the map sets.

## Decision

A research agent answered each item on 2026-11-20 against Bun v1.4.5, released 2026-11-19. The notes are `01-research-bun-latest.notes.md`, with a source URL for each claim.

1. `bun check` exists. It is a port of TypeScript 7. It took 0.22 s on the site, against 1.16 s for `tsc` with no incremental cache. The `check` script of the site hides it, so the spec renames the script or runs `bun check --no-script`. `next typegen` still runs before it.
2. `bun fmt` exists. It gives Prettier output and sorts the Tailwind classes.
3. `bun lint` is on canary only, in 1.4.6-canary.1. The map's fallback holds: Oxlint runs the lint now. Oxlint `jsPlugins` and canary `bun lint` both run one ESLint-style plugin, so the design rules move to `bun lint` with no rewrite when it ships.
4. `bun install` runs the workspace and writes `bun.lock` in place of `pnpm-lock.yaml`. The repo has no root `package.json`, so it fails as it is. The lock migration also fails, so Bun resolves fresh versions. New ticket 05 decides the path.
5. `bun test` has `--shard`, `--parallel`, and `--changed`, which follows the import graph. It cannot run the suite as it is. It lacks `vi.stubGlobal`, `vi.resetModules`, `vi.hoisted`, `vi.stubEnv`, and 7 more, with about 155 uses. Nine of 20 sample files fail, 7 of them on a missing `vi` call and 1 on a happy-dom difference. New ticket 06 decides the path.
6. The time on the 11 sample files that pass: Vitest 3.25 s with the local cap of 2 workers, Vitest 1.85 s with `CI=1`, `bun test` 0.60 s, and `bun test --parallel` 0.49 s.
