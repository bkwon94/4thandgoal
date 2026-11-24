# Cap the bun test workers of a local run

Kind: quick-win
Status: done
Branch: `win-bun-worker-cap`.
Source: the session of 2026-11-24.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. A local run of `pnpm test:bun` starts one worker per CPU core

Done condition: With no `BUN_TEST_WORKERS` and no `CI` set, `apps/site/scripts/bun-test.mjs` runs `bun test` with `--parallel=3`, and with `CI` set it keeps one worker per CPU core.
Method: tdd
Red: at `54ecd484` with `apps/site/scripts/test-scope.test.mjs` of `8fc1a72d`, `cd apps/site && bun test --isolate ./scripts/test-scope.test.mjs`. The parent has no `workerCount`, so a scratch worktree adds the old rule as `workerCount`: `env.BUN_TEST_WORKERS || String(cores)`.

```text
error: expect(received).toBe(expected)

Expected: "3"
Received: "10"

(fail) the count of workers of a bun test run > is 3 on a local run, with no BUN_TEST_WORKERS and no CI, so many agents at once do not swap the Mac
 17 pass
 1 fail
```
Green: at `8fc1a72d`, `cd apps/site && bun test --isolate ./scripts/test-scope.test.mjs`

```text
 18 pass
 0 fail
 54 expect() calls
Ran 18 tests across 1 file.
```
Test verdict: PASS

## Smoke

Smoke: none. The change is to the test runner, not to a page, and `pnpm --dir apps/site pick --base main` prints "No flow: no file of the diff matches a glob of the flow list."

## Comments

Closes with the squash merge of the PR of `win-bun-worker-cap`. Commits: `54ecd484`, `8fc1a72d`, `b7a30d63`, `b4b32ace`, `f7062107`. Date: 2026-11-24.
The loop `bun test --isolate ./scripts/test-scope.test.mjs` went red at 17 pass and 1 fail, then green at 18 pass and 0 fail; `make check-fast BASE=main` passed with 1972 tests and 0 fail.
The red output comes from the old rule in a scratch worktree, because the parent commit has no `workerCount` to call.
Read 7 files: AGENTS.md, apps/site/AGENTS.md, Makefile, apps/site/scripts/bun-test.mjs, apps/site/scripts/test-scope.mjs, apps/site/scripts/test-scope.test.mjs, apps/site/playwright.config.ts.
