# 01: What the latest Bun does for each job of the swap

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The spec swaps pnpm, Vitest, `tsc`, and the new linter and formatter for Bun. The local Bun is 1.3.9, and its `--help` lists no `check`, `lint`, or `fmt`. Check the latest Bun release against the Bun docs, the release notes, and the source. Answer each item with a link to the primary source:

1. `bun install`: does it run the pnpm workspace of the root and its members? What replaces `pnpm-lock.yaml`? What does `pnpm --dir apps/site <script>` become?
2. `bun test`: can it run the 179 site test files that Vitest runs now from `apps/site/vitest.config.mts`? Check the jsdom setup or the `happy-dom` preload, the `vi.*` calls, the `@` alias, the setup files, and React Testing Library.
3. `bun test`: does it have a shard flag and a `--changed` flag, or the like?
4. `bun check`, `bun lint`, and `bun fmt`: does each one exist, and what does it do? Does `bun lint` take custom rules, so the design rules of ticket 03 can run in it?
5. Measure: run `bun test` on a sample of the site tests with the real setup, and give the wall-clock time beside Vitest on the same files.

If an item does not exist, say so and name the fallback that the map sets.

## Decision

None yet.
