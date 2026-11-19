# The menu sheet spec fails when the motion starts late

Kind: bug
Status: done
Branch: `bug-menu-sheet-flake`.
Source: the session of 2026-11-19, after the `Check` run 44585015323 on `main` failed in the "closes" step of `apps/site/e2e/menu-sheet.spec.ts`.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; the done condition is one sentence.

## Items

### 1. The menu sheet spec stops its samples before the list moves

Done condition: `apps/site/e2e/menu-sheet.spec.ts` passes when the motion of the list of weeks starts late after a tap on "Past weeks", and it still fails when the top edge of the menu sheet moves.
Method: diagnosing-bugs
Cause: `togglePast` in `apps/site/e2e/menu-sheet.spec.ts` calls `startSamples` of `apps/site/e2e/door-motion.ts` on each tap, and each call starts one more frame loop that never stops. At "opens" 2 loops push samples and at "closes" 3 loops push samples, a probe showed. So the 20 still samples of `samplesWhenStill` are only about 10 or 7 frames, and the still frames before the tap count too. A motion that starts later than that lets the sampler return with no motion. With one loop the spec still failed at a hold of 18 frames, so the fix also waits for the list of weeks to move.
Red: at `a99928f0`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/menu-sheet.spec.ts` in `apps/site`

```text
  ✘  1 [floor] › e2e/menu-sheet.spec.ts:88:5 › the top edge of the menu sheet stays still when the motion of Past weeks starts late (8.0s)
  ✓  2 [floor] › e2e/menu-sheet.spec.ts:84:5 › the top edge of the menu sheet stays still while Past weeks opens and closes (9.3s)
    Error: the list of weeks grows or shrinks as Past weeks opens
    Expected: > 20
    Received:   0
  1 failed
  1 passed (18.6s)
```

Green: at `f205409d`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/menu-sheet.spec.ts` in `apps/site`

```text
  ✓  1 [floor] › e2e/menu-sheet.spec.ts:94:5 › the top edge of the menu sheet stays still while Past weeks opens and closes (3.8s)
  ✓  2 [floor] › e2e/menu-sheet.spec.ts:98:5 › the top edge of the menu sheet stays still when the motion of Past weeks starts late (4.8s)
  2 passed (6.5s)
```

The test command alone, after one build, passed 5 times of 5 at `f205409d`, each with 2 passed.

The spec still fails when the top edge moves. At `f205409d`, with the `motion.finish()` line of `packages/design/site/shell/menu-sheet.tsx` reverted in the working tree, not committed, then `CLIENT=cpc pnpm build`, `builtin cd apps/site && pnpm exec playwright test --project=floor e2e/menu-sheet.spec.ts`

```text
  ✘  2 [floor] › e2e/menu-sheet.spec.ts:94:5 › the top edge of the menu sheet stays still while Past weeks opens and closes (3.5s)
  ✘  1 [floor] › e2e/menu-sheet.spec.ts:98:5 › the top edge of the menu sheet stays still when the motion of Past weeks starts late (4.5s)
    Error: the top edge of the menu sheet moves 59.874698638916016px as Past weeks opens
    Expected: <= 1
    Received:    59.874698638916016
    Error: the top edge of the menu sheet moves 60.19310760498047px as Past weeks opens
  2 failed
```
Test verdict: pending

## Comments

Closes with the squash merge of the PR of `bug-menu-sheet-flake`. Commits: `a99928f0`, `f205409d`. Date: 2026-11-19.
The late-start test went red at `a99928f0` with "Received: 0", then the spec gave 2 passed 5 times of 5 at `f205409d`, and `make check-fast BASE=main` passed.
The shared `startSamples` of `apps/site/e2e/door-motion.ts` still stacks one frame loop per call, so another spec that calls it twice can hit the same race.
Read 5 files: .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, apps/site/e2e/menu-sheet.spec.ts, apps/site/e2e/door-motion.ts, packages/design/site/shell/menu-sheet.tsx.
The rerun job of `Check` failed on PR #77, because `scripts/rerun.py` runs only `client-build.mjs` and not `next build`, so the spec found no page; the Red and Green commands now hold the build, and the runs above come from them.
