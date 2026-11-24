# Cap the bun test workers of a local run

Kind: quick-win
Status: in-progress
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
Test verdict: pending

## Smoke

Smoke: pending

## Comments
