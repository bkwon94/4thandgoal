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
Cause: pending
Red: pending
Green: pending
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
