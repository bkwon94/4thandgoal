# The wait contrast test of the analyzer stage fails on a slow runner

Kind: bug
Status: in-progress
Branch: `bug-analyzer-wait`.
Source: the handoff file `.handoff/flaky-specs.md`, item 5, and Check run 44645738360 of PR #80.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The wait hero of cpc breaks the readability floor on a loaded runner

Done condition: The AT-20 wait contrast test of `apps/site/e2e/analyzer-stage.spec.ts` passes when the frames of the wait come late, and it still fails when a hero text of the wait drops below 4.5:1.
Method: diagnosing-bugs
Cause: the AT-20 wait contrast loop in `apps/site/e2e/analyzer-stage.spec.ts` calls `lineAtRest` and then `scanHeroPixels` in a second call, so a check in the 50 ms gap of a swap of `StageLines` misses the rise of the next line, and a late read on a loaded runner reads that line mid-rise at a low opacity. This is a test bug: the CI line read 4.27:1 at an opacity of about 0.6, the line reaches 9.18:1 at rest, and the floor does not judge a fade (`openPage` waits for each fade to end). The fix adds `sampleWaitHero`, which holds the timers of the page through `holdableTimers` for the whole sample, so no line starts to swap or to rise between the check and the read. The samples now wait for 5 new frames of the mesh in place of `page.waitForTimeout(150)`. The loop `lateRise` holds the release of each next line until the next check of rest, then adds a lag of 300 ms and a rise of 1.5 s, so the old loop reads the line early in its rise on each run. The fix touches only `apps/site/e2e`.
Red: at `d2fc996a`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/analyzer-stage.spec.ts -g "wait contrast"` in `apps/site`

```text
  ✘  4 [floor] › e2e/analyzer-stage.spec.ts:491:7 › the wait, with motion on › wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait when the frames of the wait come late, light 1280px (AT-20) (5.7s)
    Error: the wait hero of cpc breaks the readability floor
    +   "pixel: hero \"Grading the Trade\" span.t-think-text \"Checking roster fit\" is 1.20:1 on #141414, under 4.5:1",
  1 failed
  4 passed (15.3s)
```

The loop went red on 5 of 5 runs with `--repeat-each 5`, each on the same line "Checking roster fit" at about 1.2:1. The 20 other runs passed.

Green: at `1093ddf7`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/analyzer-stage.spec.ts -g "wait contrast"` in `apps/site`

```text
  ✓  1 [floor] › e2e/analyzer-stage.spec.ts:543:11 › the wait, with motion on › wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, light 1280px (AT-20) (4.8s)
  ✓  2 [floor] › e2e/analyzer-stage.spec.ts:543:11 › the wait, with motion on › wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, dark 390px (AT-20) (4.8s)
  ✓  3 [floor] › e2e/analyzer-stage.spec.ts:549:7 › the wait, with motion on › wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait when the frames of the wait come late, light 1280px (AT-20) (4.7s)
  ✓  4 [floor] › e2e/analyzer-stage.spec.ts:543:11 › the wait, with motion on › wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, dark 1280px (AT-20) (4.9s)
  ✓  5 [floor] › e2e/analyzer-stage.spec.ts:543:11 › the wait, with motion on › wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, light 390px (AT-20) (4.7s)
  5 passed (15.1s)
```

At `1093ddf7`, the same command with `--repeat-each 5` gives `25 passed`. The full spec `analyzer-stage.spec.ts` gives `42 passed` and `1 skipped` in the project `floor`, and `12 passed` in the project `floor-timing`. The skipped test is for norcal only. `make check-fast BASE=origin/main` passes.

The proof that the loop still fails when a hero text of the wait drops below 4.5:1: at `1093ddf7`, with the color of `.t-think-text` in `apps/site/src/app/globals.css` set to `color-mix(in srgb, var(--color-on-dark-2) 45%, var(--color-band))` for one run and then put back, the same command gives:

```text
  ✘  1 [floor] › e2e/analyzer-stage.spec.ts:543:11 › ... dark 390px (AT-20) (4.8s)
  ✘  2 [floor] › e2e/analyzer-stage.spec.ts:543:11 › ... light 1280px (AT-20) (4.8s)
  ✘  4 [floor] › e2e/analyzer-stage.spec.ts:549:7 › ... when the frames of the wait come late, light 1280px (AT-20) (4.8s)
  ✘  3 [floor] › e2e/analyzer-stage.spec.ts:543:11 › ... dark 1280px (AT-20) (4.8s)
  ✘  5 [floor] › e2e/analyzer-stage.spec.ts:543:11 › ... light 390px (AT-20) (4.7s)
    +   "pixel: hero \"Grading the Trade\" span.t-think-text \"Weighing the sides\" is 3.17:1 on #181716, under 4.5:1",
    +   "pixel: hero \"Grading the Trade\" span.t-think-text \"Checking roster fit\" is 3.23:1 on #151515, under 4.5:1",
  5 failed
```
Test verdict: pending

## Smoke

Smoke: none. `pnpm --dir apps/site pick --base origin/main` prints "No flow: no file of the diff matches a glob of the flow list.", because the run changes only `apps/site/e2e/analyzer-stage.spec.ts`.

## Comments

- CI failure in run 44645738360: "the wait hero of cpc breaks the readability floor" in "wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, light 1280px (AT-20)". The handoff names the same spec at run 44201201184 and run 44393438643.
