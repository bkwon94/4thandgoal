# Flaky browser specs that block deploys

Kind: bug
Status: in-progress
Branch: `bug-flaky-browser-specs`.
Source: the handoff file `.handoff/flaky-specs.md`, Run 1.
Boundary: holds. 4 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The tour glide tests fail on a slow runner

Done condition: The AT-15 glide tests of `apps/site/e2e/front-door-tour-motion.spec.ts` pass when the first frame of the glide comes late, and they still fail when the hole stays at the old Stop.
Method: diagnosing-bugs
Cause: `glideTogether` in `apps/site/e2e/front-door-tour-motion.spec.ts` reads the real clock of the page, so a runner frame of 330 ms or more lands past 99% of the 450 ms spring and a real glide looks like a jump. This is a test bug: the spring of framer-motion runs on time and already starts late from its first frame (`resolveStartTime`, 40 ms). The fix gives the page a clock of frames, `frameClock`, that moves 1000/60 ms or 150 ms per frame. The stacked loops of `startSamples` only double each sample and do not cause this failure, so `door-motion.ts` stays as it is (item 6 under Later).
Red: at `1c9baeaa`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-motion.spec.ts -g "AT-15"` in `apps/site`

```text
AT-15 time of the hole between the Stops: 0.0 ms
  ✘  2 [floor] › e2e/front-door-tour-motion.spec.ts:198:7 › iPhone 390x660 with motion on › when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15) (4.3s)
    Error: the hole shows between the Stops for 80 ms or more; the hole tops at each ms: 321@0, 321@0, 321@18, 321@18, 321@34, 321@34, 321@35, 321@35, 321@36, 321@36, 321@452, 321@452, 321@862, 321@862, 377@1277, 377@1277, ...
  1 failed
  2 passed (15.1s)
```

Green: at `c3c54350`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-motion.spec.ts -g "AT-15"` in `apps/site`

```text
AT-15 time of the hole between the Stops: 316.7 ms
  ✓  2 [floor] › e2e/front-door-tour-motion.spec.ts:195:7 › iPhone 390x660 with motion on › the hole and the card glide together from Stop 1 to Stop 2, until the card changes side (AT-15) (3.8s)
AT-15 time of the hole between the Stops: 316.7 ms
  ✓  1 [floor] › e2e/front-door-tour-motion.spec.ts:203:7 › iPhone 390x660 with motion on › when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15) (5.0s)
AT-15 time of the hole between the Stops: 300.0 ms
  ✓  3 [floor] › e2e/front-door-tour-motion.spec.ts:199:7 › iPhone 390x660 with motion on › on a slow runner with 150 ms frames, the hole and the card still glide together (AT-15) (2.3s)
  3 passed (7.5s)
```

The proof that the loop still fails when the hole stays at the old Stop: at `c3c54350`, with the hole transition of `tour.tsx` set to `orStill(true, GLIDE)` for one run and then put back, the same command gives:

```text
  ✘  2 [floor] › ... the hole and the card glide together from Stop 1 to Stop 2, until the card changes side (AT-15) (3.2s)
  ✘  1 [floor] › ... when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15) (4.4s)
  ✘  3 [floor] › ... on a slow runner with 150 ms frames, the hole and the card still glide together (AT-15) (2.5s)
    Error: the hole shows between the Stops for 80 ms or more; the hole tops at each ms: 321@0, 321@0, 321@150, 321@150, 321@300, 321@300, 321@450, 321@450, 377@600, 377@600, ...
  3 failed
```
Test verdict: pending

### 2. The card covers its control after a burst of scroll

Done condition: After each burst of scroll in WebKit at 390x660, the tour card comes to rest beside its hole and never over its control, on a loaded runner too.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 3. The norcal scene is not at rest after 100 ms

Done condition: The norcal scene test of `apps/site/e2e/scene.spec.ts` passes when the scene starts late, and it still fails when the scene plays its motion before it settles.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 4. The passphrase box tests time out

Done condition: Both AT-51 tests of `apps/site/e2e/front-door-passphrase.spec.ts` pass when an Announcement or the Tour opens on the load beat, and they still fail when the box sits under the keyboard.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments
