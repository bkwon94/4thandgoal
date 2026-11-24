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
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments
