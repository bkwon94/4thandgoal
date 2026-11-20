# 06: How the site tests move from Vitest to `bun test`

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Ticket 01 found that `bun test` cannot run the 179 site test files as they are. Bun lacks `vi.stubGlobal`, `vi.resetModules`, `vi.hoisted`, `vi.stubEnv`, and 7 more calls, with about 155 uses. Bun has no jsdom of its own and uses a happy-dom preload. In a sample of 20 files, 9 failed. Seven failed on a missing `vi` call, and `war-chest.test.tsx` failed on a happy-dom difference. The notes are `01-research-bun-latest.notes.md`, sections 2 and 5.

Decide:

1. Does each missing `vi` call get a rewrite to the `bun:test` API in each file, or does one shared shim file give the missing calls?
2. Do the tests run in happy-dom, with a fix of each test that depends on jsdom, or does a jsdom preload replace happy-dom?
3. Does the swap land all at once, or do Vitest and `bun test` run side by side while the files move?
4. What runs the 4 shards and the diff-only run in CI: `bun test --shard` and `bun test --changed`?

## Decision

Brian decided on 2026-11-20 in a grill:

1. Each missing `vi` call gets a rewrite to the native `bun:test` API: `vi.fn` to `mock`, `vi.spyOn` to `spyOn`, `vi.mock` to `mock.module`. One small helper file gives `stubGlobal` and `stubEnv`, each restored in `afterEach`. A test with `vi.resetModules` or `vi.hoisted` changes its setup. No full shim of `vi`, because a second fake API hides the real runner and needs upkeep.
2. The tests run in happy-dom, through the preload that the Bun docs give. A test that depends on jsdom gets a fix. If a test needs a real jsdom feature, its ticket says so and Brian decides then.
3. The files move in batches on the spec branch, one ticket for each group of packages. Until the last ticket, `check:fast` runs Vitest on the old files and `bun test` on the moved files. The last ticket removes Vitest. `main` gets one swap in the squash merge.
4. CI runs `bun test --shard=<i>/<n>` in a matrix, and `bun test --changed=origin/main` on a PR. A change to a config file or the lock file runs the full suite. The spec sets the shard count from the time of the full suite after the port. Four shards ship only if the time shows a gain over fewer shards.
